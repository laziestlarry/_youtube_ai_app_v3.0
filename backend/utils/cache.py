import asyncio
import json
import time
from typing import Any, Optional, Dict
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "evictions": 0
        }
        self.cleanup_task = None
    
    async def initialize(self):
        """Initialize cache manager."""
        try:
            # Start cleanup task
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("Cache manager initialized")
            
        except Exception as e:
            logger.error(f"Cache initialization failed: {e}")
            raise
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            if key not in self.cache:
                self.stats["misses"] += 1
                return None
            
            entry = self.cache[key]
            
            # Check if expired
            if entry["expires_at"] < time.time():
                del self.cache[key]
                self.stats["misses"] += 1
                return None
            
            # Update access time
            entry["accessed_at"] = time.time()
            self.stats["hits"] += 1
            
            return entry["value"]
            
        except Exception as e:
            logger.error(f"Cache get failed for key {key}: {e}")
            self.stats["misses"] += 1
            return None
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set value in cache."""
        try:
            # Use default TTL if not specified
            ttl = expire or self.default_ttl
            
            # Check if cache is full and evict if necessary
            if len(self.cache) >= self.max_size and key not in self.cache:
                await self._evict_lru()
            
            # Store value
            self.cache[key] = {
                "value": value,
                "created_at": time.time(),
                "accessed_at": time.time(),
                "expires_at": time.time() + ttl
            }
            
            self.stats["sets"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache set failed for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            if key in self.cache:
                del self.cache[key]
                self.stats["deletes"] += 1
                return True
            return False
            
        except Exception as e:
            logger.error(f"Cache delete failed for key {key}: {e}")
            return False
    
    async def clear(self):
        """Clear all cache entries."""
        try:
            self.cache.clear()
            logger.info("Cache cleared")
            
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
    
    async def _evict_lru(self):
        """Evict least recently used entry."""
        try:
            if not self.cache:
                return
            
            # Find LRU entry
            lru_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k]["accessed_at"]
            )
            
            del self.cache[lru_key]
            self.stats["evictions"] += 1
            
        except Exception as e:
            logger.error(f"LRU eviction failed: {e}")
    
    async def _cleanup_loop(self):
        """Periodic cleanup of expired entries."""
        while True:
            try:
                current_time = time.time()
                expired_keys = [
                    key for key, entry in self.cache.items()
                    if entry["expires_at"] < current_time
                ]
                
                for key in expired_keys:
                    del self.cache[key]
                
                if expired_keys:
                    logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
                
                # Sleep for 5 minutes before next cleanup
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Cache cleanup failed: {e}")
                await asyncio.sleep(300)  # Continue cleanup despite errors
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = (self.stats["hits"] / total_requests) if total_requests > 0 else 0
            
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hit_rate": round(hit_rate, 3),
                "stats": self.stats.copy(),
                "memory_usage": self._estimate_memory_usage()
            }
            
        except Exception as e:
            logger.error(f"Cache stats failed: {e}")
            return {"error": str(e)}
    
    def _estimate_memory_usage(self) -> Dict[str, Any]:
        """Estimate cache memory usage."""
        try:
            total_size = 0
            for key, entry in self.cache.items():
                # Rough estimation
                key_size = len(str(key))
                value_size = len(str(entry["value"]))
                metadata_size = 100  # Rough estimate for timestamps
                total_size += key_size + value_size + metadata_size
            
            return {
                "estimated_bytes": total_size,
                "estimated_mb": round(total_size / (1024 * 1024), 2),
                "entries": len(self.cache)
            }
            
        except Exception as e:
            logger.error(f"Memory usage estimation failed: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> bool:
        """Check if cache is healthy."""
        try:
            # Test basic operations
            test_key = "__health_check__"
            test_value = "test"
            
            await self.set(test_key, test_value, expire=60)
            retrieved = await self.get(test_key)
            await self.delete(test_key)
            
            return retrieved == test_value
            
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup cache manager."""
        try:
            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            await self.clear()
            logger.info("Cache manager cleaned up")
            
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")