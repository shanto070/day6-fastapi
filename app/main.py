import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app import models
from app.config import settings
from app.database import Base, engine
from app.routers import users

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.include_router(users.router)


@app.middleware("http")
async def process_time_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    return response


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.get("/")
def home():
    return {"message": "Welcome to FastAPI User API"}