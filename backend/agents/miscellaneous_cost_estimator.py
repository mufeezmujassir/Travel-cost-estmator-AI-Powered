"""
Miscellaneous Cost Estimator
Uses LLM to estimate realistic miscellaneous expenses (tips, souvenirs, emergencies, etc.)
"""

import json
import re
from typing import Dict, Any
from models.travel_models import VibeType


class MiscellaneousCostEstimator:
    """Estimates miscellaneous costs based on destination and travel style"""
    
    def __init__(self, grok_service):
        self.grok_service = grok_service
    
    async def estimate_miscellaneous_cost(
        self,
        destination: str,
        country: str,
        num_travelers: int,
        trip_duration_days: int,
        vibe: VibeType
    ) -> Dict[str, Any]:
        """
        Estimate miscellaneous expenses at destination
        
        Args:
            destination: City name (e.g., "Matara")
            country: Country name (e.g., "Sri Lanka")
            num_travelers: Number of travelers
            trip_duration_days: Number of days
            vibe: Travel style
            
        Returns:
            Dict with daily_cost, total_cost, breakdown, and tips
        """
        print(f"\n💰 Estimating miscellaneous costs for {destination}, {country}")
        print(f"   Travelers: {num_travelers}, Duration: {trip_duration_days} days, Vibe: {vibe.value}")
        
        prompt = f"""Estimate daily MISCELLANEOUS expenses in {destination}, {country} for {num_travelers} travelers.

Travel Style: {vibe.value}
Duration: {trip_duration_days} days

Miscellaneous expenses include:

1. **Tips and Service Charges**:
   - Restaurant tips (if customary)
   - Hotel staff tips
   - Tour guide tips
   - Taxi/driver tips

2. **Shopping and Souvenirs**:
   - Small souvenirs for family/friends
   - Local crafts
   - Postcards
   - Photos

3. **Incidentals**:
   - Phone/SIM card or data
   - Bottled water (daily)
   - Sunscreen, toiletries
   - Laundry (if multi-day trip)
   - Emergency medicine

4. **Unexpected Costs**:
   - Extra snacks
   - Convenience items
   - Small fees (toilet fees, photo fees)

For {destination}, {country} specifically:
- Is tipping expected/customary? What percentage?
- What are typical souvenir prices?
- Is tap water safe or need bottled water? ($1-2/day)
- Are there common small fees tourists encounter?
- Any mobile data/SIM card costs?

Consider travel style:
- **Romantic/Wellness**: May spend more on souvenirs, spa products
- **Cultural**: May buy local crafts, books, art
- **Adventure**: May need extra gear, first aid supplies
- **Beach**: Sunscreen, beach items, water

Provide realistic DAILY cost PER PERSON in USD.

Respond ONLY with valid JSON:
{{
    "daily_per_person_usd": 8.0,
    "misc_breakdown": {{
        "tips": 2.0,
        "souvenirs": 3.0,
        "incidentals": 2.0,
        "contingency": 1.0
    }},
    "tipping_culture": "Not customary in restaurants, but small tips appreciated for guides",
    "key_expenses": [
        "SIM card: $5-10 one-time",
        "Bottled water: $0.50/bottle",
        "Sunscreen: $5-8",
        "Small souvenirs: $2-5 each"
    ],
    "money_saving_tips": [
        "Tap water is safe in hotels",
        "Negotiate prices at markets",
        "Buy local products, not imported goods"
    ],
    "reasoning": "Sri Lanka is budget-friendly. Tipping not mandatory but appreciated. Souvenirs cheap ($2-5). Water, toiletries minimal. $8-10/day realistic for misc expenses."
}}"""
        
        try:
            response = await self.grok_service.generate_response(
                prompt,
                system_message="You are a travel budget expert. Provide realistic miscellaneous expense estimates based on local customs and prices. Respond only with valid JSON.",
                force_json=True
            )
            
            # Extract JSON
            data = self._extract_json(response)
            
            if data and "daily_per_person_usd" in data:
                daily_per_person = data["daily_per_person_usd"]
                total_cost = daily_per_person * trip_duration_days * num_travelers
                
                print(f"   ✓ Daily per person: ${daily_per_person}")
                print(f"   ✓ Tipping culture: {data.get('tipping_culture', 'N/A')[:50]}...")
                print(f"   ✓ Total: ${total_cost} ({trip_duration_days} days × {num_travelers} travelers)")
                
                return {
                    "daily_per_person": round(daily_per_person, 2),
                    "total_cost": round(total_cost, 2),
                    "misc_breakdown": data.get("misc_breakdown", {}),
                    "tipping_culture": data.get("tipping_culture", ""),
                    "key_expenses": data.get("key_expenses", []),
                    "money_saving_tips": data.get("money_saving_tips", []),
                    "reasoning": data.get("reasoning", ""),
                    "confidence": 0.85
                }
            else:
                print(f"   ⚠️ Invalid LLM response, using fallback")
                return self._fallback_estimate(country, num_travelers, trip_duration_days, vibe)
                
        except Exception as e:
            print(f"   ❌ Error estimating miscellaneous cost: {e}")
            return self._fallback_estimate(country, num_travelers, trip_duration_days, vibe)
    
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
            base_daily = 15.0
        elif any(c in country_lower for c in cheap_countries):
            base_daily = 6.0  # Cheaper for developing countries
        elif any(c in country_lower for c in mid_countries):
            base_daily = 10.0
        else:
            base_daily = 10.0
        
        # Adjust for vibe
        if vibe == VibeType.ROMANTIC:
            daily_per_person = base_daily * 1.3  # More souvenirs, special touches
        elif vibe == VibeType.WELLNESS:
            daily_per_person = base_daily * 1.2  # Spa products, wellness items
        else:
            daily_per_person = base_daily
        
        total_cost = daily_per_person * trip_duration_days * num_travelers
        
        return {
            "daily_per_person": round(daily_per_person, 2),
            "total_cost": round(total_cost, 2),
            "misc_breakdown": {
                "tips": round(daily_per_person * 0.25, 2),
                "souvenirs": round(daily_per_person * 0.40, 2),
                "incidentals": round(daily_per_person * 0.25, 2),
                "contingency": round(daily_per_person * 0.10, 2)
            },
            "tipping_culture": "Check local customs",
            "key_expenses": ["Tips", "Souvenirs", "Water", "Toiletries"],
            "money_saving_tips": ["Buy local products", "Negotiate at markets", "Avoid tourist traps"],
            "reasoning": f"Estimated based on {country or 'country'} economic tier and {vibe.value} travel style",
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

