import asyncio
import sys
if sys.platform=="win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import strawberry
from strawberry.fastapi import GraphQLRouter

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from FastApi.DataBaseConfig.models import init_db,database
from FastApi.Controller.AI_controller import AI_controller, Query, Mutation
from FastApi.Services.webSocketService import webSocketManager

origin = [
    "http://localhost:4200"
]
@asynccontextmanager
async def lifespan(app:FastAPI):
    app.state.manager =webSocketManager()
    await init_db()
    print("db start")
    yield
    await database.disconnect()
schema= strawberry.Schema(query=Query,mutation=Mutation)
graphql_R=GraphQLRouter(schema)
app=FastAPI(lifespan=lifespan)


app.include_router(AI_controller)
app.add_middleware(CORSMiddleware,allow_origins=origin,allow_methods=['*'],allow_headers=['*'])
# if __name__=="__main__":
#     uvicorn.run("FastApi.main:app",port=8081,reload=True)