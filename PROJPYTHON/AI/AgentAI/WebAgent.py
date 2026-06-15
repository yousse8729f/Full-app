
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain_tavily import TavilySearch
from AI.AgentAI.Utils.AllClass import AllUrlResult,MessageState as ms
from AI.AgentAI.Utils.ModelConfig import Model
from AI.AgentAI.Utils.prompt import webPrompt
from langgraph.graph import START,END,StateGraph
from dotenv import load_dotenv
from os import getenv

load_dotenv()
SERP=getenv('SERP_API')
TAVILY=getenv('TAVILY_API_KEY')



class WebAgent:
    _graph=None
    def __init__(self):
        self.llm=Model(temp=0.2).model_Grog()
    class MessageState(ms):
        task:str
    async  def Search_Tavily(self,state:MessageState):
        tavily = TavilySearch(
            max_results=3,
            include_answer=True,
        )
        message = state["messages"][-1].content
        llm_tool=self.llm.bind_tools([tavily])

        sys_Search=SystemMessage(content=webPrompt.format(task=state["task"],query=message))
        msg=[sys_Search]
        res = await llm_tool.ainvoke(msg)

        return {"messages":[res]}




    async def final_res(self,state:MessageState):
        sys_convert=SystemMessage(content="you are helpful who convert json to a specific format of json")
        llm_struture=self.llm.with_structured_output(schema=AllUrlResult)
        msg=[sys_convert]+state['messages']
        res = await llm_struture.ainvoke(msg)
        content_str = res.model_dump_json()
        return {"messages":[AIMessage(content=content_str)]}
    async def compileweb(self):
        if not WebAgent._graph:
            graph = StateGraph(self.MessageState)
            graph.add_node("Search_Tavily",self.Search_Tavily)
            graph.add_node("final_res",self.final_res)
            graph.add_edge(START,"Search_Tavily")
            graph.add_edge("Search_Tavily","final_res")
            graph.add_edge("final_res",END)
            WebAgent._graph=graph.compile()
        return WebAgent._graph
    async def return_answer(self,questions: list[str],task):
        webai = await self.compileweb()
        results = []

        for question in questions:
            human = HumanMessage(content=question)
            res = await webai.ainvoke(input={"messages": [human],"task":task})
            results.append({
                "question": question,
                "result": res["messages"][-1].content
            })

        return results










