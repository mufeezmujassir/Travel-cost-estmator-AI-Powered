import asyncio
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent
from models.travel_models import TravelRequest, CostBreakdown, VibeType
from services.grok_service import GrokService

class CostEstimationAgent(BaseAgent):
    """Agent responsible for comprehensive cost estimation and budget analysis"""
    
    def __init__(self, settings):
        super().__init__("Cost Estimation Agent", settings)
        self.grok_service = None
    
    async def initialize(self):
        """Initialize the cost estimation agent"""
        await super().initialize()
        self.grok_service = GrokService(self.settings)
        await self.grok_service.initialize()
    
    async def process(self, request: TravelRequest, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Estimate comprehensive travel costs"""
        try:
            self.validate_request(request)
            
            # Get cost data from other agents
            agent_data = context or {}
            
            # Calculate cost breakdown
            cost_breakdown = await self._calculate_cost_breakdown(request, agent_data)
            
            # Analyze budget vs estimated costs
            budget_analysis = await self._analyze_budget(request, cost_breakdown)
            
            # Get cost optimization suggestions
            optimization_suggestions = await self._get_cost_optimization_suggestions(request, cost_breakdown)
            
            # Calculate total cost
            total_cost = round(sum([
                cost_breakdown.flights,
                cost_breakdown.accommodation,
                cost_breakdown.transportation,
                cost_breakdown.activities,
                cost_breakdown.food,
                cost_breakdown.miscellaneous
            ]), 2)
            
            return {
                "cost_breakdown": cost_breakdown.dict(),
                "total_cost": total_cost,
                "budget_analysis": budget_analysis,
                "optimization_suggestions": optimization_suggestions,
                "cost_per_person": round(total_cost / request.travelers, 2) if request.travelers > 0 else 0
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _calculate_cost_breakdown(self, request: TravelRequest, agent_data: Dict[str, Any]) -> CostBreakdown:
        """Calculate detailed cost breakdown"""
        trip_duration = self.calculate_trip_duration(request.start_date, request.return_date)
        
        # Flight costs - use the cheapest flight
        flights_cost = 0
        if "flight_search_agent" in agent_data:
            flights_data = agent_data["flight_search_agent"].get("data", {})
            flights = flights_data.get("flights", [])
            if flights:
                # Find the cheapest flight by price
                cheapest_flight = min(flights, key=lambda x: x.get("price", float('inf')))
                # Price is already total for all travelers (multiplied in FlightSearchAgent)
                flights_cost = cheapest_flight.get("price", 0)
        
        # Accommodation costs
        accommodation_cost = 0
        if "hotel_search_agent" in agent_data:
            hotels_data = agent_data["hotel_search_agent"].get("data", {})
            hotels = hotels_data.get("hotels", [])
            if hotels:
                price_per_night = hotels[0].get("price_per_night", 0)
                # Calculate rooms needed - assume 2 travelers share 1 room
                # 1 traveler = 1 room, 2 travelers = 1 room, 3 travelers = 2 rooms, etc.
                rooms_needed = (request.travelers + 1) // 2
                accommodation_cost = price_per_night * trip_duration * rooms_needed
        
        # Transportation costs
        transportation_cost = 0
        if "transportation_agent" in agent_data:
            transport_data = agent_data["transportation_agent"]
            transportation_cost = transport_data.get("total_transportation_cost", 0)
        
        # Activities costs (estimated based on vibe and destination)
        activities_cost = await self._estimate_activities_cost(request, trip_duration)
        
        # Food costs (estimated based on destination and vibe)
        food_cost = await self._estimate_food_cost(request, trip_duration)
        
        # Miscellaneous costs
        miscellaneous_cost = await self._estimate_miscellaneous_cost(request, trip_duration)
        
        return CostBreakdown(
            flights=round(flights_cost, 2),
            accommodation=round(accommodation_cost, 2),
            transportation=round(transportation_cost, 2),
            activities=round(activities_cost, 2),
            food=round(food_cost, 2),
            miscellaneous=round(miscellaneous_cost, 2)
        )
    
    async def _estimate_activities_cost(self, request: TravelRequest, trip_duration: int) -> float:
        """Estimate activities cost using SERP activities search and vibe"""
        try:
            from services.serp_service import SerpService
            serp = SerpService(self.settings)
            await serp.initialize()
            activities = await serp.search_activities(destination=request.destination, vibe=request.vibe.value)
            avg_activity_price = 40.0
            return avg_activity_price * trip_duration * request.travelers
        except Exception:
            return 35.0 * trip_duration * request.travelers

    async def _estimate_food_cost(self, request: TravelRequest, trip_duration: int) -> float:
        destination_lower = request.destination.lower()
        if any(city in destination_lower for city in ["zurich", "oslo", "tokyo", "new york", "paris"]):
            per_person_per_day = 60.0
        elif any(city in destination_lower for city in ["colombo", "bangkok", "hanoi", "mexico", "lisbon"]):
            per_person_per_day = 25.0
        else:
            per_person_per_day = 35.0
        return per_person_per_day * trip_duration * request.travelers

    async def _estimate_miscellaneous_cost(self, request: TravelRequest, trip_duration: int) -> float:
        return 10.0 * trip_duration * request.travelers

    async def _analyze_budget(self, request: TravelRequest, cost_breakdown: CostBreakdown) -> Dict[str, Any]:
        total_cost = sum([
            cost_breakdown.flights,
            cost_breakdown.accommodation,
            cost_breakdown.transportation,
            cost_breakdown.activities,
            cost_breakdown.food,
            cost_breakdown.miscellaneous,
        ])
        budget = request.budget or 0.0
        remaining = budget - total_cost
        return {
            "budget_provided": budget > 0,
            "budget": budget,
            "estimated_total_cost": total_cost,
            "difference": remaining,
            "within_budget": remaining >= 0,
            "per_person_cost": total_cost / request.travelers if request.travelers > 0 else total_cost,
        }

    async def _get_cost_optimization_suggestions(self, request: TravelRequest, cost_breakdown: CostBreakdown) -> List[str]:
        suggestions: List[str] = []
        if cost_breakdown.flights > 0:
            suggestions.append("Check alternate airports and flexible dates for cheaper flights")
        if cost_breakdown.accommodation > 0:
            suggestions.append("Consider neighborhoods outside the center or apartments for groups")
        if cost_breakdown.transportation > 0:
            suggestions.append("Use public transport passes instead of taxis where possible")
        if cost_breakdown.activities > 0:
            suggestions.append("Prioritize free/low-cost attractions and city passes")
        if cost_breakdown.food > 0:
            suggestions.append("Mix restaurants with markets and takeaways to save")
        suggestions.append("Book early and bundle where possible to secure discounts")
        return suggestions