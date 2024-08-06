from fastapi import FastAPI
from app.api.api_v1.router import api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ContentForge API",
    version="1.0.0",
)

origins = [
    "http://localhost:4200",  # Angular development server
    "http://localhost:8000",  # FastAPI development server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
