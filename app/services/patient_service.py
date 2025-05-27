from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database.models import Patient, User
from app.models.schemas import PatientCreate, PatientUpdate, PatientResponse, PatientWithRecords
from app.core.security import hash_cpf, format_cpf_for_display

async def create_patient(
    session: AsyncSession, 
    patient_data: PatientCreate, 
    current_user: User 
) -> PatientResponse:
    
    hashed_cpf = hash_cpf(patient_data.cpf, current_user.id)
    
    result = await session.execute(
        select(Patient).filter(
            Patient.cpf == hashed_cpf,
            Patient.doctor_id == current_user.id
        )
    )
    existing_patient = result.scalar_one_or_none()
    
    if existing_patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você já possui um paciente cadastrado com este CPF"
        )
    
    db_patient = Patient(
        nome=patient_data.nome,
        cpf=hashed_cpf,
        cpf_display="***.***.***-**",
        email=patient_data.email,
        data_nascimento=patient_data.data_nascimento,
        doctor_id=current_user.id
    )
    
    session.add(db_patient)
    await session.flush()
    await session.refresh(db_patient)
    
    return PatientResponse.model_validate(db_patient)

async def get_patients(
    session: AsyncSession, 
    current_user: User,
    skip: int = 0, 
    limit: int = 100
) -> List[PatientResponse]:
    
    result = await session.execute(
        select(Patient)
        .filter(Patient.doctor_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(Patient.nome)
    )
    patients = result.scalars().all()
    
    return [PatientResponse.model_validate(patient) for patient in patients]

async def get_patient_by_id(
    session: AsyncSession, 
    patient_id: int, 
    current_user: User
) -> PatientWithRecords:
    
    result = await session.execute(
        select(Patient)
        .options(selectinload(Patient.prontuarios))
        .filter(
            Patient.id == patient_id,
            Patient.doctor_id == current_user.id
        )
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado ou não pertence a você"
        )
    
    return PatientWithRecords.model_validate(patient)

async def get_patient_by_cpf(
    session: AsyncSession, 
    cpf_search: str, 
    current_user: User
) -> Optional[PatientWithRecords]:
    
    hashed_cpf = hash_cpf(cpf_search, current_user.id)
    
    result = await session.execute(
        select(Patient)
        .options(selectinload(Patient.prontuarios))
        .filter(
            Patient.cpf == hashed_cpf,
            Patient.doctor_id == current_user.id
        )
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    return PatientWithRecords.model_validate(patient)

async def update_patient(
    session: AsyncSession, 
    patient_id: int, 
    patient_data: PatientUpdate, 
    current_user: User
) -> PatientResponse:
    
    result = await session.execute(
        select(Patient).filter(
            Patient.id == patient_id,
            Patient.doctor_id == current_user.id
        )
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado ou não pertence a você"
        )
    
    if patient_data.cpf and patient_data.cpf != patient.cpf:
        cpf_result = await session.execute(
            select(Patient).filter(
                Patient.cpf == patient_data.cpf,
                Patient.doctor_id == current_user.id,
                Patient.id != patient_id
            )
        )
        existing_patient = cpf_result.scalar_one_or_none()
        if existing_patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Você já possui outro paciente com este CPF"
            )
    
    update_data = patient_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    await session.flush()
    await session.refresh(patient)
    
    return PatientResponse.model_validate(patient)

async def delete_patient(
    session: AsyncSession, 
    patient_id: int, 
    current_user: User
) -> bool:
    
    result = await session.execute(
        select(Patient).filter(
            Patient.id == patient_id,
            Patient.doctor_id == current_user.id
        )
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado ou não pertence a você"
        )
    
    await session.delete(patient)
    return True

async def verify_patient_ownership(
    session: AsyncSession, 
    patient_id: int, 
    current_user: User
) -> Patient:
    
    result = await session.execute(
        select(Patient).filter(
            Patient.id == patient_id,
            Patient.doctor_id == current_user.id
        )
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: este paciente não pertence a você"
        )
    
    return patient