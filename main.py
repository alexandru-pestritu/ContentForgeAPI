from datetime import datetime, timezone
import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from app.models.user import User
from app.services.settings_service import SettingsService
from scripts.update_stock import scheduled_stock_update
from app.api.api_v1.router import api_router
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from app.dependencies.auth import get_current_user_basic

scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for FastAPI that starts and stops the scheduler.
    """

    SettingsService.initialize_default_settings()
    check_inteval_days = SettingsService.get_setting_value("stock_check_log_interval")
    
    scheduler.add_job(
        scheduled_stock_update,
        "interval",
        days=check_inteval_days,
        next_run_time=datetime.now(timezone.utc),
    )
    scheduler.start()

    yield

    scheduler.shutdown()

app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)

origins = os.getenv(
    "CORS_ORIGINS", "http://localhost:4200,http://localhost:8000"
).split(",")

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

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui(current_user: User = Depends(get_current_user_basic)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API Docs")

@app.get("/redoc", include_in_schema=False)
async def custom_redoc_ui(current_user: User = Depends(get_current_user_basic)):
    return get_redoc_html(openapi_url="/openapi.json", title="API Docs")

@app.get("/openapi.json", include_in_schema=False)
async def openapi(current_user: User = Depends(get_current_user_basic)):
    return JSONResponse(app.openapi())
