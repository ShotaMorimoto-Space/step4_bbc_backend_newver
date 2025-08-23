from __future__ import annotations
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete

from app.models import SwingSection
from app.schemas.section import SwingSectionCreate, SwingSectionUpdate


class SwingSectionCRUD:
    @staticmethod
    def create_section(db: Session, section: SwingSectionCreate) -> SwingSection:
        db_section = SwingSection(**section.model_dump(exclude_unset=True))
        db.add(db_section)
        await db.commit()
        await db.refresh(db_section)
        return db_section

    @staticmethod
    def get_section(db: Session, section_id: UUID) -> Optional[SwingSection]:
        res = await db.execute(select(SwingSection).where(SwingSection.section_id == section_id))
        return res.scalar_one_or_none()

    @staticmethod
    def get_sections_by_group(db: Session, section_group_id: UUID) -> List[SwingSection]:
        res = await db.execute(
            select(SwingSection).where(SwingSection.section_group_id == section_group_id).order_by(SwingSection.start_sec)
        )
        return res.scalars().all()

    @staticmethod
    def update_section(db: Session, section_id: UUID, section_update: SwingSectionUpdate) -> Optional[SwingSection]:
        update_data = {k: v for k, v in section_update.model_dump(exclude_unset=True).items() if v is not None}

        if update_data:
            await db.execute(
                update(SwingSection).where(SwingSection.section_id == section_id).values(**update_data)
            )
            await db.commit()

        return await SwingSectionCRUD.get_section(db, section_id)

    @staticmethod
    def delete_section(db: Session, section_id: UUID) -> bool:
        res = await db.execute(delete(SwingSection).where(SwingSection.section_id == section_id))
        await db.commit()
        return (res.rowcount or 0) > 0

    @staticmethod
    def add_coach_comment(db: Session, section_id: UUID, comment: str, summary: str) -> Optional[SwingSection]:
        await db.execute(
            update(SwingSection)
            .where(SwingSection.section_id == section_id)
            .values(coach_comment=comment, coach_comment_summary=summary)
        )
        await db.commit()
        return await SwingSectionCRUD.get_section(db, section_id)


swing_section_crud = SwingSectionCRUD()
