# app/schemas/__init__.py

# --- Enums ---
from .common import (
    LocationType, ReservationStatus, PaymentStatus, SwingSectionTag
)

# --- Sections / Feedback ---
from .section import (
    MarkupObject,
    SectionGroupBase, SectionGroupCreate, SectionGroupResponse,
    SwingSectionBase, SwingSectionCreate, SwingSectionUpdate, SwingSectionResponse,
    CoachCommentRequest, CoachCommentResponse,
    OverallFeedbackRequest, OverallFeedbackResponse,
)

# --- Video ---
from .video import (
    VideoBase, VideoCreate, VideoUpdate, VideoResponse, VideoUploadRequest,
    VideoWithSectionsResponse,
)

# --- Reservation ---
from .reservation import (
    CoachingReservationBase, CoachingReservationCreate,
    CoachingReservationUpdate, CoachingReservationResponse,
)

# --- User ---
from .user import UserCreate, UserResponse, UserMini

# --- Coach ---
from .coach import CoachCreate, CoachResponse, CoachOut


__all__ = [
    # Enums
    "LocationType", "ReservationStatus", "PaymentStatus", "SwingSectionTag",
    # Section / Feedback
    "MarkupObject",
    "SectionGroupBase", "SectionGroupCreate", "SectionGroupResponse",
    "SwingSectionBase", "SwingSectionCreate", "SwingSectionUpdate", "SwingSectionResponse",
    "CoachCommentRequest", "CoachCommentResponse",
    "OverallFeedbackRequest", "OverallFeedbackResponse",
    # Video
    "VideoBase", "VideoCreate", "VideoUpdate", "VideoResponse", "VideoUploadRequest",
    "VideoWithSectionsResponse",
    # Reservation
    "CoachingReservationBase", "CoachingReservationCreate",
    "CoachingReservationUpdate", "CoachingReservationResponse",
    # User
    "UserCreate", "UserResponse", "UserMini",
    # Coach
    "CoachCreate", "CoachResponse", "CoachOut",
]
