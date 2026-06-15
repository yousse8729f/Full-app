from typing import TypedDict, Annotated, Literal

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from pydantic import BaseModel, Field


class UrlResult(BaseModel):
    source: str = Field(description="the source of the url")
    url: str = Field(description='the url of the provided one')
    description: str = Field(description='the description of the url if there is any return empty string')


class AllUrlResult(BaseModel):
    UrlList: list[UrlResult]
    summary:str=Field(description='this is a summary on how this url solve user probleme')

class MessageState(TypedDict):
        messages:Annotated[list[BaseMessage],add_messages]
class Enhance(BaseModel):
    original_query:str=Field(description='the original query of the user ')
    rewritten_query:str=Field(description='Full clean version of the query')

    needs_realtime_data:bool=Field(description="needs data in the internet or not?")
    needs_historical_context:bool=Field(description="does it need a knowledge what the user said before? ")
    needs_document_search:bool=Field(description="does it need Files,user send it before?")
    needs_github:bool=Field(description="does it need to manipulate github")
    needs_email:bool=Field(description="does it need to manipulate email and send email")
    complexity:Literal["simple","complexe"]=Field(description="based on the subquestion how much agent we need.  simple: mean one question ,if there is more than one subquestion then its complexe YOU MUST RESPOND ONLY WITH complexe OR simple ")

class Step(BaseModel):
    step:str=Field(description="what are the steps for the plan start from 1 must be in string exmple '1'")
    agent:Literal["memory_agent","rag_agent","web_agent","Sql_Image_agent","email_agent","github_agent"]=Field(description="choose the appropriate agent")
    task:str=Field(description="precise what should he do")
    sub_questions_assigned:list=Field(description="question that are needed for the specific agent for the Memeory-agent one question is enough")



class Orch(BaseModel):
    plan_reasoning:str=Field(description="explain why you choose these agent")
    execution_order:Literal["sequential","parallel"]=Field(description="what kind of execution needed")
    steps:list[Step]=Field(description="All the agents and their mission")


class postDetails(BaseModel):
    content: str = Field(description="title of the project")
    description: str = Field(description='description de post')
    file_url:str=Field(description= """for the id in the post_attachement return like that return the path of the file it start  """)


class AllpostDetails(BaseModel):
    posts: list[postDetails] = Field(description="array of dict of ProductDetails ")



class filedetails(BaseModel):
        id:str=Field(description="that the number the of the post exmple:'1' ")
        Important:bool=Field(description="is it important related to studies and work , exmple true. must be a boolean")
        resume:str=Field(description="explain what the file is about")

class fileList(BaseModel):
        Allfilelist:list[filedetails]
