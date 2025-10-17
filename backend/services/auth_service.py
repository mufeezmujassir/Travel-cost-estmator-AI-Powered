from models.user import users_collection
from utils.security import verify_password, get_password_hash, create_access_token, verify_token
from schemas.user_schema import UserResponse
from bson import ObjectId
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
import os
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
# Optional scheme that does not raise when token is missing
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

class AuthService:
    
    @staticmethod
    async def register_user(user_data):
        # Check if user already exists
        if users_collection.find_one({"email": user_data.email}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user document
        user_dict = user_data.dict()
        user_dict["password"] = hashed_password
        user_dict["created_at"] = datetime.utcnow()
        user_dict["type"] = "basic"
        user_dict["hasUsedFreePlan"] = False
        user_dict["subscriptionStatus"] = "expired"
        user_dict["subscriptionEndDate"] = None
        user_dict["stripeCustomerId"] = None
        user_dict["subscriptionId"] = None
        user_dict["generationsRemaining"] = 1  # One free generation
        
        # Insert user
        result = users_collection.insert_one(user_dict)
        
        # Return user without password
        user = users_collection.find_one({"_id": result.inserted_id})
        return UserResponse(
            id=str(user["_id"]),
            name=user["name"],
            email=user["email"],
            created_at=user["created_at"],
            type=user.get("type", "basic"),
            hasUsedFreePlan=user.get("hasUsedFreePlan", False),
            subscriptionStatus=user.get("subscriptionStatus", "expired"),
            subscriptionEndDate=user.get("subscriptionEndDate"),
            stripeCustomerId=user.get("stripeCustomerId"),
            subscriptionId=user.get("subscriptionId"),
            generationsRemaining=user.get("generationsRemaining", 1)
        )
    
    @staticmethod
    async def authenticate_user(email: str, password: str):
        user = users_collection.find_one({"email": email})
        if not user:
            return None
        if not verify_password(password, user["password"]):
            return None
        
        return UserResponse(
            id=str(user["_id"]),
            name=user["name"],
            email=user["email"],
            created_at=user["created_at"],
            type=user.get("type", "basic"),
            hasUsedFreePlan=user.get("hasUsedFreePlan", False),
            subscriptionStatus=user.get("subscriptionStatus", "expired"),
            subscriptionEndDate=user.get("subscriptionEndDate"),
            stripeCustomerId=user.get("stripeCustomerId"),
            subscriptionId=user.get("subscriptionId"),
            generationsRemaining=user.get("generationsRemaining", 1)
        )
    
    @staticmethod
    async def get_user_by_id(user_id: str):
        try:
            user = users_collection.find_one({"_id": ObjectId(user_id)})
        except:
            return None
            
        if not user:
            return None
        
        return UserResponse(
            id=str(user["_id"]),
            name=user["name"],
            email=user["email"],
            created_at=user["created_at"],
            type=user.get("type", "basic"),
            hasUsedFreePlan=user.get("hasUsedFreePlan", False),
            subscriptionStatus=user.get("subscriptionStatus", "expired"),
            subscriptionEndDate=user.get("subscriptionEndDate"),
            stripeCustomerId=user.get("stripeCustomerId"),
            subscriptionId=user.get("subscriptionId"),
            generationsRemaining=user.get("generationsRemaining", 1)
        )
    
    @staticmethod
    async def update_user(user_id: str, update_data):
        # Remove None values
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        
        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No data to update"
            )
        
        # Check if email already exists
        if update_data.email:
            try:
                existing_user = users_collection.find_one({
                    "email": update_data.email,
                    "_id": {"$ne": ObjectId(user_id)}
                })
            except:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user ID"
                )
                
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        try:
            users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_dict}
            )
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID"
            )
        
        return await AuthService.get_user_by_id(user_id)
    
    @staticmethod
    async def delete_user(user_id: str):
        try:
            result = users_collection.delete_one({"_id": ObjectId(user_id)})
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID"
            )
            
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"message": "User deleted successfully"}
    
    @staticmethod
    async def check_generation_limit(user_id: str) -> bool:
        """Check if user can generate a travel plan"""
        try:
            user = users_collection.find_one({"_id": ObjectId(user_id)})
        except:
            return False
            
        if not user:
            return False
        
        user_type = user.get("type", "basic")
        
        # Premium users with active subscription
        if user_type == "premium":
            subscription_status = user.get("subscriptionStatus", "expired")
            if subscription_status == "active":
                subscription_end = user.get("subscriptionEndDate")
                if subscription_end and subscription_end > datetime.utcnow():
                    return True
                else:
                    # Subscription expired, downgrade to basic
                    users_collection.update_one(
                        {"_id": ObjectId(user_id)},
                        {"$set": {
                            "type": "basic",
                            "subscriptionStatus": "expired",
                            "generationsRemaining": 0
                        }}
                    )
                    return False
        
        # Basic users
        generations_remaining = user.get("generationsRemaining", 0)
        return generations_remaining > 0
    
    @staticmethod
    async def use_generation(user_id: str):
        """Use one generation for basic users"""
        try:
            user = users_collection.find_one({"_id": ObjectId(user_id)})
        except:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_type = user.get("type", "basic")
        
        # Premium users don't need to decrement
        if user_type == "premium":
            subscription_status = user.get("subscriptionStatus", "expired")
            if subscription_status == "active":
                return
        
        # Basic users - decrement and mark as used
        generations_remaining = user.get("generationsRemaining", 0)
        if generations_remaining > 0:
            users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "generationsRemaining": 0,
                    "hasUsedFreePlan": True
                }}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No generations remaining. Please upgrade to premium."
            )

# Dependency to get current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    email = verify_token(token)
    if email is None:
        raise credentials_exception
    
    user = users_collection.find_one({"email": email})
    if user is None:
        raise credentials_exception
    
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        created_at=user["created_at"],
        type=user.get("type", "basic"),
        hasUsedFreePlan=user.get("hasUsedFreePlan", False),
        subscriptionStatus=user.get("subscriptionStatus", "expired"),
        subscriptionEndDate=user.get("subscriptionEndDate"),
        stripeCustomerId=user.get("stripeCustomerId"),
        subscriptionId=user.get("subscriptionId"),
        generationsRemaining=user.get("generationsRemaining", 1)
    )

# Optional current user that returns None when no/invalid token is provided

async def get_optional_current_user(token: Optional[str] = Depends(optional_oauth2_scheme)):
    if not token:
        return None
    try:
        email = verify_token(token)
        if email is None:
            return None
        user = users_collection.find_one({"email": email})
        if user is None:
            return None
        return UserResponse(
            id=str(user["_id"]),
            name=user["name"],
            email=user["email"],
            created_at=user["created_at"],
            type=user.get("type", "basic"),
            hasUsedFreePlan=user.get("hasUsedFreePlan", False),
            subscriptionStatus=user.get("subscriptionStatus", "expired"),
            subscriptionEndDate=user.get("subscriptionEndDate"),
            stripeCustomerId=user.get("stripeCustomerId"),
            subscriptionId=user.get("subscriptionId"),
            generationsRemaining=user.get("generationsRemaining", 1)
        )
    except Exception:
        return None