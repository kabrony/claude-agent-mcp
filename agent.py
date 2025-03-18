"""
Main Agent Module - Combines all components into a unified agent with enhanced memory and AI chat
"""
import os
import json
import asyncio
import argparse
from rich.console import Console
from dotenv import load_dotenv
from datetime import datetime

# Internal modules
from claude_client import ClaudeClient
from memory_system import MemorySystem
from system_bridge import SystemBridge
from mcp_manager import MCPManager
from web_research import WebResearcher
from utils import setup_environment, retry_async, Timer, log

# Setup rich console
console = Console()

class ClaudeAgent:
    def __init__(self, max_memory_age_days=30):
        # Setup environment
        setup_environment()
        load_dotenv()
        
        # Create core components with enhanced features
        self.memory = MemorySystem(max_memory_age_days=max_memory_age_days)
        self.system = SystemBridge()
        self.mcp = MCPManager()
        
        # Initialize Claude client with API key from environment
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.claude = ClaudeClient(api_key=api_key)
        
        # Initialize web researcher
        self.researcher = WebResearcher(memory_system=self.memory)
        
        # Register tools with MCP
        self._register_tools()
        
        # System information
        self.agent_info = {
            "name": "OrganiX",
            "version": "1.0.0",
            "system_info": self.system.get_system_info()
        }
        
        # Start a new conversation
        self.claude.start_new_conversation("Agent Session")
        
        log.info(f"Claude Agent initialized: {self.agent_info['name']} v{self.agent_info['version']}")
        
    def _register_tools(self):
        """Register all available tools with MCP"""
        # File system tools
        self.mcp.register_tool(
            "list_files", 
            "List files in a directory",
            lambda directory: os.listdir(directory)
        )
        
        # Web research tools
        self.mcp.register_tool(
            "web_search",
            "Search the web for information",
            self.researcher.search
        )
        
        self.mcp.register_tool(
            "extract_url",
            "Extract content from a specific URL",
            self.researcher.extract_content
        )
        
        # System tools
        self.mcp.register_tool(
            "execute_command",
            "Execute a command on the local system",
            self.system.execute_local
        )
        
        # Memory tools
        self.mcp.register_tool(
            "retrieve_memory",
            "Retrieve memories relevant to a query",
            self.memory.retrieve_relevant
        )
        
        # Add enhanced memory tools
        self.mcp.register_tool(
            "retrieve_memory_by_timeframe",
            "Retrieve memories within a specific timeframe",
            self.memory.retrieve_by_timeframe
        )
        
        self.mcp.register_tool(
            "summarize_memories",
            "Generate a summary of recent memories",
            self.memory.summarize_memories
        )
        
        log.info(f"Registered tools: {self.mcp.get_registered_tools()}")
        
    async def process_query(self, query, system_prompt=None, max_tokens=4096, extended_thinking=False):
        """Process a user query using Claude with all capabilities"""
        timer = Timer("Query processing").start()
        
        # Add memory of this query with importance based on length/complexity
        importance = min(5, max(1, len(query) // 100))  # 1-5 based on length
        memory_id = self.memory.add_memory("episodic", query, {"type": "user_query"}, importance=importance)
        
        # Construct system prompt if none provided
        if system_prompt is None:
            system_prompt = f"""You are OrganiX, an advanced AI assistant with access to various tools and capabilities.
Current time: {datetime.now().isoformat()}
System Info: {json.dumps(self.system.get_system_info())}
Available Tools: {', '.join(self.mcp.get_registered_tools())}

When using tools, clearly indicate which tool you're using and why. 
Always provide thoughtful, helpful responses."""
        
        # Process with Claude, using extended thinking if requested
        log.info(f"Sending query to Claude: {query[:50]}...")
        timer.lap("Query preparation")
        
        if extended_thinking:
            response = await retry_async(
                self.claude.send_extended_thinking_message,
                query,
                system=system_prompt,
                max_tokens=max_tokens
            )
        else:
            response = await retry_async(
                self.claude.send_message,
                query,
                system=system_prompt,
                max_tokens=max_tokens
            )
        
        # Store response in memory with same importance as query
        self.memory.add_memory("episodic", response, {
            "type": "agent_response", 
            "query": query,
            "query_memory_id": memory_id
        }, importance=importance)
        
        # Analyze the response
        response_analysis = self.claude.analyze_response(response)
        
        # If response contains key information, store in semantic memory
        if len(response_analysis.get("key_points", [])) > 0:
            key_points = "\n".join(response_analysis["key_points"])
            self.memory.add_memory("semantic", key_points, {
                "type": "key_information",
                "source_query": query[:100] + "..." if len(query) > 100 else query
            }, importance=min(5, importance + 1))
        
        timer.lap("Claude response")
        timer.stop()
        
        return response
        
    async def stream_response(self, query, system_prompt=None, max_tokens=4096):
        """Stream a response to a query"""
        # Add memory of this query
        importance = min(5, max(1, len(query) // 100))  # 1-5 based on length
        memory_id = self.memory.add_memory("episodic", query, {"type": "user_query"}, importance=importance)
        
        # Construct system prompt if none provided
        if system_prompt is None:
            system_prompt = f"""You are OrganiX, an advanced AI assistant with access to various tools and capabilities.
Current time: {datetime.now().isoformat()}
System Info: {json.dumps(self.system.get_system_info())}
Available Tools: {', '.join(self.mcp.get_registered_tools())}

When using tools, clearly indicate which tool you're using and why. 
Always provide thoughtful, helpful responses."""
        
        # Stream response from Claude
        log.info(f"Streaming response for query: {query[:50]}...")
        
        full_response = ""
        async for chunk in self.claude.stream_message(query, system=system_prompt, max_tokens=max_tokens):
            full_response += chunk
            yield chunk
            
        # Store complete response in memory
        self.memory.add_memory("episodic", full_response, {
            "type": "agent_response", 
            "query": query,
            "query_memory_id": memory_id
        }, importance=importance)
        
    async def process_query_with_tools(self, query, tools=None, system_prompt=None, max_tokens=4096):
        """Process a query using tools"""
        timer = Timer("Tool-enabled query processing").start()
        
        # Add memory of this query
        importance = min(5, max(1, len(query) // 100))  # 1-5 based on length
        memory_id = self.memory.add_memory("episodic", query, {"type": "user_query_with_tools"}, importance=importance)
        
        # Prepare tools dictionary
        if tools is None:
            # Use all registered MCP tools
            tools_dict = {}
            for tool_name in self.mcp.get_registered_tools():
                if tool_name in self.mcp.registered_tools:
                    tool = self.mcp.registered_tools[tool_name]
                    tools_dict[tool_name] = {
                        "description": tool.description,
                        "function": tool.function,
                        "input_schema": {"type": "object", "properties": {}}  # Basic schema
                    }
        else:
            tools_dict = tools
            
        # Construct system prompt if none provided
        if system_prompt is None:
            system_prompt = f"""You are OrganiX, an advanced AI assistant with access to various tools and capabilities.
Current time: {datetime.now().isoformat()}
System Info: {json.dumps(self.system.get_system_info())}
Available Tools: {', '.join(tools_dict.keys())}

You should use tools when they would help answer the query more effectively.
When using tools, clearly indicate which tool you're using and why.
Always provide thoughtful, helpful responses."""
        
        # Process with Claude using tools
        log.info(f"Sending tool-enabled query to Claude: {query[:50]}...")
        timer.lap("Tool query preparation")
        
        response = await retry_async(
            self.claude.send_message_with_tools,
            query,
            tools=tools_dict,
            system=system_prompt,
            max_tokens=max_tokens
        )
        
        # Store response in memory with higher importance (tool usage is valuable)
        self.memory.add_memory("episodic", response, {
            "type": "agent_response_with_tools", 
            "query": query,
            "query_memory_id": memory_id,
            "tools_used": list(tools_dict.keys())
        }, importance=min(5, importance + 1))
        
        # Store tool usage pattern in procedural memory
        self.memory.add_memory("procedural", json.dumps({
            "query_pattern": query[:50],
            "tools_used": list(tools_dict.keys())
        }), {
            "type": "tool_usage_pattern",
            "full_query": query
        }, importance=3)
        
        timer.lap("Tool response")
        timer.stop()
        
        return response
        
    async def research_topic(self, topic, max_results=5):
        """Research a topic using web search capabilities"""
        log.info(f"Researching topic: {topic}")
        
        # Add memory of this research request
        memory_id = self.memory.add_memory("episodic", topic, {"type": "research_request"}, importance=4)
        
        results = await self.researcher.summarize_research(topic, max_results)
        
        # Format research results for presentation
        formatted_results = f"## Research on: {topic}\n\n"
        
        for i, summary in enumerate(results.get("summaries", [])):
            formatted_results += f"### {i+1}. {summary.get('title', 'Untitled')}\n"
            formatted_results += f"Source: {summary.get('url', 'Unknown')}\n\n"
            formatted_results += f"{summary.get('summary', 'No summary available')}\n\n"
            
        # Store research results in semantic memory (high importance)
        self.memory.add_memory("semantic", formatted_results, {
            "type": "research_results",
            "topic": topic,
            "request_memory_id": memory_id,
            "sources": [s.get("url") for s in results.get("summaries", [])]
        }, importance=5)
        
        return formatted_results
        
    async def connect_to_remote(self, host, username, password=None, key_file=None):
        """Connect to a remote system"""
        log.info(f"Connecting to remote system: {host}")
        
        result = await self.system.connect_remote("ubuntu", host, username, password, key_file)
        
        # Store connection information in procedural memory
        connection_info = {
            "host": host,
            "username": username,
            "key_file": key_file,
            "success": result.get("success", False)
        }
        
        self.memory.add_memory("procedural", json.dumps(connection_info), {
            "type": "remote_connection",
            "host": host
        }, importance=4)
        
        if result.get("success"):
            log.info(f"Successfully connected to {host}")
        else:
            log.error(f"Failed to connect to {host}: {result.get('error')}")
            
        return result
        
    def get_memory_stats(self):
        """Get statistics about agent memory"""
        return self.memory.get_memory_stats()
        
    def save_conversation(self, filename=None):
        """Save the current conversation to a file"""
        return self.claude.save_conversation_to_file(filename=filename)
        
    def load_conversation(self, filename):
        """Load a conversation from a file"""
        return self.claude.load_conversation_from_file(filename)
        
    def summarize_memories(self, days=7):
        """Summarize recent memories"""
        return self.memory.summarize_memories(timeframe_days=days)
        
    def get_conversation_analytics(self):
        """Get analytics about conversation history"""
        return self.claude.get_analytics()
        
    def maintain_memory(self):
        """Perform memory maintenance (prune old memories)"""
        pruned_count = self.memory.prune_old_memories()
        log.info(f"Memory maintenance: pruned {pruned_count} old memories")
        return pruned_count
        
    def create_new_conversation(self, title=None):
        """Create a new conversation session"""
        return self.claude.start_new_conversation(title)

async def main():
    """Main function to run the agent"""
    parser = argparse.ArgumentParser(description="Claude Agent with Enhanced Memory and Chat")
    parser.add_argument("--query", "-q", help="Query to process")
    parser.add_argument("--stream", "-s", action="store_true", help="Stream the response")
    parser.add_argument("--research", "-r", help="Research a topic")
    parser.add_argument("--max-tokens", "-m", type=int, default=4096, help="Maximum tokens for Claude response")
    parser.add_argument("--tools", "-t", action="store_true", help="Use tools for the query")
    parser.add_argument("--extended-thinking", "-e", action="store_true", help="Use extended thinking mode")
    parser.add_argument("--save", help="Save conversation to specified file")
    parser.add_argument("--load", help="Load conversation from specified file")
    parser.add_argument("--maintenance", action="store_true", help="Perform memory maintenance")
    args = parser.parse_args()
    
    # Initialize agent
    agent = ClaudeAgent()
    
    if args.maintenance:
        pruned = agent.maintain_memory()
        console.print(f"[bold green]Memory maintenance complete. Pruned {pruned} old memories.[/]")
    elif args.load:
        if agent.load_conversation(args.load):
            console.print(f"[bold green]Loaded conversation from {args.load}[/]")
        else:
            console.print(f"[bold red]Failed to load conversation from {args.load}[/]")
    elif args.save:
        filename = agent.save_conversation(args.save)
        if filename:
            console.print(f"[bold green]Saved conversation to {filename}[/]")
        else:
            console.print(f"[bold red]Failed to save conversation[/]")
    elif args.research:
        result = await agent.research_topic(args.research)
        console.print(result)
    elif args.query:
        if args.tools:
            response = await agent.process_query_with_tools(args.query, max_tokens=args.max_tokens)
            console.print(response)
        elif args.stream:
            async for chunk in agent.stream_response(args.query, max_tokens=args.max_tokens):
                console.print(chunk, end="")
        else:
            response = await agent.process_query(
                args.query, 
                max_tokens=args.max_tokens,
                extended_thinking=args.extended_thinking
            )
            console.print(response)
    else:
        console.print("[bold green]Claude Agent with Enhanced Memory is ready![/]")
        console.print("Use --query or --research to interact with the agent.")
        console.print(f"System info: {agent.system.get_system_info()['platform']}")
        console.print(f"Memory stats: {agent.get_memory_stats()}")
        console.print("\nAdditional commands:")
        console.print("  --tools            Use tools with your query")
        console.print("  --extended-thinking   Use extended thinking mode")
        console.print("  --save <file>      Save conversation to file")
        console.print("  --load <file>      Load conversation from file")
        console.print("  --maintenance      Perform memory maintenance")

if __name__ == "__main__":
    asyncio.run(main())
