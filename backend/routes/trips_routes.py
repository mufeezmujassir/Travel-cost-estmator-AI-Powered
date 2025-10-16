from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from datetime import datetime

from models.travel_history import travel_plans_collection
from services.auth_service import get_current_user
from schemas.user_schema import UserResponse

router = APIRouter(prefix="/api/trips", tags=["trips"])


def _serialize(doc):
    if not doc:
        return None
    doc["id"] = str(doc.pop("_id"))
    # Ensure ISO strings
    if isinstance(doc.get("generated_at"), datetime):
        doc["generated_at"] = doc["generated_at"].isoformat()
    return doc


@router.get("/")
async def list_trips(current_user: UserResponse = Depends(get_current_user)):
    cursor = travel_plans_collection.find({"userId": current_user.id}).sort("generated_at", -1)
    return [_serialize(d) for d in cursor]


@router.get("/{trip_id}")
async def get_trip(trip_id: str, current_user: UserResponse = Depends(get_current_user)):
    try:
        doc = travel_plans_collection.find_one({"_id": ObjectId(trip_id), "userId": current_user.id})
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return _serialize(doc)


@router.delete("/{trip_id}")
async def delete_trip(trip_id: str, current_user: UserResponse = Depends(get_current_user)):
    try:
        result = travel_plans_collection.delete_one({"_id": ObjectId(trip_id), "userId": current_user.id})
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return {"success": True}


