from fastapi import APIRouter
from app.api.api_v1.endpoints import stores, login

api_router = APIRouter()

api_router.include_router(stores.router, prefix="/stores", tags=["stores"])
api_router.include_router(login.router, prefix="/login", tags=["login"])
