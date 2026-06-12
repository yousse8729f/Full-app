from fastapi.websockets import WebSocket,WebSocketState

class webSocketManager:
    def __init__(self):
        self.connected_client:set[WebSocket]=set()
    async def connect(self,websocket:WebSocket):
        await websocket.accept()
        self.connected_client.add(websocket)

    async def disconnect(self,websocket:WebSocket):
        self.connected_client.discard(websocket)
    async def send_message(self,websocket:WebSocket,msg):
        if websocket.client_state != WebSocketState.CONNECTED:
            return
        try:
            await websocket.send_json(msg)
        except Exception:
            await self.disconnect(websocket)
    async def broadcast(self,message):
       disconected=[]
       for connections in self.connected_client:
           if connections.client_state==WebSocketState.CONNECTED:
               try:
                     await connections.send_json(message)
               except Exception:
                     disconected.append(connections)

           else:
               disconected.append(connections)
       for conn in disconected:
           self.connected_client.discard(conn)
