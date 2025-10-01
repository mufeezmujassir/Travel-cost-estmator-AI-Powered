import asyncio
import httpx
from typing import Dict, Any,List
import json
import re
from .base_agent import BaseAgent
from models.travel_models import TravelRequest, Flight
from services.serp_service import SerpService

class FlightSearchAgent(BaseAgent):
    """Agent responsible for finding and analyzing flight options"""
    
    def __init__(self, settings):
        super().__init__("Flight Search Agent", settings)
        self.serp_service = None
    
    async def initialize(self):
        """Initialize the flight search agent"""
        await super().initialize()
        self.serp_service = SerpService(self.settings)
        await self.serp_service.initialize()
    
    async def process(self, request: TravelRequest, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Search for flight options"""
        try:
            self.validate_request(request)
            
            # Search for flights using SERP API
            flights_data = await self._search_flights(request)
            
            # Process and rank flights
            processed_flights = await self._process_flight_data(flights_data, request)
            
            # Select best options
            best_flights = self._select_best_flights(processed_flights, request)
            
            return {
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
            
        except Exception as e:
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
        """Select the best flight options based on criteria"""
        if not flights:
            return []
        
        # Sort by price and other factors
        def flight_score(flight: Flight) -> float:
            price_score = 1.0 / (flight.price + 1)
            
            stops_score = 1.0 / (flight.stops + 1)
            
            return price_score * 0.7 + stops_score * 0.3
        
        # Sort flights by score
        sorted_flights = sorted(flights, key=flight_score, reverse=True)
        
        # Return top 3 options
        return sorted_flights[:3]