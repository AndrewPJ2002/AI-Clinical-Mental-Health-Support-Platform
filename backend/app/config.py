from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire: int = 30
    open_api_key: str
    openapi_model: str = ""

    class Config:
        env_file = ".env"


settings = Settings()