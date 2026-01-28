"""
Comprehensive tests for dashboard, AI enhancer, and wizard.
"""

import os
import pytest
from unittest.mock import Mock, patch, AsyncMock


# Test AI Enhancer
class TestAIEnhancer:
    """Tests for AI enhancement module."""

    def test_ai_enhancer_imports(self):
        """Test AI enhancer module imports."""
        from searxng_mcp.ai_enhancer import AIEnhancer, get_ai_enhancer
        assert AIEnhancer is not None
        assert get_ai_enhancer is not None

    def test_ai_enhancer_instantiation(self):
        """Test AIEnhancer can be instantiated."""
        from searxng_mcp.ai_enhancer import AIEnhancer
        enhancer = AIEnhancer()
        assert enhancer is not None

    def test_ai_enhancer_disabled_by_default(self):
        """Test AI enhancer is disabled without config."""
        from searxng_mcp.ai_enhancer import AIEnhancer
        enhancer = AIEnhancer()
        assert not enhancer.is_enabled()

    def test_openrouter_provider(self):
        """Test OpenRouter provider configuration."""
        from searxng_mcp.ai_enhancer import AIEnhancer
        os.environ["SEARXNG_AI_PROVIDER"] = "openrouter"
        os.environ["SEARXNG_AI_API_KEY"] = "test_key"
        
        enhancer = AIEnhancer()
        assert enhancer.provider == "openrouter"
        assert enhancer.model == "mistralai/mistral-large-2512"
        assert "openrouter.ai" in enhancer.config.get("base_url", "")
        
        del os.environ["SEARXNG_AI_PROVIDER"]
        del os.environ["SEARXNG_AI_API_KEY"]

    def test_ollama_cloud_provider(self):
        """Test Ollama Cloud provider configuration."""
        from searxng_mcp.ai_enhancer import AIEnhancer
        os.environ["SEARXNG_AI_PROVIDER"] = "ollama"
        os.environ["SEARXNG_AI_API_KEY"] = "test_key"
        
        enhancer = AIEnhancer()
        assert enhancer.provider == "ollama"
        assert enhancer.model == "mistral-large-3:675b-cloud"
        assert "ollama.com" in enhancer.config.get("base_url", "")
        
        del os.environ["SEARXNG_AI_PROVIDER"]
        del os.environ["SEARXNG_AI_API_KEY"]

    def test_gemini_provider(self):
        """Test Gemini provider configuration."""
        from searxng_mcp.ai_enhancer import AIEnhancer
        os.environ["SEARXNG_AI_PROVIDER"] = "gemini"
        os.environ["SEARXNG_AI_API_KEY"] = "test_key"
        
        enhancer = AIEnhancer()
        assert enhancer.provider == "gemini"
        assert "googleapis.com" in enhancer.config.get("base_url", "")
        
        del os.environ["SEARXNG_AI_PROVIDER"]
        del os.environ["SEARXNG_AI_API_KEY"]

    def test_prepare_context(self):
        """Test context preparation from results."""
        from searxng_mcp.ai_enhancer import AIEnhancer
        enhancer = AIEnhancer()
        
        results = [
            {"title": "Test 1", "url": "http://test1.com", "content": "Content 1"},
            {"title": "Test 2", "url": "http://test2.com", "content": "Content 2"},
        ]
        
        context = enhancer._prepare_context("test query", results)
        assert "test query" in context
        assert "Test 1" in context
        assert "Test 2" in context


# Test Dashboard
class TestDashboard:
    """Tests for dashboard module."""

    def test_dashboard_imports(self):
        """Test dashboard module imports."""
        from searxng_mcp.dashboard import app, DashboardManager
        assert app is not None
        assert DashboardManager is not None

    def test_dashboard_manager_instantiation(self):
        """Test DashboardManager can be instantiated."""
        from searxng_mcp.dashboard import DashboardManager
        manager = DashboardManager()
        assert manager is not None

    def test_dashboard_manager_config(self):
        """Test DashboardManager loads configuration."""
        from searxng_mcp.dashboard import DashboardManager
        manager = DashboardManager()
        assert len(manager.instances) > 0
        assert manager.timeout > 0
        assert isinstance(manager.search_stats, dict)

    def test_fastapi_app(self):
        """Test FastAPI app is created."""
        from searxng_mcp.dashboard import app
        assert app is not None
        assert len(app.routes) > 0

    def test_dashboard_routes(self):
        """Test dashboard has required routes."""
        from searxng_mcp.dashboard import app
        route_paths = [route.path for route in app.routes]
        assert "/" in route_paths
        assert "/api/health" in route_paths
        assert "/api/config" in route_paths
        assert "/api/stats" in route_paths
        assert "/ws" in route_paths


