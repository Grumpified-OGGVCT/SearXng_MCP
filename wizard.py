#!/usr/bin/env python3
"""
Interactive Setup Wizard for SearXNG MCP Server

Guides users through configuration choices including:
- OS detection and platform-specific setup
- Online vs Local instance strategy
- Custom instance configuration
- Local SearXNG installation guidance
- .env file generation
"""

import os
import platform
import sys
import time
from pathlib import Path
from typing import List, Optional


class Colors:
    """ANSI color codes for terminal output."""

    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"

    @staticmethod
    def is_supported() -> bool:
        """Check if terminal supports colors."""
        return (
            hasattr(sys.stdout, "isatty")
            and sys.stdout.isatty()
            and os.getenv("TERM") != "dumb"
        )


class SetupWizard:
    """Interactive setup wizard for SearXNG MCP Server."""

    def __init__(self):
        self.colors_enabled = Colors.is_supported()
        self.config = {}
        self.project_root = Path(__file__).parent.absolute()

    def color(self, text: str, color: str) -> str:
        """Apply color to text if colors are supported."""
        if self.colors_enabled:
            return f"{color}{text}{Colors.RESET}"
        return text

    def print_header(self, text: str):
        """Print a styled header."""
        print()
        print(self.color("=" * 80, Colors.CYAN))
        print(self.color(f"  {text}", Colors.BOLD + Colors.CYAN))
        print(self.color("=" * 80, Colors.CYAN))
        print()

    def print_section(self, text: str):
        """Print a section header."""
        print()
        print(self.color(f">>> {text}", Colors.BLUE + Colors.BOLD))
        print()

    def print_info(self, text: str):
        """Print information text."""
        print(self.color(f"ℹ  {text}", Colors.CYAN))

    def print_success(self, text: str):
        """Print success message."""
        print(self.color(f"✓ {text}", Colors.GREEN))

    def print_warning(self, text: str):
        """Print warning message."""
        print(self.color(f"⚠ {text}", Colors.YELLOW))

    def print_error(self, text: str):
        """Print error message."""
        print(self.color(f"✗ {text}", Colors.RED))

    def prompt(self, question: str, default: Optional[str] = None) -> str:
        """Prompt user for input with optional default."""
        if default:
            prompt_text = f"{question} [{default}]: "
        else:
            prompt_text = f"{question}: "

        try:
            response = input(self.color(prompt_text, Colors.YELLOW)).strip()
            return response if response else (default or "")
        except (KeyboardInterrupt, EOFError):
            print()
            self.print_warning("Setup cancelled by user")
            sys.exit(0)

    def prompt_yes_no(self, question: str, default: bool = True) -> bool:
        """Prompt user for yes/no question."""
        default_str = "Y/n" if default else "y/N"
        response = self.prompt(f"{question} ({default_str})", "").lower()

        if not response:
            return default
        return response in ["y", "yes"]

    def prompt_choice(
        self, question: str, choices: List[tuple], default: int = 0
    ) -> int:
        """Prompt user to choose from a list of options."""
        print(self.color(question, Colors.YELLOW))
        for i, (label, description) in enumerate(choices, 1):
            print(f"  {i}. {self.color(label, Colors.BOLD)}")
            if description:
                print(f"     {self.color(description, Colors.CYAN)}")

        while True:
            try:
                response = input(
                    self.color(f"\nEnter choice [1-{len(choices)}] (default: {default + 1}): ", Colors.YELLOW)
                ).strip()

                if not response:
                    return default

                choice = int(response) - 1
                if 0 <= choice < len(choices):
                    return choice

                self.print_error(f"Please enter a number between 1 and {len(choices)}")
            except ValueError:
                self.print_error("Please enter a valid number")
            except (KeyboardInterrupt, EOFError):
                print()
                self.print_warning("Setup cancelled by user")
                sys.exit(0)

    def detect_os(self):
        """Detect operating system."""
        self.print_section("Detecting Your System")

        system = platform.system()
        machine = platform.machine()
        python_version = platform.python_version()

        self.print_info(f"Operating System: {system}")
        self.print_info(f"Architecture: {machine}")
        self.print_info(f"Python Version: {python_version}")

        # Store in config
        self.config["os"] = system.lower()
        self.config["arch"] = machine.lower()
        self.config["python_version"] = python_version

        # Check Python version
        if sys.version_info < (3, 10):
            self.print_error(f"Python 3.10+ required (you have {python_version})")
            self.print_info("Please upgrade Python before continuing")
            sys.exit(1)
        else:
            self.print_success(f"Python {python_version} is compatible")

    def choose_instance_strategy(self):
        """Guide user through instance strategy selection."""
        self.print_section("Choose Your Instance Strategy")

        self.print_info("SearXNG MCP can work with:")
        self.print_info("  • Public SearXNG instances (hosted by community)")
        self.print_info("  • Your own local SearXNG instance")
        self.print_info("  • A combination of both (recommended)")
        print()

        choices = [
            (
                "Online Only (Easiest)",
                "Use public instances only. No local setup required.",
            ),
            (
                "Local + Online (Recommended)",
                "Use public instances with local fallback for reliability.",
            ),
            (
                "Local Only",
                "Use only your local instance. Requires local SearXNG setup.",
            ),
            (
                "Custom Configuration",
                "Manually specify instance URLs and priorities.",
            ),
        ]

        choice = self.prompt_choice(
            "Select your preferred setup strategy:", choices, default=1
        )

        strategy_map = {
            0: "online_only",
            1: "local_online",
            2: "local_only",
            3: "custom",
        }

        self.config["strategy"] = strategy_map[choice]
        self.print_success(f"Selected: {choices[choice][0]}")

    def configure_online_instances(self):
        """Configure online instance preferences."""
        self.print_section("Configuring Online Instances")

        default_instances = [
            "https://search.sapti.me",
            "https://searx.be",
            "https://search.bus-hit.me",
            "https://search.mdosch.de",
            "https://searx.tiekoetter.com",
        ]

        self.print_info("Default public instances:")
        for i, instance in enumerate(default_instances, 1):
            print(f"  {i}. {instance}")
        print()

        use_defaults = self.prompt_yes_no(
            "Use default public instances?", default=True
        )

        if use_defaults:
            self.config["instances"] = default_instances
            self.print_success("Using default instances")
        else:
            custom_instances = []
            self.print_info("Enter custom instance URLs (one per line, empty line to finish):")

            while True:
                url = self.prompt("Instance URL", "").strip()
                if not url:
                    break
                if url.startswith("http://") or url.startswith("https://"):
                    custom_instances.append(url)
                    self.print_success(f"Added: {url}")
                else:
                    self.print_error("URL must start with http:// or https://")

            if custom_instances:
                self.config["instances"] = custom_instances
            else:
                self.print_warning("No instances added, using defaults")
                self.config["instances"] = default_instances

    def configure_local_instance(self):
        """Configure local SearXNG instance."""
        self.print_section("Configuring Local SearXNG Instance")

        has_local = self.prompt_yes_no(
            "Do you have a local SearXNG instance running?", default=False
        )

        if has_local:
            default_url = "http://localhost:8888"
            local_url = self.prompt(
                "Enter your local SearXNG URL", default=default_url
            )
            self.config["local_instance"] = local_url
            self.print_success(f"Local instance configured: {local_url}")

            # Test connection (optional)
            test = self.prompt_yes_no(
                "Test connection to local instance now?", default=True
            )
            if test:
                self.test_local_connection(local_url)

        else:
            self.print_info("You can install SearXNG locally for better reliability")
            install_help = self.prompt_yes_no(
                "Show local installation instructions?", default=False
            )

            if install_help:
                self.show_local_installation_guide()

            self.config["local_instance"] = None

    def test_local_connection(self, url: str):
        """Test connection to local SearXNG instance."""
        self.print_info(f"Testing connection to {url}...")

        try:
            import httpx

            response = httpx.get(f"{url}/search", params={"q": "test", "format": "json"}, timeout=5.0)
            if response.status_code == 200:
                self.print_success("✓ Local instance is reachable and responding!")
            else:
                self.print_warning(
                    f"Local instance responded with status {response.status_code}"
                )
        except ImportError:
            self.print_warning("httpx not installed, skipping connection test")
        except Exception as e:
            self.print_error(f"Failed to connect: {e}")
            self.print_info("Make sure your local SearXNG instance is running")

    def show_local_installation_guide(self):
        """Show platform-specific local SearXNG installation guide."""
        self.print_section("Local SearXNG Installation Guide")

        os_type = self.config.get("os", "").lower()

        if os_type == "linux":
            self.show_linux_install_guide()
        elif os_type == "darwin":
            self.show_macos_install_guide()
        elif os_type == "windows":
            self.show_windows_install_guide()
        else:
            self.show_generic_install_guide()

        print()
        self.print_info("After installation, run this setup wizard again")
        print()

    def show_linux_install_guide(self):
        """Show Linux installation guide."""
        print(self.color("\n📦 Docker Installation (Recommended):", Colors.BOLD))
        print("""
1. Install Docker:
   sudo apt update && sudo apt install docker.io docker-compose

2. Create docker-compose.yml:
   mkdir searxng && cd searxng
   wget https://raw.githubusercontent.com/searxng/searxng-docker/master/docker-compose.yaml

3. Start SearXNG:
   docker-compose up -d

4. Access at: http://localhost:8888
        """)

        print(self.color("\n🔧 Alternative: Manual Installation:", Colors.BOLD))
        print("""
1. Clone repository:
   git clone https://github.com/searxng/searxng.git
   cd searxng

2. Install dependencies:
   pip install -r requirements.txt

3. Run:
   python -m searx.webapp
        """)

    def show_macos_install_guide(self):
        """Show macOS installation guide."""
        print(self.color("\n📦 Docker Installation (Recommended):", Colors.BOLD))
        print("""
1. Install Docker Desktop:
   brew install --cask docker

2. Create docker-compose.yml:
   mkdir searxng && cd searxng
   curl -O https://raw.githubusercontent.com/searxng/searxng-docker/master/docker-compose.yaml

3. Start SearXNG:
   docker-compose up -d

4. Access at: http://localhost:8888
        """)

    def show_windows_install_guide(self):
        """Show Windows installation guide."""
        print(self.color("\n📦 Docker Installation (Recommended):", Colors.BOLD))
        print("""
1. Install Docker Desktop:
   Download from: https://www.docker.com/products/docker-desktop

2. Create docker-compose.yml in a new folder

3. Start PowerShell in that folder and run:
   docker-compose up -d

4. Access at: http://localhost:8888
        """)

        print(self.color("\n🔧 Alternative: WSL Installation:", Colors.BOLD))
        print("""
1. Enable WSL2:
   wsl --install

2. Follow Linux instructions in WSL
        """)

    def show_generic_install_guide(self):
        """Show generic installation guide."""
        print(self.color("\n📖 General Installation Guide:", Colors.BOLD))
        print("""
Visit the official SearXNG documentation:
https://docs.searxng.org/admin/installation.html

Docker is recommended for all platforms:
https://docs.searxng.org/admin/installation-docker.html
        """)

    def configure_ai_enhancement(self):
        """Configure AI-powered search enhancement."""
        self.print_section("AI-Powered Search Enhancement (Optional)")
        
        self.print_info("SearXNG MCP can enhance search results with AI summaries.")
        self.print_info("This provides:")
        self.print_info("  • Comprehensive 3-5 paragraph analysis")
        self.print_info("  • 5-7 detailed key insights")
        self.print_info("  • Source recommendations")
        self.print_info("  • Takes 6-18 seconds per search")
        print()
        
        enable_ai = self.prompt_yes_no(
            "Enable AI-powered enhancement?", default=False
        )
        
        if not enable_ai:
            self.config["ai_enabled"] = False
            self.print_info("AI enhancement disabled. You can enable it later.")
            return
        
        self.config["ai_enabled"] = True
        
        # Choose provider
        self.print_info("\nAvailable AI providers:")
        print()
        
        providers = [
            (
                "OpenRouter",
                "Most reliable. Model: google/gemini-2.0-flash-exp\n     Get free API key: https://openrouter.ai/keys",
            ),
            (
                "Ollama Cloud",
                "Newest model. Model: gemini-3-flash-preview:cloud\n     Get API key: https://ollama.com/settings/keys",
            ),
            (
                "Google Gemini",
                "Direct from Google. Auto-detects latest Flash model\n     Get API key: https://aistudio.google.com/app/apikey",
            ),
        ]
        
        choice = self.prompt_choice(
            "Select your AI provider:", providers, default=0
        )
        
        provider_map = {
            0: "openrouter",
            1: "ollama",
            2: "gemini",
        }
        
        provider = provider_map[choice]
        self.config["ai_provider"] = provider
        self.print_success(f"Selected: {providers[choice][0]}")
        print()
        
        # Get API key
        self.print_info(f"You'll need an API key from {providers[choice][0]}")
        self.print_info(f"Get it here: {providers[choice][1].split('Get')[1].strip() if 'https://' in providers[choice][1] else 'See documentation'}")
        print()
        
        api_key = self.prompt(f"Enter your {providers[choice][0]} API key", "")
        
        if api_key:
            self.config["ai_api_key"] = api_key
            self.print_success("API key saved!")
            
            # Test connection
            test = self.prompt_yes_no(
                "Test AI connection now?", default=True
            )
            if test:
                self.test_ai_connection(provider, api_key)
        else:
            self.print_warning("No API key provided. AI enhancement will be disabled.")
            self.config["ai_enabled"] = False
    
    def test_ai_connection(self, provider: str, api_key: str):
        """Test AI provider connection."""
        self.print_info(f"Testing {provider} connection...")
        
        try:
            import httpx
            
            # Simple connectivity test based on provider
            if provider == "openrouter":
                response = httpx.get(
                    "https://openrouter.ai/api/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0
                )
            elif provider == "ollama":
                response = httpx.get(
                    "https://ollama.com/api/tags",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0
                )
            elif provider == "gemini":
                response = httpx.get(
                    f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
                    timeout=10.0
                )
            
            if response.status_code == 200:
                self.print_success("✓ AI provider connection successful!")
            else:
                self.print_warning(f"Connection returned status {response.status_code}")
                self.print_warning("Please verify your API key is correct")
                
        except ImportError:
            self.print_warning("httpx not installed, skipping connection test")
        except Exception as e:
            self.print_error(f"Connection test failed: {e}")
            self.print_warning("Please verify your API key is correct")
    
    def configure_privacy_settings(self):
        """Configure privacy and tracking preferences."""
        self.print_section("Privacy & Tracking Settings")
        
        self.print_info("SearXNG MCP can collect usage metrics for:")
        self.print_info("  • Monitoring performance and errors")
        self.print_info("  • Tracking API costs and usage")
        self.print_info("  • Improving service reliability")
        print()
        self.print_info(self.color("IMPORTANT:", Colors.BOLD) + " What is tracked:")
        self.print_info("  ✓ Request counts and categories")
        self.print_info("  ✓ Response times and success rates")
        self.print_info("  ✓ Cost estimates for AI usage")
        self.print_info("  ✓ Error types (NO error details)")
        print()
        self.print_info(self.color("NOT tracked:", Colors.BOLD))
        self.print_info("  ✗ Your actual search queries")
        self.print_info("  ✗ Search results or content")
        self.print_info("  ✗ Personal information")
        self.print_info("  ✗ IP addresses or identifiers")
        print()
        self.print_info("All data stays LOCAL on your machine (no cloud upload).")
        print()
        
        enable_metrics = self.prompt_yes_no(
            "Enable usage metrics collection?", default=True
        )
        
        if enable_metrics:
            self.config["metrics_enabled"] = True
            self.print_success("✓ Metrics enabled (stored locally in ~/.searxng_mcp/metrics)")
            print()
            
            # Ask about query logging separately
            self.print_info("For debugging, partial query text can be logged (first 50 chars only).")
            log_queries = self.prompt_yes_no(
                "Enable partial query logging for debugging?", default=False
            )
            self.config["log_queries"] = log_queries
            
            if log_queries:
                self.print_warning("⚠ Partial queries will be logged locally for debugging")
            else:
                self.print_success("✓ Query logging disabled (maximum privacy)")
        else:
            self.config["metrics_enabled"] = False
            self.config["log_queries"] = False
            self.print_success("✓ All tracking disabled (maximum privacy)")
        
        print()
        self.print_info("You can change these settings anytime in your .env file:")
        self.print_info("  SEARXNG_METRICS_ENABLED=true/false")
        self.print_info("  SEARXNG_LOG_QUERIES=true/false")
    
    def configure_advanced_settings(self):
        """Configure advanced settings."""
        self.print_section("Advanced Settings (Optional)")

        configure_advanced = self.prompt_yes_no(
            "Configure advanced settings?", default=False
        )

        if not configure_advanced:
            self.config["timeout"] = 5.0
            self.config["local_timeout"] = 15.0
            return

        # Timeout settings
        timeout = self.prompt("Request timeout for online instances (seconds)", "5.0")
        try:
            self.config["timeout"] = float(timeout)
        except ValueError:
            self.config["timeout"] = 5.0
            self.print_warning("Invalid timeout, using default: 5.0")

        if self.config.get("local_instance"):
            local_timeout = self.prompt(
                "Request timeout for local instance (seconds)", "15.0"
            )
            try:
                self.config["local_timeout"] = float(local_timeout)
            except ValueError:
                self.config["local_timeout"] = 15.0
                self.print_warning("Invalid timeout, using default: 15.0")

    def generate_env_file(self):
        """Generate .env configuration file."""
        self.print_section("Generating Configuration")

        env_path = self.project_root / ".env"

        if env_path.exists():
            overwrite = self.prompt_yes_no(
                ".env file already exists. Overwrite?", default=False
            )
            if not overwrite:
                self.print_warning("Keeping existing .env file")
                return

        # Build .env content
        lines = [
            "# SearXNG MCP Server Configuration",
            "# Generated by setup wizard",
            f"# Created: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "# ===== SearXNG Instances =====",
        ]

        # Instance configuration
        if self.config.get("instances"):
            instances_str = ",".join(self.config["instances"])
            lines.append(f"SEARXNG_INSTANCES={instances_str}")

        if self.config.get("local_instance"):
            lines.append(f"SEARXNG_LOCAL_INSTANCE={self.config['local_instance']}")

        # Timeout configuration
        if "timeout" in self.config:
            lines.append(f"SEARXNG_TIMEOUT={self.config['timeout']}")

        if "local_timeout" in self.config:
            lines.append(f"SEARXNG_LOCAL_TIMEOUT={self.config['local_timeout']}")

        lines.append("")
        
        # AI Enhancement configuration
        lines.append("# ===== AI Enhancement (Optional) =====")
        if self.config.get("ai_enabled"):
            lines.append(f"SEARXNG_AI_PROVIDER={self.config['ai_provider']}")
            lines.append(f"SEARXNG_AI_API_KEY={self.config['ai_api_key']}")
            
            # Add model info based on provider
            if self.config['ai_provider'] == "openrouter":
                lines.append("# SEARXNG_AI_MODEL=google/gemini-2.0-flash-exp  # Default")
            elif self.config['ai_provider'] == "ollama":
                lines.append("# SEARXNG_AI_MODEL=gemini-3-flash-preview:cloud  # Default")
            elif self.config['ai_provider'] == "gemini":
                lines.append("# SEARXNG_AI_MODEL=gemini-2.0-flash-exp  # Auto-detected")
        else:
            lines.append("# SEARXNG_AI_PROVIDER=openrouter  # Options: openrouter, ollama, gemini")
            lines.append("# SEARXNG_AI_API_KEY=your_api_key_here")
            lines.append("# SEARXNG_AI_MODEL=  # Leave empty for provider defaults")
        
        lines.append("")
        
        # Privacy configuration
        lines.append("# ===== Privacy & Metrics =====")
        metrics_enabled = self.config.get("metrics_enabled", True)
        log_queries = self.config.get("log_queries", False)
        
        lines.append(f"SEARXNG_METRICS_ENABLED={'true' if metrics_enabled else 'false'}")
        lines.append(f"SEARXNG_LOG_QUERIES={'true' if log_queries else 'false'}")
        lines.append("# Metrics are stored locally in ~/.searxng_mcp/metrics")
        lines.append("# No data is uploaded to any server")
        
        lines.append("")

        # Write file
        try:
            with open(env_path, "w") as f:
                f.write("\n".join(lines))
            self.print_success(f"Configuration saved to {env_path}")
        except Exception as e:
            self.print_error(f"Failed to write .env file: {e}")

    def show_next_steps(self):
        """Show next steps after setup."""
        self.print_section("Setup Complete! 🎉")

        print("Next steps:")
        print()
        print(self.color("1. Review your configuration:", Colors.BOLD))
        print(f"   {self.project_root / '.env'}")
        print()

        print(self.color("2. Start the MCP server:", Colors.BOLD))
        if self.config.get("os") == "windows":
            print("   run.bat")
        else:
            print("   ./run.sh")
        print()

        print(self.color("3. Configure your MCP client:", Colors.BOLD))
        print("   Add this server to Claude Desktop or your MCP client")
        print("   See README.md for configuration examples")
        print()

        print(self.color("4. Test the setup:", Colors.BOLD))
        print("   python -m searxng_mcp.health")
        print()

        self.print_info("For help and documentation, see:")
        self.print_info("  • README.md - Main documentation")
        self.print_info("  • QUICKSTART.md - Quick start guide")
        self.print_info("  • INSTALL.md - Detailed installation guide")

    def run(self):
        """Run the setup wizard."""
        try:
            self.print_header("SearXNG MCP Server - Interactive Setup Wizard")

            self.print_info("This wizard will guide you through setting up SearXNG MCP.")
            self.print_info("You can press Ctrl+C at any time to cancel.")
            print()

            # Run setup steps
            self.detect_os()
            self.choose_instance_strategy()

            strategy = self.config.get("strategy")

            if strategy in ["online_only", "local_online", "custom"]:
                self.configure_online_instances()

            if strategy in ["local_only", "local_online"]:
                self.configure_local_instance()

            # NEW: AI Enhancement configuration
            self.configure_ai_enhancement()
            
            # NEW: Privacy settings
            self.configure_privacy_settings()

            self.configure_advanced_settings()
            self.generate_env_file()
            self.show_next_steps()

        except KeyboardInterrupt:
            print()
            self.print_warning("\n\nSetup interrupted by user")
            sys.exit(1)
        except Exception as e:
            self.print_error(f"\n\nUnexpected error: {e}")
            import traceback

            traceback.print_exc()
            sys.exit(1)


def main():
    """Main entry point."""
    wizard = SetupWizard()
    wizard.run()


if __name__ == "__main__":
    main()
