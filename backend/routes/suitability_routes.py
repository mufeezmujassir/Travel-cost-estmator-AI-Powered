"""
Suitability Routes
API endpoints for vibe suitability scoring
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import asyncio

from services.suitability_scorer import SuitabilityScorer
from services.serp_service import SerpService
from services.config import Settings

router = APIRouter()

# Initialize services
settings = Settings()
serp_service = None
suitability_scorer = None

async def initialize_services():
    """Initialize services on startup"""
    global serp_service, suitability_scorer
    
    try:
        # Initialize SERP service for price data
        serp_service = SerpService(settings)
        await serp_service.initialize()
        
        # Initialize suitability scorer
        suitability_scorer = SuitabilityScorer(serp_service)
        
        print("✅ Suitability services initialized successfully")
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize all suitability services: {e}")
        # Initialize without SERP service (price data will be unavailable)
        suitability_scorer = SuitabilityScorer(None)

@router.get("/api/vibe-suitability")
async def get_vibe_suitability(
    vibe: str = Query(..., description="Vibe type (romantic, adventure, beach, etc.)"),
    destination: str = Query(..., description="Destination city"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    duration: int = Query(5, description="Trip duration in days", ge=1, le=30),
    origin: Optional[str] = Query(None, description="Origin city (optional, for price analysis)")
):
    """
    Get suitability score for a vibe and destination
    
    Returns a score (0-100) with label and reasoning based on:
    - Weather/climate comfort (40%)
    - Price favorability (25%) 
    - Crowd levels (15%)
    - Events relevance (10%)
    - Baseline seasonality (10%)
    """
    try:
        # Initialize services if not already done
        if not suitability_scorer:
            await initialize_services()
        
        if not suitability_scorer:
            raise HTTPException(status_code=503, detail="Suitability service not available")
        
        # Validate vibe
        valid_vibes = ["romantic", "adventure", "beach", "nature", "cultural", "culinary", "wellness"]
        if vibe.lower() not in valid_vibes:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid vibe. Must be one of: {', '.join(valid_vibes)}"
            )
        
        # Validate date format
        try:
            from datetime import datetime
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Calculate suitability score
        result = await suitability_scorer.calculate_suitability_score(
            vibe=vibe.lower(),
            destination=destination,
            start_date=start_date,
            duration_days=duration,
            origin=origin
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in vibe suitability endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/vibe-suitability/batch")
async def get_batch_vibe_suitability(
    destination: str = Query(..., description="Destination city"),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    duration: int = Query(5, description="Trip duration in days", ge=1, le=30),
    origin: Optional[str] = Query(None, description="Origin city (optional, for price analysis)"),
    vibes: str = Query("romantic,adventure,beach,nature,cultural,culinary,wellness", description="Comma-separated list of vibes")
):
    """
    Get suitability scores for multiple vibes at once
    
    Useful for the VibeSelector component to get all scores in one request
    """
    try:
        # Initialize services if not already done
        if not suitability_scorer:
            await initialize_services()
        
        if not suitability_scorer:
            raise HTTPException(status_code=503, detail="Suitability service not available")
        
        # Parse vibes
        vibe_list = [v.strip().lower() for v in vibes.split(",")]
        valid_vibes = ["romantic", "adventure", "beach", "nature", "cultural", "culinary", "wellness"]
        
        # Validate vibes
        invalid_vibes = [v for v in vibe_list if v not in valid_vibes]
        if invalid_vibes:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid vibes: {', '.join(invalid_vibes)}. Must be from: {', '.join(valid_vibes)}"
            )
        
        # Validate date format
        try:
            from datetime import datetime
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Calculate scores for all vibes in parallel with timeout
        tasks = []
        for vibe in vibe_list:
            task = suitability_scorer.calculate_suitability_score(
                vibe=vibe,
                destination=destination,
                start_date=start_date,
                duration_days=duration,
                origin=origin
            )
            tasks.append(task)
        
        # Set overall timeout for batch processing (max 10 seconds)
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=10.0
            )
        except asyncio.TimeoutError:
            print("Batch suitability calculation timed out, using fallback scores")
            results = []
            for vibe in vibe_list:
                results.append({
                    "score": 50.0,
                    "label": "✔ Good Timing",
                    "reason": "Quick assessment - detailed analysis timed out"
                })
        
        # Format results
        vibe_scores = {}
        for i, vibe in enumerate(vibe_list):
            result = results[i]
            if isinstance(result, Exception):
                print(f"Error calculating score for {vibe}: {result}")
                vibe_scores[vibe] = {
                    "score": 50.0,
                    "label": "✔ Good Timing",
                    "reason": "Unable to analyze timing",
                    "error": str(result)
                }
            else:
                vibe_scores[vibe] = result
        
        return {
            "success": True,
            "data": {
                "destination": destination,
                "start_date": start_date,
                "duration": duration,
                "scores": vibe_scores
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in batch vibe suitability endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api/vibe-suitability/health")
async def health_check():
    """Health check for suitability service"""
    try:
        if not suitability_scorer:
            await initialize_services()
        
        return {
            "status": "healthy" if suitability_scorer else "unhealthy",
            "services": {
                "suitability_scorer": suitability_scorer is not None,
                "serp_service": serp_service is not None,
                "weather_service": True,  # Always available (uses free API)
                "region_mapper": True    # Always available (uses free geocoding)
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
