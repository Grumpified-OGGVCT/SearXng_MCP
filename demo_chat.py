#!/usr/bin/env python3
"""
Quick demo script for SearXNG MCP Chat Interface

This script demonstrates the chat functionality with various queries.
"""

import asyncio
import json
from datetime import datetime

import httpx

BASE_URL = "http://localhost:8765"


async def test_chat_api():
    """Test the chat API endpoint."""
    print("=" * 60)
    print("SearXNG MCP Chat Interface Demo")
    print("=" * 60)
    print()

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Simple query
        print("Test 1: Simple search query")
        print("-" * 60)
        
        response = await client.post(
            f"{BASE_URL}/api/chat",
            json={
                "message": "What is Python programming language?",
                "language": "en",
                "category": "general"
            }
        )
        
        result = response.json()
        print(f"Response received: {result.get('response', 'No response')[:200]}...")
        print(f"Search results: {len(result.get('search_results', []))} sources found")
        print(f"Goals tracked: {len(result.get('goals', []))}")
        print()

        # Test 2: Technical query
        print("Test 2: Technical/IT query")
        print("-" * 60)
        
        response = await client.post(
            f"{BASE_URL}/api/chat",
            json={
                "message": "Latest features in FastAPI framework",
                "language": "en",
                "category": "it"
            }
        )
        
        result = response.json()
        print(f"Response received: {result.get('response', 'No response')[:200]}...")
        print(f"Search results: {len(result.get('search_results', []))} sources found")
        print()

        # Test 3: Multi-language
        print("Test 3: Multi-language query (Chinese)")
        print("-" * 60)
        
        response = await client.post(
            f"{BASE_URL}/api/chat",
            json={
                "message": "人工智能",
                "language": "zh",
                "category": "science"
            }
        )
        
        result = response.json()
        print(f"Response received: {result.get('response', 'No response')[:200]}...")
        print(f"Search results: {len(result.get('search_results', []))} sources found")
        print()

        # Test 4: Health check
        print("Test 4: System health check")
        print("-" * 60)
        
        response = await client.get(f"{BASE_URL}/api/health")
        health = response.json()
        
        print(f"Status: {health.get('status')}")
        print(f"Instances checked: {len(health.get('instances', []))}")
        healthy = sum(1 for i in health.get('instances', []) if i.get('status') == 'healthy')
        print(f"Healthy instances: {healthy}/{len(health.get('instances', []))}")
        print()

    print("=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)
    print()
    print("To start the chat interface:")
    print("  python src/searxng_mcp/dashboard.py")
    print()
    print("Then visit:")
    print("  Chat Interface: http://localhost:8765/")
    print("  Monitoring Dashboard: http://localhost:8765/dashboard")
    print("  API Documentation: http://localhost:8765/docs")


if __name__ == "__main__":
    print()
    print("Starting demo...")
    print("Make sure the dashboard is running: python src/searxng_mcp/dashboard.py")
    print()
    
    try:
        asyncio.run(test_chat_api())
    except httpx.ConnectError:
        print("❌ Error: Could not connect to dashboard at http://localhost:8765")
        print()
        print("Please start the dashboard first:")
        print("  python src/searxng_mcp/dashboard.py")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
