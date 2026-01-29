"""
Tests for configuration module.
"""

import os
import pytest
from searxng_mcp.config import get_config, DEFAULT_CONFIG


def test_default_config():
    """Test default configuration values."""
    config = DEFAULT_CONFIG

    assert "instances" in config
    assert len(config["instances"]) > 0
    assert config["timeout"] == 5.0
    assert config["local_timeout"] == 15.0


def test_get_config_defaults(monkeypatch):
    """Test get_config returns defaults when no env vars set."""
    # Clear any environment variables
    for key in ["SEARXNG_INSTANCES", "SEARXNG_LOCAL_INSTANCE", "SEARXNG_TIMEOUT"]:
        monkeypatch.delenv(key, raising=False)

    config = get_config()

    assert config["instances"] == DEFAULT_CONFIG["instances"]
    assert config["timeout"] == DEFAULT_CONFIG["timeout"]


def test_get_config_custom_instances(monkeypatch):
    """Test custom instances from environment."""
    monkeypatch.setenv("SEARXNG_INSTANCES", "https://test1.com,https://test2.com")

    config = get_config()

    assert len(config["instances"]) == 2
    assert "https://test1.com" in config["instances"]
    assert "https://test2.com" in config["instances"]


def test_get_config_custom_timeout(monkeypatch):
    """Test custom timeout from environment."""
    monkeypatch.setenv("SEARXNG_TIMEOUT", "15.0")

    config = get_config()

    assert config["timeout"] == 15.0


def test_get_config_invalid_timeout(monkeypatch):
    """Test invalid timeout value is ignored."""
    monkeypatch.setenv("SEARXNG_TIMEOUT", "invalid")

    config = get_config()

    # Should fall back to default
    assert config["timeout"] == DEFAULT_CONFIG["timeout"]
