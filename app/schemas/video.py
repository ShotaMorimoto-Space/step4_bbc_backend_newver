# app/schemas/video.py
from pydantic import BaseModel, Field, field_serializer
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.utils.timezone import to_jst
from .section import SectionGroupResponse, SwingSectionResponse


class VideoBase(BaseModel):
    user_id: UUID
    video_url: str
    thumbnail_url: Optional[str] = None
    club_type: Optional[str] = None
    # 内部名（既存実装）
    swing_form: Optional[str] = None
    swing_note: Optional[str] = None

class VideoCreate(VideoBase):
    # 相手ペイロードの別名をここで吸収（内部は swing_form / swing_note）
    swing_form: Optional[str] = Field(None, alias="swing_type")
    swing_note: Optional[str] = Field(None, alias="description")

    model_config = {"populate_by_name": True}

class VideoUpdate(BaseModel):
    club_type: Optional[str] = None
    swing_form: Optional[str] = Field(None, alias="swing_type")
    swing_note: Optional[str] = Field(None, alias="description")
    thumbnail_url: Optional[str] = None

    model_config = {"populate_by_name": True}

class VideoResponse(VideoBase):
    video_id: UUID
    upload_date: datetime
    section_group_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    @field_serializer("upload_date")
    def _ser_up(self, dt: datetime) -> datetime:
        return to_jst(dt)

    @field_serializer("created_at")
    def _ser_cr(self, dt: datetime) -> datetime:
        return to_jst(dt)

    @field_serializer("updated_at")
    def _ser_upd(self, dt: datetime) -> datetime:
        return to_jst(dt)

    model_config = {"from_attributes": True}


class VideoUploadRequest(BaseModel):
    club_type: Optional[str] = None
    swing_form: Optional[str] = Field(None, alias="swing_type")
    swing_note: Optional[str] = Field(None, alias="description")

    model_config = {"populate_by_name": True}


class VideoWithSectionsResponse(VideoResponse):
    section_group: Optional[SectionGroupResponse] = None
    sections: List[SwingSectionResponse] = Field(default_factory=list)
