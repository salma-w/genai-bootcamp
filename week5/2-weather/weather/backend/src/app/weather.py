"""
Weather module with caching and multi-language support
"""
import requests
import logging
from datetime import datetime, timedelta
from typing import Optional
logger = logging.getLogger(__name__)

# ============================================
# WEATHER CACHE
# ============================================
class WeatherCache:
    """Simple cache for weather data with TTL (time-to-live)"""
    def __init__(self, ttl_minutes: int = 30):
        self.cache = {}
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def get(self, key: str) -> Optional[dict]:
        """Get cached data if not expired"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                logger.info(f"Cache HIT for {key}")
                return data
            else:
                logger.info(f"Cache EXPIRED for {key}")
                del self.cache[key]
        logger.info(f"Cache MISS for {key}")
        return None
    
    def set(self, key: str, data: dict):
        """Store data in cache with timestamp"""
        self.cache[key] = (data, datetime.now())
        logger.info(f"Cache SET for {key}")
    
    def clear(self):
        """Clear all cached data"""
        self.cache.clear()
        logger.info("Cache CLEARED")