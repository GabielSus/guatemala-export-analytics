from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    app_name: str = "Guatemala Export Analytics"
    app_version: str = "0.4.0"
    database_url: str = (
        "postgresql+psycopg://export_user:export_dev_password@db:5432/export_analytics"
    )
    raw_csv_path: str = str(
        PROJECT_ROOT / "data" / "raw" / "exportaciones_banguat.csv"
    )
    frontend_origin: str = "http://127.0.0.1:5173"

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
