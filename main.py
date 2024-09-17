from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from scripts.update_stock import scheduled_stock_update
from app.api.api_v1.router import api_router
from contextlib import asynccontextmanager

scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for FastAPI that starts and stops the scheduler.
    """
    scheduler.add_job(scheduled_stock_update, "interval", days=14, next_run_time=datetime.now(timezone.utc))
    scheduler.start()
   
    yield 

    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

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

@app.get("/")
def read_root():
    return {"message": "Welcome to the ContentForge API!"}
