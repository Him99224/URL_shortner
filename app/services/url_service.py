from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.url import URL
from app.schemas.url import URLCreate
from app.utils.base62 import encode_base62

import logging

logger=logging.getLogger(__name__)

def create_short_url(
        url_data:URLCreate,
        db:Session
)->URL:

    expires_at=None
    if url_data.expires_in is not None:
        expires_at=datetime.now(timezone.utc)+timedelta(seconds=url_data.expires_in)
    url=URL(
        original_url=str(url_data.url),
        expires_at=expires_at
        )
    try:
        db.add(url)
        db.flush()

        url.short_code=encode_base62(url.id)

        db.commit()
        db.refresh(url)

        logger.info(
        "Created short URL '%s' for '%s'",
        url.short_code,
        url.original_url
        )

        return url
    
    except Exception:
        db.rollback()
        logger.exception("Failed to create short URL")
        raise

def find_original_url(
        short_code:str,
        db:Session
)->URL|None:
    stmt=select(URL).where(
        URL.short_code==short_code
    )
    result=db.execute(stmt)
    url=result.scalar_one_or_none()
    return url

def delete_url(
        short_code:str,
        db: Session
)->URL|None:
    url=find_original_url(short_code,db)
    if url is None:
        return None
    else:
        db.delete(url)
        db.commit()
        logger.info(
        "Deleted short URL '%s'",
        url.short_code
        )
        return url


def is_expired(
        expires_at:datetime|None
)->bool:
    current_time=datetime.now(timezone.utc)
    if expires_at is None:
        return False
    else:
        return current_time>=expires_at

