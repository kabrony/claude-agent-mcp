"""
Composio Integration - Handles integration with Composio API for MCP
"""
import os
import json
import aiohttp
import asyncio
import subprocess
import time
from dotenv import load_dotenv
from utils import log

# Load environment variables
load_dotenv()

class ComposioClient:
    def __init__(self):
        # Load credentials
        self.api_key = os.getenv("COMPOSIO_API_KEY")
        self.connection_id = os.getenv("COMPOSIO_CONNECTION_ID")
        self.integration_id = os.getenv("COMPOSIO_INTEGRATION_ID")
        self.base_url = os.getenv("COMPOSIO_BASE_URL", "https://api.composio.dev")
        
        # Check for required credentials
        self.is_configured = bool(self.api_key and self.connection_id)
        
        # Cache for connection status
        self.connection_status = None
        self.connection_last_checked = 0
        
        # Tools registry
        self.registered_tools = {}
        
        if not self.is_configured:
            log.warning("Composio credentials not found in environment variables. Some features will be disabled.")
            log.info("Set COMPOSIO_API_KEY and COMPOSIO_CONNECTION_ID in .env file to enable Composio integration.")
        
    async def check_connection(self, force_refresh=False):
        """Check if the connection to Composio is valid"""
        # Use cached result if checked recently (within last 5 minutes)
        current_time = time.time()
        if not force_refresh and self.connection_status and current_time - self.connection_last_checked < 300:
            return self.connection_status
            
        if not self.is_configured:
            self.connection_status = {
                "status": "unconfigured",
                "message": "Composio credentials not configured"
            }
            return self.connection_status
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/v1/connections/{self.connection_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.connection_status = {
                            "status": "connected",
                            "connection_details": result
                        }
                    else:
                        error_text = await response.text()
                        self.connection_status = {
                            "status": "error",
                            "message": f"API request failed with status {response.status}: {error_text}"
                        }
        except Exception as e:
            self.connection_status = {
                "status": "error",
                "message": f"Error connecting to Composio: {str(e)}"
            }
            
        self.connection_last_checked = current_time
        return self.connection_status
        
    async def register_mcp_tool(self, name, description, schema):
        """Register a tool with Composio MCP"""
        if not self.is_configured:
            return {
                "success": False,
                "message": "Composio credentials not configured"
            }
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "name": name,
                "description": description,
                "schema": schema,
                "connection_id": self.connection_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/v1/tools",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status in (200, 201):
                        result = await response.json()
                        self.registered_tools[name] = result
                        return {
                            "success": True,
                            "tool": result
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "message": f"API request failed with status {response.status}: {error_text}"
                        }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error registering tool: {str(e)}"
            }
            
    async def execute_tool(self, tool_name, inputs):
        """Execute a tool using Composio"""
        if not self.is_configured:
            return {
                "success": False,
                "message": "Composio credentials not configured"
            }
            
        if tool_name not in self.registered_tools:
            return {
                "success": False,
                "message": f"Tool '{tool_name}' not registered"
            }
            
        tool_id = self.registered_tools[tool_name].get("id")
        if not tool_id:
            return {
                "success": False,
                "message": f"Tool '{tool_name}' missing ID"
            }
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": inputs,
                "connection_id": self.connection_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/v1/tools/{tool_id}/execute",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "result": result
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "message": f"API request failed with status {response.status}: {error_text}"
                        }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error executing tool: {str(e)}"
            }
            
    async def list_tools(self):
        """List all registered tools"""
        if not self.is_configured:
            return {
                "success": False,
                "message": "Composio credentials not configured",
                "tools": []
            }
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/v1/tools?connection_id={self.connection_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        # Update local registry
                        for tool in result.get("tools", []):
                            self.registered_tools[tool.get("name")] = tool
                            
                        return {
                            "success": True,
                            "tools": result.get("tools", [])
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "message": f"API request failed with status {response.status}: {error_text}",
                            "tools": []
                        }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error listing tools: {str(e)}",
                "tools": []
            }
            
    def install_cli(self, force=False):
        """Install Composio CLI"""
        try:
            # Check if CLI is already installed
            if not force:
                result = subprocess.run(["composio", "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    log.info(f"Composio CLI already installed: {result.stdout.strip()}")
                    return {
                        "success": True,
                        "message": f"Composio CLI already installed: {result.stdout.strip()}"
                    }
        except:
            pass
            
        try:
            # Install CLI
            log.info("Installing Composio CLI...")
            
            # Use pip to install
            result = subprocess.run(
                ["pip", "install", "composio-cli"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                log.info("Composio CLI installed successfully")
                return {
                    "success": True,
                    "message": "Composio CLI installed successfully"
                }
            else:
                log.error(f"Failed to install Composio CLI: {result.stderr}")
                return {
                    "success": False,
                    "message": f"Failed to install Composio CLI: {result.stderr}"
                }
        except Exception as e:
            log.error(f"Error installing Composio CLI: {str(e)}")
            return {
                "success": False,
                "message": f"Error installing Composio CLI: {str(e)}"
            }
            
    def configure_cli(self):
        """Configure Composio CLI with API key"""
        if not self.api_key:
            return {
                "success": False,
                "message": "API key not configured"
            }
            
        try:
            # Configure CLI
            log.info("Configuring Composio CLI...")
            
            # Write configuration file
            config_dir = os.path.expanduser("~/.composio")
            os.makedirs(config_dir, exist_ok=True)
            
            config = {
                "api_key": self.api_key,
                "api_url": self.base_url
            }
            
            with open(os.path.join(config_dir, "config.json"), "w") as f:
                json.dump(config, f)
                
            log.info("Composio CLI configured successfully")
            return {
                "success": True,
                "message": "Composio CLI configured successfully"
            }
        except Exception as e:
            log.error(f"Error configuring Composio CLI: {str(e)}")
            return {
                "success": False,
                "message": f"Error configuring Composio CLI: {str(e)}"
            }
            
    def run_cli_command(self, command):
        """Run a Composio CLI command"""
        try:
            result = subprocess.run(
                ["composio"] + command.split(),
                capture_output=True,
                text=True
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "code": result.returncode
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error running CLI command: {str(e)}"
            }
            
    def ensure_cli_ready(self):
        """Ensure the CLI is installed and configured"""
        install_result = self.install_cli()
        
        if not install_result["success"]:
            return install_result
            
        return self.configure_cli()

# Initialize global client
composio_client = ComposioClient()

async def test_connection():
    """Test connection to Composio API"""
    status = await composio_client.check_connection(force_refresh=True)
    print(f"Composio connection status: {json.dumps(status, indent=2)}")
    
    # List tools
    tools = await composio_client.list_tools()
    print(f"Composio tools: {json.dumps(tools, indent=2)}")
    
    return status

if __name__ == "__main__":
    # Test connection when run directly
    asyncio.run(test_connection())
