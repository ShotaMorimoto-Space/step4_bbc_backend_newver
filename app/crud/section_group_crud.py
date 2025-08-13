from __future__ import annotations
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models import SectionGroup
from app.schemas.section import SectionGroupCreate


class SectionGroupCRUD:
    @staticmethod
    async def create_section_group(db: AsyncSession, section_group: SectionGroupCreate) -> SectionGroup:
        db_section_group = SectionGroup(**section_group.model_dump(exclude_unset=True))
        db.add(db_section_group)
        await db.commit()
        await db.refresh(db_section_group)
        return db_section_group

    @staticmethod
    async def get_section_group(db: AsyncSession, section_group_id: UUID) -> Optional[SectionGroup]:
        res = await db.execute(select(SectionGroup).where(SectionGroup.section_group_id == section_group_id))
        return res.scalar_one_or_none()

    @staticmethod
    async def get_section_group_with_sections(db: AsyncSession, section_group_id: UUID) -> Optional[SectionGroup]:
        res = await db.execute(
            select(SectionGroup)
            .options(selectinload(SectionGroup.sections))
            .where(SectionGroup.section_group_id == section_group_id)
        )
        return res.scalars().unique().one_or_none()

    @staticmethod
    async def add_overall_feedback(
        db: AsyncSession,
        section_group_id: UUID,
        overall_feedback: str,
        overall_feedback_summary: str,
    ) -> Optional[SectionGroup]:
        from datetime import datetime, timezone

        await db.execute(
            update(SectionGroup)
            .where(SectionGroup.section_group_id == section_group_id)
            .values(
                overall_feedback=overall_feedback,
                overall_feedback_summary=overall_feedback_summary,
                feedback_created_at=datetime.now(timezone.utc),
            )
        )
        await db.commit()
        return await SectionGroupCRUD.get_section_group(db, section_group_id)

    @staticmethod
    async def add_next_training_menu(
        db: AsyncSession,
        section_group_id: UUID,
        next_training_menu: str,
        next_training_menu_summary: str,
    ) -> Optional[SectionGroup]:
        from datetime import datetime, timezone

        await db.execute(
            update(SectionGroup)
            .where(SectionGroup.section_group_id == section_group_id)
            .values(
                next_training_menu=next_training_menu,
                next_training_menu_summary=next_training_menu_summary,
                feedback_created_at=datetime.now(timezone.utc),
            )
        )
        await db.commit()
        return await SectionGroupCRUD.get_section_group(db, section_group_id)


section_group_crud = SectionGroupCRUD()
