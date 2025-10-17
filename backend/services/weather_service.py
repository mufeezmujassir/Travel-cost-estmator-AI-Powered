"""
Weather Service
Integrates with Open-Meteo API to get historical climate data and score weather comfort for different vibes
"""

import httpx
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio

class WeatherService:
    """Service for weather data and comfort scoring"""
    
    def __init__(self):
        self.base_url = "https://archive-api.open-meteo.com/v1/archive"
        self._cache = {}
        self._cache_duration = 24 * 60 * 60  # 24 hours in seconds
    
    async def get_climate_normals(self, lat: float, lon: float, month: int) -> Dict[str, Any]:
        """
        Get historical climate normals for a location and month
        
        Args:
            lat: Latitude
            lon: Longitude  
            month: Month (1-12)
            
        Returns:
            Dict with temperature, precipitation, and other climate data
        """
        cache_key = f"{lat:.2f},{lon:.2f},{month}"
        
        # Check cache
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if datetime.now().timestamp() - timestamp < self._cache_duration:
                return cached_data
        
        try:
            # Calculate date range for the month (use last 5 years for normals)
            current_year = datetime.now().year
            start_date = f"{current_year-5}-{month:02d}-01"
            
            # Get last day of month
            if month == 12:
                end_date = f"{current_year-5}-12-31"
            else:
                next_month = month + 1
                end_date = f"{current_year-5}-{next_month:02d}-01"
                end_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
            
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date,
                "end_date": end_date,
                "daily": "temperature_2m_mean,precipitation_sum,relative_humidity_2m_mean,wind_speed_10m_mean,sunshine_duration",
                "timezone": "auto"
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(self.base_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    climate_data = self._process_climate_data(data, month)
                    
                    # Cache the result
                    self._cache[cache_key] = (climate_data, datetime.now().timestamp())
                    return climate_data
                else:
                    print(f"Weather API error: {response.status_code}")
                    return self._get_fallback_climate_data(month)
                    
        except Exception as e:
            print(f"Error fetching climate data: {e}")
            return self._get_fallback_climate_data(month)
    
    def _process_climate_data(self, api_data: Dict, month: int) -> Dict[str, Any]:
        """Process raw API data into climate normals"""
        daily_data = api_data.get("daily", {})
        
        if not daily_data:
            return self._get_fallback_climate_data(month)
        
        # Calculate averages
        temps = [t for t in daily_data.get("temperature_2m_mean", []) if t is not None]
        precip = [p for p in daily_data.get("precipitation_sum", []) if p is not None]
        humidity = [h for h in daily_data.get("relative_humidity_2m_mean", []) if h is not None]
        wind = [w for w in daily_data.get("wind_speed_10m_mean", []) if w is not None]
        sunshine = [s for s in daily_data.get("sunshine_duration", []) if s is not None]
        
        return {
            "avg_temperature": sum(temps) / len(temps) if temps else 20.0,
            "avg_precipitation": sum(precip) / len(precip) if precip else 0.0,
            "avg_humidity": sum(humidity) / len(humidity) if humidity else 60.0,
            "avg_wind_speed": sum(wind) / len(wind) if wind else 5.0,
            "avg_sunshine_hours": (sum(sunshine) / len(sunshine) / 3600) if sunshine else 8.0,  # Convert seconds to hours
            "month": month,
            "data_points": len(temps)
        }
    
    def _get_fallback_climate_data(self, month: int) -> Dict[str, Any]:
        """Fallback climate data when API fails"""
        # Simple seasonal estimates
        seasonal_temps = {
            1: 5, 2: 7, 3: 12, 4: 18, 5: 23, 6: 27,
            7: 30, 8: 29, 9: 24, 10: 18, 11: 12, 12: 7
        }
        
        return {
            "avg_temperature": seasonal_temps.get(month, 20.0),
            "avg_precipitation": 2.0,
            "avg_humidity": 65.0,
            "avg_wind_speed": 5.0,
            "avg_sunshine_hours": 7.0,
            "month": month,
            "data_points": 0
        }
    
    def score_weather_comfort(self, climate_data: Dict[str, Any], vibe: str) -> Dict[str, Any]:
        """
        Score weather comfort for a specific vibe
        
        Args:
            climate_data: Climate normals from get_climate_normals
            vibe: Vibe type (romantic, adventure, beach, etc.)
            
        Returns:
            Dict with comfort score (0-100) and breakdown
        """
        temp = climate_data["avg_temperature"]
        precip = climate_data["avg_precipitation"]
        humidity = climate_data["avg_humidity"]
        wind = climate_data["avg_wind_speed"]
        sunshine = climate_data["avg_sunshine_hours"]
        
        # Define comfort criteria for each vibe
        vibe_criteria = {
            "romantic": {
                "temp_ideal": (18, 26),
                "temp_acceptable": (12, 32),
                "precip_max": 3.0,
                "humidity_max": 80,
                "wind_max": 15,
                "sunshine_min": 4
            },
            "adventure": {
                "temp_ideal": (15, 25),
                "temp_acceptable": (5, 35),
                "precip_max": 5.0,
                "humidity_max": 70,
                "wind_max": 20,
                "sunshine_min": 3
            },
            "beach": {
                "temp_ideal": (25, 32),
                "temp_acceptable": (20, 38),
                "precip_max": 2.0,
                "humidity_max": 85,
                "wind_max": 25,
                "sunshine_min": 7
            },
            "nature": {
                "temp_ideal": (12, 24),
                "temp_acceptable": (0, 30),
                "precip_max": 8.0,
                "humidity_max": 90,
                "wind_max": 20,
                "sunshine_min": 2
            },
            "cultural": {
                "temp_ideal": (15, 28),
                "temp_acceptable": (5, 35),
                "precip_max": 6.0,
                "humidity_max": 85,
                "wind_max": 20,
                "sunshine_min": 3
            },
            "culinary": {
                "temp_ideal": (18, 28),
                "temp_acceptable": (10, 35),
                "precip_max": 10.0,
                "humidity_max": 90,
                "wind_max": 25,
                "sunshine_min": 2
            },
            "wellness": {
                "temp_ideal": (20, 28),
                "temp_acceptable": (15, 32),
                "precip_max": 4.0,
                "humidity_max": 75,
                "wind_max": 15,
                "sunshine_min": 5
            }
        }
        
        criteria = vibe_criteria.get(vibe, vibe_criteria["cultural"])
        
        # Score each factor (0-100)
        temp_score = self._score_temperature(temp, criteria["temp_ideal"], criteria["temp_acceptable"])
        precip_score = self._score_precipitation(precip, criteria["precip_max"])
        humidity_score = self._score_humidity(humidity, criteria["humidity_max"])
        wind_score = self._score_wind(wind, criteria["wind_max"])
        sunshine_score = self._score_sunshine(sunshine, criteria["sunshine_min"])
        
        # Weighted overall score
        overall_score = (
            temp_score * 0.35 +
            precip_score * 0.25 +
            humidity_score * 0.15 +
            wind_score * 0.10 +
            sunshine_score * 0.15
        )
        
        return {
            "overall_score": round(overall_score, 1),
            "temperature_score": round(temp_score, 1),
            "precipitation_score": round(precip_score, 1),
            "humidity_score": round(humidity_score, 1),
            "wind_score": round(wind_score, 1),
            "sunshine_score": round(sunshine_score, 1),
            "summary": self._generate_weather_summary(temp, precip, humidity, sunshine, overall_score),
            "breakdown": {
                "temperature": f"{temp:.1f}°C",
                "precipitation": f"{precip:.1f}mm/day",
                "humidity": f"{humidity:.0f}%",
                "wind": f"{wind:.1f}km/h",
                "sunshine": f"{sunshine:.1f}h/day"
            }
        }
    
    def _score_temperature(self, temp: float, ideal_range: Tuple[float, float], acceptable_range: Tuple[float, float]) -> float:
        """Score temperature comfort (0-100)"""
        ideal_min, ideal_max = ideal_range
        acceptable_min, acceptable_max = acceptable_range
        
        if ideal_min <= temp <= ideal_max:
            return 100.0
        elif acceptable_min <= temp <= acceptable_max:
            # Linear interpolation within acceptable range
            if temp < ideal_min:
                return 50 + 50 * (temp - acceptable_min) / (ideal_min - acceptable_min)
            else:
                return 50 + 50 * (acceptable_max - temp) / (acceptable_max - ideal_max)
        else:
            # Outside acceptable range
            if temp < acceptable_min:
                return max(0, 50 * (temp - acceptable_min + 10) / 10)
            else:
                return max(0, 50 * (acceptable_max + 10 - temp) / 10)
    
    def _score_precipitation(self, precip: float, max_acceptable: float) -> float:
        """Score precipitation comfort (0-100)"""
        if precip <= max_acceptable:
            return 100.0
        else:
            return max(0, 100 - (precip - max_acceptable) * 10)
    
    def _score_humidity(self, humidity: float, max_acceptable: float) -> float:
        """Score humidity comfort (0-100)"""
        if humidity <= max_acceptable:
            return 100.0
        else:
            return max(0, 100 - (humidity - max_acceptable) * 2)
    
    def _score_wind(self, wind: float, max_acceptable: float) -> float:
        """Score wind comfort (0-100)"""
        if wind <= max_acceptable:
            return 100.0
        else:
            return max(0, 100 - (wind - max_acceptable) * 3)
    
    def _score_sunshine(self, sunshine: float, min_acceptable: float) -> float:
        """Score sunshine comfort (0-100)"""
        if sunshine >= min_acceptable:
            return 100.0
        else:
            return max(0, sunshine / min_acceptable * 100)
    
    def _generate_weather_summary(self, temp: float, precip: float, humidity: float, sunshine: float, score: float) -> str:
        """Generate a human-readable weather summary"""
        if score >= 80:
            return f"Excellent weather: {temp:.0f}°C, {sunshine:.0f}h sunshine"
        elif score >= 60:
            return f"Good weather: {temp:.0f}°C, {precip:.1f}mm rain"
        elif score >= 40:
            return f"Moderate weather: {temp:.0f}°C, {precip:.1f}mm rain"
        else:
            return f"Challenging weather: {temp:.0f}°C, {precip:.1f}mm rain"
