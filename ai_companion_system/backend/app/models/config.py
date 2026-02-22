from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # OpenAI配置
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    
    # 豆包API配置
    doubao_api_key: str = ""
    doubao_model: str = "ERNIE-Bot"
    
    # 音频配置
    sample_rate: int = 16000
    audio_chunk: int = 1024
    
    # 情感分析配置
    emotion_model: str = "default"
    
    # 日志配置
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
