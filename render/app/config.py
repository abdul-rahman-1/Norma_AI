from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional
import os

class Settings(BaseSettings):
    # Core API Keys
    mongodb_uri: str = ""
    # Database Partitions
    mongodb_phi_db: str = "clinic_default_phi"
    mongodb_profile_db: str = "clinic_default_profile"
    
    gemini_api_key: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    twilio_whatsapp_enabled: bool = True
    port: int = 10000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache()
def get_settings():
    return Settings()
