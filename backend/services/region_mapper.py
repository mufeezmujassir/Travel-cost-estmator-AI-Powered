"""
Region Mapper Service
Maps destination cities to regions, climate zones, and hemispheres for suitability scoring
"""

import httpx
from typing import Dict, Any, Optional, Tuple
import json
import os
from pathlib import Path

class RegionMapper:
    """Maps destinations to geographic and climatic information"""
    
    def __init__(self):
        self._coordinate_cache = {}
        self._region_cache = {}
        self._load_events_data()
    
    def _load_events_data(self):
        """Load seasonal events data for region mapping"""
        try:
            events_file = Path(__file__).parent.parent / "data" / "seasonal_events.json"
            with open(events_file, 'r', encoding='utf-8') as f:
                self.events_data = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load events data: {e}")
            self.events_data = []
    
    async def get_destination_info(self, destination: str) -> Dict[str, Any]:
        """
        Get comprehensive destination information including region, climate, and coordinates
        
        Args:
            destination: City name (e.g., "Tokyo", "Bangkok", "Paris")
            
        Returns:
            Dict with region, climate_zone, hemisphere, coordinates, and country
        """
        # Check cache first
        cache_key = destination.lower().strip()
        if cache_key in self._region_cache:
            return self._region_cache[cache_key]
        
        try:
            # Get coordinates first
            coordinates = await self._get_coordinates(destination)
            if not coordinates:
                return self._get_fallback_info(destination)
            
            lat, lon = coordinates
            
            # Determine hemisphere
            hemisphere = "north" if lat >= 0 else "south"
            
            # Map to region and climate zone
            region_info = self._map_coordinates_to_region(lat, lon)
            
            result = {
                "destination": destination,
                "coordinates": coordinates,
                "latitude": lat,
                "longitude": lon,
                "hemisphere": hemisphere,
                "region": region_info["region"],
                "climate_zone": region_info["climate_zone"],
                "country": region_info.get("country", "Unknown")
            }
            
            # Cache the result
            self._region_cache[cache_key] = result
            return result
            
        except Exception as e:
            print(f"Error getting destination info for {destination}: {e}")
            return self._get_fallback_info(destination)
    
    async def _get_coordinates(self, city: str) -> Optional[Tuple[float, float]]:
        """Get latitude and longitude for a city using Nominatim"""
        # Check coordinate cache
        cache_key = city.lower().strip()
        if cache_key in self._coordinate_cache:
            return self._coordinate_cache[cache_key]
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={
                        "q": city,
                        "format": "json",
                        "limit": 1,
                        "addressdetails": 1
                    },
                    headers={"User-Agent": "TravelEstimator/1.0"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        lat = float(data[0]['lat'])
                        lon = float(data[0]['lon'])
                        coordinates = (lat, lon)
                        self._coordinate_cache[cache_key] = coordinates
                        return coordinates
        except Exception as e:
            print(f"Error getting coordinates for '{city}': {e}")
        
        return None
    
    def _map_coordinates_to_region(self, lat: float, lon: float) -> Dict[str, str]:
        """Map coordinates to region and climate zone"""
        
        # Define region boundaries (simplified)
        regions = {
            "Southeast Asia": {
                "bounds": {"lat_min": -10, "lat_max": 30, "lon_min": 90, "lon_max": 150},
                "climate_zone": "tropical",
                "countries": ["Thailand", "Vietnam", "Malaysia", "Singapore", "Indonesia", "Philippines", "Cambodia", "Laos", "Myanmar"]
            },
            "East Asia": {
                "bounds": {"lat_min": 20, "lat_max": 60, "lon_min": 100, "lon_max": 150},
                "climate_zone": "temperate",
                "countries": ["Japan", "South Korea", "China", "Taiwan", "Hong Kong", "Macau"]
            },
            "Europe": {
                "bounds": {"lat_min": 35, "lat_max": 70, "lon_min": -25, "lon_max": 45},
                "climate_zone": "temperate",
                "countries": ["France", "Germany", "Italy", "Spain", "United Kingdom", "Netherlands", "Belgium", "Switzerland", "Austria", "Portugal", "Greece", "Poland", "Czech Republic", "Hungary", "Croatia", "Ireland", "Denmark", "Sweden", "Norway", "Finland"]
            },
            "North America": {
                "bounds": {"lat_min": 15, "lat_max": 70, "lon_min": -170, "lon_max": -50},
                "climate_zone": "temperate",
                "countries": ["United States", "Canada", "Mexico"]
            },
            "South America": {
                "bounds": {"lat_min": -60, "lat_max": 15, "lon_min": -85, "lon_max": -30},
                "climate_zone": "tropical",
                "countries": ["Brazil", "Argentina", "Chile", "Peru", "Colombia", "Venezuela", "Ecuador", "Bolivia", "Paraguay", "Uruguay"]
            },
            "Africa": {
                "bounds": {"lat_min": -35, "lat_max": 40, "lon_min": -20, "lon_max": 55},
                "climate_zone": "tropical",
                "countries": ["South Africa", "Kenya", "Tanzania", "Morocco", "Egypt", "Nigeria", "Ghana", "Ethiopia", "Uganda", "Rwanda"]
            },
            "Oceania": {
                "bounds": {"lat_min": -50, "lat_max": 0, "lon_min": 110, "lon_max": 180},
                "climate_zone": "temperate",
                "countries": ["Australia", "New Zealand", "Fiji", "Papua New Guinea"]
            }
        }
        
        # Find matching region
        for region_name, region_data in regions.items():
            bounds = region_data["bounds"]
            if (bounds["lat_min"] <= lat <= bounds["lat_max"] and 
                bounds["lon_min"] <= lon <= bounds["lon_max"]):
                return {
                    "region": region_name,
                    "climate_zone": region_data["climate_zone"],
                    "countries": region_data["countries"]
                }
        
        # Default fallback
        if lat > 23.5:
            return {"region": "Northern Hemisphere", "climate_zone": "temperate"}
        elif lat < -23.5:
            return {"region": "Southern Hemisphere", "climate_zone": "temperate"}
        else:
            return {"region": "Tropical Zone", "climate_zone": "tropical"}
    
    def _get_fallback_info(self, destination: str) -> Dict[str, Any]:
        """Fallback when geocoding fails"""
        return {
            "destination": destination,
            "coordinates": None,
            "latitude": None,
            "longitude": None,
            "hemisphere": "unknown",
            "region": "Unknown",
            "climate_zone": "temperate",
            "country": "Unknown"
        }
    
    def get_events_for_destination(self, destination_info: Dict[str, Any], month: int) -> list:
        """Get relevant events for a destination and month"""
        region = destination_info.get("region", "Unknown")
        climate_zone = destination_info.get("climate_zone", "temperate")
        
        matching_events = []
        for event in self.events_data:
            if (event.get("region") == region and 
                event.get("month") == month):
                matching_events.append(event)
        
        return matching_events
    
    def get_events_for_vibe(self, destination_info: Dict[str, Any], month: int, vibe: str) -> list:
        """Get events that match both destination/month and vibe preference"""
        all_events = self.get_events_for_destination(destination_info, month)
        
        # Filter by vibe compatibility
        vibe_events = []
        for event in all_events:
            event_vibes = event.get("vibes", [])
            if vibe in event_vibes or not event_vibes:  # Include if vibe matches or no vibe specified
                vibe_events.append(event)
        
        return vibe_events
