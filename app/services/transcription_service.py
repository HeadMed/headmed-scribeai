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
    
    aiworkflow = AIWorkflow()
    response = await aiworkflow.init_aiflow_completion(file)
    
    if not response:
        return TranscriptionResponse(
            original_text="",
            structured={},
        )

    response_text, response_json = response
    print("\n\n\n response json: ", response_json)
    print("\n\n\n response text: ",response_text)
    record_data = MedicalRecordCreate(
        patient_id=patient_id,
        queixa_principal=response_json.get("queixa_principal"),
        historia_doenca_atual=response_json.get("historia_doenca_atual"),
        antecedentes=response_json.get("antecedentes"),
        exame_fisico=response_json.get("exame_fisico"),
        hipotese_diagnostica=response_json.get("hipotese_diagnostica"),
        conduta=response_json.get("conduta"),
        prescricao=response_json.get("prescricao"),
        encaminhamentos=response_json.get("encaminhamentos"),
        original_transcription=response_text
    )
    print("\n\n\nrecord data:", record_data)
    medical_record = await create_medical_record(session, record_data)
    
    return TranscriptionResponse(
        original_text=response_text,
        structured=response_json,
        medical_record_id=medical_record.id
    )