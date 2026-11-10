
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.api.v1.router import api_router


# Create database tables
Base.metadata.create_all(bind=engine)


# Initialize FastAPI
app = FastAPI(
    title="Day 8 FastAPI Architecture",
    description="Clean Architecture FastAPI Project",
    version="1.0.0"
)


# CORS Middleware
origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Register API Router
app.include_router(api_router)


# Process Time Middleware
@app.middleware("http")
async def process_time_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    return response


# Global Exception Handler
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Home Route
@app.get("/")
def home():
    return {
        "message": "Welcome to Day 8 FastAPI Architecture"
    }
