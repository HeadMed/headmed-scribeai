import http
from typing import List
from fastapi import APIRouter, UploadFile, File, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_async_session
from app.database.models import User
from app.core.security import get_current_user
from app.services.transcription_service import handle_transcription_flow, handle_transcription_with_patient
from app.services.auth_service import login_user, create_user
from app.services.patient_service import (
    create_patient, get_patients, get_patient_by_id, 
    get_patient_by_cpf, update_patient, delete_patient
)
from app.services.record_service import (
    create_medical_record, get_patient_records, get_medical_record,
    update_medical_record, delete_medical_record
)
from app.models.schemas import (
    TranscriptionResponse, UserLogin, UserCreate, UserResponse, Token,
    PatientCreate, PatientUpdate, PatientResponse, PatientWithRecords,
    MedicalRecordCreate, MedicalRecordUpdate, MedicalRecordResponse
)

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": http.HTTPStatus.OK, "msg": "Health Checked!"}

# Authentication routes
@router.post("/auth/login", response_model=Token)
async def login(
    user_data: UserLogin,
    session: AsyncSession = Depends(get_async_session)
):

    return await login_user(session, user_data)

@router.post("/auth/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_async_session)
):

    return await create_user(session, user_data)

@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):

    return UserResponse.model_validate(current_user)

# Transcription routes (protected)
@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):

    return await handle_transcription_flow(file)

@router.post("/transcribe/patient/{patient_id}", response_model=TranscriptionResponse)
async def transcribe_for_patient(
    patient_id: int,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):

    return await handle_transcription_with_patient(session, file, patient_id)

# Patient routes (protected)
@router.post("/patients", response_model=PatientResponse)
async def create_new_patient(
    patient_data: PatientCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):

    return await create_patient(session, patient_data)

@router.get("/patients", response_model=List[PatientResponse])
async def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):

    return await get_patients(session, skip, limit)

@router.get("/patients/{patient_id}", response_model=PatientWithRecords)
async def get_patient(
    patient_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):

    return await get_patient_by_id(session, patient_id)

@router.get("/patients/cpf/{cpf}", response_model=PatientWithRecords)
async def get_patient_by_document(
    cpf: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):

    return await get_patient_by_cpf(session, cpf)

@router.put("/patients/{patient_id}", response_model=PatientResponse)
async def update_existing_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):

    return await update_patient(session, patient_id, patient_data)

@router.delete("/patients/{patient_id}")
async def delete_existing_patient(
    patient_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):

    await delete_patient(session, patient_id)
    return {"message": "Patient deleted successfully"}

# Medical Records routes (protected)
@router.post("/records", response_model=MedicalRecordResponse)
async def create_new_medical_record(
    record_data: MedicalRecordCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    return await create_medical_record(session, record_data)

@router.get("/patients/{patient_id}/records", response_model=List[MedicalRecordResponse])
async def get_patient_medical_records(
    patient_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):

    return await get_patient_records(session, patient_id)

@router.get("/records/{record_id}", response_model=MedicalRecordResponse)
async def get_single_medical_record(
    record_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):

    return await get_medical_record(session, record_id)

@router.put("/records/{record_id}", response_model=MedicalRecordResponse)
async def update_existing_medical_record(
    record_id: int,
    record_data: MedicalRecordUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):

    return await update_medical_record(session, record_id, record_data)

@router.delete("/records/{record_id}")
async def delete_existing_medical_record(
    record_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):

    await delete_medical_record(session, record_id)
    return {"message": "Medical record deleted successfully"}