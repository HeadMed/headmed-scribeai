from fastapi import UploadFile
from app.services.whisper import transcribe_audio
from app.services.llm import extract_structured_info
from app.models.schemas import TranscriptionResponse

async def handle_transcription_flow(file: UploadFile) -> TranscriptionResponse:
    text = await transcribe_audio(file)
    structured = extract_structured_info(text)
    return TranscriptionResponse(
        original_text=text,
        structured=structured
    )
