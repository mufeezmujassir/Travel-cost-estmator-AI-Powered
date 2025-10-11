"""
Local Transportation Cost Estimator
Uses LLM to estimate realistic local transport costs based on activities and destination
"""

import json
import re
from typing import Dict, Any, List


class LocalTransportEstimator:
    """Estimates local transportation costs at destination based on activities"""
    
    def __init__(self, grok_service):
        self.grok_service = grok_service
    
    async def estimate_local_transport(
        self, 
        destination: str,
        country: str,
        num_travelers: int,
        trip_duration_days: int,
        activities: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Estimate local transportation costs at destination
        
        Args:
            destination: City name (e.g., "Matara")
            country: Country name (e.g., "Sri Lanka")
            num_travelers: Number of travelers
            trip_duration_days: Number of days at destination
            activities: List of planned activities (optional)
            
        Returns:
            Dict with daily_cost, total_cost, breakdown, and reasoning
        """
        print(f"\n💡 Estimating local transport for {destination}, {country}")
        print(f"   Travelers: {num_travelers}, Duration: {trip_duration_days} days")
        
        # Build activity context
        activity_context = ""
        if activities:
            activity_context = "\n\nPlanned Activities:\n"
            for i, act in enumerate(activities[:5], 1):  # First 5 activities
                activity_context += f"{i}. {act.get('name', 'Activity')} at {act.get('location', 'unknown')}\n"
        
        prompt = f"""Estimate LOCAL transportation costs within {destination}, {country} for {num_travelers} travelers over {trip_duration_days} days.

Local transportation means: getting around WITHIN the city to visit different attractions, NOT travel between cities.

Context:
- Destination: {destination}, {country}
- Travelers: {num_travelers}
- Duration: {trip_duration_days} days
{activity_context}

Consider typical daily activities:
1. Hotel to attractions (morning)
2. Between attractions during day (2-3 trips)
3. Lunch location
4. Return to hotel (evening)

Estimate costs for:
1. **Tuk-tuks/Auto-rickshaws**: Short trips within city (~2-5 km)
2. **Taxis**: Longer trips or when tuk-tuks unavailable
3. **Public buses**: For budget travelers (if applicable)
4. **Walking**: Many attractions might be walkable

For {destination} specifically:
- What's the typical tuk-tuk fare? (per km or per trip)
- Are attractions spread out or clustered?
- Is public transport good?
- Can travelers walk between some attractions?

Provide realistic DAILY cost (shared by all {num_travelers} travelers) in USD.

Respond ONLY with valid JSON:
{{
    "daily_cost_usd": 15.0,
    "trips_per_day": 4,
    "transport_breakdown": {{
        "tuk_tuk": 10.0,
        "taxi": 5.0,
        "public_bus": 0.0
    }},
    "reasoning": "Matara attractions are within 5km radius. Typical tuk-tuk fare is LKR 200-300 ($0.60-0.90) per trip. 4 trips/day = $3-4. For 3 travelers sharing, $12-15/day is realistic.",
    "local_fare_notes": "Tuk-tuk: $0.60-0.90/trip, Walking distance between some sites"
}}"""
        
        try:
            response = await self.grok_service.generate_response(
                prompt,
                system_message="You are a local transport cost expert. Provide realistic prices locals pay. Respond only with valid JSON.",
                force_json=True
            )
            
            # Extract JSON
            data = self._extract_json(response)
            
            if data and "daily_cost_usd" in data:
                daily_cost = data["daily_cost_usd"]
                total_cost = daily_cost * trip_duration_days
                
                print(f"   ✓ Daily cost: ${daily_cost} (for group of {num_travelers})")
                print(f"   ✓ Total: ${total_cost} ({trip_duration_days} days)")
                
                return {
                    "daily_cost": round(daily_cost, 2),
                    "total_cost": round(total_cost, 2),
                    "per_person_daily": round(daily_cost / num_travelers, 2) if num_travelers > 0 else 0,
                    "trips_per_day": data.get("trips_per_day", 4),
                    "breakdown": data.get("transport_breakdown", {}),
                    "reasoning": data.get("reasoning", ""),
                    "local_fare_notes": data.get("local_fare_notes", ""),
                    "confidence": 0.85
                }
            else:
                print(f"   ⚠️ Invalid LLM response, using fallback")
                return self._fallback_estimate(destination, country, num_travelers, trip_duration_days)
                
        except Exception as e:
            print(f"   ❌ Error estimating local transport: {e}")
            return self._fallback_estimate(destination, country, num_travelers, trip_duration_days)
    
    def _fallback_estimate(self, destination: str, country: str, num_travelers: int, trip_duration_days: int) -> Dict[str, Any]:
        """Fallback estimation when LLM fails"""
        # Simple heuristic: $4-8 per person per day for local transport
        per_person_daily = 6.0
        daily_cost = per_person_daily * num_travelers
        total_cost = daily_cost * trip_duration_days
        
        return {
            "daily_cost": round(daily_cost, 2),
            "total_cost": round(total_cost, 2),
            "per_person_daily": per_person_daily,
            "trips_per_day": 4,
            "breakdown": {
                "tuk_tuk": daily_cost * 0.7,
                "taxi": daily_cost * 0.3,
                "public_bus": 0
            },
            "reasoning": f"Estimated based on typical local transport costs in developing countries",
            "local_fare_notes": "Fallback estimate",
            "confidence": 0.5
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

