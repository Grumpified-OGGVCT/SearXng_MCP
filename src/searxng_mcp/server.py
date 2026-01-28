"""
SearXNG MCP Server

A Model Context Protocol (MCP) 2.0 server providing search capabilities through SearXNG,
a privacy-respecting metasearch engine that aggregates results from 245+ search engines.

Features:
- Multi-instance fallback with automatic health checking
- Cookie-based preference persistence across sessions
- Support for 10 categories with 245+ engines (including regional/non-English)
- Bang syntax for engine/language selection (!go, !bi, :en, :zh)
- Local instance fallback for resilience
- Comprehensive error handling and retry logic
"""

import json
import logging
import os
import time
from http.cookiejar import LWPCookieJar
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx
from fastmcp import FastMCP
from pydantic import Field

from searxng_mcp.cache import ResultCache
from searxng_mcp.metrics import MetricsCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("searxng_mcp")

# Default SearXNG instances (ordered by preference)
DEFAULT_INSTANCES = [
    "https://search.sapti.me",
    "https://searx.be",
    "https://search.bus-hit.me",
    "https://search.mdosch.de",
    "https://searx.tiekoetter.com",
]

# Categories and their common engines
CATEGORY_INFO = {
    "general": "google, bing, duckduckgo, startpage, brave, yandex, baidu, naver, quark, sogou",
    "images": "google_images, bing_images, duckduckgo_images, unsplash, pixabay",
    "videos": "youtube, vimeo, dailymotion, peertube, bilibili, niconico",
    "news": "google_news, bing_news, yahoo_news, reuters, bbc, tagesschau, 360search",
    "map": "openstreetmap, apple_maps, photon",
    "music": "genius, bandcamp, deezer, mixcloud, soundcloud, radio_browser",
    "it": "github, stackoverflow, pypi, docker_hub, huggingface, gitlab",
    "science": "arxiv, pubmed, crossref, semantic_scholar, google_scholar, mediawiki",
    "files": "apkmirror, fdroid, google_play, piratebay, zlibrary, annas_archive, nyaa",
    "social_media": "reddit, mastodon, lemmy, 9gag, tootfinder",
}


