"""
Suitability Scorer Service
Core logic for computing multi-factor suitability scores (0-100) for vibe timing recommendations
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio

from .weather_service import WeatherService
from .region_mapper import RegionMapper
from .price_calendar import PriceCalendar

class SuitabilityScorer:
    """Computes intelligent suitability scores for vibe timing recommendations"""
    
    def __init__(self, serp_service=None):
        self.weather_service = WeatherService()
        self.region_mapper = RegionMapper()
        self.price_calendar = PriceCalendar(serp_service) if serp_service else None
        
        # Scoring weights
        self.weights = {
            "weather": 0.40,
            "price": 0.25,
            "crowd": 0.15,
            "events": 0.10,
            "seasonality": 0.10
        }
    
    async def calculate_suitability_score(
        self, 
        vibe: str, 
        destination: str, 
        start_date: str, 
        duration_days: int = 5,
        origin: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive suitability score for a vibe and destination
        
        Args:
            vibe: Vibe type (romantic, adventure, beach, etc.)
            destination: Destination city
            start_date: Start date in YYYY-MM-DD format
            duration_days: Trip duration in days
            origin: Origin city (optional, for price analysis)
            
        Returns:
            Dict with score, label, reason, and detailed breakdown
        """
        try:
            # Parse start date
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            month = start_dt.month
            
            # Get destination information
            dest_info = await self.region_mapper.get_destination_info(destination)
            
            # Calculate individual scores
            try:
                weather_score = await self._calculate_weather_score(vibe, dest_info, month)
            except Exception as e:
                print(f"Weather score error: {e}")
                weather_score = {"score": 50.0, "summary": "Weather data unavailable"}
            
            try:
                price_score = await self._calculate_price_score(origin, destination, start_date, duration_days)
            except Exception as e:
                print(f"Price score error: {e}")
                price_score = {"score": 50.0, "summary": "Price data unavailable"}
            
            try:
                crowd_score = self._calculate_crowd_score(dest_info, month)
            except Exception as e:
                print(f"Crowd score error: {e}")
                crowd_score = {"score": 50.0, "summary": "Crowd data unavailable"}
            
            try:
                events_score = self._calculate_events_score(vibe, dest_info, month)
            except Exception as e:
                print(f"Events score error: {e}")
                events_score = {"score": 50.0, "summary": "Events data unavailable", "events": []}
            
            try:
                seasonality_score = self._calculate_seasonality_score(vibe, dest_info, month)
            except Exception as e:
                print(f"Seasonality score error: {e}")
                seasonality_score = {"score": 50.0, "summary": "Seasonality data unavailable"}
            
            scores = [weather_score, price_score, crowd_score, events_score, seasonality_score]
            
            # Handle exceptions in individual score calculations
            weather_score, price_score, crowd_score, events_score, seasonality_score = scores
            
            # Check for exceptions and provide fallback scores
            if isinstance(weather_score, Exception):
                print(f"Weather score error: {weather_score}")
                weather_score = {"score": 50.0, "summary": "Weather data unavailable"}
            
            if isinstance(price_score, Exception):
                print(f"Price score error: {price_score}")
                price_score = {"score": 50.0, "summary": "Price data unavailable"}
            
            if isinstance(crowd_score, Exception):
                print(f"Crowd score error: {crowd_score}")
                crowd_score = {"score": 50.0, "summary": "Crowd data unavailable"}
            
            if isinstance(events_score, Exception):
                print(f"Events score error: {events_score}")
                events_score = {"score": 50.0, "summary": "Events data unavailable", "events": []}
            
            if isinstance(seasonality_score, Exception):
                print(f"Seasonality score error: {seasonality_score}")
                seasonality_score = {"score": 50.0, "summary": "Seasonality data unavailable"}
            
            # Calculate weighted total score
            total_score = (
                weather_score["score"] * self.weights["weather"] +
                price_score["score"] * self.weights["price"] +
                crowd_score["score"] * self.weights["crowd"] +
                events_score["score"] * self.weights["events"] +
                seasonality_score["score"] * self.weights["seasonality"]
            )
            
            # Determine label and reason
            label, reason = self._generate_label_and_reason(
                total_score, weather_score, price_score, crowd_score, events_score
            )
            
            return {
                "score": round(total_score, 1),
                "label": label,
                "reason": reason,
                "details": {
                    "weather_score": weather_score["score"],
                    "weather_summary": weather_score["summary"],
                    "price_score": price_score["score"],
                    "price_summary": price_score["summary"],
                    "crowd_score": crowd_score["score"],
                    "crowd_summary": crowd_score["summary"],
                    "events": events_score["events"],
                    "events_summary": events_score["summary"],
                    "breakdown": {
                        "weather": round(weather_score["score"] * self.weights["weather"], 1),
                        "price": round(price_score["score"] * self.weights["price"], 1),
                        "crowd": round(crowd_score["score"] * self.weights["crowd"], 1),
                        "events": round(events_score["score"] * self.weights["events"], 1),
                        "seasonality": round(seasonality_score["score"] * self.weights["seasonality"], 1)
                    }
                }
            }
            
        except Exception as e:
            print(f"Error calculating suitability score: {e}")
            return self._get_fallback_score(vibe, destination, start_date)
    
    async def _calculate_weather_score(self, vibe: str, dest_info: Dict, month: int) -> Dict[str, Any]:
        """Calculate weather comfort score (0-100)"""
        try:
            coordinates = dest_info.get("coordinates")
            if not coordinates:
                return {"score": 50.0, "summary": "Weather data unavailable"}
            
            lat, lon = coordinates
            climate_data = await self.weather_service.get_climate_normals(lat, lon, month)
            weather_analysis = self.weather_service.score_weather_comfort(climate_data, vibe)
            
            return {
                "score": weather_analysis["overall_score"],
                "summary": weather_analysis["summary"],
                "details": weather_analysis["breakdown"]
            }
        except Exception as e:
            print(f"Error calculating weather score: {e}")
            return {"score": 50.0, "summary": "Weather data unavailable"}
    
    async def _calculate_price_score(self, origin: str, destination: str, start_date: str, duration_days: int) -> Dict[str, Any]:
        """Calculate price favorability score (0-100)"""
        try:
            if not self.price_calendar or not origin:
                return {"score": 50.0, "summary": "Price data unavailable"}
            
            # Get price trends
            price_trends = await self.price_calendar.get_price_trends(
                origin, destination, start_date, duration_days, search_window_days=7
            )
            
            if not price_trends or "price_analysis" not in price_trends:
                return {"score": 50.0, "summary": "Price data unavailable"}
            
            analysis = price_trends["price_analysis"]
            target_price = analysis.get("target_price", 0)
            min_price = analysis.get("min_price", target_price)
            max_price = analysis.get("max_price", target_price)
            
            if max_price == min_price:
                return {"score": 50.0, "summary": "Price data unavailable"}
            
            # Score based on price position (lower is better)
            price_score = 100 * (1 - (target_price - min_price) / (max_price - min_price))
            price_score = max(0, min(100, price_score))
            
            # Generate summary
            if target_price <= min_price * 1.1:  # Within 10% of minimum
                summary = f"Great prices: ${target_price:.0f} (near lowest)"
            elif target_price <= (min_price + max_price) / 2:  # Below median
                summary = f"Good prices: ${target_price:.0f} (below average)"
            else:  # Above median
                summary = f"Higher prices: ${target_price:.0f} (above average)"
            
            return {"score": price_score, "summary": summary}
            
        except Exception as e:
            print(f"Error calculating price score: {e}")
            return {"score": 50.0, "summary": "Price data unavailable"}
    
    def _calculate_crowd_score(self, dest_info: Dict, month: int) -> Dict[str, Any]:
        """Calculate crowd level score (0-100)"""
        try:
            region = dest_info.get("region", "Unknown")
            hemisphere = dest_info.get("hemisphere", "north")
            
            # Base score
            score = 70.0
            summary = "Moderate crowds expected"
            
            # Adjust for hemisphere and season
            if hemisphere == "north":
                # Northern Hemisphere seasons
                if month in [6, 7, 8]:  # Summer
                    score -= 20
                    summary = "Peak summer crowds"
                elif month in [12, 1, 2]:  # Winter holidays
                    score -= 15
                    summary = "Holiday season crowds"
                elif month in [4, 5, 9, 10]:  # Shoulder seasons
                    score += 10
                    summary = "Shoulder season, fewer crowds"
            else:
                # Southern Hemisphere seasons (inverted)
                if month in [12, 1, 2]:  # Summer
                    score -= 20
                    summary = "Peak summer crowds"
                elif month in [6, 7, 8]:  # Winter holidays
                    score -= 15
                    summary = "Holiday season crowds"
                elif month in [3, 4, 9, 10]:  # Shoulder seasons
                    score += 10
                    summary = "Shoulder season, fewer crowds"
            
            # Adjust for major holidays
            if month == 12:  # Christmas/New Year
                score -= 10
                summary = "Holiday crowds expected"
            elif month == 4:  # Easter (varies by year)
                score -= 5
                summary = "Easter holiday crowds"
            
            # Adjust for region-specific peak seasons
            if region in ["Southeast Asia", "East Asia"] and month in [12, 1, 2]:
                score -= 10  # Peak tourist season
                summary = "Peak tourist season"
            elif region == "Europe" and month in [7, 8]:
                score -= 15  # European summer holidays
                summary = "European summer holiday crowds"
            
            return {
                "score": max(0, min(100, score)),
                "summary": summary
            }
            
        except Exception as e:
            print(f"Error calculating crowd score: {e}")
            return {"score": 50.0, "summary": "Crowd data unavailable"}
    
    def _calculate_events_score(self, vibe: str, dest_info: Dict, month: int) -> Dict[str, Any]:
        """Calculate events relevance score (0-100)"""
        try:
            # Get events for this destination and month
            events = self.region_mapper.get_events_for_vibe(dest_info, month, vibe)
            
            if not events:
                return {
                    "score": 50.0,
                    "summary": "No major events",
                    "events": []
                }
            
            # Score based on number and relevance of events
            base_score = 50.0
            event_bonus = min(30, len(events) * 10)  # Up to 30 points for events
            
            # Bonus for vibe-specific events
            vibe_bonus = 0
            for event in events:
                event_vibes = event.get("vibes", [])
                if vibe in event_vibes:
                    vibe_bonus += 10
            
            total_score = base_score + event_bonus + vibe_bonus
            total_score = min(100, total_score)
            
            # Generate summary
            event_names = [event.get("description", "Event") for event in events[:2]]
            if len(events) > 2:
                event_names.append(f"+{len(events)-2} more")
            
            summary = f"Events: {', '.join(event_names)}" if event_names else "No major events"
            
            return {
                "score": total_score,
                "summary": summary,
                "events": event_names
            }
            
        except Exception as e:
            print(f"Error calculating events score: {e}")
            return {"score": 50.0, "summary": "Events data unavailable", "events": []}
    
    def _calculate_seasonality_score(self, vibe: str, dest_info: Dict, month: int) -> Dict[str, Any]:
        """Calculate baseline seasonality score (0-100)"""
        try:
            region = dest_info.get("region", "Unknown")
            climate_zone = dest_info.get("climate_zone", "temperate")
            hemisphere = dest_info.get("hemisphere", "north")
            
            # Define optimal seasons for each vibe
            vibe_seasons = {
                "romantic": ["spring", "autumn"],
                "adventure": ["summer", "autumn"],
                "beach": ["summer"],
                "nature": ["spring", "autumn"],
                "cultural": ["autumn", "spring"],
                "culinary": ["autumn", "spring"],
                "wellness": ["winter", "spring"]
            }
            
            # Map month to season based on hemisphere
            if hemisphere == "north":
                season_map = {
                    12: "winter", 1: "winter", 2: "winter",
                    3: "spring", 4: "spring", 5: "spring",
                    6: "summer", 7: "summer", 8: "summer",
                    9: "autumn", 10: "autumn", 11: "autumn"
                }
            else:
                season_map = {
                    12: "summer", 1: "summer", 2: "summer",
                    3: "autumn", 4: "autumn", 5: "autumn",
                    6: "winter", 7: "winter", 8: "winter",
                    9: "spring", 10: "spring", 11: "spring"
                }
            
            current_season = season_map.get(month, "unknown")
            optimal_seasons = vibe_seasons.get(vibe, ["spring", "summer", "autumn"])
            
            if current_season in optimal_seasons:
                score = 90.0
                summary = f"Optimal {current_season} season"
            elif current_season == "unknown":
                score = 50.0
                summary = "Season data unavailable"
            else:
                score = 40.0
                summary = f"Non-optimal {current_season} season"
            
            # Adjust for climate zone
            if climate_zone == "tropical":
                # Tropical climates are more consistent year-round
                score = min(100, score + 10)
                summary += " (tropical climate)"
            
            return {
                "score": score,
                "summary": summary
            }
            
        except Exception as e:
            print(f"Error calculating seasonality score: {e}")
            return {"score": 50.0, "summary": "Seasonality data unavailable"}
    
    def _generate_label_and_reason(
        self, 
        total_score: float, 
        weather_score: Dict, 
        price_score: Dict, 
        crowd_score: Dict, 
        events_score: Dict
    ) -> tuple:
        """Generate label and reason based on total score and factors"""
        
        # Determine label
        if total_score >= 75:
            label = "✓ Optimal Season"
        elif total_score >= 50:
            label = "✔ Good Timing"
        else:
            label = "⚠ Consider Timing"
        
        # Generate reason based on top factors
        factors = [
            ("weather", weather_score["score"], weather_score["summary"]),
            ("price", price_score["score"], price_score["summary"]),
            ("crowd", crowd_score["score"], crowd_score["summary"]),
            ("events", events_score["score"], events_score["summary"])
        ]
        
        # Sort by score (descending)
        factors.sort(key=lambda x: x[1], reverse=True)
        
        # Build reason from top 2 factors
        top_factors = factors[:2]
        reason_parts = []
        
        for factor_name, score, summary in top_factors:
            if score >= 70:
                reason_parts.append(summary)
            elif score >= 50:
                reason_parts.append(summary)
        
        if reason_parts:
            reason = " • ".join(reason_parts[:2])  # Max 2 factors
        else:
            reason = "Mixed conditions for this vibe"
        
        return label, reason
    
    def _get_fallback_score(self, vibe: str, destination: str, start_date: str) -> Dict[str, Any]:
        """Fallback score when calculation fails"""
        return {
            "score": 50.0,
            "label": "✔ Good Timing",
            "reason": "Unable to analyze timing - consider checking weather and prices",
            "details": {
                "weather_score": 50.0,
                "weather_summary": "Data unavailable",
                "price_score": 50.0,
                "price_summary": "Data unavailable",
                "crowd_score": 50.0,
                "crowd_summary": "Data unavailable",
                "events": [],
                "events_summary": "Data unavailable",
                "breakdown": {
                    "weather": 20.0,
                    "price": 12.5,
                    "crowd": 7.5,
                    "events": 5.0,
                    "seasonality": 5.0
                }
            }
        }
