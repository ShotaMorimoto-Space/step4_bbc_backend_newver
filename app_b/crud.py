# app/crud.py
from __future__ import annotations
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
import uuid

from . import models, schemas

# ------- Coach（uses models.Coach）-------
def create_coach(db: Session, payload: schemas.CoachCreate) -> models.Coach:
    obj = models.Coach(coach_id=str(uuid.uuid4()), **payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def list_coaches(db: Session, limit: int, offset: int) -> List[models.Coach]:
    return (
        db.query(models.Coach)
        .order_by(models.Coach.created_at.desc())
        .limit(limit).offset(offset).all()
    )

def get_coach(db: Session, coach_id: str) -> Optional[models.Coach]:
    return (
        db.query(models.Coach)
        .options(joinedload(models.Coach.location))  # JOIN location
        .filter(models.Coach.coach_id == coach_id)
        .first()
    )

def update_coach(db: Session, coach_id: str, payload: schemas.CoachUpdate) -> Optional[models.Coach]:
    obj = db.query(models.Coach).filter(models.Coach.coach_id == coach_id).first()
    if not obj:
        return None
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


# ------- Location（uses models.Location）-------
def create_location(db: Session, payload: schemas.LocationCreate) -> models.Location:
    obj = models.Location(location_id=str(uuid.uuid4()), **payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def list_locations(db: Session, limit: int, offset: int) -> List[models.Location]:
    return (
        db.query(models.Location)
        .order_by(models.Location.location_name.asc())
        .limit(limit).offset(offset).all()
    )

def get_location(db: Session, location_id: str) -> Optional[models.Location]:
    return db.query(models.Location).filter(models.Location.location_id == location_id).first()

def update_location(db: Session, location_id: str, payload: schemas.LocationUpdate) -> Optional[models.Location]:
    obj = db.query(models.Location).filter(models.Location.location_id == location_id).first()
    if not obj:
        return None
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


# ------- User（uses models.User）-------
def create_user(db: Session, payload: schemas.UserCreate) -> models.User:
    obj = models.User(user_id=str(uuid.uuid4()), **payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def list_users(db: Session, limit: int, offset: int) -> List[models.User]:
    return (
        db.query(models.User)
        .order_by(models.User.created_at.desc())
        .limit(limit).offset(offset).all()
    )

def get_user(db: Session, user_id: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def update_user(db: Session, user_id: str, payload: schemas.UserUpdate) -> Optional[models.User]:
    obj = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not obj:
        return None
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


# ------- CoachLocation（uses models.CoachLocation, models.Coach, models.Location）-------
def create_coach_location(db: Session, payload: schemas.CoachLocationCreate) -> Optional[models.CoachLocation]:
    # FK存在チェック
    if not db.query(models.Coach).filter(models.Coach.coach_id == payload.coach_id).first():
        return None
    if not db.query(models.Location).filter(models.Location.location_id == payload.location_id).first():
        return None

    obj = models.CoachLocation(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def list_coach_locations(db: Session, limit: int, offset: int) -> List[models.CoachLocation]:
    return (
        db.query(models.CoachLocation)
        .order_by(models.CoachLocation.coach_id.asc())
        .limit(limit).offset(offset).all()
    )

def get_coach_location(db: Session, coach_id: str, location_id: str) -> Optional[models.CoachLocation]:
    return (
        db.query(models.CoachLocation)
        .filter(
            models.CoachLocation.coach_id == coach_id,
            models.CoachLocation.location_id == location_id,
        )
        .first()
    )


# ------- CoachingReservation（uses models.CoachingReservation, models.User, models.Coach, models.Location）-------
def create_reservation(db: Session, payload: schemas.CoachingReservationCreate) -> Optional[models.CoachingReservation]:
    # FK存在チェック
    if not db.query(models.User).filter(models.User.user_id == payload.user_id).first():
        return None
    if not db.query(models.Coach).filter(models.Coach.coach_id == payload.coach_id).first():
        return None
    if payload.location_id:
        if not db.query(models.Location).filter(models.Location.location_id == payload.location_id).first():
            return None

    obj = models.CoachingReservation(session_id=str(uuid.uuid4()), **payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def list_reservations(db: Session, limit: int, offset: int) -> List[models.CoachingReservation]:
    return (
        db.query(models.CoachingReservation)
        .order_by(
            models.CoachingReservation.session_date.desc(),
            models.CoachingReservation.session_time.desc(),
        )
        .limit(limit).offset(offset).all()
    )

def get_reservation(db: Session, session_id: str) -> Optional[models.CoachingReservation]:
    return (
        db.query(models.CoachingReservation)
        .filter(models.CoachingReservation.session_id == session_id)
        .first()
    )

def update_reservation(db: Session, session_id: str, payload: schemas.CoachingReservationUpdate) -> Optional[models.CoachingReservation]:
    obj = (
        db.query(models.CoachingReservation)
        .filter(models.CoachingReservation.session_id == session_id)
        .first()
    )
    if not obj:
        return None
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj
