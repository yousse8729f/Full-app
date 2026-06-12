import asyncio
import sys
from os import getenv
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from langchain.tools import tool
from langgraph.graph import START,END,StateGraph
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage,HumanMessage,AIMessage
from langchain_core.runnables import RunnableConfig
from dotenv import load_dotenv
from pydantic import Field


from AI.AgentAI.Utils.ModelConfig import Model

from AI.AgentAI.Utils.GmailConfig import google_service
from AI.AgentAI.Utils.AllClass import MessageState as ms

from AI.AgentAI.Utils.GmailFunctions import send_email,get_message_and_replies,search_email_conversation,reply_email,download_attachments_parent,get_email_messages_details
from AI.AgentAI.Utils.prompt import EMAIL_AGENT_PROMPT

load_dotenv()
@tool
def Get_Email_Full_Details(msg_id,config:RunnableConfig):
    """
    this function is used if the user need full details about a specific message
    :param msg_id: the id of the message not the thread
    :param config: keep it empty
    :return:
    """
    try:
        return get_email_messages_details(service=config.get("configurable",{}).get("gmail_service"),msg_id=msg_id)
    except Exception as e:
        return "error"



@tool
def send_Email(email:str,subject:str,body:str,attachement_paths:list,config:RunnableConfig):
    """
    this function is used to send email for a specific email,
    subject defined like title and body is the content
    :param email: the one person email that will receive the email
    :param subject: what the email is about
    :param body: the content that user wil read
    :param config: leave it empty
    :param attachement_paths: if the user specify the files path put it else put it None
    """

    try:
       return send_email(service=config.get("configurable",{}).get("gmail_service"),to=email,subject=subject,body=body,attachment_paths=attachement_paths)

    except Exception as e:
        return "error"
@tool
def reply_Email(body:str,id_mes:str,config:RunnableConfig):
    """
    This function is used to reply for specific email,
    body is the content and id_mes needed to define wich conversation to reply
    :param body: the content what the user will send
    :param id_mes: we need it to reply for a pecific conversation you will get the id_mes from search_All_Email or get_Conversation function
    :param config: leave it empty


    """
    try:
        return reply_email(service=config.get("configurable",{}).get("gmail_service"),msg_id=id_mes,body=body)

    except Exception as e:
        return "error"

@tool
def get_Conversation(thread_id:str,config:RunnableConfig):
    """
      this function is used for getting Conversation for a specific thread_id
      :param thread_id: needed to filter messages and to get it will return list of id the first one is the latest then its get old by the next
        :param config: leaves it empty
    """
    try:
        l=get_message_and_replies(service=config.get("configurable",{}).get("gmail_service"), message_id=thread_id)
        return l

    except Exception as e:
        return "error"


@tool
def search_All_Email(query:str,config:RunnableConfig):
    """

        this function needed to get thread_id witch is needed for another function
        :param query: needed to filter messages
        :param config: leaves it empty
    """
    try:
        l= search_email_conversation(service=config.get("configurable",{}).get("gmail_service"),query=query)
        return l

    except Exception as e:
        return "error"

@tool
def download_Attachemnt(id_mes:str,place:str,config:RunnableConfig):
    """

    :param id_mes: the id the msg you will get when you have the list provided by get_Conversation function
    :param place:  where to store the files
    :param config: leave it empty
    :return: this function wont return anything
    """
    download_attachments_parent(service=config.get("configurable",{}).get("gmail_service"),user_id="me",msg_id=id_mes,target_dir=place)
tools = [send_Email,search_All_Email,download_Attachemnt,get_Conversation,reply_Email,Get_Email_Full_Details]
nodetool = ToolNode(tools=tools)






class EmailAgent:
    _graph=None
    def __init__(self):
        self.prompt = EMAIL_AGENT_PROMPT
        self.llm = Model(0.2).model_Gemma().bind_tools(tools,tool_choice="auto",strict=True)
        self.runtime_config = {
            "configurable": {
                "gmail_service": google_service
            }
        }
    class MessgaesState(ms):
        task:str

    async def llmResponse(self,state:MessgaesState):
        e_prompt = self.prompt.format(task=state["task"],query=state["messages"][-1].content)
        sys_msg = SystemMessage(content=e_prompt)
        messages = [sys_msg]+state["messages"]
        res = await self.llm.ainvoke(messages)
        return {"messages":[res]}
    def should_Continue(self,state:MessgaesState):
        last_msg = state["messages"][-1]
        if hasattr(last_msg,"tool_calls") and last_msg.tool_calls:
            return "tools"
        return END
    async def compile(self):
        if not EmailAgent._graph:
            g = StateGraph(self.MessgaesState)
            g.add_node("response",self.llmResponse)
            g.add_node("tools",nodetool)
            g.add_edge(START,"response")
            g.add_conditional_edges("response",self.should_Continue,{
                "tools":"tools",
                END:END
            })
            g.add_edge("tools", "response")
            EmailAgent._graph = g.compile()
            return EmailAgent._graph
        return EmailAgent._graph
    async def answer(self,query,task):
        com = await self.compile()
        res = await com.ainvoke(input={"messages":[HumanMessage(content=query)],"task":task},config=self.runtime_config)
        print(res["messages"][-1])
        return res["messages"][-1]












    def mark_unread(self):
        pass
    def get_unread_email(self):
        pass
    def trash_email(self):
        pass




emailAgent =EmailAgent()
asyncio.run(emailAgent.answer("send a brand new  email to assilifarah685@gmail.com tell him that `this is angent sending you message to remind you that tommorow is the tandem formation` fix the sentence and send it .","the user need to send the message to assilifarah685@gmail.com "))
# asyncio.run(emailAgent.answer("look for our latest conversation for email: youssefmasmoudi05@gmail.com and reply to him. that i see about that  ","the user need to reply  to youssefmasmoudi05@gmail.com to his latest conversation "))
# asyncio.run(emailAgent.answer("look for our latest conversation for email: youssefmasmoudi05@gmail.com and give the whole conversation  ","the user need to see the latest conversation with youssefmasmoudi05@gmail.com"))
# asyncio.run(emailAgent.answer("look for our second latest conversation for email: youssefmasmoudi05@gmail.com and give the whole conversation  ","the user need to see the second latest conversation with youssefmasmoudi05@gmail.com"))
# asyncio.run(emailAgent.answer("look for our latest conversation for subject:greeting and download all the files in this directory `E:/newspringbootlangchain/PROJPYTHON/AI/AgentAI` .i think you will find two files ","the user need to download all the files from the  latest conversation with youssefmasmoudi05@gmail.com"))
# l=search_email_conversation(service=google_service,query="subject:greeting")
# print(l)
# c=get_message_and_replies(service=google_service,message_id="19ea92fb203fca5e")



