from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.base import Base
from app.db.database import engine
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



from app.core.config import settings

print(settings.database_url)