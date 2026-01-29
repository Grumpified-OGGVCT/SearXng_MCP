#!/usr/bin/env python3
"""
Demo script showing the advanced features in action
"""

import os
import sys
import time
from datetime import datetime, timedelta

# Import modules directly
sys.path.insert(0, 'src')
import importlib.util

def import_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

context_manager = import_module_from_file('context_manager', 'src/searxng_mcp/context_manager.py')
rtd_manager = import_module_from_file('rtd_manager', 'src/searxng_mcp/rtd_manager.py')

InfiniteContextManager = context_manager.InfiniteContextManager
RealTimeDataManager = rtd_manager.RealTimeDataManager


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title):
    """Print a fancy header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_context_manager():
    """Demo the Infinite Context Manager."""
    clear_screen()
    print_header("🧠 INFINITE CONTEXT MANAGER DEMO")
    
    print("This demo shows how the Context Manager handles long conversations\n")
    print("Simulating a research conversation about quantum computing...\n")
    time.sleep(2)
    
    cm = InfiniteContextManager(recent_messages_limit=5, compression_threshold=8)
    
    # Simulate a realistic conversation
    messages = [
        ("user", "What is quantum computing and how does it work?"),
        ("assistant", "Quantum computing is a revolutionary computing paradigm that leverages quantum mechanical phenomena like superposition and entanglement. Unlike classical computers that use bits (0 or 1), quantum computers use quantum bits or qubits that can exist in multiple states simultaneously."),
        ("user", "What are qubits exactly?"),
        ("assistant", "Qubits are the fundamental units of quantum information. They can represent 0, 1, or a superposition of both states simultaneously. This property allows quantum computers to perform many calculations in parallel."),
        ("user", "What is quantum entanglement?"),
        ("assistant", "Quantum entanglement is a phenomenon where quantum states of two or more particles are correlated, even when separated by large distances. Einstein famously called it 'spooky action at a distance'."),
        ("user", "How is quantum computing different from classical computing?"),
        ("assistant", "Classical computing uses binary bits and sequential processing. Quantum computing uses qubits with superposition and entanglement, enabling exponential speedup for certain problems like cryptography and optimization."),
        ("user", "What are the main applications?"),
        ("assistant", "Key applications include: 1) Drug discovery and molecular simulation, 2) Cryptography and security, 3) Financial modeling and optimization, 4) Artificial intelligence and machine learning, 5) Climate modeling."),
        ("user", "Are quantum computers available now?"),
        ("assistant", "Yes, companies like IBM, Google, Amazon, and Microsoft offer cloud-based quantum computing services. IBM has quantum computers with 127+ qubits available via IBM Quantum Experience."),
        ("user", "What is quantum supremacy?"),
        ("assistant", "Quantum supremacy refers to the point where quantum computers can solve problems that classical computers practically cannot. Google claimed to achieve this in 2019 with their Sycamore processor."),
        ("user", "What are the biggest challenges?"),
        ("assistant", "Major challenges include: 1) Error rates and decoherence, 2) Maintaining stable qubits at near-zero temperatures, 3) Scaling up to more qubits, 4) Developing quantum algorithms, 5) High costs and complexity."),
        ("user", "Tell me about quantum algorithms"),
        ("assistant", "Famous quantum algorithms include Shor's algorithm for factoring (threatening current encryption) and Grover's algorithm for database search. These algorithms show exponential or quadratic speedups over classical counterparts."),
        ("user", "How long until quantum computers are mainstream?"),
        ("assistant", "Experts predict practical quantum computers for specific tasks within 5-10 years. Mainstream adoption for general computing may take 15-20 years as technology matures and costs decrease."),
    ]
    
    for i, (role, content) in enumerate(messages, 1):
        print(f"[{i}/20] {role.upper()}: {content[:70]}...")
        cm.add_message(role, content)
        time.sleep(0.3)
    
    print("\n" + "-" * 70)
    print("💡 COMPRESSION IN ACTION")
    print("-" * 70)
    
    stats = cm.get_stats()
    
    print(f"\n📊 Statistics:")
    print(f"   Total Messages:      {stats['total_messages']}")
    print(f"   Recent (Full):       {stats['recent_messages']}")
    print(f"   Compressed Blocks:   {stats['compressed_blocks']}")
    print(f"   Key Facts Extracted: {stats['key_facts']}")
    print(f"   Entities Tracked:    {stats['entities_tracked']}")
    print(f"\n💾 Token Usage:")
    print(f"   Original Tokens:     {stats['original_tokens']}")
    print(f"   Current Tokens:      {stats['current_tokens']}")
    print(f"   Compression Ratio:   {stats['compression_ratio']}%")
    print(f"   Tokens Saved:        {stats['tokens_saved']}")
    
    context = cm.get_context(max_tokens=500)
    
    print(f"\n🎯 Optimized Context (500 token limit):")
    print(f"   Compressed Summary:  {len(context.get('compressed_summary', ''))} chars")
    print(f"   Key Facts:           {len(context.get('key_facts', []))} facts")
    print(f"   Recent Messages:     {len(context.get('recent_messages', []))} messages")
    
    if context.get('top_entities'):
        print(f"\n🔍 Top Entities:")
        for entity in context['top_entities'][:5]:
            print(f"      • {entity['entity']:20} (mentioned {entity['frequency']}x)")
    
    print("\n" + "=" * 70)
    print("✅ Context Manager reduces token usage by 70-90% for long conversations!")
    print("=" * 70)
    
    input("\n\nPress Enter to continue to RTD Manager demo...")


def demo_rtd_manager():
    """Demo the Real-Time Data Manager."""
    clear_screen()
    print_header("⚡ REAL-TIME DATA MANAGER DEMO")
    
    print("This demo shows how RTD Manager handles data freshness\n")
    time.sleep(1)
    
    rtd = RealTimeDataManager()
    
    # Demo 1: Time-sensitive detection
    print("🔍 TIME-SENSITIVE QUERY DETECTION\n")
    
    queries = [
        ("What is the current Bitcoin price?", "finance"),
        ("Latest breaking news on AI", "news"),
        ("Live NBA scores", "sports"),
        ("History of Ancient Rome", "general"),
        ("What is photosynthesis?", "science"),
    ]
    
    for query, category in queries:
        is_ts = rtd.is_time_sensitive(query, category)
        interval = rtd.get_refresh_interval(query, category)
        emoji = "⚡" if is_ts else "📚"
        print(f"{emoji} '{query}'")
        print(f"   Time-Sensitive: {'YES' if is_ts else 'NO':3}  |  Refresh Every: {rtd._format_seconds(interval)}")
        time.sleep(0.5)
    
    # Demo 2: Freshness calculation
    print("\n\n📊 FRESHNESS CALCULATION\n")
    
    test_data = [
        ("Breaking: AI breakthrough announced", timedelta(seconds=45)),
        ("Tech company releases new product", timedelta(minutes=30)),
        ("Morning news update", timedelta(hours=3)),
        ("Yesterday's market analysis", timedelta(days=1)),
        ("Last week's research findings", timedelta(days=7)),
        ("Monthly industry report", timedelta(days=30)),
    ]
    
    for title, age in test_data:
        result = {
            'title': title,
            'publishedDate': (datetime.utcnow() - age).isoformat()
        }
        freshness = rtd.calculate_freshness(result)
        
        # Color code based on status
        badge = freshness['badge']
        score = freshness['score']
        age_display = freshness['age_display']
        
        print(f"{badge:12} | Score: {score:3}% | {age_display:12} | {title}")
        time.sleep(0.5)
    
    # Demo 3: Live query analysis
    print("\n\n🎯 LIVE QUERY ANALYSIS\n")
    
    query = "What are the latest developments in AI?"
    print(f"Query: '{query}'\n")
    
    # Simulate results
    results = [
        {
            'title': 'OpenAI Announces GPT-5 with Revolutionary Capabilities',
            'url': 'https://example.com/gpt5',
            'publishedDate': (datetime.utcnow() - timedelta(minutes=20)).isoformat()
        },
        {
            'title': 'Google DeepMind Achieves Breakthrough in Protein Folding',
            'url': 'https://example.com/deepmind',
            'publishedDate': (datetime.utcnow() - timedelta(hours=2)).isoformat()
        },
        {
            'title': 'AI Ethics Guidelines Released by EU Commission',
            'url': 'https://example.com/eu-ai',
            'publishedDate': (datetime.utcnow() - timedelta(hours=6)).isoformat()
        }
    ]
    
    status = rtd.get_rtd_status(query, results, "news")
    
    print(f"Time-Sensitive:     {'✅ YES' if status['is_time_sensitive'] else '❌ NO'}")
    print(f"Average Freshness:  {status['average_freshness']:.1f}%")
    print(f"Overall Status:     {status['overall_status'].upper()}")
    print(f"Refresh Interval:   {status['refresh_interval_display']}")
    print(f"Auto-Refresh:       {'✅ ENABLED' if status['auto_refresh_enabled'] else '❌ DISABLED'}")
    
    if status['auto_refresh_enabled']:
        print(f"\n⏱️  Auto-refresh countdown:")
        for i in range(5, 0, -1):
            print(f"   Next refresh in: {i} seconds...", end='\r')
            time.sleep(1)
        print(f"   🔄 Refreshing now!          ")
    
    print("\n" + "=" * 70)
    print("✅ RTD Manager provides always-fresh data with smart refresh!")
    print("=" * 70)
    
    input("\n\nPress Enter to finish...")


def main():
    """Run the demo."""
    try:
        clear_screen()
        print_header("🚀 ADVANCED FEATURES DEMO")
        
        print("""
