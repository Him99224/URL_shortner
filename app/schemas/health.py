from pydantic import BaseModel

class ServiceStatus(BaseModel):
    status:str

class HealthResponse(BaseModel):
    status:str
    services: dict[str,ServiceStatus]
