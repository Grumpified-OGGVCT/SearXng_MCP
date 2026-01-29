"""
SearXNG MCP Dashboard Server

Professional web dashboard for monitoring and managing SearXNG MCP server.
Provides real-time health monitoring, configuration management, search testing,
and an advanced chat interface with RAG capabilities.
"""

import asyncio
import json
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

try:
    from searxng_mcp.ai_enhancer import get_ai_enhancer

    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

from searxng_mcp.context_manager import InfiniteContextManager
from searxng_mcp.repl_manager import get_repl_manager
from searxng_mcp.rtd_manager import RealTimeDataManager

logger = logging.getLogger(__name__)


# Background task
async def periodic_health_check():
    """Periodically check instance health and broadcast updates."""
    while True:
        try:
            results = await manager.check_all_instances()
            await broadcast_health_update(
                {
                    "type": "health_update",
                    "data": results,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        except Exception as e:
            print(f"Health check error: {e}")
        await asyncio.sleep(30)  # Check every 30 seconds


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for background tasks."""
    # Startup: start background tasks
    health_task = asyncio.create_task(periodic_health_check())
    cleanup_task = asyncio.create_task(manager._cleanup_sessions())
    yield
    # Shutdown: cancel background tasks
    health_task.cancel()
    cleanup_task.cancel()
    try:
        await health_task
    except asyncio.CancelledError:
        pass
    try:
        await cleanup_task
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
active_connections: list[WebSocket] = []


class InstanceHealth(BaseModel):
    """Instance health status model."""

    instance: str
    status: str
    response_time: float | None = None
    error: str | None = None
    timestamp: str


class SearchRequest(BaseModel):
    """Search request model."""

    query: str
    categories: str | None = None
    engines: str | None = None
    language: str = "en"


class ChatMessage(BaseModel):
    """Chat message model."""

    message: str = Field(..., min_length=1, max_length=4000)
    language: str = "en"
    category: str = "general"


class REPLExecutionRequest(BaseModel):
    """REPL code execution request model."""

    code: str = Field(..., min_length=1, max_length=10000)
    description: str = Field(default="", max_length=500)
    session_id: str | None = None


class ChatSession:
    """Manages a chat session with history and context."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages: list[dict[str, Any]] = []
        self.goals: list[dict[str, Any]] = []
        self.user_model: dict[str, int] = {
            "Technical Knowledge": 50,
            "Research Interest": 50,
            "Detail Preference": 50,
        }
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()

        # Initialize infinite context manager (legacy)
        self.context_manager = InfiniteContextManager(
            recent_messages_limit=10, compression_threshold=15
        )

        # Initialize RLM REPL manager (revolutionary!)
        self.repl_manager = get_repl_manager()

    def add_message(self, role: str, content: str, metadata: dict | None = None):
        """Add a message to the session history."""
        self.messages.append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {},
            }
        )

        # Add to both context managers
        self.context_manager.add_message(role, content, metadata)
        self.repl_manager.add_message(role, content, metadata)

        # Keep only last MAX_MESSAGES_PER_SESSION messages
        if len(self.messages) > 100:  # Using hardcoded value for now
            self.messages = self.messages[-100:]
        self.last_activity = datetime.utcnow()

    def update_goal(self, goal_text: str, confidence: int):
        """Update or add a goal."""
        for goal in self.goals:
            if goal["text"] == goal_text:
                goal["confidence"] = confidence
                goal["updated"] = datetime.utcnow().isoformat()
                return

        self.goals.append(
            {
                "id": str(uuid.uuid4()),
                "text": goal_text,
                "confidence": confidence,
                "status": "in-progress",
                "created": datetime.utcnow().isoformat(),
                "updated": datetime.utcnow().isoformat(),
            }
        )

    def update_user_model(self, key: str, value: int):
        """Update user model attribute."""
        if key in self.user_model:
            self.user_model[key] = max(0, min(100, value))

    def get_context(self) -> str:
        """Get conversation context for AI."""
        # Use infinite context manager for optimized context
        context = self.context_manager.get_context(max_tokens=2000)
        return self.context_manager.format_for_model(context)

    def get_context_stats(self) -> dict[str, Any]:
        """Get context management statistics."""
        return {
            "legacy_context": self.context_manager.get_stats(),
            "repl_stats": self.repl_manager.get_stats(),
        }


class DashboardManager:
    """Manages dashboard data and monitoring."""

    # Configuration constants
    MAX_MESSAGES_PER_SESSION = 100  # Keep last 100 messages per session
    SESSION_TIMEOUT_SECONDS = 3600  # 1 hour inactivity timeout
    MAX_SESSIONS = 1000  # Maximum concurrent sessions
    USER_MODEL_INCREMENT_LONG_QUERY = 5  # Increment for queries > 10 words
    USER_MODEL_INCREMENT_RESEARCH = 3  # Increment for research interest

    def __init__(self):
        self.load_config()
        self.health_history: list[dict] = []
        self.search_stats = {"total_searches": 0, "successful_searches": 0, "failed_searches": 0}
        self.chat_sessions: dict[str, ChatSession] = {}
        self.ai_enhancer = get_ai_enhancer() if AI_AVAILABLE else None
        self._cleanup_task = None  # Will be started by lifespan

        # Initialize RTD manager
        self.rtd_manager = RealTimeDataManager()

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

    async def check_instance(self, instance: str, timeout: float) -> dict:
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

    async def check_all_instances(self) -> list[dict]:
        """Check health of all instances."""
        tasks = []

        for instance in self.instances:
            tasks.append(self.check_instance(instance, self.timeout))

        if self.local_instance:
            tasks.append(self.check_instance(self.local_instance, self.local_timeout))

        results = await asyncio.gather(*tasks)

        # Store in history (keep last 100)
        self.health_history.append({"timestamp": datetime.utcnow().isoformat(), "results": results})
        if len(self.health_history) > 100:
            self.health_history.pop(0)

        return list(results)

    async def search_instance(self, instance: str, query: str, **params) -> dict:
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

    def get_or_create_session(self, session_id: str | None = None) -> ChatSession:
        """Get or create a chat session."""
        if session_id and session_id in self.chat_sessions:
            return self.chat_sessions[session_id]

        # Enforce max sessions limit
        if len(self.chat_sessions) >= self.MAX_SESSIONS:
            # Remove oldest inactive session
            oldest_id = min(
                self.chat_sessions.keys(), key=lambda k: self.chat_sessions[k].last_activity
            )
            del self.chat_sessions[oldest_id]
            logger.info(f"Removed oldest session {oldest_id} due to max limit")

        new_id = session_id or str(uuid.uuid4())
        session = ChatSession(new_id)
        self.chat_sessions[new_id] = session
        return session

    async def _cleanup_sessions(self) -> None:
        """Background task to cleanup inactive sessions."""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                now = datetime.utcnow()
                to_remove = []

                for session_id, session in self.chat_sessions.items():
                    age = (now - session.last_activity).total_seconds()
                    if age > self.SESSION_TIMEOUT_SECONDS:
                        to_remove.append(session_id)

                for session_id in to_remove:
                    del self.chat_sessions[session_id]
                    logger.info(f"Cleaned up inactive session: {session_id}")

                if to_remove:
                    logger.info(f"Cleaned up {len(to_remove)} inactive sessions")
            except Exception as e:
                logger.error(f"Session cleanup error: {e}")

    async def process_chat_message(
        self, session: ChatSession, message: str, language: str = "en", category: str = "general"
    ) -> dict[str, Any]:
        """Process a chat message with search and AI enhancement."""
        response = {
            "thinking": None,
            "search_results": [],
            "ai_summary": None,
            "response": None,
            "goals": session.goals,
            "user_model": session.user_model,
            "context_stats": None,
            "rtd_status": None,
        }

        try:
            # Add user message to history
            session.add_message("user", message)

            # Get context stats
            response["context_stats"] = session.get_context_stats()

            # Update goals based on message
            session.update_goal("Understanding user intent", 75)

            # Perform search
            response["thinking"] = "Searching for relevant information..."

            search_result = None
            for instance in self.instances:
                result = await self.search_instance(
                    instance, message, language=language, categories=category
                )
                if result["status"] == "success":
                    search_result = result["data"]
                    break

            if not search_result:
                response["response"] = (
                    "I couldn't find any search results. Please try rephrasing your question."
                )
                session.add_message("assistant", response["response"])
                return response

            # Extract results
            results = search_result.get("results", [])

            # Calculate RTD status and freshness for results
            rtd_status = self.rtd_manager.get_rtd_status(message, results, category)
            response["rtd_status"] = rtd_status

            # Add freshness info to each result
            for i, result in enumerate(results):
                freshness = self.rtd_manager.calculate_freshness(result)
                result["freshness"] = freshness

            response["search_results"] = results[:10]

            # Update goals
            session.update_goal("Finding relevant sources", 90)
            session.update_goal("Analyzing information", 60)

            # AI Enhancement if available
            if self.ai_enhancer and self.ai_enhancer.is_enabled():
                response["thinking"] = "Analyzing search results with AI..."

                try:
                    enhancement = await self.ai_enhancer.enhance_results(message, results)

                    if enhancement.get("enhanced"):
                        ai_summary = enhancement.get("ai_summary", "")
                        insights = enhancement.get("key_insights", [])
                        sources = enhancement.get("recommended_sources", [])

                        # Build comprehensive response
                        response_text = f"{ai_summary}\n\n"

                        if insights:
                            response_text += "**Key Insights:**\n"
                            for i, insight in enumerate(insights[:5], 1):
                                response_text += f"{i}. {insight}\n"
                            response_text += "\n"

                        if sources:
                            response_text += "**Top Sources:**\n"
                            for i, source in enumerate(sources[:3], 1):
                                response_text += f"{i}. [{source.get('title', 'Source')}]({source.get('url', '#')})\n"
                                response_text += f"   {source.get('reason', '')}\n"

                        response["response"] = response_text
                        response["ai_summary"] = ai_summary

                        # Update user model based on query complexity
                        if len(message.split()) > 10:
                            session.update_user_model(
                                "Technical Knowledge",
                                session.user_model["Technical Knowledge"]
                                + self.USER_MODEL_INCREMENT_LONG_QUERY,
                            )
                        session.update_user_model(
                            "Research Interest",
                            session.user_model["Research Interest"]
                            + self.USER_MODEL_INCREMENT_RESEARCH,
                        )

                        # Complete goals
                        session.update_goal("Analyzing information", 100)
                        session.update_goal("Providing comprehensive answer", 100)

                    else:
                        # Fallback to basic summary
                        response["response"] = self._create_basic_summary(message, results)

                except Exception as e:
                    logger.error(f"AI enhancement failed: {e}")
                    response["response"] = self._create_basic_summary(message, results)
            else:
                # No AI available - basic summary
                response["response"] = self._create_basic_summary(message, results)

            session.add_message("assistant", response["response"])

        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            response["response"] = f"I encountered an error processing your message: {str(e)}"
            session.add_message("assistant", response["response"])

        response["goals"] = session.goals
        response["user_model"] = session.user_model
        return response

    def _create_basic_summary(self, query: str, results: list[dict]) -> str:
        """Create a basic summary when AI is not available."""
        if not results:
            return "I couldn't find any results for your query."

        summary = f"I found {len(results)} results for your query.\n\n"
        summary += "**Top Results:**\n"

        for i, result in enumerate(results[:5], 1):
            title = result.get("title", "No title")
            url = result.get("url", "")
            content = result.get("content", "")[:150]
            summary += f"{i}. **{title}**\n"
            summary += f"   {content}...\n"
            summary += f"   [View source]({url})\n\n"

        return summary


