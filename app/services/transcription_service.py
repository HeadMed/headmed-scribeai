from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.ai_workflow import AIWorkflow
from app.services.record_service import create_medical_record
from app.models.schemas import TranscriptionResponse, MedicalRecordCreate


async def handle_transcription_flow(file: UploadFile) -> TranscriptionResponse:
        
    aiworkflow = AIWorkflow()
    response = await aiworkflow.init_aiflow_completion(file)
    
    if not response:
        return TranscriptionResponse(
            original_text="",
            structured={},
        )
    
    response_text, response_json = response

    return TranscriptionResponse(
        original_text=response_text,
        structured=response_json,
    )

async def handle_transcription_with_patient(
    session: AsyncSession, 
    file: UploadFile, 
    patient_id: int
) -> TranscriptionResponse:
    return TranscriptionResponse(
        original_text="",
        structured={},
    )
    """
    aiworkflow = AIWorkflow()
    response_json, response_text = aiworkflow.init_aiflow_completion(file)

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
    """