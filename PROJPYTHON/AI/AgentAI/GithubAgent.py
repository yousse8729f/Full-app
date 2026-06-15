from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import START,END,StateGraph
from langchain.messages import (HumanMessage,AIMessage,SystemMessage)
from langgraph.prebuilt import ToolNode



from AI.AgentAI.Utils.AllClass import MessageState as ms
import asyncio

from AI.AgentAI.Utils.ModelConfig import Model
from AI.AgentAI.Utils.prompt import GITHUB_AGENT_PROMPT


async def get_tools():
    client = MultiServerMCPClient({
            "github":{
                "command":"python",
                "args":["E:/newspringbootlangchain/PROJPYTHON/AI/AgentAI/Utils/GitHubFunctions.py"],
                "transport":"stdio"
            }
        })
    return await client.get_tools()

class GithubAgent:
    _graph=None
    _tools=None
    def __init__(self):
        self.llm = None
        self.prompt = GITHUB_AGENT_PROMPT

    class MessgaesState(ms):
        task: str
    async def _ensure_tools(self):
        if GithubAgent._tools is None:
            GithubAgent._tools=await get_tools()
        if self.llm is None:
            self.llm=Model(0.2).model_Gemma().bind_tools(GithubAgent._tools,tool_choice="auto",strict=True)
        return GithubAgent._tools


    async def llmResponse(self, state: MessgaesState):
        e_prompt = self.prompt.format(task=state["task"], query=state["messages"][-1].content)
        sys_msg = SystemMessage(content=e_prompt)
        messages = [sys_msg] + state["messages"]
        res = await self.llm.ainvoke(messages)
        return {"messages": [res]}

    def should_Continue(self, state: MessgaesState):
        last_msg = state["messages"][-1]
        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
            return "tools"
        return END

    async def compile(self):
        if not GithubAgent._graph:
            tools = await self._ensure_tools()
            nodetool = ToolNode(tools)
            g = StateGraph(self.MessgaesState)
            g.add_node("response", self.llmResponse)
            g.add_node("tools", nodetool)
            g.add_edge(START, "response")
            g.add_conditional_edges("response", self.should_Continue, {
                "tools": "tools",
                END: END
            })
            g.add_edge("tools", "response")
            GithubAgent._graph = g.compile()
            return GithubAgent._graph
        return GithubAgent._graph

    async def answer(self, query, task):
        com = await self.compile()
        res = await com.ainvoke(input={"messages": [HumanMessage(content=query)], "task": task},
                                )


        return res["messages"][-1]
# githuA = GithubAgent()
# asyncio.run(githuA.answer("create an issues say 'there is a bug in the Home controller' in CinemaFilmProj with lable of bug and documentation"," "))