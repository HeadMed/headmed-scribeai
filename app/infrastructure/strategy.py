from abc import ABC, abstractmethod
from typing import Dict, Any
from enum import Enum

from fastapi import UploadFile

class AIProvider(Enum):
    GROQ = 'groq'
    OPENROUTER = 'openrouter'

class StrategyAIInfrastructure(ABC):
    """
    (descrição da classe)
    
    """
    @abstractmethod
    async def invoke_model_completion(self, prompt: str,) -> Any:
        """
        """
        pass

    @abstractmethod
    async def invoke_model_transcription(self, file: UploadFile) -> Any:
        """
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> AIProvider:
        pass
    
    @abstractmethod
    async def extract_json_from_text(self, transcription_text):
        """
        """
        pass

    @abstractmethod
    async def extract_text_from_audio(self, file) -> str:
        """
        """
        pass

