"""
Smart Airport Code Resolver
Automatically finds the nearest airport for any city
"""

import httpx
from typing import Optional, Dict, Tuple
import json
import re

class AirportResolver:
    """Intelligent airport code resolution using multiple strategies"""
    
    # Core airports for major cities (most commonly searched)
    CORE_CITY_MAP = {
        # Asia Pacific
        "tokyo": "HND", "osaka": "KIX", "singapore": "SIN", "bangkok": "BKK",
        "hong kong": "HKG", "kuala lumpur": "KUL", "manila": "MNL", "jakarta": "CGK",
        "delhi": "DEL", "mumbai": "BOM", "bangalore": "BLR", "chennai": "MAA",
        "colombo": "CMB", "kathmandu": "KTM", "dhaka": "DAC", "karachi": "KHI",
        "shanghai": "PVG", "beijing": "PEK", "guangzhou": "CAN", "shenzhen": "SZX",
        "seoul": "ICN", "taipei": "TPE", "sydney": "SYD", "melbourne": "MEL",
        
        # Sri Lanka - all cities use Colombo airport (CMB)
        "galle": "CMB", "kandy": "CMB", "negombo": "CMB", "trincomalee": "CMB",
        "batticaloa": "CMB", "matara": "CMB", "nuwara eliya": "CMB", "ella": "CMB",
        "anuradhapura": "CMB", "polonnaruwa": "CMB", "sigiriya": "CMB",
        "jaffna": "JAF",  # Jaffna has its own airport
        
        # North America
        "new york": "JFK", "los angeles": "LAX", "chicago": "ORD", "houston": "IAH",
        "san francisco": "SFO", "miami": "MIA", "boston": "BOS", "seattle": "SEA",
        "las vegas": "LAS", "orlando": "MCO", "atlanta": "ATL", "washington": "IAD",
        "toronto": "YYZ", "vancouver": "YVR", "montreal": "YUL", "mexico city": "MEX",
        
        # Europe
        "london": "LHR", "paris": "CDG", "berlin": "BER", "madrid": "MAD",
        "rome": "FCO", "amsterdam": "AMS", "frankfurt": "FRA", "munich": "MUC",
        "barcelona": "BCN", "milan": "MXP", "zurich": "ZRH", "vienna": "VIE",
        "istanbul": "IST", "athens": "ATH", "lisbon": "LIS", "copenhagen": "CPH",
        
        # Middle East & Africa
        "dubai": "DXB", "doha": "DOH", "abu dhabi": "AUH", "riyadh": "RUH",
        "jeddah": "JED", "cairo": "CAI", "johannesburg": "JNB", "cape town": "CPT",
        "nairobi": "NBO", "lagos": "LOS", "addis ababa": "ADD",
        
        # South America
        "sao paulo": "GRU", "rio de janeiro": "GIG", "buenos aires": "EZE",
        "lima": "LIM", "bogota": "BOG", "santiago": "SCL",
    }
    
    # Country to major airport mapping (fallback for unknown cities)
    COUNTRY_AIRPORTS = {
        "sri lanka": "CMB",
        "japan": "HND",
        "singapore": "SIN",
        "thailand": "BKK",
        "malaysia": "KUL",
        "indonesia": "CGK",
        "philippines": "MNL",
        "india": "DEL",
        "china": "PEK",
        "south korea": "ICN",
        "australia": "SYD",
        "united states": "JFK",
        "united kingdom": "LHR",
        "france": "CDG",
        "germany": "FRA",
        "italy": "FCO",
        "spain": "MAD",
        "uae": "DXB",
    }
    
    # City to country mapping for faster lookups
    CITY_TO_COUNTRY = {
        # Sri Lanka
        "galle": "Sri Lanka", "kandy": "Sri Lanka", "negombo": "Sri Lanka",
        "colombo": "Sri Lanka", "trincomalee": "Sri Lanka", "batticaloa": "Sri Lanka",
        "matara": "Sri Lanka", "nuwara eliya": "Sri Lanka", "ella": "Sri Lanka",
        "jaffna": "Sri Lanka", "anuradhapura": "Sri Lanka", "polonnaruwa": "Sri Lanka",
        
        # India
        "delhi": "India", "mumbai": "India", "bangalore": "India", "chennai": "India",
        "kolkata": "India", "hyderabad": "India", "pune": "India", "ahmedabad": "India",
        "jaipur": "India", "lucknow": "India", "goa": "India", "kochi": "India",
        
        # Japan
        "tokyo": "Japan", "osaka": "Japan", "kyoto": "Japan", "hiroshima": "Japan",
        "nagoya": "Japan", "sapporo": "Japan", "fukuoka": "Japan", "yokohama": "Japan",
        
        # USA
        "new york": "United States", "los angeles": "United States", "chicago": "United States",
        "houston": "United States", "san francisco": "United States", "miami": "United States",
        "boston": "United States", "seattle": "United States", "las vegas": "United States",
        
        # UK
        "london": "United Kingdom", "manchester": "United Kingdom", "birmingham": "United Kingdom",
        
        # China
        "beijing": "China", "shanghai": "China", "guangzhou": "China", "shenzhen": "China",
        
        # Add more as needed...
    }
    
    def __init__(self, serp_api_key: Optional[str] = None):
        self.serp_api_key = serp_api_key
        self._cache: Dict[str, str] = {}  # Cache resolved codes
        self._country_cache: Dict[str, str] = {}  # Cache country resolutions
    
    async def get_airport_code(self, city: str, country: Optional[str] = None) -> str:
        """
        Get airport code for a city using multiple intelligent strategies
        
        Args:
            city: City name (e.g., "Galle", "Tokyo")
            country: Optional country name for better resolution
            
        Returns:
            IATA airport code (e.g., "CMB", "HND")
        """
        # Normalize city name
        city_key = city.strip().lower()
        
        # Check cache first
        if city_key in self._cache:
            print(f"✈️ Resolved '{city}' → {self._cache[city_key]} (from cache)")
            return self._cache[city_key]
        
        # Strategy 1: Check if it's already an airport code
        if len(city.strip()) == 3 and city.strip().isalpha():
            code = self._normalize_airport_code(city.strip().upper())
            self._cache[city_key] = code
            return code
        
        # Strategy 2: Check core city map (covers 90% of searches)
        if city_key in self.CORE_CITY_MAP:
            code = self.CORE_CITY_MAP[city_key]
            print(f"✈️ Resolved '{city}' → {code} (from core map)")
            self._cache[city_key] = code
            return code
        
        # Strategy 3: Smart web search for "nearest airport"
        code = await self._search_nearest_airport(city, country)
        if code and code != "UNKNOWN":
            print(f"✈️ Resolved '{city}' → {code} (from smart search)")
            self._cache[city_key] = code
            return code
        
        # Strategy 4: Country fallback
        if country:
            country_key = country.strip().lower()
            if country_key in self.COUNTRY_AIRPORTS:
                code = self.COUNTRY_AIRPORTS[country_key]
                print(f"✈️ Resolved '{city}' → {code} (from country '{country}')")
                self._cache[city_key] = code
                return code
        
        # Strategy 5: Detect country from city and use country airport
        code = await self._detect_country_and_resolve(city)
        if code and code != "UNKNOWN":
            print(f"✈️ Resolved '{city}' → {code} (from detected country)")
            self._cache[city_key] = code
            return code
        
        print(f"⚠️ WARNING: Could not find airport for '{city}' - returning UNKNOWN")
        return "UNKNOWN"
    
    def _normalize_airport_code(self, code: str) -> str:
        """Normalize metro codes to primary airports"""
        metro_to_primary = {
            "NYC": "JFK", "LON": "LHR", "PAR": "CDG", "TYO": "HND",
            "OSA": "KIX", "SEL": "ICN", "ROM": "FCO", "MIL": "MXP",
            "WAS": "IAD", "CHI": "ORD", "SAO": "GRU", "BER": "BER",
        }
        return metro_to_primary.get(code, code)
    
    async def _search_nearest_airport(self, city: str, country: Optional[str] = None) -> Optional[str]:
        """Search for nearest airport using intelligent web search"""
        if not self.serp_api_key:
            return None
        
        # Build smart query
        if country:
            query = f"nearest international airport to {city} {country} IATA code"
        else:
            query = f"nearest airport to {city} IATA code"
        
        try:
            params = {
                "q": query,
                "api_key": self.serp_api_key,
                "engine": "google",
                "num": 5,
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://serpapi.com/search.json", params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse answer box first (most reliable)
                    if "answer_box" in data:
                        code = self._extract_code_from_text(str(data["answer_box"]))
                        if code:
                            return code
                    
                    # Parse organic results
                    for result in data.get("organic_results", [])[:3]:
                        text = f"{result.get('title', '')} {result.get('snippet', '')}"
                        code = self._extract_code_from_text(text)
                        if code and self._validate_airport_code(code):
                            return code
        
        except Exception as e:
            print(f"Web search error: {e}")
        
        return None
    
    async def _detect_country_and_resolve(self, city: str) -> Optional[str]:
        """Try to detect which country the city is in and use country's main airport"""
        if not self.serp_api_key:
            return None
        
        try:
            params = {
                "q": f"{city} country location",
                "api_key": self.serp_api_key,
                "engine": "google",
                "num": 3,
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://serpapi.com/search.json", params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    text = json.dumps(data).lower()
                    
                    # Check for country mentions
                    for country, airport in self.COUNTRY_AIRPORTS.items():
                        if country in text:
                            return airport
        
        except Exception:
            pass
        
        return None
    
    def _extract_code_from_text(self, text: str) -> Optional[str]:
        """Extract IATA code from text using smart patterns"""
        # Pattern 1: "(CODE)" or "[CODE]" or "CODE)"
        pattern1 = r'[\(\[]([A-Z]{3})[\)\]]'
        match = re.search(pattern1, text)
        if match:
            return match.group(1)
        
        # Pattern 2: "IATA: CODE" or "code CODE"
        pattern2 = r'(?:IATA|code|airport)[:\s]+([A-Z]{3})\b'
        match = re.search(pattern2, text, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        
        # Pattern 3: Just find 3-letter uppercase codes
        pattern3 = r'\b([A-Z]{3})\b'
        matches = re.findall(pattern3, text)
        for code in matches:
            if self._validate_airport_code(code):
                return code
        
        return None
    
    def _validate_airport_code(self, code: str) -> bool:
        """Validate if a code looks like a real airport code"""
        # Exclude common false positives
        excluded = {
            "THE", "AND", "FOR", "ARE", "YOU", "NOT", "BUT", "CAN",
            "ALL", "ONE", "TWO", "NEW", "OLD", "GET", "SET", "WAS",
            "HAS", "HAD", "MAY", "ITS", "OUR", "OUT", "NOW", "DAY",
            "USA", "EUR", "USD", "GBP", "WWW", "COM", "ORG", "NET",
        }
        return code not in excluded and len(code) == 3 and code.isalpha()
    
    async def get_country_for_city(self, city: str) -> Optional[str]:
        """
        Detect which country a city belongs to
        
        Args:
            city: City name
            
        Returns:
            Country name or None if not found
        """
        city_key = city.strip().lower()
        
        # Check cache first
        if city_key in self._country_cache:
            return self._country_cache[city_key]
        
        # Check static mapping
        if city_key in self.CITY_TO_COUNTRY:
            country = self.CITY_TO_COUNTRY[city_key]
            self._country_cache[city_key] = country
            return country
        
        # Try to detect using geocoding API
        country = await self._detect_country_from_api(city)
        if country:
            self._country_cache[city_key] = country
            return country
        
        return None
    
    async def _detect_country_from_api(self, city: str) -> Optional[str]:
        """Use Nominatim (OpenStreetMap) to detect country"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Use Nominatim geocoding API (free, no key required)
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
                        display_name = data[0].get("display_name", "")
                        # Country is usually the last part
                        parts = display_name.split(", ")
                        if parts:
                            country = parts[-1].strip()
                            print(f"🌍 Detected country for '{city}': {country}")
                            return country
        except Exception as e:
            print(f"⚠️ Error detecting country for '{city}': {e}")
        
        return None

