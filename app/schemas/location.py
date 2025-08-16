from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class LocationBase(BaseModel):
    location_name: str
    state: str
    address1: str
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
    pass

class LocationUpdate(LocationBase):
    pass

class LocationResponse(LocationBase):
    location_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
