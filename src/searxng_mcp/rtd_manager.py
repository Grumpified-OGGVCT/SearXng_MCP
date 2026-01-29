"""
Real-Time Data (RTD) Manager

Calculates data freshness, determines refresh needs, and manages
auto-refresh intervals for time-sensitive queries.
"""

import logging
import re
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class RealTimeDataManager:
    """
    Manages real-time data freshness and refresh logic.

    Features:
    - Calculates data freshness (0-100% score)
    - Determines if queries need refresh
    - Manages auto-refresh intervals
    - Provides freshness badges/indicators
    """

    # Time-sensitive keywords
    TIME_SENSITIVE_KEYWORDS = [
        "now",
        "current",
        "today",
        "latest",
        "recent",
        "breaking",
        "live",
        "real-time",
        "update",
        "news",
        "price",
        "stock",
        "weather",
        "traffic",
        "score",
        "trending",
        "status",
        "happening",
        "ongoing",
        "active",
        "emergency",
    ]

    # High-freshness categories
    HIGH_FRESHNESS_CATEGORIES = ["news", "social", "finance", "sports", "weather"]

    # Freshness thresholds (in seconds)
    FRESHNESS_THRESHOLDS = {
        "live": 60,  # < 1 min = LIVE
        "fresh": 3600,  # < 1 hour = FRESH
        "recent": 86400,  # < 1 day = RECENT
        "stale": 604800,  # < 1 week = STALE
        # > 1 week = OLD
    }

    # Refresh intervals (in seconds) by query type
    REFRESH_INTERVALS = {
        "live": 30,  # 30 seconds for live data
        "dynamic": 300,  # 5 minutes for dynamic content
        "regular": 900,  # 15 minutes for regular queries
        "static": 3600,  # 1 hour for static content
    }

    def __init__(self):
        """Initialize the RTD manager."""
        self.query_cache: dict[str, dict[str, Any]] = {}
        self.refresh_timers: dict[str, datetime] = {}

    def calculate_freshness(
        self, result: dict[str, Any], query_time: datetime | None = None
    ) -> dict[str, Any]:
        """
        Calculate data freshness score.

        Args:
            result: Search result with timestamp or publishedDate
            query_time: Time of query (default: now)

        Returns:
            Dict with freshness score, badge, age, and status
        """
        if query_time is None:
            query_time = datetime.utcnow()

        # Extract timestamp from result
        timestamp = self._extract_timestamp(result)

        if not timestamp:
            return {
                "score": 50,  # Unknown = medium freshness
                "badge": "🔵 UNKNOWN",
                "age_seconds": None,
                "age_display": "Unknown age",
                "status": "unknown",
            }

        # Calculate age
        age_seconds = (query_time - timestamp).total_seconds()

        # Calculate freshness score (0-100)
        score = self._calculate_score(age_seconds)

        # Determine badge and status
        badge, status = self._get_badge_and_status(age_seconds)

        # Format age display
        age_display = self._format_age(age_seconds)

        return {
            "score": score,
            "badge": badge,
            "age_seconds": age_seconds,
            "age_display": age_display,
            "status": status,
            "timestamp": timestamp.isoformat(),
        }

    def should_refresh(
        self, query: str, last_search_time: datetime | None = None, category: str | None = None
    ) -> tuple[bool, str]:
        """
        Determine if a query needs refresh.

        Args:
            query: Search query
            last_search_time: When query was last searched
            category: Query category

        Returns:
            Tuple of (should_refresh: bool, reason: str)
        """
        # No previous search = always refresh
        if not last_search_time:
            return True, "First search"

        # Check time-sensitivity
        is_time_sensitive = self.is_time_sensitive(query, category)
        query_type = self._classify_query_type(query, category)

        # Calculate time since last search
        time_since_search = (datetime.utcnow() - last_search_time).total_seconds()

        # Get refresh interval for this query type
        refresh_interval = self.REFRESH_INTERVALS.get(query_type, self.REFRESH_INTERVALS["regular"])

        # Adjust interval for time-sensitive queries
        if is_time_sensitive:
            refresh_interval = min(refresh_interval, self.REFRESH_INTERVALS["dynamic"])

        if time_since_search >= refresh_interval:
            return True, f"Data older than {self._format_seconds(refresh_interval)}"

        return False, f"Still fresh (refreshes every {self._format_seconds(refresh_interval)})"

    def get_freshness_badge(
        self, timestamp: datetime | None = None, age_seconds: float | None = None
    ) -> str:
        """
        Get visual freshness badge/indicator.

        Args:
            timestamp: Data timestamp
            age_seconds: Data age in seconds (alternative to timestamp)

        Returns:
            Emoji badge string
        """
        if age_seconds is None and timestamp:
            age_seconds = (datetime.utcnow() - timestamp).total_seconds()

        if age_seconds is None:
            return "🔵 UNKNOWN"

        badge, _ = self._get_badge_and_status(age_seconds)
        return badge

    def is_time_sensitive(self, query: str, category: str | None = None) -> bool:
        """
        Detect if a query is time-sensitive.

        Args:
            query: Search query
            category: Optional category

        Returns:
            True if time-sensitive
        """
        query_lower = query.lower()

        # Check keywords
        for keyword in self.TIME_SENSITIVE_KEYWORDS:
            if re.search(r"\b" + keyword + r"\b", query_lower):
                return True

        # Check category
        if category and category.lower() in self.HIGH_FRESHNESS_CATEGORIES:
            return True

        # Check for dates (today, this week, etc.)
        date_patterns = [
            r"\btoday\b",
            r"\bthis\s+(?:week|month|year)\b",
            r"\b(?:this|last)\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
            r"\b\d{4}\b",  # Year
        ]

        for pattern in date_patterns:
            if re.search(pattern, query_lower):
                return True

        return False

    def get_refresh_interval(self, query: str, category: str | None = None) -> int:
        """
        Get optimal refresh interval for a query.

        Args:
            query: Search query
            category: Optional category

        Returns:
            Refresh interval in seconds
        """
        query_type = self._classify_query_type(query, category)
        return self.REFRESH_INTERVALS.get(query_type, self.REFRESH_INTERVALS["regular"])

    def get_rtd_status(
        self, query: str, results: list[dict[str, Any]], category: str | None = None
    ) -> dict[str, Any]:
        """
        Get comprehensive RTD status for query results.

        Args:
            query: Search query
            results: Search results
            category: Optional category

        Returns:
            RTD status with freshness info, refresh needs, etc.
        """
        is_time_sensitive = self.is_time_sensitive(query, category)
        refresh_interval = self.get_refresh_interval(query, category)

        # Calculate freshness for all results
        freshness_scores = []
        for result in results:
            freshness = self.calculate_freshness(result)
            freshness_scores.append(freshness)

        # Calculate average freshness
        avg_score = 0
        if freshness_scores:
            valid_scores = [f["score"] for f in freshness_scores if f["score"] is not None]
            if valid_scores:
                avg_score = sum(valid_scores) / len(valid_scores)

        # Determine overall status
        if avg_score >= 80:
            overall_status = "excellent"
        elif avg_score >= 60:
            overall_status = "good"
        elif avg_score >= 40:
            overall_status = "fair"
        else:
            overall_status = "stale"

        return {
            "is_time_sensitive": is_time_sensitive,
            "refresh_interval": refresh_interval,
            "refresh_interval_display": self._format_seconds(refresh_interval),
            "average_freshness": round(avg_score, 1),
            "overall_status": overall_status,
            "result_freshness": freshness_scores,
            "auto_refresh_enabled": is_time_sensitive,
            "next_refresh_in": refresh_interval if is_time_sensitive else None,
        }

    def _extract_timestamp(self, result: dict[str, Any]) -> datetime | None:
        """Extract timestamp from search result."""
        # Try various timestamp fields
        timestamp_fields = ["publishedDate", "timestamp", "created", "date", "updated"]

        for field in timestamp_fields:
            if field in result:
                value = result[field]
                try:
                    # Try parsing ISO format
                    if isinstance(value, str):
                        # Handle various formats
                        for fmt in [
                            "%Y-%m-%dT%H:%M:%S.%fZ",
                            "%Y-%m-%dT%H:%M:%SZ",
                            "%Y-%m-%dT%H:%M:%S",
                            "%Y-%m-%d %H:%M:%S",
                            "%Y-%m-%d",
                        ]:
                            try:
                                return datetime.strptime(value, fmt)
                            except ValueError:
                                continue

                        # Try ISO parse as fallback
                        try:
                            return datetime.fromisoformat(value.replace("Z", "+00:00"))
                        except (ValueError, AttributeError):
                            pass

                    elif isinstance(value, (int, float)):
                        # Unix timestamp
                        return datetime.fromtimestamp(value)

                    elif isinstance(value, datetime):
                        return value

                except Exception as e:
                    logger.debug(f"Failed to parse timestamp {value}: {e}")
                    continue

        return None

    def _calculate_score(self, age_seconds: float) -> int:
        """Calculate freshness score (0-100) based on age."""
        if age_seconds < 0:
            return 100  # Future timestamp?

        # Logarithmic decay for freshness score
        if age_seconds < self.FRESHNESS_THRESHOLDS["live"]:
            return 100
        elif age_seconds < self.FRESHNESS_THRESHOLDS["fresh"]:
            # 95-80 score for < 1 hour
            ratio = age_seconds / self.FRESHNESS_THRESHOLDS["fresh"]
            return int(95 - (ratio * 15))
        elif age_seconds < self.FRESHNESS_THRESHOLDS["recent"]:
            # 80-60 score for 1 hour - 1 day
            ratio = (age_seconds - self.FRESHNESS_THRESHOLDS["fresh"]) / (
                self.FRESHNESS_THRESHOLDS["recent"] - self.FRESHNESS_THRESHOLDS["fresh"]
            )
            return int(80 - (ratio * 20))
        elif age_seconds < self.FRESHNESS_THRESHOLDS["stale"]:
            # 60-30 score for 1 day - 1 week
            ratio = (age_seconds - self.FRESHNESS_THRESHOLDS["recent"]) / (
                self.FRESHNESS_THRESHOLDS["stale"] - self.FRESHNESS_THRESHOLDS["recent"]
            )
            return int(60 - (ratio * 30))
        else:
            # 30-0 score for > 1 week
            weeks_old = age_seconds / 604800
            score = int(30 - (weeks_old * 5))
            return max(0, score)

    def _get_badge_and_status(self, age_seconds: float) -> tuple[str, str]:
        """Get badge emoji and status string."""
        if age_seconds < self.FRESHNESS_THRESHOLDS["live"]:
            return "🔴 LIVE", "live"
        elif age_seconds < self.FRESHNESS_THRESHOLDS["fresh"]:
            return "🟢 FRESH", "fresh"
        elif age_seconds < self.FRESHNESS_THRESHOLDS["recent"]:
            return "🟡 RECENT", "recent"
        elif age_seconds < self.FRESHNESS_THRESHOLDS["stale"]:
            return "🟠 STALE", "stale"
        else:
            return "⚪ OLD", "old"

    def _format_age(self, age_seconds: float) -> str:
        """Format age in human-readable form."""
        if age_seconds < 60:
            return f"{int(age_seconds)}s ago"
        elif age_seconds < 3600:
            minutes = int(age_seconds / 60)
            return f"{minutes}m ago"
        elif age_seconds < 86400:
            hours = int(age_seconds / 3600)
            return f"{hours}h ago"
        elif age_seconds < 604800:
            days = int(age_seconds / 86400)
            return f"{days}d ago"
        elif age_seconds < 2592000:  # 30 days
            weeks = int(age_seconds / 604800)
            return f"{weeks}w ago"
        else:
            months = int(age_seconds / 2592000)
            return f"{months}mo ago"

    def _format_seconds(self, seconds: int) -> str:
        """Format seconds in human-readable form."""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m"
        elif seconds < 86400:
            return f"{seconds // 3600}h"
        else:
            return f"{seconds // 86400}d"

    def _classify_query_type(self, query: str, category: str | None = None) -> str:
        """
        Classify query type for refresh interval.

        Returns: 'live', 'dynamic', 'regular', or 'static'
        """
        query_lower = query.lower()

        # Live data keywords
        live_keywords = ["live", "real-time", "now", "current", "streaming", "score"]
        for keyword in live_keywords:
            if keyword in query_lower:
                return "live"

        # Dynamic content keywords
        dynamic_keywords = [
            "news",
            "breaking",
            "latest",
            "update",
            "trending",
            "price",
            "stock",
            "weather",
            "traffic",
        ]
        for keyword in dynamic_keywords:
            if keyword in query_lower:
                return "dynamic"

        # Check category
        if category:
            cat_lower = category.lower()
            if cat_lower in ["news", "social"]:
                return "dynamic"
            elif cat_lower in ["finance", "weather", "sports"]:
                return "live"

        # Historical/research queries = static
        static_keywords = [
            "history",
            "definition",
            "biography",
            "meaning",
            "what is",
            "who is",
            "who was",
            "when was",
        ]
        for keyword in static_keywords:
            if keyword in query_lower:
                return "static"

        return "regular"
