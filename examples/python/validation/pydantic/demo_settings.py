from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CHEATSHEET_PYDANTIC_", case_sensitive=False,
        env_file=None, extra="ignore",
    )
    app_name: str = "Training"
    database_url: str
    api_key: SecretStr | None = None
