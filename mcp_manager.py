"""
MCP Manager - Handles Model Context Protocol integration
"""
try:
    from modelcontextprotocol.python_sdk import MCPClient, Tool
except ImportError:
    print("Warning: MCP SDK not installed. Installing required dependencies first.")
    import subprocess
    subprocess.call(["pip", "install", "modelcontextprotocol-python-sdk"])
    from modelcontextprotocol.python_sdk import MCPClient, Tool

class MCPManager:
    def __init__(self):
        self.client = MCPClient()
        self.registered_tools = {}
        
    def register_tool(self, tool_name, tool_description, function):
        """Register a new tool with MCP"""
        tool = Tool(
            name=tool_name,
            description=tool_description,
            function=function
        )
        self.registered_tools[tool_name] = tool
        self.client.register_tool(tool)
        
    async def process_with_tools(self, query):
        """Process a query using available tools"""
        return await self.client.process(query)
        
    def get_registered_tools(self):
        """Get list of all registered tools"""
        return list(self.registered_tools.keys())
