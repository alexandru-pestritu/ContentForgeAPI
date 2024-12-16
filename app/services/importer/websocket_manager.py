from typing import Dict, List
from fastapi import WebSocket

class WebsocketManager:
    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, task_id: str):
        await websocket.accept()
        if task_id not in self.connections:
            self.connections[task_id] = []
        self.connections[task_id].append(websocket)

    def disconnect(self, websocket: WebSocket, task_id: str):
        if task_id in self.connections:
            self.connections[task_id].remove(websocket)
            if not self.connections[task_id]:
                del self.connections[task_id]

    async def broadcast_task_update(self, task_id: str, message: dict):
        if task_id in self.connections:
            for ws in self.connections[task_id]:
                await ws.send_json(message)

websocket_manager = WebsocketManager()
