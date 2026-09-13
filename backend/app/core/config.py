from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = PROJECT_ROOT / "backend"
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    app_name: str = "Guatemala Export Analytics"
    app_version: str = "0.5.0"
    database_url: str = (
        "postgresql+psycopg://export_user:export_dev_password"
        "@127.0.0.1:55432/export_analytics"
    )
    raw_csv_path: str = str(
        PROJECT_ROOT / "data" / "raw" / "exportaciones_banguat.csv"
    )
    sac_pdf_path: str = str(
        PROJECT_ROOT / "data" / "raw" / "sac.pdf"
    )
    frontend_origin: str = "http://127.0.0.1:5173"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
