import json
from typing import Optional
from src.config.logging import get_logger

logger = get_logger(__name__)

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    logger.warning("Redis is down. Caching will be disabled, sorry.")
    aioredis = None
    REDIS_AVAILABLE = False

from src.config.settings import get_settings
from src.models.api_models import QueryResponse


class CacheService:
    def __init__(self):
        self.settings = get_settings()
        if REDIS_AVAILABLE:
            self.redis = aioredis.from_url(self.settings.redis_url, decode_responses=True)
        else:
            self.redis = None
    
    async def get_cached_query(self, question: str) -> Optional[QueryResponse]:
        """
        function to get the cached query result
        
        """
        if not REDIS_AVAILABLE or not self.redis:
            return None
            
        try:
            cache_key = f"query:{question}"
            cached = await self.redis.get(cache_key)
            if cached:
                return QueryResponse(**json.loads(cached))
        except Exception as e:
            logger.warning(f"cache read error: {e}")
        return None
    
    async def cache_query_result(self, question: str, response: QueryResponse) -> None:
        """
        function to cache the query result
        
        """
        if not REDIS_AVAILABLE or not self.redis:
            return
            
        try:
            cache_key = f"query:{question}"
            await self.redis.set(
                cache_key,
                response.model_dump_json(),
                ex=self.settings.redis_cache_ttl
            )
        except Exception as e:
            logger.warning(f"cache write error: {e}")
    
    async def ping(self) -> bool:
        """
        Check if Redis is available:
        
        """
        if not REDIS_AVAILABLE or not self.redis:
            return False
            
        try:
            return await self.redis.ping()
        except Exception:
            return False
