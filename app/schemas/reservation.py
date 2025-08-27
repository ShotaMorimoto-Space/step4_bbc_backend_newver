# app/schemas/reservation.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from .common import LocationType, ReservationStatus, PaymentStatus


class CoachingReservationBase(BaseModel):
    user_id: UUID
    coach_id: UUID
    session_date: datetime
    session_time: datetime
    location_type: LocationType
    location_id: UUID
    price: Decimal

class CoachingReservationCreate(CoachingReservationBase):
    pass

class CoachingReservationUpdate(BaseModel):
    session_date: Optional[datetime] = None
    session_time: Optional[datetime] = None
    location_type: Optional[LocationType] = None
    location_id: Optional[UUID] = None
    status: Optional[ReservationStatus] = None
    price: Optional[Decimal] = None
    payment_status: Optional[PaymentStatus] = None

class CoachingReservationResponse(CoachingReservationBase):
    session_id: str  # UUIDからstr型に変更
    status: ReservationStatus
    payment_status: PaymentStatus

    model_config = {"from_attributes": True}