class InstanceManager:
    """Manages SearXNG instances with fallback and cookie persistence."""

    def __init__(
        self,
        instances: list[str] | None = None,
        cookie_dir: str | None = None,
        local_instance: str | None = None,
        timeout: float = 5.0,
        local_timeout: float = 15.0,
    ):
        self.instances = instances or DEFAULT_INSTANCES.copy()
        self.local_instance = local_instance
        self.timeout = timeout
        self.local_timeout = local_timeout
        self.cookie_dir = Path(cookie_dir or Path.home() / ".searxng_mcp" / "cookies")
        self.cookie_dir.mkdir(parents=True, exist_ok=True)
        self.cookie_jars: dict[str, LWPCookieJar] = {}
        self._init_cookie_jars()

    def _init_cookie_jars(self) -> None:
        """Initialize cookie jars for each instance."""
        for instance in self.instances + ([self.local_instance] if self.local_instance else []):
            cookie_file = self.cookie_dir / f"{self._sanitize_url(instance)}.txt"
            jar = LWPCookieJar(str(cookie_file))
            try:
                if cookie_file.exists():
                    jar.load(ignore_discard=True, ignore_expires=True)
                    logger.debug(f"Loaded cookies for {instance}")
            except Exception as e:
                logger.warning(f"Failed to load cookies for {instance}: {e}")
            self.cookie_jars[instance] = jar

    def _sanitize_url(self, url: str) -> str:
        """Convert URL to safe filename."""
        return (
            url.replace("https://", "").replace("http://", "").replace("/", "_").replace(":", "_")
        )

    def save_cookies(self, instance: str) -> None:
        """Save cookies for a specific instance."""
        if instance in self.cookie_jars:
            try:
                self.cookie_jars[instance].save(ignore_discard=True, ignore_expires=True)
                logger.debug(f"Saved cookies for {instance}")
            except Exception as e:
                logger.warning(f"Failed to save cookies for {instance}: {e}")

    async def search(
        self,
        query: str,
        categories: str | None = None,
        engines: str | None = None,
        language: str = "en",
        time_range: str | None = None,
        safesearch: int = 0,
        page: int = 1,
    ) -> dict[str, Any]:
        """
        Perform search with automatic instance fallback.

        Args:
            query: Search query (supports bang syntax: !go, :zh, etc.)
            categories: Comma-separated categories (general, images, videos, etc.)
            engines: Comma-separated engine names
            language: Language code (en, zh, de, etc.)
            time_range: Time range filter (day, week, month, year)
            safesearch: Safe search level (0=off, 1=moderate, 2=strict)
            page: Results page number

        Returns:
            Search results dictionary with results, suggestions, and metadata
        """
        params = {
            "q": query,
            "format": "json",
            "language": language,
            "safesearch": safesearch,
            "pageno": page,
        }
        if categories:
            params["categories"] = categories
        if engines:
            params["engines"] = engines
        if time_range:
            params["time_range"] = time_range

        # Try online instances first
        for instance in self.instances:
            try:
                result = await self._search_instance(instance, params, self.timeout)
                if result:
                    return result
            except Exception as e:
                logger.exception(f"Instance {instance} failed: {e}")
                continue

        # Fallback to local instance if configured
        if self.local_instance:
            try:
                logger.info(f"Falling back to local instance: {self.local_instance}")
                result = await self._search_instance(
                    self.local_instance, params, self.local_timeout
                )
                if result:
                    return result
            except Exception as e:
                logger.exception(f"Local instance {self.local_instance} failed: {e}")

        raise Exception("All SearXNG instances failed. Please try again later.")

    async def _search_instance(
        self, instance: str, params: dict[str, Any], timeout: float
    ) -> dict[str, Any] | None:
        """Search a specific instance."""
        url = urljoin(instance, "/search")
        jar = self.cookie_jars.get(instance)

        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            cookies=jar,
        ) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()

            # Update cookies
            if jar and response.cookies:
                for cookie in response.cookies.jar:
                    jar.set_cookie(cookie)
                self.save_cookies(instance)

            data = response.json()
            data["_instance"] = instance
            logger.info(f"Search successful on {instance}: {len(data.get('results', []))} results")
            return data


# Initialize FastMCP server
mcp = FastMCP("SearXNG Search")

# Global instance manager
instance_manager: InstanceManager | None = None

# Global cache and metrics instances
_cache: ResultCache | None = None
_metrics: MetricsCollector | None = None


def get_instance_manager() -> InstanceManager:
    """Get or create the global instance manager."""
    global instance_manager
    if instance_manager is None:
        instances = os.environ.get("SEARXNG_INSTANCES")
        instance_list = instances.split(",") if instances else None
        local = os.environ.get("SEARXNG_LOCAL_INSTANCE")
        instance_manager = InstanceManager(
            instances=instance_list,
            local_instance=local,
        )
    return instance_manager


def get_cache() -> ResultCache:
    """Get or create the global cache instance."""
    global _cache
    if _cache is None:
        _cache = ResultCache()
        logger.info("Cache initialized")
    return _cache


def get_metrics() -> MetricsCollector:
    """Get or create the global metrics collector."""
    global _metrics
    if _metrics is None:
        _metrics = MetricsCollector()
        logger.info("Metrics collector initialized")
    return _metrics


