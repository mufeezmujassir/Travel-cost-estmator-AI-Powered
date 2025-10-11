"""
Activities Cost Estimator
Uses LLM to estimate realistic activity and attraction costs based on destination
"""

import json
import re
from typing import Dict, Any, List
from models.travel_models import VibeType


class ActivitiesCostEstimator:
    """Estimates activity costs based on destination and travel vibe"""
    
    def __init__(self, grok_service):
        self.grok_service = grok_service
    
    async def estimate_activities_cost(
        self,
        destination: str,
        country: str,
        num_travelers: int,
        trip_duration_days: int,
        vibe: VibeType,
        activities: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Estimate activities and attractions costs at destination
        
        Args:
            destination: City name (e.g., "Matara")
            country: Country name (e.g., "Sri Lanka")
            num_travelers: Number of travelers
            trip_duration_days: Number of days
            vibe: Travel style (cultural, adventure, beach, etc.)
            activities: Optional list of activities from SERP API
            
        Returns:
            Dict with daily_cost, total_cost, breakdown, and suggested activities
        """
        print(f"\n🎯 Estimating activities costs for {destination}, {country}")
        print(f"   Travelers: {num_travelers}, Duration: {trip_duration_days} days, Vibe: {vibe.value}")
        
        # Build activity context if available
        activity_context = ""
        if activities and len(activities) > 0:
            activity_context = "\n\nActivities available from search:\n"
            for i, act in enumerate(activities[:5], 1):
                activity_context += f"{i}. {act.get('name', 'Activity')}\n"
                if act.get('price'):
                    activity_context += f"   Price: {act.get('price')}\n"
        
        # Map vibe to activity preferences
        activity_focus = self._vibe_to_activity_focus(vibe)
        
        prompt = f"""Estimate daily ACTIVITIES and ATTRACTIONS costs in {destination}, {country} for {num_travelers} travelers.

Travel Vibe: {vibe.value} ({activity_focus})
Duration: {trip_duration_days} days
{activity_context}

Consider typical activities per day:
1. **Main attractions**: Museums, temples, parks, tours (1-2 per day)
2. **Experiences**: Cooking classes, water sports, cultural shows
3. **Entry fees**: National parks, historic sites, viewpoints
4. **Guided tours**: City tours, nature walks, food tours
5. **Equipment rental**: Snorkeling gear, bikes, beach items

For {destination}, {country} specifically:
- What are the TOP 3-5 must-do attractions/activities?
- What's the typical entry fee for major sites?
- Are there free activities (beaches, temples, parks)?
- What's realistic spending for {vibe.value} travelers?

IMPORTANT: Research ACTUAL LOCAL PRICES, not tourist/Western prices!
- In developing countries like Sri Lanka, India, Thailand, many attractions are FREE or very cheap ($1-5)
- Temples, beaches, forts often have NO entry fee or small donations
- Don't assume Western pricing standards

Vibe-specific guidance:
- **Cultural**: Focus on museums, temples, historical sites, local experiences
- **Adventure**: Focus on outdoor activities, water sports, hiking, excursions
- **Beach**: Beach access (often free), water sports, boat trips
- **Nature**: National parks, wildlife, hiking, eco-tours
- **Romantic**: Sunset cruises, spa treatments, fine dining experiences
- **Culinary**: Food tours, cooking classes, market visits
- **Wellness**: Yoga classes, spa treatments, meditation retreats

Provide realistic DAILY cost PER PERSON in USD.

EXAMPLES for context:
- Sri Lanka temples: FREE (donation optional)
- Sri Lanka lighthouse: $1-2 entry
- Sri Lanka beaches: FREE
- India monuments: $2-5 for locals, $5-10 for foreigners
- Thailand temples: FREE (proper dress required)
- USA museums: $15-30 entry

For budget countries (Sri Lanka, India, Thailand, Vietnam), typical cultural traveler: $10-15/day
For mid-tier (China, Mexico, Turkey): $20-30/day
For expensive (Japan, Switzerland, USA): $40-60/day

Respond ONLY with valid JSON:
{{
    "daily_per_person_usd": 12.0,
    "activities_breakdown": {{
        "main_attractions": 7.0,
        "experiences": 4.0,
        "tours": 0.0,
        "equipment_rental": 1.0
    }},
    "suggested_activities": [
        {{"name": "Dondra Head Lighthouse", "cost": 2.0, "duration": "1-2 hours"}},
        {{"name": "Paravi Duwa Temple", "cost": 0.0, "duration": "1 hour"}},
        {{"name": "Matara Beach", "cost": 0.0, "duration": "flexible"}},
        {{"name": "Weherahena Temple", "cost": 0.0, "duration": "1 hour"}},
        {{"name": "Matara Fort", "cost": 0.0, "duration": "30 minutes"}}
    ],
    "free_activities": ["Beach access", "Temple visits", "Coastal walks", "Fort exploration"],
    "reasoning": "Matara is budget-friendly. Most attractions FREE (temples, beach, fort). Lighthouse $2. Cultural travelers focus on free temples and historical sites. $10-15/day realistic for Sri Lanka.",
    "activity_style": "Budget-conscious cultural exploration"
}}"""
        
        try:
            response = await self.grok_service.generate_response(
                prompt,
                system_message="You are a travel activities expert. Provide realistic prices based on actual local costs. Include both paid and free activities. Respond only with valid JSON.",
                force_json=True
            )
            
            # Extract JSON
            data = self._extract_json(response)
            
            if data and "daily_per_person_usd" in data:
                daily_per_person = data["daily_per_person_usd"]
                
                # Sanity check: prevent unrealistically high costs
                country_lower = country.lower() if country else ""
                if any(c in country_lower for c in ["sri lanka", "india", "thailand", "vietnam", "cambodia", "philippines", "indonesia", "nepal"]):
                    # Cheap countries: cap at $20/day for cultural/nature, $35/day for adventure
                    max_daily = 35.0 if vibe == VibeType.ADVENTURE else 20.0
                    if daily_per_person > max_daily:
                        print(f"   ⚠️ Activities cost ${daily_per_person} too high for {country}, adjusting to ${max_daily}")
                        daily_per_person = max_daily
                
                total_cost = daily_per_person * trip_duration_days * num_travelers
                
                print(f"   ✓ Daily per person: ${daily_per_person}")
                print(f"   ✓ Suggested activities: {len(data.get('suggested_activities', []))}")
                print(f"   ✓ Free activities: {len(data.get('free_activities', []))}")
                print(f"   ✓ Total: ${total_cost} ({trip_duration_days} days × {num_travelers} travelers)")
                
                return {
                    "daily_per_person": round(daily_per_person, 2),
                    "total_cost": round(total_cost, 2),
                    "activities_breakdown": data.get("activities_breakdown", {}),
                    "suggested_activities": data.get("suggested_activities", []),
                    "free_activities": data.get("free_activities", []),
                    "reasoning": data.get("reasoning", ""),
                    "activity_style": data.get("activity_style", ""),
                    "confidence": 0.85
                }
            else:
                print(f"   ⚠️ Invalid LLM response, using fallback")
                return self._fallback_estimate(country, num_travelers, trip_duration_days, vibe)
                
        except Exception as e:
            print(f"   ❌ Error estimating activities cost: {e}")
            return self._fallback_estimate(country, num_travelers, trip_duration_days, vibe)
    
    def _vibe_to_activity_focus(self, vibe: VibeType) -> str:
        """Map vibe to activity preferences"""
        mapping = {
            VibeType.ROMANTIC: "Romantic experiences, sunset cruises, spa treatments",
            VibeType.ADVENTURE: "Outdoor activities, water sports, hiking, excursions",
            VibeType.BEACH: "Beach activities, water sports, boat trips",
            VibeType.NATURE: "Nature tours, wildlife, national parks, eco-activities",
            VibeType.CULTURAL: "Museums, temples, historical sites, cultural experiences",
            VibeType.CULINARY: "Food tours, cooking classes, culinary experiences",
            VibeType.WELLNESS: "Yoga, spa treatments, meditation, wellness activities"
        }
        return mapping.get(vibe, "General sightseeing and experiences")
    
    def _fallback_estimate(
        self, 
        country: str, 
        num_travelers: int, 
        trip_duration_days: int,
        vibe: VibeType
    ) -> Dict[str, Any]:
        """Fallback estimation based on country economic tier"""
        # Categorize countries by activity costs
        expensive_countries = ["switzerland", "norway", "iceland", "denmark", "japan", "singapore", "australia"]
        cheap_countries = ["india", "sri lanka", "vietnam", "thailand", "cambodia", "philippines", 
                          "indonesia", "nepal", "bangladesh", "pakistan", "myanmar", "laos"]
        mid_countries = ["china", "brazil", "poland", "mexico", "turkey", "egypt", "argentina", "south africa"]
        
        country_lower = country.lower() if country else ""
        
        # Base rates per person per day
        if any(c in country_lower for c in expensive_countries):
            base_daily = 60.0
        elif any(c in country_lower for c in cheap_countries):
            base_daily = 20.0  # More realistic for developing countries
        elif any(c in country_lower for c in mid_countries):
            base_daily = 35.0
        else:
            base_daily = 40.0
        
        # Adjust for vibe
        if vibe == VibeType.ADVENTURE:
            daily_per_person = base_daily * 1.5  # Adventure activities more expensive
        elif vibe == VibeType.WELLNESS:
            daily_per_person = base_daily * 1.4  # Spa and wellness treatments
        elif vibe == VibeType.ROMANTIC:
            daily_per_person = base_daily * 1.3  # Special experiences
        elif vibe == VibeType.CULINARY:
            daily_per_person = base_daily * 1.2  # Food tours and classes
        elif vibe == VibeType.BEACH:
            daily_per_person = base_daily * 0.8  # Many beach activities free
        else:
            daily_per_person = base_daily
        
        total_cost = daily_per_person * trip_duration_days * num_travelers
        
        return {
            "daily_per_person": round(daily_per_person, 2),
            "total_cost": round(total_cost, 2),
            "activities_breakdown": {
                "main_attractions": round(daily_per_person * 0.6, 2),
                "experiences": round(daily_per_person * 0.3, 2),
                "equipment_rental": round(daily_per_person * 0.1, 2)
            },
            "suggested_activities": [],
            "free_activities": ["Explore local markets", "Beach/park walks", "Free viewpoints"],
            "reasoning": f"Estimated based on {country or 'country'} economic tier and {vibe.value} travel style",
            "activity_style": f"{vibe.value} activities",
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

