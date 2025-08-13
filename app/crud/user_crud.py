from __future__ import annotations
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


class UserCRUD:
    @staticmethod
    async def create_user(db: AsyncSession, payload: UserCreate) -> User:
        user = User(
            username=payload.username,
            email=payload.email,
            usertype=payload.usertype or "user",
            password_hash=get_password_hash(payload.password),
            birthday=payload.birthday,
            line_user_id=payload.line_user_id,
            profile_picture_url=payload.profile_picture_url,
            bio=payload.bio,
            golf_score_ave=payload.golf_score_ave,
            golf_exp=payload.golf_exp,
            zip_code=payload.zip_code,
            state=payload.state,
            address1=payload.address1,
            address2=payload.address2,
            sport_exp=payload.sport_exp,
            industry=payload.industry,
            job_title=payload.job_title,
            position=payload.position,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get(db: AsyncSession, user_id: UUID) -> Optional[User]:
        res = await db.execute(select(User).where(User.user_id == user_id))
        return res.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        res = await db.execute(select(User).where(User.email == email))
        return res.scalar_one_or_none()

    @staticmethod
    async def get_by_line_user_id(db: AsyncSession, line_user_id: str) -> Optional[User]:
        if not line_user_id:
            return None
        res = await db.execute(select(User).where(User.line_user_id == line_user_id))
        return res.scalar_one_or_none()

    @staticmethod
    async def list(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        res = await db.execute(
            select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
        )
        return res.scalars().all()

    @staticmethod
    async def update_partial(db: AsyncSession, user_id: UUID, data: dict) -> Optional[User]:
        if not data:
            return await UserCRUD.get(db, user_id)
        await db.execute(update(User).where(User.user_id == user_id).values(**data))
        await db.commit()
        return await UserCRUD.get(db, user_id)


user_crud = UserCRUD()
