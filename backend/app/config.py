from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire: int = 30
    open_api_key: str = Field(validation_alias="OPEN_API_KEY")
    openapi_model: str = Field(default="", validation_alias="OPENAPI_MODEL")

settings = Settings()
