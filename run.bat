@echo off
REM ============================================================================
REM SearXNG MCP Server - Windows Run Script
REM ============================================================================
REM This script runs the SearXNG MCP Server on Windows systems.
REM
REM Usage:
REM   run.bat [options]
REM
REM Options:
REM   --help      Show this help message
REM   --version   Show version information
REM   --config    Specify custom config file
REM ============================================================================

setlocal enabledelayedexpansion

REM Check for help flag
if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help

REM Check for version flag
if "%1"=="--version" goto :show_version
if "%1"=="-v" goto :show_version

REM Set color codes
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "RESET=[0m"

REM Display banner
echo.
echo %BLUE%============================================================================%RESET%
echo %BLUE%  SearXNG MCP Server%RESET%
echo %BLUE%============================================================================%RESET%
echo.

REM Check if installed
echo %YELLOW%Checking installation...%RESET%
python -c "import searxng_mcp" 2>nul
if errorlevel 1 (
    echo %RED%Error: SearXNG MCP Server is not installed%RESET%
    echo.
    echo Please run install.bat first:
    echo   %BLUE%install.bat%RESET%
    echo.
    exit /b 1
)
echo %GREEN%Installation verified%RESET%

REM Check if virtual environment exists and activate it
if exist .venv\Scripts\activate.bat (
    echo %YELLOW%Activating virtual environment...%RESET%
    call .venv\Scripts\activate.bat
    if errorlevel 1 (
        echo %RED%Failed to activate virtual environment%RESET%
        exit /b 1
    )
    echo %GREEN%Virtual environment activated%RESET%
)

REM Load environment variables from .env file if it exists
if exist .env (
    echo %YELLOW%Loading configuration from .env...%RESET%
    for /f "usebackq tokens=1,2 delims==" %%a in (.env) do (
        set "line=%%a"
        REM Skip comments and empty lines
        if not "!line:~0,1!"=="#" if not "!line!"=="" (
            set "%%a=%%b"
        )
    )
    echo %GREEN%Configuration loaded%RESET%
)

REM Display configuration
echo.
echo %BLUE%Configuration:%RESET%
if defined SEARXNG_INSTANCES (
    echo   Instances: %SEARXNG_INSTANCES%
) else (
    echo   Instances: Default instances
)
if defined SEARXNG_LOCAL_INSTANCE (
    echo   Local Instance: %SEARXNG_LOCAL_INSTANCE%
)
if defined SEARXNG_TIMEOUT (
    echo   Timeout: %SEARXNG_TIMEOUT%s
)

REM Start the server
echo.
echo %GREEN%Starting SearXNG MCP Server...%RESET%
echo %YELLOW%Press Ctrl+C to stop the server%RESET%
echo.
echo %BLUE%============================================================================%RESET%
echo.

python -m searxng_mcp.server

REM Check exit code
if errorlevel 1 (
    echo.
    echo %RED%Server stopped with error%RESET%
    exit /b 1
)

echo.
echo %GREEN%Server stopped%RESET%
exit /b 0

:show_help
echo.
echo Usage: run.bat [options]
echo.
echo Options:
echo   --help      Show this help message
echo   --version   Show version information
echo.
echo Environment Variables:
echo   SEARXNG_INSTANCES        Comma-separated list of instance URLs
echo   SEARXNG_LOCAL_INSTANCE   Local instance URL for fallback
echo   SEARXNG_TIMEOUT          Request timeout in seconds
echo   SEARXNG_LOCAL_TIMEOUT    Local instance timeout in seconds
echo   SEARXNG_COOKIE_DIR       Directory for cookie storage
echo.
echo Configuration:
echo   Edit .env file to customize settings
echo   See .env.example for available options
echo.
echo Examples:
echo   run.bat                  Run with default settings
echo   run.bat --version        Show version information
echo.
exit /b 0

:show_version
python -c "import searxng_mcp; print(f'SearXNG MCP Server v{searxng_mcp.__version__}'); print(f'Author: {searxng_mcp.__author__}'); print(f'License: {searxng_mcp.__license__}')"
exit /b 0
