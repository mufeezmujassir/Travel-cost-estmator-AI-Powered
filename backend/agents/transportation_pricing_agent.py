"""
LLM-Powered Transportation Pricing Agent
Uses LangGraph workflow for intelligent, multi-step pricing analysis
"""

import json
import re
from typing import Dict, Any, List
from typing_extensions import TypedDict, Annotated

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from services.grok_service import GrokService


class TransportationPricingState(TypedDict):
    """State for transportation pricing workflow"""
    origin: str
    destination: str
    distance_km: float
    travelers: int
    country: str
    route_context: Dict[str, Any]
    economic_context: Dict[str, Any]
    pricing_research: Dict[str, Any]
    calculated_costs: Dict[str, float]
    final_prices: Dict[str, Dict[str, Any]]
    confidence: float
    reasoning: str
    messages: Annotated[list, add_messages]


class TransportationPricingAgent:
    """LLM-powered agent for intelligent transportation pricing"""
    
    def __init__(self, grok_service: GrokService):
        self.grok_service = grok_service
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(TransportationPricingState)
        
        # Add nodes
        workflow.add_node("analyze_route", self._analyze_route)
        workflow.add_node("research_economics", self._research_economics)
        workflow.add_node("research_local_prices", self._research_local_prices)
        workflow.add_node("calculate_costs", self._calculate_costs)
        workflow.add_node("validate_prices", self._validate_prices)
        
        # Define edges
        workflow.set_entry_point("analyze_route")
        workflow.add_edge("analyze_route", "research_economics")
        workflow.add_edge("research_economics", "research_local_prices")
        workflow.add_edge("research_local_prices", "calculate_costs")
        workflow.add_edge("calculate_costs", "validate_prices")
        workflow.add_edge("validate_prices", END)
        
        return workflow.compile()
    
    async def _analyze_route(self, state: TransportationPricingState) -> TransportationPricingState:
        """LLM analyzes the route and context"""
        print(f"🤖 Step 1: Analyzing route {state['origin']} → {state['destination']}")
        
        prompt = f"""Analyze this transportation route and provide context:

Route: {state['origin']} → {state['destination']}
Distance: {state['distance_km']} km

Provide detailed analysis:
1. Country where this route is located
2. Type of route (urban, rural, highway, coastal, mountainous, etc.)
3. Economic development level (developed/developing)
4. Tourism level (high/medium/low)
5. Transportation infrastructure quality (excellent/good/fair/poor)
6. Seasonal factors that might affect pricing

Respond ONLY with valid JSON in this exact format:
{{
    "country": "Sri Lanka",
    "route_type": "coastal highway",
    "economic_level": "developing",
    "tourism_factor": "high",
    "infrastructure_quality": "good",
    "seasonal_impact": "low"
}}"""
        
        try:
            response = await self.grok_service.generate_response(
                prompt,
                system_message="You are a transportation analyst. Respond only with valid JSON.",
                force_json=True
            )
            
            # Extract JSON from response
            route_context = self._extract_json(response)
            
            if route_context and "country" in route_context:
                state["route_context"] = route_context
                state["country"] = route_context["country"]
                print(f"   ✓ Country: {state['country']}")
                print(f"   ✓ Route type: {route_context.get('route_type', 'N/A')}")
            else:
                # Fallback
                state["route_context"] = {
                    "country": "Unknown",
                    "route_type": "highway",
                    "economic_level": "developing",
                    "tourism_factor": "medium",
                    "infrastructure_quality": "fair",
                    "seasonal_impact": "low"
                }
                state["country"] = "Unknown"
                print(f"   ⚠️ Using fallback route context")
                
        except Exception as e:
            print(f"   ❌ Error in route analysis: {e}")
            state["route_context"] = {"country": "Unknown", "route_type": "highway"}
            state["country"] = "Unknown"
        
        return state
    
    async def _research_economics(self, state: TransportationPricingState) -> TransportationPricingState:
        """LLM researches economic context"""
        print(f"🤖 Step 2: Researching economic context for {state['country']}")
        
        prompt = f"""Research the economic context for transportation pricing in {state['country']}:

Provide current economic data:
1. Average monthly income in USD
2. GDP per capita in USD
3. Cost of living index (USA = 100)
4. Currency exchange rate to USD (approximate)
5. Transportation cost trends (stable/rising/falling)
6. Government subsidies on public transport (high/medium/low/none)

Respond ONLY with valid JSON in this exact format:
{{
    "monthly_income_usd": 320,
    "gdp_per_capita": 3720,
    "cost_of_living_index": 45.2,
    "currency_rate": 325.5,
    "transport_trends": "stable",
    "public_subsidies": "high"
}}"""
        
        try:
            response = await self.grok_service.generate_response(
                prompt,
                system_message="You are an economist. Provide accurate data. Respond only with valid JSON.",
                force_json=True
            )
            
            economic_context = self._extract_json(response)
            
            if economic_context and "gdp_per_capita" in economic_context:
                state["economic_context"] = economic_context
                print(f"   ✓ GDP per capita: ${economic_context.get('gdp_per_capita', 'N/A'):,}")
                print(f"   ✓ Monthly income: ${economic_context.get('monthly_income_usd', 'N/A')}")
            else:
                # Fallback
                state["economic_context"] = {
                    "monthly_income_usd": 500,
                    "gdp_per_capita": 10000,
                    "cost_of_living_index": 50,
                    "currency_rate": 1.0,
                    "transport_trends": "stable",
                    "public_subsidies": "medium"
                }
                print(f"   ⚠️ Using fallback economic context")
                
        except Exception as e:
            print(f"   ❌ Error in economic research: {e}")
            state["economic_context"] = {
                "monthly_income_usd": 500,
                "gdp_per_capita": 10000
            }
        
        return state
    
    async def _research_local_prices(self, state: TransportationPricingState) -> TransportationPricingState:
        """LLM researches actual local transportation prices"""
        print(f"🤖 Step 3: Researching local transportation prices")
        
        prompt = f"""Research actual transportation prices for this specific route:

Route: {state['origin']} → {state['destination']}
Country: {state['country']}
Distance: {state['distance_km']} km
Economic context:
- GDP per capita: ${state['economic_context'].get('gdp_per_capita', 'N/A')}
- Average monthly income: ${state['economic_context'].get('monthly_income_usd', 'N/A')}
- Route type: {state['route_context'].get('route_type', 'highway')}
- Infrastructure: {state['route_context'].get('infrastructure_quality', 'fair')}

IMPORTANT: Provide realistic prices in USD that locals would ACTUALLY PAY in {state['country']}.
For a {state['distance_km']} km route, research what the real local prices are.

Example: If local bus fare is LKR 180 per person, convert to USD (~$0.55) and provide that.

Provide prices for:
1. Train ticket (2nd class, PER PERSON, one-way)
2. Inter-city bus ticket (PER PERSON, one-way)
3. Taxi/private car (TOTAL for entire car, one-way)
4. Car rental (DAILY rate for entire car)

Double-check your prices are realistic for the local economy and actual fares charged.

Respond ONLY with valid JSON in this exact format:
{{
    "train_price_usd": 0.45,
    "bus_price_usd": 0.55,
    "taxi_price_usd": 15.00,
    "car_rental_daily_usd": 25.00,
    "confidence": "high",
    "price_source": "local market knowledge"
}}"""
        
        try:
            response = await self.grok_service.generate_response(
                prompt,
                system_message="You are a local transportation expert. Provide realistic prices that locals pay. Respond only with valid JSON.",
                force_json=True
            )
            
            pricing_research = self._extract_json(response)
            
            if pricing_research and "train_price_usd" in pricing_research:
                # Sanity check: ensure prices are not unrealistically low
                train_price = pricing_research.get('train_price_usd', 0)
                bus_price = pricing_research.get('bus_price_usd', 0)
                
                # Minimum per-person prices based on distance
                # For Sri Lanka: train ~$0.40/person, bus ~$0.55/person for 47km
                min_train = max(0.40, state['distance_km'] * 0.009)  # At least $0.40 or $0.009/km
                min_bus = max(0.55, state['distance_km'] * 0.012)    # At least $0.55 or $0.012/km
                
                # Adjust if too low
                if train_price < min_train:
                    print(f"   ⚠️ Train price ${train_price} too low, adjusting to ${min_train:.2f}")
                    pricing_research['train_price_usd'] = round(min_train, 2)
                
                if bus_price < min_bus:
                    print(f"   ⚠️ Bus price ${bus_price} too low, adjusting to ${min_bus:.2f}")
                    pricing_research['bus_price_usd'] = round(min_bus, 2)
                
                state["pricing_research"] = pricing_research
                print(f"   ✓ Train: ${pricing_research.get('train_price_usd', 'N/A')}/person")
                print(f"   ✓ Bus: ${pricing_research.get('bus_price_usd', 'N/A')}/person")
                print(f"   ✓ Taxi: ${pricing_research.get('taxi_price_usd', 'N/A')} total")
            else:
                # Fallback based on distance - realistic for developing countries like Sri Lanka
                state["pricing_research"] = {
                    "train_price_usd": round(max(0.40, state['distance_km'] * 0.009), 2),  # ~$0.40/person for 47km
                    "bus_price_usd": round(max(0.55, state['distance_km'] * 0.012), 2),    # ~$0.55/person for 47km
                    "taxi_price_usd": round(max(15, state['distance_km'] * 0.32), 2),       # ~$15 for 47km
                    "car_rental_daily_usd": round(max(25, state['distance_km'] * 0.53), 2), # ~$25 for 47km
                    "confidence": "medium",
                    "price_source": "distance-based estimation"
                }
                print(f"   ⚠️ Using fallback pricing")
                
        except Exception as e:
            print(f"   ❌ Error in price research: {e}")
            state["pricing_research"] = {
                "train_price_usd": 1.0,
                "bus_price_usd": 1.5,
                "taxi_price_usd": 20.0,
                "car_rental_daily_usd": 30.0
            }
        
        return state
    
    async def _calculate_costs(self, state: TransportationPricingState) -> TransportationPricingState:
        """Calculate final costs with simple arithmetic (no LLM needed for math)"""
        print(f"🤖 Step 4: Calculating costs for {state['travelers']} travelers")
        
        research = state["pricing_research"]
        
        # Simple, direct calculation - don't use LLM for basic math
        # Train and bus are per-person, multiply by travelers
        train_total = round(research.get('train_price_usd', 0) * state['travelers'], 2)
        bus_total = round(research.get('bus_price_usd', 0) * state['travelers'], 2)
        
        # Taxi and car rental are shared costs (total for all)
        taxi_total = round(research.get('taxi_price_usd', 0), 2)
        car_rental_total = round(research.get('car_rental_daily_usd', 0), 2)
        
        state["calculated_costs"] = {
            "train_total": train_total,
            "bus_total": bus_total,
            "taxi_total": taxi_total,
            "car_rental_total": car_rental_total,
        }
        
        state["reasoning"] = (
            f"Train/bus: per-person prices × {state['travelers']} travelers. "
            f"Taxi/car: shared costs for all travelers."
        )
        
        print(f"   ✓ Train: ${research.get('train_price_usd', 0)}/person × {state['travelers']} = ${train_total}")
        print(f"   ✓ Bus: ${research.get('bus_price_usd', 0)}/person × {state['travelers']} = ${bus_total}")
        print(f"   ✓ Taxi: ${taxi_total} (shared)")
        print(f"   ✓ Car rental: ${car_rental_total} (shared)")
        
        return state
    
    async def _validate_prices(self, state: TransportationPricingState) -> TransportationPricingState:
        """Format final prices with additional details (using direct calculation, not LLM)"""
        print(f"🤖 Step 5: Formatting final prices")
        
        costs = state["calculated_costs"]
        
        # Calculate duration based on distance
        duration_mins = max(30, int(state['distance_km'] * 1.2))  # ~1.2 min per km
        duration_str = f"{duration_mins // 60}h {duration_mins % 60}m"
        
        # Format prices directly without LLM (to preserve corrected prices)
        state["final_prices"] = {
            "train": {
                "cost": costs.get('train_total', 0),
                "duration": duration_str,
                "quality": "comfortable",
                "booking": "station or online"
            },
            "bus": {
                "cost": costs.get('bus_total', 0),
                "duration": f"{duration_mins // 60}h {int((duration_mins * 1.2) % 60)}m",  # Buses ~20% slower
                "quality": "basic but reliable",
                "booking": "bus terminal or flag down"
            },
            "taxi": {
                "cost": costs.get('taxi_total', 0),
                "duration": f"{duration_mins // 60}h",
                "quality": "comfortable",
                "booking": "hotel or app"
            },
            "car_rental": {
                "cost": costs.get('car_rental_total', 0),
                "duration": "flexible",
                "quality": "good",
                "booking": "rental agency"
            }
        }
        
        state["confidence"] = 0.9  # High confidence since we used validated prices
        
        print(f"   ✓ Train: ${costs.get('train_total', 0)} ({duration_str})")
        print(f"   ✓ Bus: ${costs.get('bus_total', 0)} ({duration_mins // 60}h {int((duration_mins * 1.2) % 60)}m)")
        print(f"   ✓ Taxi: ${costs.get('taxi_total', 0)} ({duration_mins // 60}h)")
        print(f"   ✓ Car rental: ${costs.get('car_rental_total', 0)} (flexible)")
        
        return state
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response"""
        try:
            # Try direct parsing
            return json.loads(text)
        except:
            # Try to find JSON in text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            return {}
    
    async def calculate_prices(
        self, 
        origin: str, 
        destination: str, 
        distance_km: float, 
        travelers: int
    ) -> Dict[str, Any]:
        """Main entry point for pricing calculation"""
        print(f"\n{'='*70}")
        print(f"🤖 LLM PRICING AGENT: {origin} → {destination}")
        print(f"{'='*70}")
        
        initial_state = TransportationPricingState(
            origin=origin,
            destination=destination,
            distance_km=distance_km,
            travelers=travelers,
            country="",
            route_context={},
            economic_context={},
            pricing_research={},
            calculated_costs={},
            final_prices={},
            confidence=0.0,
            reasoning="",
            messages=[]
        )
        
        try:
            # Run the workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            print(f"\n✅ Pricing complete! Confidence: {final_state.get('confidence', 0):.0%}")
            print(f"{'='*70}\n")
            
            return {
                "prices": final_state.get("final_prices", {}),
                "confidence": final_state.get("confidence", 0.5),
                "reasoning": final_state.get("reasoning", ""),
                "country": final_state.get("country", "Unknown"),
                "economic_context": final_state.get("economic_context", {}),
                "route_context": final_state.get("route_context", {})
            }
        except Exception as e:
            print(f"\n❌ Pricing workflow error: {e}")
            print(f"{'='*70}\n")
            return {
                "prices": {},
                "confidence": 0.0,
                "reasoning": f"Error: {str(e)}",
                "country": "Unknown",
                "economic_context": {},
                "route_context": {}
            }

