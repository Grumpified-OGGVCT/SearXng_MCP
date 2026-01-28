"""
SearXNG MCP Server Package

A Model Context Protocol 2.0 server for SearXNG metasearch integration.
"""

__version__ = "0.1.0"
__author__ = "Grumpified OGGVCT"
__license__ = "MIT"

from searxng_mcp.server import get_instances, list_categories, main, mcp, search

__all__ = [
    "main",
    "mcp",
    "search",
    "list_categories",
    "get_instances",
    "__version__",
    "__author__",
    "__license__",
]
