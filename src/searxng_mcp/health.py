#!/usr/bin/env python3
"""
Health Check Tool for SearXNG MCP Server

Tests configured instances and displays health status, response times, and diagnostics.
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run: pip install httpx")
    sys.exit(1)


class Colors:
    """ANSI color codes."""

    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    @staticmethod
    def is_supported() -> bool:
        """Check if terminal supports colors."""
        return (
            hasattr(sys.stdout, "isatty")
            and sys.stdout.isatty()
            and os.getenv("TERM") != "dumb"
        )


class HealthChecker:
    """Health check tool for SearXNG instances."""

    def __init__(self):
        self.colors_enabled = Colors.is_supported()
        self.load_config()

    def color(self, text: str, color: str) -> str:
        """Apply color to text if supported."""
        if self.colors_enabled:
            return f"{color}{text}{Colors.RESET}"
        return text

    def load_config(self):
        """Load configuration from environment or .env file."""
        # Try to load from .env file
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ.setdefault(key.strip(), value.strip())

        # Load instances
        instances_str = os.environ.get("SEARXNG_INSTANCES", "")
        if instances_str:
            self.instances = [i.strip() for i in instances_str.split(",")]
        else:
            # Default instances
            self.instances = [
                "https://search.sapti.me",
                "https://searx.be",
                "https://search.bus-hit.me",
                "https://search.mdosch.de",
                "https://searx.tiekoetter.com",
            ]

        # Load local instance
        self.local_instance = os.environ.get("SEARXNG_LOCAL_INSTANCE")

        # Load timeouts
        try:
            self.timeout = float(os.environ.get("SEARXNG_TIMEOUT", "5.0"))
        except ValueError:
            self.timeout = 5.0

        try:
            self.local_timeout = float(
                os.environ.get("SEARXNG_LOCAL_TIMEOUT", "15.0")
            )
        except ValueError:
            self.local_timeout = 15.0

    async def check_instance(
        self, instance: str, timeout: float
    ) -> Dict[str, any]:
        """Check health of a single instance."""
        result = {
            "instance": instance,
            "status": "unknown",
            "response_time": None,
            "error": None,
            "version": None,
        }

        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                # Try to get search results
                response = await client.get(
                    f"{instance}/search",
                    params={"q": "test", "format": "json"},
                )

                response_time = time.time() - start_time
                result["response_time"] = response_time

                if response.status_code == 200:
                    result["status"] = "healthy"

                    # Try to parse response
                    try:
                        data = response.json()
                        result["version"] = data.get("version")
                    except Exception:
                        pass
                else:
                    result["status"] = "unhealthy"
                    result["error"] = f"HTTP {response.status_code}"

        except httpx.TimeoutException:
            result["status"] = "timeout"
            result["error"] = f"Timeout after {timeout}s"
        except httpx.ConnectError as e:
            result["status"] = "unreachable"
            result["error"] = f"Connection failed: {str(e)[:50]}"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)[:100]

        return result

    async def check_all_instances(self) -> List[Dict]:
        """Check health of all configured instances."""
        tasks = []

        # Check online instances
        for instance in self.instances:
            tasks.append(self.check_instance(instance, self.timeout))

        # Check local instance
        if self.local_instance:
            tasks.append(self.check_instance(self.local_instance, self.local_timeout))

        results = await asyncio.gather(*tasks)
        return list(results)

    def print_header(self):
        """Print health check header."""
        print()
        print(self.color("=" * 80, Colors.CYAN))
        print(
            self.color("  SearXNG MCP Server - Health Check", Colors.BOLD + Colors.CYAN)
        )
        print(self.color("=" * 80, Colors.CYAN))
        print()

    def print_summary(self, results: List[Dict]):
        """Print summary of health check results."""
        healthy = sum(1 for r in results if r["status"] == "healthy")
        total = len(results)

        print()
        print(self.color("Summary:", Colors.BOLD))
        print(f"  Total instances: {total}")
        print(
            f"  Healthy: {self.color(str(healthy), Colors.GREEN if healthy > 0 else Colors.RED)}/{total}"
        )

        if healthy == 0:
            print()
            print(
                self.color(
                    "⚠ WARNING: No healthy instances found!", Colors.YELLOW + Colors.BOLD
                )
            )
            print("  - Check your network connection")
            print("  - Verify instance URLs in .env file")
            print("  - Try different instances from https://searx.space")

        elif healthy < total:
            print()
            print(
                self.color("⚠ Some instances are unavailable", Colors.YELLOW)
            )
            print("  This is normal - public instances can be temporarily down")
            print("  The server will automatically use healthy instances")

    def print_result(self, result: Dict):
        """Print result for a single instance."""
        instance = result["instance"]
        status = result["status"]
        response_time = result.get("response_time")
        error = result.get("error")

        # Determine status symbol and color
        if status == "healthy":
            symbol = "✓"
            color = Colors.GREEN
        elif status == "timeout":
            symbol = "⏱"
            color = Colors.YELLOW
        elif status in ["unreachable", "error"]:
            symbol = "✗"
            color = Colors.RED
        else:
            symbol = "?"
            color = Colors.YELLOW

        # Print instance URL
        print(f"\n{self.color(symbol, color)} {self.color(instance, Colors.BOLD)}")

        # Print status
        status_text = status.upper()
        print(f"  Status: {self.color(status_text, color)}")

        # Print response time
        if response_time is not None:
            time_color = Colors.GREEN if response_time < 2.0 else Colors.YELLOW
            print(f"  Response time: {self.color(f'{response_time:.2f}s', time_color)}")

        # Print error
        if error:
            print(f"  Error: {self.color(error, Colors.RED)}")

        # Print version if available
        if result.get("version"):
            print(f"  Version: {result['version']}")

    def print_configuration(self):
        """Print current configuration."""
        print(self.color("\nConfiguration:", Colors.BOLD))
        print(f"  Online instances: {len(self.instances)}")
        for i, instance in enumerate(self.instances, 1):
            print(f"    {i}. {instance}")

        if self.local_instance:
            print(f"  Local instance: {self.local_instance}")
        else:
            print("  Local instance: Not configured")

        print(f"  Timeout (online): {self.timeout}s")
        print(f"  Timeout (local): {self.local_timeout}s")

    async def run(self, verbose: bool = False):
        """Run health check."""
        self.print_header()

        if verbose:
            self.print_configuration()

        print(self.color("\nChecking instances...", Colors.CYAN))

        results = await self.check_all_instances()

        # Print individual results
        for result in results:
            self.print_result(result)

        # Print summary
        self.print_summary(results)

        print()

        # Return exit code based on health
        healthy = sum(1 for r in results if r["status"] == "healthy")
        return 0 if healthy > 0 else 1


def main():
    """Main entry point."""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    try:
        checker = HealthChecker()
        exit_code = asyncio.run(checker.run(verbose=verbose))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nHealth check cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
