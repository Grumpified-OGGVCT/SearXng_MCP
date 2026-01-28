# SearXNG MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) 2.0 server that provides AI agents with powerful search capabilities through [SearXNG](https://docs.searxng.org), a privacy-respecting metasearch engine aggregating results from 245+ search engines.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## Features

- 🌐 **Multi-Instance Resilience**: Automatic fallback across public SearXNG instances with optional local instance support
- 🍪 **Preference Persistence**: Cookie-based session management to maintain user preferences across searches
- 🌍 **Global Reach**: Support for 245+ engines including regional and non-English engines (Baidu, Yandex, Naver, etc.)
- 🎯 **Advanced Search**: Bang syntax (!go, !gh), language modifiers (:en, :zh), and 10 specialized categories
- 🔒 **Privacy-Focused**: No tracking, respects SearXNG's privacy principles and MCP security guidelines
- ⚡ **FastMCP Integration**: Built with FastMCP for automatic schema generation and transport flexibility

## Search Categories & Engines

SearXNG organizes 245+ search engines into 10 categories:

| Category | Description | Example Engines | Bang Examples |
|----------|-------------|-----------------|---------------|
| **general** | General web search | google, bing, duckduckgo, startpage, brave, yandex, baidu (ZH), naver (KO), quark (ZH), sogou (ZH) | `!go`, `!bi`, `!ddg`, `!yd`, `!bd` |
| **images** | Image search | google_images, bing_images, unsplash, pixabay, flickr | `!goi`, `!bii`, `!unsplash` |
| **videos** | Video search | youtube, vimeo, dailymotion, bilibili, niconico | `!yt`, `!vim`, `!bili` |
| **news** | News search | google_news, bing_news, reuters, bbc, tagesschau (DE), 360search (ZH) | `!gn`, `!bn`, `!bbc` |
| **map** | Maps & location | openstreetmap, apple_maps, photon | `!osm`, `!am` |
| **music** | Music search | genius, bandcamp, soundcloud, deezer, radio_browser | `!gen`, `!sc`, `!bc` |
| **it** | IT & software | github, stackoverflow, pypi, docker_hub, huggingface, gitlab | `!gh`, `!so`, `!pypi`, `!hf` |
| **science** | Scientific papers | arxiv, pubmed, crossref, semantic_scholar, google_scholar | `!arx`, `!pub`, `!gs` |
| **files** | File search | apkmirror, fdroid, google_play, zlibrary, annas_archive | `!apk`, `!fdr`, `!zlib` |
| **social_media** | Social platforms | reddit, mastodon, lemmy, 9gag, tootfinder | `!red`, `!mast`, `!lem` |

## Installation

### Prerequisites

- Python 3.10 or higher
- pip or uv package manager

### Install via pip

```bash
# Clone the repository
git clone https://github.com/Grumpified-OGGVCT/SearXng_MCP.git
cd SearXng_MCP

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### Install via uv (recommended)

```bash
# Clone the repository
git clone https://github.com/Grumpified-OGGVCT/SearXng_MCP.git
cd SearXng_MCP

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### Platform-Specific Instructions

#### macOS

```bash
# Using Homebrew
brew install python@3.11
pip3 install -r requirements.txt
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.11 python3-pip
pip3 install -r requirements.txt
```

#### Windows

```powershell
# Download Python from python.org or use winget
winget install Python.Python.3.11

# Install dependencies
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Configure SearXNG instances and behavior via environment variables:

```bash
# Custom SearXNG instances (comma-separated)
export SEARXNG_INSTANCES="https://search.example.com,https://searx.example.org"

# Local SearXNG instance for fallback (optional)
export SEARXNG_LOCAL_INSTANCE="http://localhost:8888"
```

### MCP Client Configuration

Add to your MCP client configuration (e.g., Claude Desktop):

#### Using stdio transport (recommended)

```json
{
  "mcpServers": {
    "searxng": {
      "command": "python",
      "args": ["-m", "searxng_mcp.server"],
      "env": {
        "SEARXNG_INSTANCES": "https://search.sapti.me,https://searx.be"
      }
    }
  }
}
```

#### Using SSE transport

```json
{
  "mcpServers": {
    "searxng": {
      "url": "http://localhost:8000/sse",
      "transport": "sse"
    }
  }
}
```

## Usage

### Running the Server

#### Stdio mode (for MCP clients)

```bash
python -m searxng_mcp.server
```

#### SSE mode (for HTTP clients)

```bash
# Coming soon - FastMCP supports multiple transports
```

### MCP Tools

The server exposes three MCP tools:

#### 1. `search` - Perform searches

```python
# Basic search
search(query="python asyncio")

