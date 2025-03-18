"""
Enhanced Claude Client - Advanced interface for working with Claude 3.7 API
Supports conversation management, tools handling, and response analysis
"""
import os
import json
import asyncio
import aiohttp
import time
import textwrap
import re
from datetime import datetime
from dotenv import load_dotenv

# Import configuration manager
try:
    from config_manager import config_manager
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    from dotenv import load_dotenv
    load_dotenv()  # Fallback to direct env loading

class ClaudeClient:
    def __init__(self, api_key=None, model=None):
        # Get API key from config manager if available, with fallbacks
        if CONFIG_AVAILABLE:
            self.api_key = api_key or config_manager.get_api_key("anthropic")
            self.model = model or config_manager.get_current_model()
            self.base_url = config_manager.default_apis["anthropic"]["api_url"]
        else:
            # Legacy fallback
            self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            self.model = model or os.getenv("CLAUDE_MODEL", "claude-3-7-sonnet-20250219")
            self.base_url = "https://api.anthropic.com/v1"
            
        if not self.api_key:
            raise ValueError("Anthropic API key not found. Please configure it using config_manager or set ANTHROPIC_API_KEY environment variable.")
        
        self.messages = []
        self.conversations = {}
        self.current_conversation_id = None
        self.response_analytics = {
            "total_tokens": 0,
            "response_times": [],
            "average_response_time": 0,
            "requests_made": 0
        }
        
        # Initialize with a new conversation
        self.start_new_conversation()
        
    def start_new_conversation(self, title=None):
        """Start a new conversation with a fresh message history"""
        conversation_id = f"conv_{int(time.time())}"
        
        if title is None:
            title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
        self.conversations[conversation_id] = {
            "id": conversation_id,
            "title": title,
            "messages": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.current_conversation_id = conversation_id
        self.messages = []
        
        return conversation_id
        
    def switch_conversation(self, conversation_id):
        """Switch to an existing conversation"""
        if conversation_id not in self.conversations:
            return False
            
        self.current_conversation_id = conversation_id
        self.messages = self.conversations[conversation_id]["messages"]
        return True
        
    def get_conversations(self):
        """Get list of all conversations"""
        return [
            {
                "id": conv_id,
                "title": conv["title"],
                "message_count": len(conv["messages"]),
                "created_at": conv["created_at"],
                "updated_at": conv["updated_at"]
            }
            for conv_id, conv in self.conversations.items()
        ]
        
    def _save_message(self, role, content):
        """Save message to current conversation"""
        message = {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        
        # Add to current messages list
        self.messages.append({"role": role, "content": content})
        
        # If in a conversation, save to that too
        if self.current_conversation_id and self.current_conversation_id in self.conversations:
            self.conversations[self.current_conversation_id]["messages"].append(message)
            self.conversations[self.current_conversation_id]["updated_at"] = datetime.now().isoformat()
            
    async def send_message(self, content, system=None, max_tokens=1024):
        """Send a message to Claude and return the response"""
        # Check if API key is available
        if not self.api_key and CONFIG_AVAILABLE:
            # Try to get API key again (in case it was added since initialization)
            self.api_key = config_manager.get_api_key("anthropic")
            if not self.api_key:
                return "API key not configured. Please run the configuration manager to set up your API keys."
        
        # Add user message to conversation history
        self._save_message("user", content)
        
        start_time = time.time()
        
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
                    error_message = f"API request failed with status {response.status}: {error_text}"
                    
                    # Add error message to conversation
                    self._save_message("system", f"Error: {error_message}")
                    
                    raise Exception(error_message)
                
                result = await response.json()
                
                # Extract and save assistant message
                assistant_message = result.get("content", [{"text": "No response from Claude"}])[0]["text"]
                self._save_message("assistant", assistant_message)
                
                # Update analytics
                elapsed_time = time.time() - start_time
                self.response_analytics["response_times"].append(elapsed_time)
                self.response_analytics["average_response_time"] = sum(self.response_analytics["response_times"]) / len(self.response_analytics["response_times"])
                self.response_analytics["requests_made"] += 1
                self.response_analytics["total_tokens"] += result.get("usage", {}).get("output_tokens", 0) + result.get("usage", {}).get("input_tokens", 0)
                
                return assistant_message
                
    async def stream_message(self, content, system=None, max_tokens=1024):
        """Stream a message response from Claude"""
        # Check if API key is available
        if not self.api_key and CONFIG_AVAILABLE:
            # Try to get API key again
            self.api_key = config_manager.get_api_key("anthropic")
            if not self.api_key:
                yield "API key not configured. Please run the configuration manager to set up your API keys."
                return
        
        # Add user message to conversation history
        self._save_message("user", content)
        
        start_time = time.time()
        
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
                        error_message = f"API request failed with status {response.status}: {error_text}"
                        yield f"Error: {error_message}"
                        return
                        
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
            self._save_message("assistant", full_response)
            
            # Update analytics
            elapsed_time = time.time() - start_time
            self.response_analytics["response_times"].append(elapsed_time)
            self.response_analytics["average_response_time"] = sum(self.response_analytics["response_times"]) / len(self.response_analytics["response_times"])
            self.response_analytics["requests_made"] += 1
            # Can't get exact token count from streaming response
            self.response_analytics["total_tokens"] += len(content) // 4 + len(full_response) // 4  # Rough estimate
            
        except Exception as e:
            error_message = f"Error streaming message: {str(e)}"
            self._save_message("system", f"Error: {error_message}")
            yield f"Error: {error_message}"
            
    async def send_message_with_tools(self, content, tools, system=None, max_tokens=1024):
        """Send a message to Claude with tools and handle tool execution"""
        # Check if API key is available
        if not self.api_key and CONFIG_AVAILABLE:
            # Try to get API key again
            self.api_key = config_manager.get_api_key("anthropic")
            if not self.api_key:
                return "API key not configured. Please run the configuration manager to set up your API keys."
        
        # Add user message to conversation history
        self._save_message("user", content)
        
        start_time = time.time()
        
        headers = {
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "x-api-key": self.api_key
        }
        
        # Format tools for Claude API
        formatted_tools = [
            {
                "name": name,
                "description": tool["description"],
                "input_schema": tool["input_schema"]
            }
            for name, tool in tools.items()
        ]
        
        payload = {
            "model": self.model,
            "messages": self.messages,
            "max_tokens": max_tokens,
            "tools": formatted_tools
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
                    error_message = f"API request failed with status {response.status}: {error_text}"
                    self._save_message("system", f"Error: {error_message}")
                    raise Exception(error_message)
                
                result = await response.json()
                
                # Handle tool calls if present
                tool_calls = []
                tool_results = []
                
                for content_block in result.get("content", []):
                    if content_block.get("type") == "tool_use":
                        tool_name = content_block.get("name")
                        tool_input = content_block.get("input", {})
                        tool_id = content_block.get("id")
                        
                        if tool_name in tools:
                            # Execute the tool
                            tool_function = tools[tool_name]["function"]
                            try:
                                tool_output = await tool_function(**tool_input)
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_call_id": tool_id,
                                    "content": tool_output
                                })
                            except Exception as e:
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_call_id": tool_id,
                                    "content": f"Error executing tool: {str(e)}"
                                })
                        
                        tool_calls.append({
                            "name": tool_name,
                            "input": tool_input,
                            "id": tool_id
                        })
                    
                # If there were tool calls, send a follow-up request with results
                if tool_calls:
                    follow_up_messages = self.messages.copy()
                    
                    # Add assistant message with tool calls
                    follow_up_messages.append({
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "name": tc["name"],
                                "input": tc["input"],
                                "id": tc["id"]
                            }
                            for tc in tool_calls
                        ]
                    })
                    
                    # Add tool results
                    follow_up_messages.append({
                        "role": "user",
                        "content": tool_results
                    })
                    
                    # Send follow-up request
                    follow_up_payload = {
                        "model": self.model,
                        "messages": follow_up_messages,
                        "max_tokens": max_tokens,
                    }
                    
                    if system:
                        follow_up_payload["system"] = system
                        
                    async with session.post(
                        f"{self.base_url}/messages",
                        headers=headers,
                        json=follow_up_payload
                    ) as follow_up_response:
                        if follow_up_response.status != 200:
                            error_text = await follow_up_response.text()
                            error_message = f"API request failed with status {follow_up_response.status}: {error_text}"
                            self._save_message("system", f"Error: {error_message}")
                            raise Exception(error_message)
                        
                        follow_up_result = await follow_up_response.json()
                        
                        # Extract final response
                        final_text = ""
                        for content_block in follow_up_result.get("content", []):
                            if content_block.get("type") == "text":
                                final_text += content_block.get("text", "")
                        
                        # Save the entire conversation including tool usage
                        tool_call_message = {
                            "role": "assistant", 
                            "content": f"[Tool calls: {', '.join(tc['name'] for tc in tool_calls)}]"
                        }
                        self.messages.append(tool_call_message)
                        
                        tool_result_message = {
                            "role": "system", 
                            "content": f"[Tool results processed]"
                        }
                        self.messages.append(tool_result_message)
                        
                        # Save final response
                        self._save_message("assistant", final_text)
                        
                        # Update analytics
                        elapsed_time = time.time() - start_time
                        self.response_analytics["response_times"].append(elapsed_time)
                        self.response_analytics["average_response_time"] = sum(self.response_analytics["response_times"]) / len(self.response_analytics["response_times"])
                        self.response_analytics["requests_made"] += 2  # Count both requests
                        self.response_analytics["total_tokens"] += follow_up_result.get("usage", {}).get("output_tokens", 0) + follow_up_result.get("usage", {}).get("input_tokens", 0)
                        
                        return final_text
                else:
                    # No tool calls, just extract the normal response
                    response_text = ""
                    for content_block in result.get("content", []):
                        if content_block.get("type") == "text":
                            response_text += content_block.get("text", "")
                    
                    # Save assistant response
                    self._save_message("assistant", response_text)
                    
                    # Update analytics
                    elapsed_time = time.time() - start_time
                    self.response_analytics["response_times"].append(elapsed_time)
                    self.response_analytics["average_response_time"] = sum(self.response_analytics["response_times"]) / len(self.response_analytics["response_times"])
                    self.response_analytics["requests_made"] += 1
                    self.response_analytics["total_tokens"] += result.get("usage", {}).get("output_tokens", 0) + result.get("usage", {}).get("input_tokens", 0)
                    
                    return response_text
    
    async def send_extended_thinking_message(self, content, system=None, max_tokens=4096):
        """Send a message to Claude with extended reasoning mode"""
        # Craft a system prompt that encourages step-by-step thinking
        extended_system = """
        Take your time to think through this problem step by step. 
        First, break down the query into its key components.
        Then, analyze each component carefully, considering different angles and perspectives.
        Evaluate multiple approaches before deciding on the best one.
        Show your reasoning process clearly, explaining why certain approaches work better than others.
        Finally, synthesize your analysis into a comprehensive, well-reasoned response.
        """
        
        if system:
            extended_system = f"{system}\n\n{extended_system}"
            
        # Add user message to conversation history
        self._save_message("user", content)
        
        # Send with the extended thinking prompt
        result = await self.send_message(content, system=extended_system, max_tokens=max_tokens)
        
        return result
    
    def analyze_response(self, response):
        """Analyze a response for sentiment, readability, and key information"""
        analysis = {
            "length": len(response),
            "paragraph_count": len(re.split(r'\n\s*\n', response)),
            "sentence_count": len(re.split(r'[.!?]+', response)),
            "word_count": len(response.split())
        }
        
        # Calculate readability (simple Flesch-Kincaid approximation)
        if analysis["sentence_count"] > 0:
            words_per_sentence = analysis["word_count"] / analysis["sentence_count"]
            # Approximate average syllables per word
            syllables_per_word = 1.5  
            analysis["readability_score"] = 206.835 - (1.015 * words_per_sentence) - (84.6 * syllables_per_word)
        else:
            analysis["readability_score"] = 0
            
        # Extract likely key points (simple heuristic based on sentence length and position)
        sentences = re.split(r'(?<=[.!?])\s+', response)
        
        # Sentences at beginning, end, or with keywords like "important", "key", "significant" are likely key points
        key_sentences = []
        for i, sentence in enumerate(sentences):
            if i < 2 or i > len(sentences) - 3:  # First or last two sentences
                key_sentences.append(sentence)
            elif any(keyword in sentence.lower() for keyword in ["important", "key", "significant", "critical", "essential"]):
                key_sentences.append(sentence)
            elif len(sentence.split()) > 20:  # Longer sentences often contain key information
                key_sentences.append(sentence)
                
        analysis["key_points"] = key_sentences
        
        # Detect sentiment (very basic approach)
        positive_words = ["good", "great", "excellent", "positive", "wonderful", "beneficial", "recommend", "advantage"]
        negative_words = ["bad", "poor", "negative", "terrible", "harmful", "avoid", "disadvantage", "problem"]
        
        word_count = len(response.split())
        positive_count = sum(1 for word in positive_words if word in response.lower())
        negative_count = sum(1 for word in negative_words if word in response.lower())
        
        if positive_count > negative_count:
            analysis["sentiment"] = "positive"
        elif negative_count > positive_count:
            analysis["sentiment"] = "negative"
        else:
            analysis["sentiment"] = "neutral"
            
        return analysis
        
    def save_conversation_to_file(self, conversation_id=None, filename=None):
        """Save a conversation to a JSON file"""
        if conversation_id is None:
            conversation_id = self.current_conversation_id
            
        if conversation_id not in self.conversations:
            return False
            
        conversation = self.conversations[conversation_id]
        
        if filename is None:
            safe_title = re.sub(r'[^\w\s-]', '', conversation["title"]).strip().lower()
            safe_title = re.sub(r'[-\s]+', '-', safe_title)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{safe_title}_{timestamp}.json"
            
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(filename)) or '.', exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(conversation, f, indent=2)
            return filename
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return False
            
    def load_conversation_from_file(self, filename):
        """Load a conversation from a JSON file"""
        try:
            with open(filename, 'r') as f:
                conversation = json.load(f)
                
            # Validate basic structure
            if not all(key in conversation for key in ["id", "title", "messages"]):
                return False
                
            # Add to conversations
            self.conversations[conversation["id"]] = conversation
            
            # Switch to this conversation
            self.switch_conversation(conversation["id"])
            
            return conversation["id"]
        except Exception as e:
            print(f"Error loading conversation: {e}")
            return False
    
    def get_analytics(self):
        """Get analytics about API usage"""
        return {
            "total_requests": self.response_analytics["requests_made"],
            "total_tokens": self.response_analytics["total_tokens"],
            "average_response_time": self.response_analytics["average_response_time"],
            "total_conversations": len(self.conversations),
            "total_messages": sum(len(conv["messages"]) for conv in self.conversations.values()),
            "current_model": self.model
        }
        
    def clear_conversation(self):
        """Clear the current conversation history"""
        self.messages = []
        
        if self.current_conversation_id and self.current_conversation_id in self.conversations:
            self.conversations[self.current_conversation_id]["messages"] = []
            self.conversations[self.current_conversation_id]["updated_at"] = datetime.now().isoformat()
            
    def summarize_conversation(self, conversation_id=None):
        """Generate a summary of the conversation"""
        if conversation_id is None:
            conversation_id = self.current_conversation_id
            
        if conversation_id not in self.conversations:
            return None
            
        conversation = self.conversations[conversation_id]
        messages = conversation["messages"]
        
        if not messages:
            return "No messages in conversation."
            
        # Create summary
        user_message_count = sum(1 for m in messages if m.get("role") == "user")
        assistant_message_count = sum(1 for m in messages if m.get("role") == "assistant")
        
        first_user_message = next((m.get("content") for m in messages if m.get("role") == "user"), "")
        first_user_message_preview = first_user_message[:100] + "..." if len(first_user_message) > 100 else first_user_message
        
        # Extract main topics (simple approach)
        all_text = " ".join([m.get("content", "") for m in messages])
        words = all_text.lower().split()
        word_counts = {}
        
        for word in words:
            if len(word) > 3 and word not in ["this", "that", "with", "from", "have", "what", "your", "would"]:
                word_counts[word] = word_counts.get(word, 0) + 1
                
        top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        summary = {
            "title": conversation["title"],
            "message_count": len(messages),
            "user_messages": user_message_count,
            "assistant_messages": assistant_message_count,
            "created_at": conversation["created_at"],
            "updated_at": conversation["updated_at"],
            "first_user_message": first_user_message_preview,
            "likely_topics": [word for word, count in top_words]
        }
        
        return summary
        
    def change_model(self, new_model):
        """Change the Claude model being used"""
        if CONFIG_AVAILABLE:
            # Update in config manager
            if config_manager.set_current_model(new_model):
                self.model = new_model
                return True
        else:
            # Just update locally
            self.model = new_model
            return True
            
        return False
        
    def get_available_models(self):
        """Get information about available Claude models"""
        if CONFIG_AVAILABLE:
            return config_manager.get_model_info()
        else:
            # Hardcoded fallback
            return {
                "claude-3-7-sonnet-20250219": {
                    "name": "Claude 3.7 Sonnet",
                    "description": "Latest Claude model with enhanced reasoning"
                },
                "claude-3-opus-20240229": {
                    "name": "Claude 3 Opus",
                    "description": "Most capable Claude model for complex tasks"
                },
                "claude-3-sonnet-20240229": {
                    "name": "Claude 3 Sonnet",
                    "description": "Balanced Claude model for general tasks"
                },
                "claude-3-haiku-20240307": {
                    "name": "Claude 3 Haiku",
                    "description": "Fast, efficient Claude model"
                }
            }

async def main():
    """Test the Claude client"""
    client = ClaudeClient()
    
    print(f"Using model: {client.model}")
    print("Available models:")
    for model_id, info in client.get_available_models().items():
        print(f"- {info['name']} ({model_id})")
        
    query = "Hello! Can you tell me about yourself?"
    print(f"\nSending query: {query}")
    
    response = await client.send_message(query)
    print(f"\nResponse: {response[:200]}...")
    
    analytics = client.get_analytics()
    print("\nAnalytics:")
    for key, value in analytics.items():
        print(f"- {key}: {value}")
        
    print("\nConversation summary:")
    summary = client.summarize_conversation()
    for key, value in summary.items():
        print(f"- {key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())
