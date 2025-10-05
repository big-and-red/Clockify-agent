from typing import Optional
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    clockify_api_key: str
    clockify_workspace_id: str
    clockify_user_id: str
    max_period_days: int = 31
    timezone: str = "UTC"
    timezone_offset: int = 0  # Смещение в часах от UTC (например, 3 для GMT+3)
    cache_ttl_minutes: int = 5
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False
    )

settings = Settings()
