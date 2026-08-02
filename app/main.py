from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.base import Base
from app.db.database import engine
from app.api.url import router as url_router

import app.models
@asynccontextmanager
async def lifespan(app:FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app=FastAPI(
    title="URL Shortener API",
    description="A scalable URL shortening service built with FastAPI",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
def root():
    return {"message":"Hello World"}

app.include_router(url_router)