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
            
            # Check if this is domestic travel (no flights)
            has_flights = False
            if context and context.get("flight_search_agent"):
                flights = context["flight_search_agent"].get("data", {}).get("flights", [])
                has_flights = len(flights) > 0
            
            # Get transportation options
            transportation_options = await self._get_transportation_options(request, context)
            
            # Calculate costs (pass has_flights to exclude airport transfers for domestic)
            cost_breakdown = await self._calculate_transportation_costs(transportation_options, request, has_flights)
            
            # Get route optimization
            route_optimization = await self._optimize_routes(request, context)
            
            # Format inter-city options for UI display
            inter_city_options = []
            if transportation_options.get("inter_city_transportation"):
                for option in transportation_options["inter_city_transportation"]:
                    # Format duration
                    if "duration_hours" in option:
                        hours = int(option["duration_hours"])
                        minutes = int((option["duration_hours"] - hours) * 60)
                        duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                    else:
                        duration_str = "Varies"
                    
                    inter_city_options.append({
                        "type": option.get("type"),
                        "cost": option.get("cost_per_trip", option.get("cost", 0)),
                        "duration": duration_str,
                        "description": option.get("description", ""),
                        "notes": option.get("notes")
                    })
            
            # Format local transportation for UI
            local_transportation = {}
            if transportation_options.get("local_transportation"):
                local_options = [opt["type"] for opt in transportation_options["local_transportation"]]
                daily_cost = transportation_options["local_transportation"][0].get("cost_per_day", 0) if transportation_options["local_transportation"] else 0
                local_transportation = {
                    "options": local_options,
                    "daily_cost": daily_cost
                }
            
            return {
                "transportation_options": transportation_options,
                "inter_city_options": inter_city_options,  # Formatted for UI
                "local_transportation": local_transportation,  # Formatted for UI
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
        """
        Get inter-city transportation options.
        For domestic travel, provide comprehensive ground transport options.
        """
        # Try to get distance if available from context
        try:
            if self.gmaps_client:
                result = self.gmaps_client.distance_matrix(
                    origins=[request.origin],
                    destinations=[request.destination],
                    mode="driving",
                    units="metric"
                )
                
                if result['rows'][0]['elements'][0]['status'] == 'OK':
                    element = result['rows'][0]['elements'][0]
                    distance_km = element['distance']['value'] / 1000
                    duration_hours = element['duration']['value'] / 3600
                    
                    # Calculate costs based on actual distance
                    train_cost = max(20, min(100, 15 + (distance_km * 0.15)))  # $15 base + $0.15/km
                    bus_cost = max(10, min(60, 10 + (distance_km * 0.10)))     # $10 base + $0.10/km
                    car_cost = max(30, min(150, 25 + (distance_km * 0.20)))    # $25 base + $0.20/km
                    taxi_cost = max(40, min(300, 35 + (distance_km * 0.50)))   # $35 base + $0.50/km
                    
                    return [
                        {
                            "type": "train",
                            "cost_per_trip": round(train_cost, 2),
                            "duration_hours": round(duration_hours * 1.1, 1),  # Trains slightly slower
                            "distance_km": round(distance_km, 1),
                            "description": f"Train service covering {distance_km:.0f} km"
                        },
                        {
                            "type": "bus",
                            "cost_per_trip": round(bus_cost, 2),
                            "duration_hours": round(duration_hours * 1.2, 1),  # Buses slower than cars
                            "distance_km": round(distance_km, 1),
                            "description": f"Inter-city bus covering {distance_km:.0f} km"
                        },
                        {
                            "type": "car_rental",
                            "cost_per_trip": round(car_cost, 2),
                            "duration_hours": round(duration_hours, 1),
                            "distance_km": round(distance_km, 1),
                            "description": f"Self-drive car rental ({distance_km:.0f} km)"
                        },
                        {
                            "type": "private_car",
                            "cost_per_trip": round(taxi_cost, 2),
                            "duration_hours": round(duration_hours, 1),
                            "distance_km": round(distance_km, 1),
                            "description": f"Private car/taxi service ({distance_km:.0f} km)"
                        }
                    ]
        except Exception as e:
            print(f"Could not calculate distance-based costs: {e}")
        
        # Fallback to default options
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
            },
            {
                "type": "private_car",
                "cost_per_trip": 80,
                "duration_hours": 3,
                "description": "Private car/taxi service"
            }
        ]
    
    async def _calculate_transportation_costs(self, options: Dict[str, Any], request: TravelRequest, has_flights: bool = True) -> Dict[str, Any]:
        trip_duration = self.calculate_trip_duration(request.start_date, request.return_date)
        
        # Airport transfers (arrival and departure) - ONLY for international travel with flights
        airport_transfer_cost = 0
        if has_flights and options.get("airport_transfer"):
            taxi_cost = options["airport_transfer"][0]["cost_per_trip"]
            airport_transfer_cost = taxi_cost * 2 * request.travelers  # Round trip
        
        # Local transportation
        local_transport_cost = 0
        if options.get("local_transportation"):
            public_transport_cost = options["local_transportation"][0]["cost_per_day"]
            local_transport_cost = public_transport_cost * trip_duration * request.travelers
        
        # Inter-city transportation - using cheapest option (usually train or bus)
        inter_city_cost = 0
        if options.get("inter_city_transportation") and len(options["inter_city_transportation"]) > 0:
            # Use the cheapest option (first one is usually cheapest after sorting)
            cheapest_option = min(options["inter_city_transportation"], 
                                 key=lambda x: x.get("cost_per_trip", float('inf')))
            cost_per_trip = cheapest_option.get("cost_per_trip", 0)
            
            # Round trip cost (going there and coming back) for all travelers
            inter_city_cost = cost_per_trip * 2 * request.travelers
        
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