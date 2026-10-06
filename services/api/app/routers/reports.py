from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..utils.security import get_current_user
from ..services import reporting, gstc_standard
from ..utils.gstc_validation import validate_criteria_codes, get_gstc_standard_info

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


@router.get("/gstc-standard/metadata")
async def gstc_metadata(_=Depends(get_current_user)):
    """Get GSTC Hotel Standard v4.01 metadata."""
    return gstc_standard.get_standard_metadata()


@router.get("/gstc-standard/criteria")
async def gstc_all_criteria(_=Depends(get_current_user)):
    """Get all GSTC Hotel Standard v4.01 criteria."""
    return {"criteria": gstc_standard.get_all_criteria()}


@router.get("/gstc-standard/pillar/{pillar_code}")
async def gstc_pillar_criteria(pillar_code: str, _=Depends(get_current_user)):
    """Get GSTC criteria for a specific pillar (A, B, C, or D)."""
    criteria = gstc_standard.get_pillar_criteria(pillar_code)
    if not criteria:
        raise HTTPException(status_code=404, detail=f"Pillar {pillar_code} not found")
    return {"pillar": pillar_code.upper(), "criteria": criteria}


@router.post("/gstc-standard/validate-codes")
async def validate_gstc_codes(payload: dict, _=Depends(get_current_user)):
    """Validate a list of criteria codes against the GSTC standard.

    Request: {"codes": ["A1", "B2", "X1", "ZZ99"]}
    Response: {"valid": [...], "invalid": [...], "custom": [...], "errors": [...]}
    """
    codes = payload.get("codes", [])
    if not isinstance(codes, list):
        raise HTTPException(status_code=422, detail="codes must be a list of strings")
    return validate_criteria_codes(codes)


@router.get("/gstc-standard/info")
async def gstc_standard_info(_=Depends(get_current_user)):
    """Get comprehensive GSTC Hotel Standard information for audit setup."""
    return get_gstc_standard_info()
