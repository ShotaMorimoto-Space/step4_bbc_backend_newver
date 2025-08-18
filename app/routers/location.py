from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from app import models
from app.deps import get_database
from app.schemas.location import LocationResponse, LocationCreate, LocationUpdate

router = APIRouter(prefix="/locations", tags=["locations"])

@router.get("/", response_model=List[LocationResponse])
async def list_locations(db: AsyncSession = Depends(get_database)):
    from sqlalchemy import select
    result = await db.execute(select(models.Location))
    return result.scalars().all()

@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(location_id: UUID, db: AsyncSession = Depends(get_database)):
    location = await db.get(models.Location, str(location_id))
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

@router.post("/", response_model=LocationResponse)
async def create_location(location: LocationCreate, db: AsyncSession = Depends(get_database)):
    new_location = models.Location(**location.dict())
    db.add(new_location)
    await db.commit()
    await db.refresh(new_location)
    return new_location

@router.put("/{location_id}", response_model=LocationResponse)
async def update_location(location_id: UUID, location: LocationUpdate, db: AsyncSession = Depends(get_database)):
    db_location = await db.get(models.Location, str(location_id))
    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")
    for key, value in location.dict(exclude_unset=True).items():
        setattr(db_location, key, value)
    await db.commit()
    await db.refresh(db_location)
    return db_location
