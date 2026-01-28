# Quick Start Guide

Get started with SearXNG MCP Server in under 5 minutes!

## 🚀 Installation

### Windows

1. **Install Python 3.10+** from [python.org](https://www.python.org/downloads/) (check "Add to PATH")

2. **Run installation:**
   ```cmd
   git clone https://github.com/Grumpified-OGGVCT/SearXng_MCP.git
   cd SearXng_MCP
   install.bat
   ```

3. **Start the server:**
   ```cmd
   run.bat
   ```

### Linux / macOS

1. **Install Python 3.10+:**
   ```bash
   # macOS with Homebrew
   brew install python@3.11
   
   # Ubuntu/Debian
   sudo apt install python3.11 python3-pip
   ```

2. **Run installation:**
   ```bash
   git clone https://github.com/Grumpified-OGGVCT/SearXng_MCP.git
   cd SearXng_MCP
   chmod +x install.sh run.sh
   ./install.sh
   ```

3. **Start the server:**
   ```bash
   ./run.sh
   ```

## ⚙️ Configuration

### Option 1: Use Default Settings

The server works out-of-the-box with default SearXNG instances!

### Option 2: Customize Settings

1. **Edit configuration file:**
   ```bash
   # Copy example config
   cp .env.example .env  # Linux/macOS
   copy .env.example .env  # Windows
   
   # Edit settings
   nano .env  # Linux/macOS
   notepad .env  # Windows
   ```

2. **Common settings:**
   ```bash
   # Change instances
   SEARXNG_INSTANCES=https://your-instance.com,https://another-instance.com
   
   # Add local fallback
   SEARXNG_LOCAL_INSTANCE=http://localhost:8888
   
   # Adjust timeouts
   SEARXNG_TIMEOUT=10.0
   ```

## 🔌 Connect to Claude Desktop

1. **Find configuration file:**
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux:** `~/.config/claude/claude_desktop_config.json`

2. **Add SearXNG MCP server:**
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

3. **Restart Claude Desktop**

## 📖 Usage Examples

### Basic Search

Ask Claude:
```
Search for "python asyncio tutorial"
```

### Image Search

```
Search for "mountain landscapes" in images category
```

### GitHub Code Search

```
Search GitHub for "fastmcp examples"
```

### Scientific Papers

```
Search arXiv for "transformer neural networks"
```

### Language-Specific Search

```
Search in Chinese for "人工智能"
```

### Advanced Search

```
Search for "machine learning" in science and IT categories, 
published in the last month
```

## 🛠️ Testing

### Test Installation

```bash
python -c "import searxng_mcp; print(f'Version: {searxng_mcp.__version__}')"
```

### Run Examples

```bash
# Basic search examples
python examples/basic_search.py

# Advanced search examples
python examples/advanced_search.py
```

## 🐛 Troubleshooting

### Python Not Found

**Windows:** Reinstall Python and check "Add Python to PATH"

**Linux/macOS:** Run `which python3` to verify installation

### Permission Denied (Linux/macOS)

```bash
chmod +x install.sh run.sh
```

### Import Errors

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Reinstall
pip install -e .
```

### Connection Issues

- Check internet connection
- Try different instances in `.env`
- Increase timeout values

## 📚 Next Steps

1. **Read full documentation:** [README.md](README.md)
2. **Installation guide:** [INSTALL.md](INSTALL.md)
3. **API reference:** Check the MCP tools section in README
4. **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)
5. **Get help:** [GitHub Issues](https://github.com/Grumpified-OGGVCT/SearXng_MCP/issues)

## 🎯 Search Categories

The server supports 10 categories with 245+ engines:

| Category | Examples |
|----------|----------|
| **general** | google, bing, duckduckgo, yandex, baidu |
| **images** | google_images, unsplash, pixabay |
| **videos** | youtube, vimeo, bilibili |
| **news** | google_news, bbc, reuters |
| **map** | openstreetmap, apple_maps |
| **music** | soundcloud, bandcamp, genius |
| **it** | github, stackoverflow, pypi |
| **science** | arxiv, pubmed, google_scholar |
| **files** | fdroid, apkmirror, zlibrary |
| **social_media** | reddit, mastodon, lemmy |

## 🌟 Key Features

- ✅ **245+ Search Engines** across 10 categories
- ✅ **Multi-Instance Fallback** for reliability
- ✅ **Regional Engines** (Baidu, Yandex, Naver, etc.)
- ✅ **Cookie Persistence** for preferences
- ✅ **Bang Syntax** (!go, !gh, :en, :zh)
- ✅ **Privacy-Focused** (no tracking)
- ✅ **MCP 2.0 Compliant**

## ⚡ Quick Commands

```bash
# Install
./install.sh            # Linux/macOS
install.bat             # Windows

# Run
./run.sh                # Linux/macOS
run.bat                 # Windows

# Upgrade
./install.sh --upgrade  # Linux/macOS
install.bat --upgrade   # Windows

# Development mode
./install.sh --dev      # Linux/macOS
install.bat --dev       # Windows

# Help
./install.sh --help     # Linux/macOS
install.bat --help      # Windows
```

---

**Need Help?** Open an issue on [GitHub](https://github.com/Grumpified-OGGVCT/SearXng_MCP/issues)

**License:** MIT | **Version:** 0.1.0 | **Last Updated:** 2026-01-28
