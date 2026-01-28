"""
AI-Powered Search Enhancement Module

Provides intelligent scraping, summarization, and presentation of search results
using Gemini Flash models via multiple providers:
- OpenRouter (google/gemini-2.0-flash-exp)
- Ollama Cloud (gemini-3-flash-preview:cloud)
- Google Gemini (auto-detected latest Flash model)
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any

try:
    import httpx
except ImportError:
    httpx = None

from searxng_mcp.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class AIEnhancer:
    """
    AI-powered search result enhancement using Gemini Flash models.
    
    Supports multiple providers, all using Gemini Flash for optimal performance:
    - OpenRouter: google/gemini-2.0-flash-exp
    - Ollama Cloud: gemini-3-flash-preview:cloud
    - Google Gemini: Auto-detected latest Flash model
    """

    def __init__(self):
        """Initialize AI enhancer with configuration."""
        self.provider = os.environ.get("SEARXNG_AI_PROVIDER", "").lower()
        self.api_key = os.environ.get("SEARXNG_AI_API_KEY", "")
        self.model = os.environ.get("SEARXNG_AI_MODEL", "")
        self.enabled = self.provider and self.api_key

        # Set default models based on provider
        # All providers use Gemini Flash for optimal speed/cost/quality balance
        if self.provider == "openrouter" and not self.model:
            self.model = "google/gemini-2.0-flash-exp"
        elif self.provider == "ollama" and not self.model:
            self.model = "gemini-3-flash-preview:cloud"
        elif self.provider == "gemini" and not self.model:
            # Auto-detect latest Flash model or use current default
            self.model = self._get_latest_gemini_flash_model()

        # Provider configurations
        self.config = self._get_provider_config()
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter()
        logger.info(f"AI enhancer initialized with provider: {self.provider}, model: {self.model}")

    def _get_provider_config(self) -> Dict[str, Any]:
        """Get provider-specific configuration."""
        configs = {
            "openrouter": {
                "base_url": "https://openrouter.ai/api/v1",
                "headers": {
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "https://github.com/Grumpified-OGGVCT/SearXng_MCP",
                    "X-Title": "SearXNG MCP Server",
                },
            },
            "ollama": {
                "base_url": "https://ollama.com/api",
                "headers": {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            },
            "gemini": {
                "base_url": "https://generativelanguage.googleapis.com/v1beta",
                "headers": {
                    "Content-Type": "application/json",
                },
                "api_key_param": True,  # Gemini uses ?key= parameter
                "api_key": self.api_key,  # Store API key for Gemini
            },
        }

        return configs.get(self.provider, {})
    
    def _get_latest_gemini_flash_model(self) -> str:
        """
        Auto-detect the latest Gemini Flash model.
        
        Returns the latest available Flash model or falls back to known default.
        Checks Google's model list API for the newest gemini-*-flash model.
        """
        default_model = "gemini-2.0-flash-exp"  # Fallback model (Jan 2026)
        
        if not self.api_key or httpx is None:
            return default_model
            
        try:
            # Try to fetch available models from Google API
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    models = data.get("models", [])
                    
                    # Find all flash models and sort by version
                    flash_models = []
                    for model in models:
                        name = model.get("name", "")
                        # Extract model name from "models/gemini-x.x-flash-xxx" format
                        if "flash" in name.lower():
                            model_id = name.split("/")[-1] if "/" in name else name
                            # Prefer experimental versions as they're the latest
                            if "exp" in model_id or "latest" in model_id:
                                flash_models.insert(0, model_id)
                            else:
                                flash_models.append(model_id)
                    
                    # Return the first (most recent) flash model found
                    if flash_models:
                        return flash_models[0]
                else:
                    # Log non-200 responses for debugging
                    logger.warning(
                        f"Gemini model detection failed with status {response.status_code}, "
                        f"using fallback model {default_model}"
                    )
                        
        except Exception as e:
            # Log but don't fail - just use default
            # Don't log exception details to avoid exposing API key
            logger.debug(f"Could not auto-detect Gemini model, using fallback: {default_model}")
            
        return default_model

    def is_enabled(self) -> bool:
        """Check if AI enhancement is enabled."""
        return self.enabled and httpx is not None

    async def enhance_results(
        self, query: str, results: List[Dict], max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Enhance search results with AI-powered summarization and insights.

        Args:
            query: Original search query
            results: Raw search results from SearXNG
            max_results: Maximum number of results to process

        Returns:
            Enhanced results with AI summary, key insights, and organized data
        """
        if not self.is_enabled():
            return {
                "enhanced": False,
                "reason": "AI enhancement not configured",
                "original_results": results,
            }

        try:
            # Prepare context from search results
            context = self._prepare_context(query, results[:max_results])

            # Generate AI enhancement
            enhancement = await self._generate_enhancement(query, context)

            return {
                "enhanced": True,
                "query": query,
                "ai_summary": enhancement.get("summary", ""),
                "key_insights": enhancement.get("insights", []),
                "recommended_sources": enhancement.get("sources", []),
                "original_results": results,
                "model": self.model,
                "provider": self.provider,
            }

        except Exception as e:
            return {
                "enhanced": False,
                "reason": f"AI enhancement failed: {str(e)}",
                "original_results": results,
            }

    def _prepare_context(self, query: str, results: List[Dict]) -> str:
        """Prepare context from search results for AI processing."""
        from datetime import datetime
        
        # Get current date and time for context
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        context_parts = [
            f"Current Date and Time: {current_datetime}\n",
            f"Note: Use this current date for any time-sensitive analysis, not your training cutoff date.\n\n",
            f"Search Query: {query}\n\n",
            f"Search Results ({len(results)} sources):\n"
        ]

        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            url = result.get("url", "")
            content = result.get("content", "")
            engine = result.get("engine", "unknown")

            context_parts.append(
                f"\n{i}. {title}\n"
                f"   Source: {engine}\n"
                f"   URL: {url}\n"
                f"   Content: {content}\n"
            )

        return "".join(context_parts)

    async def _generate_enhancement(
        self, query: str, context: str
    ) -> Dict[str, Any]:
        """Generate AI enhancement using configured provider."""
        system_prompt = """You are an expert research analyst with access to current web search results.

CRITICAL INSTRUCTIONS:
1. The search results provided are CURRENT and from TODAY. Use the provided current date/time, NOT your training cutoff date.
2. Provide COMPREHENSIVE, DETAILED summaries - do not abbreviate or "whittle down" information.
3. Extract facts and truths from ALL provided sources - be thorough and inclusive.
4. Your summary should be 3-5 paragraphs of substantive analysis, not brief snippets.
5. Include specific details, statistics, quotes, and findings from the sources.
6. When referencing time-sensitive information, use the current date provided in the context.

Your task:
1. Provide a COMPREHENSIVE summary (3-5 substantial paragraphs) synthesizing ALL search results
2. Extract 5-7 key insights or important findings (be specific and detailed)
3. Recommend the top 3-5 most valuable sources with detailed explanations of why they're important

Format your response as JSON with these keys:
- summary: A comprehensive 3-5 paragraph analysis covering all major findings
- insights: Array of 5-7 detailed key insights with specifics
- sources: Array of top 3-5 source recommendations, each with:
  - title: Source title
  - url: Source URL  
  - reason: Detailed explanation (2-3 sentences) of why this source is valuable

Be thorough, accurate, and comprehensive. Quality over brevity."""

        user_prompt = f"{context}\n\nProvide a comprehensive enhancement of these search results."

        if self.provider == "openrouter":
            return await self._call_openrouter(system_prompt, user_prompt)
        elif self.provider == "ollama":
            return await self._call_ollama(system_prompt, user_prompt)
        elif self.provider == "gemini":
            return await self._call_gemini(system_prompt, user_prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    async def _call_openrouter(
        self, system_prompt: str, user_prompt: str
    ) -> Dict[str, Any]:
        """Call OpenRouter API with rate limiting."""
        # Check rate limit
        allowed = await self.rate_limiter.wait_if_needed(self.provider)
        if not allowed:
            raise Exception(f"Rate limit exceeded for {self.provider}")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.config['base_url']}/chat/completions",
                    headers=self.config["headers"],
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "response_format": {"type": "json_object"},
                    },
                )

                response.raise_for_status()
                data = response.json()

                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.error(f"Rate limit error from {self.provider}: {e}")
                raise Exception(f"Rate limit exceeded by provider: {self.provider}")
            raise

    async def _call_ollama(
        self, system_prompt: str, user_prompt: str
    ) -> Dict[str, Any]:
        """Call Ollama Cloud API with rate limiting."""
        # Check rate limit
        allowed = await self.rate_limiter.wait_if_needed(self.provider)
        if not allowed:
            raise Exception(f"Rate limit exceeded for {self.provider}")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.config['base_url']}/chat",
                    headers=self.config["headers"],
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "stream": False,
                        "format": "json",
                    },
                )

                response.raise_for_status()
                data = response.json()

                content = data["message"]["content"]
                return json.loads(content)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.error(f"Rate limit error from {self.provider}: {e}")
                raise Exception(f"Rate limit exceeded by provider: {self.provider}")
            raise

    async def _call_gemini(
        self, system_prompt: str, user_prompt: str
    ) -> Dict[str, Any]:
        """Call Google Gemini API with rate limiting."""
        # Check rate limit
        allowed = await self.rate_limiter.wait_if_needed(self.provider)
        if not allowed:
            raise Exception(f"Rate limit exceeded for {self.provider}")
        
        # Combine system and user prompts for Gemini
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.config['base_url']}/models/{self.model}:generateContent?key={self.api_key}",
                    headers=self.config["headers"],
                    json={
                        "contents": [{"parts": [{"text": combined_prompt}]}],
                        "generationConfig": {
                            "response_mime_type": "application/json",
                        },
                    },
                )

                response.raise_for_status()
                data = response.json()

                content = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(content)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.error(f"Rate limit error from {self.provider}: {e}")
                raise Exception(f"Rate limit exceeded by provider: {self.provider}")
            raise

    async def quick_summary(self, query: str, results: List[Dict]) -> str:
        """
        Generate a quick one-paragraph summary of results.

        Args:
            query: Search query
            results: Search results

        Returns:
            One-paragraph summary
        """
        if not self.is_enabled():
            return "AI enhancement not available."

        try:
            context = self._prepare_context(query, results[:5])

            system_prompt = "You are a concise research assistant. Summarize search results in exactly one paragraph."
            user_prompt = f"{context}\n\nProvide a one-paragraph summary."

            if self.provider == "openrouter":
                response = await self._call_openrouter(system_prompt, user_prompt)
            elif self.provider == "ollama":
                response = await self._call_ollama(system_prompt, user_prompt)
            elif self.provider == "gemini":
                response = await self._call_gemini(system_prompt, user_prompt)
            else:
                return "Unsupported AI provider."

            return response.get("summary", "Summary generation failed.")

        except Exception as e:
            return f"Summary generation failed: {str(e)}"


# Global enhancer instance
_enhancer: Optional[AIEnhancer] = None


def get_ai_enhancer() -> AIEnhancer:
    """Get or create global AI enhancer instance."""
    global _enhancer
    if _enhancer is None:
        _enhancer = AIEnhancer()
    return _enhancer
