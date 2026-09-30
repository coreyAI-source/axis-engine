from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..utils.security import get_current_user
from ..services import reporting

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/audits/{audit_id}/document-review")
async def document_review_report(audit_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    data = await reporting.build_document_review_report(audit_id, db)
    return JSONResponse(content=data)


@router.get("/audits/{audit_id}/audit-plan")
async def audit_plan(audit_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    data = await reporting.build_audit_plan(audit_id, db)
    return JSONResponse(content=data)


@router.get("/audits/{audit_id}/timetable")
async def audit_timetable(audit_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    data = await reporting.build_audit_timetable(audit_id, db)
    return JSONResponse(content=data)


@router.get("/audits/{audit_id}/report")
async def audit_report(audit_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    data = await reporting.build_audit_report(audit_id, db)
    return JSONResponse(content=data)


@router.get("/audits/{audit_id}/findings-register")
async def findings_register(audit_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    data = await reporting.build_findings_register(audit_id, db)
    return JSONResponse(content=data)
