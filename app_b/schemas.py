# app/schemas.py
from __future__ import annotations
from pydantic import BaseModel
from pydantic.config import ConfigDict
from typing import Optional, List
from datetime import datetime, date, time
from decimal import Decimal

# --------------- 共通: ORMからの変換を許可 ---------------
class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ======================== Location ========================
class LocationBase(BaseModel):
    location_name: Optional[str] = None
    state: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    zipcode: Optional[str] = None
    phone_number: Optional[str] = None
    website_url: Optional[str] = None
    opening_hours: Optional[str] = None
    capacity: Optional[int] = None
    description: Optional[str] = None
    image_url_main: Optional[str] = None
    image_url_sub1: Optional[str] = None
    image_url_sub2: Optional[str] = None
    image_url_sub3: Optional[str] = None
    image_url_sub4: Optional[str] = None

class LocationCreate(LocationBase):
    # 必須があればここで指定（例：location_name を必須にしたい場合はコメント解除）
    # location_name: str
    pass

class LocationUpdate(LocationBase):
    pass  # 全て任意（部分更新用）

class LocationRead(LocationBase, ORMBase):
    location_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ========================= Coach =========================
# ※ 既存DBの列名（Sex, Lesson_rank など）をそのまま採用
class CoachBase(BaseModel):
    usertype: Optional[str] = None
    coachname: str  # 作成時に最低限は必須にしておく例
    email: Optional[str] = None
    birthday: Optional[str] = None
    Sex: Optional[str] = None

    SNS_handle_instagram: Optional[str] = None
    SNS_handle_X: Optional[str] = None
    SNS_handle_youtube: Optional[str] = None
    SNS_handle_facebook: Optional[str] = None
    SNS_handle_tiktok: Optional[str] = None

    password_hash: Optional[str] = None
    line_user_id: Optional[str] = None
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None

    hourly_rate: Optional[Decimal] = None
    location_id: Optional[str] = None
    golf_exp: Optional[int] = None
    certification: Optional[str] = None
    setting_1: Optional[str] = None
    setting_2: Optional[str] = None
    setting_3: Optional[str] = None
    Lesson_rank: Optional[str] = None

class CoachCreate(CoachBase):
    pass

class CoachUpdate(BaseModel):
    # 部分更新で全て任意
    usertype: Optional[str] = None
    coachname: Optional[str] = None
    email: Optional[str] = None
    birthday: Optional[str] = None
    Sex: Optional[str] = None
    SNS_handle_instagram: Optional[str] = None
    SNS_handle_X: Optional[str] = None
    SNS_handle_youtube: Optional[str] = None
    SNS_handle_facebook: Optional[str] = None
    SNS_handle_tiktok: Optional[str] = None
    password_hash: Optional[str] = None
    line_user_id: Optional[str] = None
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    hourly_rate: Optional[Decimal] = None
    location_id: Optional[str] = None
    golf_exp: Optional[int] = None
    certification: Optional[str] = None
    setting_1: Optional[str] = None
    setting_2: Optional[str] = None
    setting_3: Optional[str] = None
    Lesson_rank: Optional[str] = None

class CoachRead(CoachBase, ORMBase):
    coach_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ========================== User =========================
# ※ 既存DBの列名（Position など）をそのまま採用
class UserBase(BaseModel):
    usertype: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    password_hash: Optional[str] = None
    line_user_id: Optional[str] = None
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
    Position: Optional[str] = None

class UserCreate(UserBase):
    # 例：最小限 username を必須化したい場合はコメント解除
    # username: str
    pass

class UserUpdate(UserBase):
    pass

class UserRead(UserBase, ORMBase):
    user_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ===================== CoachLocation =====================
class CoachLocationBase(BaseModel):
    notes: Optional[str] = None

class CoachLocationCreate(CoachLocationBase):
    coach_id: str
    location_id: str

class CoachLocationUpdate(CoachLocationBase):
    pass  # 今回は notes のみ更新対象想定

class CoachLocationRead(CoachLocationBase, ORMBase):
    coach_id: str
    location_id: str


# ================== CoachingReservation ==================
class CoachingReservationBase(BaseModel):
    session_date: Optional[date] = None
    session_time: Optional[time] = None
    location_type: Optional[str] = None
    location_id: Optional[str] = None
    status: Optional[str] = None
    price: Optional[Decimal] = None
    payment_status: Optional[str] = None

class CoachingReservationCreate(CoachingReservationBase):
    # 予約の主キーはサーバー側生成にする想定（UUIDなど）
    user_id: str
    coach_id: str
    session_date: date
    session_time: time

class CoachingReservationUpdate(CoachingReservationBase):
    # 予約の状態変更/日時変更等で任意
    pass

class CoachingReservationRead(CoachingReservationBase, ORMBase):
    session_id: str
    user_id: Optional[str] = None
    coach_id: Optional[str] = None


# =========（オプション）ネスト付きの返却形 =========
class CoachReadWithLocation(CoachRead):
    # JOINして返す場合に使用
    location: Optional[LocationRead] = None

class LocationReadWithCoaches(LocationRead):
    coaches: Optional[List[CoachRead]] = None

class CoachingReservationExpanded(CoachingReservationRead):
    user: Optional[UserRead] = None
    coach: Optional[CoachRead] = None
    location: Optional[LocationRead] = None
