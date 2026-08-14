from pydantic import BaseModel, Field, HttpUrl


class URLCreate(BaseModel):
    url:HttpUrl
    expires_in:int |None = Field(default=None,gt=0,description="Expiration time in seconds. Must be greater than 0.")

class URLResponse(BaseModel):
    short_url:str