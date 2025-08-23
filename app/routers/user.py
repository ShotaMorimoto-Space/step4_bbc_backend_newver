# app/routers/user.py
from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.deps import get_database, get_default_user_id
from app.schemas.video import VideoResponse
from app.schemas.reservation import (
    CoachingReservationResponse,
    CoachingReservationCreate,
    CoachingReservationUpdate,
)
from app.crud import video_crud, coaching_reservation_crud

router = APIRouter(tags=["users"])

@router.get("/my-videos", response_model=List[VideoResponse])
def get_my_videos(
    user_id: Optional[str] = Query(None, description="User ID (uses default if not provided)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_database),
):
    """
    Get all videos for a user
    """
    try:
        actual_user_id = user_id if user_id else get_default_user_id()
        videos = video_crud.get_videos_by_user(db, UUID(actual_user_id), skip, limit)
        return videos
    except ValueError:
        raise HTTPException(status_code=400, detail="無効なユーザーIDです")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"動画一覧の取得に失敗しました: {str(e)}")

@router.get("/my-reservations", response_model=List[CoachingReservationResponse])
def get_my_reservations(
    user_id: Optional[str] = Query(None, description="User ID (uses default if not provided)"),
    db: Session = Depends(get_database),
):
    """
    Get all coaching reservations for a user
    """
    try:
        actual_user_id = user_id if user_id else get_default_user_id()
        reservations = coaching_reservation_crud.get_reservations_by_user(db, UUID(actual_user_id))
        return reservations
    except ValueError:
        raise HTTPException(status_code=400, detail="無効なユーザーIDです")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予約一覧の取得に失敗しました: {str(e)}")

@router.post("/create-reservation", response_model=CoachingReservationResponse)
def create_coaching_reservation(
    reservation: CoachingReservationCreate,
    db: Session = Depends(get_database),
):
    """
    Create a new coaching reservation
    """
    try:
        db_reservation = coaching_reservation_crud.create_reservation(db, reservation)
        return db_reservation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予約の作成に失敗しました: {str(e)}")

@router.put("/reservation/{session_id}", response_model=CoachingReservationResponse)
def update_coaching_reservation(
    session_id: UUID,
    reservation_update: CoachingReservationUpdate,
    db: Session = Depends(get_database),
):
    """
    Update a coaching reservation
    """
    try:
        updated_reservation = coaching_reservation_crud.update_reservation(
            db, session_id, reservation_update
        )
        if not updated_reservation:
            raise HTTPException(status_code=404, detail="予約が見つかりません")
        return updated_reservation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予約の更新に失敗しました: {str(e)}")

@router.get("/reservation/{session_id}", response_model=CoachingReservationResponse)
def get_reservation_details(
    session_id: UUID,
    db: Session = Depends(get_database),
):
    """
    Get detailed information about a specific reservation
    """
    try:
        reservation = coaching_reservation_crud.get_reservation(db, session_id)
        if not reservation:
            raise HTTPException(status_code=404, detail="予約が見つかりません")
        return reservation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予約詳細の取得に失敗しました: {str(e)}")
