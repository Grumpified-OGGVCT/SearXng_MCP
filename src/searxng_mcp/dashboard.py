"""
SearXNG MCP Dashboard Server

Professional web dashboard for monitoring and managing SearXNG MCP server.
Provides real-time health monitoring, configuration management, and search testing.
"""

import asyncio
import json
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import httpx
from pydantic import BaseModel


# Background task
async def periodic_health_check():
    """Periodically check instance health and broadcast updates."""
    while True:
        try:
            results = await manager.check_all_instances()
            await broadcast_health_update({
                "type": "health_update",
                "data": results,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            print(f"Health check error: {e}")
        await asyncio.sleep(30)  # Check every 30 seconds


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for background tasks."""
    # Startup: start background health checks
    task = asyncio.create_task(periodic_health_check())
    yield
    # Shutdown: cancel background tasks
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="SearXNG MCP Dashboard",
    description="Professional monitoring dashboard for SearXNG MCP Server",
    version="0.1.0",
    lifespan=lifespan,
)

# Store WebSocket connections
active_connections: List[WebSocket] = []


class InstanceHealth(BaseModel):
    """Instance health status model."""

    instance: str
    status: str
    response_time: Optional[float] = None
    error: Optional[str] = None
    timestamp: str


class SearchRequest(BaseModel):
    """Search request model."""

    query: str
    categories: Optional[str] = None
    engines: Optional[str] = None
    language: str = "en"


class DashboardManager:
    """Manages dashboard data and monitoring."""

    def __init__(self):
        self.load_config()
        self.health_history: List[Dict] = []
        self.search_stats = {"total_searches": 0, "successful_searches": 0, "failed_searches": 0}

    def load_config(self):
        """Load configuration from environment."""
        # Try to load from .env file
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ.setdefault(key.strip(), value.strip())

        # Load instances
        instances_str = os.environ.get("SEARXNG_INSTANCES", "")
        if instances_str:
            self.instances = [i.strip() for i in instances_str.split(",")]
        else:
            self.instances = [
                "https://search.sapti.me",
                "https://searx.be",
                "https://search.bus-hit.me",
                "https://search.mdosch.de",
                "https://searx.tiekoetter.com",
            ]

        self.local_instance = os.environ.get("SEARXNG_LOCAL_INSTANCE")

        try:
            self.timeout = float(os.environ.get("SEARXNG_TIMEOUT", "5.0"))
        except ValueError:
            self.timeout = 5.0

        try:
            self.local_timeout = float(os.environ.get("SEARXNG_LOCAL_TIMEOUT", "15.0"))
        except ValueError:
            self.local_timeout = 15.0

    async def check_instance(self, instance: str, timeout: float) -> Dict:
        """Check health of a single instance."""
        result = {
            "instance": instance,
            "status": "unknown",
            "response_time": None,
            "error": None,
            "timestamp": datetime.utcnow().isoformat(),
        }

        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(
                    f"{instance}/search",
                    params={"q": "test", "format": "json"},
                )

                response_time = time.time() - start_time
                result["response_time"] = round(response_time, 3)

                if response.status_code == 200:
                    result["status"] = "healthy"
                else:
                    result["status"] = "unhealthy"
                    result["error"] = f"HTTP {response.status_code}"

        except httpx.TimeoutException:
            result["status"] = "timeout"
            result["error"] = f"Timeout after {timeout}s"
        except httpx.ConnectError:
            result["status"] = "unreachable"
            result["error"] = "Connection failed"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)[:100]

        return result

    async def check_all_instances(self) -> List[Dict]:
        """Check health of all instances."""
        tasks = []

        for instance in self.instances:
            tasks.append(self.check_instance(instance, self.timeout))

        if self.local_instance:
            tasks.append(self.check_instance(self.local_instance, self.local_timeout))

        results = await asyncio.gather(*tasks)

        # Store in history (keep last 100)
        self.health_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "results": results
        })
        if len(self.health_history) > 100:
            self.health_history.pop(0)

        return list(results)

    async def search_instance(self, instance: str, query: str, **params) -> Dict:
        """Perform search on instance."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                search_params = {"q": query, "format": "json", **params}
                response = await client.get(f"{instance}/search", params=search_params)
                
                if response.status_code == 200:
                    self.search_stats["successful_searches"] += 1
                    return {"status": "success", "data": response.json()}
                else:
                    self.search_stats["failed_searches"] += 1
                    return {"status": "error", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            self.search_stats["failed_searches"] += 1
            return {"status": "error", "error": str(e)}
        finally:
            self.search_stats["total_searches"] += 1


# Initialize manager
manager = DashboardManager()


# WebSocket connection manager
async def broadcast_health_update(data: Dict):
    """Broadcast health update to all connected clients."""
    message = json.dumps(data)
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except Exception:
            active_connections.remove(connection)


# API Endpoints
@app.get("/")
async def root():
    """Serve the dashboard HTML."""
    return FileResponse("src/searxng_mcp/static/dashboard.html")


@app.get("/api/health")
async def get_health():
    """Get current health status of all instances."""
    results = await manager.check_all_instances()
    return {"status": "ok", "instances": results, "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/config")
async def get_config():
    """Get current configuration."""
    return {
        "instances": manager.instances,
        "local_instance": manager.local_instance,
        "timeout": manager.timeout,
        "local_timeout": manager.local_timeout,
    }


@app.get("/api/stats")
async def get_stats():
    """Get search statistics."""
    return {
        "search_stats": manager.search_stats,
        "health_history_count": len(manager.health_history),
    }


@app.post("/api/search")
async def test_search(request: SearchRequest):
    """Test search on first available instance."""
    for instance in manager.instances:
        result = await manager.search_instance(
            instance,
            request.query,
            categories=request.categories,
            engines=request.engines,
            language=request.language,
        )
        if result["status"] == "success":
            return result
    
    return {"status": "error", "error": "All instances failed"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        # Send initial data
        results = await manager.check_all_instances()
        await websocket.send_text(json.dumps({
            "type": "health_update",
            "data": results,
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            # Echo back or handle commands
            await websocket.send_text(data)
    except WebSocketDisconnect:
        active_connections.remove(websocket)


# Mount static files
try:
    app.mount("/static", StaticFiles(directory="src/searxng_mcp/static"), name="static")
except RuntimeError:
    pass  # Directory might not exist yet


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting SearXNG MCP Dashboard...")
    print("📊 Dashboard: http://localhost:8765")
    print("📚 API Docs: http://localhost:8765/docs")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8765, log_level="info")
