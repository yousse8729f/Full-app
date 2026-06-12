import datetime
import traceback
import typing
from typing import Optional

import sqlalchemy
from uuid import UUID
from strawberry import type,field,mutation
from tempfile import NamedTemporaryFile
from pathlib import Path

from AI.AgentAI.OrchestratorAgent import OrchestratorAgent
from AI.AgentAI.DocumentService import DocumentService

from fastapi import APIRouter, Depends, UploadFile,File,HTTPException,status
from fastapi import WebSocket,WebSocketException,WebSocketDisconnect

from FastApi.DataBaseConfig.models import database,message_table,conversation_table,user_table


from FastApi.Services.webSocketService import webSocketManager

AI_controller = APIRouter(prefix="/conversation")
upload_dir = Path("C:/Users/Youssef/Files")
date=datetime.datetime.now()
def getmanager(service:WebSocket):
    return service.app.state.manager

@AI_controller.post("/upload/{user_id}/{conv_id}")
async def Upload(user_id:int,conv_id:int,files:list[UploadFile]=File(...)):

    docservice=DocumentService(user_id,conv_id)
    filetemp=[]
    for file in files:
        suffix=Path(file.filename).suffix
        if suffix!=".pdf":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='not supported')
        try:
            temp= NamedTemporaryFile(prefix=file.filename,suffix=suffix,delete=False, dir=str(upload_dir))
            temp.write(await file.read())
            temp.flush()
            temp.close()
            filetemp.append(Path(temp.name).relative_to(upload_dir))
            print(filetemp)
        except Exception:
            traceback.print_exc()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='ERROR')
    await docservice.rag_tool(filetemp)
    return {"status": "ok", "message": f"Uploaded {len(files)} files"}

@AI_controller.websocket("/ws/journal")
async def AI_endpoint(
                      websocket:WebSocket,
                      manager:webSocketManager=Depends(getmanager)):
    await manager.connect(websocket)
    service=OrchestratorAgent(0,0,date)
    try:

            async for chunk in  service.answer("give me the best 3 post in the last 7 day "):
                await manager.send_message(websocket,chunk)

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except WebSocketException:
        await manager.disconnect(websocket)
    except Exception:
        traceback.print_exc()
        await manager.disconnect(websocket)




@AI_controller.websocket("/ws/{user_id}/{conv_id}")
async def AI_endpoint(user_id:int,conv_id:int,
                      websocket:WebSocket,

                      manager:webSocketManager=Depends(getmanager)):

    await manager.connect(websocket)
    service=OrchestratorAgent(user_id,conv_id,date)
    try:
        while True:
            msg=''
            data = await websocket.receive_json()
            user_text = data.get("text")
            queryhuman = message_table.insert().values(message=user_text, role='HUMAN', conversation_id=conv_id)
            await database.execute(queryhuman)
            async for chunk in  service.answer(user_text):
                await manager.send_message(websocket,chunk)
                if chunk.get('type','')=="message":
                    msg+=chunk.get('text')
            queryAI=message_table.insert().values(message=msg,role='AI',conversation_id=conv_id)
            await database.execute(queryAI)

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except WebSocketException:
        await manager.disconnect(websocket)
    except Exception:
        traceback.print_exc()
        await manager.disconnect(websocket)


@type
class Message:
    idMes: int
    message: str
    role: str
@type
class Conv:
    convId:int
    name:str
    userId:UUID
    messages: typing.List[Message]
@type
class Query:
     @field(name="allConvsByUserId")
     async def allConvsByUserId(self,user_id:str)->typing.List[Conv]:
         user_id = UUID(user_id)
         join = conversation_table.join(
             message_table,
             conversation_table.c.conv_id == message_table.c.conversation_id,
             isouter=True  # THIS IS THE FIX
         )

         query = sqlalchemy.select(
             conversation_table.c.conv_id,
             conversation_table.c.name,
             conversation_table.c.user_id,
             message_table.c.id_mes,
             message_table.c.message,
             message_table.c.role
         ).select_from(join).where(
             conversation_table.c.user_id == user_id
         )
         rows=await database.fetch_all(query)
         convs={}
         for row in rows:
             conv_id= row["conv_id"]
             if conv_id not in convs:
                 convs[conv_id] = {
                     "convId": conv_id,
                     "name": row["name"],
                     "userId": str(row["user_id"]),
                     "messages": []
                 }
             if row["id_mes"]:
                 convs[conv_id]["messages"].append(
                     Message(
                         idMes=row["id_mes"],
                         message=row["message"],
                         role=row["role"]
                     )
                 )
         return [
                 Conv(
                     convId=c["convId"],
                     name=c["name"],
                     userId=c["userId"],
                     messages=c["messages"]
                 )
                 for c in convs.values()
             ]
@type
class Mutation:
    @mutation
    async def createconv(self,user_id:str,name:str="nouveau conversation")->Conv:
        user_id = UUID(user_id)
        query = conversation_table.insert().values(created_at=date.strftime("%Y-%m-%d"),name=name,user_id=user_id)
        conv_id=        await database.execute(query)
        return Conv(
            convId=conv_id,
            name=name,
            userId=user_id,
            messages=[]
        )

    @mutation
    async def deleteconv(self, conv_id: int) -> bool:
        query = conversation_table.delete().where(
            conversation_table.c.conv_id == conv_id
        )
        await database.execute(query)
        return True






