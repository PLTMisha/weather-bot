import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Telegram Bot
    telegram_bot_token: str
    webhook_url: Optional[str] = None
    
    # Database
    database_url: str
    
    # Environment
    environment: str = "development"
    log_level: str = "INFO"
    
    # Monitoring
    better_stack_token: Optional[str] = None
    
    # Weather API
    weather_api_key: Optional[str] = None
    
    # App settings
    port: int = 8000
    host: str = "0.0.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# API URLs
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
WEATHER_API_URL = "https://api.weatherapi.com/v1"

# Cache settings
CITY_CACHE_TTL = 86400  # 24 hours
WEATHER_CACHE_TTL = 1800  # 30 minutes

# Scheduler settings
SCHEDULER_TIMEZONE = "UTC"
KEEP_ALIVE_INTERVAL = 600  # 10 minutes

# Supported languages
SUPPORTED_LANGUAGES = ["en", "ru", "uk"]
DEFAULT_LANGUAGE = "en"

# Default settings
DEFAULT_NOTIFICATION_TIME = "09:00"
DEFAULT_TIMEZONE = "UTC"
