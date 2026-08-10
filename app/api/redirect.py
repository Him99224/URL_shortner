from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException

from app.services.url_service import find_original_url,is_expired
from app.db.session import get_db

router=APIRouter()

@router.get("/{short_code}")
def redirect(
    short_code:str,
    db:Session=Depends(get_db)
):
    url=find_original_url(
        short_code,db
    )

    if url is None:
        raise HTTPException(
            status_code=404,
            detail="short URL not Found"
        )
    elif is_expired(url):
        raise HTTPException(
            status_code=410,
            detail="short URL Expired"
        )
    url.click_count+=1
    db.commit()
    return RedirectResponse(
        url=url.original_url,
        status_code=307
    )