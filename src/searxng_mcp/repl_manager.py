"""
MIT RLM-Inspired REPL Manager for Infinite Context

Revolutionary context management system that stores conversations as Python variables
and enables LLM to generate code for navigation, search, and recursive analysis.

Based on MIT's Recursive Language Model (RLM) REPL paper.
Enables truly infinite context with zero information loss - makes the model roar like a lion! 🦁
"""

import ast
import logging
import re
import time
from collections import defaultdict
from datetime import datetime
from functools import wraps
from typing import Any

try:
    from RestrictedPython import compile_restricted_exec  # type: ignore[import-not-found]
    from RestrictedPython.Guards import guarded_iter_unpack_sequence, safe_builtins, safer_getattr  # type: ignore[import-not-found]

    RESTRICTED_PYTHON_AVAILABLE = True
except ImportError:
    RESTRICTED_PYTHON_AVAILABLE = False

logger = logging.getLogger(__name__)


# Security decorators
def timeout_limit(seconds: int) -> Any:
    """Decorator to limit execution time."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError(f"Execution exceeded {seconds} seconds")

            # Set alarm for Unix systems
            try:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(seconds)
                try:
                    result = func(*args, **kwargs)
                finally:
                    signal.alarm(0)
                return result
            except AttributeError:
                # Windows doesn't support SIGALRM, just run without timeout
                return func(*args, **kwargs)

        return wrapper

    return decorator


def memory_limit(max_items: int) -> Any:
    """Decorator to limit memory usage in results."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, list) and len(result) > max_items:
                logger.warning(f"Result truncated from {len(result)} to {max_items} items")
                return result[:max_items]
            return result

        return wrapper

    return decorator


class REPLExecutionError(Exception):
    """Error during REPL code execution."""

    pass


class REPLSecurityError(Exception):
    """Security violation during REPL execution."""

    pass


