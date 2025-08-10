from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.enum.env import Env


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        validate_default=False, env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    environment: Env = Field(default=Env.PRODUCTION, validation_alias="ENVIRONMENT")
    sqlalchemy_database_uri: str = Field(default="", validation_alias="SQLALCHEMY_DATABASE_URI")
    x_api_key: str = Field(default="0077012a-8ae6-4fd8-b701-2a8ae64fd882", validation_alias="X_API_KEY")
    jwt_public_key: str = Field(default="", validation_alias="JWT_PUBLIC_KEY")
    jwt_private_key: str = Field(default="", validation_alias="JWT_PRIVATE_KEY")
    jwt_algorithm: str = Field(default="RS256", validation_alias="JWT_ALGORITHM")
    jwt_access_token_exp_h: int = Field(default=8, validation_alias="JWT_ACCESS_EXPIRATION_HOURS")
    jwt_refresh_token_exp_h: int = Field(default=24, validation_alias="JWT_REFRESH_EXPIRATION_HOURS")
    jwt_confirm_token_exp_h: int = Field(default=24, validation_alias="JWT_CONFIRM_EXPIRATION_HOURS")
    smtp_server: str = Field(default="", validation_alias="SMTP_SERVER")
    smtp_port: int = Field(default=0, validation_alias="SMTP_PORT")
    app_password: str = Field(default="", validation_alias="APP_PASSWORD")
    from_email: str = Field(default="", validation_alias="FROM_EMAIL")
    app_url: str = Field(default="", validation_alias="APP_URL")

    app_name: str = Field(default="App", validation_alias="APP_NAME")
    service_name: str = Field(default="api", validation_alias="SERVICE_NAME")
    loki_url: str = Field(default="", validation_alias="LOKI_URL")
    loki_enabled: bool = Field(default=False, validation_alias="LOKI_ENABLED")
    log_request: bool = Field(default=False, validation_alias="LOG_REQUEST")

    rabbitmq_url: str = Field(default="amqp://guest:guest@localhost/", validation_alias="RABBITMQ_URL")

    # CORS Settings
    cors_allow_origins: List[str] = Field(default=["*"], validation_alias="CORS_ALLOW_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, validation_alias="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default=["*"], validation_alias="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(default=["*"], validation_alias="CORS_ALLOW_HEADERS")
    cors_expose_headers: List[str] = Field(
        default=["X-Total-Count", "X-Per-Page", "X-Current-Page", "X-Total-Pages", "X-User-Role"],
        validation_alias="CORS_EXPOSE_HEADERS"
    )


app_config = Settings()  # type: ignore
