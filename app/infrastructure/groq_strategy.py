from app.infrastructure.strategy import StrategyAIInfrastructure, AIProvider
from app.utils import extract_json_from_text
from typing import Dict
import os
from groq import Groq
from app.prompts import PROMPT_MEDICAL
from fastapi import UploadFile
from typing import Dict, Any
from tempfile import NamedTemporaryFile
from app.utils import extract_json_from_text
from app.config.base import global_config

class GroqAIInfratrastructure(StrategyAIInfrastructure):
    """
    GroqAIInfratrastructure

    Args:
        StrategyAIInfrastructure (_type_): _description_
    """
    def __init__(self):
        self.client = Groq()
        self.model_id = global_config.GROQ_MODEL_ID
        self.model_id_transcription = global_config.GROQ_MODEL_TRANSCRIPTION_ID
        self.model_transcription_language = global_config.GROQ_MODEL_TRANSCRIPTION_LANGUAGE
        self.model_temperature_transcription = global_config.GROQ_MODEL_TRANSCRIPTION_TEMPERATURE
        self.model_temperature = global_config.GROQ_TEMPERATURE

    async def invoke_model_completion(self, prompt: str):
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.model_temperature
        )

        return response.choices[0].message.content
        
    async def invoke_model_transcription(self, file: UploadFile) -> Any:

        with NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(await file.read())
            temp_file_path = temp_file.name

        with open(temp_file_path, "rb") as audio_file:
            transcription = self.client.audio.transcriptions.create(
                    file=audio_file,
                    model=self.model_id_transcription,
                    prompt="",
                    response_format="verbose_json",
                    timestamp_granularities=["segment"],
                    language=self.model_transcription_language,
                    temperature=self.model_temperature_transcription
                )

        os.remove(temp_file_path)

        return transcription

    def get_provider_name(self):
        return AIProvider.GROQ

    async def extract_json_from_text(self, transcription_text):
        if not self.client:
            raise ValueError('Groq client is not available')

        response = self.invoke_model_completion(PROMPT_MEDICAL.format(transcription_text=transcription_text))
        json_response = extract_json_from_text(response)

        return json_response

    async def extract_text_from_audio(self, file: UploadFile) -> str:

        res = await self.invoke_model_transcription(file)
        res_text = str(res.text)
        
        return res_text
    