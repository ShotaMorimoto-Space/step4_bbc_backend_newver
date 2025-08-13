from __future__ import annotations
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models import CoachingReservation
from app.schemas.reservation import CoachingReservationCreate, CoachingReservationUpdate


class CoachingReservationCRUD:
    @staticmethod
    async def create_reservation(db: AsyncSession, reservation: CoachingReservationCreate) -> CoachingReservation:
        db_reservation = CoachingReservation(**reservation.model_dump(exclude_unset=True))
        db.add(db_reservation)
        await db.commit()
        await db.refresh(db_reservation)
        return db_reservation

    @staticmethod
    async def get_reservation(db: AsyncSession, session_id: UUID) -> Optional[CoachingReservation]:
        res = await db.execute(
            select(CoachingReservation).where(CoachingReservation.session_id == session_id)
        )
        return res.scalar_one_or_none()

    @staticmethod
    async def get_reservations_by_user(db: AsyncSession, user_id: UUID) -> List[CoachingReservation]:
        res = await db.execute(
            select(CoachingReservation)
            .where(CoachingReservation.user_id == user_id)
            .order_by(CoachingReservation.session_date.desc())
        )
        return res.scalars().all()

    @staticmethod
    async def get_reservations_by_coach(db: AsyncSession, coach_id: UUID) -> List[CoachingReservation]:
        res = await db.execute(
            select(CoachingReservation)
            .where(CoachingReservation.coach_id == coach_id)
            .order_by(CoachingReservation.session_date.desc())
        )
        return res.scalars().all()

    @staticmethod
    async def update_reservation(
        db: AsyncSession, session_id: UUID, reservation_update: CoachingReservationUpdate
    ) -> Optional[CoachingReservation]:
        update_data = {k: v for k, v in reservation_update.model_dump(exclude_unset=True).items() if v is not None}

        if update_data:
            await db.execute(
                update(CoachingReservation).where(CoachingReservation.session_id == session_id).values(**update_data)
            )
            await db.commit()

        return await CoachingReservationCRUD.get_reservation(db, session_id)


coaching_reservation_crud = CoachingReservationCRUD()
