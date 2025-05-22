from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.whisper import transcribe_audio
from app.services.llm import extract_structured_info
from app.services.record_service import create_medical_record
from app.models.schemas import TranscriptionResponse, MedicalRecordCreate

async def handle_transcription_flow(file: UploadFile) -> TranscriptionResponse:
    text = await transcribe_audio(file)
    structured = extract_structured_info(text)
    return TranscriptionResponse(
        original_text=text,
        structured=structured
    )

async def handle_transcription_with_patient(
    session: AsyncSession, 
    file: UploadFile, 
    patient_id: int
) -> TranscriptionResponse:
    text = await transcribe_audio(file)
    structured = extract_structured_info(text)

    record_data = MedicalRecordCreate(
        patient_id=patient_id,
        queixa_principal=structured.get("queixa_principal"),
        historia_doenca_atual=structured.get("historia_doenca_atual"),
        antecedentes=structured.get("antecedentes"),
        exame_fisico=structured.get("exame_fisico"),
        hipotese_diagnostica=structured.get("hipotese_diagnostica"),
        conduta=structured.get("conduta"),
        prescricao=structured.get("prescricao"),
        encaminhamentos=structured.get("encaminhamentos"),
        original_transcription=text
    )
    
    medical_record = await create_medical_record(session, record_data)
    
    return TranscriptionResponse(
        original_text=text,
        structured=structured,
        medical_record_id=medical_record.id
    )