#!/bin/bash
# ============================================================================
# SearXNG MCP Server - Unix/Linux/macOS Run Script
# ============================================================================
# This script runs the SearXNG MCP Server on Unix-like systems.
#
# Usage:
#   ./run.sh [options]
#   bash run.sh [options]
#
# Options:
#   --help      Show this help message
#   --version   Show version information
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
  --help      Show this help message
  --version   Show version information

Environment Variables:
  SEARXNG_INSTANCES        Comma-separated list of instance URLs
  SEARXNG_LOCAL_INSTANCE   Local instance URL for fallback
  SEARXNG_TIMEOUT          Request timeout in seconds
  SEARXNG_LOCAL_TIMEOUT    Local instance timeout in seconds
  SEARXNG_COOKIE_DIR       Directory for cookie storage

Configuration:
  Edit .env file to customize settings
  See .env.example for available options

Examples:
  $0                       Run with default settings
  $0 --version             Show version information

EOF
    exit 0
}

show_version() {
    python3 -c "import searxng_mcp; print(f'SearXNG MCP Server v{searxng_mcp.__version__}'); print(f'Author: {searxng_mcp.__author__}'); print(f'License: {searxng_mcp.__license__}')"
    exit 0
}

error_exit() {
    echo -e "${RED}Error: $1${RESET}" >&2
    exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            ;;
        --version|-v)
            show_version
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
echo -e "${BLUE}  SearXNG MCP Server${RESET}"
echo -e "${BLUE}============================================================================${RESET}"
echo ""

# Check if installed
echo -e "${YELLOW}Checking installation...${RESET}"
if ! python3 -c "import searxng_mcp" 2>/dev/null; then
    error_exit "SearXNG MCP Server is not installed. Please run ./install.sh first."
fi
echo -e "${GREEN}Installation verified${RESET}"

# Check if virtual environment exists and activate it
if [ -f ".venv/bin/activate" ]; then
    echo -e "${YELLOW}Activating virtual environment...${RESET}"
    source .venv/bin/activate || error_exit "Failed to activate virtual environment"
    echo -e "${GREEN}Virtual environment activated${RESET}"
fi

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}Loading configuration from .env...${RESET}"
    # Export variables from .env (ignore comments and empty lines)
    set -a
    source <(grep -v '^#' .env | grep -v '^$' | sed 's/\r$//')
    set +a
    echo -e "${GREEN}Configuration loaded${RESET}"
fi

# Display configuration
echo ""
echo -e "${BLUE}Configuration:${RESET}"
if [ -n "$SEARXNG_INSTANCES" ]; then
    echo "  Instances: $SEARXNG_INSTANCES"
else
    echo "  Instances: Default instances"
fi
if [ -n "$SEARXNG_LOCAL_INSTANCE" ]; then
    echo "  Local Instance: $SEARXNG_LOCAL_INSTANCE"
fi
if [ -n "$SEARXNG_TIMEOUT" ]; then
    echo "  Timeout: ${SEARXNG_TIMEOUT}s"
fi

# Start the server
echo ""
echo -e "${GREEN}Starting SearXNG MCP Server...${RESET}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${RESET}"
echo ""
echo -e "${BLUE}============================================================================${RESET}"
echo ""

# Run the server
python3 -m searxng_mcp.server

# Check exit code
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo -e "${RED}Server stopped with error (exit code: $EXIT_CODE)${RESET}"
    exit $EXIT_CODE
fi

echo ""
echo -e "${GREEN}Server stopped${RESET}"
exit 0
