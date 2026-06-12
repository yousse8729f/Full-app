import asyncio
import datetime
import json
from typing import Any

from langgraph.graph import  StateGraph,START,END
from langchain_core.messages import AIMessage, HumanMessage


from AI.AgentAI.SQLAGENT import SQLAgent
from AI.AgentAI.DocumentAgentMas import ImageAgent
from AI.AgentAI.Utils.AllClass import MessageState as ms, MessageState


date=datetime.datetime.now()
class SqlImageAi:
    _graph = None

    def __init__(self,date):
        self.sql_agent=SQLAgent()
        self.image_ai = ImageAgent(date)
    class MessageState(ms):
        file_url:str
        sql_answer:list
        image_answer:dict[str, Any]

    async def Sql_answer(self,state:MessageState):
        res= await self.sql_agent.answer(state["messages"][0].content)
        print(res)
        return {"sql_answer":[json.loads(res)]}
    async def Image_answer(self,state:MessageState):
        sql_res_dict = state["sql_answer"][0] if state["sql_answer"] else {}
        posts = sql_res_dict.get("posts", [])


        listfile = [s["file_url"] for s in posts if "file_url" in s]
        print(listfile,"\n",posts,"\n",sql_res_dict)
        res = await self.image_ai.answer(listfile)
        print(res)
        return {"image_answer": json.loads(res)}
    async def Sync(self,state:MessageState):
        l=[]
        sql_posts = state["sql_answer"][0].get("posts", []) if state["sql_answer"] else []
        raw_image_data = state.get("image_answer")
        ai_file_list = raw_image_data.get("Allfilelist", [])


        for s, i in zip(sql_posts, ai_file_list):

            if i.get('Important'):
                d={"about":s,"file_about":i.get('resume')}
                l.append(d)
        return {"messages":[AIMessage(content=f'{l}')]}
    async def Compose(self):
        if not SqlImageAi._graph:
            graph= StateGraph(MessageState)
            graph.add_node("Sql_answer",self.Sql_answer)
            graph.add_node("Image_answer",self.Image_answer)
            graph.add_node("Sync",self.Sync)
            graph.add_edge(START,"Sql_answer")
            graph.add_edge("Sql_answer","Image_answer")
            graph.add_edge("Image_answer","Sync")
            graph.add_edge("Sync",END)
            SqlImageAi._graph=graph.compile()
        return  SqlImageAi._graph
    async def answer(self,q):
        si_ai=await self.Compose()
        res= await si_ai.ainvoke(input={"messages":[HumanMessage(content=q)]})
        print(res["messages"][-1])
        return res["messages"][-1]
# async def main():
#     x=SqlImageAi(date)
#     await x.answer('give me the best 3 post in the last 7 day')
# asyncio.run(main())













    


