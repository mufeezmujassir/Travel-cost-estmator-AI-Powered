import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
import httpx
import json
import re

class HotelContextService:
    """
    Provides contextual information about hotels similar to Google Hotels:
    - Where to stay (top areas/neighborhoods) - fetched from Google Search
    - When to visit (seasonal pricing, weather, crowds) - fetched from multiple sources
    - What you'll pay (price breakdown by star rating) - analyzed from real hotel data
    """
    
    def __init__(self, serp_service, grok_service):
        self.serp_service = serp_service
        self.grok_service = grok_service
    
    async def get_hotel_context(
        self, 
        destination: str, 
        check_in_date: str,
        check_out_date: str,
        hotels_data: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive hotel context including areas, timing, and pricing
        """
        destination_lower = destination.strip().lower()
        
        # Calculate stay duration
        check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
        check_out = datetime.strptime(check_out_date, "%Y-%m-%d")
        duration_days = (check_out - check_in).days
        current_month = check_in.strftime("%B")
        
        # Get all context information concurrently
        tasks = [
            self._get_where_to_stay(destination_lower),
            self._get_when_to_visit(destination_lower, current_month),
            self._get_what_youll_pay(destination_lower, hotels_data),
        ]
        
        where_info, when_info, pricing_info = await asyncio.gather(*tasks)
        
        return {
            "status": "success",
            "destination": destination,
            "duration_days": duration_days,
            "where_to_stay": where_info,
            "when_to_visit": when_info,
            "what_youll_pay": pricing_info,
            "tips": self._generate_tips(where_info, when_info, pricing_info)
        }
    
    async def _get_where_to_stay(self, destination: str) -> Dict[str, Any]:
        """Get top areas/neighborhoods for the destination using web search + AI"""
        print(f"🔍 Fetching top areas for {destination}...")
        
        # Step 1: Search for "best neighborhoods to stay in [destination]"
        search_query = f"best neighborhoods areas to stay in {destination} for tourists"
        search_results = await self.serp_service._web_search(search_query, num_results=5)
        
        # Step 2: Extract information from search results
        context_text = ""
        for result in search_results.get("organic_results", [])[:5]:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            context_text += f"{title}. {snippet}\n"
        
        # Step 3: Use AI to analyze and structure the data
        prompt = f"""Based on this information about {destination}, provide 3-4 top areas/neighborhoods to stay for tourists.

Information from web:
{context_text}

For each area, provide:
- name: Area name
- description: Brief 5-7 word description
- score: Rating out of 5 (estimate between 4.0-4.7 as a float)
- known_for: List of 3-4 things the area is known for

Return ONLY a JSON object with this structure:
{{"areas": [{{"name": "...", "description": "...", "score": 4.5, "known_for": ["...", "..."]}}]}}"""
        
        try:
            response = await asyncio.to_thread(
                self.grok_service.generate_response,
                prompt,
                force_json=True
            )
            data = json.loads(response)
            print(f"✅ Found {len(data.get('areas', []))} areas for {destination}")
            return {
                "top_areas": data.get("areas", []),
                "source": "web_search_ai"
            }
        except Exception as e:
            print(f"⚠️ Error generating area recommendations: {e}")
            return {
                "top_areas": [],
                "source": "unavailable"
            }
    
    async def _get_when_to_visit(self, destination: str, current_month: str) -> Dict[str, Any]:
        """Get seasonal pricing and visit information using web search + AI"""
        print(f"🔍 Fetching seasonal information for {destination}...")
        
        # Step 1: Search for weather and tourism information
        search_query = f"{destination} best time to visit weather crowds tourism seasons"
        search_results = await self.serp_service._web_search(search_query, num_results=5)
        
        # Step 2: Extract context from search results
        context_text = ""
        for result in search_results.get("organic_results", [])[:5]:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            context_text += f"{title}. {snippet}\n"
        
        # Step 3: Use AI to analyze and structure seasonal data
        prompt = f"""Based on this information, provide seasonal data for {destination} for 12 months.

Information from web:
{context_text}

For each month (January through December), provide:
- month: Month name
- temp_range: Temperature range (e.g., "17°C - 21°C")
- weather: Brief weather description (e.g., "Mostly sunny", "Rainy season")
- crowd_level: "Low", "Moderate", "Busy", or "Very Busy"
- price_level: "$" (cheapest), "$$", "$$$", or "$$$$" (most expensive)
- price_range: Estimated hotel price range in LKR (e.g., "LKR10K-LKR25K")

Return ONLY a JSON object with this structure:
{{"months": [{{"month": "January", "temp_range": "...", "weather": "...", "crowd_level": "...", "price_level": "$$", "price_range": "LKR10K-LKR25K"}}]}}"""
        
        try:
            response = await asyncio.to_thread(
                self.grok_service.generate_response,
                prompt,
                force_json=True
            )
            data = json.loads(response)
            seasonal_data = data.get("months", [])
            
            # Find current month info
            current_month_info = next(
                (m for m in seasonal_data if m["month"] == current_month),
                None
            )
            
            # Find best months (lowest price level)
            best_months = [m for m in seasonal_data if m.get("price_level") in ["$", "$$"]]
            peak_months = [m for m in seasonal_data if m.get("price_level") == "$$$$"]
            
            print(f"✅ Fetched seasonal data for {destination}: {len(seasonal_data)} months")
            
            return {
                "current_month": current_month_info,
                "best_value_months": best_months[:3],
                "peak_season_months": peak_months[:2],
                "all_months": seasonal_data,
                "source": "web_search_ai"
            }
        except Exception as e:
            print(f"⚠️ Error generating seasonal data: {e}")
            return {
                "current_month": {"month": current_month, "price_level": "$$$"},
                "all_months": [],
                "source": "error"
            }
    
    async def _get_what_youll_pay(
        self, 
        destination: str, 
        hotels_data: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze hotel prices by star rating"""
        if not hotels_data:
            # Return default estimates
            return {
                "by_star_rating": [
                    {"stars": 2, "avg_price": 16000, "range": "LKR14K-LKR25K", "count": "80+ hotels", "label": "Typical"},
                    {"stars": 3, "avg_price": 29000, "range": "LKR24K-LKR43K", "count": "114+ hotels", "label": "Typical"},
                    {"stars": 4, "avg_price": 65000, "range": "LKR43K-LKR83K", "count": "15+ hotels", "label": "Typical"},
                    {"stars": 5, "avg_price": 162000, "range": "LKR94K-LKR221K", "count": "1+ hotels", "label": "Typical"},
                ],
                "source": "estimated"
            }
        
        # Analyze actual hotel data
        by_rating = defaultdict(list)
        
        for hotel in hotels_data:
            rating = hotel.get("rating", 0)
            price = hotel.get("price", 0)
            
            # Determine star category (rough approximation based on rating)
            if rating >= 4.5:
                stars = 5
            elif rating >= 4.0:
                stars = 4
            elif rating >= 3.5:
                stars = 3
            else:
                stars = 2
            
            if price > 0:
                by_rating[stars].append(price)
        
        # Calculate statistics for each star rating
        star_breakdown = []
        for stars in sorted(by_rating.keys()):
            prices = by_rating[stars]
            if prices:
                avg_price = sum(prices) / len(prices)
                min_price = min(prices)
                max_price = max(prices)
                
                star_breakdown.append({
                    "stars": stars,
                    "avg_price": round(avg_price),
                    "range": f"LKR{round(min_price/1000)}K-LKR{round(max_price/1000)}K",
                    "count": f"{len(prices)}+ hotels",
                    "label": "Typical"
                })
        
        return {
            "by_star_rating": star_breakdown if star_breakdown else [],
            "source": "actual_data"
        }
    
    def _generate_tips(
        self, 
        where_info: Dict[str, Any], 
        when_info: Dict[str, Any], 
        pricing_info: Dict[str, Any]
    ) -> List[str]:
        """Generate helpful tips based on context"""
        tips = []
        
        # Area tip
        if where_info.get("top_areas"):
            top_area = where_info["top_areas"][0]
            tips.append(f"🏙️ {top_area['name']} is a top choice for visitors (Score: {top_area['score']}/5)")
        
        # Seasonal tip
        current_month = when_info.get("current_month", {})
        if current_month:
            crowd = current_month.get("crowd_level", "")
            if crowd == "Very Busy":
                tips.append(f"⚠️ {current_month['month']} is peak season - book early!")
            elif crowd == "Moderate":
                tips.append(f"✅ {current_month['month']} offers good value with moderate crowds")
        
        # Best value months
        if when_info.get("best_value_months"):
            best_month = when_info["best_value_months"][0]["month"]
            tips.append(f"💰 Best value: {best_month} typically has lower hotel prices")
        
        # Pricing tip
        if pricing_info.get("by_star_rating"):
            three_star = next((r for r in pricing_info["by_star_rating"] if r["stars"] == 3), None)
            if three_star:
                tips.append(f"💡 3-star hotels average ~LKR{round(three_star['avg_price']/1000)}K per night")
        
        return tips

