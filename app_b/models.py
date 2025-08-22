# app/models.py
from sqlalchemy import (
    Column, String, Integer, Date, Time, DateTime, Numeric, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

# =========================
# Location
# =========================
class Location(Base):
    __tablename__ = "location"

    location_id = Column(String(36), primary_key=True, index=True)
    location_name = Column(String(255))
    state = Column(String(50))
    address1 = Column(String(255))
    address2 = Column(String(255))
    zipcode = Column(String(10))
    phone_number = Column(String(50))
    website_url = Column(String(2048))
    opening_hours = Column(String(255))
    capacity = Column(Integer)
    description = Column(String(2048))
    image_url_main = Column(String(2048))
    image_url_sub1 = Column(String(2048))
    image_url_sub2 = Column(String(2048))
    image_url_sub3 = Column(String(2048))
    image_url_sub4 = Column(String(2048))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relations
    coaches = relationship("Coach", back_populates="location")
    coach_locations = relationship(
        "CoachLocation", back_populates="location", cascade="all, delete-orphan"
    )
    reservations = relationship("CoachingReservation", back_populates="location")

    def __repr__(self) -> str:
        return f"<Location {self.location_id} {self.location_name}>"


# =========================
# Coach
# =========================
class Coach(Base):
    __tablename__ = "coach"

    coach_id = Column(String(36), primary_key=True, index=True)
    usertype = Column(String(50))
    coachname = Column(String(255))
    email = Column(String(255))
    birthday = Column(String(50))
    Sex = Column(String(50))  # 既存カラム名を尊重

    SNS_handle_instagram = Column(String(255))
    SNS_handle_X = Column(String(255))
    SNS_handle_youtube = Column(String(255))
    SNS_handle_facebook = Column(String(255))
    SNS_handle_tiktok = Column(String(255))

    password_hash = Column(String(255))
    line_user_id = Column(String(255))
    profile_picture_url = Column(String(2048))
    bio = Column(String(2048))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    hourly_rate = Column(Numeric(10, 2))
    location_id = Column(String(36), ForeignKey("location.location_id"))
    golf_exp = Column(Integer)
    certification = Column(String(100))
    setting_1 = Column(String(50))
    setting_2 = Column(String(50))
    setting_3 = Column(String(50))
    Lesson_rank = Column(String(50))  # 既存名を尊重

    # relations
    location = relationship("Location", back_populates="coaches")
    coach_locations = relationship(
        "CoachLocation", back_populates="coach", cascade="all, delete-orphan"
    )
    reservations = relationship("CoachingReservation", back_populates="coach")

    def __repr__(self) -> str:
        return f"<Coach {self.coach_id} {self.coachname}>"


# =========================
# User  （テーブル名は users）
# =========================
class User(Base):
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, index=True)
    usertype = Column(String(50))
    username = Column(String(255))
    email = Column(String(255))
    password_hash = Column(String(255))
    line_user_id = Column(String(255))
    profile_picture_url = Column(String(2048))
    bio = Column(String(2048))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    birthday = Column(Date)
    golf_score_ave = Column(Integer)
    golf_exp = Column(Integer)
    zip_code = Column(String(10))
    state = Column(String(50))
    address1 = Column(String(255))
    address2 = Column(String(255))
    sport_exp = Column(String(100))
    industry = Column(String(100))
    job_title = Column(String(100))
    Position = Column(String(100))  # 既存の大文字小文字を保持

    # relations
    reservations = relationship("CoachingReservation", back_populates="user")

    def __repr__(self) -> str:
        return f"<User {self.user_id} {self.username}>"


# =========================
# CoachLocation (association object)
# =========================
class CoachLocation(Base):
    __tablename__ = "coach_location"

    coach_id = Column(String(36), ForeignKey("coach.coach_id"), primary_key=True)
    location_id = Column(String(36), ForeignKey("location.location_id"), primary_key=True)
    notes = Column(String(2048))

    # relations
    coach = relationship("Coach", back_populates="coach_locations")
    location = relationship("Location", back_populates="coach_locations")

    def __repr__(self) -> str:
        return f"<CoachLocation coach={self.coach_id} location={self.location_id}>"


# =========================
# CoachingReservation
# =========================
class CoachingReservation(Base):
    __tablename__ = "coaching_reservation"

    session_id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"))
    coach_id = Column(String(36), ForeignKey("coach.coach_id"))
    session_date = Column(Date)
    session_time = Column(Time)
    location_type = Column(String(50))
    location_id = Column(String(36), ForeignKey("location.location_id"))
    status = Column(String(50))
    price = Column(Numeric(10, 2))
    payment_status = Column(String(50))

    # relations
    user = relationship("User", back_populates="reservations")
    coach = relationship("Coach", back_populates="reservations")
    location = relationship("Location", back_populates="reservations")

    def __repr__(self) -> str:
        return f"<CoachingReservation {self.session_id} user={self.user_id} coach={self.coach_id}>"
