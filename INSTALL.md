# Installation Guide

Complete installation guide for SearXNG MCP Server across all platforms.

## Table of Contents

- [Quick Start](#quick-start)
- [Windows Installation](#windows-installation)
- [Linux Installation](#linux-installation)
- [macOS Installation](#macos-installation)
- [Manual Installation](#manual-installation)
- [Docker Installation](#docker-installation)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

---

## Quick Start

### Windows

```cmd
REM Download or clone the repository
git clone https://github.com/Grumpified-OGGVCT/SearXng_MCP.git
cd SearXng_MCP

REM Run installation script
install.bat

REM Start the server
run.bat
```

### Linux / macOS

```bash
# Download or clone the repository
git clone https://github.com/Grumpified-OGGVCT/SearXng_MCP.git
cd SearXng_MCP

# Make scripts executable (if not already)
chmod +x install.sh run.sh

# Run installation script
./install.sh

# Start the server
./run.sh
```

---

## Windows Installation

### Prerequisites

1. **Python 3.10 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"
   - Verify: `python --version`

2. **Git** (optional, for cloning)
   - Download from [git-scm.com](https://git-scm.com/download/win)
   - Or use GitHub Desktop

### Step-by-Step Installation

#### Option 1: Using Installation Script (Recommended)

1. **Download the repository**
   ```cmd
   git clone https://github.com/Grumpified-OGGVCT/SearXng_MCP.git
   cd SearXng_MCP
   ```
   
   Or download ZIP from GitHub and extract it.

2. **Run the installation script**
   ```cmd
   install.bat
   ```
   
   This will:
   - Check Python installation
   - Create a virtual environment
   - Install all dependencies
   - Set up the package
   - Create configuration files

3. **Customize configuration** (optional)
   ```cmd
   notepad .env
   ```
   Edit the settings as needed (see [Configuration](#configuration) section).

4. **Run the server**
   ```cmd
   run.bat
   ```

#### Option 2: With Development Tools

Install with development dependencies for contributing:

```cmd
install.bat --dev
```

#### Option 3: Upgrade Existing Installation

```cmd
install.bat --upgrade
```

### Script Options

```cmd
install.bat [options]

Options:
  --dev       Install with development dependencies
  --upgrade   Upgrade existing installation
  --help      Show help message
```

---

## Linux Installation

### Prerequisites

1. **Python 3.10 or higher**
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt update
   sudo apt install python3.11 python3.11-venv python3-pip
   ```
   
   **Fedora/RHEL:**
   ```bash
   sudo dnf install python3.11 python3-pip
   ```
   
   **Arch Linux:**
   ```bash
   sudo pacman -S python python-pip
   ```

2. **Git**
   ```bash
   # Ubuntu/Debian
   sudo apt install git
   
   # Fedora/RHEL
   sudo dnf install git
   
   # Arch Linux
   sudo pacman -S git
   ```

### Step-by-Step Installation

#### Option 1: Using Installation Script (Recommended)

1. **Download the repository**
   ```bash
   git clone https://github.com/Grumpified-OGGVCT/SearXng_MCP.git
   cd SearXng_MCP
   ```

2. **Make scripts executable**
   ```bash
   chmod +x install.sh run.sh
   ```

3. **Run the installation script**
   ```bash
   ./install.sh
   ```

4. **Customize configuration** (optional)
   ```bash
   nano .env
   # or
   vim .env
   ```

5. **Run the server**
   ```bash
   ./run.sh
   ```

#### Option 2: With Development Tools

```bash
./install.sh --dev
```

#### Option 3: Upgrade Existing Installation

```bash
./install.sh --upgrade
```

### Script Options

```bash
./install.sh [options]

Options:
  --dev       Install with development dependencies
  --upgrade   Upgrade existing installation
  --help      Show help message
```

---

## macOS Installation

### Prerequisites

1. **Python 3.10 or higher**
   
   **Using Homebrew (Recommended):**
   ```bash
   # Install Homebrew if not installed
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Install Python
   brew install python@3.11
   ```
   
   **Official Installer:**
   - Download from [python.org](https://www.python.org/downloads/macos/)
   - Run the installer

2. **Git**
   ```bash
   # Usually pre-installed, verify with:
   git --version
   
   # If not installed:
   brew install git
   ```

### Step-by-Step Installation

Follow the same steps as [Linux Installation](#linux-installation).

The installation script automatically detects macOS and adjusts accordingly.

---

## Manual Installation

If you prefer not to use the installation scripts:

### 1. Clone the Repository

```bash
git clone https://github.com/Grumpified-OGGVCT/SearXng_MCP.git
cd SearXng_MCP
```

### 2. Create Virtual Environment

**Windows:**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Upgrade pip

```bash
python -m pip install --upgrade pip
```

### 4. Install Dependencies

```bash
# Main dependencies
pip install -r requirements.txt

# Development dependencies (optional)
pip install -r requirements-dev.txt
```

### 5. Install Package

```bash
pip install -e .
```

### 6. Create Configuration

```bash
# Copy example config
cp .env.example .env

# Edit configuration
nano .env  # or vim, code, notepad, etc.
```

### 7. Run the Server

```bash
python -m searxng_mcp.server
```

---

## Docker Installation

### Coming Soon

Docker support is planned for a future release.

---

## Configuration

### Configuration File

The server uses a `.env` file for configuration. A template is provided in `.env.example`.

### Configuration Options

```bash
# SearXNG Instances (comma-separated)
SEARXNG_INSTANCES=https://search.sapti.me,https://searx.be,https://search.bus-hit.me

# Local SearXNG Instance (optional fallback)
SEARXNG_LOCAL_INSTANCE=http://localhost:8888

# Request Timeout (seconds)
SEARXNG_TIMEOUT=5.0

# Local Instance Timeout (seconds)
SEARXNG_LOCAL_TIMEOUT=15.0

# Cookie Directory
SEARXNG_COOKIE_DIR=~/.searxng_mcp/cookies
```

### MCP Client Configuration

Add to your MCP client configuration (e.g., Claude Desktop):

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**Linux/macOS:** `~/.config/claude/claude_desktop_config.json`

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

**Or with absolute paths:**

```json
{
  "mcpServers": {
    "searxng": {
      "command": "C:\\Path\\To\\SearXng_MCP\\.venv\\Scripts\\python.exe",
      "args": ["-m", "searxng_mcp.server"],
      "env": {
        "SEARXNG_INSTANCES": "https://search.sapti.me"
      }
    }
  }
}
```

---

## Verification

### Test Installation

```bash
# Check if package is installed
python -c "import searxng_mcp; print(searxng_mcp.__version__)"

# Should output: 0.1.0
```

### Test Search

**Windows:**
```cmd
python -c "import asyncio; from searxng_mcp.server import get_instance_manager; print(asyncio.run(get_instance_manager().search('test')))"
```

**Linux/macOS:**
```bash
python3 -c "import asyncio; from searxng_mcp.server import get_instance_manager; print(asyncio.run(get_instance_manager().search('test')))"
```

### Test with Examples

```bash
# Basic search examples
python examples/basic_search.py

# Advanced search examples
python examples/advanced_search.py
```

---

## Troubleshooting

### Python Not Found

**Windows:**
- Reinstall Python and check "Add Python to PATH"
- Or manually add Python to PATH:
  - Right-click "This PC" → Properties → Advanced System Settings
  - Environment Variables → Path → Add Python directory

**Linux/macOS:**
- Ensure `python3` is in PATH: `which python3`
- Install Python 3.10+: See [Prerequisites](#prerequisites)

### Permission Denied (Linux/macOS)

```bash
# Make scripts executable
chmod +x install.sh run.sh

# If still issues, try with bash explicitly
bash install.sh
bash run.sh
```

### Virtual Environment Issues

```bash
# Remove and recreate
rm -rf .venv

# Run installation again
./install.sh  # Linux/macOS
install.bat   # Windows
```

### Import Errors

```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
pip install -e .
```

### Connection Errors

- Check your internet connection
- Try different SearXNG instances in `.env`
- Increase timeout values in `.env`

### Port Already in Use

If running as HTTP server:
- Change port in configuration
- Or stop conflicting service

---

## Uninstallation

### Remove Package

```bash
# Activate virtual environment first
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Uninstall package
pip uninstall searxng-mcp
```

### Remove Virtual Environment

**Windows:**
```cmd
rmdir /s /q .venv
```

**Linux/macOS:**
```bash
rm -rf .venv
```

### Remove Configuration and Cookies

**Windows:**
```cmd
rmdir /s /q %USERPROFILE%\.searxng_mcp
```

**Linux/macOS:**
```bash
rm -rf ~/.searxng_mcp
```

### Remove Repository

```bash
cd ..
rm -rf SearXng_MCP  # Linux/macOS
rmdir /s /q SearXng_MCP  # Windows
```

---

## Getting Help

- **Documentation**: [README.md](README.md)
- **Issues**: [GitHub Issues](https://github.com/Grumpified-OGGVCT/SearXng_MCP/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Grumpified-OGGVCT/SearXng_MCP/discussions)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Next Steps

After installation:

1. **Configure the server**: Edit `.env` file
2. **Set up MCP client**: Add to Claude Desktop config
3. **Test the tools**: Try example scripts
4. **Read the docs**: Check README.md for usage examples
5. **Join discussions**: Share feedback on GitHub

---

**Last Updated**: 2026-01-28  
**Version**: 0.1.0
