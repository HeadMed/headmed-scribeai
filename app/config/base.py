from pydantic_settings import BaseSettings
from os import getenv
from dotenv import load_dotenv

from app.infrastructure.strategy import AIProvider


load_dotenv()


class GlobalConfig(BaseSettings):
    """
    """
        
    OPENROUTER_API_KEY: str = str(getenv("OPENROUTER_API_KEY"))
    OPENROUTER_TEMPERATURE: float = 0.3
    OPENROUTER_MODEL_ID: str = 'openai/gpt-4o'
    
    GROQ_API_KEY: str = str(getenv("GROQ_API_KEY"))
    GROQ_TEMPERATURE: float = 0.3
    GROQ_MODEL_ID: str = 'meta-llama/llama-4-scout-17b-16e-instruct'
    GROQ_MODEL_TRANSCRIPTION_ID: str = 'whisper-large-v3-turbo'
    GROQ_MODEL_TRANSCRIPTION_LANGUAGE: str = 'pt'
    GROQ_MODEL_TRANSCRIPTION_TEMPERATURE: float = 0.0
    
    PROVIDER_DEFAULT: AIProvider = AIProvider.GROQ
    
    class Config:
        case_sensitive = True
    
global_config = GlobalConfig()