from __future__ import annotations
from pydantic import BaseModel, EmailStr, field_serializer
from typing import Optional
from datetime import date, datetime
from app.utils.timezone import to_jst
from uuid import UUID


# -------------------------
# 初回登録用（必須）
# -------------------------
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    gender: Optional[str] = None    # Enum化してもOK
    birthday: Optional[date] = None


# -------------------------
# プロフィール更新用（任意）
# -------------------------
class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    gender: Optional[str] = None
    birthday: Optional[date] = None
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


# -------------------------
# メールアドレス更新
# -------------------------
class UserEmailUpdate(BaseModel):
    email: EmailStr


# -------------------------
# パスワード更新
# -------------------------
class UserPasswordUpdate(BaseModel):
    new_password: str


# -------------------------
# レスポンス
# -------------------------
class UserResponse(BaseModel):
    user_id: UUID
    usertype: str
    username: str
    email: EmailStr
    gender: Optional[str] = None
    birthday: Optional[date] = None
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
    created_at: datetime
    updated_at: datetime

    # UUID → str に変換
    @field_serializer("user_id")
    def _id(self, v) -> str:
        return str(v)

    @field_serializer("created_at")
    def _c(self, dt: datetime) -> str:
        return to_jst(dt).isoformat()

    @field_serializer("updated_at")
    def _u(self, dt: datetime) -> str:
        return to_jst(dt).isoformat()

    class Config:
        from_attributes = True


# -------------------------
# 簡易レスポンス
# -------------------------
class UserMini(BaseModel):
    user_id: str
    username: str
    email: EmailStr

    # UUID → str に変換
    @field_serializer("user_id")
    def _id(self, v) -> str:
        return str(v)

    class Config:
        from_attributes = True
