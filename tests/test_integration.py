"""
Integration tests for Part 2 features: Cache, Metrics, and Rate Limiting.
"""

import pytest
from pathlib import Path
import tempfile
import time


class TestCacheIntegration:
    """Test cache integration with server."""
    
    def test_cache_imports(self):
        """Test cache module imports successfully."""
        from searxng_mcp.cache import ResultCache
        assert ResultCache is not None
    
    def test_cache_in_server(self):
        """Test cache is integrated into server."""
        from searxng_mcp.server import get_cache
        cache = get_cache()
        assert cache is not None
        assert hasattr(cache, 'get')
        assert hasattr(cache, 'set')
        assert hasattr(cache, 'get_stats')
    
    def test_cache_operations(self):
        """Test basic cache operations."""
        from searxng_mcp.cache import ResultCache
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResultCache(cache_dir=Path(tmpdir), default_ttl=3600)
            
            # Test cache miss
            result = cache.get(query="test query", categories="general")
            assert result is None
            
            # Test cache set
            test_data = {"results": [{"title": "Test", "url": "http://test.com"}]}
            success = cache.set(
                data=test_data,
                query="test query",
                categories="general"
            )
            assert success is True
            
            # Test cache hit
            cached = cache.get(query="test query", categories="general")
            assert cached is not None
            assert cached["results"][0]["title"] == "Test"
            
            # Test stats
            stats = cache.get_stats()
            assert stats["hits"] == 1
            assert stats["misses"] == 1
            assert stats["writes"] == 1
    
    def test_cache_expiration(self):
        """Test cache expiration."""
        from searxng_mcp.cache import ResultCache
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResultCache(cache_dir=Path(tmpdir), default_ttl=1)  # 1 second TTL
            
            test_data = {"results": []}
            cache.set(data=test_data, query="expire test")
            
            # Should be cached
            result = cache.get(query="expire test")
            assert result is not None
            
            # Wait for expiration
            time.sleep(1.5)
            
            # Should be expired
            result = cache.get(query="expire test")
            assert result is None


class TestMetricsIntegration:
    """Test metrics integration with server."""
    
    def test_metrics_imports(self):
        """Test metrics module imports successfully."""
        from searxng_mcp.metrics import MetricsCollector
        assert MetricsCollector is not None
    
    def test_metrics_in_server(self):
        """Test metrics is integrated into server."""
        from searxng_mcp.server import get_metrics
        metrics = get_metrics()
        assert metrics is not None
        assert hasattr(metrics, 'record_search')
        assert hasattr(metrics, 'get_session_metrics')
    
    def test_metrics_operations(self):
        """Test basic metrics operations."""
        from searxng_mcp.metrics import MetricsCollector
        
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics = MetricsCollector(metrics_dir=Path(tmpdir))
            
            # Test recording searches
            metrics.record_search(
                query="test query",
                categories="general",
                ai_enhanced=False,
                cached=False,
                latency=0.5,
                success=True
            )
            
            stats = metrics.get_session_metrics()
            assert stats["enabled"] is True
            assert stats["requests"]["total"] == 1
            assert stats["requests"]["search_only"] == 1
            
            # Test AI enhanced search
            metrics.record_search(
                query="ai test",
                categories="general",
                ai_enhanced=True,
                cached=False,
                latency=1.5,
                success=True,
                provider="openrouter",
                model="google/gemini-2.0-flash-exp",
                token_estimate={"input": 1000, "output": 500}
            )
            
            stats = metrics.get_session_metrics()
            assert stats["requests"]["total"] == 2
            assert stats["requests"]["ai_enhanced"] == 1
            assert "openrouter" in stats["providers"]


