import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

from .base_agent import BaseAgent
from models.travel_models import TravelRequest, DayItinerary, Activity, VibeType
from services.grok_service import GrokService

class RecommendationAgent(BaseAgent):
    """Agent responsible for creating personalized itineraries and recommendations"""
    
    def __init__(self, settings):
        super().__init__("Recommendation Agent", settings)
        self.grok_service = None
    
    async def initialize(self):
        """Initialize the recommendation agent"""
        await super().initialize()
        self.grok_service = GrokService(self.settings)
        await self.grok_service.initialize()
    
    async def process(self, request: TravelRequest, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create personalized itinerary and recommendations"""
        try:
            self.validate_request(request)
            
            # Get data from other agents
            agent_data = context or {}
            
            # Create day-by-day itinerary
            itinerary = await self._generate_itinerary_with_llm(request, agent_data)
            
            # Get personalized recommendations
            recommendations = await self._get_personalized_recommendations(request, agent_data)
            
            # Analyze season and timing
            season_analysis = await self._analyze_season_timing(request)
            
            return {
                "itinerary": [day.dict() for day in itinerary],
                "recommendations": recommendations,
                "season_analysis": season_analysis,
                "vibe_enhancement_tips": await self._get_vibe_enhancement_tips(request)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _generate_itinerary_with_llm(self, request: TravelRequest, agent_data: Dict[str, Any]) -> List[DayItinerary]:
        """Generate day-by-day itinerary using Grok LLM"""
        prompt = f"""
        Create a detailed day-by-day itinerary for this trip:
        
        Destination: {request.destination}
        Vibe: {request.vibe.value}
        Travelers: {request.travelers}
        Start Date: {request.start_date}
        Return Date: {request.return_date}
        Duration: {self.calculate_trip_duration(request.start_date, request.return_date)} days
        
        For each day, provide 4-6 activities with:
        - name
        - description
        - location (specific place in {request.destination})
        - time (e.g., 9:00 AM)
        - duration (e.g., 2 hours)
        - price (estimate in USD per person)
        - category (e.g., sightseeing, dining, activity)
        
        Make the activities match the {request.vibe.value} vibe.
        Include travel time between locations where appropriate.
        Calculate total_cost for each day as sum of activity prices * travelers.
        
        Respond ONLY in JSON format as an object with 'itinerary' key:
        {{
            "itinerary": [
                {{
                    "date": "YYYY-MM-DD",
                    "activities": [
                        {{
                            "name": "Activity Name",
                            "description": "Detailed description",
                            "location": "Specific location",
                            "time": "HH:MM AM/PM",
                            "duration": "X hours",
                            "price": X,
                            "category": "category"
                        }},
                        ...
                    ],
                    "total_cost": X
                }},
                ...
            ]
        }}
        Make sure the JSON is valid with no extra text, no trailing commas, and proper formatting.
        """
        
        try:
            response = await self.grok_service.generate_response(prompt)
            text = response.strip()
            # Improved cleaning: Find the JSON object
            start = text.find('{')
            end = text.rfind('}') + 1
            cleaned = text[start:end] if start != -1 and end != 0 else text
            data = json.loads(cleaned)
            itinerary_data = data["itinerary"]  # Extract the array
            
            # Convert to DayItinerary objects
            itinerary = []
            for day_data in itinerary_data:
                activities = [Activity(
                    name=act["name"],
                    description=act["description"],
                    location=act["location"],
                    time=act["time"],
                    duration=act["duration"],
                    price=act["price"],
                    category=act["category"],
                    vibe_match=0.9  
                ) for act in day_data["activities"]]
                
                itinerary.append(DayItinerary(
                    date=day_data["date"],
                    activities=activities,
                    total_cost=day_data["total_cost"]
                ))
            
            return itinerary
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Raw response: {response}")  # Log for debugging
            return self._get_fallback_itinerary(request)
        except Exception as e:
            print(f"Error generating itinerary with LLM: {e}")
            return self._get_fallback_itinerary(request)


    def _get_fallback_itinerary(self, request: TravelRequest) -> List[DayItinerary]:
        return [
            DayItinerary(
                date=request.start_date,
                activities=[
                    Activity(
                        name="Arrival and Exploration",
                        description="Arrive and explore the city",
                        location=request.destination,
                        time="9:00 AM",
                        duration="All day",
                        price=0,
                        category="arrival",
                        vibe_match=0.8
                    )
                ],
                total_cost=0
            )
        ]

    async def _get_personalized_recommendations(self, request: TravelRequest, agent_data: Dict[str, Any]) -> List[str]:
        try:
            prompt = f"""
            Provide personalized travel recommendations for this trip:
            
            Destination: {request.destination}
            Vibe: {request.vibe.value}
            Travelers: {request.travelers}
            Duration: {self.calculate_trip_duration(request.start_date, request.return_date)} days
            Season: {self.get_season_from_date(request.start_date)}
            
            Provide 5-7 specific, actionable recommendations that enhance the {request.vibe.value} experience.
            Focus on practical tips, hidden gems, and unique experiences.
            
            Respond as a simple list of recommendations, one per line.
            """
            
            response = await self.grok_service.generate_response(prompt)
            recommendations = [line.strip() for line in response.split('\n') if line.strip()]
            
            return recommendations[:7]
            
        except Exception as e:
            print(f"Error getting personalized recommendations: {e}")
            return self._get_fallback_recommendations(request)
    
    def _get_fallback_recommendations(self, request: TravelRequest) -> List[str]:
        recommendations = [
            f"Book activities in advance to secure the best {request.vibe.value} experiences",
            "Pack according to the seasonal weather patterns",
            "Learn a few basic phrases in the local language",
            "Download offline maps and translation apps",
            "Keep emergency contact information handy"
        ]
        
        if request.vibe.value == "romantic":
            recommendations.append("Consider booking private experiences for intimate moments")
        elif request.vibe.value == "adventure":
            recommendations.append("Ensure you have proper travel insurance for adventure activities")
        elif request.vibe.value == "beach":
            recommendations.append("Pack reef-safe sunscreen and beach essentials")
        
        return recommendations[:7]
    
    async def _analyze_season_timing(self, request: TravelRequest) -> Dict[str, Any]:
        current_season = self.get_season_from_date(request.start_date)
        
        season_insights = {
            "spring": {
                "weather": "Mild temperatures, occasional rain",
                "advantages": ["Fewer crowds", "Lower prices", "Beautiful blooms"],
                "considerations": ["Pack layers", "Check for seasonal closures"]
            },
            "summer": {
                "weather": "Warm to hot temperatures, peak season",
                "advantages": ["Longer days", "All attractions open", "Festival season"],
                "considerations": ["Book early", "Expect crowds", "Stay hydrated"]
            },
            "autumn": {
                "weather": "Cool temperatures, changing colors",
                "advantages": ["Beautiful foliage", "Harvest season", "Moderate crowds"],
                "considerations": ["Pack warm layers", "Check harvest schedules"]
            },
            "winter": {
                "weather": "Cold temperatures, potential snow",
                "advantages": ["Lowest prices", "Fewest crowds", "Winter activities"],
                "considerations": ["Pack warm clothes", "Check for closures", "Winter driving conditions"]
            }
        }
        
        return {
            "current_season": current_season,
            "season_insights": season_insights.get(current_season, season_insights["spring"]),
            "optimal_timing": self._get_optimal_timing_for_vibe(request.vibe, current_season)
        }
    
    def _get_optimal_timing_for_vibe(self, vibe: VibeType, current_season: str) -> str:
        optimal_seasons = {
            VibeType.ROMANTIC: ["spring", "autumn"],
            VibeType.ADVENTURE: ["summer", "autumn"],
            VibeType.BEACH: ["summer"],
            VibeType.NATURE: ["spring", "autumn"],
            VibeType.CULTURAL: ["autumn", "spring"],
            VibeType.CULINARY: ["autumn", "spring"],
            VibeType.WELLNESS: ["winter", "spring"]
        }
        
        optimal = optimal_seasons.get(vibe, ["spring", "summer", "autumn"])
        
        if current_season in optimal:
            return f"Perfect timing! {current_season.title()} is ideal for {vibe.value} experiences."
        else:
            return f"Consider visiting in {optimal[0]} for the best {vibe.value} experience, but {current_season} can still be enjoyable."
    
    async def _get_vibe_enhancement_tips(self, request: TravelRequest) -> List[str]:
        prompt = f"""
        Provide 4-6 practical tips to enhance a {request.vibe.value} travel experience in {request.destination}.
        
        Respond as a simple list in JSON format:
        ["tip1", "tip2", ...]
        """
        
        try:
            response = await self.grok_service.generate_response(prompt)
            return json.loads(response)
        except:
            return ["Research local customs", "Pack appropriately", "Book in advance"]