# Category-specific search
search(query="machine learning", categories="science")

# Engine-specific search
search(query="pytorch tutorials", engines="github,stackoverflow")

# Language-specific search
search(query="人工智能", language="zh")

# Time-filtered search
search(query="AI news", categories="news", time_range="week")

# Using bang syntax
search(query="fastapi docs !gh")  # Search GitHub
search(query="quantum computing :de")  # Search in German
```

**Parameters:**
- `query` (required): Search query with optional bang syntax
- `categories`: Comma-separated categories (general, images, videos, news, map, music, it, science, files, social_media)
- `engines`: Comma-separated engine names
- `language`: Language code (en, zh, de, fr, es, ja, ko, ru, ar, etc.)
- `time_range`: Filter by time (day, week, month, year)
- `safesearch`: Safe search level (0=off, 1=moderate, 2=strict)
- `page`: Results page number (default: 1)

#### 2. `list_categories` - List available categories

```python
list_categories()
# Returns: Dictionary of categories and their popular engines
```

#### 3. `get_instances` - View configured instances

```python
get_instances()
# Returns: List of online instances, local instance, and timeout settings
```

### Search Syntax

SearXNG supports powerful search syntax:

- **Bang modifiers**: `!go` (Google), `!gh` (GitHub), `!yt` (YouTube), `!arx` (arXiv)
- **Language modifiers**: `:en`, `:zh`, `:de`, `:fr`, `:ja`, `:ko`
- **External bangs**: `!!w` (Wikipedia), `!!g` (Google)
- **Special queries**: `random uuid`, `md5 text`, `user-agent`

### Cookie Persistence

Cookies are automatically saved per instance in `~/.searxng_mcp/cookies/`. This preserves:
- Language preferences
- Disabled plugins
- Selected engines
- Theme settings

## Architecture

### Instance Management

The server implements a resilient multi-instance architecture:

1. **Primary Instances**: Tries configured public instances in order (default timeout: 5s)
2. **Local Fallback**: Falls back to local instance if configured (timeout: 15s)
3. **Cookie Persistence**: Maintains separate cookie jars per instance
4. **Automatic Retry**: Seamlessly fails over to next instance on error

### MCP 2.0 Compliance

- **JSON-RPC 2.0**: All communication follows MCP specification
- **Capability Negotiation**: Proper handshake and capability exchange
- **Security**: Respects user consent, data privacy, and tool safety principles
- **Transport Flexibility**: Supports stdio, SSE, and future transports

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Or with uv
uv pip install -r requirements-dev.txt
```

### Code Quality

```bash
# Format code
black src/

# Lint code
ruff check src/

# Type checking
mypy src/
```

### Testing

```bash
# Run tests (when test suite is added)
pytest tests/
```

## Deployment

### Docker (Coming Soon)

```dockerfile
# Dockerfile example
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["python", "-m", "searxng_mcp.server"]
```

### Systemd Service (Linux)

```ini
[Unit]
Description=SearXNG MCP Server
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/SearXng_MCP
Environment="SEARXNG_INSTANCES=https://search.example.com"
ExecStart=/usr/bin/python3 -m searxng_mcp.server
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## Roadmap

- [ ] Dynamic instance discovery from searx.space
- [ ] Local caching layer for frequent queries
- [ ] Rate limiting and quota management
- [ ] MCP resources for preference management
- [ ] Authentication support for API-key–protected instances
- [ ] Health monitoring and metrics
- [ ] Docker container and Kubernetes deployment
- [ ] Comprehensive test suite
- [ ] CLI interface for standalone use

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2025-11-25)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [SearXNG Documentation](https://docs.searxng.org)
- [SearXNG Search API](https://docs.searxng.org/dev/search_api.html)
- [SearXNG Search Syntax](https://docs.searxng.org/user/search-syntax.html)
- [SearXNG Public Instances](https://searx.space)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **SearXNG Team**: For building an amazing privacy-respecting metasearch engine
- **FastMCP Authors**: For the excellent Python MCP framework
- **MCP Community**: For advancing the Model Context Protocol specification
