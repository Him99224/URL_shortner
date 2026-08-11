from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL:str
    BASE_URL:str

    # Kafka settings
    KAFKA_BOOTSTRAP_SERVERS:str
    KAFKA_CLICK_TOPIC:str

    model_config=SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings=Settings()