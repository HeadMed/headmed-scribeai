from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.models import MedicalRecord, Patient
from app.models.schemas import MedicalRecordCreate, MedicalRecordUpdate, MedicalRecordResponse

async def create_medical_record(session: AsyncSession, record_data: MedicalRecordCreate) -> MedicalRecordResponse:
    patient_result = await session.execute(select(Patient).filter(Patient.id == record_data.patient_id))
    patient = patient_result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    db_record = MedicalRecord(
        patient_id=record_data.patient_id,
        queixa_principal=record_data.queixa_principal,
        historia_doenca_atual=record_data.historia_doenca_atual,
        antecedentes=record_data.antecedentes,
        exame_fisico=record_data.exame_fisico,
        hipotese_diagnostica=record_data.hipotese_diagnostica,
        conduta=record_data.conduta,
        prescricao=record_data.prescricao,
        encaminhamentos=record_data.encaminhamentos,
        original_transcription=record_data.original_transcription
    )
    
    session.add(db_record)
    await session.flush()
    await session.refresh(db_record)
    
    return MedicalRecordResponse.model_validate(db_record)

async def get_patient_records(session: AsyncSession, patient_id: int) -> List[MedicalRecordResponse]:
    patient_result = await session.execute(select(Patient).filter(Patient.id == patient_id))
    patient = patient_result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    result = await session.execute(
        select(MedicalRecord)
        .filter(MedicalRecord.patient_id == patient_id)
        .order_by(MedicalRecord.created_at.desc())
    )
    records = result.scalars().all()
    
    return [MedicalRecordResponse.model_validate(record) for record in records]

async def get_medical_record(session: AsyncSession, record_id: int) -> MedicalRecordResponse:
    result = await session.execute(select(MedicalRecord).filter(MedicalRecord.id == record_id))
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )
    
    return MedicalRecordResponse.model_validate(record)

async def update_medical_record(session: AsyncSession, record_id: int, record_data: MedicalRecordUpdate) -> MedicalRecordResponse:
    result = await session.execute(select(MedicalRecord).filter(MedicalRecord.id == record_id))
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )
    
    update_data = record_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    
    await session.flush()
    await session.refresh(record)
    
    return MedicalRecordResponse.model_validate(record)

async def delete_medical_record(session: AsyncSession, record_id: int) -> bool:
    result = await session.execute(select(MedicalRecord).filter(MedicalRecord.id == record_id))
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )
    
    await session.delete(record)
    return True