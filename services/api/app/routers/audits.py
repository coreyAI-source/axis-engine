from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.audit import Audit, AuditTeamMember, AuditLocation, AuditProcess
from ..schemas.audit import (
    AuditCreate, AuditUpdate, AuditOut,
    AuditTeamMemberCreate, AuditTeamMemberOut,
    AuditLocationCreate, AuditLocationOut,
    AuditProcessCreate, AuditProcessOut,
)
from ..services.audit_validator import validate_audit_against_gstc
from ..utils.security import get_current_user

router = APIRouter(prefix="/audits", tags=["audits"])


@router.get("/", response_model=list[AuditOut])
async def list_audits(
    status: str | None = None,
    organisation_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    q = select(Audit)
    if status:
        q = q.where(Audit.status == status)
    if organisation_id:
        q = q.where(Audit.organisation_id == organisation_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/", response_model=AuditOut, status_code=201)
async def create_audit(payload: AuditCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = Audit(**payload.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.get("/{audit_id}", response_model=AuditOut)
async def get_audit(audit_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = await db.get(Audit, audit_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Audit not found")
    return obj


@router.patch("/{audit_id}", response_model=AuditOut)
async def update_audit(audit_id: UUID, payload: AuditUpdate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = await db.get(Audit, audit_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Audit not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.delete("/{audit_id}", status_code=204)
async def cancel_audit(audit_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = await db.get(Audit, audit_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Audit not found")
    obj.status = "Cancelled"
    await db.flush()


@router.post("/{audit_id}/validate-gstc")
async def validate_gstc_requirements(
    audit_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user)
):
    """
    Validate audit against GSTC Section 8.5 requirements.

    Returns validation result with:
    - is_valid: true if audit meets all GSTC requirements
    - errors: list of validation errors (if any)
    - warnings: list of warnings (if any)

    GSTC sections covered:
    - 8.5.12.1: Auditor conclusions (Conform/NotConform/NotAssessed)
    - 8.5.12.4-6: Risk assessment (HIGH/LOW/EXTREMELY_LOW)
    - 8.5.12.8-9: Audit duration rules (1/0.5/2+ days)
    - 8.5.12.9: Extremely low risk qualification (6 criteria)
    - 8.5.12.12-14: Sensitive area assessment
    - 8.5.10.3-4: 3-year certification cycle
    - 8.5.19.1: Surveillance timing (12/24-month windows)
    - 8.5.19.5: Section coverage restrictions
    """
    obj = await db.get(Audit, audit_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Audit not found")

    result = await validate_audit_against_gstc(audit_id, obj)
    return result


# --- Team members ---

@router.get("/{audit_id}/team-members", response_model=list[AuditTeamMemberOut])
async def list_team(audit_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(AuditTeamMember).where(AuditTeamMember.audit_id == audit_id))
    return result.scalars().all()


@router.post("/{audit_id}/team-members", response_model=AuditTeamMemberOut, status_code=201)
async def add_team_member(audit_id: UUID, payload: AuditTeamMemberCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = AuditTeamMember(audit_id=audit_id, **payload.model_dump(exclude={"audit_id"}))
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


# --- Locations ---

@router.get("/{audit_id}/locations", response_model=list[AuditLocationOut])
async def list_locations(audit_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(AuditLocation).where(AuditLocation.audit_id == audit_id))
    return result.scalars().all()


@router.post("/{audit_id}/locations", response_model=AuditLocationOut, status_code=201)
async def add_location(audit_id: UUID, payload: AuditLocationCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = AuditLocation(audit_id=audit_id, **payload.model_dump(exclude={"audit_id"}))
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


# --- Processes in scope ---

@router.get("/{audit_id}/processes", response_model=list[AuditProcessOut])
async def list_audit_processes(audit_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(AuditProcess).where(AuditProcess.audit_id == audit_id))
    return result.scalars().all()


@router.post("/{audit_id}/processes", response_model=AuditProcessOut, status_code=201)
async def add_audit_process(audit_id: UUID, payload: AuditProcessCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = AuditProcess(audit_id=audit_id, process_id=payload.process_id)
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj
