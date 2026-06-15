import asyncio
import sys

from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from langgraph.runtime import Runtime
from pydantic import Field
from pydantic import BaseModel
from pydantic.v1.typing import convert_generics
from torch.utils.bundled_inputs import augment_many_model_functions_with_bundled_inputs
from langchain.messages import RemoveMessage
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from typing import TypedDict, Annotated

from langgraph.prebuilt import ToolRuntime, ToolNode

from AI.AgentAI.Utils.PostgresConfig import get_checkpointer,get_store
from AI.AgentAI.Utils.ModelConfig import Model
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END, START, add_messages
from AI.AgentAI.Utils.prompt import Memoryprompt
from AI.AgentAI.Utils.AllClass import MessageState as MS
llm=Model(temp=0)
prompt="""you are helpful AI that return or save  what the text say for exemple the get last 3 messges or save user prompt or get summarize of the user entire conversation you task is {task} """


class save_user_info(BaseModel):
    """Saves user preferences or personal details to the database."""

    user_info:dict=Field(description=  """
        STRICT FORMAT RULES:
        - Arrays ONLY for: likes, skills, goals, hobbies, languages
        - Strings ONLY for: name, age, location, occupation, notes
        EXEMPLE:
        CORRECT:
        {
            "likes": ["PyTorch"],
            "skills": ["Python", "Angular"],
            "name": "Youssef",
            "notes": "Prefers dark UI"
        }
        
        WRONG — never do this:
        {"likes": "PyTorch"}        ← likes must always be array
        {"skills": "Python"}        ← skills must always be array
        
        """
    )


class MemoryAI:
    _graph=None
    def __init__(self,conv_id,user_id):
        self.conv_id=conv_id
        self.user_id=user_id
        self.model = llm.model_llama()

    class MessageState(MS):
        task:str
        summary:str
    class Context(BaseModel):
        user_id: str
        conv_id:str


    async def get_user_info(self,state:MessageState,runtime: ToolRuntime[Context]) :
        """get user data"""

        store_user = runtime.store

        user_info = await store_user.aget((str(self.conv_id), str(self.user_id)), "memory_data")
        if user_info and user_info.value:

            return {"messages":[AIMessage(content=str(user_info.value))]}
        return {"messages":[AIMessage(content="none")]}

    async def configuration(self):
        config:RunnableConfig={"configurable": {"thread_id": f"{self.user_id}_{self.conv_id}"}}
        return  config

    async def save_user_info(self, state: MessageState, runtime: ToolRuntime[Context]):
        """saving user info"""
        store_user = runtime.store

        last_msg = state['messages'][-1]

        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
            user_info = last_msg.tool_calls[0]['args']['user_info']

            namespace = (str(self.conv_id), str(self.user_id))
            exist_item = await store_user.aget(namespace, "memory_data")
            exist_data = exist_item.value if exist_item else {}

            for k,v  in user_info.items():
                if k in exist_data.keys():
                    if isinstance(v,list):
                        exist_data[k]=exist_data[k]+v
                    else:
                        exist_data[k]=user_info[k]
                else:
                     exist_data[k]=user_info[k]
            update_data = {**exist_data}
            await store_user.aput(namespace, "memory_data", update_data)

            return {
                "messages": [
                    ToolMessage(
                        tool_call_id=last_msg.tool_calls[0]['id'],
                        content="Successfully saved user info"
                    ),
                    AIMessage(content="Got it! I've updated your preferences.")
                ]
            }

        return {"messages": [AIMessage(content="I couldn't find anything specific to save.")]}
    async def summarize(self):
        MAX=30
        KEEP=6
        config = await self.configuration()
        graph = await self.compilegraph()
        memo =  await graph.aget_state(config)

        messages = memo.values.get("messages",[])
        if len(messages)>MAX:
            keep_msg=messages[-KEEP:]
            summary_msg = messages[:-KEEP]
            summary_message = (
                f"This is a summary of the conversation to date: {summary_msg}\n\n"
                "Extend the summary by taking into account the new messages above:"
            )
            sys_msg = SystemMessage(content=summary_message)
            res =await self.model.ainvoke([sys_msg])
            [RemoveMessage(id = m.id) for m in summary_msg]



        return


        print(memo)




    async def callToolsaveUser(self, state: MessageState):
        sys_msg = SystemMessage(content=(
            "You are a specialized Data Extraction Agent. Your ONLY goal is to identify "
            "personal information, preferences, hobbies, or user facts from the conversation. "
            "If you find relevant info, call the 'save_user_info' tool with a clean dictionary. "
            "If no new information is present, simply acknowledge the input."
        ))
        llm_with_tools = self.model.bind_tools([save_user_info])


        clean_msgs = []
        for msg in state['messages']:
            if isinstance(msg.content, str):
                clean_msgs.append(msg)
            elif isinstance(msg.content, list):
                text = " ".join(
                    block.get("text", "")
                    for block in msg.content
                    if isinstance(block, dict) and block.get("type") == "text"
                )
                if text:
                    clean_msgs.append(type(msg)(content=text))

        all_msg = [sys_msg] + clean_msgs
        res = await llm_with_tools.ainvoke(all_msg)
        return {"messages": [res]}

    async def recent_message(self,state:MessageState,runtime: Runtime):

        messages = state["messages"]
        messages.reverse()
        print("config",messages)
    def router(self,state:MessageState):
        task= state["task"]
        print('memeory file task',task)
        if task=='HISTORY':
            return"get_user_info"
        if task=='summarize':
            return 'recent_message'
        return "callToolsaveUser"
    async def compilegraph(self):
        long = await get_store()
        short =  await get_checkpointer()
        if not MemoryAI._graph:
            graph = StateGraph(self.MessageState)
            graph.add_node("callToolsaveUser",self.callToolsaveUser)
            graph.add_node("get_user_info",self.get_user_info)
            graph.add_node("recent_message",self.recent_message)

            graph.add_node("save_user_info",self.save_user_info)

            graph.add_conditional_edges(START,self.router)
            graph.add_edge("callToolsaveUser","save_user_info")
            graph.add_edge("save_user_info",END)
            graph.add_edge("get_user_info",END)
            graph.add_edge("recent_message",END)
            MemoryAI._graph=graph.compile(checkpointer=short, store=long)


        return MemoryAI._graph
    async def return_answer(self,query:str,task:str):
        config = await self.configuration()
        human = HumanMessage(content=query)

        memoAI = await  self.compilegraph()
        input_ = {"messages": [human],"task":task}
        res= await memoAI.ainvoke(
            input=input_,
            config=config,
            context=self.Context(user_id=str(self.user_id),
                                 conv_id=str(self.conv_id)),

        )


        return res
async def main():
    x= MemoryAI(0,0)


    await x.summarize()
asyncio.run(main())