# Initialize manager
manager = DashboardManager()


# WebSocket connection manager
async def broadcast_health_update(data: dict):
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
    """Serve the chat interface."""
    return FileResponse("src/searxng_mcp/static/chat.html")


@app.get("/dashboard")
async def dashboard():
    """Serve the monitoring dashboard."""
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


@app.get("/api/context/stats")
async def get_context_stats():
    """Get context management statistics for all active sessions."""
    stats = {"total_sessions": len(manager.chat_sessions), "sessions": {}}

    for session_id, session in manager.chat_sessions.items():
        stats["sessions"][session_id] = session.get_context_stats()

    return stats


@app.get("/api/rtd/status")
async def get_rtd_status():
    """Get RTD manager status and capabilities."""
    return {
        "enabled": True,
        "freshness_thresholds": {
            "live": "< 1 minute",
            "fresh": "< 1 hour",
            "recent": "< 1 day",
            "stale": "< 1 week",
            "old": "> 1 week",
        },
        "refresh_intervals": {
            "live": "30 seconds",
            "dynamic": "5 minutes",
            "regular": "15 minutes",
            "static": "1 hour",
        },
        "time_sensitive_keywords": manager.rtd_manager.TIME_SENSITIVE_KEYWORDS[:10],
        "high_freshness_categories": manager.rtd_manager.HIGH_FRESHNESS_CATEGORIES,
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


@app.post("/api/chat")
async def chat_endpoint(message: ChatMessage):
    """Process a chat message via REST API."""
    session = manager.get_or_create_session()
    result = await manager.process_chat_message(
        session, message.message, message.language, message.category
    )
    return result


@app.post("/api/repl/execute")
async def repl_execute_endpoint(request: REPLExecutionRequest):
    """
    Execute code in REPL environment.

    This is the revolutionary RLM REPL system that enables:
    - LLM-generated code for context navigation
    - Recursive sub-LLM calls
    - Semantic search and aggregation
    - Zero information loss with infinite context
    """
    session = manager.get_or_create_session(request.session_id)

    try:
        result = session.repl_manager.execute_code(request.code, request.description)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"REPL execution error: {e}", exc_info=True)
        return {"status": "error", "error": str(e), "error_type": type(e).__name__}


