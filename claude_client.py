"""
Claude Client - Interface for working with Claude 3.7 API
"""
import os
import json
import asyncio
import aiohttp
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ClaudeClient:
    def __init__(self, api_key=None, model="claude-3-7-sonnet-20250219"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable or api_key parameter is required")
        
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"
        self.messages = []
        
    async def send_message(self, content, system=None, max_tokens=1024):
        """Send a message to Claude and return the response"""
        # Add user message to conversation history
        self.messages.append({"role": "user", "content": content})
        
        headers = {
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "x-api-key": self.api_key
        }
        
        payload = {
            "model": self.model,
            "messages": self.messages,
            "max_tokens": max_tokens
        }
        
        if system:
            payload["system"] = system
            
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API request failed with status {response.status}: {error_text}")
                
                result = await response.json()
                assistant_message = result.get("content", [{"text": "No response from Claude"}])[0]["text"]
                
                # Add assistant response to conversation history
                self.messages.append({"role": "assistant", "content": assistant_message})
                
                return assistant_message
                
    async def stream_message(self, content, system=None, max_tokens=1024):
        """Stream a message response from Claude"""
        # Add user message to conversation history
        self.messages.append({"role": "user", "content": content})
        
        headers = {
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "x-api-key": self.api_key
        }
        
        payload = {
            "model": self.model,
            "messages": self.messages,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        if system:
            payload["system"] = system
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"API request failed with status {response.status}: {error_text}")
                        
                    full_response = ""
                    async for line in response.content:
                        if line:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data: '):
                                data = line_text[6:]  # Remove 'data: ' prefix
                                if data == "[DONE]":
                                    break
                                
                                try:
                                    chunk = json.loads(data)
                                    if chunk["type"] == "content_block_delta":
                                        content_delta = chunk["delta"].get("text", "")
                                        full_response += content_delta
                                        yield content_delta
                                except json.JSONDecodeError:
                                    pass
                                    
            # Add assistant response to conversation history
            self.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            print(f"Error streaming message: {e}")
            raise
            
    def clear_conversation(self):
        """Clear the conversation history"""
        self.messages = []
