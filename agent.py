"""
Main Agent Module - Combines all components into a unified agent
"""
import os
import json
import asyncio
import argparse
from rich.console import Console
from dotenv import load_dotenv

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
    def __init__(self):
        # Setup environment
        setup_environment()
        load_dotenv()
        
        # Create core components
        self.memory = MemorySystem()
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
        
        log.info(f"Registered tools: {self.mcp.get_registered_tools()}")
        
    async def process_query(self, query, system_prompt=None, max_tokens=4096):
        """Process a user query using Claude with all capabilities"""
        timer = Timer("Query processing").start()
        
        # Add memory of this query
        self.memory.add_memory("episodic", query, {"type": "user_query"})
        
        # Construct system prompt if none provided
        if system_prompt is None:
            system_prompt = f"""You are OrganiX, an advanced AI assistant with access to various tools and capabilities.
Current time: {Timer().start_time}
System Info: {json.dumps(self.system.get_system_info())}
Available Tools: {', '.join(self.mcp.get_registered_tools())}

When using tools, clearly indicate which tool you're using and why. 
Always provide thoughtful, helpful responses."""
        
        # Process with Claude
        log.info(f"Sending query to Claude: {query[:50]}...")
        timer.lap("Query preparation")
        
        response = await retry_async(
            self.claude.send_message,
            query,
            system=system_prompt,
            max_tokens=max_tokens
        )
        
        # Store response in memory
        self.memory.add_memory("episodic", response, {"type": "agent_response", "query": query})
        
        timer.lap("Claude response")
        timer.stop()
        
        return response
        
    async def stream_response(self, query, system_prompt=None, max_tokens=4096):
        """Stream a response to a query"""
        # Add memory of this query
        self.memory.add_memory("episodic", query, {"type": "user_query"})
        
        # Construct system prompt if none provided
        if system_prompt is None:
            system_prompt = f"""You are OrganiX, an advanced AI assistant with access to various tools and capabilities.
Current time: {Timer().start_time}
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
        self.memory.add_memory("episodic", full_response, {"type": "agent_response", "query": query})
        
    async def research_topic(self, topic, max_results=5):
        """Research a topic using web search capabilities"""
        log.info(f"Researching topic: {topic}")
        
        results = await self.researcher.summarize_research(topic, max_results)
        
        # Format research results for presentation
        formatted_results = f"## Research on: {topic}\n\n"
        
        for i, summary in enumerate(results.get("summaries", [])):
            formatted_results += f"### {i+1}. {summary.get('title', 'Untitled')}\n"
            formatted_results += f"Source: {summary.get('url', 'Unknown')}\n\n"
            formatted_results += f"{summary.get('summary', 'No summary available')}\n\n"
            
        return formatted_results
        
    async def connect_to_remote(self, host, username, password=None, key_file=None):
        """Connect to a remote system"""
        log.info(f"Connecting to remote system: {host}")
        
        result = await self.system.connect_remote("ubuntu", host, username, password, key_file)
        
        if result.get("success"):
            log.info(f"Successfully connected to {host}")
        else:
            log.error(f"Failed to connect to {host}: {result.get('error')}")
            
        return result
        
    def get_memory_stats(self):
        """Get statistics about agent memory"""
        return self.memory.get_memory_stats()

async def main():
    """Main function to run the agent"""
    parser = argparse.ArgumentParser(description="Claude Agent with MCP")
    parser.add_argument("--query", "-q", help="Query to process")
    parser.add_argument("--stream", "-s", action="store_true", help="Stream the response")
    parser.add_argument("--research", "-r", help="Research a topic")
    parser.add_argument("--max-tokens", "-m", type=int, default=4096, help="Maximum tokens for Claude response")
    args = parser.parse_args()
    
    # Initialize agent
    agent = ClaudeAgent()
    
    if args.research:
        result = await agent.research_topic(args.research)
        console.print(result)
    elif args.query:
        if args.stream:
            async for chunk in agent.stream_response(args.query, max_tokens=args.max_tokens):
                console.print(chunk, end="")
        else:
            response = await agent.process_query(args.query, max_tokens=args.max_tokens)
            console.print(response)
    else:
        console.print("[bold green]Claude Agent is ready![/]")
        console.print("Use --query or --research to interact with the agent.")
        console.print(f"System info: {agent.system.get_system_info()['platform']}")
        console.print(f"Memory stats: {agent.get_memory_stats()}")

if __name__ == "__main__":
    asyncio.run(main())
