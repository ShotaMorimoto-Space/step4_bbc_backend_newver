from __future__ import annotations
from pydantic import BaseModel, EmailStr, field_serializer
from typing import Optional
from datetime import date, datetime
from app.utils.timezone import to_jst
from uuid import UUID

class CoachCreate(BaseModel):
    coachname: str
    email: EmailStr
    password: str
    usertype: str = "coach"
    birthday: Optional[date] = None
    sex: Optional[str] = None
    SNS_handle_instagram: Optional[str] = None
    SNS_handle_X: Optional[str] = None
    SNS_handle_youtube: Optional[str] = None
    SNS_handle_facebook: Optional[str] = None
    SNS_handle_tiktok: Optional[str] = None
    line_user_id: Optional[str] = None
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    hourly_rate: Optional[int] = None
    location_id: Optional[str] = None
    golf_exp: Optional[int] = None
    certification: Optional[str] = None
    setting_1: Optional[str] = None
    setting_2: Optional[str] = None
    setting_3: Optional[str] = None
    lesson_rank: Optional[str] = None

class CoachUpdate(BaseModel):
    coachname: Optional[str] = None
    email: Optional[EmailStr] = None
    new_password: Optional[str] = None
    birthday: Optional[date] = None
    sex: Optional[str] = None
    SNS_handle_instagram: Optional[str] = None
    SNS_handle_X: Optional[str] = None
    SNS_handle_youtube: Optional[str] = None
    SNS_handle_facebook: Optional[str] = None
    SNS_handle_tiktok: Optional[str] = None
    line_user_id: Optional[str] = None
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    hourly_rate: Optional[int] = None
    location_id: Optional[str] = None
    golf_exp: Optional[int] = None
    certification: Optional[str] = None
    setting_1: Optional[str] = None
    setting_2: Optional[str] = None
    setting_3: Optional[str] = None
    lesson_rank: Optional[str] = None

class CoachResponse(BaseModel):
    coach_id: UUID
    usertype: str
    coachname: str
    email: EmailStr
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    birthday: Optional[date] = None
    sex: Optional[str] = None
    SNS_handle_instagram: Optional[str] = None
    SNS_handle_X: Optional[str] = None
    SNS_handle_youtube: Optional[str] = None
    SNS_handle_facebook: Optional[str] = None
    SNS_handle_tiktok: Optional[str] = None
    line_user_id: Optional[str] = None
    hourly_rate: Optional[int] = None
    location_id: Optional[str] = None
    golf_exp: Optional[int] = None
    certification: Optional[str] = None
    setting_1: Optional[str] = None
    setting_2: Optional[str] = None
    setting_3: Optional[str] = None
    lesson_rank: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at")
    def _c(self, dt: datetime) -> datetime:
        return to_jst(dt)

    @field_serializer("updated_at")
    def _u(self, dt: datetime) -> datetime:
        return to_jst(dt)

    class Config:
        from_attributes = True

class CoachOut(BaseModel):
    coach_id: UUID
    coachname: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True
