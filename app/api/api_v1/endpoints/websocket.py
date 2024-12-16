from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services.importer.websocket_manager import websocket_manager

router = APIRouter()

@router.websocket("/import")
async def websocket_imports_endpoint(websocket: WebSocket, task_id: str = Query(...)):
    await websocket_manager.connect(websocket, task_id)
    try:
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, task_id)
