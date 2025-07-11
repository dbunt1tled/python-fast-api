from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(validate_default=False, env_file=".env", env_file_encoding="utf-8", extra="ignore")
    sqlalchemy_database_uri: str = Field(default="", validation_alias="SQLALCHEMY_DATABASE_URI")
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

app_config = Settings()  # type: ignore
