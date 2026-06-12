import asyncio
import os
import sys
from pathlib import Path
if sys.platform=="win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from dotenv import load_dotenv
import databases
import sqlalchemy
from sqlalchemy import Column,Integer,Text,Table,Enum,ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.dialects.postgresql import UUID
import urllib.parse
envPath=Path(__file__).resolve().parent.parent
envPath = envPath / ".env"
load_dotenv(dotenv_path=envPath)
db_user = os.getenv('POSTGRES_USER')
db_pass = os.getenv('POSTGRES_PASSWORD')
db_port = os.getenv('POSTGRES_PORT')
db_host = os.getenv('POSTGRES_HOST')
db_name = os.getenv('POSTGRES_DB')


DATABASE_URL=f"postgresql+psycopg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

metadata = sqlalchemy.MetaData()
engine = create_async_engine(DATABASE_URL)

user_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True)
)

message_table = Table(
    "message_table",
    metadata,
    Column("id_mes",Integer,primary_key=True),
    Column("message",Text),
    Column("role",Enum("AI","HUMAN",name="role_enum")),
        Column("conversation_id", Integer, ForeignKey("conversation.conv_id"),nullable=False)
)

conversation_table =Table(
    "conversation",
    metadata,
    Column("conv_id",Integer,primary_key=True),
        Column("created_at",Text),
        Column("name",Text),
        Column("user_id",Integer,ForeignKey("users.id"),nullable=False)



)
database= databases.Database(
        DATABASE_URL
    )
async def init_db():
    await database.connect()
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    return database