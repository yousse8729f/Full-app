import asyncio
import re
import uuid
from os import getenv
from pathlib import Path
from AI.AgentAI.Utils.AllClass import AllpostDetails,MessageState as ms
from langgraph.graph import START, StateGraph, END, add_messages
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage, BaseMessage, SystemMessage
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit

from dotenv import load_dotenv

import urllib.parse

from AI.AgentAI.Utils.ModelConfig import Model

cur=Path(__file__).parent
env_path=cur/'.env'

load_dotenv(dotenv_path=env_path)
user=getenv('POSTGRES_USER')
password=urllib.parse.quote_plus(getenv('POSTGRES_PASSWORD'))
host=getenv("POSTGRES_HOST")
db=getenv('POSTGRES_DB')
port=getenv('POSTGRES_PORT')

class SQLAgent:

    _graph=None
    def __init__(self):

        self.db = SQLDatabase.from_uri(f"postgresql://{user}:{password}@{host}:{port}/{db}")


        self.llm = Model(temp=0.2).model_llama_Grog()

        self.toolKit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        self.Tools = self.toolKit.get_tools()
        self.sql_db_list_tables = self.gettool("sql_db_list_tables")
        self.sql_db_schema= self.gettool("sql_db_schema")
        self.sql_db_query = self.gettool("sql_db_query")
        self.sql_db_query_checker = self.gettool("sql_db_query_checker")

    def  gettool(self,name: str):
        return next(t for t in self.Tools if t.name == name)


    class MessageState(ms):
        sql_query: str

    GENERATE_PROMPT = """
    You are a specialized {dialect} Expert. Your sole task is to generate a valid SELECT statement based on the provided schema and user requirements.

    ### DATABASE CONTEXT:
    - Primary Tables: `post` and `post_attachment`.
    - Relationships: `post_attachment` links to `post` (typically via `post_id` or similar foreign key).

    ### LOGIC RULES:
    1. IF A SPECIFIC POST ID IS PROVIDED:
       - Select the `content` and `id` from the `post_attachment` table filtered by that post ID.

    2. IF NO SPECIFIC POST ID IS PROVIDED:
       - Select the 3 best subjects/records from `post.content`.
       - Join with `post_attachment` to include the corresponding `id, file_path` from `post_attachment`.

    ### CONSTRAINTS:
    - Return ONLY the raw SQL. 
    - Do NOT include markdown blocks (```sql), explanations, or preamble.
    - LIMIT: If no specific ID is provided, limit the result to {top_k} rows.
    - STRICT: Only use SELECT statements. DML statements (INSERT, UPDATE, DELETE, DROP) are strictly FORBIDDEN.

    ### USER REQUEST:
    {user_input}

    ### SCHEMA:
    {schema}
    """


    def get_all_list_tables(self, state: MessageState):
        """Step 1 – Restrict to ONLY two tables."""
        # Hardcoding the focus tables ensures the LLM doesn't hallucinate other tables
        tables = "post, post_attachment"
        print(f"Restricting search to: {tables}")
        return {"messages": [AIMessage(content=f"Available tables: {tables}")]}


    def getallSchema(self,state: MessageState):
        """Step 2 – fetch the full schema directly (no LLM tool-call trick)."""
        tables_msg = next(
            (m for m in reversed(state["messages"])
             if isinstance(m, AIMessage) and "Available tables:" in m.content),
            None,
        )
        tables_str = (
            tables_msg.content.replace("Available tables: ", "").strip()
            if tables_msg else ""
        )
        schema_result = self.sql_db_schema.invoke({"table_names": tables_str})
        return {"messages": [AIMessage(content=f"Database schema:\n{schema_result}")]}

    async def generate_query(self, state: MessageState):
        """Step 3 – Generate SQL with corrected prompt formatting."""

        # Get the schema from the previous step's message
        schema_msg = next(
            (m for m in reversed(state["messages"])
             if "Database schema:" in m.content),
            None
        )
        current_schema = schema_msg.content if schema_msg else "No schema found"
        user_query = state["messages"][0].content  # The initial human question

        # Format the prompt correctly with all required variables
        formatted_prompt = self.GENERATE_PROMPT.format(
            dialect=self.db.dialect,
            top_k=5,
            user_input=user_query,
            schema=current_schema
        )

        sys_msg = SystemMessage(content=formatted_prompt)

        response = await self.llm.ainvoke([sys_msg] + state["messages"])

        sql = response.content.strip()

        sql = re.sub(r"```(?:sql)?", "", sql, flags=re.IGNORECASE).replace("```", "").strip()

        print(f"[generate_query] SQL → {sql}")
        return {"messages": [AIMessage(content=f"Generated SQL:\n{sql}")], "sql_query": sql}


    def check_query(self,state: MessageState):

        sql = state.get("sql_query", "")
        if not sql:
            print("no sql")
            return {}

        checked = self.sql_db_query_checker.invoke({"query": sql})
        corrected = checked.strip()
        match = re.search(r"```(?:sql)?\s*(.*?)```", corrected,  re.IGNORECASE)
        if match:
            corrected = match.group(1).strip()

        print(f"[check_query] verified SQL → {corrected}")
        return {
            "messages": [AIMessage(content=f"Verified SQL:\n{corrected}")],

        }


    def execute_query(self,state: MessageState):
        """Step 5 – run the verified SQL directly (no LLM needed)."""
        sql = state.get("sql_query", "")
        if not sql:
            return {"messages": [AIMessage(content="No SQL query to execute.")]}

        try:
            result = self.sql_db_query.invoke({"query": sql})
        except Exception as e:
            result = f"Query execution error: {e}"

        print(f"[execute_query] result → {result}")
        return {"messages": [ToolMessage(content=str(result), tool_call_id=str(uuid.uuid4()))]}


    async def final_answer(self,state: MessageState):
        """Step 6 – turn the raw DB result into a readable answer."""

        sys_msg = SystemMessage(content=(
            "You are a reporting assistant tasked with converting raw SQL results into a structured JSON report. "
            "You MUST return a JSON object that matches the AllpostDetails schema exactly.\n\n"

            "### CONTENT QUALITY FILTER (CRITICAL):\n"
            "- Only include 'serious' posts that contain educational, professional, or informative value.\n"
            "- IGNORE system messages, lobby notifications, test posts, or meaningless text.\n"
            "- Example of what to IGNORE: 'new user joined', 'test', 'hello', '...', 'post pdf file test'.\n"
            "- Example of what to INCLUDE: Technical tutorials, architectural styles, project updates, or course materials.\n\n"

            "### FIELD MAPPING RULES:\n"
            "1. 'content': Use the title or main subject found in the SQL result.\n"
            "2. 'description': Provide a concise 1-sentence summary of why this post is significant.\n"
            "3. 'file_url': Convert the attachment in the file_path\n\n"

            "### EXAMPLE OF EXPECTED OUTPUT:\n"
            "If the SQL result contains: [('Microservices Guide', 'ca1f548f'), ('test post', '59960c7c')]\n"
            "Your response should ONLY include the serious post:\n"
            "{\n"
            "  \"posts\": [\n"
            "    {\n"
            "      \"content\": \"Microservices Guide\",\n"
            "      \"description\": \"A comprehensive guide detailing microservices architectural styles and implementation.\",\n"
            "      \"file_url\": \"E:/projectganara/Microservice.pdf\"\n"
            "    }\n"
            "  ]\n"
            "}\n\n"

            "### CONSTRAINTS:\n"
            "- Root Key: Must be 'posts'.\n"
            "- DO NOT include markdown code blocks (```json).\n"
            "- If no serious posts are found, return: {\"posts\": []}\n"
            "- Every post in the list MUST have all three fields: 'content', 'description', 'file_url'."
        ))

        llmWithStructure=self.llm.with_structured_output(schema=AllpostDetails)
        response:AllpostDetails  =await llmWithStructure.ainvoke([sys_msg] + state["messages"])
        return {"messages": [AIMessage(content=response.model_dump_json(indent=2))]}

    async def Compile(self):
        if not SQLAgent._graph:
            graph = StateGraph(self.MessageState)

            graph.add_node("get_all_list_tables", self.get_all_list_tables)
            graph.add_node("getallSchema", self.getallSchema)
            graph.add_node("generate_query",self.generate_query)
            graph.add_node("check_query",self.check_query)
            graph.add_node("execute_query",self.execute_query)
            graph.add_node("final_answer",self.final_answer)

            graph.add_edge(START,                 "get_all_list_tables")
            graph.add_edge("get_all_list_tables", "getallSchema")
            graph.add_edge("getallSchema","generate_query")
            graph.add_edge("generate_query","check_query")
            graph.add_edge("check_query","execute_query")
            graph.add_edge("execute_query","final_answer")
            graph.add_edge("final_answer",END)
            SQLAgent._graph=graph.compile()


        return SQLAgent._graph
    async def answer(self,q):
        agentSQL=await self.Compile()
        event= await agentSQL.ainvoke(
            {
                "messages": [HumanMessage(
                    content=q
                )],
                "sql_query": "",

            },

        )

        return event["messages"][-1].content

# async def main():
#     x=SQLAgent()
#     await x.answer('give me the best 3 post in the last 7 day')
# asyncio.run(main())

