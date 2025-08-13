from __future__ import annotations
from pydantic import BaseModel, EmailStr, field_serializer
from typing import Optional
from datetime import date, datetime
from app.utils.timezone import to_jst

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    usertype: str = "user"
    birthday: Optional[date] = None
    line_user_id: Optional[str] = None
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    golf_score_ave: Optional[int] = None
    golf_exp: Optional[int] = None
    zip_code: Optional[str] = None
    state: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    sport_exp: Optional[str] = None
    industry: Optional[str] = None
    job_title: Optional[str] = None
    position: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    new_password: Optional[str] = None
    birthday: Optional[date] = None
    line_user_id: Optional[str] = None
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    golf_score_ave: Optional[int] = None
    golf_exp: Optional[int] = None
    zip_code: Optional[str] = None
    state: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    sport_exp: Optional[str] = None
    industry: Optional[str] = None
    job_title: Optional[str] = None
    position: Optional[str] = None

class UserResponse(BaseModel):
    user_id: str
    usertype: str
    username: str
    email: EmailStr
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    birthday: Optional[date] = None
    golf_score_ave: Optional[int] = None
    golf_exp: Optional[int] = None
    zip_code: Optional[str] = None
    state: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    sport_exp: Optional[str] = None
    industry: Optional[str] = None
    job_title: Optional[str] = None
    position: Optional[str] = None
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

class UserMini(BaseModel):
    user_id: str
    username: str
    email: EmailStr

    class Config:
        from_attributes = True
