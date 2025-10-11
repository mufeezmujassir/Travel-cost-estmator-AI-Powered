from typing import Optional, Dict
import asyncio
from services.airport_resolver import AirportResolver
import logging

logger = logging.getLogger(__name__)

class RegionResolver:
    """Service to resolve city/destination to region (country) for trip pass matching"""
    
    def __init__(self, serp_api_key: str):
        self.airport_resolver = AirportResolver(serp_api_key)
        self._cache: Dict[str, str] = {}
    
    async def get_region_for_destination(self, destination: str) -> Optional[str]:
        """
        Get region (country) for a destination city.
        Uses country-level matching for trip passes.
        
        Args:
            destination: City or destination name
            
        Returns:
            Region identifier (country name) or None if cannot resolve
        """
        # Check cache first
        cache_key = destination.lower().strip()
        if cache_key in self._cache:
            logger.info(f"📋 Region cache hit for {destination}: {self._cache[cache_key]}")
            return self._cache[cache_key]
        
        try:
            # Use airport resolver to get country
            country = await self.airport_resolver.get_country_for_city(destination)
            
            if country and country != "Unknown":
                # Normalize country name for consistent matching
                region = country.strip().title()
                
                # Cache the result
                self._cache[cache_key] = region
                logger.info(f"✅ Resolved {destination} → Region: {region}")
                return region
            else:
                logger.warning(f"⚠️  Could not resolve region for {destination}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error resolving region for {destination}: {e}")
            return None
    
    async def are_same_region(self, destination1: str, destination2: str) -> bool:
        """
        Check if two destinations are in the same region (country).
        
        Args:
            destination1: First destination
            destination2: Second destination
            
        Returns:
            True if both destinations are in the same region
        """
        try:
            region1 = await self.get_region_for_destination(destination1)
            region2 = await self.get_region_for_destination(destination2)
            
            if region1 and region2:
                are_same = region1.lower() == region2.lower()
                logger.info(f"🔍 Region comparison: {destination1} ({region1}) vs {destination2} ({region2}) → Same: {are_same}")
                return are_same
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error comparing regions for {destination1} and {destination2}: {e}")
            return False
    
    def clear_cache(self):
        """Clear the region cache"""
        self._cache.clear()
        logger.info("🗑️  Region cache cleared")
    
    def get_cache_size(self) -> int:
        """Get number of cached regions"""
        return len(self._cache)
    
    def get_cached_regions(self) -> Dict[str, str]:
        """Get all cached regions (for debugging)"""
        return self._cache.copy()