@app.get("/api/repl/context/{session_id}")
async def repl_get_context(session_id: str):
    """Get REPL context for a session."""
    session = manager.chat_sessions.get(session_id)
    if not session:
        return {"status": "error", "error": "Session not found"}

    return {"status": "success", "context": session.repl_manager.get_context()}


@app.get("/api/repl/stats/{session_id}")
async def repl_get_stats(session_id: str):
    """Get REPL execution statistics."""
    session = manager.chat_sessions.get(session_id)
    if not session:
        return {"status": "error", "error": "Session not found"}

    return {"status": "success", "stats": session.repl_manager.get_stats()}


@app.post("/api/repl/generate-code")
async def repl_generate_code(request: dict):
    """
    Generate Python code for a natural language query.
    This is where LLM would generate navigation code.
    """
    session_id = request.get("session_id")
    query = request.get("query", "")

    session = manager.get_or_create_session(session_id)

    try:
        code = session.repl_manager.generate_navigation_code(query)
        return {"status": "success", "code": code, "description": f"Generated code for: {query}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()
    session_id = str(uuid.uuid4())
    session = manager.get_or_create_session(session_id)

    try:
        # Send welcome message
        await websocket.send_json({"type": "connected", "session_id": session_id})

        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")

            if message_type == "chat":
                message = data.get("message", "")
                language = data.get("language", "en")
                category = data.get("category", "general")

                # Send thinking status
                await websocket.send_json(
                    {"type": "thinking", "content": "Processing your query..."}
                )

                # Send monologue update
                await websocket.send_json(
                    {"type": "monologue", "content": f"Analyzing query: '{message}'"}
                )

                # Process message
                result = await manager.process_chat_message(session, message, language, category)

                # Send thinking update
                if result.get("thinking"):
                    await websocket.send_json({"type": "thinking", "content": result["thinking"]})
                    await websocket.send_json({"type": "monologue", "content": result["thinking"]})

                # Send search results
                if result.get("search_results"):
                    await websocket.send_json(
                        {"type": "search_results", "content": result["search_results"]}
                    )
                    await websocket.send_json(
                        {
                            "type": "monologue",
                            "content": f"Found {len(result['search_results'])} relevant sources",
                        }
                    )

                # Send context stats
                if result.get("context_stats"):
                    await websocket.send_json(
                        {"type": "context_stats", "content": result["context_stats"]}
                    )

                # Send RTD status
                if result.get("rtd_status"):
                    await websocket.send_json(
                        {"type": "rtd_status", "content": result["rtd_status"]}
                    )

                # Send goals update
                if result.get("goals"):
                    await websocket.send_json({"type": "goal_update", "content": result["goals"]})

                # Send user model update
                if result.get("user_model"):
                    await websocket.send_json(
                        {"type": "user_model_update", "content": result["user_model"]}
                    )

                # Send final response
                if result.get("response"):
                    await websocket.send_json({"type": "response", "content": result["response"]})
                    await websocket.send_json(
                        {"type": "monologue", "content": "Response generated successfully"}
                    )

            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        logger.info(f"Chat session {session_id} disconnected")
    except Exception as e:
        logger.error(f"Chat WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({"type": "error", "content": f"Server error: {str(e)}"})
        except Exception as send_error:
            logger.error(f"Failed to send error to client: {send_error}")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        # Send initial data
        results = await manager.check_all_instances()
        await websocket.send_text(
            json.dumps(
                {
                    "type": "health_update",
                    "data": results,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
        )

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
    import uvicorn  # type: ignore[import-not-found]

    print("🚀 Starting SearXNG MCP Dashboard...")
    print("📊 Dashboard: http://localhost:8765")
    print("📚 API Docs: http://localhost:8765/docs")
    print()

    uvicorn.run(app, host="0.0.0.0", port=8765, log_level="info")
