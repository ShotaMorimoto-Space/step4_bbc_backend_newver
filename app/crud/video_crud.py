from __future__ import annotations
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
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
    # ---- 作成 ----
    @staticmethod
    def create_video(db: Session, video: VideoCreate) -> Video:
        db_video = Video(**video.model_dump(exclude_unset=True))
        db_video.is_pinned = False
        db_video.is_reviewed = False
        db.add(db_video)
        db.commit()
        db.refresh(db_video)
        return db_video

    # ---- 取得 ----
    @staticmethod
    def get_video(db: Session, video_id: UUID) -> Optional[Video]:
        res = db.execute(select(Video).where(Video.video_id == video_id))
        return res.scalar_one_or_none()

    @staticmethod
    def get_video_with_sections(db: Session, video_id: UUID) -> Optional[Video]:
        res = db.execute(
            select(Video)
            .options(selectinload(Video.section_groups).selectinload(SectionGroup.sections))
            .where(Video.video_id == video_id)
        )
        return res.scalars().unique().one_or_none()

    @staticmethod
    def get_videos_by_user(
        db: Session, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Video]:
        res = db.execute(
            select(Video)
            .where(Video.user_id == user_id)
            .order_by(Video.upload_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return res.scalars().all()

    @staticmethod
    def get_all_videos_with_sections(
        db: Session, skip: int = 0, limit: int = 100
    ) -> List[Video]:
        res = db.execute(
            select(Video)
            .options(selectinload(Video.section_groups).selectinload(SectionGroup.sections))
            .order_by(Video.upload_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return res.scalars().unique().all()

    # ---- 更新 ----
    @staticmethod
    def update_video(db: Session, video_id: UUID, video_update: VideoUpdate) -> Optional[Video]:
        update_data = {
            k: v for k, v in video_update.model_dump(exclude_unset=True).items() if v is not None
        }
        update_data = _normalize_video_update_payload(update_data)

        if update_data:
            db.execute(
                update(Video).where(Video.video_id == video_id).values(**update_data)
            )
            db.commit()

        return VideoCRUD.get_video(db, video_id)

    # ---- 削除 ----
    @staticmethod
    def delete_video(db: Session, video_id: UUID) -> bool:
        res = db.execute(delete(Video).where(Video.video_id == video_id))
        db.commit()
        return (res.rowcount or 0) > 0

    # ---- ピン留め ----
    @staticmethod
    def set_pinned_video(db: Session, user_id: UUID, video_id: UUID):
        # 既存のピンを外す
        db.execute(
            update(Video).where(Video.user_id == user_id).values(is_pinned=False)
        )
        # 新しいピンを設定
        db.execute(
            update(Video).where(Video.video_id == video_id).values(is_pinned=True)
        )
        db.commit()

    @staticmethod
    def get_pinned_video(db: Session, user_id: UUID) -> Optional[Video]:
        res = db.execute(
            select(Video).where(Video.user_id == user_id, Video.is_pinned == True)
        )
        return res.scalars().first()

    # ---- 添削済み ----
    @staticmethod
    def mark_video_as_reviewed(db: Session, video_id: UUID):
        db.execute(
            update(Video).where(Video.video_id == video_id).values(is_reviewed=True)
        )
        db.commit()


# インスタンス（既存の import スタイル互換）
video_crud = VideoCRUD()
