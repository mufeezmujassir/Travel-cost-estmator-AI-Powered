"""
Food Cost Estimator
Uses LLM to estimate realistic food costs based on destination, country, and travel vibe
"""

import json
import re
from typing import Dict, Any
from models.travel_models import VibeType


class FoodCostEstimator:
    """Estimates food costs based on destination economy and travel style"""
    
    def __init__(self, grok_service):
        self.grok_service = grok_service
    
    async def estimate_food_cost(
        self,
        destination: str,
        country: str,
        num_travelers: int,
        trip_duration_days: int,
        vibe: VibeType = VibeType.CULTURAL
    ) -> Dict[str, Any]:
        """
        Estimate food costs at destination
        
        Args:
            destination: City name (e.g., "Matara")
            country: Country name (e.g., "Sri Lanka")
            num_travelers: Number of travelers
            trip_duration_days: Number of days
            vibe: Travel style (luxury, balanced, budget, etc.)
            
        Returns:
            Dict with daily_cost, total_cost, breakdown, and reasoning
        """
        print(f"\n🍽️ Estimating food costs for {destination}, {country}")
        print(f"   Travelers: {num_travelers}, Duration: {trip_duration_days} days, Vibe: {vibe.value}")
        
        # Map vibe to budget style
        budget_style = self._vibe_to_budget_style(vibe)
        
        prompt = f"""Estimate daily FOOD costs in {destination}, {country} for {num_travelers} travelers.

Travel Style: {budget_style}
Duration: {trip_duration_days} days

Consider typical daily meals:
1. **Breakfast**: Hotel (often included) or local café
2. **Lunch**: Local restaurant or street food
3. **Dinner**: Restaurant (main meal)
4. **Snacks/Drinks**: Coffee, water, snacks during day

For {destination}, {country} specifically:
- What's the typical cost of a meal at a local restaurant?
- Are there cheap street food options?
- How much is a coffee/tea/drink?
- What's realistic for {budget_style} travelers?

Budget Styles:
- **Luxury**: Fine dining, upscale restaurants, expensive venues
- **Balanced**: Mix of local restaurants and mid-range places
- **Budget**: Street food, local eateries, self-catering when possible
- **Backpacker**: Cheapest options, street food, markets

Provide DAILY cost PER PERSON in USD.

Respond ONLY with valid JSON:
{{
    "daily_per_person_usd": 12.0,
    "meal_breakdown": {{
        "breakfast": 2.0,
        "lunch": 4.0,
        "dinner": 5.0,
        "snacks_drinks": 1.0
    }},
    "dining_style": "Mix of local restaurants and street food",
    "reasoning": "Matara has excellent local Sri Lankan food. Rice and curry lunch = LKR 400 ($1.20), dinner at local restaurant = LKR 800-1000 ($2.50-3), breakfast $2. Total $10-12/day is realistic for balanced travelers.",
    "local_specialties": "Rice and curry, hoppers, kottu roti",
    "price_notes": "Street food: $1-2, Local restaurant: $3-5, Tourist restaurant: $8-12"
}}"""
        
        try:
            response = await self.grok_service.generate_response(
                prompt,
                system_message="You are a food cost expert. Provide realistic prices locals and tourists pay. Respond only with valid JSON.",
                force_json=True
            )
            
            # Extract JSON
            data = self._extract_json(response)
            
            if data and "daily_per_person_usd" in data:
                daily_per_person = data["daily_per_person_usd"]
                total_cost = daily_per_person * trip_duration_days * num_travelers
                
                print(f"   ✓ Daily per person: ${daily_per_person}")
                print(f"   ✓ Total: ${total_cost} ({trip_duration_days} days × {num_travelers} travelers)")
                
                return {
                    "daily_per_person": round(daily_per_person, 2),
                    "total_cost": round(total_cost, 2),
                    "meal_breakdown": data.get("meal_breakdown", {}),
                    "dining_style": data.get("dining_style", ""),
                    "reasoning": data.get("reasoning", ""),
                    "local_specialties": data.get("local_specialties", ""),
                    "price_notes": data.get("price_notes", ""),
                    "confidence": 0.85
                }
            else:
                print(f"   ⚠️ Invalid LLM response, using fallback")
                return self._fallback_estimate(country, num_travelers, trip_duration_days, vibe)
                
        except Exception as e:
            print(f"   ❌ Error estimating food cost: {e}")
            return self._fallback_estimate(country, num_travelers, trip_duration_days, vibe)
    
    def _vibe_to_budget_style(self, vibe: VibeType) -> str:
        """Map vibe to budget style"""
        mapping = {
            VibeType.ROMANTIC: "Balanced (leaning upscale)",
            VibeType.ADVENTURE: "Balanced (practical meals)",
            VibeType.BEACH: "Balanced (casual dining)",
            VibeType.NATURE: "Balanced (local food)",
            VibeType.CULTURAL: "Balanced (try local specialties)",
            VibeType.CULINARY: "Upscale (food-focused)",
            VibeType.WELLNESS: "Balanced (healthy options)"
        }
        return mapping.get(vibe, "Balanced")
    
    def _fallback_estimate(
        self, 
        country: str, 
        num_travelers: int, 
        trip_duration_days: int,
        vibe: VibeType
    ) -> Dict[str, Any]:
        """Fallback estimation based on country economic tier"""
        # Categorize countries by cost of living
        expensive_countries = ["switzerland", "norway", "iceland", "denmark", "japan", "singapore"]
        cheap_countries = ["india", "sri lanka", "vietnam", "thailand", "cambodia", "philippines", 
                          "indonesia", "nepal", "bangladesh", "pakistan"]
        mid_countries = ["china", "brazil", "poland", "mexico", "turkey", "egypt"]
        
        country_lower = country.lower() if country else ""
        
        # Base rates per person per day
        if any(c in country_lower for c in expensive_countries):
            base_daily = 60.0
        elif any(c in country_lower for c in cheap_countries):
            base_daily = 15.0
        elif any(c in country_lower for c in mid_countries):
            base_daily = 25.0
        else:
            base_daily = 35.0
        
        # Adjust for vibe
        if vibe == VibeType.CULINARY:
            daily_per_person = base_daily * 1.5  # Food-focused travelers spend more
        elif vibe == VibeType.ROMANTIC:
            daily_per_person = base_daily * 1.3  # Nice dinners
        elif vibe == VibeType.WELLNESS:
            daily_per_person = base_daily * 1.2  # Healthy/organic food
        else:
            daily_per_person = base_daily  # Standard for adventure, cultural, beach, nature
        
        total_cost = daily_per_person * trip_duration_days * num_travelers
        
        return {
            "daily_per_person": round(daily_per_person, 2),
            "total_cost": round(total_cost, 2),
            "meal_breakdown": {
                "breakfast": round(daily_per_person * 0.2, 2),
                "lunch": round(daily_per_person * 0.35, 2),
                "dinner": round(daily_per_person * 0.35, 2),
                "snacks_drinks": round(daily_per_person * 0.1, 2)
            },
            "dining_style": f"{vibe.value} style dining",
            "reasoning": f"Estimated based on {country or 'country'} economic tier and {vibe.value} travel style",
            "local_specialties": "Local cuisine available",
            "price_notes": "Fallback estimate",
            "confidence": 0.6
        }
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response"""
        try:
            return json.loads(text)
        except:
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            return {}

