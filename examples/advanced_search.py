"""
Advanced Search Example

Demonstrates advanced features including bang syntax and multi-category searches.
"""

import asyncio
import json

from searxng_mcp.server import get_instance_manager


async def main():
    """Run advanced search examples."""
    manager = get_instance_manager()

    print("=" * 80)
    print("SearXNG MCP Server - Advanced Search Examples")
    print("=" * 80)

    # Example 1: Bang syntax for GitHub
    print("\n1. Bang syntax - GitHub search:")
    print("-" * 80)
    results = await manager.search(query="pytorch !gh")
    data = json.loads(results) if isinstance(results, str) else results
    print("Query: pytorch !gh")
    print(f"Results: {len(data.get('results', []))} found")

    # Example 2: Language modifier
    print("\n2. Language modifier - German search:")
    print("-" * 80)
    results = await manager.search(query="künstliche intelligenz :de")
    data = json.loads(results) if isinstance(results, str) else results
    print("Query: künstliche intelligenz :de")
    print(f"Results: {len(data.get('results', []))} found")

    # Example 3: Multiple categories
    print("\n3. Multiple categories - IT & Science:")
    print("-" * 80)
    results = await manager.search(query="machine learning frameworks", categories="it,science")
    data = json.loads(results) if isinstance(results, str) else results
    print("Query: machine learning frameworks")
    print("Categories: it,science")
    print(f"Results: {len(data.get('results', []))} found")

    # Example 4: Multiple engines
    print("\n4. Multiple engines - GitHub + StackOverflow:")
    print("-" * 80)
    results = await manager.search(
        query="async python best practices", engines="github,stackoverflow"
    )
    data = json.loads(results) if isinstance(results, str) else results
    print("Query: async python best practices")
    print("Engines: github,stackoverflow")
    print(f"Results: {len(data.get('results', []))} found")

    # Example 5: Scientific search with filters
    print("\n5. Scientific papers - Recent arXiv:")
    print("-" * 80)
    results = await manager.search(
        query="transformer architecture", categories="science", engines="arxiv", time_range="month"
    )
    data = json.loads(results) if isinstance(results, str) else results
    print("Query: transformer architecture")
    print("Category: science")
    print("Engine: arxiv")
    print("Time range: month")
    print(f"Results: {len(data.get('results', []))} found")

    # Example 6: Safe search enabled
    print("\n6. Safe search - Family-friendly results:")
    print("-" * 80)
    results = await manager.search(
        query="educational videos", categories="videos", safesearch=2  # Strict
    )
    data = json.loads(results) if isinstance(results, str) else results
    print("Query: educational videos")
    print("Category: videos")
    print("Safe search: 2 (strict)")
    print(f"Results: {len(data.get('results', []))} found")

    # Example 7: Pagination
    print("\n7. Pagination - Page 2 results:")
    print("-" * 80)
    results = await manager.search(query="python tutorials", page=2)
    data = json.loads(results) if isinstance(results, str) else results
    print("Query: python tutorials")
    print("Page: 2")
    print(f"Results: {len(data.get('results', []))} found")

    # Example 8: Regional engine - Baidu (Chinese)
    print("\n8. Regional engine - Baidu:")
    print("-" * 80)
    results = await manager.search(query="百度搜索", engines="baidu", language="zh")
    data = json.loads(results) if isinstance(results, str) else results
    print("Query: 百度搜索 (Baidu Search)")
    print("Engine: baidu")
    print("Language: zh")
    print(f"Results: {len(data.get('results', []))} found")

    print("\n" + "=" * 80)
    print("Advanced examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
