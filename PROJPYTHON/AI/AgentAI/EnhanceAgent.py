import asyncio

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph,START,END
from AI.AgentAI.Utils.ModelConfig import Model
from AI.AgentAI.Utils.prompt import QUERY_ENHANCER_PROMPT
from AI.AgentAI.Utils.AllClass import Enhance,MessageState as ms
class EnhanceAi:
    def __init__(self):
        self.llm=Model(temp=0.2).model_Grog()
        self.prompt=QUERY_ENHANCER_PROMPT

    class MessageState(ms):
        user:str

    async def final_Answer(self,state:MessageState):
        sys_mdg=SystemMessage(content=self.prompt.format(query=state["user"]))
        llm_ouput = self.llm.with_structured_output(schema=Enhance)
        allmsg=[sys_mdg]+state["messages"]
        output:Enhance = await llm_ouput.ainvoke(allmsg)
        resformat = output.model_dump_json()
        return {"messages":[AIMessage(content=resformat)]}
    async def Compile(self):
        graph = StateGraph(self.MessageState)
        graph.add_node("final_Answer",self.final_Answer)
        graph.add_edge(START,"final_Answer")
        graph.add_edge("final_Answer",END)
        return graph.compile()
    async def answer(self,q):
        enhance =await self.Compile()
        input_={"messages":[HumanMessage(content=q)],"user":q}
        res = await enhance.ainvoke(input=input_)

        return res
# async def main():
#     x= EnhanceAi()
#     await x.answer("what do i like")
# asyncio.run(main())


