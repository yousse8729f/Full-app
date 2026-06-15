import asyncio
import json
from datetime import datetime

from langchain_core.globals import set_llm_cache

from langchain_community.cache import RedisCache


from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from langgraph.graph import StateGraph,START,END

# from AI.AgentAI.GithubAgent import GithubAgent
# from AI.AgentAI.GmailAgent import EmailAgent
from AI.AgentAI.Sql_ImageAI import SqlImageAi
from AI.AgentAI.Utils.PostgresConfig import get_checkpointer
from AI.AgentAI.WebAgent import WebAgent
from AI.AgentAI.RagAgent import RagAgent
from AI.AgentAI.MemoryAI import MemoryAI
from AI.AgentAI.EnhanceAgent import EnhanceAi
from AI.AgentAI.Utils.prompt import ORCHESTRATOR_PROMPT,REFINE_PROMPT
from AI.AgentAI.Utils.ModelConfig import  Model
from AI.AgentAI.Utils.AllClass import Orch, MessageState as sm,Step

from AI.AgentAI.Utils.RedisConfig import cache

redis_cache = RedisCache(redis_=cache,ttl=3600*24*7)
set_llm_cache(redis_cache)
class OrchestratorAgent:
   _graph=None

   async def configuration(self):
      config: RunnableConfig = {
         "configurable": {
            "thread_id": f"{self.user_id}_{self.conv_id}"
         }
      }
      return config
   def __init__(self,user_id,conv_id,date,chunks=None):
      self.conv_id=conv_id
      self.user_id=user_id
      self.llm = Model(temp=0.2).model_llama_Grog()
      self.prompt=ORCHESTRATOR_PROMPT
      self.RagAgent=RagAgent(user_id,conv_id)
      self.SqlImageAi=SqlImageAi(date)
      self.chunk=chunks
      # self.GithubAgent=GithubAgent()
      # self.EmailAgent = EmailAgent()
      self.MemoryAgent=MemoryAI(conv_id,user_id)
      self.EnhanceAgent = EnhanceAi()
      self.webAgent=WebAgent()
      self.refine_prompt=REFINE_PROMPT

   def clean_messages(self, messages: list) -> list:
      clean = []
      for msg in messages:
         if isinstance(msg.content, str):
            clean.append(msg)
         elif isinstance(msg.content, list):
            text = " ".join(
               block.get("text", "")
               for block in msg.content
               if isinstance(block, dict) and block.get("type") == "text"
            )
            if text:
               clean.append(type(msg)(content=text))
      return clean
   class MessageState(sm):
      task:str
      user: str
      agent_results:list



   async def EnhanceAi_Action(self,state:MessageState):
      print("ENHANCEAI")
      res= await self.EnhanceAgent.answer(state['user'])
      return {"messages":[res["messages"][-1]]}
   async def plan(self,state:MessageState):
      lstmsg= json.loads(state["messages"][-1].content)
      print("plan",lstmsg)
      argPrompt= self.prompt.format(
         original_query=lstmsg["original_query"],
         rewritten_query=lstmsg["rewritten_query"],
         needs_realtime_data=lstmsg["needs_realtime_data"],
         needs_historical_context=lstmsg["needs_historical_context"],
         needs_document_search=lstmsg["needs_document_search"],
         complexity=lstmsg["complexity"],
         needs_email=lstmsg["needs_email"],
         needs_github=lstmsg["needs_github"]
      )
      sysmsg=SystemMessage(content=argPrompt)
      Allmsg=[sysmsg]+self.clean_messages(state["messages"])
      llm_no_cache = self.llm.bind(cache=False)
      llm_output = llm_no_cache.with_structured_output(schema=Orch)
      res:Orch = await  llm_output.ainvoke(Allmsg)
      Format=  res.model_dump_json()
      print(Format)
      return {"messages":[AIMessage(content=Format)]}
   async def _run_step(self, step: dict, state: MessageState) -> dict:
      print("runstep")
      """Runs one step — calls the right agent with the right questions."""
      agent = step["agent"]
      task = step["task"]
      questions = step["sub_questions_assigned"]

      if agent == "web_agent":
         res = await self.webAgent.return_answer(questions,task)
      # elif agent=="github_agent":
      #    res= await self.GithubAgent.answer(questions[0],task)
      # elif agent=='email_agent':
      #    res= await self.EmailAgent.answer(questions[0],task)

      elif agent == "rag_agent":
         res = await self.RagAgent.answer(questions,self.chunk)

      elif agent == "memory_agent":
         res = await self.MemoryAgent.return_answer(questions[0], task)
         res=[res["messages"][-1].content]
      elif agent == "Sql_Image_agent":
         res = await self.SqlImageAi.answer(questions[0])
         if isinstance(res, AIMessage):
            res = [res.content]
         else:
            res = [res]


      else:
         res = []
      print(res)

      return {
         "agent": agent,
         "results": res
      }
   async def execute_plan(self,state:MessageState):
         print("exuteqaiton")

         plan = json.loads(state["messages"][-1].content)
         steps = plan["steps"]
         execution = plan["execution_order"]
         results = []

         if execution == "parallel":
            async with asyncio.TaskGroup() as tg:
               tasks = [
                  tg.create_task(self._run_step(step, state))
                  for step in steps
               ]
            results = [t.result() for t in tasks]
            print("pararlele result",results)

         elif execution == "sequential":
            for step in steps:
               res = await self._run_step(step, state)
               results.append(res)
         print("sequentiatl result",results)

         return {
            "agent_results": results,
            "messages": [AIMessage(content=json.dumps(results))]
         }
   async def RefineAi_Action(self,state:MessageState):


      prompt=self.refine_prompt.format(original_query=state["user"],agent_results=state["agent_results"])
      sys_msg=SystemMessage(content=prompt)
      all_msg=[sys_msg]+self.clean_messages(state["messages"])
      res= await self.llm.ainvoke(all_msg)
      return {"messages":[res]}


   async def Compile(self):
      if not OrchestratorAgent._graph:
         short = await get_checkpointer()

         graph = StateGraph(self.MessageState)
         graph.add_node("EnhanceAi_Action", self.EnhanceAi_Action)
         graph.add_node("plan", self.plan)
         graph.add_node("execute_plan", self.execute_plan)
         graph.add_node("RefineAi_Action", self.RefineAi_Action)

         graph.add_edge(START, "EnhanceAi_Action")
         graph.add_edge("EnhanceAi_Action", "plan")
         graph.add_edge("plan", "execute_plan")
         graph.add_edge("execute_plan","RefineAi_Action")
         graph.add_edge("RefineAi_Action", END)
         OrchestratorAgent._graph=graph.compile(checkpointer=short)
      return OrchestratorAgent._graph

   async def answer(self,q:str):
      human_input = q.lower().strip()
      conf = await self.configuration()

      mainagent= await self.Compile()
      input_={"messages":[HumanMessage(content=human_input)],"user":human_input,"task":'',"agent_results":[]}
      res=await mainagent.ainvoke(input =input_, config=conf)
      return res
      # async for chunk in  mainagent.astream_events(input =input_,version="v2", config=conf):
      #    if chunk:
      #       events=chunk.get("event")
      #       node = chunk.get("metadata",{}).get('langgraph_node','')
      #       if node=='plan':
      #          yield {'type':'tool','text':'thinking'}
      #       if node=='Search_Tavily':
      #          yield {'type':'tool','text':'searching web'}
      #       if node=='save_user_info':
      #          yield {'type':'tool','text':'save info'}
      #       if node=='save_user_info':
      #          yield {'type':'tool','text':'save info'}
      #       if node=='get_user_info':
      #          yield {'type':'tool','text':'get info'}
      #       if events=='on_retriever_start':
      #          yield {'type':'tool','text':'retrieve document'}
      #
      #       if events=="on_chat_model_stream" and node=='RefineAi_Action':
      #          content = chunk.get("data").get('chunk').content
      #          if content:
      #             yield {'type':'message','text':content}






#
# async def main():
#    x = OrchestratorAgent(0, 0, datetime.now())
#    return await x.answer("hello")
#
#
# asyncio.run(main())



