from fastapi import APIRouter,Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.schemas.health import HealthResponse
from app.services.health_service import health_check
from app.db.session import get_db

router=APIRouter(
    tags=["Health"]
)


@router.get("/health")
def health(
    db:Session=Depends(get_db)
):
    response=health_check(db)
    status_code = 200

    if response.status == "unhealthy":
        status_code = 503

    return JSONResponse(
        status_code=status_code,
        content=response.model_dump()
    )