from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.ai_workflow import AIWorkflow
from app.services.record_service import create_medical_record
from app.models.schemas import TranscriptionResponse, MedicalRecordCreate, TranscriptionTaskResponse
from app.services.task_service import create_transcription_task


async def handle_transcription_flow(file: UploadFile) -> TranscriptionResponse:
    """Processamento síncrono de transcrição (mantido para compatibilidade)"""
        
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

async def handle_transcription_flow_async(session: AsyncSession, file: UploadFile) -> TranscriptionTaskResponse:
    """Novo processamento assíncrono de transcrição"""
    
    # Lê o conteúdo do arquivo
    file_content = await file.read()
    
    # Cria tarefa assíncrona
    task_response = await create_transcription_task(
        session=session,
        file_name=file.filename or "audio.mp3",
        file_content=file_content
    )
    
    return task_response

async def handle_transcription_with_patient(
    session: AsyncSession, 
    file: UploadFile, 
    patient_id: int
) -> TranscriptionResponse:
    """Processamento síncrono com paciente (mantido para compatibilidade)"""
    
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

async def handle_transcription_with_patient_async(
    session: AsyncSession, 
    file: UploadFile, 
    patient_id: int
) -> TranscriptionTaskResponse:
    """Novo processamento assíncrono com paciente"""
    
    # Lê o conteúdo do arquivo
    file_content = await file.read()
    
    # Cria tarefa assíncrona com patient_id
    task_response = await create_transcription_task(
        session=session,
        file_name=file.filename or "audio.mp3",
        file_content=file_content,
        patient_id=patient_id
    )
    
    return task_response