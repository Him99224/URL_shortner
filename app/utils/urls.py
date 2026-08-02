from app.core.config import settings


def build_short_url(short_code:str)->str:
    return f"{settings.BASE_URL}/{short_code}"