from pydantic import BaseModel, ConfigDict
from typing import Dict, Optional, List
from datetime import date, datetime

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class PatientCreate(BaseModel):
    nome: str
    cpf: str
    data_nascimento: date

class PatientUpdate(BaseModel):
    nome: Optional[str] = None
    cpf: Optional[str] = None
    data_nascimento: Optional[date] = None

class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    nome: str
    cpf: str
    data_nascimento: date
    created_at: datetime

class PatientWithRecords(PatientResponse):
    prontuarios: List["MedicalRecordResponse"] = []

class MedicalRecordCreate(BaseModel):
    patient_id: int
    queixa_principal: Optional[str] = None
    historia_doenca_atual: Optional[str] = None
    antecedentes: Optional[str] = None
    exame_fisico: Optional[str] = None
    hipotese_diagnostica: Optional[str] = None
    conduta: Optional[str] = None
    prescricao: Optional[str] = None
    encaminhamentos: Optional[str] = None
    original_transcription: Optional[str] = None

class MedicalRecordUpdate(BaseModel):
    queixa_principal: Optional[str] = None
    historia_doenca_atual: Optional[str] = None
    antecedentes: Optional[str] = None
    exame_fisico: Optional[str] = None
    hipotese_diagnostica: Optional[str] = None
    conduta: Optional[str] = None
    prescricao: Optional[str] = None
    encaminhamentos: Optional[str] = None

class MedicalRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    patient_id: int
    queixa_principal: Optional[str] = None
    historia_doenca_atual: Optional[str] = None
    antecedentes: Optional[str] = None
    exame_fisico: Optional[str] = None
    hipotese_diagnostica: Optional[str] = None
    conduta: Optional[str] = None
    prescricao: Optional[str] = None
    encaminhamentos: Optional[str] = None
    original_transcription: Optional[str] = None
    created_at: datetime

class TranscriptionResponse(BaseModel):
    original_text: str
    structured: Dict[str, str]
    medical_record_id: Optional[int] = None

class TranscriptionWithPatient(BaseModel):
    patient_id: int
    original_text: str
    structured: Dict[str, str]