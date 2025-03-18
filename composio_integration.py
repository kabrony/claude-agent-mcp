"""
Composio Integration for OrganiX - Handles integration with Composio APIs and tools
"""
import os
import json
import asyncio
import logging
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional

try:
    import composio
    from composio.client import ComposioClient
    from composio.client.collections import TriggerEventData
except ImportError:
    logging.error("Composio SDK not installed. Please run: pip install composio-core composio-langchain")
    
# Load environment variables
load_dotenv()

class ComposioIntegration:
    def __init__(self, api_key=None):
        # Get API key from environment or parameter
        self.api_key = api_key or os.getenv("COMPOSIO_API_KEY")
        if not self.api_key:
            logging.warning("COMPOSIO_API_KEY not found in environment variables. Some features will be disabled.")
            
        # Connection IDs from the environment
        self.connection_id = os.getenv("COMPOSIO_CONNECTION_ID")
        self.integration_id = os.getenv("COMPOSIO_INTEGRATION_ID")
        
        # Initialize client if API key is available
        self.client = None
        if self.api_key:
            try:
                self.client = ComposioClient(api_key=self.api_key)
                logging.info("Composio client initialized successfully")
            except Exception as e:
                logging.error(f"Error initializing Composio client: {str(e)}")
                
        # Store available tools
        self.available_tools = {}
        
    async def initialize(self):
        """Initialize the integration and load available tools"""
        if not self.client:
            return False
            
        try:
            # Get available integrations
            self.available_tools = await self.get_available_tools()
            return True
        except Exception as e:
            logging.error(f"Error initializing Composio integration: {str(e)}")
            return False
            
    async def get_available_tools(self) -> Dict[str, Any]:
        """Get all available tools from Composio"""
        if not self.client:
            return {}
            
        try:
            # This would be replaced with the actual Composio API call when their SDK is available
            # For now, we'll mock the response based on their documentation
            tools = {
                "github": {
                    "actions": [
                        "GITHUB_GET_CODE_CHANGES_IN_PR",
                        "GITHUB_PULLS_CREATE_REVIEW_COMMENT",
                        "GITHUB_ACTIVITY_STAR_REPO_FOR_AUTHENTICATED_USER"
                    ]
                },
                "twitter": {
                    "actions": [
                        "TWITTER_POST_TWEET",
                        "TWITTER_GET_USER_TIMELINE",
                        "TWITTER_SEARCH_TWEETS"
                    ]
                },
                "slackbot": {
                    "actions": [
                        "SLACKBOT_CHAT_POST_MESSAGE",
                        "SLACKBOT_CHAT_UPDATE_MESSAGE"
                    ]
                }
            }
            
            return tools
        except Exception as e:
            logging.error(f"Error fetching available tools: {str(e)}")
            return {}
            
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Composio tool with the given parameters"""
        if not self.client:
            return {"error": "Composio client not initialized"}
            
        try:
            # This would be the actual call to execute a tool via the Composio API
            # For now, we'll mock a response based on their documentation
            logging.info(f"Executing Composio tool: {tool_name} with parameters: {parameters}")
            
            # We'll simulate different responses based on the tool
            if "GITHUB" in tool_name:
                return {"success": True, "result": "GitHub action executed successfully"}
            elif "TWITTER" in tool_name:
                return {"success": True, "result": "Twitter action executed successfully"}
            elif "SLACKBOT" in tool_name:
                return {"success": True, "result": "Slackbot message sent successfully"}
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logging.error(f"Error executing Composio tool {tool_name}: {str(e)}")
            return {"error": str(e)}
            
    async def post_tweet(self, content: str) -> Dict[str, Any]:
        """Post a tweet using Composio's Twitter integration"""
        return await self.execute_tool("TWITTER_POST_TWEET", {"content": content})
        
    async def star_github_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        """Star a GitHub repository using Composio's GitHub integration"""
        return await self.execute_tool(
            "GITHUB_ACTIVITY_STAR_REPO_FOR_AUTHENTICATED_USER", 
            {"owner": owner, "repo": repo}
        )
        
    async def send_slack_message(self, channel: str, message: str) -> Dict[str, Any]:
        """Send a Slack message using Composio's SlackBot integration"""
        return await self.execute_tool(
            "SLACKBOT_CHAT_POST_MESSAGE",
            {"channel": channel, "text": message}
        )
        
    def register_trigger(self, trigger_name: str, callback_function):
        """Register a callback for a Composio trigger event"""
        if not self.client:
            logging.error("Cannot register trigger: Composio client not initialized")
            return False
            
        try:
            # This would be the actual code to register a trigger callback
            # For now, we'll just log the information
            logging.info(f"Registered trigger {trigger_name} with callback function")
            return True
        except Exception as e:
            logging.error(f"Error registering trigger {trigger_name}: {str(e)}")
            return False
            
    def start_listening(self):
        """Start listening for Composio trigger events"""
        if not self.client:
            logging.error("Cannot start listening: Composio client not initialized")
            return False
            
        try:
            # This would be the actual code to start listening for events
            logging.info("Started listening for Composio trigger events")
            return True
        except Exception as e:
            logging.error(f"Error starting Composio listener: {str(e)}")
            return False
            
    def get_connection_status(self) -> Dict[str, Any]:
        """Get status of current Composio connections"""
        if not self.client:
            return {"status": "Not connected", "error": "Composio client not initialized"}
            
        try:
            # This would be the actual code to get connection status
            return {
                "status": "Connected",
                "connection_id": self.connection_id,
                "integration_id": self.integration_id,
                "available_tools": len(self.available_tools)
            }
        except Exception as e:
            logging.error(f"Error getting connection status: {str(e)}")
            return {"status": "Error", "error": str(e)}
            
async def test_composio():
    """Test function for Composio integration"""
    composio_integration = ComposioIntegration()
    await composio_integration.initialize()
    
    # Print available tools
    print("Available tools:", composio_integration.available_tools)
    
    # Test twitter integration
    tweet_result = await composio_integration.post_tweet("Testing OrganiX Composio integration!")
    print("Tweet result:", tweet_result)
    
    # Test GitHub integration
    star_result = await composio_integration.star_github_repo("kabrony", "claude-agent-mcp")
    print("Star result:", star_result)
    
    # Test Slack integration
    slack_result = await composio_integration.send_slack_message("general", "Hello from OrganiX!")
    print("Slack result:", slack_result)
    
if __name__ == "__main__":
    # Run test function
    asyncio.run(test_composio())
