import json
from os import getenv
from typing import Dict, Any

import httpx
from app.prompts import PROMPT_MEDICAL

from app.config.base import global_config
from app.infrastructure.strategy import AIProvider, StrategyAIInfrastructure
from app.utils.text_transformers import extract_json_from_text

from fastapi import UploadFile

class OpenRouterAIInfrastructure(StrategyAIInfrastructure):
    """
    OpenRouterAIInfrastructure
    """
    def __init__(self):
        
        self._headers = {
            "Authorization": f"Bearer {global_config.OPENROUTER_API_KEY}",
        }
        
        self._base_url = "https://openrouter.ai/api/v1/chat/completions"
        
    async def invoke_model_completion(self, prompt: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=self._base_url,
                headers=self._headers,
                json={
                    "model": global_config.OPENROUTER_MODEL_ID,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    "temperature": global_config.OPENROUTER_TEMPERATURE,
                },
            )
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def invoke_model_transcription(self, file: UploadFile) -> Any:
        return "not implemented"


    def get_provider_name(self):
        return AIProvider.OPENROUTER
    
    async def extract_json_from_text(self, transcription_text):
        
        response = await self.invoke_model_completion(
            PROMPT_MEDICAL.format(transcription_text=transcription_text),
        )
        
        json_response = extract_json_from_text(response)

        return json_response

    async def extract_text_from_audio(self, file):
        return "not implemented"