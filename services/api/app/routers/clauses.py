from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.standard import Clause
from ..schemas.standard import ClauseOut
from ..utils.security import get_current_user

router = APIRouter(prefix="/clauses", tags=["clauses"])


@router.get("/", response_model=list[ClauseOut])
async def list_clauses(
    standard_code: str | None = None,
    hls_section: str | None = None,
    requires_documented_information: bool | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    from ..models.standard import Standard
    q = select(Clause).where(Clause.active_flag == True)
    if standard_code:
        q = q.join(Standard).where(Standard.code == standard_code)
    if hls_section:
        q = q.where(Clause.hls_section == hls_section)
    if requires_documented_information is not None:
        q = q.where(Clause.requires_documented_information == requires_documented_information)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{clause_id}", response_model=ClauseOut)
async def get_clause(clause_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = await db.get(Clause, clause_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Clause not found")
    return obj
