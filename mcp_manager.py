"""
MCP Manager - Handles Model Context Protocol integration
Includes Composio integration for enhanced capabilities
"""
try:
    from modelcontextprotocol.python_sdk import MCPClient, Tool
except ImportError:
    print("Warning: MCP SDK not installed. Installing required dependencies first.")
    import subprocess
    subprocess.call(["pip", "install", "modelcontextprotocol-python-sdk"])
    from modelcontextprotocol.python_sdk import MCPClient, Tool

import os
import json
import asyncio
from datetime import datetime
from utils import log

# Import Composio integration if available
try:
    from composio_integration import composio_client
    COMPOSIO_AVAILABLE = True
except ImportError:
    COMPOSIO_AVAILABLE = False
    print("Composio integration not available. Some features will be disabled.")
    
class MCPManager:
    def __init__(self, use_composio=True):
        self.client = MCPClient()
        self.registered_tools = {}
        self.tool_usage_stats = {}
        self.use_composio = use_composio and COMPOSIO_AVAILABLE
        
        # Initialize Composio if available
        if self.use_composio:
            self.composio = composio_client
            asyncio.create_task(self._sync_composio_tools())
        
    async def _sync_composio_tools(self):
        """Sync tools with Composio"""
        if not self.use_composio:
            return
            
        try:
            # Check connection
            connection_status = await self.composio.check_connection()
            if connection_status.get("status") != "connected":
                log.warning(f"Cannot sync Composio tools: {connection_status.get('message', 'Unknown error')}")
                return
                
            # List existing tools
            tools_result = await self.composio.list_tools()
            if not tools_result.get("success"):
                log.warning(f"Failed to list Composio tools: {tools_result.get('message', 'Unknown error')}")
                return
                
            # Register existing Composio tools with MCP
            for tool in tools_result.get("tools", []):
                tool_name = tool.get("name")
                if tool_name:
                    # Create a wrapper function to call Composio
                    async def tool_function(**kwargs):
                        result = await self.composio.execute_tool(tool_name, kwargs)
                        return result.get("result")
                        
                    self.register_tool(
                        tool_name,
                        tool.get("description", f"Composio tool: {tool_name}"),
                        tool_function,
                        source="composio"
                    )
                    
            log.info(f"Synced {len(tools_result.get('tools', []))} tools from Composio")
        except Exception as e:
            log.error(f"Error syncing Composio tools: {str(e)}")
        
    def register_tool(self, tool_name, tool_description, function, source="local"):
        """Register a new tool with MCP"""
        tool = Tool(
            name=tool_name,
            description=tool_description,
            function=function
        )
        
        # Add to registered tools with metadata
        self.registered_tools[tool_name] = {
            "tool": tool,
            "description": tool_description,
            "source": source,
            "registered_at": datetime.now().isoformat(),
            "usage_count": 0,
            "function": function
        }
        
        # Register with MCP client
        self.client.register_tool(tool)
        
        # Register with Composio if not from Composio already
        if self.use_composio and source != "composio":
            asyncio.create_task(self._register_with_composio(tool_name, tool_description))
            
        log.info(f"Registered tool: {tool_name} (source: {source})")
        return True
        
    async def _register_with_composio(self, tool_name, tool_description):
        """Register a tool with Composio"""
        if not self.use_composio:
            return
            
        try:
            # Create a simple schema for the tool
            schema = {
                "type": "object",
                "properties": {},
                "required": []
            }
            
            result = await self.composio.register_mcp_tool(
                tool_name,
                tool_description,
                schema
            )
            
            if result.get("success"):
                log.info(f"Successfully registered tool {tool_name} with Composio")
            else:
                log.warning(f"Failed to register tool {tool_name} with Composio: {result.get('message', 'Unknown error')}")
        except Exception as e:
            log.error(f"Error registering tool with Composio: {str(e)}")
        
    async def process_with_tools(self, query):
        """Process a query using available tools"""
        # Track tool usage during processing
        original_tools = {}
        
        # Wrap each tool to track usage
        for tool_name, tool_info in self.registered_tools.items():
            original_function = tool_info["function"]
            
            # Store original function
            original_tools[tool_name] = original_function
            
            # Create wrapper function to track usage
            async def wrapped_function(*args, **kwargs):
                # Increment usage count
                self.registered_tools[tool_name]["usage_count"] += 1
                
                # Track usage stats
                if tool_name not in self.tool_usage_stats:
                    self.tool_usage_stats[tool_name] = []
                
                # Record usage
                usage_record = {
                    "timestamp": datetime.now().isoformat(),
                    "query": query,
                    "args": args,
                    "kwargs": kwargs
                }
                
                self.tool_usage_stats[tool_name].append(usage_record)
                
                # Call original function
                result = await original_function(*args, **kwargs)
                return result
                
            # Replace function with wrapped version temporarily
            tool_info["tool"].function = wrapped_function
        
        try:
            # Process the query
            result = await self.client.process(query)
            return result
        finally:
            # Restore original functions
            for tool_name, tool_info in self.registered_tools.items():
                if tool_name in original_tools:
                    tool_info["tool"].function = original_tools[tool_name]
        
    def get_registered_tools(self):
        """Get list of all registered tools"""
        return list(self.registered_tools.keys())
        
    def get_tool_info(self, tool_name):
        """Get information about a specific tool"""
        if tool_name not in self.registered_tools:
            return None
            
        tool_info = self.registered_tools[tool_name]
        return {
            "name": tool_name,
            "description": tool_info["description"],
            "source": tool_info["source"],
            "registered_at": tool_info["registered_at"],
            "usage_count": tool_info["usage_count"]
        }
        
    def get_tool_usage_stats(self):
        """Get tool usage statistics"""
        stats = {}
        for tool_name, tool_info in self.registered_tools.items():
            stats[tool_name] = {
                "usage_count": tool_info["usage_count"],
                "source": tool_info["source"]
            }
            
        return stats
        
    async def refresh_composio_tools(self):
        """Refresh tools from Composio"""
        if not self.use_composio:
            return {
                "success": False,
                "message": "Composio integration not available"
            }
            
        try:
            await self._sync_composio_tools()
            return {
                "success": True,
                "message": f"Refreshed Composio tools. {len([t for t in self.registered_tools.values() if t['source'] == 'composio'])} Composio tools registered."
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error refreshing Composio tools: {str(e)}"
            }
