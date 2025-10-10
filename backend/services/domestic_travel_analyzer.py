"""
Dynamic Transportation Analyzer
Intelligently determines transportation strategy based on country characteristics
"""

import httpx
import math
import time
from typing import Dict, Any, List, Optional, Tuple
from services.config import Settings


class DynamicTransportationAnalyzer:
    """Dynamically determines transportation strategy based on country characteristics"""
    
    def __init__(self, settings: Settings = None):
        self.settings = settings or Settings()
        self.country_data_cache = {}
        
    async def get_country_transportation_strategy(self, country: str) -> Dict[str, Any]:
        """
        Dynamically calculate transportation strategy for any country
        
        Args:
            country: Country name (e.g., "Sri Lanka", "India")
            
        Returns:
            Dictionary with max_ground_distance_km, preferred_transport, and size category
        """
        # Get country data (area, population, infrastructure)
        country_info = await self._get_country_info(country)
        
        if not country_info:
            print(f"⚠️ Could not get country info for '{country}', using default strategy")
            return self._get_default_strategy()
        
        # Calculate max ground distance based on country size
        max_ground_distance = self._calculate_max_ground_distance(
            country_info['area_km2'],
            country_info['population_density']
        )
        
        # Determine preferred transport modes
        preferred_transport = self._determine_transport_modes(
            max_ground_distance,
            country_info['infrastructure_score']
        )
        
        size_category = self._categorize_country_size(country_info['area_km2'])
        
        print(f"🌍 Country Strategy for {country}:")
        print(f"   Area: {country_info['area_km2']:,.0f} km²")
        print(f"   Size Category: {size_category}")
        print(f"   Max Ground Distance: {max_ground_distance:.0f} km")
        print(f"   Preferred Transport: {', '.join(preferred_transport)}")
        
        return {
            "max_ground_distance_km": max_ground_distance,
            "preferred_transport": preferred_transport,
            "country_size_category": size_category,
            "area_km2": country_info['area_km2'],
            "infrastructure_score": country_info['infrastructure_score']
        }
    
    def _calculate_max_ground_distance(self, area_km2: float, population_density: float) -> float:
        """
        Calculate maximum practical ground travel distance
        
        Args:
            area_km2: Country area in square kilometers
            population_density: Population per square kilometer
            
        Returns:
            Maximum practical ground travel distance in kilometers
        """
        # Estimate country diameter (assuming roughly circular)
        diameter = math.sqrt((4 * area_km2) / math.pi)
        
        # Adjust based on population density
        # Dense countries = better infrastructure = longer ground travel feasible
        # Normalize density: 0-50 = low, 50-200 = medium, 200+ = high
        if population_density < 50:
            density_factor = 0.5  # Low density, limited infrastructure
        elif population_density < 200:
            density_factor = 0.8  # Medium density
        else:
            density_factor = 1.2  # High density, good infrastructure
        
        # Calculate max ground distance as percentage of diameter
        # Use 35% for small countries, scale down for larger ones
        size_factor = 0.35 if area_km2 < 100000 else 0.25
        max_distance = diameter * size_factor * density_factor
        
        # Apply reasonable bounds (50km minimum, 800km maximum)
        return max(50, min(800, max_distance))
    
    def _determine_transport_modes(self, max_distance: float, infrastructure_score: float) -> List[str]:
        """
        Determine preferred transportation modes based on distance and infrastructure
        
        Args:
            max_distance: Maximum practical ground travel distance
            infrastructure_score: Quality of infrastructure (0-1 scale)
            
        Returns:
            List of preferred transport modes in priority order
        """
        if max_distance < 200:
            # Small countries - ground transport preferred
            if infrastructure_score > 0.7:
                return ["train", "bus", "car"]
            else:
                return ["bus", "car", "train"]
        
        elif max_distance < 500:
            # Medium countries - mixed approach
            if infrastructure_score > 0.8:
                return ["train", "flight", "bus"]  # Good rail network
            else:
                return ["flight", "bus", "train"]
        
        else:
            # Large countries - flights preferred for long distances
            return ["flight", "train", "car"]
    
    def _categorize_country_size(self, area_km2: float) -> str:
        """Categorize country by size"""
        if area_km2 < 100000:
            return "small"
        elif area_km2 < 1000000:
            return "medium"
        else:
            return "large"
    
    async def _get_country_info(self, country: str) -> Optional[Dict[str, Any]]:
        """
        Get country information from external sources
        
        Args:
            country: Country name
            
        Returns:
            Dictionary with area, population, and infrastructure data
        """
        # Check cache first
        cache_key = country.lower().strip()
        if cache_key in self.country_data_cache:
            cached_data, timestamp = self.country_data_cache[cache_key]
            # Cache valid for 7 days
            if time.time() - timestamp < 7 * 24 * 60 * 60:
                return cached_data
        
        try:
            # Use REST Countries API (free, no auth required)
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"https://restcountries.com/v3.1/name/{country}",
                    params={"fullText": "false"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        country_data = data[0]
                        
                        area = country_data.get("area", 0)
                        population = country_data.get("population", 0)
                        population_density = population / max(area, 1)
                        
                        # Estimate infrastructure score
                        infrastructure_score = await self._estimate_infrastructure_score(
                            country,
                            country_data
                        )
                        
                        result = {
                            "area_km2": area,
                            "population": population,
                            "population_density": population_density,
                            "infrastructure_score": infrastructure_score
                        }
                        
                        # Cache the result
                        self.country_data_cache[cache_key] = (result, time.time())
                        
                        return result
        except Exception as e:
            print(f"⚠️ Error fetching country data for '{country}': {e}")
        
        return None
    
    async def _estimate_infrastructure_score(self, country: str, country_data: Dict[str, Any]) -> float:
        """
        Estimate infrastructure quality (0-1 scale)
        
        Uses heuristics based on:
        - Development status (developed/developing)
        - GDP per capita
        - Region
        
        Args:
            country: Country name
            country_data: Country data from REST Countries API
            
        Returns:
            Infrastructure score between 0 and 1
        """
        country_lower = country.lower()
        
        # Tier 1: Highly developed countries (0.85-0.95)
        highly_developed = [
            "japan", "germany", "france", "united kingdom", "netherlands",
            "switzerland", "norway", "sweden", "denmark", "finland",
            "austria", "belgium", "australia", "canada", "singapore",
            "south korea", "new zealand", "ireland", "luxembourg"
        ]
        
        # Tier 2: Developed countries with good infrastructure (0.75-0.85)
        developed = [
            "united states", "spain", "italy", "portugal", "greece",
            "israel", "united arab emirates", "qatar", "czech republic",
            "poland", "estonia", "slovenia", "taiwan", "hong kong"
        ]
        
        # Tier 3: Large developing countries with mixed infrastructure (0.6-0.75)
        large_developing = [
            "china", "india", "brazil", "russia", "mexico",
            "turkey", "indonesia", "thailand", "malaysia", "south africa"
        ]
        
        # Tier 4: Developing countries (0.4-0.6)
        developing = [
            "vietnam", "philippines", "egypt", "morocco", "colombia",
            "peru", "argentina", "chile", "romania", "bulgaria"
        ]
        
        # Check which tier the country belongs to
        if country_lower in highly_developed:
            return 0.9
        elif country_lower in developed:
            return 0.8
        elif country_lower in large_developing:
            return 0.7
        elif country_lower in developing:
            return 0.5
        
        # Default: estimate based on region and GDP
        try:
            region = country_data.get("region", "").lower()
            
            if region in ["europe", "northern europe", "western europe"]:
                return 0.7
            elif region in ["americas", "northern america"]:
                return 0.65
            elif region in ["asia", "eastern asia"]:
                return 0.6
            else:
                return 0.5
        except:
            return 0.5  # Conservative default
    
    def _get_default_strategy(self) -> Dict[str, Any]:
        """Default strategy for unknown countries"""
        return {
            "max_ground_distance_km": 300,  # Conservative default
            "preferred_transport": ["flight", "bus", "train"],
            "country_size_category": "unknown",
            "area_km2": 0,
            "infrastructure_score": 0.5
        }


class TransportationStrategyCache:
    """Cache transportation strategies to avoid repeated API calls"""
    
    _instance = None
    _cache = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TransportationStrategyCache, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.cache_duration = 24 * 60 * 60  # 24 hours
    
    async def get_strategy(self, country: str, settings: Settings = None) -> Dict[str, Any]:
        """
        Get cached strategy or calculate new one
        
        Args:
            country: Country name
            settings: Application settings
            
        Returns:
            Transportation strategy dictionary
        """
        cache_key = country.lower().strip()
        
        # Check cache
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self.cache_duration:
                print(f"✅ Using cached strategy for {country}")
                return cached_data
        
        # Calculate new strategy
        print(f"🔍 Calculating new strategy for {country}")
        analyzer = DynamicTransportationAnalyzer(settings)
        strategy = await analyzer.get_country_transportation_strategy(country)
        
        # Cache the result
        self._cache[cache_key] = (strategy, time.time())
        
        return strategy
    
    def clear_cache(self):
        """Clear the entire cache"""
        self._cache.clear()
        print("🗑️ Transportation strategy cache cleared")

