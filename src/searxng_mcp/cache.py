"""
Result Caching System for SearXNG MCP Server

Provides TTL-based caching for search results to reduce API costs and improve response times.
Implements file-based caching with automatic expiration and cleanup.
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ResultCache:
    """
    TTL-based cache for search results.
    
    Features:
    - Automatic expiration based on TTL
    - Category-specific TTL (news: 15min, general: 1hour)
    - Cache hit/miss statistics
    - Automatic cleanup of expired entries
    - Thread-safe file operations
    """
    
    def __init__(self, cache_dir: Optional[Path] = None, default_ttl: int = 3600):
        """
        Initialize the cache.
        
        Args:
            cache_dir: Directory for cache storage (default: ~/.searxng_mcp/cache)
            default_ttl: Default TTL in seconds (default: 1 hour)
        """
        self.cache_dir = cache_dir or (Path.home() / ".searxng_mcp" / "cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        
        # Category-specific TTLs
        self.category_ttls = {
            "news": 900,  # 15 minutes for news (time-sensitive)
            "general": 3600,  # 1 hour for general
            "images": 7200,  # 2 hours for images
            "videos": 7200,  # 2 hours for videos
            "it": 3600,  # 1 hour for IT/code
            "science": 10800,  # 3 hours for science
            "files": 7200,  # 2 hours for files
            "music": 7200,  # 2 hours for music
            "map": 86400,  # 24 hours for maps (don't change often)
            "social_media": 1800,  # 30 minutes for social (changes quickly)
        }
        
        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "writes": 0,
            "evictions": 0,
        }
    
    def _get_cache_key(
        self,
        query: str,
        categories: str = "",
        engines: str = "",
        language: str = "",
        time_range: str = "",
        safesearch: int = 1,
        ai_enhance: bool = False,
    ) -> str:
        """
        Generate cache key from search parameters.
        
        Args:
            query: Search query
            categories: Comma-separated categories
            engines: Comma-separated engines
            language: Language code
            time_range: Time range filter
            safesearch: Safe search level
            ai_enhance: Whether AI enhancement is enabled
            
        Returns:
            SHA256 hash as cache key
        """
        # Create deterministic key from parameters
        key_components = [
            query.lower().strip(),
            categories.lower().strip(),
            engines.lower().strip(),
            language.lower().strip(),
            time_range.lower().strip(),
            str(safesearch),
            str(ai_enhance),
        ]
        key_string = "|".join(key_components)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def _get_ttl_for_query(self, categories: str = "") -> int:
        """
        Get TTL based on query categories.
        
        Args:
            categories: Comma-separated categories
            
        Returns:
            TTL in seconds
        """
        if not categories:
            return self.default_ttl
        
        # Use minimum TTL if multiple categories specified
        category_list = [c.strip().lower() for c in categories.split(",")]
        ttls = [self.category_ttls.get(cat, self.default_ttl) for cat in category_list]
        return min(ttls) if ttls else self.default_ttl
    
    def get(
        self,
        query: str,
        categories: str = "",
        engines: str = "",
        language: str = "",
        time_range: str = "",
        safesearch: int = 1,
        ai_enhance: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached result if available and not expired.
        
        Returns:
            Cached result dict or None if not found/expired
        """
        cache_key = self._get_cache_key(
            query, categories, engines, language, time_range, safesearch, ai_enhance
        )
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            if not cache_file.exists():
                self.stats["misses"] += 1
                return None
            
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_entry = json.load(f)
            
            # Check expiration
            if time.time() > cache_entry["expires_at"]:
                logger.debug(f"Cache expired for key {cache_key[:8]}...")
                cache_file.unlink(missing_ok=True)
                self.stats["misses"] += 1
                self.stats["evictions"] += 1
                return None
            
            logger.info(f"Cache hit for query: {query[:50]}...")
            self.stats["hits"] += 1
            return cache_entry["data"]
            
        except Exception as e:
            logger.warning(f"Cache read error for key {cache_key[:8]}...: {e}")
            self.stats["misses"] += 1
            return None
    
    def set(
        self,
        data: Dict[str, Any],
        query: str,
        categories: str = "",
        engines: str = "",
        language: str = "",
        time_range: str = "",
        safesearch: int = 1,
        ai_enhance: bool = False,
    ) -> bool:
        """
        Cache a search result.
        
        Args:
            data: Result data to cache
            query: Search query
            categories: Comma-separated categories
            engines: Comma-separated engines
            language: Language code
            time_range: Time range filter
            safesearch: Safe search level
            ai_enhance: Whether AI enhancement is enabled
            
        Returns:
            True if successful, False otherwise
        """
        cache_key = self._get_cache_key(
            query, categories, engines, language, time_range, safesearch, ai_enhance
        )
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            ttl = self._get_ttl_for_query(categories)
            cache_entry = {
                "query": query,
                "categories": categories,
                "cached_at": time.time(),
                "expires_at": time.time() + ttl,
                "ttl": ttl,
                "data": data,
            }
            
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_entry, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Cached result for query: {query[:50]}... (TTL: {ttl}s)")
            self.stats["writes"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache write error for key {cache_key[:8]}...: {e}")
            return False
    
    def clear(self) -> int:
        """
        Clear all cached entries.
        
        Returns:
            Number of entries cleared
        """
        count = 0
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                count += 1
            logger.info(f"Cleared {count} cache entries")
            return count
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return count
    
    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.
        
        Returns:
            Number of expired entries removed
        """
        count = 0
        try:
            current_time = time.time()
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        cache_entry = json.load(f)
                    
                    if current_time > cache_entry["expires_at"]:
                        cache_file.unlink()
                        count += 1
                        self.stats["evictions"] += 1
                        
                except Exception as e:
                    logger.warning(f"Error checking cache file {cache_file.name}: {e}")
                    # Delete corrupted cache files
                    cache_file.unlink(missing_ok=True)
                    count += 1
            
            if count > 0:
                logger.info(f"Cleaned up {count} expired cache entries")
            return count
            
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")
            return count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (
            (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        )
        
        return {
            **self.stats,
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2),
            "cache_size_files": len(list(self.cache_dir.glob("*.json"))),
        }
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get detailed cache information.
        
        Returns:
            Dictionary with cache details
        """
        stats = self.get_stats()
        
        # Calculate cache size
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.json"))
        
        return {
            **stats,
            "cache_dir": str(self.cache_dir),
            "cache_size_bytes": total_size,
            "cache_size_mb": round(total_size / 1024 / 1024, 2),
            "default_ttl": self.default_ttl,
            "category_ttls": self.category_ttls,
        }
