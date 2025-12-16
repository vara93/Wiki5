from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_path: Path = Field(default=Path("data/itdocs.db"))
    secret_key: str = Field(default="changeme-secret")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60 * 12)
    upload_dir: Path = Field(default=Path("data/uploads"))
    static_dir: Path = Field(default=Path("static"))

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.database_path}"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.static_dir.mkdir(parents=True, exist_ok=True)
settings.database_path.parent.mkdir(parents=True, exist_ok=True)
