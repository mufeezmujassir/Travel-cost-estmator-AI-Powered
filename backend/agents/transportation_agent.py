import asyncio
from typing import Dict, Any, List
import googlemaps
from datetime import datetime

from .base_agent import BaseAgent
from models.travel_models import TravelRequest
from services.config import Settings

class TransportationAgent(BaseAgent):
    """Agent responsible for transportation planning and cost estimation"""
    
    def __init__(self, settings: Settings):
        super().__init__("Transportation Agent", settings)
        self.gmaps_client = None
    
    async def initialize(self):
        """Initialize the transportation agent"""
        await super().initialize()
        
        if self.settings.google_maps_api_key:
            self.gmaps_client = googlemaps.Client(key=self.settings.google_maps_api_key)
        else:
            print("⚠️ Google Maps API key not provided, using mock data")
    
    async def process(self, request: TravelRequest, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Plan transportation and calculate costs"""
        try:
            self.validate_request(request)
            
            # Get transportation options
            transportation_options = await self._get_transportation_options(request, context)
            
            # Calculate costs
            cost_breakdown = await self._calculate_transportation_costs(transportation_options, request)
            
            # Get route optimization
            route_optimization = await self._optimize_routes(request, context)
            
            return {
                "transportation_options": transportation_options,
                "cost_breakdown": cost_breakdown,
                "route_optimization": route_optimization,
                "total_transportation_cost": cost_breakdown.get("total", 0)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_transportation_options(self, request: TravelRequest, context: Dict[str, Any] = None) -> Dict[str, Any]:
        options = {
            "airport_transfer": await self._get_airport_transfer_options(request),
            "local_transportation": await self._get_local_transportation_options(request),
            "inter_city_transportation": await self._get_inter_city_transportation_options(request)
        }
        
        return options
    
    async def _get_airport_transfer_options(self, request: TravelRequest) -> List[Dict[str, Any]]:
        if not self.gmaps_client:
            return self._get_mock_airport_transfer_options(request)
        
        try:
            # Get airport to hotel distance and time
            origin = f"{request.destination} Airport"
            destination = "Downtown " + request.destination
            
            # Get distance matrix
            result = self.gmaps_client.distance_matrix(
                origins=[origin],
                destinations=[destination],
                mode="driving",
                units="metric"
            )
            
            if result['rows'][0]['elements'][0]['status'] == 'OK':
                element = result['rows'][0]['elements'][0]
                distance = element['distance']['value'] / 1000  # Convert to km
                duration = element['duration']['value'] / 60  # Convert to minutes
                
                return [
                    {
                        "type": "taxi",
                        "cost_per_trip": 25 + (distance * 2),
                        "duration_minutes": duration,
                        "description": "Airport taxi service"
                    },
                    {
                        "type": "uber",
                        "cost_per_trip": 20 + (distance * 1.5),
                        "duration_minutes": duration,
                        "description": "Ride-sharing service"
                    },
                    {
                        "type": "shuttle",
                        "cost_per_trip": 15,
                        "duration_minutes": duration + 10,
                        "description": "Airport shuttle bus"
                    }
                ]
        except Exception as e:
            print(f"Error getting airport transfer options: {e}")
        
        return self._get_mock_airport_transfer_options(request)
    
    def _get_mock_airport_transfer_options(self, request: TravelRequest) -> List[Dict[str, Any]]:
        return [
            {
                "type": "taxi",
                "cost_per_trip": 35,
                "duration_minutes": 25,
                "description": "Airport taxi service"
            },
            {
                "type": "uber",
                "cost_per_trip": 28,
                "duration_minutes": 25,
                "description": "Ride-sharing service"
            },
            {
                "type": "shuttle",
                "cost_per_trip": 18,
                "duration_minutes": 35,
                "description": "Airport shuttle bus"
            }
        ]
    
    async def _get_local_transportation_options(self, request: TravelRequest) -> List[Dict[str, Any]]:
        return [
            {
                "type": "public_transport",
                "cost_per_day": 12,
                "description": "Unlimited public transport pass"
            },
            {
                "type": "taxi",
                "cost_per_day": 50,
                "description": "Taxi for local travel"
            },
            {
                "type": "uber",
                "cost_per_day": 40,
                "description": "Ride-sharing for local travel"
            },
            {
                "type": "car_rental",
                "cost_per_day": 45,
                "description": "Car rental with insurance"
            },
            {
                "type": "bike_rental",
                "cost_per_day": 15,
                "description": "Bicycle rental"
            }
        ]
    
    async def _get_inter_city_transportation_options(self, request: TravelRequest) -> List[Dict[str, Any]]:
        return [
            {
                "type": "train",
                "cost_per_trip": 45,
                "duration_hours": 2.5,
                "description": "High-speed train"
            },
            {
                "type": "bus",
                "cost_per_trip": 25,
                "duration_hours": 4,
                "description": "Inter-city bus"
            },
            {
                "type": "car_rental",
                "cost_per_trip": 60,
                "duration_hours": 3,
                "description": "Car rental for day trips"
            }
        ]
    
    async def _calculate_transportation_costs(self, options: Dict[str, Any], request: TravelRequest) -> Dict[str, Any]:
        trip_duration = self.calculate_trip_duration(request.start_date, request.return_date)
        
        # Airport transfers (arrival and departure)
        airport_transfer_cost = 0
        if options.get("airport_transfer"):
            taxi_cost = options["airport_transfer"][0]["cost_per_trip"]
            airport_transfer_cost = taxi_cost * 2 * request.travelers  # Round trip
        
        # Local transportation
        local_transport_cost = 0
        if options.get("local_transportation"):
            public_transport_cost = options["local_transportation"][0]["cost_per_day"]
            local_transport_cost = public_transport_cost * trip_duration * request.travelers
        
        # Inter-city transportation (if needed)
        inter_city_cost = 0
        if options.get("inter_city_transportation"):
            train_cost = options["inter_city_transportation"][0]["cost_per_trip"]
            inter_city_cost = train_cost * 2 * request.travelers
        
        total_cost = airport_transfer_cost + local_transport_cost + inter_city_cost
        
        return {
            "airport_transfer": airport_transfer_cost,
            "local_transportation": local_transport_cost,
            "inter_city_transportation": inter_city_cost,
            "total": total_cost,
            "cost_per_person": total_cost / request.travelers if request.travelers > 0 else 0
        }
    
    async def _optimize_routes(self, request: TravelRequest, context: Dict[str, Any] = None) -> Dict[str, Any]:
        if not self.gmaps_client:
            return self._get_mock_route_optimization(request)
        
        try:
            attractions = await self._get_popular_attractions(request.destination)
            
            optimized_routes = []
            for i in range(len(attractions) - 1):
                origin = attractions[i]["location"]
                destination = attractions[i + 1]["location"]
                
                result = self.gmaps_client.distance_matrix(
                    origins=[origin],
                    destinations=[destination],
                    mode="driving"
                )
                
                if result['rows'][0]['elements'][0]['status'] == 'OK':
                    element = result['rows'][0]['elements'][0]
                    optimized_routes.append({
                        "from": attractions[i]["name"],
                        "to": attractions[i + 1]["name"],
                        "distance_km": element['distance']['value'] / 1000,
                        "duration_minutes": element['duration']['value'] / 60
                    })
            
            return {
                "optimized_routes": optimized_routes,
                "total_distance_km": sum(route["distance_km"] for route in optimized_routes),
                "total_duration_minutes": sum(route["duration_minutes"] for route in optimized_routes)
            }
            
        except Exception as e:
            print(f"Error optimizing routes: {e}")
            return self._get_mock_route_optimization(request)
    
    def _get_mock_route_optimization(self, request: TravelRequest) -> Dict[str, Any]:
        return {
            "optimized_routes": [
                {
                    "from": "Hotel",
                    "to": "City Center",
                    "distance_km": 5.2,
                    "duration_minutes": 15
                },
                {
                    "from": "City Center",
                    "to": "Museum District",
                    "distance_km": 2.8,
                    "duration_minutes": 8
                },
                {
                    "from": "Museum District",
                    "to": "Restaurant Area",
                    "distance_km": 1.5,
                    "duration_minutes": 5
                }
            ],
            "total_distance_km": 9.5,
            "total_duration_minutes": 28
        }
    
    async def _get_popular_attractions(self, destination: str) -> List[Dict[str, Any]]:
        attractions_data = {
            "tokyo": [
                {"name": "Senso-ji Temple", "location": "Asakusa, Tokyo"},
                {"name": "Tokyo Skytree", "location": "Sumida, Tokyo"},
                {"name": "Shibuya Crossing", "location": "Shibuya, Tokyo"},
                {"name": "Tsukiji Fish Market", "location": "Chuo, Tokyo"}
            ],
            "paris": [
                {"name": "Eiffel Tower", "location": "7th arrondissement, Paris"},
                {"name": "Louvre Museum", "location": "1st arrondissement, Paris"},
                {"name": "Notre-Dame Cathedral", "location": "4th arrondissement, Paris"},
                {"name": "Champs-Élysées", "location": "8th arrondissement, Paris"}
            ],
            "new york": [
                {"name": "Times Square", "location": "Manhattan, New York"},
                {"name": "Central Park", "location": "Manhattan, New York"},
                {"name": "Statue of Liberty", "location": "Liberty Island, New York"},
                {"name": "Brooklyn Bridge", "location": "Brooklyn, New York"}
            ]
        }
        
        default_attractions = [
            {"name": "City Center", "location": f"Downtown {destination}"},
            {"name": "Museum District", "location": f"Museum Quarter, {destination}"},
            {"name": "Restaurant Area", "location": f"Food District, {destination}"},
            {"name": "Shopping District", "location": f"Shopping Area, {destination}"}
        ]
        
        destination_lower = destination.lower()
        for city, attractions in attractions_data.items():
            if city in destination_lower:
                return attractions
        
        return default_attractions