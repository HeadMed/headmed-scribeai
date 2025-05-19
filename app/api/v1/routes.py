import http.client
from fastapi import APIRouter, UploadFile, File
from app.services.transcription_service import handle_transcription_flow
from app.schemas.transcription import TranscriptionResponse
import http

router = APIRouter()

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(file: UploadFile = File(...)):
    return await handle_transcription_flow(file)

@router.get("/health")
async def health_check():
    return {"status": http.HTTPStatus.OK, "msg": "Health Checked!"}