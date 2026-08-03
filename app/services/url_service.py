from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.url import URL
from app.schemas.url import URLCreate
from app.utils.base62 import encode_base62


def create_short_url(
        url_data:URLCreate,
        db:Session
)->URL:
    url=URL(
        original_url=str(url_data.url),
        )
    try:
        db.add(url)
        db.flush()
        url.short_code=encode_base62(url.id)
        db.commit()
        db.refresh(url)
        return url
    except Exception:
        db.rollback()
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



#not adding the incrementor for click count here yet for future

# TODO(Kafka):
# Emit a "url_clicked" event instead of updating click_count directly.
# Click aggregation will be handled asynchronously by a Kafka consumer.