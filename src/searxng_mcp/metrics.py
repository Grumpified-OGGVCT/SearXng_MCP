"""
Metrics Collection System for SearXNG MCP Server

Tracks requests, costs, latency, errors, and provider usage for monitoring and optimization.
Respects user privacy preferences - can be fully disabled.
"""

import json
import logging
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collects and stores metrics for monitoring and analysis.

    Privacy-first design:
    - Respects SEARXNG_METRICS_ENABLED environment variable
    - Does NOT log actual search queries by default
    - Only logs partial queries (first 50 chars) if SEARXNG_LOG_QUERIES=true
    - All data stored locally (never uploaded to any server)

    Features:
    - Request counting and tracking
    - Response time measurement
    - Cost estimation
    - Error tracking
    - Provider breakdown
    - Historical data retention
    """

    # Estimated costs per 1M tokens (as of Jan 2026)
    PROVIDER_COSTS = {
        "openrouter": {
            "google/gemini-2.0-flash-exp": {"input": 0.075, "output": 0.30},
        },
        "ollama": {
            "gemini-3-flash-preview:cloud": {"input": 0.10, "output": 0.40},
        },
        "gemini": {
            "gemini-2.0-flash-exp": {"input": 0.075, "output": 0.30},
        },
    }

    def __init__(self, metrics_dir: Path | None = None):
        """
        Initialize metrics collector.

        Args:
            metrics_dir: Directory for metrics storage
        """
        # Check if metrics are enabled via environment variable
        self.enabled = os.environ.get("SEARXNG_METRICS_ENABLED", "true").lower() == "true"
        self.log_queries = os.environ.get("SEARXNG_LOG_QUERIES", "false").lower() == "true"

        if not self.enabled:
            logger.info("Metrics collection disabled (SEARXNG_METRICS_ENABLED=false)")
            return

        self.metrics_dir = metrics_dir or (Path.home() / ".searxng_mcp" / "metrics")
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        # In-memory metrics (current session)
        self.session_metrics = {
            "start_time": time.time(),
            "requests": {
                "total": 0,
                "search_only": 0,
                "ai_enhanced": 0,
                "cached": 0,
            },
            "providers": defaultdict(
                lambda: {
                    "requests": 0,
                    "successes": 0,
                    "failures": 0,
                    "total_latency": 0.0,
                }
            ),
            "categories": defaultdict(int),
            "errors": [],
            "cost_estimate": 0.0,
        }

        logger.info(
            f"Metrics collection enabled. Query logging: {'enabled' if self.log_queries else 'disabled'}"
        )

    def record_search(
        self,
        query: str,
        categories: str = "",
        ai_enhanced: bool = False,
        cached: bool = False,
        latency: float = 0.0,
        success: bool = True,
        error: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        token_estimate: dict[str, int] | None = None,
    ):
        """
        Record a search request.

        Respects privacy settings:
        - If metrics disabled, does nothing
        - Query text only logged if SEARXNG_LOG_QUERIES=true (truncated to 50 chars)

        Args:
            query: Search query
            categories: Search categories
            ai_enhanced: Whether AI enhancement was used
            cached: Whether result was cached
            latency: Response time in seconds
            success: Whether request succeeded
            error: Error message if failed
            provider: AI provider used
            model: AI model used
            token_estimate: Estimated tokens {input, output}
        """
        # Skip if metrics disabled
        if not self.enabled:
            return

        # Update request counts
        self.session_metrics["requests"]["total"] += 1
        if ai_enhanced:
            self.session_metrics["requests"]["ai_enhanced"] += 1
        else:
            self.session_metrics["requests"]["search_only"] += 1
        if cached:
            self.session_metrics["requests"]["cached"] += 1

        # Update category counts
        if categories:
            for cat in categories.split(","):
                self.session_metrics["categories"][cat.strip()] += 1

        # Update provider metrics
        if provider:
            prov_metrics = self.session_metrics["providers"][provider]
            prov_metrics["requests"] += 1
            prov_metrics["total_latency"] += latency

            if success:
                prov_metrics["successes"] += 1
            else:
                prov_metrics["failures"] += 1

            # Estimate cost
            if token_estimate and model:
                cost = self._estimate_cost(provider, model, token_estimate)
                self.session_metrics["cost_estimate"] += cost

        # Record errors (with privacy respect)
        if error:
            # Only log partial query if query logging is enabled
            query_log = None
            if self.log_queries:
                query_log = query[:50] if query else None  # Truncate for privacy

            self.session_metrics["errors"].append(
                {
                    "timestamp": time.time(),
                    "query": query_log,  # None if logging disabled
                    "error": error,
                    "provider": provider,
                }
            )

            # Keep only last 100 errors
            if len(self.session_metrics["errors"]) > 100:
                self.session_metrics["errors"] = self.session_metrics["errors"][-100:]

        # Persist to disk periodically
        if self.session_metrics["requests"]["total"] % 10 == 0:
            self._persist_metrics()

    def _estimate_cost(self, provider: str, model: str, token_estimate: dict[str, int]) -> float:
        """
        Estimate cost based on provider, model, and token usage.

        Args:
            provider: Provider name
            model: Model name
            token_estimate: Dictionary with 'input' and 'output' token counts

        Returns:
            Estimated cost in USD
        """
        try:
            costs = self.PROVIDER_COSTS.get(provider, {}).get(model, {})
            if not costs:
                return 0.0

            input_tokens = token_estimate.get("input", 0)
            output_tokens = token_estimate.get("output", 0)

            input_cost = (input_tokens / 1_000_000) * costs.get("input", 0)
            output_cost = (output_tokens / 1_000_000) * costs.get("output", 0)

            return input_cost + output_cost

        except Exception as e:
            logger.warning(f"Cost estimation error: {e}")
            return 0.0

    def get_session_metrics(self) -> dict[str, Any]:
        """
        Get current session metrics.

        Returns:
            Dictionary with session metrics or empty dict if disabled
        """
        if not self.enabled:
            return {"enabled": False, "message": "Metrics collection disabled"}

        uptime = time.time() - self.session_metrics["start_time"]
        total_requests = self.session_metrics["requests"]["total"]

        # Calculate provider statistics
        provider_stats = {}
        for provider, metrics in self.session_metrics["providers"].items():
            requests = metrics["requests"]
            avg_latency = metrics["total_latency"] / requests if requests > 0 else 0
            success_rate = metrics["successes"] / requests * 100 if requests > 0 else 0

            provider_stats[provider] = {
                "requests": requests,
                "successes": metrics["successes"],
                "failures": metrics["failures"],
                "avg_latency_seconds": round(avg_latency, 2),
                "success_rate_percent": round(success_rate, 2),
            }

        return {
            "enabled": True,
            "uptime_seconds": round(uptime, 1),
            "uptime_formatted": self._format_duration(uptime),
            "requests": self.session_metrics["requests"],
            "providers": provider_stats,
            "categories": dict(self.session_metrics["categories"]),
            "cost_estimate_usd": round(self.session_metrics["cost_estimate"], 4),
            "recent_errors_count": len(self.session_metrics["errors"]),
            "requests_per_minute": round(total_requests / (uptime / 60), 2) if uptime > 0 else 0,
            "query_logging": self.log_queries,
        }

    def get_historical_metrics(self, days: int = 7) -> dict[str, Any]:
        """
        Get historical metrics from persisted data.

        Args:
            days: Number of days to retrieve

        Returns:
            Dictionary with historical metrics
        """
        historical_data = []
        cutoff_date = datetime.now() - timedelta(days=days)

        try:
            for metrics_file in sorted(self.metrics_dir.glob("metrics_*.json")):
                try:
                    # Parse date from filename
                    date_str = metrics_file.stem.replace("metrics_", "")
                    file_date = datetime.strptime(date_str, "%Y%m%d")

                    if file_date >= cutoff_date:
                        with open(metrics_file, encoding="utf-8") as f:
                            data = json.load(f)
                            historical_data.append(data)

                except Exception as e:
                    logger.warning(f"Error reading metrics file {metrics_file.name}: {e}")

            # Aggregate historical data
            total_requests = sum(d.get("requests", {}).get("total", 0) for d in historical_data)
            total_cost = sum(d.get("cost_estimate_usd", 0) for d in historical_data)

            return {
                "period_days": days,
                "total_requests": total_requests,
                "total_cost_estimate_usd": round(total_cost, 4),
                "daily_data": historical_data,
            }

        except Exception as e:
            logger.error(f"Error retrieving historical metrics: {e}")
            return {
                "period_days": days,
                "total_requests": 0,
                "total_cost_estimate_usd": 0.0,
                "daily_data": [],
            }

    def _persist_metrics(self):
        """Persist current metrics to disk."""
        try:
            date_str = datetime.now().strftime("%Y%m%d")
            metrics_file = self.metrics_dir / f"metrics_{date_str}.json"

            # Load existing metrics for today if available
            if metrics_file.exists():
                with open(metrics_file, encoding="utf-8") as f:
                    existing_metrics = json.load(f)
            else:
                existing_metrics = None

            # Merge with current session metrics
            current_metrics = self.get_session_metrics()

            if existing_metrics:
                # Merge request counts
                for key in ["total", "search_only", "ai_enhanced", "cached"]:
                    existing_metrics["requests"][key] = (
                        existing_metrics["requests"].get(key, 0) + current_metrics["requests"][key]
                    )

                # Merge costs
                existing_metrics["cost_estimate_usd"] = round(
                    existing_metrics.get("cost_estimate_usd", 0)
                    + current_metrics["cost_estimate_usd"],
                    4,
                )

                merged_metrics = existing_metrics
            else:
                merged_metrics = current_metrics

            # Add timestamp
            merged_metrics["last_updated"] = time.time()
            merged_metrics["date"] = date_str

            # Write to file
            with open(metrics_file, "w", encoding="utf-8") as f:
                json.dump(merged_metrics, f, indent=2, ensure_ascii=False)

            logger.debug(f"Persisted metrics to {metrics_file.name}")

        except Exception as e:
            logger.error(f"Error persisting metrics: {e}")

    def get_recent_errors(self, count: int = 10) -> list[dict[str, Any]]:
        """
        Get recent errors.

        Args:
            count: Number of errors to return

        Returns:
            List of recent error records
        """
        errors = self.session_metrics["errors"][-count:]

        # Format timestamps
        for error in errors:
            error["timestamp_formatted"] = datetime.fromtimestamp(error["timestamp"]).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        return errors

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format duration in human-readable form."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"

    def reset_session_metrics(self):
        """Reset session metrics (useful for testing)."""
        self.session_metrics = {
            "start_time": time.time(),
            "requests": {
                "total": 0,
                "search_only": 0,
                "ai_enhanced": 0,
                "cached": 0,
            },
            "providers": defaultdict(
                lambda: {
                    "requests": 0,
                    "successes": 0,
                    "failures": 0,
                    "total_latency": 0.0,
                }
            ),
            "categories": defaultdict(int),
            "errors": [],
            "cost_estimate": 0.0,
        }
        logger.info("Session metrics reset")
