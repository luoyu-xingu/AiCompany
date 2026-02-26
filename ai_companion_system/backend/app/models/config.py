from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    sample_rate: int = 16000
    audio_chunk: int = 1024
    
    emotion_model: str = "default"
    
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
