"""
Shared CRUD helper used by all routers.
Each router module imports make_crud_router and mounts it.
"""
from typing import Any, Callable, Type
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.base import Base
from ..utils.security import get_current_user


def make_crud_router(
    prefix: str,
    tag: str,
    model: Type[Base],
    create_schema: Type[BaseModel],
    update_schema: Type[BaseModel],
    out_schema: Type[BaseModel],
    soft_delete_field: str | None = "active_flag",
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=[tag])

    @router.get("/", response_model=list[out_schema])
    async def list_items(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
        result = await db.execute(select(model))
        return result.scalars().all()

    @router.post("/", response_model=out_schema, status_code=201)
    async def create_item(payload: create_schema, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
        obj = model(**payload.model_dump(exclude_unset=True))
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    @router.get("/{item_id}", response_model=out_schema)
    async def get_item(item_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
        obj = await db.get(model, item_id)
        if not obj:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        return obj

    @router.patch("/{item_id}", response_model=out_schema)
    async def update_item(item_id: UUID, payload: update_schema, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
        obj = await db.get(model, item_id)
        if not obj:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        await db.flush()
        await db.refresh(obj)
        return obj

    @router.delete("/{item_id}", status_code=204)
    async def delete_item(item_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
        obj = await db.get(model, item_id)
        if not obj:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        if soft_delete_field and hasattr(obj, soft_delete_field):
            setattr(obj, soft_delete_field, False)
        else:
            await db.delete(obj)
        await db.flush()

    return router
