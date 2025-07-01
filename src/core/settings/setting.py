from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(validate_default=False, env_file=".env", env_file_encoding="utf-8", extra="ignore")
    sqlalchemyDatabaseUri: str = Field(
    default="",
    validation_alias="SQLALCHEMY_DATABASE_URI",
    )

app_config = Settings()  # type: ignore