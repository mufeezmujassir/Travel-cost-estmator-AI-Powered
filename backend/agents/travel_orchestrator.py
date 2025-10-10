import asyncio
from typing import Dict, Any, List
from datetime import datetime
import uuid

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Annotated

from .base_agent import BaseAgent
from .emotional_intelligence_agent import EmotionalIntelligenceAgent
from .flight_search_agent import FlightSearchAgent
from .hotel_search_agent import HotelSearchAgent
from .transportation_agent import TransportationAgent
from .cost_estimation_agent import CostEstimationAgent
from .recommendation_agent import RecommendationAgent

from models.travel_models import TravelRequest, TravelResponse, Flight, Hotel, DayItinerary, CostBreakdown, SeasonRecommendation
from services.config import Settings
from services.domestic_travel_analyzer import TransportationStrategyCache
from services.distance_calculator import DistanceCalculator
from services.airport_resolver import AirportResolver

class TravelState(TypedDict):
    """State for the travel planning workflow"""
    request: TravelRequest
    emotional_analysis: Dict[str, Any]
    flights: List[Flight]
    hotels: List[Hotel]
    transportation: Dict[str, Any]
    cost_breakdown: CostBreakdown
    itinerary: List[DayItinerary]
    recommendations: List[str]
    season_recommendation: SeasonRecommendation
    errors: List[str]
    completed_agents: List[str]
    price_trends: Dict[str, Any]  # Price calendar data
    skip_flight_search: bool  # Whether to skip flight search for domestic travel
    is_domestic_travel: bool  # Whether this is domestic travel
    travel_distance_km: float  # Distance between origin and destination

