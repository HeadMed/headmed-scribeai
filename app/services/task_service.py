import uuid
import json
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.models import Task, TaskStatus as DBTaskStatus
from app.models.schemas import TaskResponse, TranscriptionTaskResponse, TaskStatus as SchemaTaskStatus
from app.infrastructure.rabbitmq import rabbitmq_manager
import logging

logger = logging.getLogger(__name__)

async def create_transcription_task(
    session: AsyncSession,
    file_name: str,
    file_content: bytes,
    patient_id: Optional[int] = None
) -> TranscriptionTaskResponse:
    """Cria uma tarefa de transcrição assíncrona"""
    
    # Gera um ID único para a tarefa
    task_id = str(uuid.uuid4())
    
    # Cria registro da tarefa no banco
    db_task = Task(
        task_id=task_id,
        task_type="transcription",
        status=DBTaskStatus.PENDING,
        input_data=json.dumps({
            "file_name": file_name,
            "file_size": len(file_content)
        }),
        patient_id=patient_id
    )
    
    session.add(db_task)
    await session.flush()
    
    # Prepara dados para o RabbitMQ
    task_data = {
        "task_id": task_id,
        "file_name": file_name,
        "file_content": file_content.hex(),  # Converte bytes para hex string
        "patient_id": patient_id
    }
    
    # Envia para a fila do RabbitMQ
    success = rabbitmq_manager.publish_transcription_task(task_data)
    
    if not success:
        # Se falhou ao enviar para a fila, marca como erro
        db_task.status = DBTaskStatus.FAILED
        db_task.error_message = "Falha ao enviar tarefa para processamento"
        await session.flush()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor ao processar transcrição"
        )
    
    return TranscriptionTaskResponse(
        task_id=task_id,
        status=SchemaTaskStatus.PENDING,
        message="Tarefa de transcrição criada com sucesso. Use o task_id para consultar o status."
    )

async def get_task_status(session: AsyncSession, task_id: str) -> TaskResponse:
    """Consulta o status de uma tarefa"""
    
    result = await session.execute(select(Task).filter(Task.task_id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada"
        )
    
    return TaskResponse.model_validate(task)

async def update_task_status(
    session: AsyncSession,
    task_id: str,
    new_status: DBTaskStatus,
    result_data: Optional[dict] = None,
    error_message: Optional[str] = None,
    medical_record_id: Optional[int] = None
) -> bool:
    """Atualiza o status de uma tarefa (usado pelo worker)"""
    
    result = await session.execute(select(Task).filter(Task.task_id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        logger.error(f"Tarefa {task_id} não encontrada para atualização")
        return False
    
    task.status = new_status
    
    if result_data:
        task.result_data = json.dumps(result_data)
    
    if error_message:
        task.error_message = error_message
    
    if medical_record_id:
        task.medical_record_id = medical_record_id
    
    if new_status == DBTaskStatus.PROCESSING:
        from sqlalchemy.sql import func
        task.started_at = func.now()
    elif new_status in [DBTaskStatus.COMPLETED, DBTaskStatus.FAILED]:
        from sqlalchemy.sql import func
        task.completed_at = func.now()
    
    await session.flush()
    logger.info(f"Status da tarefa {task_id} atualizada para {new_status}")
    return True