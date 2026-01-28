"""
Configuration module for SearXNG MCP Server.

Handles loading configuration from environment variables and config files.
"""

import os
from pathlib import Path
from typing import List, Optional

# Default configuration
DEFAULT_CONFIG = {
    "instances": [
        "https://search.sapti.me",
        "https://searx.be",
        "https://search.bus-hit.me",
        "https://search.mdosch.de",
        "https://searx.tiekoetter.com",
    ],
    "timeout": 5.0,
    "local_timeout": 15.0,
    "cookie_dir": str(Path.home() / ".searxng_mcp" / "cookies"),
}


def get_config() -> dict:
    """
    Load configuration from environment variables.

    Environment Variables:
        SEARXNG_INSTANCES: Comma-separated list of instance URLs
        SEARXNG_LOCAL_INSTANCE: Optional local instance URL
        SEARXNG_TIMEOUT: Request timeout in seconds (default: 5.0)
        SEARXNG_LOCAL_TIMEOUT: Local instance timeout in seconds (default: 15.0)
        SEARXNG_COOKIE_DIR: Directory for cookie storage

    Returns:
        Configuration dictionary
    """
    config = DEFAULT_CONFIG.copy()

    # Load instances from environment
    instances_env = os.environ.get("SEARXNG_INSTANCES")
    if instances_env:
        config["instances"] = [i.strip() for i in instances_env.split(",")]

    # Load local instance
    local_instance = os.environ.get("SEARXNG_LOCAL_INSTANCE")
    if local_instance:
        config["local_instance"] = local_instance.strip()

    # Load timeouts
    timeout = os.environ.get("SEARXNG_TIMEOUT")
    if timeout:
        try:
            config["timeout"] = float(timeout)
        except ValueError:
            pass

    local_timeout = os.environ.get("SEARXNG_LOCAL_TIMEOUT")
    if local_timeout:
        try:
            config["local_timeout"] = float(local_timeout)
        except ValueError:
            pass

    # Load cookie directory
    cookie_dir = os.environ.get("SEARXNG_COOKIE_DIR")
    if cookie_dir:
        config["cookie_dir"] = cookie_dir

    return config