class TravelOrchestrator:
    """Main orchestrator for coordinating all travel planning agents"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.agents: Dict[str, BaseAgent] = {}
        self.graph = None
        self.initialized = False
        self.strategy_cache = TransportationStrategyCache()
        self.distance_calculator = None
        self.airport_resolver = None
    
    async def initialize(self):
        """Initialize all agents and create the workflow graph"""
        print("🚀 Initializing Travel Orchestrator...")
        
        # Initialize all agents
        self.agents = {
            "emotional_intelligence": EmotionalIntelligenceAgent(self.settings),
            "flight_search": FlightSearchAgent(self.settings),
            "hotel_search": HotelSearchAgent(self.settings),
            "transportation": TransportationAgent(self.settings),
            "cost_estimation": CostEstimationAgent(self.settings),
            "recommendation": RecommendationAgent(self.settings)
        }
        
        # Initialize each agent
        for name, agent in self.agents.items():
            await agent.initialize()
            print(f"✅ {name} agent initialized")
        
        # Initialize domestic travel services
        self.airport_resolver = AirportResolver(self.settings.serp_api_key)
        
        # Get gmaps_client from transportation agent
        transport_agent = self.agents.get("transportation")
        gmaps_client = transport_agent.gmaps_client if hasattr(transport_agent, 'gmaps_client') else None
        self.distance_calculator = DistanceCalculator(self.settings, gmaps_client)
        
        print("✅ Domestic travel analyzer initialized")
        
        # Create the workflow graph
        self._create_workflow_graph()
        
        self.initialized = True
        print("🎯 Travel Orchestrator fully initialized!")
    
    def _create_workflow_graph(self):
        """Create the LangGraph workflow for travel planning with conditional routing"""
        workflow = StateGraph(TravelState)
        
        # Add nodes for each agent
        workflow.add_node("analyze_travel_type", self._analyze_travel_type)
        workflow.add_node("emotional_intelligence", self._run_emotional_intelligence_agent)
        workflow.add_node("flight_search", self._run_flight_search_agent)
        workflow.add_node("hotel_search", self._run_hotel_search_agent)
        workflow.add_node("transportation_node", self._run_transportation_agent)
        workflow.add_node("cost_estimation", self._run_cost_estimation_agent)
        workflow.add_node("recommendation", self._run_recommendation_agent)
        workflow.add_node("finalize", self._finalize_travel_plan)
        
        # Define the workflow edges with conditional routing
        workflow.set_entry_point("analyze_travel_type")
        
        # Analyze travel type first
        workflow.add_edge("analyze_travel_type", "emotional_intelligence")
        
        # After emotional intelligence, conditionally route based on travel type
        workflow.add_conditional_edges(
            "emotional_intelligence",
            self._route_after_emotional_intelligence,
            {
                "flight_search": "flight_search",
                "hotel_search": "hotel_search"
            }
        )
        
        # Flight search routes to hotel search
        workflow.add_edge("flight_search", "hotel_search")
        
        # Hotel search routes to transportation
        workflow.add_edge("hotel_search", "transportation_node")
        
        # Transportation runs after hotels
        workflow.add_edge("transportation_node", "cost_estimation")
        
        # Cost estimation runs after transportation
        workflow.add_edge("cost_estimation", "recommendation")
        
        # Recommendation runs last
        workflow.add_edge("recommendation", "finalize")
        
        # Finalize ends the workflow
        workflow.add_edge("finalize", END)
        
        # Compile the graph
        self.graph = workflow.compile()
    
    async def process_travel_request(self, request: TravelRequest) -> TravelResponse:
        """Process a travel request through all agents"""
        if not self.initialized:
            raise RuntimeError("Orchestrator not initialized")
        
        print(f"🎯 Processing travel request: {request.origin} → {request.destination}")
        
        # Create initial state
        initial_state = TravelState(
            request=request,
            emotional_analysis={},
            flights=[],
            hotels=[],
            transportation={},
            cost_breakdown=CostBreakdown(),
            itinerary=[],
            recommendations=[],
            season_recommendation=SeasonRecommendation(
                current_season="unknown",
                optimal_season="unknown",
                is_optimal=False,
                recommendation=""
            ),
            errors=[],
            completed_agents=[],
            price_trends={},  # Initialize price trends
            skip_flight_search=False,  # Initialize domestic travel flags
            is_domestic_travel=False,
            travel_distance_km=0.0
        )
        
        # Run the workflow
        try:
            final_state = await self.graph.ainvoke(initial_state)
            
            # Create the response
            response = self._create_travel_response(final_state)
            
            print("✅ Travel request processed successfully")
            return response
            
        except Exception as e:
            print(f"❌ Error processing travel request: {e}")
            raise
    
    async def _analyze_travel_type(self, state: TravelState) -> TravelState:
        """Analyze travel type to determine if flight search should be skipped"""
        print("🔍 Analyzing travel type (domestic vs international)...")
        
        try:
            request = state["request"]
            
            # Get airport codes for both origin and destination
            origin_airport = await self.airport_resolver.get_airport_code(request.origin)
            dest_airport = await self.airport_resolver.get_airport_code(request.destination)
            
            print(f"   Origin: {request.origin} → {origin_airport}")
            print(f"   Destination: {request.destination} → {dest_airport}")
            
            # Case 1: Same airport code (e.g., Galle and Colombo both = CMB)
            if origin_airport == dest_airport and origin_airport != "UNKNOWN":
                state["skip_flight_search"] = True
                state["is_domestic_travel"] = True
                state["travel_distance_km"] = 0.0
                print(f"✅ Same airport detected ({origin_airport}) - Skipping flight search")
                print(f"   This is domestic ground travel within the same region")
                return state
            
            # Case 2: Different airports - check distance and country
            if origin_airport != "UNKNOWN" and dest_airport != "UNKNOWN":
                # Detect countries
                origin_country = await self.airport_resolver.get_country_for_city(request.origin)
                dest_country = await self.airport_resolver.get_country_for_city(request.destination)
                
                print(f"   Origin Country: {origin_country}")
                print(f"   Destination Country: {dest_country}")
                
                # Calculate distance
                distance = await self.distance_calculator.calculate_distance(
                    request.origin,
                    request.destination
                )
                
                if distance:
                    state["travel_distance_km"] = distance
                    print(f"   Distance: {distance:.1f} km")
                    
                    # Check if same country
                    if origin_country and dest_country and origin_country.lower() == dest_country.lower():
                        state["is_domestic_travel"] = True
                        
                        # Get country-specific transportation strategy
                        strategy = await self.strategy_cache.get_strategy(origin_country, self.settings)
                        max_ground_distance = strategy.get("max_ground_distance_km", 300)
                        
                        # Decide whether to skip flight search
                        if distance <= max_ground_distance:
                            state["skip_flight_search"] = True
                            print(f"✅ Domestic travel within {origin_country}")
                            print(f"   Distance ({distance:.1f} km) ≤ Max ground distance ({max_ground_distance} km)")
                            print(f"   Skipping flight search - Ground transport recommended")
                        else:
                            state["skip_flight_search"] = False
                            print(f"✅ Domestic travel within {origin_country}")
                            print(f"   Distance ({distance:.1f} km) > Max ground distance ({max_ground_distance} km)")
                            print(f"   Including flight search - Long distance requires air travel")
                    else:
                        # International travel
                        state["is_domestic_travel"] = False
                        state["skip_flight_search"] = False
                        print(f"✅ International travel detected")
                        print(f"   From {origin_country} to {dest_country}")
                        print(f"   Including flight search")
                else:
                    # Could not calculate distance, default to including flights
                    state["skip_flight_search"] = False
                    state["is_domestic_travel"] = False
                    print(f"⚠️ Could not calculate distance - Including flight search by default")
            else:
                # Could not resolve airports, default to including flights
                state["skip_flight_search"] = False
                state["is_domestic_travel"] = False
                print(f"⚠️ Could not resolve airports - Including flight search by default")
            
            state["completed_agents"].append("travel_type_analyzer")
            
        except Exception as e:
            error_msg = f"Travel type analysis error: {str(e)}"
            state["errors"].append(error_msg)
            print(f"❌ {error_msg}")
            # Default to including flight search on error
            state["skip_flight_search"] = False
            state["is_domestic_travel"] = False
        
        return state
    
    def _route_after_emotional_intelligence(self, state: TravelState) -> str:
        """Determine routing after emotional intelligence based on travel type"""
        if state.get("skip_flight_search", False):
            print("🔀 Routing: Skipping flight search → Going to hotel search")
            return "hotel_search"
        else:
            print("🔀 Routing: Including flight search")
            return "flight_search"
    
    async def _run_emotional_intelligence_agent(self, state: TravelState) -> TravelState:
        """Run the emotional intelligence agent"""
        print("🧠 Running Emotional Intelligence Agent...")
        
        try:
            agent = self.agents["emotional_intelligence"]
            response = await agent.execute_with_timeout(state["request"])
            
            if response.success:
                state["emotional_analysis"] = response.data
                state["completed_agents"].append("emotional_intelligence")
                print("✅ Emotional Intelligence Agent completed")
            else:
                state["errors"].append(f"Emotional Intelligence Agent failed: {response.error}")
                print(f"❌ Emotional Intelligence Agent failed: {response.error}")
            
        except Exception as e:
            error_msg = f"Emotional Intelligence Agent error: {str(e)}"
            state["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        return state
    
    async def _run_flight_search_agent(self, state: TravelState) -> TravelState:
        """Run the flight search agent"""
        print("✈️ Running Flight Search Agent...")
        
        try:
            agent = self.agents["flight_search"]
            context = {
                "emotional_intelligence": state["emotional_analysis"],
                "include_price_trends": state["request"].include_price_trends
            }
            response = await agent.execute_with_timeout(state["request"], context)
            
            if response.success:
                flights_data = response.data.get("flights", [])
                state["flights"] = [Flight(**flight) for flight in flights_data]
                
                # Store price trends if available
                if "price_trends" in response.data:
                    if "price_trends" not in state:
                        state["price_trends"] = {}
                    state["price_trends"] = response.data["price_trends"]
                
                state["completed_agents"].append("flight_search")
                print("✅ Flight Search Agent completed")
            else:
                state["errors"].append(f"Flight Search Agent failed: {response.error}")
                print(f"❌ Flight Search Agent failed: {response.error}")
            
        except Exception as e:
            error_msg = f"Flight Search Agent error: {str(e)}"
            state["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        return state
    
    async def _run_hotel_search_agent(self, state: TravelState) -> TravelState:
        """Run the hotel search agent"""
        print("🏨 Running Hotel Search Agent...")
        
        try:
            agent = self.agents["hotel_search"]
            context = {
                "emotional_intelligence": state["emotional_analysis"],
                "flight_search_agent": {"data": {"flights": [flight.dict() for flight in state["flights"]]}}
            }
            response = await agent.execute_with_timeout(state["request"], context)
            
            if response.success:
                hotels_data = response.data.get("hotels", [])
                state["hotels"] = [Hotel(**hotel) for hotel in hotels_data]
                
                state["completed_agents"].append("hotel_search")
                print("✅ Hotel Search Agent completed")
            else:
                state["errors"].append(f"Hotel Search Agent failed: {response.error}")
                print(f"❌ Hotel Search Agent failed: {response.error}")
            
        except Exception as e:
            error_msg = f"Hotel Search Agent error: {str(e)}"
            state["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        return state
    
    async def _run_transportation_agent(self, state: TravelState) -> TravelState:
        """Run the transportation agent"""
        print("🚗 Running Transportation Agent...")
        
        try:
            agent = self.agents["transportation"]
            context = {
                "emotional_intelligence": state["emotional_analysis"],
                "flight_search_agent": {"data": {"flights": [flight.dict() for flight in state["flights"]]}},
                "hotel_search_agent": {"data": {"hotels": [hotel.dict() for hotel in state["hotels"]]}}
            }
            response = await agent.execute_with_timeout(state["request"], context)
            
            if response.success:
                state["transportation"] = response.data
                state["completed_agents"].append("transportation")
                print("✅ Transportation Agent completed")
            else:
                state["errors"].append(f"Transportation Agent failed: {response.error}")
                print(f"❌ Transportation Agent failed: {response.error}")
            
        except Exception as e:
            error_msg = f"Transportation Agent error: {str(e)}"
            state["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        return state
    
    async def _run_cost_estimation_agent(self, state: TravelState) -> TravelState:
        """Run the cost estimation agent"""
        print("💰 Running Cost Estimation Agent...")
        
        try:
            agent = self.agents["cost_estimation"]
            context = {
                "emotional_intelligence": state["emotional_analysis"],
                "flight_search_agent": {"data": {"flights": [flight.dict() for flight in state["flights"]]}},
                "hotel_search_agent": {"data": {"hotels": [hotel.dict() for hotel in state["hotels"]]}},
                "transportation_agent": state["transportation"]
            }
            response = await agent.execute_with_timeout(state["request"], context)
            
            if response.success:
                cost_data = response.data.get("cost_breakdown", {})
                state["cost_breakdown"] = CostBreakdown(**cost_data)
                state["completed_agents"].append("cost_estimation")
                print("✅ Cost Estimation Agent completed")
            else:
                state["errors"].append(f"Cost Estimation Agent failed: {response.error}")
                print(f"❌ Cost Estimation Agent failed: {response.error}")
            
        except Exception as e:
            error_msg = f"Cost Estimation Agent error: {str(e)}"
            state["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        return state
    
    async def _run_recommendation_agent(self, state: TravelState) -> TravelState:
        """Run the recommendation agent"""
        print("🎯 Running Recommendation Agent...")
        
        try:
            agent = self.agents["recommendation"]
            context = {
                "emotional_intelligence": state["emotional_analysis"],
                "flight_search_agent": {"data": {"flights": [flight.dict() for flight in state["flights"]]}},
                "hotel_search_agent": {"data": {"hotels": [hotel.dict() for hotel in state["hotels"]]}},
                "transportation_agent": state["transportation"],
                "cost_estimation_agent": {"data": {"cost_breakdown": state["cost_breakdown"].dict()}}
            }
            response = await agent.execute_with_timeout(state["request"], context)
            
            if response.success:
                itinerary_data = response.data.get("itinerary", [])
                state["itinerary"] = [DayItinerary(**day) for day in itinerary_data]
                state["recommendations"] = response.data.get("recommendations", [])
                state["completed_agents"].append("recommendation")
                print("✅ Recommendation Agent completed")
            else:
                state["errors"].append(f"Recommendation Agent failed: {response.error}")
                print(f"❌ Recommendation Agent failed: {response.error}")
            
        except Exception as e:
            error_msg = f"Recommendation Agent error: {str(e)}"
            state["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        return state
    
    async def _finalize_travel_plan(self, state: TravelState) -> TravelState:
        """Finalize the travel plan and create season recommendation"""
        print("🎉 Finalizing travel plan...")
        
        try:
            # Create season recommendation
            current_season = self._get_season_from_date(state["request"].start_date)
            optimal_seasons = self._get_optimal_seasons_for_vibe(state["request"].vibe)
            is_optimal = current_season in optimal_seasons
            
            state["season_recommendation"] = SeasonRecommendation(
                current_season=current_season,
                optimal_season=optimal_seasons[0] if optimal_seasons else current_season,
                is_optimal=is_optimal,
                recommendation=self._get_season_recommendation_message(
                    state["request"].vibe, current_season, optimal_seasons
                ),
                alternative_months=self._get_alternative_months(optimal_seasons),
                weather_considerations=self._get_weather_considerations(current_season)
            )
            
            print("✅ Travel plan finalized")
            
        except Exception as e:
            error_msg = f"Finalization error: {str(e)}"
            state["errors"].append(error_msg)
            print(f"❌ {error_msg}")
        
        return state
    
    def _create_travel_response(self, state: TravelState) -> TravelResponse:
        """Create the final travel response"""
        total_cost = sum([
            state["cost_breakdown"].flights,
            state["cost_breakdown"].accommodation,
            state["cost_breakdown"].transportation,
            state["cost_breakdown"].activities,
            state["cost_breakdown"].food,
            state["cost_breakdown"].miscellaneous
        ])
        
        return TravelResponse(
            request_id=str(uuid.uuid4()),
            flights=state["flights"],
            hotels=state["hotels"],
            itinerary=state["itinerary"],
            cost_breakdown=state["cost_breakdown"],
            total_cost=total_cost,
            season_recommendation=state["season_recommendation"],
            recommendations=state["recommendations"],
            vibe_analysis=state["emotional_analysis"],
            price_trends=state.get("price_trends") if state.get("price_trends") else None,
            transportation=state.get("transportation"),  # Include transportation data
            is_domestic_travel=state.get("is_domestic_travel", False),  # Include domestic travel flag
            travel_distance_km=state.get("travel_distance_km", 0.0),  # Include distance
            generated_at=datetime.now()
        )
    
    def _get_season_from_date(self, date_str: str) -> str:
        """Get season from date string"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            month = date_obj.month
            
            if month in [12, 1, 2]:
                return "winter"
            elif month in [3, 4, 5]:
                return "spring"
            elif month in [6, 7, 8]:
                return "summer"
            else:
                return "autumn"
        except:
            return "unknown"
    
    def _get_optimal_seasons_for_vibe(self, vibe) -> List[str]:
        """Get optimal seasons for a vibe"""
        optimal_seasons = {
            "romantic": ["spring", "autumn"],
            "adventure": ["summer", "autumn"],
            "beach": ["summer"],
            "nature": ["spring", "autumn"],
            "cultural": ["autumn", "spring"],
            "culinary": ["autumn", "spring"],
            "wellness": ["winter", "spring"]
        }
        return optimal_seasons.get(vibe.value, ["spring", "summer", "autumn"])
    
    def _get_season_recommendation_message(self, vibe, current_season: str, optimal_seasons: List[str]) -> str:
        """Get season recommendation message"""
        if current_season in optimal_seasons:
            return f"Perfect timing! {current_season.title()} is ideal for {vibe.value} experiences."
        else:
            return f"Consider visiting in {optimal_seasons[0]} for the best {vibe.value} experience, but {current_season} can still be enjoyable."
    
    def _get_alternative_months(self, optimal_seasons: List[str]) -> List[int]:
        """Get alternative months for optimal seasons"""
        season_months = {
            "winter": [12, 1, 2],
            "spring": [3, 4, 5],
            "summer": [6, 7, 8],
            "autumn": [9, 10, 11]
        }
        
        months = []
        for season in optimal_seasons:
            months.extend(season_months.get(season, []))
        
        return sorted(list(set(months)))
    
    def _get_weather_considerations(self, season: str) -> List[str]:
        """Get weather considerations for season"""
        considerations = {
            "winter": ["Pack warm clothing", "Check for snow conditions", "Book indoor activities"],
            "spring": ["Pack layers", "Expect occasional rain", "Enjoy blooming flowers"],
            "summer": ["Stay hydrated", "Use sunscreen", "Book air-conditioned activities"],
            "autumn": ["Pack warm layers", "Enjoy fall colors", "Check for seasonal closures"]
        }
        return considerations.get(season, ["Check local weather forecast"])
    
    async def get_season_recommendation(self, vibe: str, destination: str, start_date: str) -> Dict[str, Any]:
        """Get season recommendation for a specific vibe and destination"""
        try:
            current_season = self._get_season_from_date(start_date)
            
            # Create a mock vibe object
            class MockVibe:
                def __init__(self, value):
                    self.value = value
            
            mock_vibe = MockVibe(vibe)
            optimal_seasons = self._get_optimal_seasons_for_vibe(mock_vibe)
            is_optimal = current_season in optimal_seasons
            
            return {
                "current_season": current_season,
                "optimal_season": optimal_seasons[0] if optimal_seasons else current_season,
                "is_optimal": is_optimal,
                "recommendation": self._get_season_recommendation_message(mock_vibe, current_season, optimal_seasons),
                "alternative_months": self._get_alternative_months(optimal_seasons),
                "weather_considerations": self._get_weather_considerations(current_season)
            }
            
        except Exception as e:
            return {
                "error": f"Failed to get season recommendation: {str(e)}"
            }
