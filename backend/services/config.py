from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional, List
import os
from enum import Enum

class Environment(str, Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class LogLevel(str, Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Environment
    environment: Environment = Field(default=Environment.DEVELOPMENT, description="Application environment")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")
    
    # API Keys
    grok_api_key: str = Field(default="", description="Grok API key for AI responses")
    serp_api_key: str = Field(default="", description="SERP API key for search data")
    google_maps_api_key: str = Field(default="", description="Google Maps API key for location services")
    
    # Database
    database_url: str = Field(
        default="sqlite:///./travel_estimator.db", 
        description="Database connection URL"
    )
    
    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379", 
        description="Redis connection URL for caching"
    )
    
    # API Configuration
    api_timeout: int = Field(default=30, ge=1, le=300, description="API request timeout in seconds")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum retry attempts for API calls")
    
    # Agent Configuration
    max_concurrent_agents: int = Field(default=5, ge=1, le=20, description="Maximum concurrent agents")
    agent_timeout: int = Field(default=60, ge=10, le=600, description="Agent execution timeout in seconds")
    
    # Grok Configuration
    grok_model: str = Field(default="meta-llama/llama-4-scout-17b-16e-instruct", description="Grok model to use")
    grok_temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Grok temperature for creativity")
    grok_max_tokens: int = Field(default=2000, ge=100, le=8000, description="Maximum tokens for Grok responses")
    grok_base_url: str = Field(default="https://api.groq.com/openai/v1/chat/completions", description="Grok API base URL")
    
    # SERP Configuration
    serp_engine: str = Field(default="google", description="SERP search engine")
    serp_country: str = Field(default="us", description="SERP country code")
    serp_language: str = Field(default="en", description="SERP language code")
    serp_base_url: str = Field(default="https://serpapi.com/search", description="SERP API base URL")
    
    # Google Maps Configuration
    maps_region: str = Field(default="us", description="Google Maps region")
    maps_language: str = Field(default="en", description="Google Maps language")
    
    # Travel Configuration
    default_currency: str = Field(default="USD", description="Default currency for pricing")
    max_travelers: int = Field(default=10, ge=1, le=50, description="Maximum number of travelers")
    max_trip_duration: int = Field(default=30, ge=1, le=365, description="Maximum trip duration in days")
    min_trip_duration: int = Field(default=1, ge=1, le=30, description="Minimum trip duration in days")
    
    # Caching
    cache_ttl: int = Field(default=3600, ge=60, le=86400, description="Cache TTL in seconds")
    enable_caching: bool = Field(default=True, description="Enable response caching")
    
    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production", description="Secret key for security")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"], 
        description="Allowed CORS origins"
    )
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, ge=1, le=10000, description="Rate limit requests per minute")
    rate_limit_window: int = Field(default=60, ge=1, le=3600, description="Rate limit window in seconds")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    metrics_port: int = Field(default=9090, ge=1000, le=65535, description="Metrics server port")
    
    # Email Configuration (for notifications)
    smtp_host: Optional[str] = Field(default=None, description="SMTP host for email notifications")
    smtp_port: int = Field(default=587, ge=1, le=65535, description="SMTP port")
    smtp_username: Optional[str] = Field(default=None, description="SMTP username")
    smtp_password: Optional[str] = Field(default=None, description="SMTP password")
    smtp_use_tls: bool = Field(default=True, description="Use TLS for SMTP")
    
    # File Upload
    max_file_size: int = Field(default=10485760, ge=1024, le=104857600, description="Maximum file size in bytes (10MB)")
    allowed_file_types: List[str] = Field(
        default=["image/jpeg", "image/png", "image/gif"], 
        description="Allowed file types for uploads"
    )
    
    # Performance
    enable_compression: bool = Field(default=True, description="Enable response compression")
    compression_level: int = Field(default=6, ge=1, le=9, description="Compression level")
    
    @validator('grok_api_key')
    def validate_grok_key(cls, v):
        """Validate Grok API key format"""
        if v and not v.startswith('gsk_'):
            raise ValueError('Grok API key should start with "xai-"')
        return v
    
    @validator('serp_api_key')
    def validate_serp_key(cls, v):
        """Validate SERP API key format"""
        if v and len(v) < 32:
            raise ValueError('SERP API key should be at least 32 characters')
        return v
    
    @validator('google_maps_api_key')
    def validate_maps_key(cls, v):
        """Validate Google Maps API key format"""
        if v and len(v) < 32:
            raise ValueError('Google Maps API key should be at least 32 characters')
        return v
    
    @validator('cors_origins')
    def validate_cors_origins(cls, v):
        """Validate CORS origins"""
        if not v:
            raise ValueError('At least one CORS origin must be specified')
        return v
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        """Validate secret key"""
        if v == "your-secret-key-change-in-production":
            import warnings
            warnings.warn("Using default secret key! Change this in production.")
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment == Environment.PRODUCTION
    
    @property
    def has_grok_api(self) -> bool:
        """Check if Grok API key is configured"""
        return bool(self.grok_api_key)
    
    @property
    def has_serp_api(self) -> bool:
        """Check if SERP API key is configured"""
        return bool(self.serp_api_key)
    
    @property
    def has_maps_api(self) -> bool:
        """Check if Google Maps API key is configured"""
        return bool(self.google_maps_api_key)
    
    def get_database_url(self) -> str:
        """Get database URL with proper formatting"""
        if self.database_url.startswith('sqlite'):
            return self.database_url
        return self.database_url
    
    def get_redis_url(self) -> str:
        """Get Redis URL with proper formatting"""
        return self.redis_url
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        validate_assignment = True
        extra = "ignore"
        
        # Environment variable mapping
        fields = {
            'grok_api_key': {'env': 'GROK_API_KEY'},
            'serp_api_key': {'env': 'SERP_API_KEY'},
            'google_maps_api_key': {'env': 'GOOGLE_MAPS_API_KEY'},
            'database_url': {'env': 'DATABASE_URL'},
            'redis_url': {'env': 'REDIS_URL'},
            'secret_key': {'env': 'SECRET_KEY'},
            'environment': {'env': 'ENVIRONMENT'},
            'debug': {'env': 'DEBUG'},
            'log_level': {'env': 'LOG_LEVEL'},
        }
