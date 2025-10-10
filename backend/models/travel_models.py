from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum

class VibeType(str, Enum):
    ROMANTIC = "romantic"
    ADVENTURE = "adventure"
    BEACH = "beach"
    NATURE = "nature"
    CULTURAL = "cultural"
    CULINARY = "culinary"
    WELLNESS = "wellness"

class TravelRequest(BaseModel):
    """Travel estimation request model"""
    origin: str = Field(..., description="Origin city", min_length=2, max_length=100)
    destination: str = Field(..., description="Destination city", min_length=2, max_length=100)
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    return_date: str = Field(..., description="Return date in YYYY-MM-DD format")
    travelers: int = Field(..., description="Number of travelers", ge=1, le=10)
    budget: Optional[float] = Field(None, description="Budget in USD", ge=0)
    vibe: VibeType = Field(..., description="Travel vibe preference")
    include_price_trends: bool = Field(True, description="Include price calendar analysis")
    
    @validator('start_date', 'return_date')
    def validate_dates(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')
    
    @validator('return_date')
    def validate_return_date(cls, v, values):
        if 'start_date' in values:
            start_date = datetime.strptime(values['start_date'], '%Y-%m-%d')
            return_date = datetime.strptime(v, '%Y-%m-%d')
            if return_date <= start_date:
                raise ValueError('Return date must be after start date')
        return v

class Flight(BaseModel):
    """Flight information model"""
    airline: str
    flight_number: str
    departure_time: str
    arrival_time: str
    departure_airport: str
    arrival_airport: str
    duration: str
    class_type: str
    price: float
    currency: str = "USD"
    stops: int = 0
    aircraft: Optional[str] = None

class Hotel(BaseModel):
    """Hotel information model"""
    name: str
    location: str
    price_per_night: float
    currency: str = "USD"
    rating: float = Field(..., ge=0, le=5)
    description: str
    amenities: List[str] = []
    image_url: Optional[str] = None
    distance_from_center: Optional[float] = None
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    price_confidence: Optional[str] = "high"  # "high" for actual prices, "estimated" for fallback
    data_source: Optional[str] = None  # Track where the data came from

class Activity(BaseModel):
    """Activity information model"""
    name: str
    description: str
    location: str
    time: str
    duration: str
    price: Optional[float] = None
    currency: str = "USD"
    category: str
    vibe_match: float = Field(..., ge=0, le=1, description="How well this activity matches the selected vibe")

class DayItinerary(BaseModel):
    """Daily itinerary model"""
    date: str
    activities: List[Activity]
    total_cost: float = 0
    currency: str = "USD"

class CostBreakdown(BaseModel):
    """Cost breakdown model"""
    flights: float = 0
    accommodation: float = 0
    transportation: float = 0
    activities: float = 0
    food: float = 0
    miscellaneous: float = 0
    currency: str = "USD"

class SeasonRecommendation(BaseModel):
    """Season recommendation model"""
    current_season: str
    optimal_season: str
    is_optimal: bool
    recommendation: str
    alternative_months: List[int] = []
    weather_considerations: List[str] = []

class TravelResponse(BaseModel):
    """Complete travel estimation response"""
    request_id: str
    flights: List[Flight] = []
    hotels: List[Hotel] = []
    itinerary: List[DayItinerary] = []
    cost_breakdown: CostBreakdown
    total_cost: float
    currency: str = "USD"
    season_recommendation: SeasonRecommendation
    recommendations: List[str] = []
    vibe_analysis: Dict[str, Any] = {}
    price_trends: Optional[Dict[str, Any]] = None  # Price calendar data
    transportation: Optional[Dict[str, Any]] = None  # Transportation options and details
    is_domestic_travel: bool = False  # Whether this is domestic travel
    travel_distance_km: float = 0.0  # Distance between origin and destination
    generated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AgentResponse(BaseModel):
    """Individual agent response model"""
    agent_name: str
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    processing_time: float = 0
    timestamp: datetime = Field(default_factory=datetime.now)

class EmotionalAnalysis(BaseModel):
    """Emotional intelligence analysis model"""
    vibe_score: float = Field(..., ge=0, le=1)
    season_compatibility: float = Field(..., ge=0, le=1)
    mood_indicators: List[str] = []
    recommended_activities: List[str] = []
    emotional_wellness_tips: List[str] = []
    vibe_enhancement_suggestions: List[str] = []