import asyncio
import sys

from flashrank import Ranker
from langchain_community.embeddings import HypotheticalDocumentEmbedder

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import logging
from dataclasses import dataclass
from AI.AgentAI.Utils.PostgresConfig import  init_vector_store_engine,close
from pathlib import Path
from dotenv import load_dotenv
from os import getenv
import os
from AI.AgentAI.Utils.ModelConfig import Model

from langchain_community.retrievers import BM25Retriever
from langchain_community.document_compressors import FlashrankRerank
from langchain_classic.retrievers import EnsembleRetriever, ContextualCompressionRetriever

load_dotenv()
os.environ["USER_AGENT"] = "Youssef-RAG-Agent"
logger = logging.getLogger(__name__)
project = getenv("LANGSMITH_PROJECT")
api_key = getenv("LANGSMITH_API_KEY")
path = Path(getenv("BASE_PATH"))
@dataclass
class RagAgent:

    vector_store=None

    def __init__(self,user_id,conv_id):
        self.user_id = user_id
        self.conv_id=conv_id
        self.embedding=Model(temp=0.2).model_embedding()
        self.llm=Model(0.2).model_llama2()

        logger.info(f"user_id = {user_id}, conv_id={conv_id}")
    async def initVectorStore(self):
        if not RagAgent.vector_store:
            RagAgent.vector_store=await init_vector_store_engine()
        return RagAgent.vector_store
    async def builder(self,chunks=None):

        semantic = RagAgent.vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4, "filter": {
            "user_id": {"$eq": self.user_id},
            "conversation_id": {"$eq": self.conv_id}
        }})
        if chunks:
            bm25 = BM25Retriever.from_documents(chunks)
            bm25.k=10
            retriver=EnsembleRetriever(
                retrievers=[bm25,semantic],
                weights=[0.5,0.5]
            )
        else:
            retriver=semantic
        hyde = HypotheticalDocumentEmbedder.from_llm(
            llm=self.llm,
            base_retriever=retriver,
            embeddings=self.embedding
        )
        ranker = Ranker(model_name=self.llm)
        reranker = FlashrankRerank(client=ranker,top_n=5)
        return ContextualCompressionRetriever(
            base_retriever=hyde,
            base_compressor=reranker
        )


    async def answer(self, query: list,chunks=None):
        """this is helper function is gonna help you if you dont know what to answer call it each time when
        there is alot of question or there is personal data"""

        RagAgent.vector_store = await self.initVectorStore()
        retriver=await self.builder(chunks)


        text = ""

        for q in query:
                content = await retriver.ainvoke(q)
                text += "\n\n".join(doc.page_content for doc in content if doc.page_content not in text)
        return f"personal_context: {text}"

    @staticmethod
    async def close_all():
        await close()
# async def r():
#     await MultiAgentService.initialise()
#     x=MultiAgentService(1,1)
#     await x.main("expliquer les style architectiraux")
# asyncio.run(r())










