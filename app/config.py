from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "Day 7 Authentication API"

    database_url: str = "sqlite:///./users.db"

    jwt_secret_key: str

    jwt_algorithm: str = "HS256"

    access_token_expire_minutes: int = 30

    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()