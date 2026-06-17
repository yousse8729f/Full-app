import asyncio
import sys
import urllib

from langchain_postgres.v2.hybrid_search_config import HybridSearchConfig
from langgraph.checkpoint.serde.base import SerializerProtocol

if sys.platform=="win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from dotenv import load_dotenv
from langchain_postgres import PGEngine, PGVectorStore, Column
from sqlalchemy.ext.asyncio import create_async_engine
import urllib.parse
from langgraph.store.postgres import AsyncPostgresStore
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_postgres.v2.indexes import HNSWIndex
from psycopg_pool import AsyncConnectionPool
from os import getenv
from psycopg.errors import DuplicateTable,DuplicateObject


from pathlib import Path

from AI.AgentAI.Utils.ModelConfig import Model
HybridSearchConfig

current = Path(__file__).parent
env_path = current/".env"
embedding_service = None
pg_engine=None
checkpoint = None
store=None
pool = None
vectore_store=None
engine = None

load_dotenv(dotenv_path=env_path)

def get_embedding():
    global embedding_service
    if embedding_service is None:
        print("Loading embedding model into memory...")
        embedding_service = Model(temp=0.2).model_embedding()
    return embedding_service


user = getenv("POSTGRES_USER")
password = getenv("POSTGRES_PASSWORD")
host = getenv("POSTGRES_HOST")
port = getenv("POSTGRES_PORT")
db = getenv("POSTGRES_DB")
table = getenv("TABLE_NAME")
vector_size = int(getenv("VECTOR_SIZE"))

CONNECTION_STRING = (
    f"postgresql+psycopg://{user}:{password}@{host}"
    f":{port}/{db}"
)
index = HNSWIndex(name="my-hnsw-index")
async def  get_connection_poo()->AsyncConnectionPool:
    cnt = (
        f"postgresql://{user}:{password}@{host}:"
        f"{port}/{db}"
    )
    global pool
    if pool is None:
        pool=   AsyncConnectionPool(conninfo=cnt,min_size=1,max_size=10,open=False,kwargs={"autocommit":True})
        await pool.open()
        print("pool good")
    return  pool
#pg_engine = PGEngine.from_connection_string(url=CONNECTION_STRING)
async def get_connection_engine():

    global engine,pg_engine
    if pg_engine is None and engine is None:
        engine = create_async_engine(
            CONNECTION_STRING,
        )
        pg_engine = PGEngine.from_engine(engine=engine)

        try:

            await pg_engine.ainit_vectorstore_table(
                vector_size=vector_size,
                table_name=table,
                id_column=Column("langchain_id", data_type="UUID"),
                metadata_columns=[
                    Column("source", "TEXT"),
                    Column("user_id", "UUID"),
                    Column("conversation_id","INTEGER"),
                    Column("creationdate","TEXT")
                ],



            )
        except Exception as e:

            print(f"Table {table} already exists, skipping initialization.")
        print("engine good")
    return pg_engine
async def init_vector_store_engine(doc=None):
    global vectore_store
    if vectore_store is None:
        pg_engine = await get_connection_engine()

        vectore_store = await PGVectorStore.create(

            engine=pg_engine,
            table_name=table,
            embedding_service=get_embedding(),

            metadata_columns=[
                "source",
               "user_id",
                "conversation_id",
                "creationdate"
            ],



        )
        print("vecotrstore good")

        if not( await  vectore_store.ais_valid_index("my-hnsw-index")):
            try:
                await vectore_store.aapply_vector_index(index)
                try:

                    await vectore_store.areindex("my-hnsw-index")
                except DuplicateObject:
                    print("Index already exesite")

            except DuplicateTable :
                print("table already exesite")
                pass




    if doc:
        await vectore_store.aadd_documents(documents=doc)
    return vectore_store

async def get_checkpointer()->AsyncPostgresSaver:
    global checkpoint
    if checkpoint is None:
        _pool = await  get_connection_poo()
        checkpoint =  AsyncPostgresSaver(conn=_pool)
        await checkpoint.setup()
    return  checkpoint
async def get_store()->AsyncPostgresStore:
    global store
    if store is None:
        _pool = await get_connection_poo()
        store = AsyncPostgresStore(
            conn=_pool,
            index={
                "dims":vector_size,
                "embed":get_embedding(),
                "fields":["text"]

            },



        )
        await store.setup()
    return store
async def close():
    global pg_engine,pool,store,checkpoint,engine,vectore_store,embedding_service
    if pool is not None:
        await pool.close()
        pool = None

    if engine is not None:
        await engine.dispose()
        engine=None
        await pg_engine.close()
        pg_engine=None
    vectore_store = None
    store = None
    checkpoint = None
    embedding_service=None

# asyncio.run(init_vector_store_engine())



