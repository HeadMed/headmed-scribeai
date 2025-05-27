import pika
import json
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RabbitMQManager:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://admin:admin123@localhost:5672/")
        
    def connect(self):
        """Estabelece conexão com RabbitMQ"""
        try:
            parameters = pika.URLParameters(self.rabbitmq_url)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declara a fila de transcrições
            self.channel.queue_declare(queue='transcription_queue', durable=True)
            
            logger.info("Conectado ao RabbitMQ com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar ao RabbitMQ: {e}")
            return False
    
    def disconnect(self):
        """Fecha conexão com RabbitMQ"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Desconectado do RabbitMQ")
    
    def publish_transcription_task(self, task_data: Dict[str, Any]) -> bool:
        """Publica uma tarefa de transcrição na fila"""
        try:
            if not self.connection or self.connection.is_closed:
                self.connect()
            
            message = json.dumps(task_data)
            self.channel.basic_publish(
                exchange='',
                routing_key='transcription_queue',
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Torna a mensagem persistente
                )
            )
            logger.info(f"Tarefa de transcrição enviada: {task_data.get('task_id')}")
            return True
        except Exception as e:
            logger.error(f"Erro ao publicar tarefa: {e}")
            return False
    
    def consume_transcription_tasks(self, callback):
        """Consome tarefas da fila de transcrição"""
        try:
            if not self.connection or self.connection.is_closed:
                self.connect()
                
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue='transcription_queue',
                on_message_callback=callback
            )
            
            logger.info("Aguardando mensagens. Para sair pressione CTRL+C")
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Parando consumer...")
            self.channel.stop_consuming()
            self.disconnect()
        except Exception as e:
            logger.error(f"Erro no consumer: {e}")

# Instância global
rabbitmq_manager = RabbitMQManager()