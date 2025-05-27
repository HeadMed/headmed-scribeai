import json
import asyncio
import logging
from io import BytesIO
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db import async_session_maker
from app.database.models import TaskStatus as DBTaskStatus
from app.infrastructure.rabbitmq import rabbitmq_manager
from app.infrastructure.ai_workflow import AIWorkflow
from app.services.task_service import update_task_status
from app.services.record_service import create_medical_record
from app.models.schemas import MedicalRecordCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranscriptionWorker:
    def __init__(self):
        self.ai_workflow = AIWorkflow()
    
    async def process_transcription_task(self, task_data: dict):
        """Processa uma tarefa de transcrição"""
        task_id = task_data.get("task_id")
        file_name = task_data.get("file_name")
        file_content_hex = task_data.get("file_content")
        patient_id = task_data.get("patient_id")
        
        logger.info(f"Iniciando processamento da tarefa {task_id}")
        
        # Atualiza status para processando
        async with async_session_maker() as session:
            try:
                await update_task_status(session, task_id, DBTaskStatus.PROCESSING)
                await session.commit()
            except Exception as e:
                logger.error(f"Erro ao atualizar status para PROCESSING: {e}")
                await session.rollback()
                return
        
        try:
            # Converte hex string de volta para bytes
            file_content = bytes.fromhex(file_content_hex)
            
            # Cria objeto UploadFile simulado
            file_obj = BytesIO(file_content)
            upload_file = UploadFile(
                filename=file_name,
                file=file_obj
            )
            
            # Processa a transcrição
            logger.info(f"Processando transcrição para {file_name}")
            response = await self.ai_workflow.init_aiflow_completion(upload_file)
            
            if not response:
                raise Exception("Falha na transcrição - resposta vazia")
            
            response_text, response_json = response
            
            medical_record_id = None
            
            # Se tem patient_id, cria o prontuário médico
            if patient_id:
                async with async_session_maker() as session:
                    try:
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
                        
                        medical_record = await create_medical_record(session, record_data)
                        medical_record_id = medical_record.id
                        await session.commit()
                        logger.info(f"Prontuário médico criado: ID {medical_record_id}")
                    except Exception as e:
                        logger.error(f"Erro ao criar prontuário: {e}")
                        await session.rollback()
            
            # Prepara resultado
            result_data = {
                "original_text": response_text,
                "structured": response_json,
                "medical_record_id": medical_record_id
            }
            
            # Atualiza status para completado
            async with async_session_maker() as session:
                try:
                    await update_task_status(
                        session, 
                        task_id, 
                        DBTaskStatus.COMPLETED,
                        result_data=result_data,
                        medical_record_id=medical_record_id
                    )
                    await session.commit()
                    logger.info(f"Tarefa {task_id} processada com sucesso")
                except Exception as e:
                    logger.error(f"Erro ao atualizar status para COMPLETED: {e}")
                    await session.rollback()
                    
        except Exception as e:
            logger.error(f"Erro ao processar tarefa {task_id}: {str(e)}")
            
            # Atualiza status para falha
            async with async_session_maker() as session:
                try:
                    await update_task_status(
                        session,
                        task_id,
                        DBTaskStatus.FAILED,
                        error_message=str(e)
                    )
                    await session.commit()
                except Exception as commit_error:
                    logger.error(f"Erro ao atualizar status para FAILED: {commit_error}")
                    await session.rollback()
    
    def callback(self, ch, method, properties, body):
        """Callback para processar mensagens do RabbitMQ"""
        try:
            task_data = json.loads(body.decode())
            
            # Executa o processamento assíncrono
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.process_transcription_task(task_data))
            loop.close()
            
            # Confirma o processamento da mensagem
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Erro no callback: {str(e)}")
            # Rejeita a mensagem e não recoloca na fila
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    """Função principal do worker"""
    logger.info("Iniciando Transcription Worker...")
    
    worker = TranscriptionWorker()
    
    try:
        # Conecta ao RabbitMQ e inicia consumo
        rabbitmq_manager.consume_transcription_tasks(worker.callback)
    except Exception as e:
        logger.error(f"Erro no worker: {str(e)}")

if __name__ == "__main__":
    main()