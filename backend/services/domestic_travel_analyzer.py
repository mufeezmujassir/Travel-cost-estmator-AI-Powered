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
                        
                        # Validate and fix data quality issues
                        area = self._validate_country_area(country, area)
                        population = self._validate_country_population(country, population)
                        
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
    
    def _validate_country_area(self, country: str, area: float) -> float:
        """Validate and fix country area data from REST Countries API"""
        country_lower = country.lower().strip()
        
        # Known correct areas for major countries (in km²)
        correct_areas = {
            "united states": 9833517,
            "usa": 9833517,
            "us": 9833517,
            "china": 9596961,
            "russia": 17125242,
            "canada": 9984670,
            "brazil": 8514877,
            "australia": 7692024,
            "india": 3287590,
            "argentina": 2780400,
            "kazakhstan": 2724900,
            "algeria": 2381741,
            "democratic republic of the congo": 2344858,
            "saudi arabia": 2149690,
            "mexico": 1964375,
            "indonesia": 1904569,
            "sudan": 1886068,
            "libya": 1759540,
            "iran": 1648195,
            "mongolia": 1564110,
            "peru": 1285216,
            "chad": 1284000,
            "niger": 1267000,
            "angola": 1246700,
            "mali": 1240192,
            "south africa": 1221037,
            "ethiopia": 1104300,
            "bolivia": 1098581,
            "mauritania": 1030700,
            "egypt": 1001449,
            "tanzania": 947303,
            "nigeria": 923768,
            "venezuela": 916445,
            "namibia": 824292,
            "mozambique": 801590,
            "pakistan": 796095,
            "turkey": 783562,
            "chile": 756102,
            "zambia": 752612,
            "myanmar": 676578,
            "afghanistan": 652230,
            "south sudan": 644329,
            "france": 643801,
            "somalia": 637657,
            "central african republic": 622984,
            "ukraine": 603550,
            "madagascar": 587041,
            "botswana": 581730,
            "kenya": 580367,
            "yemen": 527968,
            "thailand": 513120,
            "spain": 505992,
            "turkmenistan": 488100,
            "cameroon": 475442,
            "papua new guinea": 462840,
            "sweden": 450295,
            "uzbekistan": 447400,
            "morocco": 446550,
            "iraq": 438317,
            "paraguay": 406752,
            "zimbabwe": 390757,
            "norway": 385207,
            "japan": 377975,
            "germany": 357114,
            "republic of the congo": 342000,
            "finland": 338424,
            "vietnam": 331212,
            "malaysia": 330803,
            "poland": 312679,
            "oman": 309500,
            "italy": 301340,
            "philippines": 300000,
            "ecuador": 283561,
            "burkina faso": 274200,
            "new zealand": 270467,
            "gabon": 267668,
            "guinea": 245857,
            "united kingdom": 242900,
            "ghana": 238533,
            "romania": 238391,
            "laos": 236800,
            "uganda": 241550,
            "guyana": 214969,
            "belarus": 207600,
            "senegal": 196722,
            "syria": 185180,
            "cambodia": 181035,
            "uruguay": 176215,
            "tunisia": 163610,
            "suriname": 163820,
            "bangladesh": 147570,
            "nepal": 147181,
            "tajikistan": 143100,
            "greece": 131957,
            "nicaragua": 130373,
            "north korea": 120538,
            "malawi": 118484,
            "eritrea": 117600,
            "benin": 112622,
            "honduras": 112492,
            "liberia": 111369,
            "bulgaria": 110879,
            "cuba": 109884,
            "guatemala": 108889,
            "iceland": 103000,
            "south korea": 100210,
            "hungary": 93028,
            "portugal": 92090,
            "jordan": 89342,
            "azerbaijan": 86600,
            "austria": 83871,
            "united arab emirates": 83600,
            "czech republic": 78865,
            "panama": 75417,
            "sierra leone": 71740,
            "ireland": 70273,
            "georgia": 69700,
            "sri lanka": 65610,
            "lithuania": 65300,
            "latvia": 64559,
            "togo": 56785,
            "croatia": 56594,
            "bosnia and herzegovina": 51197,
            "costa rica": 51100,
            "slovakia": 49035,
            "dominican republic": 48671,
            "estonia": 45227,
            "denmark": 43094,
            "netherlands": 41850,
            "switzerland": 41277,
            "bhutan": 38394,
            "guinea-bissau": 36125,
            "taiwan": 36193,
            "moldova": 33846,
            "belgium": 30528,
            "lesotho": 30355,
            "armenia": 29743,
            "albania": 28748,
            "solomon islands": 28896,
            "equatorial guinea": 28051,
            "burundi": 27834,
            "haiti": 27750,
            "rwanda": 26338,
            "macedonia": 25713,
            "djibouti": 23200,
            "belize": 22966,
            "el salvador": 21041,
            "israel": 20770,
            "slovenia": 20273,
            "fiji": 18274,
            "kuwait": 17818,
            "swaziland": 17364,
            "east timor": 14874,
            "montenegro": 13812,
            "falkland islands": 12173,
            "vanuatu": 12189,
            "qatar": 11586,
            "gambia": 11295,
            "jamaica": 10991,
            "lebanon": 10452,
            "cyprus": 9251,
            "puerto rico": 8870,
            "brunei": 5765,
            "trinidad and tobago": 5130,
            "cape verde": 4033,
            "samoa": 2842,
            "luxembourg": 2586,
            "comoros": 2235,
            "mauritius": 2040,
            "sao tome and principe": 964,
            "kiribati": 811,
            "dominica": 751,
            "tonga": 747,
            "micronesia": 702,
            "singapore": 697,
            "bahrain": 665,
            "palau": 459,
            "seychelles": 455,
            "andorra": 468,
            "antigua and barbuda": 442,
            "barbados": 430,
            "saint vincent and the grenadines": 389,
            "grenada": 344,
            "malta": 316,
            "maldives": 300,
            "saint kitts and nevis": 261,
            "marshall islands": 181,
            "liechtenstein": 160,
            "san marino": 61,
            "tuvalu": 26,
            "nauru": 21,
            "monaco": 2,
            "vatican city": 0.44
        }
        
        # Check if we have a known correct area
        if country_lower in correct_areas:
            correct_area = correct_areas[country_lower]
            if abs(area - correct_area) / correct_area > 0.5:  # More than 50% difference
                print(f"🔧 Fixed area for {country}: {area} → {correct_area} km²")
                return correct_area
        
        return area
    
    def _validate_country_population(self, country: str, population: int) -> int:
        """Validate and fix country population data from REST Countries API"""
        country_lower = country.lower().strip()
        
        # Known correct populations for major countries
        correct_populations = {
            "united states": 331900000,
            "usa": 331900000,
            "us": 331900000,
            "china": 1439000000,
            "india": 1380000000,
            "indonesia": 273500000,
            "pakistan": 220900000,
            "brazil": 212600000,
            "nigeria": 206100000,
            "bangladesh": 164700000,
            "russia": 146200000,
            "mexico": 128900000,
            "japan": 125800000,
            "ethiopia": 114900000,
            "philippines": 109600000,
            "egypt": 102300000,
            "vietnam": 97340000,
            "turkey": 84340000,
            "iran": 83990000,
            "germany": 83190000,
            "thailand": 69799978,
            "united kingdom": 67886000,
            "france": 65270000,
            "italy": 60460000,
            "south africa": 59310000,
            "myanmar": 54410000,
            "kenya": 53770000,
            "uganda": 45740000,
            "algeria": 43850000,
            "sudan": 43850000,
            "iraq": 40220000,
            "canada": 37740000,
            "afghanistan": 38930000,
            "morocco": 36910000,
            "saudi arabia": 34810000,
            "peru": 32970000,
            "uzbekistan": 33470000,
            "malaysia": 32300000,
            "angola": 32870000,
            "mozambique": 31260000,
            "ghana": 31070000,
            "yemen": 29830000,
            "nepal": 29140000,
            "venezuela": 28440000,
            "madagascar": 27690000,
            "cameroon": 26550000,
            "ivory coast": 26380000,
            "north korea": 25780000,
            "australia": 25690000,
            "niger": 24200000,
            "sri lanka": 21919000,
            "burkina faso": 20900000,
            "mali": 20250000,
            "romania": 19240000,
            "malawi": 19130000,
            "chile": 19120000,
            "kazakhstan": 18780000,
            "zambia": 18380000,
            "guatemala": 17920000,
            "ecuador": 17640000,
            "syria": 17500000,
            "netherlands": 17130000,
            "senegal": 16740000,
            "cambodia": 16720000,
            "chad": 16430000,
            "somalia": 15890000,
            "zimbabwe": 14860000,
            "guinea": 13130000,
            "rwanda": 12950000,
            "benin": 12120000,
            "burundi": 11890000,
            "tunisia": 11820000,
            "bolivia": 11670000,
            "belgium": 11590000,
            "haiti": 11400000,
            "cuba": 11330000,
            "south sudan": 11190000,
            "dominican republic": 10850000,
            "czech republic": 10710000,
            "greece": 10420000,
            "jordan": 10200000,
            "portugal": 10190000,
            "azerbaijan": 10140000,
            "sweden": 10099000,
            "honduras": 9905000,
            "united arab emirates": 9890000,
            "hungary": 9660000,
            "tajikistan": 9538000,
            "belarus": 9449000,
            "austria": 9006000,
            "papua new guinea": 8947000,
            "serbia": 8737000,
            "israel": 8655000,
            "switzerland": 8655000,
            "togo": 8278000,
            "sierra leone": 7977000,
            "hong kong": 7497000,
            "laos": 7276000,
            "paraguay": 7133000,
            "libya": 6871000,
            "lebanon": 6825000,
            "jordan": 10200000,
            "nicaragua": 6624000,
            "kyrgyzstan": 6524000,
            "el salvador": 6486000,
            "turkmenistan": 6031000,
            "singapore": 5850000,
            "denmark": 5792000,
            "finland": 5541000,
            "slovakia": 5460000,
            "norway": 5421000,
            "oman": 5106000,
            "palestine": 4981000,
            "costa rica": 5094000,
            "liberia": 5057000,
            "ireland": 4938000,
            "central african republic": 4829000,
            "new zealand": 4822000,
            "mauritania": 4649000,
            "panama": 4314000,
            "kuwait": 4271000,
            "croatia": 4105000,
            "moldova": 4034000,
            "georgia": 3989000,
            "eritrea": 3546000,
            "uruguay": 3474000,
            "bosnia and herzegovina": 3281000,
            "mongolia": 3278000,
            "armenia": 2963000,
            "jamaica": 2961000,
            "qatar": 2881000,
            "albania": 2877000,
            "puerto rico": 2861000,
            "lithuania": 2722000,
            "namibia": 2541000,
            "gambia": 2417000,
            "botswana": 2352000,
            "gabon": 2225000,
            "lesotho": 2142000,
            "north macedonia": 2083000,
            "slovenia": 2079000,
            "guinea-bissau": 1968000,
            "latvia": 1886000,
            "bahrain": 1702000,
            "equatorial guinea": 1403000,
            "trinidad and tobago": 1399000,
            "estonia": 1326000,
            "mauritius": 1272000,
            "cyprus": 1207000,
            "eswatini": 1160000,
            "djibouti": 988000,
            "fiji": 896000,
            "réunion": 895000,
            "comoros": 869000,
            "guyana": 786000,
            "bhutan": 771000,
            "solomon islands": 686000,
            "macao": 649000,
            "montenegro": 628000,
            "luxembourg": 625000,
            "western sahara": 597000,
            "suriname": 586000,
            "cape verde": 555000,
            "malta": 441000,
            "brunei": 437000,
            "belize": 397000,
            "bahamas": 393000,
            "maldives": 540000,
            "iceland": 341000,
            "vanuatu": 307000,
            "barbados": 287000,
            "new caledonia": 285000,
            "french polynesia": 280000,
            "mayotte": 272000,
            "sao tome and principe": 219000,
            "samoa": 198000,
            "saint lucia": 183000,
            "channel islands": 173000,
            "guam": 168000,
            "kiribati": 119000,
            "micronesia": 115000,
            "tonga": 105000,
            "grenada": 112000,
            "saint vincent and the grenadines": 110000,
            "aruba": 106000,
            "united states virgin islands": 104000,
            "antigua and barbuda": 97000,
            "isle of man": 85000,
            "andorra": 77000,
            "dominica": 72000,
            "cayman islands": 65000,
            "bermuda": 62000,
            "marshall islands": 59000,
            "northern mariana islands": 57000,
            "greenland": 56000,
            "american samoa": 55000,
            "saint kitts and nevis": 53000,
            "faroe islands": 49000,
            "sint maarten": 40000,
            "monaco": 39000,
            "turks and caicos islands": 39000,
            "liechtenstein": 38000,
            "san marino": 34000,
            "gibraltar": 34000,
            "british virgin islands": 30000,
            "caribbean netherlands": 26000,
            "palau": 18000,
            "cook islands": 17000,
            "anguilla": 15000,
            "tuvalu": 12000,
            "wallis and futuna": 11000,
            "nauru": 11000,
            "saint helena": 6000,
            "saint pierre and miquelon": 6000,
            "montserrat": 5000,
            "falkland islands": 3000,
            "niue": 2600,
            "tokelau": 1400,
            "vatican city": 800
        }
        
        # Check if we have a known correct population
        if country_lower in correct_populations:
            correct_population = correct_populations[country_lower]
            if abs(population - correct_population) / correct_population > 0.5:  # More than 50% difference
                print(f"🔧 Fixed population for {country}: {population} → {correct_population}")
                return correct_population
        
        return population
    
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

