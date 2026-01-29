# Contributing to SearXNG MCP Server

Thank you for your interest in contributing to the SearXNG MCP Server! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the issue list to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the behavior
- **Expected behavior**
- **Actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Log output** if applicable

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description**
- **Use case** explaining why this would be useful
- **Possible implementation** if you have ideas
- **Alternatives considered**

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the code style guidelines
3. **Add tests** if applicable
4. **Update documentation** to reflect your changes
5. **Ensure all tests pass** and code is properly formatted
6. **Submit a pull request** with a clear description

#### Pull Request Guidelines

- Keep changes focused and atomic
- Follow existing code style and conventions
- Write clear commit messages
- Update README.md if needed
- Add comments for complex logic
- Ensure backward compatibility unless explicitly breaking

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- pip or uv package manager

### Setting Up Your Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/SearXng_MCP.git
cd SearXng_MCP

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install the package in editable mode
pip install -e .
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=searxng_mcp --cov-report=html

# Run specific test file
pytest tests/test_server.py
```

### Code Quality

We use several tools to maintain code quality:

#### Formatting with Black

```bash
# Format all Python files
black src/ tests/

# Check without modifying
black --check src/ tests/
```

#### Linting with Ruff

```bash
# Lint all files
ruff check src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/
```

#### Type Checking with MyPy

```bash
# Type check
mypy src/
```

#### Run All Checks

```bash
# Format, lint, and type check
black src/ tests/ && ruff check src/ tests/ && mypy src/
```

## Code Style Guidelines

### Python Style

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use type hints for function parameters and return values
- Maximum line length: 100 characters
- Use descriptive variable and function names
- Add docstrings to all public functions and classes

### Example Code Style

```python
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


async def search_instance(
    instance: str,
    query: str,
    timeout: float = 5.0,
) -> Optional[Dict[str, Any]]:
    """
    Search a specific SearXNG instance.

    Args:
        instance: The SearXNG instance URL
        query: The search query
        timeout: Request timeout in seconds

    Returns:
        Search results dictionary or None if failed

    Raises:
        httpx.HTTPError: If the request fails
    """
    logger.info(f"Searching {instance} for: {query}")
    # Implementation here
    pass
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: add support for custom user agents
fix: handle timeout errors in instance fallback
docs: update installation instructions for Windows
refactor: simplify cookie persistence logic
```

## Project Structure

```
SearXng_MCP/
├── src/
│   └── searxng_mcp/
│       ├── __init__.py
│       ├── server.py          # Main MCP server implementation
│       └── utils.py           # Utility functions (future)
├── tests/
│   ├── __init__.py
│   └── test_server.py         # Server tests
├── examples/
│   ├── basic_search.py        # Basic usage examples
│   └── advanced_search.py     # Advanced usage examples
├── docs/                      # Extended documentation
├── .github/
│   └── workflows/
│       └── ci.yml             # CI/CD pipeline
├── pyproject.toml             # Project configuration
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
├── README.md
├── CONTRIBUTING.md
├── LICENSE
└── .gitignore
```

## Testing Guidelines

### Writing Tests

- Write tests for all new features
- Maintain or improve code coverage
- Use descriptive test names
- Test edge cases and error conditions
- Mock external dependencies (HTTP requests, etc.)

### Test Structure

```python
import pytest
from searxng_mcp.server import InstanceManager


@pytest.fixture
def instance_manager():
    """Create an instance manager for testing."""
    return InstanceManager(
        instances=["https://test.example.com"],
        timeout=1.0,
    )


@pytest.mark.asyncio
async def test_search_success(instance_manager):
    """Test successful search with valid query."""
    # Arrange
    query = "test query"
    
    # Act
    result = await instance_manager.search(query)
    
    # Assert
    assert result is not None
    assert "results" in result
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of the function.

    Longer description if needed, explaining the behavior
    and any important notes.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is negative
    """
    pass
```

### README Updates

When adding features:
- Update the Features section
- Add usage examples
- Update the table of contents if needed
- Add to the Roadmap section if partially complete

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create a release branch
4. Run all tests and quality checks
5. Create a pull request
6. After merge, tag the release
7. Publish to PyPI (if applicable)

## Questions?

- Check existing issues and discussions
- Ask in GitHub Discussions
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to SearXNG MCP Server! 🎉
