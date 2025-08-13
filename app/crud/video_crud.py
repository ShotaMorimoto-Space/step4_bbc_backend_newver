from __future__ import annotations
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.models import Video, SectionGroup
from app.schemas.video import VideoCreate, VideoUpdate


def _normalize_video_update_payload(data: dict) -> dict:
    """相手側のキー名が来ても内部名へ正規化（保険）"""
    if "swing_type" in data and "swing_form" not in data:
        data["swing_form"] = data.pop("swing_type")
    if "description" in data and "swing_note" not in data:
        data["swing_note"] = data.pop("description")
    return data


class VideoCRUD:
    @staticmethod
    async def create_video(db: AsyncSession, video: VideoCreate) -> Video:
        db_video = Video(**video.model_dump(exclude_unset=True))
        db.add(db_video)
        await db.commit()
        await db.refresh(db_video)
        return db_video

    @staticmethod
    async def get_video(db: AsyncSession, video_id: UUID) -> Optional[Video]:
        res = await db.execute(select(Video).where(Video.video_id == video_id))
        return res.scalar_one_or_none()

    @staticmethod
    async def get_video_with_sections(db: AsyncSession, video_id: UUID) -> Optional[Video]:
        res = await db.execute(
            select(Video)
            .options(selectinload(Video.section_groups).selectinload(SectionGroup.sections))
            .where(Video.video_id == video_id)
        )
        return res.scalars().unique().one_or_none()

    @staticmethod
    async def get_videos_by_user(db: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Video]:
        res = await db.execute(
            select(Video)
            .where(Video.user_id == user_id)
            .order_by(Video.upload_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return res.scalars().all()

    @staticmethod
    async def get_all_videos_with_sections(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Video]:
        res = await db.execute(
            select(Video)
            .options(selectinload(Video.section_groups).selectinload(SectionGroup.sections))
            .order_by(Video.upload_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return res.scalars().unique().all()

    @staticmethod
    async def update_video(db: AsyncSession, video_id: UUID, video_update: VideoUpdate) -> Optional[Video]:
        update_data = {k: v for k, v in video_update.model_dump(exclude_unset=True).items() if v is not None}
        update_data = _normalize_video_update_payload(update_data)

        if update_data:
            await db.execute(
                update(Video).where(Video.video_id == video_id).values(**update_data)
            )
            await db.commit()

        return await VideoCRUD.get_video(db, video_id)

    @staticmethod
    async def delete_video(db: AsyncSession, video_id: UUID) -> bool:
        res = await db.execute(delete(Video).where(Video.video_id == video_id))
        await db.commit()
        return (res.rowcount or 0) > 0


# インスタンス（既存の import スタイル互換）
video_crud = VideoCRUD()
