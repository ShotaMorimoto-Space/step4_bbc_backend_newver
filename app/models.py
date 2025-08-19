from __future__ import annotations

import enum
import os
import ssl
import uuid
from datetime import datetime, date
import uuid
from uuid import UUID

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Date,
    Text,
    Integer,
    DECIMAL,
    JSON,
    ForeignKey,
    Enum as SQLEnum,
    TypeDecorator,
    CHAR,
    Boolean,
)
from sqlalchemy.dialects.mysql import CHAR as MYSQL_CHAR
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy.sql import func

from app.core.config import settings

Base = declarative_base()

# -------- GUID (UUID文字列を36桁で保存) --------
class GUID(TypeDecorator):
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(MYSQL_CHAR(36)) if dialect.name == "mysql" else dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        return None if value is None else str(value)

    def process_result_value(self, value, dialect):
        return None if value is None else uuid.UUID(str(value))

# -------- Enums --------
class LocationType(str, enum.Enum):
    simulation_golf = "simulation_golf"
    real_golf_course = "real_golf_course"

class ReservationStatus(str, enum.Enum):
    booked = "booked"
    completed = "completed"
    cancelled = "cancelled"

class PaymentStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"

# -------- Users --------
class User(Base):
    __tablename__ = "users"

    user_id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    usertype = Column(String(50), nullable=False, default="user")
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    gender = Column(String(10), nullable=True)
    line_user_id = Column(String(255), unique=True, nullable=True)

    profile_picture_url = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    birthday = Column(Date, nullable=True)
    golf_score_ave = Column(Integer, nullable=True)
    golf_exp = Column(Integer, nullable=True)

    zip_code = Column(String(10), nullable=True)
    state = Column(String(50), nullable=True)
    address1 = Column(String(255), nullable=True)
    address2 = Column(String(255), nullable=True)

    sport_exp = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    job_title = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)

# -------- Coaches --------
class Coach(Base):
    __tablename__ = "coaches"

    coach_id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    usertype = Column(String(50), nullable=False, default="coach")
    coachname = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    line_user_id = Column(String(255), unique=True, nullable=True)

    profile_picture_url = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    birthday = Column(Date, nullable=True)
    sex = Column(String(50), nullable=True)

    # SNS
    SNS_handle_instagram = Column(String(255), nullable=True)
    SNS_handle_X = Column(String(255), nullable=True)
    SNS_handle_youtube = Column(String(255), nullable=True)
    SNS_handle_facebook = Column(String(255), nullable=True)
    SNS_handle_tiktok = Column(String(255), nullable=True)

    # その他
    hourly_rate = Column(Integer, nullable=True)  # INT に統一
    location_id = Column(GUID(), nullable=True)
    golf_exp = Column(Integer, nullable=True)
    certification = Column(String(100), nullable=True)
    setting_1 = Column(String(50), nullable=True)
    setting_2 = Column(String(50), nullable=True)
    setting_3 = Column(String(50), nullable=True)
    lesson_rank = Column(String(50), nullable=True)

# -------- Location --------
class Location(Base):
    __tablename__ = "locations"

    location_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    location_name = Column(String(255), nullable=False)
    state = Column(String(50), nullable=False)
    address1 = Column(String(255), nullable=False)
    address2 = Column(String(255))
    zipcode = Column(String(10))
    phone_number = Column(String(50))
    website_url = Column(Text)
    opening_hours = Column(String(255))
    capacity = Column(Integer)
    description = Column(Text)
    image_url_main = Column(Text)
    image_url_sub1 = Column(Text)
    image_url_sub2 = Column(Text)
    image_url_sub3 = Column(Text)
    image_url_sub4 = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# -------- Videos --------
class Video(Base):
    __tablename__ = "videos"

    video_id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.user_id"), nullable=False)
    video_url = Column(Text, nullable=False)
    thumbnail_url = Column(Text, nullable=True)
    club_type = Column(String(50), nullable=True)
    swing_form = Column(String(50), nullable=True)
    swing_note = Column(Text, nullable=True)

    is_pinned = Column(Boolean, default=False)
    is_reviewed = Column(Boolean, default=False)

    section_group_id = Column(GUID(), nullable=True)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    section_groups = relationship("SectionGroup", back_populates="video")
    sessions = relationship("CoachingSession", back_populates="video")



# -------- Coaching Session (動画添削依頼) --------
class CoachingSession(Base):
    __tablename__ = "coaching_sessions"

    session_id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.user_id"), nullable=False)
    coach_id = Column(GUID(), ForeignKey("coaches.coach_id"), nullable=False)
    video_id = Column(GUID(), ForeignKey("videos.video_id"), nullable=False)

    status = Column(String(50), nullable=False, default="pending")  # pending / in_progress / completed
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # リレーション
    video = relationship("Video", back_populates="sessions")
    coach = relationship("Coach")
    user = relationship("User")
    section_groups = relationship("SectionGroup", back_populates="session")

# -------- Coaching Reservation --------
class CoachingReservation(Base):
    __tablename__ = "coaching_reservation"

    session_id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.user_id"), nullable=False)
    coach_id = Column(GUID(), ForeignKey("coaches.coach_id"), nullable=False)
    session_date = Column(DateTime(timezone=True), nullable=False)
    session_time = Column(DateTime(timezone=True), nullable=False)
    location_type = Column(SQLEnum(LocationType), nullable=False)
    location_id = Column(GUID(), nullable=False)
    status = Column(SQLEnum(ReservationStatus), default=ReservationStatus.booked)
    price = Column(DECIMAL(10, 2), nullable=False)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# -------- Section Groups --------
class SectionGroup(Base):
    __tablename__ = "section_groups"

    section_group_id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    video_id = Column(GUID(), ForeignKey("videos.video_id"), nullable=False)
    session_id = Column(GUID(), ForeignKey("coaching_sessions.session_id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 相手機能取り込み用（任意）
    overall_feedback = Column(Text, nullable=True)
    overall_feedback_summary = Column(Text, nullable=True)
    next_training_menu = Column(Text, nullable=True)
    next_training_menu_summary = Column(Text, nullable=True)
    feedback_created_at = Column(DateTime(timezone=True), nullable=True)

    video = relationship("Video", back_populates="section_groups")
    session = relationship("CoachingSession", back_populates="section_groups")
    sections = relationship("SwingSection", back_populates="section_group")

# -------- Swing Sections --------
class SwingSection(Base):
    __tablename__ = "swing_sections"

    section_id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    section_group_id = Column(GUID(), ForeignKey("section_groups.section_group_id"), nullable=False)
    start_sec = Column(DECIMAL(6, 2), nullable=False)
    end_sec = Column(DECIMAL(6, 2), nullable=False)
    image_url = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)
    markup_json = Column(JSON, nullable=True)
    coach_comment = Column(Text, nullable=True)
    coach_comment_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    section_group = relationship("SectionGroup", back_populates="sections")

# ---------- Async Engine / Session ----------
DATABASE_URL = settings.assemble_db_url()

pem = os.path.join(os.path.dirname(__file__), "DigiCertGlobalRootCA.crt.pem")
if os.path.exists(pem):
    ssl_ctx = ssl.create_default_context(cafile=pem)
else:
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE  # 証明書なしでTLS必須環境を満たす

engine = create_async_engine(
    DATABASE_URL,
    echo=(settings.env.lower() == "development"),
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,
    pool_pre_ping=True,
    connect_args={"ssl": ssl_ctx},
)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
