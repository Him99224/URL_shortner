from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException

from datetime import datetime

from app.core.logging import logging
from app.services.url_service import find_original_url,is_expired
from app.db.session import get_db
from app.events.producer import publish_click_event
from app.cache.redis import cache_url,get_cached_url

logger=logging.getLogger(__name__)

router=APIRouter()

@router.get("/{short_code}")
def redirect(
    short_code:str,
    db:Session=Depends(get_db)
):
    cached_url = get_cached_url(short_code)
    if cached_url:
        logger.info("Cache HIT for short code '%s'", short_code)
        if (cached_url["expires_at"] is not None and is_expired(cached_url["expires_at"])):
            raise HTTPException(
                status_code=410,
                detail="short URL Expired"
            )
        publish_click_event(short_code)
        return RedirectResponse(
            url=cached_url["original_url"],
            status_code=307
        )
    else:
        logger.info("Cache MISS for short code '%s'", short_code)

        url=find_original_url(
            short_code,db
        )

        if url is None:
            raise HTTPException(
                status_code=404,
                detail="short URL not Found"
            )
        elif is_expired(url.expires_at):
            raise HTTPException(
                status_code=410,
                detail="short URL Expired"
            )
        publish_click_event(short_code)
        cache_url(
            short_code,
            url.original_url,
            url.expires_at
        )
        
        return RedirectResponse(
            url=url.original_url,
            status_code=307
        )