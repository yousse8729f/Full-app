import asyncio
import base64
import datetime

import requests
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredImageLoader
from langgraph.graph import START, StateGraph, END
from AI.AgentAI.Utils.AllClass import fileList

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from dotenv import load_dotenv
from os import getenv

from pydantic import BaseModel, Field

from AI.AgentAI.Utils.AllClass import MessageState as ms
load_dotenv()
api = getenv("GROG_API")
# x=UnstructuredImageLoader('http://localhost:8080/api/attachments/display/e22bfff2-87c8-44ae-90ea-86a3d7bee216')
# l=x.load()
# print(l)

class ImageAgent:
    _graph=None
    def __init__(self,date):
        self.now = date
        self.llm2=ChatGroq(model="llama-3.3-70b-versatile",api_key=api)


    class MessagesState(ms):
        file_url:list[str]
        file_content:list[dict]


    def AnalyseFile(self,state:MessagesState):

            all_content=[]
            file_urls = state.get("file_url", [])
            if not file_urls:
                return {"file_content": []}

            try:
                for i, url in enumerate(file_urls):
                    if "pdf" not in url.lower():
                        image= UnstructuredImageLoader(file_path=url,strategy="fast")
                        loader = image.load()
                        file_content = '\n\n'.join(doc.page_content for doc in loader)
                        all_content.append({"data":file_content,"number":i})
                        print(file_content)

                    else:
                        pdf= PyPDFLoader(file_path=url)
                        loader=pdf.load()
                        file_content='\n\n'.join( doc.page_content for doc in loader)
                        print(file_content)
                        all_content.append({"data":file_content,"number":i+1})


            except Exception as e:
               return{
                "file_content": "",
            "messages": [AIMessage(content=f"Image fetch failed: {e}")]
                 }
            return {"file_content":all_content}

    async def AgentAnswer(self,state:MessagesState):
        file_content = state.get("file_content", [])
        if not file_content:
            return {"messages": [AIMessage(content='{"Allfilelist": []}')]}
        global human_message


        example_output = {
            "Allfilelist": [
                {
                    "id": "1",
                    "Important": True,
                    "resume": "A technical document covering Java exception handling best practices."
                }
            ]
        }

        sys_msg = SystemMessage(
            content=(
                """fToday is {self.now}. You are a professional document classifier.
                Your task is to analyze  provided and categorize them into the 'Allfilelist' schema.

                RULES:
                - 'Important': Set to True for tech, studies, or work. Set to False for memes, personal logs, or junk.
                - 'id': Use the 'number' provided in the input as a string.
                - 'resume': A one-sentence summary of the file content.
                STRICT RULES:
                1. Output ONLY a single JSON object.
                2. NEVER wrap the JSON in a list [].
                4. If content is about studies/work, Important=True.

                EXAMPLE:
                **IMPORTANT RULE** FOLLOAW THE EXEMPLE
                fOutput JSON: { {
            "Allfilelist": [
                {
                    "id": "1",
                    "Important": True,
                    "resume": "A technical document covering Java exception handling best practices."
                }
            ]
        }}

                STRICT REQUIREMENT: You must return ONLY the structured JSON mapping the provided file_content."""
            )
        )
        file_content=state["file_content"]


        human_message = HumanMessage(content=f"analyse those file {file_content} ")
        structured_llm = self.llm2.with_structured_output(fileList)
        try:
            res = await structured_llm.ainvoke([sys_msg, human_message])
            # Ensure we return a stringified JSON for the message content
            return {"messages": [AIMessage(content=res.model_dump_json())]}
        except Exception as e:
            print(f"LLM Structure Error: {e}")
            empty_res = fileList(Allfilelist=[])
            return {
                "messages": [AIMessage(content=empty_res.model_dump_json())],

            }
    async def Compile(self):
        if not ImageAgent._graph:
            graph=StateGraph(self.MessagesState)
            graph.add_node("AnalyseFile",self.AnalyseFile)
            graph.add_node("AgentAnswer",self.AgentAnswer)

            graph.add_edge(START,"AnalyseFile")
            graph.add_edge("AnalyseFile","AgentAnswer")
            graph.add_edge("AgentAnswer",END)
            ImageAgent._graph=graph.compile()

        return ImageAgent._graph
    async def answer(self,file_url):

         agentImage =await self.Compile()
         res =await  agentImage.ainvoke(
            {
                "messages": [HumanMessage(
                    content="Analyse the file "
                )],
                "file_url": file_url ,

                "file_content":[]


            },

            )

         return res["messages"][-1].content
# async def main():
#     x=ImageAgent(datetime.datetime.now())
#     await x.answer([])
# asyncio.run(main())




















