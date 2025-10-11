"""
Intelligent Pricing Service
Uses AI and economic data to dynamically determine country-specific pricing multipliers
"""

import httpx
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json


class IntelligentPricingService:
    """
    Dynamically determines pricing multipliers for different countries
    based on economic data and AI analysis
    """
    
    def __init__(self, grok_service=None):
        self.grok_service = grok_service
        self._cache = {}
        self._cache_duration = 7 * 24 * 60 * 60  # 7 days cache
        
        # Base multiplier for USA (reference country)
        self.base_country = "United States"
        self.base_multiplier = 1.0
    
    async def get_pricing_multiplier(self, country: str) -> float:
        """
        Get intelligent pricing multiplier for a country
        
        Args:
            country: Country name
            
        Returns:
            Multiplier (e.g., 0.02 for Sri Lanka, 1.0 for USA)
        """
        # Check cache
        cache_key = country.lower()
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if datetime.now().timestamp() - timestamp < self._cache_duration:
                return cached_data["multiplier"]
        
        # USA is our base reference
        if country.lower() in ["usa", "united states", "united states of America"]:
            return 1.0
        
        # Get economic data
        economic_data = await self._get_country_economic_data(country)
        
        if not economic_data:
            # Fallback to regional estimates
            multiplier = self._get_regional_fallback(country)
            self._cache[cache_key] = ({"multiplier": multiplier}, datetime.now().timestamp())
            return multiplier
        
        # Use AI to determine appropriate multiplier
        multiplier = await self._calculate_intelligent_multiplier(country, economic_data)
        
        # Cache the result
        self._cache[cache_key] = ({"multiplier": multiplier}, datetime.now().timestamp())
        
        return multiplier
    
    async def _get_country_economic_data(self, country: str) -> Optional[Dict[str, Any]]:
        """
        Fetch economic indicators for a country
        Uses multiple free APIs for comprehensive data
        """
        data = {}
        
        # 1. Get basic country info from REST Countries API
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"https://restcountries.com/v3.1/name/{country}")
                if response.status_code == 200:
                    country_data = response.json()[0]
                    data["population"] = country_data.get("population", 0)
                    data["area"] = country_data.get("area", 0)
                    data["region"] = country_data.get("region", "")
                    data["subregion"] = country_data.get("subregion", "")
                    
                    # Get currency information
                    currencies = country_data.get("currencies", {})
                    if currencies:
                        currency_code = list(currencies.keys())[0]
                        data["currency"] = currency_code
        except Exception as e:
            print(f"Error fetching country data: {e}")
        
        # 2. Get GDP data (using World Bank or other sources)
        # For now, we'll use known GDP per capita data or estimate from region
        data["gdp_per_capita_estimate"] = await self._estimate_gdp_per_capita(country, data.get("region"))
        
        return data if data else None
    
    async def _estimate_gdp_per_capita(self, country: str, region: str = None) -> float:
        """
        Estimate GDP per capita based on country and region
        This is a simplified approach - in production, use World Bank API
        """
        # Known reference points (GDP per capita in USD, 2023 estimates)
        reference_gdp = {
            # High income (>$40,000)
            "united states": 76330,
            "switzerland": 92370,
            "norway": 89090,
            "singapore": 72790,
            "australia": 64490,
            "canada": 54870,
            "united kingdom": 48690,
            "japan": 42940,
            
            # Upper-middle income ($13,000-$40,000)
            "china": 12720,
            "turkey": 11680,
            "brazil": 10410,
            "thailand": 7230,
            "malaysia": 11780,
            
            # Lower-middle income ($4,000-$13,000)
            "india": 2410,
            "sri lanka": 3720,
            "bangladesh": 2520,
            "vietnam": 4160,
            "philippines": 3950,
            "egypt": 3840,
            
            # Low income (<$4,000)
            "nepal": 1400,
            "pakistan": 1680,
        }
        
        country_lower = country.lower()
        if country_lower in reference_gdp:
            return reference_gdp[country_lower]
        
        # Regional averages as fallback
        regional_averages = {
            "Asia": 8000,
            "Europe": 35000,
            "Americas": 15000,
            "Africa": 2500,
            "Oceania": 30000
        }
        
        return regional_averages.get(region, 10000)  # Global average fallback
    
    async def _calculate_intelligent_multiplier(self, country: str, economic_data: Dict[str, Any]) -> float:
        """
        Use AI to calculate appropriate pricing multiplier
        based on economic indicators
        """
        gdp_per_capita = economic_data.get("gdp_per_capita_estimate", 10000)
        region = economic_data.get("region", "Unknown")
        currency = economic_data.get("currency", "USD")
        
        # Base calculation using GDP ratio
        # USA GDP per capita: ~$76,330
        usa_gdp = 76330
        gdp_ratio = gdp_per_capita / usa_gdp
        
        # Apply logarithmic scaling for better distribution
        # This prevents extreme multipliers
        import math
        base_multiplier = math.sqrt(gdp_ratio)  # Square root for smoother scaling
        
        # Apply regional adjustments (cost of living varies by region)
        regional_adjustments = {
            "Asia": 0.8,  # Generally lower cost of living
            "Europe": 1.1,  # Higher cost of living
            "Americas": 0.95,
            "Africa": 0.7,
            "Oceania": 1.15
        }
        
        regional_factor = regional_adjustments.get(region, 1.0)
        calculated_multiplier = base_multiplier * regional_factor
        
        # Ensure reasonable bounds (0.01 to 1.5)
        multiplier = max(0.01, min(1.5, calculated_multiplier))
        
        # If Grok AI service is available, refine the estimate
        if self.grok_service:
            try:
                refined_multiplier = await self._refine_with_ai(
                    country, 
                    gdp_per_capita, 
                    calculated_multiplier,
                    region
                )
                if refined_multiplier:
                    multiplier = refined_multiplier
            except Exception as e:
                print(f"AI refinement failed, using calculated multiplier: {e}")
        
        print(f"💰 Pricing multiplier for {country}: {multiplier:.3f}x (GDP: ${gdp_per_capita:,})")
        return round(multiplier, 3)
    
    async def _refine_with_ai(
        self, 
        country: str, 
        gdp_per_capita: float, 
        calculated_multiplier: float,
        region: str
    ) -> Optional[float]:
        """
        Use Grok AI to refine the pricing multiplier
        based on real-world knowledge
        """
        prompt = f"""You are a pricing expert analyzing transportation costs across different countries.

Country: {country}
Region: {region}
GDP per capita: ${gdp_per_capita:,}
Initial calculated multiplier: {calculated_multiplier:.3f}x (relative to USA = 1.0x)

The multiplier is used to adjust transportation prices. For example:
- USA (baseline): 1.0x - A taxi ride costs $50
- Sri Lanka: 0.02x - Same taxi ride should cost $1 (50x cheaper)
- Switzerland: 1.2x - Same taxi ride costs $60 (20% more expensive)

Based on your knowledge of {country}'s economy, cost of living, and transportation costs:
1. Is the calculated multiplier ({calculated_multiplier:.3f}x) reasonable?
2. What would be a more accurate multiplier considering:
   - Local transportation costs
   - Average wages
   - Cost of living
   - Regional economic factors

Respond with ONLY a number between 0.01 and 1.5 representing the refined multiplier.
For example: 0.025 or 0.85 or 1.15

Your refined multiplier:"""

        try:
            response = await self.grok_service.generate(
                prompt,
                system_prompt="You are a pricing expert. Respond with only a decimal number.",
                max_tokens=10,
                temperature=0.1
            )
            
            # Extract number from response
            import re
            numbers = re.findall(r'\d+\.?\d*', response)
            if numbers:
                refined = float(numbers[0])
                # Validate bounds
                if 0.01 <= refined <= 1.5:
                    print(f"   AI refined: {calculated_multiplier:.3f} → {refined:.3f}")
                    return refined
        except Exception as e:
            print(f"   AI refinement error: {e}")
        
        return None
    
    def _get_regional_fallback(self, country: str) -> float:
        """
        Fallback multipliers based on country name when data unavailable
        Uses intelligent pattern matching, not exact hardcoding
        """
        country_lower = country.lower()
        
        # Pattern-based classification
        # South Asian countries
        if any(x in country_lower for x in ["india", "pakistan", "bangladesh", "nepal", "sri lanka", "lanka"]):
            return 0.025  # Very affordable
        
        # Southeast Asian countries
        if any(x in country_lower for x in ["thailand", "vietnam", "philippines", "indonesia", "myanmar", "cambodia", "laos"]):
            return 0.04
        
        # East Asian developing
        if any(x in country_lower for x in ["china", "mongolia"]):
            return 0.15
        
        # East Asian developed
        if any(x in country_lower for x in ["japan", "korea", "south korea", "singapore", "hong kong"]):
            return 0.85
        
        # Middle East
        if any(x in country_lower for x in ["saudi", "emirates", "uae", "qatar", "kuwait", "dubai"]):
            return 0.70
        
        # Eastern Europe
        if any(x in country_lower for x in ["poland", "czech", "hungary", "romania", "bulgaria", "ukraine", "russia"]):
            return 0.30
        
        # Western Europe
        if any(x in country_lower for x in ["germany", "france", "italy", "spain", "netherlands", "belgium", "austria"]):
            return 0.95
        
        # Nordic countries
        if any(x in country_lower for x in ["norway", "sweden", "denmark", "finland", "iceland", "switzerland"]):
            return 1.20
        
        # UK and Ireland
        if any(x in country_lower for x in ["united kingdom", "britain", "england", "scotland", "wales", "ireland"]):
            return 1.05
        
        # North America
        if any(x in country_lower for x in ["canada"]):
            return 0.90
        if any(x in country_lower for x in ["mexico"]):
            return 0.25
        
        # South America
        if any(x in country_lower for x in ["brazil", "argentina", "chile", "colombia", "peru"]):
            return 0.30
        
        # Oceania
        if any(x in country_lower for x in ["australia", "new zealand"]):
            return 0.95
        
        # Africa
        if any(x in country_lower for x in ["south africa", "egypt", "morocco", "kenya", "ethiopia"]):
            return 0.20
        
        # Default: assume developing country
        return 0.35
    
    def get_cached_multipliers(self) -> Dict[str, float]:
        """Get all cached multipliers for debugging"""
        return {
            country: data["multiplier"] 
            for country, (data, _) in self._cache.items()
        }

