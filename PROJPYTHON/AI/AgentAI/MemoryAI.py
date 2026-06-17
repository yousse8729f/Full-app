import asyncio
import sys

from langchain_core.globals import set_llm_cache
from langchain_core.runnables import RunnableConfig
from langchain_community.cache import RedisCache

from langchain.messages import RemoveMessage

from AI.AgentAI.Utils.RedisConfig import cache

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from typing import  Annotated
from langchain_community.utils.math import cosine_similarity



from AI.AgentAI.Utils.PostgresConfig import get_checkpointer
from AI.AgentAI.Utils.ModelConfig import Model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END, START, add_messages
from AI.AgentAI.Utils.prompt import MEMORY_PROMPT
from AI.AgentAI.Utils.AllClass import MessageState as MS
from langchain_community.cache import RedisCache





class MemoryAI:
    redis_cache = RedisCache(redis_=cache, ttl=3600 * 24 * 7)
    set_llm_cache(redis_cache)
    _graph=None
    def __init__(self,conv_id,user_id):
        self.conv_id=conv_id
        self.user_id=user_id
        self.model = Model(0.2).model_llama()
        self.helper = Model(0.2).model_llama()
        self.config: RunnableConfig = {"configurable": {"thread_id": f"{self.user_id}_{self.conv_id}"}}
        self.embeding = Model(0.2).model_embedding()
        self.prompt=MEMORY_PROMPT

    class MessageState(MS):
        task:str
        summary:str
        old_messages:Annotated[list,add_messages]
        search_msg:list
        current_state:Annotated[list,add_messages]


    async def summarize(self,state:MessageState):
        MAX=30
        KEEP=6


        messages = state.get("messages",[])
        if len(messages)>MAX:
            keep_msg=messages[-KEEP:]
            summary_msg = messages[:-KEEP]
            current_summary = state.get("summary", "")
            prompt= self.prompt.format(task=state["task"])

            summary_message = (
                f"This is a piece of the conversation to date and some summary: {summary_msg }\n{current_summary}\n\n"
                "Extend the summary by taking into account the new messages above:"
            )
            sys_msg = SystemMessage(content=prompt+summary_message)
            res =await self.model.ainvoke([sys_msg])
            delete_msg=[RemoveMessage(id = m.id) for m in summary_msg]
            return \
            {
                "messages":delete_msg+keep_msg,
                "summary":res.content,
                "old_messages":summary_msg
            }
        return {}

    async def retrive_old_messges(self, state: MessageState):
        try:

            if not state.get("old_messages") or not state.get("messages") or len(state["messages"]) < 4:
                return {"search_msg": []}

            msg_close = []
            seen_message_ids = set()


            archive_objects = [i for i in state["old_messages"] if
                               isinstance(i, (HumanMessage, AIMessage)) and hasattr(i, "content")]
            last_4_objects = [i for i in state["messages"][-4:] if
                              isinstance(i, (HumanMessage, AIMessage)) and hasattr(i, "content")]

            archive_texts = [msg.content for msg in archive_objects]
            last_4_texts = [msg.content for msg in last_4_objects]

            if not archive_texts or not last_4_texts:
                return {"search_msg": []}

            archive_vector = await self.embeding.aembed_documents(archive_texts)
            last_4_vector = await self.embeding.aembed_documents(last_4_texts)

            similarity_matrix = cosine_similarity(last_4_vector, archive_vector)

            for recent_idx, archive_scores in enumerate(similarity_matrix):
                for archive_idx, score in enumerate(archive_scores):
                    if score > 0.75:
                        matched_msg = archive_objects[archive_idx]

                        if matched_msg.id not in seen_message_ids:
                            msg_close.append(matched_msg)
                            seen_message_ids.add(matched_msg.id)

            return {"search_msg": msg_close}
        except Exception as e:
            print(f"Error in lookup: {e}")
            return {"search_msg": []}
    async def current_state(self,state:MessageState):
        try:
            summary_text = state.get("summary", "")
            old_messages = state.get("old_messages", [])
            user = state["messages"]+[summary_text]+old_messages
            prompt = self.prompt.format(task=state["task"])
            sys_msg = SystemMessage(content=prompt)
            msg = [sys_msg]+user
            res = await self.helper.ainvoke(msg)
            return {"current_state":[res]}
        except Exception as e:
            print("error",e)
            return {"current_state":[]}



    def router(self,state:MessageState):
        if state["task"]=="summary":
            return "summary"
        elif state["task"]=="retrieve":
            return "retrieve"
        elif state["task"]=="state":
            return "state"
        return END

    async def compilegraph(self):
        if MemoryAI._graph is None:
            check = await get_checkpointer()
            graph = StateGraph(self.MessageState)
            graph.add_node("summary",self.summarize)
            graph.add_node("retrieve",self.retrive_old_messges)
            graph.add_node("state",self.current_state)
            graph.add_conditional_edges(START,self.router,{
                "summary":"summary",
                "retrieve":"retrieve",
                "state": "state"
            })
            graph.add_edge("summary",END)
            graph.add_edge("retrieve",END)
            graph.add_edge("state",END)
            MemoryAI._graph = graph.compile(checkpointer=check)
            return MemoryAI._graph
        return MemoryAI._graph
    async def return_answer(self,query:str,task:str):

        human = HumanMessage(content=query)


        memoAI = await  self.compilegraph()
        input_ = {"messages": [human],"task":task}
        res= await memoAI.ainvoke(

            input=input_,
            config=self.config,


        )

        # print(res)

        return {"memeory_agent": [{"current_state": res.get("current_state", [])},
                                  {"old_messages": res.get("old_messages", [])}]}
# async def main():
#     x= MemoryAI(0,0)
#
#
#     await x.return_answer("my name is youssef and i just add backend spring boot to my angular project","state")
# asyncio.run(main())