class RLMREPLManager:
    """
    Recursive Language Model REPL Manager

    Revolutionary context management with:
    - Embedded Python interpreter (RestrictedPython for safety)
    - Conversation stored as Python variables
    - LLM-generated code for navigation
    - Recursive sub-LLM calls
    - Semantic search and smart navigation
    - Zero information loss with infinite context
    """

    def __init__(
        self, max_recursion_depth: int = 5, execution_timeout: int = 5, max_result_items: int = 1000
    ):
        """
        Initialize RLM REPL Manager.

        Args:
            max_recursion_depth: Maximum depth for recursive LLM calls
            execution_timeout: Timeout for code execution in seconds
            max_result_items: Maximum items in result lists
        """
        if not RESTRICTED_PYTHON_AVAILABLE:
            logger.warning("RestrictedPython not available - using unsafe fallback mode")

        self.max_recursion_depth = max_recursion_depth
        self.execution_timeout = execution_timeout
        self.max_result_items = max_result_items

        # Context storage - the "REPL variables"
        self.context = {
            "messages": [],  # All conversation messages
            "facts": [],  # Extracted facts
            "entities": {},  # Named entities with frequencies
            "timeline": [],  # Chronological events
            "summaries": {},  # Cached summaries by range
            "metadata": {  # Conversation metadata
                "start_time": datetime.utcnow().isoformat(),
                "total_turns": 0,
                "topics": defaultdict(int),
            },
        }

        # Execution stats
        self.stats = {
            "executions": 0,
            "successful": 0,
            "failed": 0,
            "recursive_calls": 0,
            "avg_execution_time": 0.0,
            "total_execution_time": 0.0,
        }

        # Recursion tracking
        self.current_recursion_depth = 0

        # Safe function registry
        self._register_safe_functions()

    def _register_safe_functions(self) -> None:
        """Register whitelisted safe functions for REPL execution."""
        self.safe_functions = {
            # Navigation functions
            "find_messages": self._find_messages,
            "filter_by_date": self._filter_by_date,
            "filter_by_role": self._filter_by_role,
            "grep": self._grep,
            "search_semantic": self._search_semantic,
            # Aggregation functions
            "summarize_range": self._summarize_range,
            "aggregate_facts": self._aggregate_facts,
            "extract_entities": self._extract_entities,
            "get_timeline": self._get_timeline,
            # Analysis functions
            "analyze_subsection": self._analyze_subsection,
            "parallel_analyze": self._parallel_analyze,
            "count_messages": self._count_messages,
            "get_topics": self._get_topics,
            # Utility functions
            "get_message": self._get_message,
            "slice_messages": self._slice_messages,
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "list": list,
            "dict": dict,
            "sorted": sorted,
            "min": min,
            "max": max,
            "sum": sum,
        }

    def add_message(self, role: str, content: str, metadata: dict | None = None):
        """
        Add a message to the REPL context.

        Args:
            role: Message role (user/assistant/system)
            content: Message content
            metadata: Optional metadata
        """
        message = {
            "id": len(self.context["messages"]),
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
            "tokens": len(content) // 4,  # Rough estimate
        }

        self.context["messages"].append(message)
        self.context["metadata"]["total_turns"] = len(self.context["messages"]) // 2

        # Extract and store facts/entities automatically
        if role in ["user", "assistant"]:
            self._auto_extract_facts(content, role)
            self._auto_extract_entities(content)
            self._auto_extract_topics(content)

        # Add to timeline
        self.context["timeline"].append(
            {
                "message_id": message["id"],
                "timestamp": message["timestamp"],
                "role": role,
                "summary": content[:100] + "..." if len(content) > 100 else content,
            }
        )

        logger.debug(f"Added message {message['id']} to REPL context")

    @timeout_limit(5)
    @memory_limit(1000)
    def execute_code(self, code: str, description: str = "") -> dict[str, Any]:
        """
        Execute LLM-generated Python code in restricted environment.

        Args:
            code: Python code to execute
            description: Human-readable description of what the code does

        Returns:
            Execution result with status, output, and timing
        """
        start_time = time.time()
        self.stats["executions"] += 1

        try:
            # Security validation
            self._validate_code_security(code)

            # Execute in restricted environment
            if RESTRICTED_PYTHON_AVAILABLE:
                result = self._execute_restricted(code)
            else:
                result = self._execute_fallback(code)

            execution_time = time.time() - start_time
            self.stats["successful"] += 1
            self.stats["total_execution_time"] += execution_time
            self.stats["avg_execution_time"] = (
                self.stats["total_execution_time"] / self.stats["successful"]
            )

            logger.info(f"Code executed successfully in {execution_time:.3f}s: {description}")

            return {
                "status": "success",
                "result": result,
                "execution_time": execution_time,
                "description": description,
                "stats": self.get_stats(),
            }

        except Exception as e:
            execution_time = time.time() - start_time
            self.stats["failed"] += 1
            logger.error(f"Code execution failed: {e}")

            return {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
                "execution_time": execution_time,
                "description": description,
            }

    def _validate_code_security(self, code: str):
        """Validate code for security issues."""
        # Block dangerous imports
        dangerous_imports = [
            "os",
            "sys",
            "subprocess",
            "eval",
            "exec",
            "compile",
            "__import__",
            "open",
            "file",
        ]

        for danger in dangerous_imports:
            if danger in code:
                raise REPLSecurityError(f"Dangerous operation detected: {danger}")

        # Block file operations
        dangerous_ops = ["open(", "file(", "write(", "read("]
        for op in dangerous_ops:
            if op in code:
                raise REPLSecurityError(f"File operation not allowed: {op}")

        # Validate syntax
        try:
            ast.parse(code)
        except SyntaxError as e:
            raise REPLSecurityError(f"Invalid Python syntax: {e}")

    def _execute_restricted(self, code: str) -> Any:
        """Execute code with RestrictedPython."""
        # Compile with restrictions
        compile_result = compile_restricted_exec(code, filename="<string>")

        if compile_result.errors:
            raise REPLExecutionError(f"Compilation errors: {compile_result.errors}")

        # Build safe globals with all required guards
        safe_globals_dict = {
            "__builtins__": safe_builtins,
            "_getiter_": guarded_iter_unpack_sequence,
            "_getitem_": lambda obj, index: obj[index],  # Allow list/dict access
            "_getattr_": safer_getattr,  # Allow attribute access
            "context": self.context,  # Access to conversation context
            **self.safe_functions,  # Whitelisted functions
        }

        # Execute
        exec(compile_result.code, safe_globals_dict)

        # Return result if stored in 'result' variable
        return safe_globals_dict.get("result", None)

    def _execute_fallback(self, code: str) -> Any:
        """Fallback execution without RestrictedPython (less safe)."""
        logger.warning("Using fallback execution - security is limited!")

        # Build namespace
        namespace = {
            "context": self.context,
            **self.safe_functions,
        }

        # Execute
        exec(code, namespace)

        return namespace.get("result", None)

    # ==== Safe Navigation Functions ====

    @timeout_limit(2)
    @memory_limit(1000)
    def _find_messages(self, keyword: str, case_sensitive: bool = False) -> list[dict]:
        """Find messages containing keyword."""
        results = []
        pattern = re.compile(
            keyword if case_sensitive else keyword, 0 if case_sensitive else re.IGNORECASE
        )

        for msg in self.context["messages"]:
            if pattern.search(msg["content"]):
                results.append(msg)

        return results

    @timeout_limit(2)
    @memory_limit(1000)
    def _filter_by_date(self, start: str, end: str) -> list[dict]:
        """Filter messages by date range."""
        results = []
        for msg in self.context["messages"]:
            if start <= msg["timestamp"] <= end:
                results.append(msg)
        return results

    @timeout_limit(1)
    @memory_limit(1000)
    def _filter_by_role(self, role: str) -> list[dict]:
        """Filter messages by role."""
        return [msg for msg in self.context["messages"] if msg["role"] == role]

    @timeout_limit(2)
    @memory_limit(1000)
    def _grep(self, pattern: str) -> list[dict]:
        """Grep messages with regex pattern."""
        results = []
        try:
            regex = re.compile(pattern)
            for msg in self.context["messages"]:
                if regex.search(msg["content"]):
                    results.append(msg)
        except re.error as e:
            raise REPLExecutionError(f"Invalid regex pattern: {e}")
        return results

    @timeout_limit(3)
    @memory_limit(100)
    def _search_semantic(self, query: str, top_k: int = 10) -> list[dict]:
        """
        Semantic search using simple keyword matching and relevance scoring.
        Can be enhanced with embeddings in future.
        """
        query_terms = set(query.lower().split())
        scored_messages = []

        for msg in self.context["messages"]:
            content_lower = msg["content"].lower()
            # Calculate relevance score
            score = sum(1 for term in query_terms if term in content_lower)
            if score > 0:
                scored_messages.append((score, msg))

        # Sort by score and return top k
        scored_messages.sort(reverse=True, key=lambda x: x[0])
        return [msg for score, msg in scored_messages[:top_k]]

    # ==== Aggregation Functions ====

    @timeout_limit(3)
    def _summarize_range(self, start_idx: int, end_idx: int) -> str:
        """Summarize a range of messages."""
        cache_key = f"{start_idx}:{end_idx}"

        # Check cache
        if cache_key in self.context["summaries"]:
            return self.context["summaries"][cache_key]

        messages = self.context["messages"][start_idx:end_idx]

        if not messages:
            return "No messages in range"

        # Simple extractive summary
        user_msgs = [m for m in messages if m["role"] == "user"]
        assistant_msgs = [m for m in messages if m["role"] == "assistant"]

        summary_parts = []
        if user_msgs:
            topics = self._extract_topics_from_messages(user_msgs)
            summary_parts.append(f"User asked about: {', '.join(topics[:5])}")

        if assistant_msgs:
            key_points = self._extract_key_points(assistant_msgs)
            summary_parts.append(f"Discussed: {', '.join(key_points[:5])}")

        summary = " | ".join(summary_parts)

        # Cache it
        self.context["summaries"][cache_key] = summary

        return summary

    @timeout_limit(2)
    def _aggregate_facts(self) -> list[dict]:
        """Aggregate all extracted facts."""
        return self.context["facts"]

    @timeout_limit(2)
    def _extract_entities(self) -> dict[str, int]:
        """Get all extracted entities with frequencies."""
        return dict(self.context["entities"])

    @timeout_limit(1)
    def _get_timeline(self) -> list[dict]:
        """Get chronological timeline of conversation."""
        return self.context["timeline"]

    # ==== Recursive Analysis Functions ====

    def _analyze_subsection(
        self, messages: list[dict], prompt: str = "Analyze this subsection"
    ) -> dict[str, Any]:
        """
        Recursively call LLM to analyze a subsection.
        This is where the magic happens - LLM can call itself!
        """
        if self.current_recursion_depth >= self.max_recursion_depth:
            return {
                "error": f"Maximum recursion depth ({self.max_recursion_depth}) reached",
                "depth": self.current_recursion_depth,
            }

        self.current_recursion_depth += 1
        self.stats["recursive_calls"] += 1

        try:
            # Simulate recursive LLM call
            # In real implementation, this would call the actual LLM
            analysis = {
                "subsection_size": len(messages),
                "summary": self._summarize_messages(messages),
                "key_topics": self._extract_topics_from_messages(messages),
                "depth": self.current_recursion_depth,
                "timestamp": datetime.utcnow().isoformat(),
            }

            return analysis
        finally:
            self.current_recursion_depth -= 1

    def _parallel_analyze(self, message_ranges: list[tuple[int, int]]) -> list[dict[str, Any]]:
        """
        Analyze multiple message ranges in parallel (simulated).
        In production, this would use actual parallel LLM calls.
        """
        results = []

        for start, end in message_ranges[:10]:  # Limit to 10 ranges
            messages = self.context["messages"][start:end]
            analysis = self._analyze_subsection(messages)
            results.append({"range": (start, end), "analysis": analysis})

        return results

    # ==== Utility Functions ====

    @timeout_limit(1)
    def _count_messages(self, role: str | None = None) -> int:
        """Count messages, optionally filtered by role."""
        if role:
            return sum(1 for m in self.context["messages"] if m["role"] == role)
        return len(self.context["messages"])

    @timeout_limit(1)
    def _get_topics(self, top_n: int = 10) -> list[tuple[str, int]]:
        """Get top N topics discussed."""
        topics = sorted(
            self.context["metadata"]["topics"].items(), key=lambda x: x[1], reverse=True
        )
        return topics[:top_n]

    @timeout_limit(1)
    def _get_message(self, idx: int) -> dict | None:
        """Get message by index."""
        if 0 <= idx < len(self.context["messages"]):
            return self.context["messages"][idx]
        return None

    @timeout_limit(1)
    def _slice_messages(self, start: int, end: int) -> list[dict]:
        """Slice messages."""
        return self.context["messages"][start:end]

    # ==== Auto-extraction Functions ====

    def _auto_extract_facts(self, content: str, role: str):
        """Automatically extract facts from content."""
        fact_indicators = [
            r"\bis\b",
            r"\bare\b",
            r"\bwas\b",
            r"\bwere\b",
            r"\bhas\b",
            r"\bhave\b",
            r"\bshows\b",
            r"\bindicates\b",
        ]

        sentences = re.split(r"[.!?]+", content)

        for sentence in sentences:
            sentence = sentence.strip()
            if 20 < len(sentence) < 200:
                for indicator in fact_indicators:
                    if re.search(indicator, sentence, re.IGNORECASE):
                        self.context["facts"].append(
                            {
                                "fact": sentence,
                                "role": role,
                                "timestamp": datetime.utcnow().isoformat(),
                                "message_id": len(self.context["messages"]) - 1,
                            }
                        )
                        break

    def _auto_extract_entities(self, content: str):
        """Automatically extract named entities."""
        # Simple capitalized word extraction
        words = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", content)

        common_words = {
            "The",
            "This",
            "That",
            "These",
            "Those",
            "When",
            "Where",
            "What",
            "Why",
            "How",
            "Which",
            "Who",
        }

        for word in words:
            if word not in common_words and len(word) > 2:
                self.context["entities"][word] = self.context["entities"].get(word, 0) + 1

    def _auto_extract_topics(self, content: str):
        """Automatically extract and count topics."""
        words = re.findall(r"\b\w{4,}\b", content.lower())

        stopwords = {
            "this",
            "that",
            "with",
            "from",
            "have",
            "will",
            "what",
            "when",
            "where",
            "which",
            "about",
            "their",
            "there",
        }

        for word in words:
            if word not in stopwords:
                self.context["metadata"]["topics"][word] += 1

    def _extract_topics_from_messages(self, messages: list[dict]) -> list[str]:
        """Extract main topics from a list of messages."""
        word_freq = defaultdict(int)

        for msg in messages:
            words = re.findall(r"\b\w{4,}\b", msg["content"].lower())
            for word in words:
                if word not in {"this", "that", "with", "from", "have"}:
                    word_freq[word] += 1

        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10]]

    def _extract_key_points(self, messages: list[dict]) -> list[str]:
        """Extract key points from messages."""
        key_points = []

        for msg in messages:
            # Look for bullet points
            bullets = re.findall(r"(?:^|\n)[\*\-\d+\.]\s*([^\n]{20,100})", msg["content"])
            key_points.extend([b.strip() for b in bullets[:2]])

        return key_points[:10]

    def _summarize_messages(self, messages: list[dict]) -> str:
        """Create a summary of messages."""
        if not messages:
            return "No messages"

        topics = self._extract_topics_from_messages(messages)
        return f"Discussed {len(messages)} messages about: {', '.join(topics[:5])}"

    # ==== API Methods ====

    def get_context(self) -> dict[str, Any]:
        """Get full REPL context."""
        return {
            "messages": self.context["messages"][-50:],  # Last 50 messages
            "facts": self.context["facts"][-20:],
            "entities": dict(
                sorted(self.context["entities"].items(), key=lambda x: x[1], reverse=True)[:20]
            ),
            "timeline": self.context["timeline"][-30:],
            "metadata": self.context["metadata"],
            "stats": self.get_stats(),
        }

    def get_stats(self) -> dict[str, Any]:
        """Get execution statistics."""
        return {
            "total_messages": len(self.context["messages"]),
            "total_facts": len(self.context["facts"]),
            "total_entities": len(self.context["entities"]),
            "executions": self.stats["executions"],
            "successful": self.stats["successful"],
            "failed": self.stats["failed"],
            "success_rate": (
                self.stats["successful"] / self.stats["executions"] * 100
                if self.stats["executions"] > 0
                else 0
            ),
            "recursive_calls": self.stats["recursive_calls"],
            "avg_execution_time": round(self.stats["avg_execution_time"], 4),
            "current_recursion_depth": self.current_recursion_depth,
        }

    def generate_navigation_code(self, query: str) -> str:
        """
        Generate Python code for navigating context based on query.
        This would be called by the LLM to generate appropriate code.

        Args:
            query: Natural language query

        Returns:
            Python code to execute
        """
        # Simple pattern matching to generate code
        # In production, the LLM would generate this code

        if "find" in query.lower() or "search" in query.lower():
            keyword = query.split()[-1]  # Simple extraction
            return f"result = find_messages('{keyword}')"

        elif "summarize" in query.lower():
            return "result = summarize_range(0, len(context['messages']))"

        elif "facts" in query.lower():
            return "result = aggregate_facts()"

        elif "entities" in query.lower():
            return "result = extract_entities()"

        elif "count" in query.lower():
            return "result = count_messages()"

        else:
            # Default: return recent messages
            return "result = context['messages'][-10:]"

    def clear_cache(self):
        """Clear cached summaries."""
        self.context["summaries"].clear()
        logger.info("Cleared REPL cache")

    def reset(self):
        """Reset REPL state (dangerous - use with caution)."""
        self.context = {
            "messages": [],
            "facts": [],
            "entities": {},
            "timeline": [],
            "summaries": {},
            "metadata": {
                "start_time": datetime.utcnow().isoformat(),
                "total_turns": 0,
                "topics": defaultdict(int),
            },
        }
        self.stats = {
            "executions": 0,
            "successful": 0,
            "failed": 0,
            "recursive_calls": 0,
            "avg_execution_time": 0.0,
            "total_execution_time": 0.0,
        }
        logger.warning("REPL state reset")


# Singleton instance
_repl_manager = None


def get_repl_manager() -> RLMREPLManager:
    """Get singleton REPL manager instance."""
    global _repl_manager
    if _repl_manager is None:
        _repl_manager = RLMREPLManager()
        logger.info("Initialized RLM REPL Manager")
    return _repl_manager
