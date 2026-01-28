#!/bin/bash
# ============================================================================
# SearXNG MCP Server - Unix/Linux/macOS Installation Script
# ============================================================================
# This script installs the SearXNG MCP Server and all its dependencies
# on Unix-like systems (Linux, macOS, BSD).
#
# Requirements:
#   - Python 3.10 or higher
#   - pip package manager
#
# Usage:
#   ./install.sh [options]
#   bash install.sh [options]
#
# Options:
#   --dev       Install with development dependencies
#   --upgrade   Upgrade existing installation
#   --help      Show this help message
# ============================================================================

set -e  # Exit on error

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RESET='\033[0m'

# Functions
show_help() {
    cat << EOF

Usage: $0 [options]

Options:
  --dev       Install with development dependencies
  --upgrade   Upgrade existing installation
  --help      Show this help message

Examples:
  $0                     Install with default settings
  $0 --dev               Install with development tools
  $0 --upgrade           Upgrade existing installation
  $0 --dev --upgrade     Upgrade with development tools

EOF
    exit 0
}

error_exit() {
    echo -e "${RED}Error: $1${RESET}" >&2
    exit 1
}

# Parse arguments
DEV_FLAG=""
UPGRADE_FLAG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            DEV_FLAG="1"
            shift
            ;;
        --upgrade)
            UPGRADE_FLAG="--upgrade"
            shift
            ;;
        --help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}Unknown option: $1${RESET}"
            show_help
            ;;
    esac
done

# Display banner
echo ""
echo -e "${BLUE}============================================================================${RESET}"
echo -e "${BLUE}  SearXNG MCP Server - Installation Script${RESET}"
echo -e "${BLUE}============================================================================${RESET}"
echo ""

# Check if Python is installed
echo -e "${YELLOW}[1/6] Checking Python installation...${RESET}"
if ! command -v python3 &> /dev/null; then
    error_exit "Python 3 is not installed. Please install Python 3.10 or higher."
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}Found Python $PYTHON_VERSION${RESET}"

# Verify Python version is 3.10 or higher
MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 10 ]); then
    error_exit "Python 3.10 or higher is required. You have $PYTHON_VERSION"
fi

# Check if pip is installed
echo ""
echo -e "${YELLOW}[2/6] Checking pip installation...${RESET}"
if ! python3 -m pip --version &> /dev/null; then
    error_exit "pip is not installed. Please install pip for Python 3."
fi
echo -e "${GREEN}pip is installed${RESET}"

# Upgrade pip
echo ""
echo -e "${YELLOW}[3/6] Upgrading pip...${RESET}"
python3 -m pip install --upgrade pip --quiet || echo -e "${RED}Warning: Failed to upgrade pip${RESET}"
echo -e "${GREEN}pip upgraded successfully${RESET}"

# Create virtual environment
echo ""
echo -e "${YELLOW}[4/6] Setting up virtual environment...${RESET}"
if [ -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists${RESET}"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf .venv
    else
        echo "Using existing virtual environment..."
    fi
fi

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv || error_exit "Failed to create virtual environment"
    echo -e "${GREEN}Virtual environment created${RESET}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate || error_exit "Failed to activate virtual environment"
echo -e "${GREEN}Virtual environment activated${RESET}"

# Install dependencies
echo ""
echo -e "${YELLOW}[5/6] Installing dependencies...${RESET}"

# Install main dependencies
echo "Installing main dependencies..."
pip install -r requirements.txt $UPGRADE_FLAG --quiet || error_exit "Failed to install dependencies"
echo -e "${GREEN}Main dependencies installed${RESET}"

# Install development dependencies if --dev flag is set
if [ -n "$DEV_FLAG" ]; then
    echo "Installing development dependencies..."
    pip install -r requirements-dev.txt $UPGRADE_FLAG --quiet || error_exit "Failed to install development dependencies"
    echo -e "${GREEN}Development dependencies installed${RESET}"
fi

# Install package in editable mode
echo ""
echo -e "${YELLOW}[6/6] Installing SearXNG MCP Server...${RESET}"
pip install -e . $UPGRADE_FLAG --quiet || error_exit "Failed to install SearXNG MCP Server"
echo -e "${GREEN}SearXNG MCP Server installed successfully${RESET}"

# Create cookie directory
COOKIE_DIR="$HOME/.searxng_mcp/cookies"
if [ ! -d "$COOKIE_DIR" ]; then
    mkdir -p "$COOKIE_DIR"
    echo -e "${GREEN}Created cookie directory${RESET}"
fi

# Copy example config if it doesn't exist
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo -e "${GREEN}Created .env configuration file${RESET}"
    echo -e "${YELLOW}Please edit .env to customize your configuration${RESET}"
fi

# Make shell scripts executable
if [ -f "run.sh" ]; then
    chmod +x run.sh
fi
if [ -f "install.sh" ]; then
    chmod +x install.sh
fi

# Display success message
echo ""
echo -e "${GREEN}============================================================================${RESET}"
echo -e "${GREEN}  Installation Complete!${RESET}"
echo -e "${GREEN}============================================================================${RESET}"
echo ""
echo "To run the server:"
echo -e "  ${BLUE}./run.sh${RESET}"
echo ""
echo "To activate the virtual environment manually:"
echo -e "  ${BLUE}source .venv/bin/activate${RESET}"
echo ""
echo "To run the server directly:"
echo -e "  ${BLUE}python -m searxng_mcp.server${RESET}"
echo ""
echo "For more information, see README.md"
echo ""

exit 0
