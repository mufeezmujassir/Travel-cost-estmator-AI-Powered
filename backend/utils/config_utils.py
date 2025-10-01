"""
Configuration utilities for the Travel Cost Estimator application
"""
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

from services.config import Settings, Environment, LogLevel

class ConfigManager:
    """Configuration manager for handling settings across different environments"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or ".env"
        self.settings = None
    
    def load_settings(self) -> Settings:
        """Load settings from environment variables and config files"""
        try:
            self.settings = Settings()
            return self.settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            # Return default settings if loading fails
            return Settings()
    
    def get_settings(self) -> Settings:
        """Get current settings instance"""
        if self.settings is None:
            self.settings = self.load_settings()
        return self.settings
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate the current configuration"""
        settings = self.get_settings()
        validation_results = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Check API keys
        if not settings.has_grok_api:
            validation_results["warnings"].append("Grok API key not configured - using mock responses")
            validation_results["recommendations"].append("Add GROK_API_KEY to environment for AI-powered recommendations")
        
        if not settings.has_serp_api:
            validation_results["warnings"].append("SERP API key not configured - using mock data")
            validation_results["recommendations"].append("Add SERP_API_KEY to environment for real-time travel data")
        
        if not settings.has_maps_api:
            validation_results["warnings"].append("Google Maps API key not configured - using mock routing")
            validation_results["recommendations"].append("Add GOOGLE_MAPS_API_KEY to environment for accurate transportation planning")
        
        # Check security settings
        if settings.secret_key == "your-secret-key-change-in-production":
            validation_results["errors"].append("Default secret key detected - change SECRET_KEY in production")
            validation_results["valid"] = False
        
        # Check environment-specific settings
        if settings.is_production:
            if settings.debug:
                validation_results["errors"].append("Debug mode should be disabled in production")
                validation_results["valid"] = False
            
            if not settings.has_grok_api or not settings.has_serp_api:
                validation_results["errors"].append("API keys are required in production")
                validation_results["valid"] = False
        
        # Check database configuration
        if settings.database_url.startswith("sqlite") and settings.is_production:
            validation_results["warnings"].append("SQLite database not recommended for production")
            validation_results["recommendations"].append("Use PostgreSQL or MySQL for production")
        
        return validation_results
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration"""
        settings = self.get_settings()
        
        return {
            "environment": settings.environment.value,
            "debug_mode": settings.debug,
            "log_level": settings.log_level.value,
            "api_keys_configured": {
                "grok": settings.has_grok_api,
                "serp": settings.has_serp_api,
                "maps": settings.has_maps_api
            },
            "database": {
                "type": "sqlite" if settings.database_url.startswith("sqlite") else "other",
                "url": settings.database_url
            },
            "caching": {
                "enabled": settings.enable_caching,
                "ttl": settings.cache_ttl
            },
            "rate_limiting": {
                "requests_per_minute": settings.rate_limit_requests,
                "window_seconds": settings.rate_limit_window
            },
            "monitoring": {
                "enabled": settings.enable_metrics,
                "port": settings.metrics_port
            }
        }
    
    def export_config(self, file_path: str) -> bool:
        """Export current configuration to a JSON file"""
        try:
            settings = self.get_settings()
            config_data = {
                "environment": settings.environment.value,
                "debug": settings.debug,
                "log_level": settings.log_level.value,
                "api_timeout": settings.api_timeout,
                "max_retries": settings.max_retries,
                "max_concurrent_agents": settings.max_concurrent_agents,
                "agent_timeout": settings.agent_timeout,
                "grok_model": settings.grok_model,
                "grok_temperature": settings.grok_temperature,
                "grok_max_tokens": settings.grok_max_tokens,
                "serp_engine": settings.serp_engine,
                "serp_country": settings.serp_country,
                "serp_language": settings.serp_language,
                "maps_region": settings.maps_region,
                "maps_language": settings.maps_language,
                "default_currency": settings.default_currency,
                "max_travelers": settings.max_travelers,
                "max_trip_duration": settings.max_trip_duration,
                "min_trip_duration": settings.min_trip_duration,
                "cache_ttl": settings.cache_ttl,
                "enable_caching": settings.enable_caching,
                "rate_limit_requests": settings.rate_limit_requests,
                "rate_limit_window": settings.rate_limit_window,
                "enable_metrics": settings.enable_metrics,
                "metrics_port": settings.metrics_port,
                "enable_compression": settings.enable_compression,
                "compression_level": settings.compression_level
            }
            
            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error exporting config: {e}")
            return False
    
    def create_env_file(self, file_path: str = ".env") -> bool:
        """Create a .env file with current settings"""
        try:
            settings = self.get_settings()
            
            env_content = f"""# Environment Configuration
