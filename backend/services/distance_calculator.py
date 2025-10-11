"""
Distance Calculator Service
Calculate distances between cities using multiple strategies
"""

import httpx
import math
from typing import Optional, Tuple
from services.config import Settings


class DistanceCalculator:
    """Calculate distances between cities using Google Maps or fallback methods"""
    
    def __init__(self, settings: Settings = None, gmaps_client=None):
        self.settings = settings or Settings()
        self.gmaps_client = gmaps_client
        self._distance_cache = {}
    
    async def calculate_distance(self, origin: str, destination: str) -> Optional[float]:
        """
        Calculate distance between two cities in kilometers
        
        Args:
            origin: Origin city name
            destination: Destination city name
            
        Returns:
            Distance in kilometers, or None if calculation fails
        """
        # Check cache
        cache_key = f"{origin.lower()}:{destination.lower()}"
        if cache_key in self._distance_cache:
            return self._distance_cache[cache_key]
        
        # Try Google Maps API first (most accurate)
        if self.gmaps_client:
            distance = await self._calculate_with_gmaps(origin, destination)
            if distance:
                self._distance_cache[cache_key] = distance
                print(f"📏 Distance {origin} → {destination}: {distance:.1f} km (Google Maps)")
                return distance
        
        # Fallback to geocoding + haversine formula
        distance = await self._calculate_with_geocoding(origin, destination)
        if distance:
            self._distance_cache[cache_key] = distance
            print(f"📏 Distance {origin} → {destination}: {distance:.1f} km (Geocoding)")
            return distance
        
        print(f"⚠️ Could not calculate distance between {origin} and {destination}")
        return None
    
    async def _calculate_with_gmaps(self, origin: str, destination: str) -> Optional[float]:
        """Calculate distance using Google Maps Distance Matrix API"""
        try:
            result = self.gmaps_client.distance_matrix(
                origins=[origin],
                destinations=[destination],
                mode="driving",
                units="metric"
            )
            
            if result['rows'][0]['elements'][0]['status'] == 'OK':
                distance_meters = result['rows'][0]['elements'][0]['distance']['value']
                return distance_meters / 1000  # Convert to km
        except Exception as e:
            print(f"Google Maps API error: {e}")
        
        return None
    
    async def _calculate_with_geocoding(self, origin: str, destination: str) -> Optional[float]:
        """Calculate distance using geocoding + haversine formula"""
        try:
            # Get coordinates for both cities
            origin_coords = await self._get_coordinates(origin)
            dest_coords = await self._get_coordinates(destination)
            
            if origin_coords and dest_coords:
                return self._haversine_distance(
                    origin_coords[0], origin_coords[1],
                    dest_coords[0], dest_coords[1]
                )
        except Exception as e:
            print(f"Geocoding error: {e}")
        
        return None
    
    async def _get_coordinates(self, city: str) -> Optional[Tuple[float, float]]:
        """Get latitude and longitude for a city using Nominatim"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={
                        "q": city,
                        "format": "json",
                        "limit": 1
                    },
                    headers={"User-Agent": "TravelEstimator/1.0"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        lat = float(data[0]['lat'])
                        lon = float(data[0]['lon'])
                        return (lat, lon)
        except Exception as e:
            print(f"Error getting coordinates for '{city}': {e}")
        
        return None
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points on Earth using Haversine formula
        
        Args:
            lat1, lon1: Coordinates of first point
            lat2, lon2: Coordinates of second point
            
        Returns:
            Distance in kilometers
        """
        # Earth's radius in kilometers
        R = 6371.0
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        
        return distance