# Test Wizard
class TestWizard:
    """Tests for setup wizard."""

    def test_wizard_imports(self):
        """Test wizard module imports."""
        import wizard
        assert wizard is not None

    def test_wizard_setup_class(self):
        """Test SetupWizard class exists."""
        from wizard import SetupWizard
        assert SetupWizard is not None

    def test_wizard_colors_class(self):
        """Test Colors class exists."""
        from wizard import Colors
        assert Colors is not None

    def test_wizard_instantiation(self):
        """Test SetupWizard can be instantiated."""
        from wizard import SetupWizard
        wizard_instance = SetupWizard()
        assert wizard_instance is not None
        assert wizard_instance.config == {}


# Test Integration
class TestIntegration:
    """Tests for integration between components."""

    def test_search_tool_exists(self):
        """Test search tool is accessible."""
        from searxng_mcp.server import search
        assert search is not None

    def test_search_tool_has_ai_parameter(self):
        """Test search tool has ai_enhance parameter."""
        from searxng_mcp.server import search
        import inspect
        
        # Get the function that FastMCP wraps
        if hasattr(search, 'fn'):
            func = search.fn
        else:
            func = search
        
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        assert "ai_enhance" in params, f"ai_enhance not in {params}"

    def test_mcp_tools_accessible(self):
        """Test all MCP tools are accessible."""
        from searxng_mcp.server import search, list_categories, get_instances
        assert search is not None
        assert list_categories is not None
        assert get_instances is not None

    def test_ai_enhancer_integration(self):
        """Test AI enhancer can be imported from server context."""
        from searxng_mcp.ai_enhancer import get_ai_enhancer
        enhancer = get_ai_enhancer()
        assert enhancer is not None


# Test Health Check
class TestHealthCheck:
    """Tests for health check module."""

    def test_health_check_imports(self):
        """Test health check module imports."""
        from searxng_mcp.health import HealthChecker
        assert HealthChecker is not None

    def test_health_checker_instantiation(self):
        """Test HealthChecker can be instantiated."""
        from searxng_mcp.health import HealthChecker
        checker = HealthChecker()
        assert checker is not None

    def test_health_checker_config(self):
        """Test HealthChecker loads configuration."""
        from searxng_mcp.health import HealthChecker
        checker = HealthChecker()
        assert len(checker.instances) > 0
        assert checker.timeout > 0


# Test File Structure
class TestFileStructure:
    """Tests for file structure and assets."""

    def test_wizard_file_exists(self):
        """Test wizard.py exists."""
        from pathlib import Path
        assert Path("wizard.py").exists()

    def test_dashboard_file_exists(self):
        """Test dashboard.py exists."""
        from pathlib import Path
        assert Path("src/searxng_mcp/dashboard.py").exists()

    def test_ai_enhancer_file_exists(self):
        """Test ai_enhancer.py exists."""
        from pathlib import Path
        assert Path("src/searxng_mcp/ai_enhancer.py").exists()

    def test_dashboard_html_exists(self):
        """Test dashboard.html exists."""
        from pathlib import Path
        assert Path("src/searxng_mcp/static/dashboard.html").exists()

    def test_dashboard_md_exists(self):
        """Test DASHBOARD.md exists."""
        from pathlib import Path
        assert Path("DASHBOARD.md").exists()


# Test Documentation
class TestDocumentation:
    """Tests for documentation completeness."""

    def test_readme_mentions_dashboard(self):
        """Test README mentions dashboard."""
        from pathlib import Path
        content = Path("README.md").read_text().lower()
        assert "dashboard" in content

    def test_dashboard_md_has_features(self):
        """Test DASHBOARD.md has features section."""
        from pathlib import Path
        content = Path("DASHBOARD.md").read_text().lower()
        assert "features" in content

    def test_dashboard_md_has_api(self):
        """Test DASHBOARD.md has API documentation."""
        from pathlib import Path
        content = Path("DASHBOARD.md").read_text().lower()
        assert "api" in content

    def test_dashboard_md_has_setup(self):
        """Test DASHBOARD.md has setup instructions."""
        from pathlib import Path
        content = Path("DASHBOARD.md").read_text().lower()
        assert "setup" in content or "install" in content
