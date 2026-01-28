# MCP Agent Guide: SearXNG Search Tool

**Version:** 0.2.0  
**Last Updated:** 2026-01-28  
**Status:** Production-Ready

> **Single Source of Truth** for AI agents using the SearXNG MCP Server  
> This document contains everything an AI agent needs to effectively use this tool.

---

## 📋 Table of Contents

1. [Quick Reference](#quick-reference)
2. [What This Tool Does](#what-this-tool-does)
3. [Tool Catalog](#tool-catalog)
4. [Search Capabilities](#search-capabilities)
5. [AI Enhancement](#ai-enhancement)
6. [Usage Patterns](#usage-patterns)
7. [Configuration](#configuration)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Reference

### Primary Tool: `search`

```python
search(
    query: str,              # Required: Your search query
    categories: str = "",    # Optional: Comma-separated categories
    engines: str = "",       # Optional: Specific engines to use
    language: str = "en",    # Optional: Language code
    time_range: str = "",    # Optional: day, week, month, year
    safesearch: int = 0,     # Optional: 0=off, 1=moderate, 2=strict
    ai_enhance: bool = False # Optional: Enable AI-powered enhancement
)
```

### Quick Examples

```python
# Basic search
search(query="Python tutorials")

# Search specific category
search(query="machine learning", categories="science")

# Search with specific engine
search(query="python asyncio", engines="github")

# AI-enhanced search (requires configuration)
search(query="quantum computing", ai_enhance=True)

# Advanced search with filters
search(
    query="climate change research",
    categories="science",
    time_range="year",
    language="en"
)
```

---

## 🎯 What This Tool Does

### Core Functionality

**SearXNG MCP Server** is a privacy-respecting metasearch engine that:

1. **Aggregates results** from 245+ search engines across 10 categories
2. **Respects privacy** - no tracking, no data collection
3. **Provides resilience** - automatic failover across multiple instances
4. **Maintains preferences** - cookie-based session persistence
5. **Supports global reach** - regional and non-English engines (Baidu, Yandex, Naver, etc.)
6. **Enhances with AI** - optional AI-powered summarization and insights

### Why Use This Tool?

- **Comprehensive**: Access hundreds of search engines through one interface
- **Private**: No tracking or personal data collection
- **Reliable**: Automatic failover ensures continuous availability
- **Flexible**: Bang syntax, language modifiers, category filtering
- **Intelligent**: Optional AI enhancement for summarization and insights

---

## 🛠️ Tool Catalog

### 1. `search` - Main Search Tool

**Purpose:** Perform comprehensive web searches across 245+ engines

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | ✅ Yes | - | Search query (supports bang syntax) |
| `categories` | string | ❌ No | "" | Comma-separated categories (see [Search Categories](#search-categories)) |
| `engines` | string | ❌ No | "" | Comma-separated engine names |
| `language` | string | ❌ No | "en" | Language code (en, zh, ja, ko, de, fr, es, etc.) |
| `time_range` | string | ❌ No | "" | Time filter: "day", "week", "month", "year" |
| `safesearch` | integer | ❌ No | 0 | Safe search level: 0=off, 1=moderate, 2=strict |
| `format` | string | ❌ No | "json" | Response format (always use "json") |
| `ai_enhance` | boolean | ❌ No | False | Enable AI-powered enhancement (requires config) |

**Returns:**

```json
{
  "query": "search query",
  "number_of_results": 42,
  "results": [
    {
      "title": "Result title",
      "url": "https://example.com",
      "content": "Result snippet...",
      "engine": "google",
      "category": "general",
      "score": 1.0
    }
  ],
  "enhanced": false,
  "metadata": {
    "instance_used": "https://search.sapti.me",
    "search_time": 0.45,
    "engines_used": ["google", "bing"]
  }
}
```

**With AI Enhancement:**

```json
{
  "query": "search query",
  "number_of_results": 42,
  "results": [...],
  "enhanced": true,
  "ai_summary": "Comprehensive summary...",
  "key_insights": [
    "Important finding 1",
    "Important finding 2",
    "Important finding 3"
  ],
  "recommended_sources": [
    {
      "title": "Source 1",
      "url": "https://...",
      "reason": "Why this is recommended"
    }
  ],
  "model": "mistralai/mistral-large-2512",
  "provider": "openrouter"
}
```

---

## 🔍 Search Capabilities

### Search Categories

SearXNG organizes 245+ engines into 10 categories:

| Category | Description | Example Engines | Use When |
|----------|-------------|-----------------|----------|
| **general** | General web search | google, bing, duckduckgo, brave, yandex, baidu, naver | Looking for general information, websites, articles |
| **images** | Image search | google_images, bing_images, unsplash, pixabay, flickr | Searching for photos, graphics, illustrations |
| **videos** | Video search | youtube, vimeo, dailymotion, bilibili, niconico | Looking for video content, tutorials, entertainment |
| **news** | News search | google_news, bing_news, reuters, bbc, tagesschau | Searching for news articles, current events |
| **map** | Maps & location | openstreetmap, apple_maps, photon | Looking for locations, directions, places |
| **music** | Music search | genius, bandcamp, soundcloud, deezer, radio_browser | Searching for songs, artists, albums, lyrics |
| **it** | IT & software | github, stackoverflow, pypi, docker_hub, huggingface | Looking for code, documentation, packages, libraries |
| **science** | Scientific papers | arxiv, pubmed, crossref, semantic_scholar, google_scholar | Searching for research papers, academic content |
| **files** | File search | apkmirror, fdroid, google_play, zlibrary, annas_archive | Looking for apps, books, files |
| **social_media** | Social platforms | reddit, mastodon, lemmy, 9gag, tootfinder | Searching social media content, discussions |

### Bang Syntax

Use `!` prefix to search specific engines directly:

**General:**
- `!go` - Google
- `!ddg` - DuckDuckGo
- `!bi` - Bing
- `!br` - Brave
- `!sp` - Startpage

**Regional:**
- `!yd` - Yandex (Russian)
- `!bd` - Baidu (Chinese)
- `!naver` - Naver (Korean)
- `!qk` - Quark (Chinese)

**IT & Development:**
- `!gh` - GitHub
- `!so` - StackOverflow
- `!pypi` - Python Package Index
- `!npm` - npm registry
- `!hf` - Hugging Face

**Science:**
- `!arx` - arXiv
- `!pub` - PubMed
- `!gs` - Google Scholar
- `!sem` - Semantic Scholar

**Media:**
- `!yt` - YouTube
- `!sc` - SoundCloud
- `!unsplash` - Unsplash
- `!red` - Reddit

**Example:**
```python
search(query="!gh fastmcp")  # Search GitHub directly
search(query="!arx quantum computing")  # Search arXiv
```

### Language Modifiers

Use `:` prefix to specify language:

```python
search(query=":zh 人工智能")  # Chinese
search(query=":ja 機械学習")  # Japanese
search(query=":ko 인공지능")  # Korean
search(query=":de maschinelles lernen")  # German
search(query=":fr intelligence artificielle")  # French
```

### Time Range Filters

Filter results by publication date:

```python
search(query="AI news", time_range="day")      # Last 24 hours
search(query="Python updates", time_range="week")    # Last 7 days
search(query="Tech trends", time_range="month")   # Last 30 days
search(query="Research papers", time_range="year")    # Last 365 days
```

### Multiple Categories

Search across multiple categories:

```python
search(
    query="machine learning frameworks",
    categories="it,science"  # Search both IT and Science categories
)
```

### Specific Engines

Target specific engines:

```python
search(
    query="python async",
    engines="github,stackoverflow"  # Only use these engines
)
```

---

## 🤖 AI Enhancement

### Overview

AI Enhancement uses large language models to:
1. **Summarize** search results into digestible insights
2. **Extract** key findings and important points
3. **Recommend** the most relevant sources with explanations

### Supported Providers

#### 1. OpenRouter

**Model:** Mistral Large 2512 (mistralai/mistral-large-2512)

**Setup:**
```bash
export SEARXNG_AI_PROVIDER=openrouter
export SEARXNG_AI_API_KEY=your_openrouter_key
```

**Get API Key:** https://openrouter.ai/keys

#### 2. Ollama Cloud

**Model:** Mistral Large 3 (mistral-large-3:675b-cloud)

**Setup:**
```bash
export SEARXNG_AI_PROVIDER=ollama
export SEARXNG_AI_API_KEY=your_ollama_cloud_key
```

**Get API Key:** https://ollama.com/settings/keys

**Note:** This is Ollama **CLOUD** service, not local Ollama

#### 3. Google Gemini

**Model:** Auto-detected latest Flash (e.g., gemini-2.0-flash-exp)

**Setup:**
```bash
export SEARXNG_AI_PROVIDER=gemini
export SEARXNG_AI_API_KEY=your_gemini_api_key
```

**Get API Key:** https://aistudio.google.com/app/apikey

**Features:**
- Auto-detects latest Gemini Flash model
- Checks Google's model API for newest version
- Falls back to known stable version if detection fails

### Usage

Enable AI enhancement with `ai_enhance=True`:

```python
# Basic AI-enhanced search
result = search(query="quantum computing", ai_enhance=True)

# Access AI-generated content
print(result["ai_summary"])           # Comprehensive summary
print(result["key_insights"])         # List of key points
print(result["recommended_sources"])  # Top sources with reasons

# Check which model was used
print(result["model"])      # e.g., "mistralai/mistral-large-2512"
print(result["provider"])   # e.g., "openrouter"
```

### When to Use AI Enhancement

**✅ Good Use Cases:**
- Research questions needing synthesis
- Complex topics requiring summarization
- When you need curated source recommendations
- Information gathering for decision-making

**❌ Avoid When:**
- Simple factual lookups (adds latency)
- When raw search results are sufficient
- Budget-conscious scenarios (AI calls cost money)
- Real-time/time-sensitive searches

---

## 💡 Usage Patterns

### Pattern 1: Simple Information Lookup

```python
# Quick fact-finding
result = search(query="Python 3.12 release date")

# Extract answer from top result
if result["results"]:
    print(result["results"][0]["content"])
```

### Pattern 2: Academic Research

```python
# Search scientific literature
result = search(
    query="machine learning interpretability",
    categories="science",
    time_range="year"
)

# Focus on arxiv
arxiv_results = [r for r in result["results"] if "arxiv" in r["engine"]]
```

### Pattern 3: Code Discovery

```python
# Find code examples
result = search(
    query="!gh FastMCP examples",
    categories="it"
)

# Or search multiple sources
result = search(
    query="async python best practices",
    engines="github,stackoverflow"
)
```

### Pattern 4: Multi-Language Search

```python
# Search in Chinese
result = search(
    query=":zh 深度学习框架",
    categories="it,science"
)

# Search Japanese technical docs
result = search(
    query=":ja Pythonフレームワーク",
    categories="it"
)
```

### Pattern 5: News Monitoring

```python
# Latest news on topic
result = search(
    query="artificial intelligence regulation",
    categories="news",
    time_range="week"
)

# Filter by source
reuters = [r for r in result["results"] if "reuters" in r["url"]]
```

### Pattern 6: Research with AI Summary

```python
# Get comprehensive overview
result = search(
    query="climate change mitigation strategies",
    categories="science,news",
    ai_enhance=True
)

# Present findings
print("Summary:", result["ai_summary"])
print("\nKey Insights:")
for insight in result["key_insights"]:
    print(f"  • {insight}")

print("\nRecommended Reading:")
for source in result["recommended_sources"]:
    print(f"  • {source['title']}: {source['reason']}")
```

### Pattern 7: Comparative Search

```python
# Compare multiple queries
topics = ["pytorch", "tensorflow", "jax"]
results = {}

for topic in topics:
    results[topic] = search(
        query=f"{topic} advantages",
        categories="it,science",
        ai_enhance=True
    )

# Compare summaries
for topic, result in results.items():
    print(f"\n{topic.upper()}:")
    print(result["ai_summary"])
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# Core Configuration
SEARXNG_INSTANCES=https://search.sapti.me,https://searx.be
SEARXNG_LOCAL_INSTANCE=http://localhost:8888  # Optional
SEARXNG_TIMEOUT=5.0
SEARXNG_LOCAL_TIMEOUT=15.0

# AI Enhancement (Optional)
SEARXNG_AI_PROVIDER=openrouter  # or ollama, gemini
SEARXNG_AI_API_KEY=your_api_key
SEARXNG_AI_MODEL=  # Auto-detected if not set

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Configuration File

Create `.env` file in project root:

```bash
# Copy example configuration
cp .env.example .env

# Edit with your settings
nano .env
```

### Interactive Setup

Run the setup wizard for guided configuration:

```bash
python wizard.py
```

The wizard will help you:
1. Detect your OS
2. Choose instance strategy (online-only, local, hybrid)
3. Configure AI enhancement
4. Set up local SearXNG if desired
5. Generate `.env` file

---

## ⚠️ Error Handling

### Common Errors

#### 1. No Results Returned

```json
{
  "error": "No results found",
  "query": "very specific obscure query",
  "instances_tried": 3
}
```

**Solution:** Broaden search query or try different category

#### 2. All Instances Failed

```json
{
  "error": "All SearXNG instances failed",
  "instances_tried": 5,
  "last_error": "Connection timeout"
}
```

**Solution:** 
- Check internet connection
- Verify instance URLs in configuration
- Consider setting up local instance

#### 3. AI Enhancement Failed

```json
{
  "enhanced": false,
  "reason": "AI enhancement failed: Invalid API key",
  "original_results": [...]
}
```

**Solution:**
- Verify API key is correct
- Check API key permissions
- Ensure sufficient API credits

#### 4. Invalid Category

```json
{
  "error": "Invalid category: 'invalid'",
  "valid_categories": ["general", "images", "videos", ...]
}
```

**Solution:** Use valid category names from list

### Error Recovery

The tool implements automatic failover:

1. **Instance Failover:** Automatically tries next instance if one fails
2. **Graceful Degradation:** Returns partial results if some engines fail
3. **AI Fallback:** Returns raw results if AI enhancement fails

### Checking Health

Use the health check tool to verify configuration:

```bash
# Check all instances
python -m searxng_mcp.health

# Verbose output
python -m searxng_mcp.health --verbose
```

---

## ✅ Best Practices

### 1. Query Formulation

**✅ Good:**
```python
search(query="Python async programming best practices")
search(query="!gh fastmcp examples")
search(query="climate change recent research", time_range="year")
```

**❌ Avoid:**
```python
search(query="help")  # Too vague
search(query="a")  # Too short
search(query="the python")  # Unnecessary words
```

### 2. Category Selection

**✅ Choose appropriate category:**
```python
# Academic research
search(query="quantum computing", categories="science")

# Code search
search(query="async patterns", categories="it")

# News
search(query="AI regulation", categories="news")
```

**❌ Don't mix incompatible categories:**
```python
# These rarely makes sense together
search(query="puppies", categories="science,music")
```

### 3. Language Specification

**✅ Specify language for non-English:**
```python
search(query=":zh 人工智能", language="zh")
search(query=":ja 機械学習", language="ja")
```

**✅ Or use language parameter:**
```python
search(query="深度学习", language="zh")
```

### 4. AI Enhancement Usage

**✅ Use for complex research:**
```python
search(
    query="implications of quantum supremacy",
    categories="science",
    ai_enhance=True  # Worth the cost for synthesis
)
```

**❌ Don't waste on simple lookups:**
```python
search(
    query="Python version",
    ai_enhance=True  # Overkill, wastes API credits
)
```

### 5. Result Processing

**✅ Handle empty results:**
```python
result = search(query="obscure topic")

if result.get("number_of_results", 0) == 0:
    # Try broader query or different category
    result = search(query="broader topic", categories="general")
```

**✅ Check for errors:**
```python
result = search(query="test")

if "error" in result:
    print(f"Search failed: {result['error']}")
    # Handle error appropriately
```

### 6. Performance Optimization

**✅ Cache results when appropriate:**
```python
# For repeated queries, cache results in your application
cache = {}

def cached_search(query, **kwargs):
    key = f"{query}:{kwargs}"
    if key not in cache:
        cache[key] = search(query=query, **kwargs)
    return cache[key]
```

**✅ Use specific engines for targeted searches:**
```python
# Faster than searching all engines
search(query="python package", engines="pypi")
```

---

## 🔧 Troubleshooting

### Issue: Slow Search Response

**Symptoms:** Searches taking >10 seconds

**Diagnosis:**
```bash
python -m searxng_mcp.health  # Check instance response times
```

**Solutions:**
1. Use instances with better response times
2. Set up local instance for faster searches
3. Use specific engines instead of all
4. Reduce timeout value if acceptable

### Issue: Missing Results from Specific Engine

**Symptoms:** Expected engine not returning results

**Cause:** Engine might be disabled on that instance

**Solution:** Try different instance or use bang syntax:
```python
search(query="!gh repository")  # Forces GitHub search
```

### Issue: AI Enhancement Not Working

**Symptoms:** `enhanced: false` in results

**Diagnosis:**
```python
# Check configuration
import os
print(os.environ.get("SEARXNG_AI_PROVIDER"))
print(os.environ.get("SEARXNG_AI_API_KEY"))
```

**Solutions:**
1. Verify API key is set and valid
2. Check API credits/quota
3. Test API key directly with provider
4. Review logs for specific error

### Issue: Language Results Not as Expected

**Symptoms:** Getting English results for non-English query

**Solution:** Use both language modifier and parameter:
```python
search(
    query=":zh 人工智能",
    language="zh",
    engines="baidu,sogou"  # Chinese search engines
)
```

### Issue: Cookie/Preference Not Persisting

**Symptoms:** Preferences reset between searches

**Solution:** Check cookie directory permissions:
```bash
ls -la ~/.searxng_mcp/cookies/
# Ensure directory is writable
```

---

## 📊 Monitoring & Observability

### Web Dashboard

Access real-time monitoring dashboard:

```bash
python -m searxng_mcp.dashboard
```

Then open: http://localhost:8765

**Features:**
- Real-time instance health monitoring
- Response time tracking
- Built-in search testing
- Configuration viewer
- WebSocket-based live updates

### Health Check API

Programmatic health checking:

```bash
# Check all instances
python -m searxng_mcp.health

# With verbose output
python -m searxng_mcp.health --verbose
```

**Exit Codes:**
- `0` - All instances healthy
- `1` - Some instances failing
- `2` - All instances failing

---

## 📚 Additional Resources

### Documentation

- **Installation Guide:** [INSTALL.md](INSTALL.md)
- **Quick Start:** [QUICKSTART.md](QUICKSTART.md)
- **Dashboard Guide:** [DASHBOARD.md](DASHBOARD.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Security:** [SECURITY.md](SECURITY.md)

### External Links

- **MCP Specification:** https://modelcontextprotocol.io/specification/2025-11-25
- **SearXNG Documentation:** https://docs.searxng.org
- **SearXNG Instances:** https://searx.space
- **FastMCP:** https://github.com/jlowin/fastmcp

### Support

- **Issues:** https://github.com/Grumpified-OGGVCT/SearXng_MCP/issues
- **Discussions:** https://github.com/Grumpified-OGGVCT/SearXng_MCP/discussions

---

## 📄 Version History

**v0.2.0** (Current)
- Added AI enhancement with 3 providers
- Added web dashboard
- Added interactive setup wizard
- Added health check tool
- Auto-detection of latest Gemini Flash model

**v0.1.0** (Initial Release)
- Core MCP server functionality
- Multi-instance support with failover
- Cookie-based preference persistence
- 245+ search engines across 10 categories

---

## 🎯 Summary

This tool provides AI agents with:

1. **Comprehensive Search:** Access to 245+ engines via single interface
2. **Privacy:** No tracking, respects user privacy
3. **Resilience:** Automatic failover across instances
4. **Flexibility:** Bang syntax, categories, filters, languages
5. **Intelligence:** Optional AI-powered enhancement
6. **Observability:** Dashboard and health monitoring

**Use this tool when agents need to:**
- Search the web for current information
- Access specialized search engines (academic, code, media)
- Find region-specific or non-English content
- Get AI-powered summaries of research topics

**Key Principle:** This tool brings the power of 245 search engines to AI agents while maintaining privacy and reliability.

---

*Last updated: 2026-01-28*  
*Document version: 1.0.0*
