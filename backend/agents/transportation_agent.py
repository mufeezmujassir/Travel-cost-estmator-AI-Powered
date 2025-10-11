import asyncio
from typing import Dict, Any, List
import googlemaps
from datetime import datetime

from .base_agent import BaseAgent
from models.travel_models import TravelRequest
from services.config import Settings
from services.intelligent_pricing_service import IntelligentPricingService
from services.airport_resolver import AirportResolver
from services.grok_service import GrokService
from .local_transport_estimator import LocalTransportEstimator

class TransportationAgent(BaseAgent):
    """Agent responsible for transportation planning and cost estimation"""
    
    def __init__(self, settings: Settings):
        super().__init__("Transportation Agent", settings)
        self.gmaps_client = None
        self.pricing_service = None
        self.airport_resolver = None
        self.llm_pricing_agent = None
        self.grok_service = None
        self.local_transport_estimator = None
    
    async def initialize(self):
        """Initialize the transportation agent"""
        await super().initialize()
        
        if self.settings.google_maps_api_key:
            self.gmaps_client = googlemaps.Client(key=self.settings.google_maps_api_key)
        else:
            print("⚠️ Google Maps API key not provided, using mock data")
        
        # Initialize Grok service for LLM pricing
        self.grok_service = GrokService(self.settings)
        await self.grok_service.initialize()
        
        # Initialize LLM pricing agent (preferred method)
        try:
            from .transportation_pricing_agent import TransportationPricingAgent
            self.llm_pricing_agent = TransportationPricingAgent(self.grok_service)
            print("✅ LLM Pricing Agent initialized")
        except Exception as e:
            print(f"⚠️ Could not initialize LLM pricing agent: {e}")
            self.llm_pricing_agent = None
        
        # Fallback: Initialize simple intelligent pricing service
        self.pricing_service = IntelligentPricingService(self.grok_service)
        self.airport_resolver = AirportResolver(self.settings)
        
        # Initialize local transport estimator
        self.local_transport_estimator = LocalTransportEstimator(self.grok_service)
    
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
                    # Format duration if not already provided
                    duration_str = option.get("duration_str")
                    if not duration_str and "duration_hours" in option and option["duration_hours"] > 0:
                        hours = int(option["duration_hours"])
                        minutes = int((option["duration_hours"] - hours) * 60)
                        duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                    elif not duration_str:
                        duration_str = "Varies"
                    
                    # Pass through ALL fields from the original option
                    formatted_option = {
                        "type": option.get("type"),
                        "cost": option.get("cost_per_trip", option.get("cost", 0)),
                        "cost_per_trip": option.get("cost_per_trip", option.get("cost", 0)),
                        "duration": duration_str,
                        "duration_str": duration_str,
                        "duration_hours": option.get("duration_hours", 0),
                        "distance_km": option.get("distance_km", 0),
                        "description": option.get("description", ""),
                        "quality": option.get("quality", ""),
                        "booking": option.get("booking", ""),
                        "notes": option.get("notes"),
                        "ai_confidence": option.get("ai_confidence", 0)
                    }
                    inter_city_options.append(formatted_option)
            
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
                "inter_city_transportation": inter_city_options,  # Also provide as inter_city_transportation for compatibility
                "local_transportation": local_transportation,  # Formatted for UI
                "costs": cost_breakdown,  # Also provide as "costs" for UI
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
        Uses LLM-powered intelligent pricing for maximum accuracy.
        """
        # Get distance first
        distance_km = 50  # Default fallback
        duration_hours = 1.0
        
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
        except Exception as e:
            print(f"Could not get distance from Google Maps: {e}")
        
        # Try LLM pricing agent first (most intelligent)
        if self.llm_pricing_agent:
            try:
                pricing_result = await self.llm_pricing_agent.calculate_prices(
                    origin=request.origin,
                    destination=request.destination,
                    distance_km=distance_km,
                    travelers=request.travelers
                )
                
                print(f"🔍 LLM Pricing Result: {pricing_result.keys() if pricing_result else 'None'}")
                
                if pricing_result.get("prices"):
                    formatted_prices = self._format_llm_prices(pricing_result, distance_km)
                    print(f"🔍 Formatted Prices Count: {len(formatted_prices)}")
                    if formatted_prices:
                        print(f"🔍 First Option: {formatted_prices[0].get('type')} - ${formatted_prices[0].get('cost_per_trip')}")
                    return formatted_prices
                else:
                    print(f"⚠️ No prices in LLM result")
            except Exception as e:
                print(f"⚠️ LLM pricing failed, falling back: {e}")
                import traceback
                traceback.print_exc()
        
        # Fallback to multiplier-based pricing
        return await self._get_fallback_pricing(request, distance_km, duration_hours)
    
    def _format_llm_prices(self, pricing_result: Dict[str, Any], distance_km: float) -> List[Dict[str, Any]]:
        """Format LLM pricing results into expected structure"""
        prices = pricing_result.get("prices", {})
        
        options = []
        
        # Train
        if "train" in prices:
            train_data = prices["train"]
            duration_str = train_data.get("duration", "1h")
            options.append({
                "type": "train",
                "cost_per_trip": round(train_data.get("cost", 0), 2),
                "duration_hours": self._parse_duration(duration_str),
                "duration_str": duration_str,  # Keep original string for display
                "distance_km": distance_km,
                "description": f"Train service covering {distance_km:.0f} km",
                "quality": train_data.get("quality", "standard"),
                "booking": train_data.get("booking", "station or online"),
                "ai_confidence": pricing_result.get("confidence", 0.9)
            })
        
        # Bus
        if "bus" in prices:
            bus_data = prices["bus"]
            duration_str = bus_data.get("duration", "1h 20m")
            options.append({
                "type": "bus",
                "cost_per_trip": round(bus_data.get("cost", 0), 2),
                "duration_hours": self._parse_duration(duration_str),
                "duration_str": duration_str,  # Keep original string for display
                "distance_km": distance_km,
                "description": f"Inter-city bus covering {distance_km:.0f} km",
                "quality": bus_data.get("quality", "basic"),
                "booking": bus_data.get("booking", "bus terminal"),
                "ai_confidence": pricing_result.get("confidence", 0.9)
            })
        
        # Car rental
        if "car_rental" in prices:
            car_data = prices["car_rental"]
            duration_str = car_data.get("duration", "1h")
            options.append({
                "type": "car_rental",
                "cost_per_trip": round(car_data.get("cost", 0), 2),
                "duration_hours": self._parse_duration(duration_str),
                "duration_str": duration_str,  # Keep original string for display
                "distance_km": distance_km,
                "description": f"Self-drive car rental ({distance_km:.0f} km)",
                "quality": car_data.get("quality", "good"),
                "booking": car_data.get("booking", "rental agency"),
                "ai_confidence": pricing_result.get("confidence", 0.9)
            })
        
        # Taxi/private car
        if "taxi" in prices:
            taxi_data = prices["taxi"]
            duration_str = taxi_data.get("duration", "1h")
            options.append({
                "type": "private_car",
                "cost_per_trip": round(taxi_data.get("cost", 0), 2),
                "duration_hours": self._parse_duration(duration_str),
                "duration_str": duration_str,  # Keep original string for display
                "distance_km": distance_km,
                "description": f"Private car/taxi service ({distance_km:.0f} km)",
                "quality": taxi_data.get("quality", "comfortable"),
                "booking": taxi_data.get("booking", "hotel or app"),
                "ai_confidence": pricing_result.get("confidence", 0.9)
            })
        
        return options
    
    def _parse_duration(self, duration_str: str) -> float:
        """Parse duration string like '1h 15m' to hours"""
        try:
            hours = 0
            minutes = 0
            if 'h' in duration_str:
                hours = int(duration_str.split('h')[0].strip())
            if 'm' in duration_str:
                min_part = duration_str.split('h')[-1] if 'h' in duration_str else duration_str
                minutes = int(min_part.replace('m', '').strip())
            return round(hours + minutes / 60, 1)
        except:
            return 1.0
    
    async def _get_fallback_pricing(self, request: TravelRequest, distance_km: float, duration_hours: float) -> List[Dict[str, Any]]:
        """Fallback pricing using multiplier method"""
        # Get country for pricing multiplier
        country = await self._detect_country(request.origin)
        pricing_multiplier = 1.0  # Default to USA pricing
        
        if country and self.pricing_service:
            try:
                pricing_multiplier = await self.pricing_service.get_pricing_multiplier(country)
                print(f"🌍 Fallback: Applying {country} pricing multiplier: {pricing_multiplier:.3f}x")
            except Exception as e:
                print(f"⚠️ Could not get pricing multiplier, using default: {e}")
        
        # Calculate base costs (USA pricing)
        base_train = max(20, min(100, 15 + (distance_km * 0.15)))
        base_bus = max(10, min(60, 10 + (distance_km * 0.10)))
        base_car = max(30, min(150, 25 + (distance_km * 0.20)))
        base_taxi = max(40, min(300, 35 + (distance_km * 0.50)))
        
        # Apply country-specific multiplier
        train_cost = base_train * pricing_multiplier
        bus_cost = base_bus * pricing_multiplier
        car_cost = base_car * pricing_multiplier
        taxi_cost = base_taxi * pricing_multiplier
        
        # Helper function to format duration hours to string
        def format_duration(hours):
            h = int(hours)
            m = int((hours - h) * 60)
            if h > 0 and m > 0:
                return f"{h}h {m}m"
            elif h > 0:
                return f"{h}h"
            else:
                return f"{m}m"
        
        train_duration = round(duration_hours * 1.1, 1)
        bus_duration = round(duration_hours * 1.2, 1)
        car_duration = round(duration_hours, 1)
        
        return [
            {
                "type": "train",
                "cost_per_trip": round(train_cost, 2),
                "duration_hours": train_duration,
                "duration_str": format_duration(train_duration),
                "distance_km": round(distance_km, 1),
                "description": f"Train service covering {distance_km:.0f} km"
            },
            {
                "type": "bus",
                "cost_per_trip": round(bus_cost, 2),
                "duration_hours": bus_duration,
                "duration_str": format_duration(bus_duration),
                "distance_km": round(distance_km, 1),
                "description": f"Inter-city bus covering {distance_km:.0f} km"
            },
            {
                "type": "car_rental",
                "cost_per_trip": round(car_cost, 2),
                "duration_hours": car_duration,
                "duration_str": format_duration(car_duration),
                "distance_km": round(distance_km, 1),
                "description": f"Self-drive car rental ({distance_km:.0f} km)"
            },
            {
                "type": "private_car",
                "cost_per_trip": round(taxi_cost, 2),
                "duration_hours": car_duration,
                "duration_str": format_duration(car_duration),
                "distance_km": round(distance_km, 1),
                "description": f"Private car/taxi service ({distance_km:.0f} km)"
            }
        ]
    
    async def _calculate_transportation_costs(self, options: Dict[str, Any], request: TravelRequest, has_flights: bool = True) -> Dict[str, Any]:
        trip_duration = self.calculate_trip_duration(request.start_date, request.return_date)
        
        # Airport transfers (arrival and departure) - ONLY for international travel with flights
        airport_transfer_cost = 0
        if has_flights and options.get("airport_transfer"):
            taxi_cost = options["airport_transfer"][0]["cost_per_trip"]
            airport_transfer_cost = taxi_cost * 2 * request.travelers  # Round trip
        
        # Local transportation - use LLM estimator for intelligent calculation
        local_transport_cost = 0
        if self.local_transport_estimator:
            try:
                # Detect country for better estimation
                country = await self._detect_country_for_local(request.destination)
                
                # Use LLM to estimate realistic local transport costs
                local_estimate = await self.local_transport_estimator.estimate_local_transport(
                    destination=request.destination,
                    country=country or "Unknown",
                    num_travelers=request.travelers,
                    trip_duration_days=trip_duration
                )
                local_transport_cost = local_estimate.get("total_cost", 0)
                print(f"   💡 LLM Local Transport: ${local_transport_cost} ({trip_duration} days)")
            except Exception as e:
                print(f"   ⚠️ LLM local transport failed, using fallback: {e}")
                # Fallback to old method
                if options.get("local_transportation"):
                    # More realistic: $4-6 per person per day (not $12!)
                    daily_per_person = 5.0
                    local_transport_cost = daily_per_person * trip_duration * request.travelers
        else:
            # Fallback if no estimator
            if options.get("local_transportation"):
                daily_per_person = 5.0
                local_transport_cost = daily_per_person * trip_duration * request.travelers
        
        # Inter-city transportation - using cheapest option (usually train or bus)
        inter_city_cost = 0
        if options.get("inter_city_transportation") and len(options["inter_city_transportation"]) > 0:
            # Use the cheapest option (first one is usually cheapest after sorting)
            cheapest_option = min(options["inter_city_transportation"], 
                                 key=lambda x: x.get("cost_per_trip", float('inf')))
            cost_per_trip = cheapest_option.get("cost_per_trip", 0)
            
            # Round trip cost (going there and coming back)
            # Note: cost_per_trip already includes all travelers from LLM pricing agent
            inter_city_cost = cost_per_trip * 2
        
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
    
    async def _detect_country(self, city: str) -> str:
        """Detect which country a city is in"""
        try:
            if self.airport_resolver:
                country = await self.airport_resolver.get_country_for_city(city)
                if country:
                    return country
        except Exception as e:
            print(f"Could not detect country for {city}: {e}")
        
        # Fallback - return None if we can't detect
        return None
    
    async def _detect_country_for_local(self, city: str) -> str:
        """Detect country for local transport estimation (alias of _detect_country)"""
        return await self._detect_country(city)
    
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