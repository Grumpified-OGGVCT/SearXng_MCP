# Dashboard & Setup Guide

## 🎨 Professional Dark-Themed Dashboard

Access a beautiful, real-time monitoring dashboard for your SearXNG MCP server.

### Features
- ✅ **Real-time monitoring** with WebSocket updates
- ✅ **Instance health tracking** with response times
- ✅ **Search testing** directly from the dashboard
- ✅ **Professional dark theme** with smooth animations
- ✅ **Responsive design** for all screen sizes
- ✅ **Auto-reconnecting** WebSocket connections

### Running the Dashboard

```bash
# Install dashboard dependencies
pip install fastapi uvicorn[standard] websockets

# Start the dashboard server
python -m searxng_mcp.dashboard

# Or use uvicorn directly
uvicorn searxng_mcp.dashboard:app --host 0.0.0.0 --port 8765
```

Then open your browser to:
- **Dashboard**: http://localhost:8765
- **API Docs**: http://localhost:8765/docs

### Dashboard Screenshot

The dashboard features:
- Live instance health monitoring
- Response time tracking
- Color-coded status indicators
- Real-time updates via WebSocket
- Built-in search testing interface
- Professional cyberpunk-inspired dark theme

---

## 🧙 Interactive Setup Wizard

Run the interactive setup wizard to configure your SearXNG MCP server.

### Features
- ✅ **OS detection** (Windows/Linux/macOS)
- ✅ **Instance strategy selection** (Online/Local/Hybrid)
- ✅ **Custom instance configuration**
- ✅ **Local SearXNG installation guidance** per OS
- ✅ **.env file generation**
- ✅ **Color-coded terminal output**

### Running the Setup Wizard

```bash
python setup.py
```

The wizard will guide you through:

1. **System Detection**
   - Detects your OS and Python version
   - Verifies compatibility (Python 3.10+)

2. **Instance Strategy**
   - Online Only (easiest)
   - Local + Online (recommended for reliability)
   - Local Only (requires local SearXNG)
   - Custom Configuration

3. **Instance Configuration**
   - Choose default public instances
   - Or specify custom instance URLs

4. **Local Instance Setup**
   - Detects if you have a local SearXNG instance
   - Provides OS-specific installation instructions
   - Tests connection to local instance

5. **Advanced Settings**
   - Configure timeouts
   - Adjust instance priorities

6. **Configuration Generation**
   - Automatically generates .env file
   - Shows next steps for completion

### Example Wizard Flow

```
================================================================================
  SearXNG MCP Server - Interactive Setup Wizard
================================================================================

>>> Detecting Your System

ℹ  Operating System: Linux
ℹ  Architecture: x86_64
ℹ  Python Version: 3.12.3
✓ Python 3.12.3 is compatible

>>> Choose Your Instance Strategy

Select your preferred setup strategy:
  1. Online Only (Easiest)
     Use public instances only. No local setup required.
  2. Local + Online (Recommended)
     Use public instances with local fallback for reliability.
  3. Local Only
     Use only your local instance. Requires local SearXNG setup.
  4. Custom Configuration
     Manually specify instance URLs and priorities.

Enter choice [1-4] (default: 2): 2

✓ Selected: Local + Online (Recommended)

>>> Configuring Online Instances

Default public instances:
  1. https://search.sapti.me
  2. https://searx.be
  3. https://search.bus-hit.me
  4. https://search.mdosch.de
  5. https://searx.tiekoetter.com

Use default public instances? (Y/n): y
✓ Using default instances

>>> Configuring Local SearXNG Instance

Do you have a local SearXNG instance running? (y/N): n

ℹ  You can install SearXNG locally for better reliability
Show local installation instructions? (y/N): y

📦 Docker Installation (Recommended):

1. Install Docker:
   sudo apt update && sudo apt install docker.io docker-compose

2. Create docker-compose.yml:
   mkdir searxng && cd searxng
   wget https://raw.githubusercontent.com/searxng/searxng-docker/master/docker-compose.yaml

3. Start SearXNG:
   docker-compose up -d

4. Access at: http://localhost:8888

>>> Advanced Settings (Optional)

Configure advanced settings? (y/N): n

>>> Generating Configuration

✓ Configuration saved to /path/to/.env

Setup Complete! 🎉

Next steps:

1. Review your configuration:
   /path/to/.env

2. Start the MCP server:
   ./run.sh

3. Configure your MCP client:
   Add this server to Claude Desktop or your MCP client
   See README.md for configuration examples

4. Test the setup:
   python -m searxng_mcp.health
```

---

## 🏥 Health Check Tool

Check the health of all configured SearXNG instances.

### Usage

```bash
# Basic health check
python -m searxng_mcp.health

# Verbose mode (show configuration)
python -m searxng_mcp.health --verbose
```

### Example Output

```
================================================================================
  SearXNG MCP Server - Health Check
================================================================================

Checking instances...

✓ https://search.sapti.me
  Status: HEALTHY
  Response time: 0.45s

⏱ https://searx.be
  Status: TIMEOUT
  Response time: 5.01s
  Error: Timeout after 5.0s

✗ https://search.bus-hit.me
  Status: UNREACHABLE
  Error: Connection failed

✓ https://search.mdosch.de
  Status: HEALTHY
  Response time: 0.67s

Summary:
  Total instances: 4
  Healthy: 2/4

⚠ Some instances are unavailable
  This is normal - public instances can be temporarily down
  The server will automatically use healthy instances
```

