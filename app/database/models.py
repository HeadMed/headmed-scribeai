from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.db import Base
from enum import Enum

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    patients = relationship("Patient", back_populates="doctor", cascade="all, delete-orphan")

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    cpf = Column(String(255), index=True, nullable=False)
    cpf_display = Column(String(15), nullable=True)
    email = Column(String(255), nullable=True)
    data_nascimento = Column(Date, nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    doctor = relationship("User", back_populates="patients")
    prontuarios = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")

class MedicalRecord(Base):
    __tablename__ = "medical_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    queixa_principal = Column(Text)
    historia_doenca_atual = Column(Text)
    antecedentes = Column(Text)
    exame_fisico = Column(Text)
    hipotese_diagnostica = Column(Text)
    conduta = Column(Text)
    prescricao = Column(Text)
    encaminhamentos = Column(Text)
    
    original_transcription = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    patient = relationship("Patient", back_populates="prontuarios")


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), unique=True, index=True, nullable=False)  # UUID da tarefa
    task_type = Column(String(50), nullable=False)  # 'transcription'
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    
    # Dados da tarefa (JSON como texto)
    input_data = Column(Text)  # Dados de entrada (ex: referência do arquivo)
    result_data = Column(Text)  # Resultado da tarefa (JSON)
    error_message = Column(Text)  # Mensagem de erro se falhar
    
    # Relacionamentos opcionais
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    medical_record_id = Column(Integer, ForeignKey("medical_records.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
