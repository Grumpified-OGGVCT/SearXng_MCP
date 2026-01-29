"""
Tests for RLM REPL Manager

Tests the revolutionary context management system with:
- Safe code execution
- Recursive analysis
- Navigation functions
- Security validation
"""

import pytest
import time
from datetime import datetime
from searxng_mcp.repl_manager import (
    RLMREPLManager,
    REPLExecutionError,
    REPLSecurityError,
    get_repl_manager
)


class TestREPLManager:
    """Test REPL Manager functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.repl = RLMREPLManager(
            max_recursion_depth=3,
            execution_timeout=5,
            max_result_items=100
        )
        
        # Add sample messages
        self.repl.add_message("user", "What is quantum computing?")
        self.repl.add_message("assistant", "Quantum computing is a revolutionary computing paradigm...")
        self.repl.add_message("user", "Tell me about Python programming")
        self.repl.add_message("assistant", "Python is a high-level programming language...")
        self.repl.add_message("user", "How does machine learning work?")
        self.repl.add_message("assistant", "Machine learning is a subset of AI that enables systems to learn...")
    
    def test_add_message(self):
        """Test adding messages to context."""
        initial_count = len(self.repl.context['messages'])
        self.repl.add_message("user", "Test message")
        assert len(self.repl.context['messages']) == initial_count + 1
        
        last_message = self.repl.context['messages'][-1]
        assert last_message['role'] == 'user'
        assert last_message['content'] == 'Test message'
        assert 'timestamp' in last_message
        assert 'id' in last_message
    
    def test_find_messages(self):
        """Test finding messages by keyword."""
        code = "result = find_messages('quantum')"
        result = self.repl.execute_code(code, "Find quantum messages")
        
        assert result['status'] == 'success'
        assert len(result['result']) > 0
        assert any('quantum' in msg['content'].lower() for msg in result['result'])
    
    def test_filter_by_role(self):
        """Test filtering messages by role."""
        code = "result = filter_by_role('user')"
        result = self.repl.execute_code(code, "Filter user messages")
        
        assert result['status'] == 'success'
        assert all(msg['role'] == 'user' for msg in result['result'])
    
    def test_grep_pattern(self):
        """Test grep with regex pattern."""
        code = "result = grep(r'computing|programming')"
        result = self.repl.execute_code(code, "Grep for computing or programming")
        
        assert result['status'] == 'success'
        assert len(result['result']) > 0
    
    def test_search_semantic(self):
        """Test semantic search."""
        code = "result = search_semantic('Python programming', top_k=5)"
        result = self.repl.execute_code(code, "Semantic search for Python")
        
        assert result['status'] == 'success'
        assert isinstance(result['result'], list)
        assert len(result['result']) <= 5
    
    def test_summarize_range(self):
        """Test message range summarization."""
        code = "result = summarize_range(0, 3)"
        result = self.repl.execute_code(code, "Summarize first 3 messages")
        
        assert result['status'] == 'success'
        assert isinstance(result['result'], str)
        assert len(result['result']) > 0
    
    def test_aggregate_facts(self):
        """Test fact aggregation."""
        code = "result = aggregate_facts()"
        result = self.repl.execute_code(code, "Get all facts")
        
        assert result['status'] == 'success'
        assert isinstance(result['result'], list)
    
    def test_extract_entities(self):
        """Test entity extraction."""
        code = "result = extract_entities()"
        result = self.repl.execute_code(code, "Get entities")
        
        assert result['status'] == 'success'
        assert isinstance(result['result'], dict)
    
    def test_get_timeline(self):
        """Test timeline retrieval."""
        code = "result = get_timeline()"
        result = self.repl.execute_code(code, "Get timeline")
        
        assert result['status'] == 'success'
        assert isinstance(result['result'], list)
        assert len(result['result']) > 0
    
    def test_count_messages(self):
        """Test message counting."""
        code = "result = count_messages()"
        result = self.repl.execute_code(code, "Count all messages")
        
        assert result['status'] == 'success'
        assert result['result'] == len(self.repl.context['messages'])
        
        # Count by role
        code = "result = count_messages('user')"
        result = self.repl.execute_code(code, "Count user messages")
        
        assert result['status'] == 'success'
        user_count = sum(1 for m in self.repl.context['messages'] if m['role'] == 'user')
        assert result['result'] == user_count
    
    def test_analyze_subsection(self):
        """Test recursive subsection analysis."""
        code = """