ENVIRONMENT={settings.environment.value}
DEBUG={str(settings.debug).lower()}
LOG_LEVEL={settings.log_level.value}

# API Keys (Add your actual keys here)
GROK_API_KEY=
SERP_API_KEY=
GOOGLE_MAPS_API_KEY=

# Database
DATABASE_URL={settings.database_url}

# Redis
REDIS_URL={settings.redis_url}

# Security
SECRET_KEY={settings.secret_key}

# API Configuration
API_TIMEOUT={settings.api_timeout}
MAX_RETRIES={settings.max_retries}

# Agent Configuration
MAX_CONCURRENT_AGENTS={settings.max_concurrent_agents}
AGENT_TIMEOUT={settings.agent_timeout}

# Grok Configuration
GROK_MODEL={settings.grok_model}
GROK_TEMPERATURE={settings.grok_temperature}
GROK_MAX_TOKENS={settings.grok_max_tokens}
GROK_BASE_URL={settings.grok_base_url}

# SERP Configuration
SERP_ENGINE={settings.serp_engine}
SERP_COUNTRY={settings.serp_country}
SERP_LANGUAGE={settings.serp_language}
SERP_BASE_URL={settings.serp_base_url}

# Google Maps Configuration
MAPS_REGION={settings.maps_region}
MAPS_LANGUAGE={settings.maps_language}

# Travel Configuration
DEFAULT_CURRENCY={settings.default_currency}
MAX_TRAVELERS={settings.max_travelers}
MAX_TRIP_DURATION={settings.max_trip_duration}
MIN_TRIP_DURATION={settings.min_trip_duration}

# Caching
CACHE_TTL={settings.cache_ttl}
ENABLE_CACHING={str(settings.enable_caching).lower()}

# CORS Configuration
CORS_ORIGINS={json.dumps(settings.cors_origins)}

# Rate Limiting
RATE_LIMIT_REQUESTS={settings.rate_limit_requests}
RATE_LIMIT_WINDOW={settings.rate_limit_window}

# Monitoring
ENABLE_METRICS={str(settings.enable_metrics).lower()}
METRICS_PORT={settings.metrics_port}

# Performance
ENABLE_COMPRESSION={str(settings.enable_compression).lower()}
COMPRESSION_LEVEL={settings.compression_level}
"""
            
            with open(file_path, 'w') as f:
                f.write(env_content)
            
            return True
        except Exception as e:
            print(f"Error creating .env file: {e}")
            return False

def get_config() -> Settings:
    """Get the global configuration instance"""
    global _config_manager
    if '_config_manager' not in globals():
        _config_manager = ConfigManager()
    return _config_manager.get_settings()

def validate_config() -> Dict[str, Any]:
    """Validate the global configuration"""
    global _config_manager
    if '_config_manager' not in globals():
        _config_manager = ConfigManager()
    return _config_manager.validate_configuration()

def get_config_summary() -> Dict[str, Any]:
    """Get configuration summary"""
    global _config_manager
    if '_config_manager' not in globals():
        _config_manager = ConfigManager()
    return _config_manager.get_config_summary()

# Global config manager instance
_config_manager: Optional[ConfigManager] = None
