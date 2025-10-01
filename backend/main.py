from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
import logging
import re

from agents.travel_orchestrator import TravelOrchestrator
from models.travel_models import TravelRequest, TravelResponse
from services.config import Settings

# Load environment variables
load_dotenv()

# Initialize settings
settings = Settings()

# Global orchestrator instance
orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global orchestrator
    # Startup
    print("🚀 Starting Travel Cost Estimator API...")
    orchestrator = TravelOrchestrator(settings)
    await orchestrator.initialize()
    print("✅ All agents initialized successfully!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Travel Cost Estimator API...")

# Create FastAPI app
app = FastAPI(
    title="Travel Cost Estimator API",
    description="AI-Powered Multi-Agent Travel Planning System",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000","http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create logger
logger = logging.getLogger("travel_api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Travel Cost Estimator API",
        "version": "1.0.0",
        "status": "active",
        "agents": [
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
    return {"status": "healthy", "agents_ready": orchestrator is not None}

@app.post("/api/estimate-travel", response_model=TravelResponse)
async def estimate_travel(request: TravelRequest):
    """
    Main endpoint for travel cost estimation
    Orchestrates all agents to provide comprehensive travel planning
    """
    try:
        logger.info("Received request body: %s", request.dict())
        logger.info("Received /api/estimate-travel request: %s", request.dict())
        if not orchestrator:
            raise HTTPException(status_code=503, detail="Service not ready")
        
        logger.info("🎯 Processing travel request: %s → %s", request.origin, request.destination)
        logger.info("📅 Dates: %s to %s", request.start_date, request.return_date)
        logger.info("👥 Travelers: %s", request.travelers)
        logger.info("💭 Vibe: %s", request.vibe)        
        # Process the travel request through all agents
        result = await orchestrator.process_travel_request(request)
        
        logger.info("✅ Travel estimation completed successfully")
        return result
        
    except Exception as e:
        logger.exception("❌ Error processing travel request")
        raise HTTPException(status_code=500, detail=f"Failed to process travel request: {str(e)}")

@app.get("/api/vibes")
async def get_available_vibes():
    """Get available travel vibes and their characteristics"""
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
async def get_season_recommendation(vibe: str, destination: str, start_date: str):
    """Get season-based recommendations for a specific vibe and destination"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=503, detail="Service not ready")
        
        recommendation = await orchestrator.get_season_recommendation(vibe, destination, start_date)
        return recommendation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get season recommendation: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )