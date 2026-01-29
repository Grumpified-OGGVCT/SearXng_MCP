"""
SearXNG MCP Server Package

A Model Context Protocol 2.0 server for SearXNG metasearch integration.
"""

__version__ = "0.1.0"
__author__ = "Grumpified OGGVCT"
__license__ = "MIT"


# Lazy imports to avoid dependency issues during installation
def __getattr__(name):
    """Lazy import of server functions to avoid requiring dependencies at import time."""
    if name in ("main", "mcp", "search", "list_categories", "get_instances"):
        from searxng_mcp import server

        return getattr(server, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


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