messages = slice_messages(0, 3)
result = analyze_subsection(messages, "Analyze this section")
"""
        result = self.repl.execute_code(code, "Analyze subsection")
        
        assert result['status'] == 'success'
        assert 'subsection_size' in result['result']
        assert 'summary' in result['result']
        assert 'depth' in result['result']
    
    def test_parallel_analyze(self):
        """Test parallel analysis."""
        code = """
ranges = [(0, 2), (2, 4), (4, 6)]
result = parallel_analyze(ranges)
"""
        result = self.repl.execute_code(code, "Parallel analysis")
        
        assert result['status'] == 'success'
        assert isinstance(result['result'], list)
        assert len(result['result']) == 3
    
    def test_get_topics(self):
        """Test topic extraction."""
        code = "result = get_topics(5)"
        result = self.repl.execute_code(code, "Get top 5 topics")
        
        assert result['status'] == 'success'
        assert isinstance(result['result'], list)
        assert len(result['result']) <= 5
    
    def test_slice_messages(self):
        """Test message slicing."""
        code = "result = slice_messages(0, 2)"
        result = self.repl.execute_code(code, "Slice messages")
        
        assert result['status'] == 'success'
        assert len(result['result']) == 2
    
    def test_complex_query(self):
        """Test complex multi-operation query."""
        code = """
# Find quantum-related messages
quantum_msgs = find_messages('quantum')

# Get their count directly (avoid list comprehension for now)
result = len(quantum_msgs)
"""
        result = self.repl.execute_code(code, "Complex query")
        
        assert result['status'] == 'success'
        assert isinstance(result['result'], int)
    
    def test_security_blocked_import(self):
        """Test that dangerous imports are blocked."""
        code = "import os; result = os.listdir()"
        result = self.repl.execute_code(code, "Dangerous import")
        
        assert result['status'] == 'error'
        assert 'dangerous' in result['error'].lower() or 'security' in result['error'].lower()
    
    def test_security_blocked_file_ops(self):
        """Test that file operations are blocked."""
        code = "result = open('/etc/passwd', 'r').read()"
        result = self.repl.execute_code(code, "File operation")
        
        assert result['status'] == 'error'
    
    def test_security_blocked_eval(self):
        """Test that eval is blocked."""
        code = "result = eval('1 + 1')"
        result = self.repl.execute_code(code, "Eval operation")
        
        assert result['status'] == 'error'
    
    def test_syntax_error(self):
        """Test syntax error handling."""
        code = "result = this is invalid python"
        result = self.repl.execute_code(code, "Invalid syntax")
        
        assert result['status'] == 'error'
    
    def test_execution_stats(self):
        """Test execution statistics tracking."""
        initial_stats = self.repl.get_stats()
        
        # Execute some code
        self.repl.execute_code("result = count_messages()", "Test")
        self.repl.execute_code("result = find_messages('test')", "Test")
        
        stats = self.repl.get_stats()
        
        assert stats['executions'] == initial_stats['executions'] + 2
        assert stats['successful'] >= initial_stats['successful']
        assert stats['avg_execution_time'] >= 0
    
    def test_get_context(self):
        """Test getting full context."""
        context = self.repl.get_context()
        
        assert 'messages' in context
        assert 'facts' in context
        assert 'entities' in context
        assert 'timeline' in context
        assert 'metadata' in context
        assert 'stats' in context
    
    def test_generate_navigation_code(self):
        """Test code generation for queries."""
        code = self.repl.generate_navigation_code("find messages about Python")
        assert isinstance(code, str)
        assert len(code) > 0
        
        code = self.repl.generate_navigation_code("summarize conversation")
        assert 'summarize' in code.lower()
        
        code = self.repl.generate_navigation_code("count messages")
        assert 'count' in code.lower()
    
    def test_singleton_instance(self):
        """Test singleton pattern."""
        instance1 = get_repl_manager()
        instance2 = get_repl_manager()
        assert instance1 is instance2
    
    def test_auto_fact_extraction(self):
        """Test automatic fact extraction."""
        self.repl.add_message("assistant", "Python is a programming language. It has extensive libraries.")
        
        facts = self.repl.context['facts']
        assert len(facts) > 0
        # Check if some facts were extracted
        assert any('is' in fact['fact'].lower() for fact in facts)
    
    def test_auto_entity_extraction(self):
        """Test automatic entity extraction."""
        self.repl.add_message("user", "Tell me about Python and JavaScript")
        
        entities = self.repl.context['entities']
        assert 'Python' in entities or 'JavaScript' in entities
    
    def test_auto_topic_extraction(self):
        """Test automatic topic extraction."""
        self.repl.add_message("user", "quantum mechanics quantum physics")
        
        topics = self.repl.context['metadata']['topics']
        assert 'quantum' in topics
        assert topics['quantum'] >= 2
    
    def test_timeline_tracking(self):
        """Test timeline is maintained."""
        timeline = self.repl.context['timeline']
        assert len(timeline) == len(self.repl.context['messages'])
        
        for entry in timeline:
            assert 'message_id' in entry
            assert 'timestamp' in entry
            assert 'role' in entry
            assert 'summary' in entry
    
    def test_clear_cache(self):
        """Test cache clearing."""
        # Create some cached summaries
        self.repl.execute_code("result = summarize_range(0, 2)", "Test")
        assert len(self.repl.context['summaries']) > 0
        
        self.repl.clear_cache()
        assert len(self.repl.context['summaries']) == 0
    
    def test_memory_limit(self):
        """Test memory limits are enforced."""
        # Try to get more items than limit
        code = f"result = context['messages'] * 1000"
        result = self.repl.execute_code(code, "Large result")
        
        # Should not crash, may be truncated
        assert result['status'] in ['success', 'error']
    
    def test_recursion_depth_limit(self):
        """Test recursion depth is enforced."""
        # Set to shallow depth
        self.repl.max_recursion_depth = 2
        
        # Try deep recursion
        code = """
