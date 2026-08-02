from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session

from app.services.url_service import create_short_url
from app.utils.urls import build_short_url
from app.schemas.url import URLCreate,URLResponse
from app.db.session import get_db
from app.core.config import settings

router=APIRouter(
    prefix="/urls",
    tags=["URLs"]
)

@router.post("/")
def shorten_url(
    long_url:URLCreate,
    db:Session=Depends(get_db)
)->URLResponse:
    url=create_short_url(long_url,db)
    return URLResponse(short_url=build_short_url(url.short_code))