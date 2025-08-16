from pydantic import BaseModel, Field, field_serializer
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.utils.timezone import to_jst
from .common import SwingSectionTag


# ---- Markup (図形) ----
class MarkupObject(BaseModel):
    type: str  # "circle", "line", "arrow" など
    coordinates: List[float]
    color: str
    size: Optional[float] = None


# ---- Coaching Session ----
class CoachingSessionBase(BaseModel):
    video_id: UUID
    user_id: UUID
    coach_id: UUID
    status: str  # "pending" | "in_progress" | "completed"

class CoachingSessionCreate(BaseModel):
    video_id: UUID
    coach_id: UUID

class CoachingSessionResponse(CoachingSessionBase):
    session_id: UUID
    requested_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    @field_serializer("requested_at")
    def _ser_req(self, dt: datetime) -> datetime:
        return to_jst(dt)

    @field_serializer("completed_at")
    def _ser_compl(self, dt: Optional[datetime]) -> Optional[datetime]:
        return to_jst(dt) if dt else None

    @field_serializer("created_at")
    def _ser_cr(self, dt: datetime) -> datetime:
        return to_jst(dt)

    @field_serializer("updated_at")
    def _ser_upd(self, dt: datetime) -> datetime:
        return to_jst(dt)

    model_config = {"from_attributes": True}

class CoachingSessionUpdate(BaseModel):
    status: Optional[str] = None
    completed_at: Optional[datetime] = None


# ---- SectionGroup ----
class SectionGroupBase(BaseModel):
    video_id: UUID
    session_id: UUID   # ★ 追加: どのセッションに属するか

class SectionGroupCreate(SectionGroupBase):
    pass

class SectionGroupResponse(SectionGroupBase):
    section_group_id: UUID
    created_at: datetime
    # 相手機能互換用（DB無くてもレスポンス上は任意）
    overall_feedback: Optional[str] = None
    overall_feedback_summary: Optional[str] = None
    next_training_menu: Optional[str] = None
    next_training_menu_summary: Optional[str] = None
    feedback_created_at: Optional[datetime] = None

    @field_serializer("feedback_created_at")
    def _ser_fb(self, dt: Optional[datetime]) -> Optional[datetime]:
        return to_jst(dt) if dt else None

    model_config = {"from_attributes": True}


# ---- SwingSection ----
class SwingSectionBase(BaseModel):
    section_group_id: UUID
    start_sec: Decimal
    end_sec: Decimal
    image_url: Optional[str] = None
    tags: Optional[List[SwingSectionTag]] = None
    markup_json: Optional[List[MarkupObject]] = None

class SwingSectionCreate(SwingSectionBase):
    pass

class SwingSectionUpdate(BaseModel):
    start_sec: Optional[Decimal] = None
    end_sec: Optional[Decimal] = None
    image_url: Optional[str] = None
    tags: Optional[List[SwingSectionTag]] = None
    markup_json: Optional[List[MarkupObject]] = None
    coach_comment: Optional[str] = None

class SwingSectionResponse(SwingSectionBase):
    section_id: UUID
    coach_comment: Optional[str] = None
    coach_comment_summary: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---- コメント / フィードバック ----
class CoachCommentRequest(BaseModel):
    section_id: UUID
    comment: str

class CoachCommentResponse(BaseModel):
    section_id: UUID
    comment: str
    summary: str

class OverallFeedbackRequest(BaseModel):
    section_group_id: UUID
    feedback_type: str  # "overall" or "next_training"

class OverallFeedbackResponse(BaseModel):
    section_group_id: UUID
    overall_feedback: Optional[str] = None
    overall_feedback_summary: Optional[str] = None
    next_training_menu: Optional[str] = None
    next_training_menu_summary: Optional[str] = None
    feedback_created_at: Optional[datetime] = None
