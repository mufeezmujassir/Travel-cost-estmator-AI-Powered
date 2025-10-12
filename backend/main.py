from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
import uvicorn
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
import logging
import re
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from agents.travel_orchestrator import TravelOrchestrator
from models.travel_models import TravelRequest, TravelResponse
from services.config import Settings

# Load environment variables
load_dotenv()

# Initialize settings
settings = Settings()

# Global orchestrator instance
orchestrator = None

# User Management Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# MongoDB Configuration (using your existing connection)
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "travel_agent_db")

# Import MongoDB dependencies
users_collection = None
try:
    from pymongo import MongoClient
    from bson import ObjectId
    
    # MongoDB connection
    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    users_collection = db["users"]
    
    # Create unique index for email
    users_collection.create_index("email", unique=True)
    print("✅ MongoDB user collection initialized successfully")
    
except ImportError:
    print("⚠️  PyMongo not installed. User management features will be disabled.")
except Exception as e:
    print(f"⚠️  MongoDB connection failed: {e}")
    users_collection = None

# Pydantic models for user management
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# User management utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    if users_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User management service not available"
        )
    
    user = users_collection.find_one({"email": email})
    if user is None:
        raise credentials_exception
    
    return UserResponse(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        created_at=user["created_at"]
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global orchestrator
    # Startup
    print("🚀 Starting Travel Cost Estimator API...")
    orchestrator = TravelOrchestrator(settings)
    await orchestrator.initialize()
    print("✅ All agents initialized successfully!")
    
    # Initialize subscription services
    print("💳 Initializing subscription system...")
    try:
        from services.subscription_service import SubscriptionService
        from services.region_resolver import RegionResolver
        import routes.subscription_routes
        import routes.payment_routes
        
        # Initialize RegionResolver for SubscriptionService
        region_resolver = RegionResolver(settings.serp_api_key)
        subscription_svc = SubscriptionService(region_resolver)
        
        # Set global service instances using module-level assignment
        routes.subscription_routes.subscription_service = subscription_svc
        routes.payment_routes.subscription_service = subscription_svc
        print("✅ Subscription service initialized")
        
        # Initialize Stripe service if keys are available
        if settings.stripe_secret_key:
            from services.stripe_service import StripeService
            stripe_svc = StripeService(
                secret_key=settings.stripe_secret_key,
                webhook_secret=settings.stripe_webhook_secret,
                mode=settings.stripe_mode
            )
            routes.payment_routes.stripe_service = stripe_svc
            print("✅ Stripe service initialized")
        else:
            print("⚠️  Stripe keys not configured - payments disabled")
            
    except Exception as e:
        print(f"⚠️  Failed to initialize subscription services: {e}")
        import traceback
        traceback.print_exc()
    
    # Check MongoDB connection for user management
    if users_collection is not None:
        try:
            # Test MongoDB connection
            client.admin.command('ping')
            print("✅ MongoDB connected successfully for user management")
        except Exception as e:
            print(f"⚠️  MongoDB connection failed: {e}")
    else:
        print("⚠️  User management disabled - MongoDB not available")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Travel Cost Estimator API...")

# Create FastAPI app
app = FastAPI(
    title="Travel Cost Estimator API",
    description="AI-Powered Multi-Agent Travel Planning System with User Management",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create logger
logger = logging.getLogger("travel_api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Import and include subscription and payment routes
from routes.subscription_routes import router as subscription_router
from routes.payment_routes import router as payment_router

# Include routers
app.include_router(subscription_router)
app.include_router(payment_router)

# User Management Endpoints
@app.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate):
    """User registration endpoint"""
    if users_collection is None:
        raise HTTPException(status_code=503, detail="User management service not available")
    
    # Check if user already exists
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(user.password)
    
    # Create user document
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    user_dict["created_at"] = datetime.utcnow()
    
    # Insert user
    try:
        result = users_collection.insert_one(user_dict)
        
        # Return user without password
        created_user = users_collection.find_one({"_id": result.inserted_id})
        return UserResponse(
            id=str(created_user["_id"]),
            name=created_user["name"],
            email=created_user["email"],
            created_at=created_user["created_at"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

@app.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    """User login endpoint"""
    if users_collection is None:
        raise HTTPException(status_code=503, detail="User management service not available")
    
    user = users_collection.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/profile", response_model=UserResponse)
async def get_profile(current_user: UserResponse = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@app.put("/auth/profile", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update user profile"""
    if users_collection is None:
        raise HTTPException(status_code=503, detail="User management service not available")
    
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
            "_id": {"$ne": ObjectId(current_user.id)}
        })
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    users_collection.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": update_dict}
    )
    
    # Return updated user
    updated_user = users_collection.find_one({"_id": ObjectId(current_user.id)})
    return UserResponse(
        id=str(updated_user["_id"]),
        name=updated_user["name"],
        email=updated_user["email"],
        created_at=updated_user["created_at"]
    )

@app.delete("/auth/profile")
async def delete_profile(current_user: UserResponse = Depends(get_current_user)):
    """Delete user account"""
    if users_collection is None:
        raise HTTPException(status_code=503, detail="User management service not available")
    
    result = users_collection.delete_one({"_id": ObjectId(current_user.id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": "User deleted successfully"}

@app.get("/auth/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: str):
    """Get user by ID (public endpoint)"""
    if users_collection is None:
        raise HTTPException(status_code=503, detail="User management service not available")
    
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=str(user["_id"]),
            name=user["name"],
            email=user["email"],
            created_at=user["created_at"]
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

# Existing Travel Endpoints (Protected)
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Travel Cost Estimator API with User Management",
        "version": "1.0.0",
        "status": "active",
        "features": [
            "User Authentication & Management",
            "Emotional Intelligence Agent",
            "Flight Search Agent", 
            "Hotel Search Agent",
            "Transportation Agent",
            "Cost Estimation Agent",
            "Recommendation Agent"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "agents_ready": orchestrator is not None,
        "user_management_ready": users_collection is not None
    }

@app.post("/api/estimate-travel", response_model=TravelResponse)
async def estimate_travel(
    request: TravelRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Main endpoint for travel cost estimation (Protected)
    Orchestrates all agents to provide comprehensive travel planning
    """
    try:
        logger.info(f"Received travel request from user: {current_user.email}")
        logger.info("Received request body: %s", request.dict())
        
        if not orchestrator:
            raise HTTPException(status_code=503, detail="Service not ready")
        
        logger.info("🎯 Processing travel request: %s → %s", request.origin, request.destination)
        logger.info("📅 Dates: %s to %s", request.start_date, request.return_date)
        logger.info("👥 Travelers: %s", request.travelers)
        logger.info("💭 Vibe: %s", request.vibe)        
        # Process the travel request through all agents
        result = await orchestrator.process_travel_request(request)
        
        # Track trip generation for subscription usage
        try:
            from middleware.subscription_middleware import get_subscription_middleware
            from services.subscription_service import SubscriptionService
            from services.region_resolver import RegionResolver
            
            # Get subscription service instance
            region_resolver = RegionResolver(settings.serp_api_key)
            subscription_service = SubscriptionService(region_resolver)
            subscription_middleware = await get_subscription_middleware(subscription_service)
            
            # Track the trip generation
            await subscription_middleware.track_trip_generation(current_user, request.destination)
            logger.info(f"✅ Tracked trip generation for user {current_user.id} to {request.destination}")
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to track trip generation: {e}")
        
        logger.info("✅ Travel estimation completed successfully for user: %s", current_user.email)
        return result
        
    except Exception as e:
        logger.exception("❌ Error processing travel request")
        raise HTTPException(status_code=500, detail=f"Failed to process travel request: {str(e)}")

@app.get("/api/vibes")
async def get_available_vibes(current_user: UserResponse = Depends(get_current_user)):
    """Get available travel vibes and their characteristics (Protected)"""
    return {
        "vibes": [
            {
                "id": "romantic",
                "name": "Romantic",
                "description": "Perfect for couples seeking intimate moments",
                "season": "spring",
                "activities": ["Sunset dinners", "Couples spa", "Romantic walks", "Wine tasting"],
                "optimal_months": [3, 4, 5, 9, 10]
            },
            {
                "id": "adventure",
                "name": "Adventure", 
                "description": "Thrilling experiences for adrenaline seekers",
                "season": "summer",
                "activities": ["Hiking", "Rock climbing", "Water sports", "Extreme sports"],
                "optimal_months": [6, 7, 8, 9]
            },
            {
                "id": "beach",
                "name": "Beach Vibes",
                "description": "Relaxing coastal experiences",
                "season": "summer", 
                "activities": ["Beach relaxation", "Water activities", "Seafood dining", "Sunset views"],
                "optimal_months": [5, 6, 7, 8, 9]
            },
            {
                "id": "nature",
                "name": "Nature & Forest",
                "description": "Connect with natural beauty and wildlife",
                "season": "spring",
                "activities": ["Forest hiking", "Wildlife watching", "Nature photography", "Camping"],
                "optimal_months": [3, 4, 5, 10, 11]
            },
            {
                "id": "cultural",
                "name": "Cultural",
                "description": "Explore history, art, and local traditions",
                "season": "autumn",
                "activities": ["Museum visits", "Historical sites", "Local festivals", "Art galleries"],
                "optimal_months": [9, 10, 11, 3, 4]
            },
            {
                "id": "culinary",
                "name": "Culinary",
                "description": "Food-focused experiences and local cuisine",
                "season": "autumn",
                "activities": ["Food tours", "Cooking classes", "Local markets", "Fine dining"],
                "optimal_months": [9, 10, 11, 4, 5]
            },
            {
                "id": "wellness",
                "name": "Wellness",
                "description": "Rejuvenating and healing experiences",
                "season": "winter",
                "activities": ["Spa treatments", "Yoga sessions", "Meditation", "Healthy dining"],
                "optimal_months": [12, 1, 2, 3]
            }
        ]
    }

@app.get("/api/season-recommendation")
async def get_season_recommendation(
    vibe: str, 
    destination: str, 
    start_date: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get season-based recommendations for a specific vibe and destination (Protected)"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=503, detail="Service not ready")
        
        recommendation = await orchestrator.get_season_recommendation(vibe, destination, start_date)
        return recommendation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get season recommendation: {str(e)}")

# Public endpoints (no authentication required)
@app.get("/public/vibes")
async def get_public_vibes():
    """Public endpoint to get available vibes without authentication"""
    return {
        "vibes": [
            {
                "id": "romantic",
                "name": "Romantic",
                "description": "Perfect for couples seeking intimate moments"
            },
            {
                "id": "adventure",
                "name": "Adventure", 
                "description": "Thrilling experiences for adrenaline seekers"
            },
            {
                "id": "beach",
                "name": "Beach Vibes",
                "description": "Relaxing coastal experiences"
            },
            {
                "id": "nature",
                "name": "Nature & Forest",
                "description": "Connect with natural beauty and wildlife"
            },
            {
                "id": "cultural",
                "name": "Cultural",
                "description": "Explore history, art, and local traditions"
            },
            {
                "id": "culinary",
                "name": "Culinary",
                "description": "Food-focused experiences and local cuisine"
            },
            {
                "id": "wellness",
                "name": "Wellness",
                "description": "Rejuvenating and healing experiences"
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )