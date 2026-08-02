from sqlalchemy.orm import Session

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
    db.add(url)
    db.flush()
    url.short_code=encode_base62(url.id)
    db.commit()
    db.refresh(url)