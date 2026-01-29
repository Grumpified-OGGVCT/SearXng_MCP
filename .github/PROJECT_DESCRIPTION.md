# Project Description

**SearXNG MCP Server** - Privacy-respecting AI search through Model Context Protocol

## Tagline

Empower AI agents with privacy-respecting, multi-source search capabilities through SearXNG metasearch engine and MCP 2.0.

## Short Description (160 chars for GitHub)

MCP 2.0 server for SearXNG metasearch: 245+ engines, multi-instance fallback, cookie persistence, regional engines. Privacy-first AI search integration.

## Long Description

SearXNG MCP Server is a Model Context Protocol (MCP) 2.0 implementation that connects AI agents to SearXNG, a privacy-respecting metasearch engine. Built with FastMCP, it provides robust search capabilities across 245+ search engines spanning 10 categories, including regional and non-English engines like Baidu, Yandex, and Naver.

### Key Features

🌐 **Multi-Instance Resilience**: Automatic fallback across public SearXNG instances with configurable local instance support ensures uninterrupted search access.

🍪 **Preference Persistence**: Per-instance cookie management maintains user preferences (language, disabled plugins, engine selections) across sessions.

🌍 **Global Coverage**: Comprehensive support for regional and non-English search engines enables true multilingual search capabilities.

🎯 **Advanced Search Syntax**: Full support for SearXNG's bang modifiers (!go, !gh), language tags (:en, :zh), and specialized categories.

🔒 **Privacy-Focused**: Zero tracking, respects SearXNG's privacy principles and MCP's security guidelines.

⚡ **Production-Ready**: Built with FastMCP for automatic schema generation, transport flexibility (stdio, SSE), and robust error handling.

### Use Cases

- **AI Research Assistants**: Enable AI agents to search academic papers across arXiv, PubMed, and Google Scholar
- **Code Discovery**: Search GitHub, StackOverflow, PyPI, and other developer resources
- **Multilingual Information Retrieval**: Search in multiple languages using regional engines
- **Privacy-Conscious Applications**: Integrate search without user tracking or data collection
- **Multi-Category Exploration**: Search across images, videos, news, maps, music, and more

### Technical Highlights

- **MCP 2.0 Compliant**: Full JSON-RPC 2.0 implementation with capability negotiation
- **FastMCP Framework**: Pythonic decorators with automatic tool registration
- **Async/Await**: Modern Python async for efficient concurrent requests
- **Type Safety**: Comprehensive type hints and Pydantic models
- **Automated Monitoring**: Weekly workflows check for SearXNG, MCP, and dependency updates

## Topics/Tags

`mcp` `model-context-protocol` `searxng` `search-engine` `metasearch` `ai-tools` `privacy` `fastmcp` `python` `async` `multi-language` `search-api` `llm-tools` `ai-agents` `automation`

## Repository Settings

### Website
https://github.com/Grumpified-OGGVCT/SearXng_MCP#readme

### Topics (20 max)
- mcp
- model-context-protocol
- searxng
- search-engine
- metasearch
- ai-tools
- privacy
- fastmcp
- python
- async
- search-api
- llm-tools
- ai-agents
- automation
- privacy-focused
- multi-language
- regional-search
- json-rpc
- httpx
- pydantic

### Social Preview

**Title**: SearXNG MCP Server - Privacy-Respecting AI Search

**Description**: Connect AI agents to 245+ search engines through SearXNG with MCP 2.0. Multi-instance fallback, cookie persistence, and global coverage.

### Features to Enable

- [x] Wikis
- [x] Issues
- [x] Sponsorships (if applicable)
- [x] Projects
- [x] Preserve this repository (for long-term archival)
- [x] Discussions
- [x] Security (enable security advisories)

### Disable Features

- [ ] Allow merge commits
- [ ] Allow rebase merging
- [x] Allow squash merging (preferred)
- [x] Automatically delete head branches

## Marketing Points

### For AI Developers

"Integrate powerful, privacy-respecting search into your AI agents with three lines of code. No API keys, no tracking, no limits."

### For Privacy Advocates

"Search 245+ engines without compromising user privacy. Built on SearXNG's no-tracking philosophy with MCP's security principles."

### For Enterprise

"Self-hosted or cloud: choose from public instances or deploy your own. Full control over search infrastructure with automated health monitoring."

### For Researchers

"Access academic databases (arXiv, PubMed, Google Scholar) alongside general search, all through a unified MCP interface."

## Comparison Matrix

| Feature | SearXNG MCP | Direct API | Other MCP Servers |
|---------|-------------|------------|-------------------|
| Privacy | ✅ No tracking | ❌ Varies | ⚠️ Depends |
| Multi-source | ✅ 245+ engines | ❌ Single | ⚠️ Limited |
| Fallback | ✅ Automatic | ❌ Manual | ❌ None |
| Regional engines | ✅ Full support | ⚠️ Limited | ❌ None |
| MCP 2.0 | ✅ Full compliance | N/A | ⚠️ Varies |
| Cookie persistence | ✅ Built-in | ❌ Manual | ❌ None |
| Cost | ✅ Free | ⚠️ May require key | ✅ Free |

## Community

- **GitHub Discussions**: For questions, ideas, and community support
- **Issue Tracker**: For bug reports and feature requests  
- **Pull Requests**: Contributions welcome! See CONTRIBUTING.md
- **Security**: Responsible disclosure via GitHub Security Advisories

## Roadmap Preview

Coming soon:
- Dynamic instance discovery from searx.space
- Local caching for frequent queries
- Rate limiting and quota management
- Docker container and Kubernetes deployment
- Comprehensive test suite
- CLI interface for standalone use

---

**Maintained by**: Grumpified OGGVCT  
**License**: MIT  
**Status**: Alpha - Active Development  
**Python**: 3.10+  
**Framework**: FastMCP
