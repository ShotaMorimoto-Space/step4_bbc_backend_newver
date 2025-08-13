from __future__ import annotations
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Coach
from app.schemas.coach import CoachCreate
from app.core.security import get_password_hash


class CoachCRUD:
    @staticmethod
    async def create_coach(db: AsyncSession, coach_in: CoachCreate) -> Coach:
        coach = Coach(
            usertype=coach_in.usertype or "coach",
            coachname=coach_in.coachname,
            email=coach_in.email,
            birthday=coach_in.birthday,
            sex=coach_in.sex,
            SNS_handle_instagram=coach_in.SNS_handle_instagram,
            SNS_handle_X=coach_in.SNS_handle_X,
            SNS_handle_youtube=coach_in.SNS_handle_youtube,
            SNS_handle_facebook=coach_in.SNS_handle_facebook,
            SNS_handle_tiktok=coach_in.SNS_handle_tiktok,
            password_hash=get_password_hash(coach_in.password),
            line_user_id=coach_in.line_user_id,
            profile_picture_url=coach_in.profile_picture_url,
            bio=coach_in.bio,
            hourly_rate=coach_in.hourly_rate,
            location_id=coach_in.location_id,
        )
        db.add(coach)
        await db.commit()
        await db.refresh(coach)
        return coach

    @staticmethod
    async def get(db: AsyncSession, coach_id: UUID) -> Optional[Coach]:
        res = await db.execute(select(Coach).where(Coach.coach_id == coach_id))
        return res.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[Coach]:
        res = await db.execute(select(Coach).where(Coach.email == email))
        return res.scalar_one_or_none()

    @staticmethod
    async def list(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Coach]:
        res = await db.execute(
            select(Coach).order_by(Coach.created_at.desc()).offset(skip).limit(limit)
        )
        return res.scalars().all()


coach_crud = CoachCRUD()
