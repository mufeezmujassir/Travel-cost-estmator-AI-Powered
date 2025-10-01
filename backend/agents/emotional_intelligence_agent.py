import asyncio
from typing import Dict, Any
import json

from .base_agent import BaseAgent
from models.travel_models import TravelRequest, EmotionalAnalysis, VibeType
from services.grok_service import GrokService

class EmotionalIntelligenceAgent(BaseAgent):
    """Agent responsible for emotional intelligence and vibe analysis"""
    
    def __init__(self, settings):
        super().__init__("Emotional Intelligence Agent", settings)
        self.grok_service = None
    
    async def initialize(self):
        """Initialize the emotional intelligence agent"""
        await super().initialize()
        self.grok_service = GrokService(self.settings)
        await self.grok_service.initialize()
    
    async def process(self, request: TravelRequest, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze emotional intelligence and vibe compatibility"""
        try:
            self.validate_request(request)
            
            # Analyze vibe and season compatibility
            vibe_analysis = await self._analyze_vibe_compatibility(request)
            
            # Get emotional recommendations
            emotional_recommendations = await self._get_emotional_recommendations(request)
            
            # Analyze mood indicators
            mood_indicators = await self._analyze_mood_indicators(request)
            
            # Create emotional analysis
            emotional_analysis = EmotionalAnalysis(
                vibe_score=vibe_analysis["vibe_score"],
                season_compatibility=vibe_analysis["season_compatibility"],
                mood_indicators=mood_indicators,
                recommended_activities=emotional_recommendations["activities"],
                emotional_wellness_tips=emotional_recommendations["wellness_tips"],
                vibe_enhancement_suggestions=emotional_recommendations["enhancement_suggestions"]
            )
            
            return {
                "emotional_analysis": emotional_analysis.dict(),
                "vibe_analysis": vibe_analysis,
                "recommendations": emotional_recommendations
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _analyze_vibe_compatibility(self, request: TravelRequest) -> Dict[str, Any]:
        current_season = self.get_season_from_date(request.start_date)
        
        vibe_seasons = {
            VibeType.ROMANTIC: ["spring", "autumn"],
            VibeType.ADVENTURE: ["summer", "autumn"],
            VibeType.BEACH: ["summer"],
            VibeType.NATURE: ["spring", "autumn"],
            VibeType.CULTURAL: ["autumn", "spring"],
            VibeType.CULINARY: ["autumn", "spring"],
            VibeType.WELLNESS: ["winter", "spring"]
        }
        
        optimal_seasons = vibe_seasons.get(request.vibe, ["spring", "summer", "autumn"])
        is_optimal_season = current_season in optimal_seasons
        
        vibe_score = 0.9 if is_optimal_season else 0.6
        season_compatibility = 1.0 if is_optimal_season else 0.5
        
        return {
            "vibe_score": vibe_score,
            "season_compatibility": season_compatibility,
            "current_season": current_season,
            "optimal_seasons": optimal_seasons,
            "is_optimal_season": is_optimal_season
        }
    
    async def _get_emotional_recommendations(self, request: TravelRequest) -> Dict[str, Any]:
        prompt = f"""
        As an emotional intelligence expert, analyze this travel request and provide recommendations:
        
        Destination: {request.destination}
        Vibe: {request.vibe.value}
        Season: {self.get_season_from_date(request.start_date)}
        Travelers: {request.travelers}
        Duration: {self.calculate_trip_duration(request.start_date, request.return_date)} days
        
        Please provide:
        1. 3-5 specific activities that match the {request.vibe.value} vibe
        2. 3-4 emotional wellness tips for this type of travel
        3. 2-3 suggestions to enhance the {request.vibe.value} experience
        
        Respond in JSON format:
        {{
            "activities": ["activity1", "activity2", ...],
            "wellness_tips": ["tip1", "tip2", ...],
            "enhancement_suggestions": ["suggestion1", "suggestion2", ...]
        }}
        """
        
        try:
            response = await self.grok_service.generate_response(prompt)
            return json.loads(response)
        except:
            # Fallback recommendations
            return self._get_fallback_recommendations(request.vibe)
    
    async def _analyze_mood_indicators(self, request: TravelRequest) -> list:
        mood_mapping = {
            VibeType.ROMANTIC: ["intimate", "peaceful", "romantic", "serene"],
            VibeType.ADVENTURE: ["energetic", "thrilling", "exciting", "bold"],
            VibeType.BEACH: ["relaxed", "calm", "refreshing", "tranquil"],
            VibeType.NATURE: ["grounded", "peaceful", "connected", "mindful"],
            VibeType.CULTURAL: ["curious", "inspired", "enlightened", "cultured"],
            VibeType.CULINARY: ["satisfied", "curious", "indulgent", "social"],
            VibeType.WELLNESS: ["balanced", "rejuvenated", "centered", "healed"]
        }
        
        return mood_mapping.get(request.vibe, ["happy", "content", "excited"])
    
    def _get_fallback_recommendations(self, vibe: VibeType) -> Dict[str, Any]:
        fallback_data = {
            VibeType.ROMANTIC: {
                "activities": ["Sunset dinner cruise", "Couples spa treatment", "Romantic walk in gardens", "Wine tasting"],
                "wellness_tips": ["Plan intimate moments", "Disconnect from technology", "Focus on each other", "Create memories"],
                "enhancement_suggestions": ["Book private experiences", "Choose romantic accommodations", "Plan surprise activities"]
            },
            VibeType.ADVENTURE: {
                "activities": ["Mountain hiking", "Rock climbing", "Water sports", "Extreme sports"],
                "wellness_tips": ["Stay hydrated", "Warm up properly", "Know your limits", "Pack safety gear"],
                "enhancement_suggestions": ["Book guided adventures", "Choose adventure-friendly hotels", "Plan recovery time"]
            },
            VibeType.BEACH: {
                "activities": ["Beach relaxation", "Snorkeling", "Beach volleyball", "Sunset watching"],
                "wellness_tips": ["Use sunscreen", "Stay hydrated", "Take breaks from sun", "Protect your skin"],
                "enhancement_suggestions": ["Book beachfront accommodation", "Plan water activities", "Choose beach restaurants"]
            },
            VibeType.NATURE: {
                "activities": ["Forest hiking", "Wildlife watching", "Nature photography", "Camping"],
                "wellness_tips": ["Respect wildlife", "Leave no trace", "Stay on trails", "Pack essentials"],
                "enhancement_suggestions": ["Book nature lodges", "Plan early morning activities", "Bring binoculars"]
            },
            VibeType.CULTURAL: {
                "activities": ["Museum visits", "Historical tours", "Local festivals", "Art galleries"],
                "wellness_tips": ["Learn local customs", "Respect cultural sites", "Dress appropriately", "Be open-minded"],
                "enhancement_suggestions": ["Book guided tours", "Choose cultural districts", "Learn basic local phrases"]
            },
            VibeType.CULINARY: {
                "activities": ["Food tours", "Cooking classes", "Local markets", "Fine dining"],
                "wellness_tips": ["Try new foods gradually", "Stay hydrated", "Balance meals", "Respect dietary restrictions"],
                "enhancement_suggestions": ["Book food experiences", "Choose foodie neighborhoods", "Research local specialties"]
            },
            VibeType.WELLNESS: {
                "activities": ["Spa treatments", "Yoga sessions", "Meditation", "Healthy dining"],
                "wellness_tips": ["Maintain routine", "Stay hydrated", "Get enough sleep", "Practice mindfulness"],
                "enhancement_suggestions": ["Book wellness retreats", "Choose spa hotels", "Plan quiet time"]
            }
        }
        
        return fallback_data.get(vibe, {
            "activities": ["Local sightseeing", "Cultural experiences", "Relaxation"],
            "wellness_tips": ["Stay hydrated", "Get enough rest", "Enjoy the moment"],
            "enhancement_suggestions": ["Book experiences in advance", "Choose comfortable accommodation"]
        })