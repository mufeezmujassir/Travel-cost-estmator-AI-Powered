import asyncio
import httpx
from typing import Dict, Any,List
import json
import re
from datetime import datetime
from .base_agent import BaseAgent
from models.travel_models import TravelRequest, Flight
from services.serp_service import SerpService
from services.price_calendar import PriceCalendar

class FlightSearchAgent(BaseAgent):
    """Agent responsible for finding and analyzing flight options"""
    
    def __init__(self, settings):
        super().__init__("Flight Search Agent", settings)
        self.serp_service = None
        self.price_calendar = None
    
    async def initialize(self):
        """Initialize the flight search agent"""
        await super().initialize()
        self.serp_service = SerpService(self.settings)
        await self.serp_service.initialize()
        self.price_calendar = PriceCalendar(self.serp_service)
    
    async def process(self, request: TravelRequest, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Search for flight options with optional price trend analysis"""
        try:
            self.validate_request(request)
            
            # Search for flights using SERP API
            flights_data = await self._search_flights(request)
            
            # Process and rank flights
            processed_flights = await self._process_flight_data(flights_data, request)
            
            # Select best options
            best_flights = self._select_best_flights(processed_flights, request)
            
            # Check if price trend analysis is requested
            include_price_trends = context and context.get("include_price_trends", False)
            price_analysis = None
            
            if include_price_trends:
                print("📊 Generating price calendar analysis...")
                price_analysis = await self.get_price_trends(request)
            
            result = {
                "flights": [flight.dict() for flight in best_flights],
                "total_options_found": len(processed_flights),
                "search_criteria": {
                    "origin": request.origin,
                    "destination": request.destination,
                    "departure_date": request.start_date,
                    "return_date": request.return_date,
                    "travelers": request.travelers
                }
            }
            
            if price_analysis:
                result["price_trends"] = price_analysis
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    async def get_price_trends(self, request: TravelRequest) -> Dict[str, Any]:
        """Get price trend analysis for flexible dates"""
        try:
            # Get airport codes
            departure_id = await self.serp_service.get_airport_code(request.origin)
            arrival_id = await self.serp_service.get_airport_code(request.destination)
            
            if departure_id == "UNKNOWN" or arrival_id == "UNKNOWN":
                return {"error": "Could not resolve airport codes"}
            
            # Calculate trip duration
            start = datetime.strptime(request.start_date, "%Y-%m-%d")
            end = datetime.strptime(request.return_date, "%Y-%m-%d")
            duration = (end - start).days
            
            # Get price trends
            trends = await self.price_calendar.get_price_trends(
                origin=departure_id,
                destination=arrival_id,
                target_date=request.start_date,
                duration_days=duration,
                search_window_days=7  # Check ±7 days
            )
            
            return trends
            
        except Exception as e:
            print(f"Error getting price trends: {e}")
            return {"error": str(e)}
    
    async def _search_flights(self, request: TravelRequest) -> List[Dict[str, Any]]:
        """Search for flights using SERP API"""
        try:
            departure_id = await self.serp_service.get_airport_code(request.origin)
            arrival_id = await self.serp_service.get_airport_code(request.destination)
            if departure_id == "UNKNOWN" or arrival_id == "UNKNOWN":
                return []
            return await self.serp_service.search_flights(
                origin=departure_id,
                destination=arrival_id,
                departure_date=request.start_date,
                return_date=request.return_date,
                travelers=request.travelers,
            )
        except Exception as e:
            print(f"Error searching flights: {e}")
            return []
    
    async def _process_flight_data(self, flights_data: List[Dict[str, Any]], request: TravelRequest) -> List[Flight]:
        """Process raw flight data into Flight objects"""
        processed_flights = []
        
        for flight_data in flights_data:
            try:
                flight = Flight(
                    airline=flight_data.get("airline", "Unknown"),
                    flight_number=flight_data.get("flight_number", "N/A"),
                    departure_time=flight_data.get("departure_time", "N/A"),
                    arrival_time=flight_data.get("arrival_time", "N/A"),
                    departure_airport=flight_data.get("departure_airport", "N/A"),
                    arrival_airport=flight_data.get("arrival_airport", "N/A"),
                    duration=flight_data.get("duration", "N/A"),
                    class_type=flight_data.get("class_type", "Economy"),
                    price=flight_data.get("price", 0.0) * request.travelers,
                    stops=flight_data.get("stops", 0),
                    aircraft=flight_data.get("aircraft")
                )
                processed_flights.append(flight)
            except Exception as e:
                print(f"Error processing flight data: {e}")
                continue
        
        return processed_flights
    
    def _select_best_flights(self, flights: List[Flight], request: TravelRequest) -> List[Flight]:
        """Select the best flight options - prioritize price with minor stop penalty"""
        if not flights:
            return []
        
        # Sort by price with small penalty for stops
        def flight_sort_key(flight: Flight) -> float:
            # Base price
            price = flight.price
            
            # Add small penalty for each stop ($50 per stop)
            # This way a 1-stop flight that's $200 cheaper will still rank higher
            stops_penalty = flight.stops * 50
            
            return price + stops_penalty
        
        # Sort flights by adjusted price (cheapest first)
        sorted_flights = sorted(flights, key=flight_sort_key)
        
        # Return top 10 options (increased from 3 to give users more choices)
        return sorted_flights[:10]