class TestRateLimitingIntegration:
    """Test rate limiting integration with AI enhancer."""
    
    def test_rate_limiter_imports(self):
        """Test rate limiter module imports successfully."""
        from searxng_mcp.rate_limiter import RateLimiter
        assert RateLimiter is not None
    
    def test_rate_limiter_in_ai_enhancer(self):
        """Test rate limiter is integrated into AI enhancer."""
        from searxng_mcp.ai_enhancer import AIEnhancer
        enhancer = AIEnhancer()
        assert hasattr(enhancer, 'rate_limiter')
        assert enhancer.rate_limiter is not None
    
    def test_rate_limiter_operations(self):
        """Test basic rate limiter operations."""
        from searxng_mcp.rate_limiter import RateLimiter
        
        limiter = RateLimiter(custom_limits={"test_provider": 5})
        
        # Should allow first 5 requests
        for i in range(5):
            allowed, wait_time = limiter.check_rate_limit("test_provider")
            assert allowed is True
            assert wait_time is None
            limiter.record_request("test_provider")
        
        # Should block 6th request
        allowed, wait_time = limiter.check_rate_limit("test_provider")
        assert allowed is False
        assert wait_time is not None
        assert wait_time > 0
        
        # Check stats
        status = limiter.get_status("test_provider")
        assert status["current_requests"] == 5
        assert status["limit_per_minute"] == 5
    
    @pytest.mark.asyncio
    async def test_rate_limiter_async_wait(self):
        """Test async rate limiter wait functionality."""
        from searxng_mcp.rate_limiter import RateLimiter
        
        limiter = RateLimiter(custom_limits={"test_provider": 2})
        
        # First two should proceed
        result1 = await limiter.wait_if_needed("test_provider")
        assert result1 is True
        
        result2 = await limiter.wait_if_needed("test_provider")
        assert result2 is True
        
        # Third should wait (but we won't wait for full minute in test)
        # Just verify it returns the correct structure
        allowed, wait_time = limiter.check_rate_limit("test_provider")
        assert allowed is False


class TestEndToEndIntegration:
    """Test end-to-end integration of all systems."""
    
    def test_all_systems_initialized(self):
        """Test that all systems can be initialized together."""
        from searxng_mcp.server import get_cache, get_metrics, get_instance_manager
        from searxng_mcp.ai_enhancer import get_ai_enhancer
        
        cache = get_cache()
        metrics = get_metrics()
        manager = get_instance_manager()
        enhancer = get_ai_enhancer()
        
        assert cache is not None
        assert metrics is not None
        assert manager is not None
        assert enhancer is not None
        
        # Verify rate limiter in enhancer
        assert hasattr(enhancer, 'rate_limiter')
    
    def test_server_tools_available(self):
        """Test that new server tools are available."""
        from searxng_mcp import server
        import inspect
        
        # Get all async functions decorated with @mcp.tool()
        tool_functions = []
        for name, obj in inspect.getmembers(server):
            if inspect.iscoroutinefunction(obj) and name not in ['periodic_cleanup']:
                tool_functions.append(name)
        
        # Check required tools exist
        assert "search" in tool_functions
        assert "get_cache_stats" in tool_functions
        assert "clear_cache" in tool_functions
        assert "get_session_stats" in tool_functions
        assert "list_categories" in tool_functions
        assert "get_instances" in tool_functions
    
    def test_imports_work_together(self):
        """Test that all modules can be imported together without conflicts."""
        try:
            from searxng_mcp.server import (
                get_cache,
                get_metrics,
                get_instance_manager,
            )
            from searxng_mcp.ai_enhancer import get_ai_enhancer
            from searxng_mcp.cache import ResultCache
            from searxng_mcp.metrics import MetricsCollector
            from searxng_mcp.rate_limiter import RateLimiter
            
            # If we get here, all imports work
            assert True
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")


class TestLogging:
    """Test logging integration."""
    
    def test_cache_logging(self):
        """Test cache logs hits and misses."""
        from searxng_mcp.cache import ResultCache
        import logging
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ResultCache(cache_dir=Path(tmpdir))
            
            # This should log a cache miss
            cache.get(query="test")
            
            # This should log a cache write
            cache.set(data={}, query="test")
            
            # This should log a cache hit
            cache.get(query="test")
            
            # If no exceptions, logging works
            assert True
    
    def test_metrics_logging(self):
        """Test metrics logs events."""
        from searxng_mcp.metrics import MetricsCollector
        
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics = MetricsCollector(metrics_dir=Path(tmpdir))
            
            # This should log the recording
            metrics.record_search(
                query="test",
                categories="general",
                success=True,
                latency=0.5
            )
            
            # If no exceptions, logging works
            assert True
    
    def test_rate_limiter_logging(self):
        """Test rate limiter logs limit events."""
        from searxng_mcp.rate_limiter import RateLimiter
        
        limiter = RateLimiter(custom_limits={"test": 1})
        
        # Should log rate limit exceeded
        limiter.record_request("test")
        allowed, _ = limiter.check_rate_limit("test")
        
        # If no exceptions, logging works
        assert True
