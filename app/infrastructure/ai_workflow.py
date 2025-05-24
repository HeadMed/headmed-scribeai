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

    async def init_aiflow_completion(self, transcription_text):
        if self.provider == AIProvider.GROQ:
            groq_infra = GroqAIInfratrastructure()
            json_text = await groq_infra.extract_json_from_text(transcription_text)

            return json_text
            
        elif self.provider == AIProvider.OPENROUTER:
            openrouter_infra = OpenRouterAIInfrastructure()

            json_text = await openrouter_infra.extract_json_from_text(transcription_text)

            return json_text

