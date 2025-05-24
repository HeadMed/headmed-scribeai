from app.infrastructure.strategy import AIProvider

from app.config.base import global_config

from app.infrastructure.groq_strategy import GroqAIInfratrastructure
from app.infrastructure.openrouter_strategy import OpenRouterAIInfrastructure

class AIWorkflow():

    def __init__(self):
        self.provider = global_config.PROVIDER_DEFAULT
    
    async def init_aiflow_transcription(self, file):
        if self.provider == AIProvider.GROQ:
            groq_infra = GroqAIInfratrastructure()

            transcription_text = await groq_infra.extract_text_from_audio(file)
            json_text = await groq_infra.extract_json_from_text(transcription_text)
            
            return json_text, transcription_text
            
        elif self.provider == AIProvider.OPENROUTER:

            groq_infra = GroqAIInfratrastructure()
            openrouter_infra = OpenRouterAIInfrastructure()

            transcription_text = await groq_infra.extract_text_from_audio(file)
            json_text = await openrouter_infra.extract_json_from_text(transcription_text)

            return json_text, transcription_text

    async def init_aiflow_completion(self, file):
        if self.provider == AIProvider.GROQ:
            groq_infra = GroqAIInfratrastructure()

            transcription_text = await groq_infra.extract_text_from_audio(file)

            json_text = await groq_infra.extract_json_from_text(transcription_text)
            
            return transcription_text, json_text
            
        elif self.provider == AIProvider.OPENROUTER:
            openrouter_infra = OpenRouterAIInfrastructure()
            groq_infra = GroqAIInfratrastructure()
            
            # Primeiro obtém o texto transcrito
            transcription_text = await groq_infra.extract_text_from_audio(file)
            # Depois obtém o JSON estruturado
            json_text = await openrouter_infra.extract_json_from_text(transcription_text)

            return transcription_text, json_text
