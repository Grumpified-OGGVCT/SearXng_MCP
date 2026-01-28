# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial MCP 2.0 server implementation with FastMCP
- Multi-instance SearXNG support with automatic fallback
- Cookie-based preference persistence
- Support for 245+ search engines across 10 categories
- Regional and non-English engine support (Baidu, Yandex, Naver, etc.)
- Bang syntax support (!go, !gh, :en, :zh, etc.)
- Three MCP tools: search, list_categories, get_instances
- Comprehensive documentation and examples
- GitHub Actions workflows for CI/CD
- Automated weekly update checks for dependencies, SearXNG, and MCP
- Issue templates and PR template
- Contributing guidelines

### Changed
- N/A (initial release)

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- Implemented secure cookie handling
- Added pip-audit for dependency vulnerability scanning
- Automated security checks in CI pipeline

## [0.1.0] - TBD

### Added
- Initial release of SearXNG MCP Server
- Core search functionality
- Instance management
- Cookie persistence
- FastMCP integration

---

## Release Types

- **Major** (x.0.0): Breaking changes to API or behavior
- **Minor** (0.x.0): New features, backwards compatible
- **Patch** (0.0.x): Bug fixes, backwards compatible

## Upgrade Notes

### From Pre-release to 0.1.0
- First official release, no upgrade path yet

---

[Unreleased]: https://github.com/Grumpified-OGGVCT/SearXng_MCP/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Grumpified-OGGVCT/SearXng_MCP/releases/tag/v0.1.0
