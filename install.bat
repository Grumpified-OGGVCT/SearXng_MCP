@echo off
REM ============================================================================
REM SearXNG MCP Server - Windows Installation Script
REM ============================================================================
REM This script installs the SearXNG MCP Server and all its dependencies
REM on Windows systems.
REM
REM Requirements:
REM   - Python 3.10 or higher
REM   - pip package manager
REM
REM Usage:
REM   install.bat [options]
REM
REM Options:
REM   --dev       Install with development dependencies
REM   --upgrade   Upgrade existing installation
REM   --help      Show this help message
REM ============================================================================

setlocal enabledelayedexpansion

REM Check for help flag
if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help

REM Set color codes
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "BLUE=[94m"
set "RESET=[0m"

REM Display banner
echo.
echo %BLUE%============================================================================%RESET%
echo %BLUE%  SearXNG MCP Server - Installation Script%RESET%
echo %BLUE%============================================================================%RESET%
echo.

REM Check if Python is installed
echo %YELLOW%[1/6] Checking Python installation...%RESET%
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%Error: Python is not installed or not in PATH%RESET%
    echo Please install Python 3.10 or higher from https://www.python.org/downloads/
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %GREEN%Found Python %PYTHON_VERSION%%RESET%

REM Verify Python version is 3.10 or higher
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)
if %MAJOR% LSS 3 (
    echo %RED%Error: Python 3.10 or higher is required%RESET%
    exit /b 1
)
if %MAJOR% EQU 3 if %MINOR% LSS 10 (
    echo %RED%Error: Python 3.10 or higher is required%RESET%
    exit /b 1
)

REM Check if pip is installed
echo.
echo %YELLOW%[2/6] Checking pip installation...%RESET%
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo %RED%Error: pip is not installed%RESET%
    echo Installing pip...
    python -m ensurepip --upgrade
    if errorlevel 1 (
        echo %RED%Failed to install pip%RESET%
        exit /b 1
    )
)
echo %GREEN%pip is installed%RESET%

REM Upgrade pip
echo.
echo %YELLOW%[3/6] Upgrading pip...%RESET%
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo %RED%Warning: Failed to upgrade pip%RESET%
) else (
    echo %GREEN%pip upgraded successfully%RESET%
)

REM Create virtual environment (optional but recommended)
echo.
echo %YELLOW%[4/6] Setting up virtual environment...%RESET%
if exist .venv (
    echo %YELLOW%Virtual environment already exists%RESET%
    choice /C YN /M "Do you want to recreate it?"
    if errorlevel 2 goto :skip_venv
    echo Removing existing virtual environment...
    rmdir /s /q .venv
)
echo Creating virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo %RED%Failed to create virtual environment%RESET%
    exit /b 1
)
echo %GREEN%Virtual environment created%RESET%

REM Activate virtual environment
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo %RED%Failed to activate virtual environment%RESET%
    exit /b 1
)
echo %GREEN%Virtual environment activated%RESET%

:skip_venv

REM Install dependencies
echo.
echo %YELLOW%[5/6] Installing dependencies...%RESET%

REM Check for --upgrade flag
set "UPGRADE_FLAG="
if "%1"=="--upgrade" set "UPGRADE_FLAG=--upgrade"
if "%2"=="--upgrade" set "UPGRADE_FLAG=--upgrade"

REM Check for --dev flag
set "DEV_FLAG="
if "%1"=="--dev" set "DEV_FLAG=1"
if "%2"=="--dev" set "DEV_FLAG=1"

REM Install main dependencies
echo Installing main dependencies...
python -m pip install -r requirements.txt %UPGRADE_FLAG% --quiet
if errorlevel 1 (
    echo %RED%Failed to install dependencies%RESET%
    exit /b 1
)
echo %GREEN%Main dependencies installed%RESET%

REM Install development dependencies if --dev flag is set
if defined DEV_FLAG (
    echo Installing development dependencies...
    python -m pip install -r requirements-dev.txt %UPGRADE_FLAG% --quiet
    if errorlevel 1 (
        echo %RED%Failed to install development dependencies%RESET%
        exit /b 1
    )
    echo %GREEN%Development dependencies installed%RESET%
)

REM Install package in editable mode
echo.
echo %YELLOW%[6/6] Installing SearXNG MCP Server...%RESET%
python -m pip install -e . %UPGRADE_FLAG% --quiet
if errorlevel 1 (
    echo %RED%Failed to install SearXNG MCP Server%RESET%
    exit /b 1
)
echo %GREEN%SearXNG MCP Server installed successfully%RESET%

REM Create cookie directory
if not exist "%USERPROFILE%\.searxng_mcp\cookies" (
    mkdir "%USERPROFILE%\.searxng_mcp\cookies"
    echo %GREEN%Created cookie directory%RESET%
)

REM Copy example config if it doesn't exist
if not exist .env (
    if exist .env.example (
        copy .env.example .env >nul
        echo %GREEN%Created .env configuration file%RESET%
        echo %YELLOW%Please edit .env to customize your configuration%RESET%
    )
)

REM Display success message
echo.
echo %GREEN%============================================================================%RESET%
echo %GREEN%  Installation Complete!%RESET%
echo %GREEN%============================================================================%RESET%
echo.
echo To run the server:
echo   %BLUE%run.bat%RESET%
echo.
echo To activate the virtual environment manually:
echo   %BLUE%.venv\Scripts\activate%RESET%
echo.
echo To run the server directly:
echo   %BLUE%python -m searxng_mcp.server%RESET%
echo.
echo For more information, see README.md
echo.

exit /b 0

:show_help
echo.
echo Usage: install.bat [options]
echo.
echo Options:
echo   --dev       Install with development dependencies
echo   --upgrade   Upgrade existing installation
echo   --help      Show this help message
echo.
echo Examples:
echo   install.bat                Install with default settings
echo   install.bat --dev          Install with development tools
echo   install.bat --upgrade      Upgrade existing installation
echo   install.bat --dev --upgrade  Upgrade with development tools
echo.
exit /b 0
