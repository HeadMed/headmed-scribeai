from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database.models import Patient
from app.models.schemas import PatientCreate, PatientUpdate, PatientResponse, PatientWithRecords

async def create_patient(session: AsyncSession, patient_data: PatientCreate) -> PatientResponse:
    result = await session.execute(select(Patient).filter(Patient.cpf == patient_data.cpf))
    existing_patient = result.scalar_one_or_none()
    
    if existing_patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient with this CPF already exists"
        )
    
    db_patient = Patient(
        nome=patient_data.nome,
        cpf=patient_data.cpf,
        data_nascimento=patient_data.data_nascimento
    )
    
    session.add(db_patient)
    await session.flush()
    await session.refresh(db_patient)
    
    return PatientResponse.model_validate(db_patient)

async def get_patients(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[PatientResponse]:
    result = await session.execute(
        select(Patient)
        .offset(skip)
        .limit(limit)
        .order_by(Patient.nome)
    )
    patients = result.scalars().all()
    
    return [PatientResponse.model_validate(patient) for patient in patients]

async def get_patient_by_id(session: AsyncSession, patient_id: int) -> PatientWithRecords:
    result = await session.execute(
        select(Patient)
        .options(selectinload(Patient.prontuarios))
        .filter(Patient.id == patient_id)
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    return PatientWithRecords.model_validate(patient)

async def get_patient_by_cpf(session: AsyncSession, cpf: str) -> PatientWithRecords:
    result = await session.execute(
        select(Patient)
        .options(selectinload(Patient.prontuarios))
        .filter(Patient.cpf == cpf)
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    return PatientWithRecords.model_validate(patient)

async def update_patient(session: AsyncSession, patient_id: int, patient_data: PatientUpdate) -> PatientResponse:
    result = await session.execute(select(Patient).filter(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    if patient_data.cpf and patient_data.cpf != patient.cpf:
        cpf_result = await session.execute(select(Patient).filter(Patient.cpf == patient_data.cpf))
        existing_patient = cpf_result.scalar_one_or_none()
        if existing_patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Patient with this CPF already exists"
            )
    
    update_data = patient_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    await session.flush()
    await session.refresh(patient)
    
    return PatientResponse.model_validate(patient)

async def delete_patient(session: AsyncSession, patient_id: int) -> bool:
    result = await session.execute(select(Patient).filter(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    await session.delete(patient)
    return True