from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.base import Base
from app.db.database import engine
from app.api.url import router as url_router
from app.api.redirect import router as redirect_router
from app.api.health import router as health_router
from app.events.producer import producer
from app.events.worker import start_polling_worker, stop_event

import app.core.logging
import app.models
@asynccontextmanager
async def lifespan(app:FastAPI):
    Base.metadata.create_all(bind=engine)
    start_polling_worker()
    yield
    stop_event.set()
    producer.flush()
    print("Stopping Kafka polling worker...")

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
app.include_router(health_router)
app.include_router(redirect_router)