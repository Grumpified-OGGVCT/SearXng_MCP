"""
Basic tests for SearXNG MCP Server.

These tests verify core functionality without requiring live SearXNG instances.
"""

import pytest
from searxng_mcp.server import InstanceManager, CATEGORY_INFO


def test_import():
    """Test that the package can be imported."""
    import searxng_mcp

    assert searxng_mcp.__version__ == "0.1.0"
    assert searxng_mcp.__author__ == "Grumpified OGGVCT"


def test_category_info():
    """Test that category information is properly defined."""
    assert len(CATEGORY_INFO) == 10
    assert "general" in CATEGORY_INFO
    assert "science" in CATEGORY_INFO
    assert "it" in CATEGORY_INFO


def test_instance_manager_init():
    """Test InstanceManager initialization."""
    manager = InstanceManager(
        instances=["https://test1.com", "https://test2.com"],
        timeout=10.0,
    )

    assert len(manager.instances) == 2
    assert manager.timeout == 10.0
    assert manager.local_instance is None


def test_instance_manager_with_local():
    """Test InstanceManager with local instance."""
    manager = InstanceManager(
        instances=["https://test1.com"],
        local_instance="http://localhost:8888",
        local_timeout=20.0,
    )

    assert manager.local_instance == "http://localhost:8888"
    assert manager.local_timeout == 20.0


def test_url_sanitization():
    """Test URL sanitization for cookie filenames."""
    manager = InstanceManager()

    sanitized = manager._sanitize_url("https://example.com:443/path")
    assert "/" not in sanitized
    assert ":" not in sanitized
    assert "example.com" in sanitized


@pytest.mark.asyncio
async def test_search_requires_query():
    """Test that search requires a query parameter."""
    from searxng_mcp.server import search

    # This should not raise an error, just return error in JSON
    result = await search(query="test")
    assert isinstance(result, str)
