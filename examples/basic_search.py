"""
Basic Search Example

Demonstrates basic usage of the SearXNG MCP server.
"""

import asyncio
import json
from searxng_mcp.server import get_instance_manager


async def main():
    """Run basic search examples."""
    manager = get_instance_manager()

    print("=" * 80)
    print("SearXNG MCP Server - Basic Search Examples")
    print("=" * 80)

    # Example 1: Basic web search
    print("\n1. Basic web search:")
    print("-" * 80)
    results = await manager.search(query="python asyncio")
    data = json.loads(results) if isinstance(results, str) else results
    print(f"Query: python asyncio")
    print(f"Results: {len(data.get('results', []))} found")
    print(f"Instance: {data.get('_instance', 'N/A')}")
    if data.get('results'):
        first = data['results'][0]
        print(f"Top result: {first.get('title', 'N/A')}")
        print(f"URL: {first.get('url', 'N/A')}")

    # Example 2: Category-specific search
    print("\n2. Image search:")
    print("-" * 80)
    results = await manager.search(query="sunset landscape", categories="images")
    data = json.loads(results) if isinstance(results, str) else results
    print(f"Query: sunset landscape")
    print(f"Category: images")
    print(f"Results: {len(data.get('results', []))} found")

    # Example 3: Engine-specific search
    print("\n3. GitHub search:")
    print("-" * 80)
    results = await manager.search(query="fastmcp", engines="github")
    data = json.loads(results) if isinstance(results, str) else results
    print(f"Query: fastmcp")
    print(f"Engine: github")
    print(f"Results: {len(data.get('results', []))} found")

    # Example 4: Language-specific search
    print("\n4. Chinese language search:")
    print("-" * 80)
    results = await manager.search(query="人工智能", language="zh")
    data = json.loads(results) if isinstance(results, str) else results
    print(f"Query: 人工智能 (Artificial Intelligence)")
    print(f"Language: zh (Chinese)")
    print(f"Results: {len(data.get('results', []))} found")

    # Example 5: Time-filtered search
    print("\n5. Recent news search:")
    print("-" * 80)
    results = await manager.search(
        query="AI breakthroughs",
        categories="news",
        time_range="week"
    )
    data = json.loads(results) if isinstance(results, str) else results
    print(f"Query: AI breakthroughs")
    print(f"Category: news")
    print(f"Time range: week")
    print(f"Results: {len(data.get('results', []))} found")

    print("\n" + "=" * 80)
    print("Examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
