from sqlalchemy.orm import Session
from sqlalchemy import select
import logging

logger=logging.getLogger(__name__)

from app.schemas.health import HealthResponse,ServiceStatus

def health_check(
        db:Session
)->HealthResponse:
    result=dict()
    try:
        db.execute(select(1))
        result["PostgreSQL"]=ServiceStatus(status="connected")
    except Exception:
        logger.exception("PostgreSQL health check failed")
        result["PostgreSQL"]=ServiceStatus(status="disconnected")
    connected = 0

    for service in result.values():
        if service.status == "connected":
            connected += 1
    if connected==len(result):
        return HealthResponse(
            status="healthy",
            services=result
        )
    elif connected==0:
        return HealthResponse(
            status="unhealthy",
            services=result
        )
    else:
        return HealthResponse(
            status="degraded",
            services=result
        )