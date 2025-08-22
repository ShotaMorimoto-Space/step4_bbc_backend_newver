# app/api.py
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from .database import get_db
from . import schemas
from . import crud

router = APIRouter()

from sqlalchemy import text



# ===== Coach =====
# @router.post("/coaches", response_model=schemas.CoachRead)
# def create_coach(payload: schemas.CoachCreate, db: Session = Depends(get_db)):
#     return crud.create_coach(db, payload)

@router.get("/coaches", response_model=List[schemas.CoachRead])
def list_coaches(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    return crud.list_coaches(db, limit, offset)

@router.get("/coaches/{coach_id}", response_model=schemas.CoachReadWithLocation)
def get_coach(coach_id: str, db: Session = Depends(get_db)):
    obj = crud.get_coach(db, coach_id)
    if not obj:
        raise HTTPException(404, "coach not found")
    return obj

# @router.patch("/coaches/{coach_id}", response_model=schemas.CoachRead)
# def update_coach(coach_id: str, payload: schemas.CoachUpdate, db: Session = Depends(get_db)):
#     obj = crud.update_coach(db, coach_id, payload)
#     if not obj:
#         raise HTTPException(404, "coach not found")
#     return obj


# ===== Location =====
# @router.post("/locations", response_model=schemas.LocationRead)
# def create_location(payload: schemas.LocationCreate, db: Session = Depends(get_db)):
#     return crud.create_location(db, payload)

@router.get("/locations", response_model=List[schemas.LocationRead])
def list_locations(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    return crud.list_locations(db, limit, offset)

@router.get("/locations/{location_id}", response_model=schemas.LocationRead)
def get_location(location_id: str, db: Session = Depends(get_db)):
    obj = crud.get_location(db, location_id)
    if not obj:
        raise HTTPException(404, "location not found")
    return obj

# @router.patch("/locations/{location_id}", response_model=schemas.LocationRead)
# def update_location(location_id: str, payload: schemas.LocationUpdate, db: Session = Depends(get_db)):
#     obj = crud.update_location(db, location_id, payload)
#     if not obj:
#         raise HTTPException(404, "location not found")
#     return obj


# ===== User =====
# @router.post("/users", response_model=schemas.UserRead)
# def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
#     return crud.create_user(db, payload)

@router.get("/users", response_model=List[schemas.UserRead])
def list_users(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    return crud.list_users(db, limit, offset)

@router.get("/users/{user_id}", response_model=schemas.UserRead)
def get_user(user_id: str, db: Session = Depends(get_db)):
    obj = crud.get_user(db, user_id)
    if not obj:
        raise HTTPException(404, "user not found")
    return obj

# @router.patch("/users/{user_id}", response_model=schemas.UserRead)
# def update_user(user_id: str, payload: schemas.UserUpdate, db: Session = Depends(get_db)):
#     obj = crud.update_user(db, user_id, payload)
#     if not obj:
#         raise HTTPException(404, "user not found")
#     return obj


# ===== CoachLocation =====
# @router.post("/coach-locations", response_model=schemas.CoachLocationRead)
# def create_coach_location(payload: schemas.CoachLocationCreate, db: Session = Depends(get_db)):
#     obj = crud.create_coach_location(db, payload)
#     if not obj:
#         raise HTTPException(400, "invalid coach_id or location_id")
#     return obj

@router.get("/coach-locations", response_model=List[schemas.CoachLocationRead])
def list_coach_locations(limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    return crud.list_coach_locations(db, limit, offset)

@router.get("/coach-locations/{coach_id}/{location_id}", response_model=schemas.CoachLocationRead)
def get_coach_location(coach_id: str, location_id: str, db: Session = Depends(get_db)):
    obj = crud.get_coach_location(db, coach_id, location_id)
    if not obj:
        raise HTTPException(404, "coach_location not found")
    return obj


# ===== CoachingReservation =====
# @router.post("/reservations", response_model=schemas.CoachingReservationRead)
# def create_reservation(payload: schemas.CoachingReservationCreate, db: Session = Depends(get_db)):
#     obj = crud.create_reservation(db, payload)
#     if not obj:
#         raise HTTPException(400, "invalid foreign key(s)")
#     return obj

@router.get("/reservations", response_model=List[schemas.CoachingReservationRead])
def list_reservations(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    return crud.list_reservations(db, limit, offset)

@router.get("/reservations/{session_id}", response_model=schemas.CoachingReservationRead)
def get_reservation(session_id: str, db: Session = Depends(get_db)):
    obj = crud.get_reservation(db, session_id)
    if not obj:
        raise HTTPException(404, "reservation not found")
    return obj

# @router.patch("/reservations/{session_id}", response_model=schemas.CoachingReservationRead)
# def update_reservation(session_id: str, payload: schemas.CoachingReservationUpdate, db: Session = Depends(get_db)):
#     obj = crud.update_reservation(db, session_id, payload)
#     if not obj:
#         raise HTTPException(404, "reservation not found")
#     return obj
