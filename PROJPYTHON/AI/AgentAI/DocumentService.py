import asyncio
import datetime
import sys
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import logging
from dataclasses import dataclass
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from AI.AgentAI.Utils.PostgresConfig import  init_vector_store_engine

from typing import List
from pathlib import Path
from dotenv import load_dotenv
from os import getenv
from langchain_core.documents import Document
from AI.AgentAI.Utils.ModelConfig import Model


load_dotenv()

logger = logging.getLogger(__name__)
project = getenv("LANGSMITH_PROJECT")
api_key = getenv("LANGSMITH_API_KEY")
path = Path(getenv("BASE_PATH"))



@dataclass
class DocumentService:
    vector_store = None
    def __init__(self, user_id, conv_id):
        self.user_id = user_id
        self.conv_id = conv_id
        self.embedding = Model(temp=0.2).model_embedding()
    async def initVectorStore(self):
        if not DocumentService.vector_store:
            DocumentService.vector_store=await init_vector_store_engine()
        return DocumentService.vector_store

    @staticmethod
    def handle_file(listfile: List) -> List[Path]:
        pathlist = []
        for n in listfile:
            filepath = path / n
            pathlist.append(filepath)
        return pathlist

    @staticmethod
    def valid_extension(filename: str):
        lastdot = filename.rfind(".")
        ext = filename[lastdot:]
        match ext:
            case ".pdf":
                return "pdf"
            case ".docx":
                return ".docx"
            case _:
                return "invalid"

    async def load_file(self, files: List[Path]) -> List[Document]:
        docs: List[Document] = []
        async with asyncio.TaskGroup() as tg:
            task_group = {}
            for file in files:
                file_str = str(file)
                ext = self.valid_extension(file_str)
                if ext in {"pdf", "docx"}:
                    loader = PyPDFLoader(file) if ext == "pdf" else Docx2txtLoader(file)
                    task = tg.create_task(loader.aload())
                    task_group[task] = file_str
                else:
                    logger.error(f"Ignored invalid file: {file}")
        for task, file_str in task_group.items():
            loaded_doc = task.result()
            for d in loaded_doc:
                d.metadata["source"] = file_str
                d.metadata["user_id"] = self.user_id
                d.metadata["conversation_id"] = self.conv_id
                d.metadata["creationdate"] = datetime.datetime.now().strftime("%Y-%m-%d-%M")
            docs.extend(loaded_doc)
        return docs

    async def rag_tool(self, file: List):
        DocumentService.vector_store= await self.initVectorStore()



        file_path = self.handle_file(file)
        files_to_load = []
        for path in file_path:
            try:
                retriever = DocumentService.vector_store.as_retriever(
                    search_type="similarity",
                    search_kwargs={
                        "k": 1,
                        "filter": {"source": {"$eq": str(path)}}
                    }
                )
                results = await retriever.ainvoke("checking_for_existence")
            except Exception as e:
                logger.error("not exsiting ", e)
                results = []
            if not results:
                files_to_load.append(path)
            else:
                logger.warning("file exsited")
        if not files_to_load:
            return
        loaded_doc = await self.load_file(files_to_load)
        split = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=512*0.15,separators=["\n\n","\n"," ",""])
        chunks = split.split_documents(documents=loaded_doc)
        if chunks:
            await DocumentService.vector_store.aadd_documents(chunks)
            logger.info("file added to database")
        return chunks