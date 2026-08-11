from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./civic_eye.db"
    media_root: Path = Path("media")
    cors_origins: str = "*"
    max_image_mb: int = 10
    max_clip_mb: int = 40
    waste_match_radius_meters: float = 20
    pothole_match_radius_meters: float = 12
    waterlog_match_radius_meters: float = 25
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

