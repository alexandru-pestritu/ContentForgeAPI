from fastapi import Request, HTTPException, status
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud.crud_setup import is_setup_completed

async def setup_middleware(request: Request, call_next):
    if request.url.path.startswith("/setup"):
        return await call_next(request)

    db: Session = SessionLocal()
    completed = is_setup_completed(db)
    db.close()

    if not completed:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Setup not completed. Please finish /setup first."}
        )

    response = await call_next(request)
    return response
