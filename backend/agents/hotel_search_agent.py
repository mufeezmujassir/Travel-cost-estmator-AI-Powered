import asyncio
from typing import Dict, Any, List
import json

from .base_agent import BaseAgent
from models.travel_models import TravelRequest, Hotel, VibeType
from services.serp_service import SerpService
from services.grok_service import GrokService
from services.hotel_context_service import HotelContextService

class HotelSearchAgent(BaseAgent):
    """Agent responsible for finding and analyzing hotel options"""
    
    def __init__(self, settings):
        super().__init__("Hotel Search Agent", settings)
        self.serp_service = None
        self.grok_service = None
        self.hotel_context_service = None
    
    async def initialize(self):
        """Initialize the hotel search agent"""
        await super().initialize()
        self.serp_service = SerpService(self.settings)
        await self.serp_service.initialize()
        self.grok_service = GrokService(self.settings)
        await self.grok_service.initialize()
        self.hotel_context_service = HotelContextService(self.serp_service, self.grok_service)
    
    async def process(self, request: TravelRequest, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Search for hotel options that match the vibe"""
        try:
            self.validate_request(request)
            
            # Search for hotels using SERP API
            hotels_data = await self._search_hotels(request)
            
            # Analyze hotels for vibe using Grok
            vibe_analyzed_hotels = await self._analyze_hotels_for_vibe(hotels_data, request)
            
            # Process and rank hotels
            processed_hotels = await self._process_hotel_data(vibe_analyzed_hotels, request)
            
            # Select best options
            best_hotels = self._select_best_hotels(processed_hotels, request)
            
            result = {
                "hotels": [hotel.dict() for hotel in best_hotels],
                "total_options_found": len(processed_hotels),
                "vibe_analysis": {
                    "vibe": request.vibe.value,
                    "hotel_criteria": self._get_vibe_hotel_criteria(request.vibe)
                }
            }
            
            # Get hotel context if requested
            if context and context.get("include_hotel_context", False):
                hotel_context = await self.get_hotel_context(request, hotels_data)
                result["hotel_context"] = hotel_context
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _search_hotels(self, request: TravelRequest) -> List[Dict[str, Any]]:
        """Search for hotels using SERP API"""
        try:
            return await self.serp_service.search_hotels(
                destination=f"{request.destination} Resorts" if "bali" in request.destination.lower() else f"{request.destination} hotels",
                check_in=request.start_date,
                check_out=request.return_date,
                travelers=request.travelers,
            )
        except Exception as e:
            print(f"Error searching hotels: {e}")
            return []
    
    async def _analyze_hotels_for_vibe(self, hotels_data: List[Dict[str, Any]], request: TravelRequest) -> List[Dict[str, Any]]:
        """Analyze hotels for vibe compatibility using Grok AI"""
        analyzed_hotels = []
        
        for hotel in hotels_data:
            prompt = f"""
            Analyze this hotel for compatibility with {request.vibe.value} vibe:
            
            Name: {hotel.get('name')}
            Description: {hotel.get('description')}
            Amenities: {', '.join(hotel.get('amenities', []))}
            
            Provide:
            - vibe_score (0-1.0 as a decimal number)
            - reasoning (short explanation)
            - vibe_enhancements (2-3 suggestions as an array)
            
            Respond in valid JSON format:
            {{
                "vibe_score": 0.9,
                "reasoning": "explanation",
                "vibe_enhancements": ["sug1", "sug2"]
            }}
            """
            
            try:
                response = await self.grok_service.generate_response(prompt, force_json=True)
                analysis = json.loads(response)
                hotel["vibe_analysis"] = analysis
            except:
                hotel["vibe_analysis"] = {
                    "vibe_score": 0.8,
                    "reasoning": "Good match for vibe",
                    "vibe_enhancements": ["Book special packages", "Request upgrades"]
                }
            
            analyzed_hotels.append(hotel)
        
        return analyzed_hotels
    
    async def _process_hotel_data(self, hotels_data: List[Dict[str, Any]], request: TravelRequest) -> List[Hotel]:
        """Process raw hotel data into Hotel objects"""
        processed_hotels = []
        
        for hotel_data in hotels_data:
            try:
                hotel = Hotel(
                    name=hotel_data.get("name", "Unknown Hotel"),
                    location=hotel_data.get("location", "Unknown Location"),
                    # Ensure we read the normalized key from SERP processing
                    price_per_night=hotel_data.get("price_per_night") or hotel_data.get("price", 0.0),
                    rating=hotel_data.get("rating", 0.0),
                    description=hotel_data.get("description", ""),
                    amenities=hotel_data.get("amenities", []),
                    image_url=hotel_data.get("image_url"),
                    distance_from_center=hotel_data.get("distance_from_center"),
                    price_confidence=hotel_data.get("price_confidence", "high"),
                    data_source=hotel_data.get("data_source")
                )
                processed_hotels.append(hotel)
            except Exception as e:
                print(f"Error processing hotel data: {e}")
                continue
        
        return processed_hotels
    
    def _select_best_hotels(self, hotels: List[Hotel], request: TravelRequest) -> List[Hotel]:
        """Select the best hotel options based on vibe and other criteria"""
        if not hotels:
            return []
        
        # Sort by rating and price
        def hotel_score(hotel: Hotel) -> float:
            rating_score = hotel.rating / 5.0
            price_score = 1.0 / (hotel.price_per_night / 100.0 + 1)
            return rating_score * 0.6 + price_score * 0.4
        
        sorted_hotels = sorted(hotels, key=hotel_score, reverse=True)
        
        return sorted_hotels[:3]
    
    def _get_vibe_hotel_criteria(self, vibe: VibeType) -> Dict[str, Any]:
        criteria = {
            VibeType.ROMANTIC: {
                "amenities": ["Spa", "Fine Dining", "Room Service", "Romantic Packages"],
                "location": "Downtown or Historic District",
                "atmosphere": "Intimate and luxurious"
            },
            VibeType.ADVENTURE: {
                "amenities": ["Gear Storage", "Fitness Center", "Adventure Desk"],
                "location": "Near outdoor activities",
                "atmosphere": "Active and energetic"
            },
            VibeType.BEACH: {
                "amenities": ["Beach Access", "Pool", "Water Sports"],
                "location": "Beachfront or coastal",
                "atmosphere": "Relaxed and tropical"
            },
            VibeType.NATURE: {
                "amenities": ["Nature Trails", "Wildlife Viewing", "Eco-Friendly"],
                "location": "Near nature reserves",
                "atmosphere": "Peaceful and natural"
            },
            VibeType.CULTURAL: {
                "amenities": ["Cultural Tours", "Art Gallery", "Historic Architecture"],
                "location": "Cultural district",
                "atmosphere": "Sophisticated and educational"
            },
            VibeType.CULINARY: {
                "amenities": ["Fine Dining", "Cooking Classes", "Wine Cellar"],
                "location": "Food district",
                "atmosphere": "Gourmet and indulgent"
            },
            VibeType.WELLNESS: {
                "amenities": ["Spa", "Yoga Studio", "Meditation Garden"],
                "location": "Spa district or peaceful area",
                "atmosphere": "Calm and rejuvenating"
            }
        }
        
        return criteria.get(vibe, {
            "amenities": ["WiFi", "Pool", "Restaurant"],
            "location": "City center",
            "atmosphere": "Comfortable and convenient"
        })
    
    async def get_hotel_context(self, request: TravelRequest, hotels_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get comprehensive hotel context including:
        - Where to stay (top areas/neighborhoods)
        - When to visit (seasonal pricing and trends)
        - What you'll pay (price breakdown by star rating)
        """
        try:
            context = await self.hotel_context_service.get_hotel_context(
                destination=request.destination,
                check_in_date=request.start_date,
                check_out_date=request.return_date,
                hotels_data=hotels_data
            )
            return context
        except Exception as e:
            print(f"⚠️ Error getting hotel context: {e}")
            return {
                "status": "error",
                "message": str(e)
            }