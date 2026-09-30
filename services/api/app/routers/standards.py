from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.standard import Standard, Clause
from ..schemas.standard import StandardOut, ClauseOut
from ..utils.security import get_current_user

router = APIRouter(prefix="/standards", tags=["standards"])


@router.get("/", response_model=list[StandardOut])
async def list_standards(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Standard))
    return result.scalars().all()


@router.get("/{standard_id}", response_model=StandardOut)
async def get_standard(standard_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = await db.get(Standard, standard_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Standard not found")
    return obj


@router.get("/{standard_id}/clauses", response_model=list[ClauseOut])
async def list_clauses_for_standard(standard_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(
        select(Clause).where(Clause.standard_id == standard_id, Clause.active_flag == True)
    )
    return result.scalars().all()