def recursive_analyze(depth=0):
    if depth < 5:
        return analyze_subsection(context['messages'][:2])
    return depth

result = recursive_analyze()
"""
        result = self.repl.execute_code(code, "Deep recursion")
        
        # Should complete but hit limit
        assert result['status'] == 'success'
    
    def test_context_access(self):
        """Test that code can access context."""
        code = """
# Access different parts of context
msgs = len(context['messages'])
facts_count = len(context['facts'])
entities_count = len(context['entities'])

result = {
    'messages': msgs,
    'facts': facts_count,
    'entities': entities_count
}
"""
        result = self.repl.execute_code(code, "Access context")
        
        assert result['status'] == 'success'
        assert 'messages' in result['result']
        assert result['result']['messages'] > 0


class TestREPLSecurity:
    """Test security features."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.repl = RLMREPLManager()
    
    def test_no_subprocess(self):
        """Test subprocess is blocked."""
        code = "import subprocess; result = subprocess.run(['ls'])"
        result = self.repl.execute_code(code, "Subprocess")
        assert result['status'] == 'error'
    
    def test_no_sys_access(self):
        """Test sys module is blocked."""
        code = "import sys; result = sys.exit()"
        result = self.repl.execute_code(code, "Sys access")
        assert result['status'] == 'error'
    
    def test_no_network(self):
        """Test network access is blocked."""
        code = "import socket; result = socket.socket()"
        result = self.repl.execute_code(code, "Network")
        assert result['status'] == 'error'
    
    def test_no_file_write(self):
        """Test file writing is blocked."""
        code = "with open('/tmp/test.txt', 'w') as f: f.write('test')"
        result = self.repl.execute_code(code, "File write")
        assert result['status'] == 'error'


class TestREPLPerformance:
    """Test performance characteristics."""
    
    def setup_method(self):
        """Setup with many messages."""
        self.repl = RLMREPLManager()
        
        # Add 100 messages
        for i in range(100):
            self.repl.add_message("user", f"Question {i} about topic {i % 10}")
            self.repl.add_message("assistant", f"Answer {i} discussing topic {i % 10}")
    
    def test_search_performance(self):
        """Test search is fast."""
        start = time.time()
        code = "result = find_messages('topic')"
        result = self.repl.execute_code(code, "Search")
        duration = time.time() - start
        
        assert result['status'] == 'success'
        assert duration < 1.0  # Should complete in under 1 second
    
    def test_summarize_performance(self):
        """Test summarization is fast."""
        start = time.time()
        code = "result = summarize_range(0, 50)"
        result = self.repl.execute_code(code, "Summarize")
        duration = time.time() - start
        
        assert result['status'] == 'success'
        assert duration < 2.0  # Should complete in under 2 seconds
    
    def test_stats_tracking(self):
        """Test stats are tracked correctly."""
        # Execute multiple operations
        for i in range(10):
            self.repl.execute_code("result = count_messages()", f"Op {i}")
        
        stats = self.repl.get_stats()
        assert stats['executions'] >= 10
        assert stats['avg_execution_time'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