---

## 🎯 Quick Start Guide

### 1. Initial Setup

```bash
# Run the interactive setup wizard
python setup.py
```

### 2. Start the MCP Server

```bash
# Start the MCP server for AI clients
./run.sh         # Linux/macOS
run.bat          # Windows
```

### 3. (Optional) Start the Dashboard

```bash
# Start the web dashboard
python -m searxng_mcp.dashboard
```

Open http://localhost:8765 in your browser.

### 4. Check Health

```bash
# Verify instances are working
python -m searxng_mcp.health --verbose
```

---

## 📁 File Structure

```
SearXng_MCP/
├── setup.py                       # Interactive setup wizard
├── src/searxng_mcp/
│   ├── server.py                  # MCP server
│   ├── dashboard.py               # Web dashboard server
│   ├── health.py                  # Health check tool
│   └── static/
│       └── dashboard.html         # Dashboard UI
├── .env.example                   # Example configuration
└── .env                          # Your configuration (generated)
```

---

## 🔧 Configuration

After running `setup.py`, your `.env` file will contain:

```bash
# SearXNG MCP Server Configuration
# Generated by setup wizard

SEARXNG_INSTANCES=https://search.sapti.me,https://searx.be,...
SEARXNG_LOCAL_INSTANCE=http://localhost:8888
SEARXNG_TIMEOUT=5.0
SEARXNG_LOCAL_TIMEOUT=15.0
```

You can manually edit this file or re-run `setup.py` to reconfigure.

---

## 🚀 Advanced Usage

### Running Dashboard and MCP Server Together

You can run both the MCP server (for AI clients) and the web dashboard simultaneously:

**Terminal 1** - MCP Server:
```bash
./run.sh
```

**Terminal 2** - Dashboard:
```bash
python -m searxng_mcp.dashboard
```

### Custom Dashboard Port

```bash
uvicorn searxng_mcp.dashboard:app --host 0.0.0.0 --port 9000
```

### Automated Health Checks

Add to cron for automated monitoring:

```bash
# Check health every 5 minutes
*/5 * * * * cd /path/to/SearXng_MCP && python -m searxng_mcp.health
```

---

## 🎨 Dashboard Features

The dashboard provides:

1. **Real-Time Monitoring**
   - Live updates every 30 seconds
   - WebSocket connection for instant notifications
   - Auto-reconnecting on disconnection

2. **Instance Health Cards**
   - Current status (healthy/timeout/unreachable)
   - Response times
   - Error messages
   - Color-coded visual indicators

3. **Statistics**
   - Total instance count
   - Healthy instance count
   - Average response time
   - Last update timestamp

4. **Search Testing**
   - Test searches directly from dashboard
   - Select language and category
   - View JSON responses
   - Real-time results

5. **Professional UI**
   - Dark theme optimized for long viewing sessions
   - Smooth animations and transitions
   - Responsive design (mobile-friendly)
   - Cyberpunk-inspired color scheme

---

## 📊 API Endpoints

The dashboard server exposes these REST API endpoints:

### GET /api/health
Get current health status of all instances.

**Response:**
```json
{
  "status": "ok",
  "instances": [
    {
      "instance": "https://search.sapti.me",
      "status": "healthy",
      "response_time": 0.453,
      "error": null,
      "timestamp": "2026-01-28T20:30:00Z"
    }
  ],
  "timestamp": "2026-01-28T20:30:00Z"
}
```

### GET /api/config
Get current configuration.

**Response:**
```json
{
  "instances": ["https://search.sapti.me", ...],
  "local_instance": "http://localhost:8888",
  "timeout": 5.0,
  "local_timeout": 15.0
}
```

### POST /api/search
Test search on instances.

**Request:**
```json
{
  "query": "python programming",
  "categories": "general",
  "language": "en"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "results": [...],
    "suggestions": [...]
  }
}
```

### WebSocket /ws
Real-time updates for dashboard.

Sends health updates every 30 seconds.

---

## 🛠️ Troubleshooting

### Dashboard Won't Start

1. Install dependencies:
   ```bash
   pip install fastapi uvicorn websockets
   ```

2. Check port availability:
   ```bash
   lsof -i :8765  # Linux/macOS
   netstat -ano | findstr :8765  # Windows
   ```

### Setup Wizard Issues

1. Ensure Python 3.10+:
   ```bash
   python --version
   ```

2. Run with explicit Python:
   ```bash
   python3 setup.py
   ```

### Health Check Fails

1. Check network connectivity
2. Verify .env file exists and is properly formatted
3. Try verbose mode:
   ```bash
   python -m searxng_mcp.health --verbose
   ```

---

## 📖 See Also

- [README.md](../README.md) - Main documentation
- [INSTALL.md](../INSTALL.md) - Installation guide
- [QUICKSTART.md](../QUICKSTART.md) - Quick start guide
- [API Documentation](http://localhost:8765/docs) - When dashboard is running
