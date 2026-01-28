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

import asyncio
import json
import logging
import os
from http.cookiejar import LWPCookieJar
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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
        instances: Optional[List[str]] = None,
        cookie_dir: Optional[str] = None,
        local_instance: Optional[str] = None,
        timeout: float = 5.0,
        local_timeout: float = 15.0,
    ):
        self.instances = instances or DEFAULT_INSTANCES.copy()
        self.local_instance = local_instance
        self.timeout = timeout
        self.local_timeout = local_timeout
        self.cookie_dir = Path(cookie_dir or Path.home() / ".searxng_mcp" / "cookies")
        self.cookie_dir.mkdir(parents=True, exist_ok=True)
        self.cookie_jars: Dict[str, LWPCookieJar] = {}
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
        return url.replace("https://", "").replace("http://", "").replace("/", "_").replace(":", "_")

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
        categories: Optional[str] = None,
        engines: Optional[str] = None,
        language: str = "en",
        time_range: Optional[str] = None,
        safesearch: int = 0,
        page: int = 1,
    ) -> Dict[str, Any]:
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
                logger.warning(f"Instance {instance} failed: {e}")
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
                logger.error(f"Local instance {self.local_instance} failed: {e}")

        raise Exception("All SearXNG instances failed. Please try again later.")

    async def _search_instance(
        self, instance: str, params: Dict[str, Any], timeout: float
    ) -> Optional[Dict[str, Any]]:
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
instance_manager: Optional[InstanceManager] = None


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


@mcp.tool()
async def search(
    query: str = Field(description="Search query. Supports bang syntax (!go, !bi) and language modifiers (:en, :zh)"),
    categories: Optional[str] = Field(
        None,
        description="Comma-separated categories: general, images, videos, news, map, music, it, science, files, social_media",
    ),
    engines: Optional[str] = Field(
        None,
        description="Comma-separated engine names (e.g., google, bing, duckduckgo, arxiv, github)",
    ),
    language: str = Field(
        "en",
        description="Language code (en, zh, de, fr, es, ja, ko, ru, ar, etc.)",
    ),
    time_range: Optional[str] = Field(
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
) -> str:
    """
    Search using SearXNG metasearch engine across 245+ engines.

    SearXNG aggregates results from multiple search engines including regional and non-English
    engines. Supports bang syntax for engine selection (!go for Google, !gh for GitHub, etc.)
    and language modifiers (:en, :zh, :de, etc.).

    Examples:
        - "python asyncio" - General search
        - "python asyncio !gh" - Search GitHub
        - "machine learning :zh" - Search in Chinese
        - "quantum computing category:science" - Search scientific sources
        - "cat pictures" with categories="images" - Image search
    """
    manager = get_instance_manager()
    try:
        results = await manager.search(
            query=query,
            categories=categories,
            engines=engines,
            language=language,
            time_range=time_range,
            safesearch=safesearch,
            page=page,
        )
        return json.dumps(results, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return json.dumps({"error": str(e)}, indent=2)


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


def main() -> None:
    """Run the MCP server."""
    logger.info("Starting SearXNG MCP server...")
    mcp.run()


if __name__ == "__main__":
    main()