@mcp.tool()
async def search(
    query: str = Field(
        description="Search query. Supports bang syntax (!go, !bi) and language "
        "modifiers (:en, :zh)"
    ),
    categories: str | None = Field(
        None,
        description="Comma-separated categories: general, images, videos, news, map, "
        "music, it, science, files, social_media",
    ),
    engines: str | None = Field(
        None,
        description="Comma-separated engine names (e.g., google, bing, duckduckgo, arxiv, github)",
    ),
    language: str = Field(
        "en",
        description="Language code (en, zh, de, fr, es, ja, ko, ru, ar, etc.)",
    ),
    time_range: str | None = Field(
        None,
        description="Filter by time: day, week, month, year",
    ),
    safesearch: int = Field(
        0,
        description="Safe search level: 0=off, 1=moderate, 2=strict",
    ),
    page: int = Field(
        1,
        description="Results page number (1-based)",
    ),
    ai_enhance: bool = Field(
        False,
        description="Enable AI-powered result enhancement using Mistral Large 3. "
        "Requires SEARXNG_AI_PROVIDER (openrouter/ollama/gemini) and SEARXNG_AI_API_KEY.",
    ),
) -> str:
    """
    Search using SearXNG metasearch engine across 245+ engines with optional AI enhancement.

    SearXNG aggregates results from multiple search engines including regional and non-English
    engines. Supports bang syntax for engine selection (!go for Google, !gh for GitHub, etc.)
    and language modifiers (:en, :zh, :de, etc.).

    When ai_enhance=True, results are enhanced with:
    - AI-powered summary (2-3 paragraphs)
    - Key insights (3-5 bullet points)
    - Recommended sources (top 3)

    Examples:
        - "python asyncio" - General search
        - "python asyncio !gh" - Search GitHub
        - "machine learning :zh" - Search in Chinese
        - "quantum computing category:science" - Search scientific sources
        - "cat pictures" with categories="images" - Image search
        - "AI research" with ai_enhance=True - Get AI-enhanced summary
    """
    manager = get_instance_manager()
    cache = get_cache()
    metrics = get_metrics()
    
    start_time = time.time()
    cached_result = False
    ai_provider = None
    ai_model = None
    search_success = True
    error_msg = None
    
    try:
        # Check cache first
        cached = cache.get(
            query=query,
            categories=categories or "",
            engines=engines or "",
            language=language,
            time_range=time_range or "",
            safesearch=safesearch,
            ai_enhance=ai_enhance,
        )
        
        if cached:
            logger.info(f"Cache hit for query: {query[:50]}...")
            cached_result = True
            results = cached
        else:
            logger.info(f"Cache miss for query: {query[:50]}...")
            # Perform search
            results = await manager.search(
                query=query,
                categories=categories,
                engines=engines,
                language=language,
                time_range=time_range,
                safesearch=safesearch,
                page=page,
            )
            
            # Apply AI enhancement if requested
            if ai_enhance:
                try:
                    from searxng_mcp.ai_enhancer import get_ai_enhancer
                    
                    enhancer = get_ai_enhancer()
                    if enhancer.is_enabled():
                        ai_provider = enhancer.provider
                        ai_model = enhancer.model
                        logger.info(f"Applying AI enhancement with provider: {ai_provider}")
                        search_results = results.get("results", [])
                        enhanced = await enhancer.enhance_results(query, search_results)
                        results["ai_enhancement"] = enhanced
                        logger.info("AI enhancement completed successfully")
                    else:
                        results["ai_enhancement"] = {
                            "enabled": False,
                            "message": "AI enhancement requires SEARXNG_AI_PROVIDER and SEARXNG_AI_API_KEY environment variables",
                            "supported_providers": ["openrouter", "ollama", "gemini"],
                        }
                except Exception as e:
                    logger.exception(f"AI enhancement failed: {e}")
                    error_msg = f"AI enhancement failed: {str(e)}"
                    results["ai_enhancement"] = {
                        "enabled": False,
                        "error": str(e),
                        "message": "AI enhancement failed but search results are still available",
                    }
            
            # Cache the result
            cache.set(
                data=results,
                query=query,
                categories=categories or "",
                engines=engines or "",
                language=language,
                time_range=time_range or "",
                safesearch=safesearch,
                ai_enhance=ai_enhance,
            )
        
        latency = time.time() - start_time
        
        # Record metrics
        metrics.record_search(
            query=query,
            categories=categories or "",
            ai_enhanced=ai_enhance,
            cached=cached_result,
            latency=latency,
            success=search_success,
            error=error_msg,
            provider=ai_provider,
            model=ai_model,
            token_estimate={"input": 2000, "output": 500} if ai_enhance else None,
        )
        
        return json.dumps(results, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.exception(f"Search failed: {e}")
        error_msg = str(e)
        search_success = False
        latency = time.time() - start_time
        
        # Record failure in metrics
        metrics.record_search(
            query=query,
            categories=categories or "",
            ai_enhanced=ai_enhance,
            cached=False,
            latency=latency,
            success=False,
            error=error_msg,
            provider=ai_provider,
            model=ai_model,
        )
        
        return json.dumps({"error": error_msg}, indent=2)


@mcp.tool()
async def list_categories() -> str:
    """
    List available SearXNG search categories and their popular engines.

    Returns information about the 10 main categories:
    - general: General web search (google, bing, duckduckgo, yandex, baidu, etc.)
    - images: Image search (google_images, unsplash, pixabay, etc.)
    - videos: Video search (youtube, vimeo, bilibili, etc.)
    - news: News search (google_news, bbc, reuters, etc.)
    - map: Map and location search (openstreetmap, apple_maps, etc.)
    - music: Music search (genius, soundcloud, bandcamp, etc.)
    - it: IT and software search (github, stackoverflow, pypi, etc.)
    - science: Scientific search (arxiv, pubmed, google_scholar, etc.)
    - files: File search (fdroid, apkmirror, etc.)
    - social_media: Social media search (reddit, mastodon, lemmy, etc.)
    """
    return json.dumps(CATEGORY_INFO, indent=2, ensure_ascii=False)


@mcp.tool()
async def get_instances() -> str:
    """
    Get the list of currently configured SearXNG instances.

    Returns the ordered list of online instances and local instance (if configured).
    Instances are tried in order with automatic fallback to the next on failure.
    """
    manager = get_instance_manager()
    info = {
        "online_instances": manager.instances,
        "local_instance": manager.local_instance,
        "timeout": manager.timeout,
        "local_timeout": manager.local_timeout,
    }
    return json.dumps(info, indent=2)


@mcp.tool()
async def get_cache_stats() -> str:
    """
    Get cache statistics and performance metrics.
    
    Returns cache hit/miss rates, size, and configuration.
    """
    cache = get_cache()
    stats = cache.get_cache_info()
    return json.dumps(stats, indent=2)


@mcp.tool()
async def clear_cache() -> str:
    """
    Clear all cached search results.
    
    Returns the number of entries cleared.
    """
    cache = get_cache()
    count = cache.clear()
    return json.dumps({"cleared": count, "message": f"Cleared {count} cache entries"}, indent=2)


@mcp.tool()
async def get_session_stats() -> str:
    """
    Get current session metrics.
    
    Returns request counts, latency, cost estimates, and provider statistics.
    """
    metrics_collector = get_metrics()
    stats = metrics_collector.get_session_metrics()
    return json.dumps(stats, indent=2)


def main() -> None:
    """Run the MCP server."""
    logger.info("Starting SearXNG MCP server...")
    
    # Initialize systems
    get_cache()
    get_metrics()
    
    # Run periodic cleanup
    import asyncio
    
    async def periodic_cleanup():
        """Periodic cleanup task."""
        while True:
            await asyncio.sleep(3600)  # Every hour
            try:
                cache = get_cache()
                cleaned = cache.cleanup_expired()
                logger.debug(f"Periodic cleanup: removed {cleaned} expired cache entries")
            except Exception as e:
                logger.error(f"Periodic cleanup error: {e}")
    
    # Start cleanup task in background
    try:
        import threading
        def run_cleanup():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(periodic_cleanup())
        
        cleanup_thread = threading.Thread(target=run_cleanup, daemon=True)
        cleanup_thread.start()
    except Exception as e:
        logger.warning(f"Could not start periodic cleanup: {e}")
    
    mcp.run()


if __name__ == "__main__":
    main()
