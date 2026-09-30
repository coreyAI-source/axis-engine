from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.org import User, Role
from ..schemas.org import UserCreate, UserUpdate, UserOut
from ..utils.security import get_current_user, require_admin, hash_password

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserOut])
async def list_users(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    result = await db.execute(select(User).where(User.active_flag == True, User.organisation_id == current_user.organisation_id))
    return result.scalars().all()


@router.post("/", response_model=UserOut, status_code=201)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db), current_user=Depends(require_admin)):
    if payload.organisation_id != current_user.organisation_id:
        raise HTTPException(status_code=403, detail="Users must belong to your organisation")
    if payload.role_code not in {"admin", "compliance_manager", "lead_auditor", "auditor", "process_owner", "viewer"}:
        raise HTTPException(status_code=422, detail="Choose a valid user role")
    if len(payload.password.encode("utf-8")) > 72:
        raise HTTPException(status_code=422, detail="Password must fit within 72 UTF-8 bytes")
    if payload.role_id:
        role = await db.get(Role, payload.role_id)
        if not role or role.code != payload.role_code:
            raise HTTPException(status_code=422, detail="Role ID and role code must match")
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        organisation_id=payload.organisation_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role_id=payload.role_id,
        role_code=payload.role_code,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    user = await db.get(User, user_id)
    if not user or user.organisation_id != current_user.organisation_id:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(user_id: UUID, payload: UserUpdate, db: AsyncSession = Depends(get_db), current_user=Depends(require_admin)):
    user = await db.get(User, user_id)
    if not user or user.organisation_id != current_user.organisation_id:
        raise HTTPException(status_code=404, detail="User not found")
    changes = payload.model_dump(exclude_unset=True)
    if "role_code" in changes and changes["role_code"] not in {"admin", "compliance_manager", "lead_auditor", "auditor", "process_owner", "viewer"}:
        raise HTTPException(status_code=422, detail="Choose a valid user role")
    if user.id == current_user.id and (changes.get("active_flag") is False or ("role_code" in changes and changes["role_code"] != "admin")):
        raise HTTPException(status_code=422, detail="You cannot remove your own administrator access")
    if changes.get("role_id"):
        role = await db.get(Role, changes["role_id"])
        if not role or role.code != changes.get("role_code", user.role_code):
            raise HTTPException(status_code=422, detail="Role ID and role code must match")
    elif "role_code" in changes:
        changes["role_id"] = None
    for field, value in changes.items():
        setattr(user, field, value)
    await db.flush()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
async def deactivate_user(user_id: UUID, db: AsyncSession = Depends(get_db), current_user=Depends(require_admin)):
    user = await db.get(User, user_id)
    if not user or user.organisation_id != current_user.organisation_id:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=422, detail="You cannot deactivate your own account")
    user.active_flag = False
    await db.flush()
