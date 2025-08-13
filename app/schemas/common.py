# app/schemas/common.py
from enum import Enum

class LocationType(str, Enum):
    simulation_golf = "simulation_golf"
    real_golf_course = "real_golf_course"

class ReservationStatus(str, Enum):
    booked = "booked"
    completed = "completed"
    cancelled = "cancelled"

class PaymentStatus(str, Enum):
    pending = "pending"
    paid = "paid"

class SwingSectionTag(str, Enum):
    address = "address"
    takeaway = "takeaway"
    halfway_back = "halfway_back"
    backswing = "backswing"
    top = "top"
    transition = "transition"
    downswing = "downswing"
    impact = "impact"
    follow_through = "follow_through"
    finish_1 = "finish_1"
    finish_2 = "finish_2"
    other = "other"