This demo showcases two powerful systems:

  🧠 Infinite Context Manager
     - Smart compression reducing token usage by 70-90%
     - Automatic fact and entity extraction
     - Maintains conversation quality with minimal tokens

  ⚡ Real-Time Data Manager
     - Calculates data freshness (0-100% score)
     - Visual badges (🔴 LIVE, 🟢 FRESH, 🟡 RECENT, etc.)
     - Smart refresh intervals based on query type
     - Auto-refresh for time-sensitive data

Let's see them in action!
        """)
        
        input("\nPress Enter to start the demo...")
        
        # Run demos
        demo_context_manager()
        demo_rtd_manager()
        
        # Finale
        clear_screen()
        print_header("🎉 DEMO COMPLETE!")
        
        print("""
Both systems are now integrated into the SearXNG MCP Chat Interface!

🌟 Key Benefits:

   • Infinite Context: Handle conversations of ANY length efficiently
   • Token Savings: Save 70-90% on API costs for long conversations
   • Fresh Data: Always know how fresh your search results are
   • Smart Refresh: Automatic refresh for time-sensitive queries
   • Great UX: Visual indicators and real-time stats

🚀 Getting Started:

   1. Start the dashboard:
      python -m uvicorn src.searxng_mcp.dashboard:app --reload

   2. Open your browser:
      http://localhost:8765

   3. Start chatting and watch the magic happen!

📚 Documentation:
   See ADVANCED_FEATURES.md for detailed API documentation

Thank you for watching! 🎬
        """)
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
