"""
Rate Limiting System for SearXNG MCP Server

Protects against API quota exhaustion with per-provider rate limiting.
"""

import time
from collections import deque
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter for API requests.
    
    Features:
    - Per-provider rate limiting
    - Configurable limits
    - Burst handling
    - Request queuing
    - Status monitoring
    """
    
    # Default rate limits (requests per minute)
    DEFAULT_LIMITS = {
        "openrouter": 60,  # 60 requests per minute
        "ollama": 100,  # 100 requests per minute
        "gemini": 60,  # 60 requests per minute
    }
    
    def __init__(self, custom_limits: Optional[Dict[str, int]] = None):
        """
        Initialize rate limiter.
        
        Args:
            custom_limits: Custom rate limits per provider (requests/min)
        """
        self.limits = {**self.DEFAULT_LIMITS, **(custom_limits or {})}
        
        # Request timestamps per provider (using deque for efficiency)
        self.request_history: Dict[str, deque] = {
            provider: deque() for provider in self.limits
        }
        
        # Statistics
        self.stats = {
            provider: {
                "total_requests": 0,
                "rate_limited": 0,
                "current_rate": 0.0,
            }
            for provider in self.limits
        }
    
    def check_rate_limit(self, provider: str) -> tuple[bool, Optional[float]]:
        """
        Check if request is allowed under rate limit.
        
        Args:
            provider: Provider name
            
        Returns:
            Tuple of (allowed: bool, wait_time: Optional[float])
            If not allowed, wait_time indicates seconds to wait
        """
        if provider not in self.limits:
            # Unknown provider, allow by default
            return True, None
        
        current_time = time.time()
        limit = self.limits[provider]
        history = self.request_history[provider]
        
        # Remove timestamps older than 1 minute
        cutoff_time = current_time - 60.0
        while history and history[0] < cutoff_time:
            history.popleft()
        
        # Check if we're under the limit
        if len(history) < limit:
            return True, None
        
        # Rate limit exceeded - calculate wait time
        oldest_request = history[0]
        wait_time = 60.0 - (current_time - oldest_request) + 0.1  # Add 0.1s buffer
        
        logger.warning(
            f"Rate limit exceeded for {provider}: "
            f"{len(history)}/{limit} requests in last minute. "
            f"Wait {wait_time:.1f}s"
        )
        
        self.stats[provider]["rate_limited"] += 1
        return False, wait_time
    
    def record_request(self, provider: str):
        """
        Record a request for rate limiting.
        
        Args:
            provider: Provider name
        """
        if provider not in self.limits:
            return
        
        current_time = time.time()
        self.request_history[provider].append(current_time)
        self.stats[provider]["total_requests"] += 1
        
        # Update current rate
        history = self.request_history[provider]
        cutoff_time = current_time - 60.0
        while history and history[0] < cutoff_time:
            history.popleft()
        self.stats[provider]["current_rate"] = len(history)
    
    async def wait_if_needed(self, provider: str) -> bool:
        """
        Wait if rate limit is exceeded (async version).
        
        Args:
            provider: Provider name
            
        Returns:
            True if request proceeded, False if aborted
        """
        allowed, wait_time = self.check_rate_limit(provider)
        
        if allowed:
            self.record_request(provider)
            return True
        
        if wait_time and wait_time > 0:
            logger.info(f"Rate limit wait: {wait_time:.1f}s for {provider}")
            import asyncio
            await asyncio.sleep(wait_time)
            
            # Try again after waiting
            allowed, _ = self.check_rate_limit(provider)
            if allowed:
                self.record_request(provider)
                return True
        
        return False
    
    def get_status(self, provider: Optional[str] = None) -> Dict:
        """
        Get rate limiter status.
        
        Args:
            provider: Specific provider or None for all
            
        Returns:
            Dictionary with rate limiter status
        """
        if provider:
            if provider not in self.limits:
                return {"error": f"Unknown provider: {provider}"}
            
            history = self.request_history[provider]
            limit = self.limits[provider]
            current_requests = len(history)
            available = limit - current_requests
            
            return {
                "provider": provider,
                "limit_per_minute": limit,
                "current_requests": current_requests,
                "available": available,
                "utilization_percent": round(current_requests / limit * 100, 1),
                "stats": self.stats[provider],
            }
        else:
            # All providers
            return {
                provider: self.get_status(provider)
                for provider in self.limits
            }
    
    def reset_stats(self, provider: Optional[str] = None):
        """
        Reset statistics.
        
        Args:
            provider: Specific provider or None for all
        """
        if provider:
            if provider in self.stats:
                self.stats[provider] = {
                    "total_requests": 0,
                    "rate_limited": 0,
                    "current_rate": 0.0,
                }
        else:
            for prov in self.stats:
                self.stats[prov] = {
                    "total_requests": 0,
                    "rate_limited": 0,
                    "current_rate": 0.0,
                }
        
        logger.info(f"Rate limiter stats reset for {provider or 'all providers'}")
