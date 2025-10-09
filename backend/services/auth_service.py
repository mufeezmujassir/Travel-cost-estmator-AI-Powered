from models.user import users_collection
from utils.security import verify_password, get_password_hash, verify_token
from schemas.user_schema import UserResponse
from bson import ObjectId
from fastapi import HTTPException, status

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
        
        # Insert user
        result = users_collection.insert_one(user_dict)
        
        # Return user without password
        user = users_collection.find_one({"_id": result.inserted_id})
        return UserResponse(
            id=str(user["_id"]),
            name=user["name"],
            email=user["email"],
            created_at=user["created_at"]
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
            created_at=user["created_at"]
        )
    
    @staticmethod
    async def get_user_by_id(user_id: str):
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return None
        
        return UserResponse(
            id=str(user["_id"]),
            name=user["name"],
            email=user["email"],
            created_at=user["created_at"]
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
            existing_user = users_collection.find_one({
                "email": update_data.email,
                "_id": {"$ne": ObjectId(user_id)}
            })
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_dict}
        )
        
        return await AuthService.get_user_by_id(user_id)
    
    @staticmethod
    async def delete_user(user_id: str):
        result = users_collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"message": "User deleted successfully"}

# Dependency to get current user
async def get_current_user(token: str):
    email = verify_token(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = users_collection.find_one({"email": email})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        created_at=user["created_at"]
    )