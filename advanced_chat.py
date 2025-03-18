"""
Advanced AI Chat - Next-generation chat capabilities with context awareness and multi-agent coordination
"""
import os
import json
import asyncio
import aiohttp
import time
import uuid
import re
from datetime import datetime
from dotenv import load_dotenv
from utils import log
from claude_client import ClaudeClient
from memory_system import MemorySystem

# Import integrations if available
try:
    from blockchain_integration import solana_integration, zk_proofs
    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    BLOCKCHAIN_AVAILABLE = False
    
try:
    from composio_integration import composio_client
    COMPOSIO_AVAILABLE = True
except ImportError:
    COMPOSIO_AVAILABLE = False

# Load environment variables
load_dotenv()

class ChatPersona:
    """Represents a specific chat persona with its own characteristics"""
    def __init__(self, name, description, system_prompt, voice=None):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.voice = voice
        self.created_at = datetime.now().isoformat()
        self.id = str(uuid.uuid4())
        
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "voice": self.voice,
            "created_at": self.created_at
        }
        
    @classmethod
    def from_dict(cls, data):
        persona = cls(
            name=data.get("name", "Unknown"),
            description=data.get("description", ""),
            system_prompt=data.get("system_prompt", ""),
            voice=data.get("voice")
        )
        persona.id = data.get("id", str(uuid.uuid4()))
        persona.created_at = data.get("created_at", datetime.now().isoformat())
        return persona

class ChatIntent:
    """Identifies and tracks user intent in conversations"""
    def __init__(self, text=None):
        self.text = text
        self.confidence = 0.0
        self.detected_intents = {}
        self.primary_intent = None
        
        # Process intent if text is provided
        if text:
            self.analyze_intent(text)
    
    def analyze_intent(self, text):
        """Analyze text to detect intent"""
        self.text = text
        
        # Simple keyword-based intent detection
        # In a real implementation, this would use a more sophisticated NLP approach
        intent_patterns = {
            "question": r"\b(?:who|what|when|where|why|how|is|are|can|could|would|should|do|does|did)\b.+\?",
            "command": r"\b(?:please|can you|would you|i want|i need|make|create|show|find|get|search|help)\b",
            "chat": r"\b(?:hi|hello|hey|howdy|greetings|good morning|good afternoon|good evening)\b",
            "feedback": r"\b(?:thanks|thank you|good|great|excellent|awesome|terrible|bad|poor|not good|not helpful)\b",
            "blockchain": r"\b(?:solana|phantom|wallet|blockchain|crypto|nft|token|transaction|eth|bitcoin|btc)\b",
            "web_search": r"\b(?:search|find|look up|google|information about|latest|news|current)\b",
            "agent_action": r"\b(?:run|execute|perform|start|activate)\b"
        }
        
        # Check each pattern
        for intent, pattern in intent_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                # Simple scoring based on pattern match
                matches = re.findall(pattern, text, re.IGNORECASE)
                score = len(matches) / len(text.split())
                self.detected_intents[intent] = score
                
        # Determine primary intent
        if self.detected_intents:
            self.primary_intent = max(self.detected_intents.items(), key=lambda x: x[1])[0]
            self.confidence = self.detected_intents[self.primary_intent]
            
        return self.primary_intent
        
    def to_dict(self):
        return {
            "text": self.text,
            "confidence": self.confidence,
            "detected_intents": self.detected_intents,
            "primary_intent": self.primary_intent
        }

class MultiAgentCoordinator:
    """Coordinates multiple specialized agents"""
    def __init__(self, memory_system=None):
        self.memory = memory_system or MemorySystem()
        self.claude_client = ClaudeClient()
        
        # Agent instances
        self.agents = {}
        self.create_default_agents()
        
        # Integration checks
        self.blockchain_available = BLOCKCHAIN_AVAILABLE
        self.composio_available = COMPOSIO_AVAILABLE
        
        # Agent coordination stats
        self.coordination_stats = {
            "total_requests": 0,
            "agent_usage": {},
            "intent_distribution": {},
            "avg_response_time": 0
        }
        
    def create_default_agents(self):
        """Create default specialized agents"""
        # Research agent
        self.register_agent(
            "researcher",
            ChatPersona(
                name="Research Specialist",
                description="Specialized in deep research and information synthesis",
                system_prompt="""You are a Research Specialist agent within OrganiX.
Your primary role is to conduct thorough research on topics and provide comprehensive information.
Always cite your sources and consider multiple perspectives on complex topics.
When answering questions, prioritize accuracy, thoroughness, and objectivity."""
            )
        )
        
        # Coding agent
        self.register_agent(
            "coder",
            ChatPersona(
                name="Code Specialist",
                description="Specialized in generating high-quality code solutions",
                system_prompt="""You are a Code Specialist agent within OrganiX.
Your primary role is to generate efficient, well-documented code solutions.
When writing code, focus on best practices, maintainability, and performance.
Explain your approach clearly and provide context for your implementation decisions."""
            )
        )
        
        # Blockchain agent
        if self.blockchain_available:
            self.register_agent(
                "blockchain",
                ChatPersona(
                    name="Blockchain Specialist",
                    description="Specialized in blockchain technology and decentralized applications",
                    system_prompt="""You are a Blockchain Specialist agent within OrganiX.
Your primary role is to provide expertise on blockchain technology, focusing on Solana.
You can help with wallet connections, NFTs, token information, and transaction analysis.
When discussing blockchain topics, prioritize technical accuracy and security."""
                )
            )
            
        # MCP Integration Specialist
        self.register_agent(
            "mcp_specialist",
            ChatPersona(
                name="MCP Integration Specialist",
                description="Specialized in Model Context Protocol for tool integration",
                system_prompt="""You are an MCP Integration Specialist agent within OrganiX.
Your primary role is to help users effectively utilize tools through the Model Context Protocol.
You understand how to integrate various tools and APIs into conversational AI.
Provide detailed guidance on MCP implementation, best practices, and advanced usage patterns."""
            )
        )
        
        # AGI Reasoning Agent
        self.register_agent(
            "agi_reasoner",
            ChatPersona(
                name="AGI Reasoning Specialist",
                description="Specialized in complex reasoning and advanced cognition",
                system_prompt="""You are an AGI Reasoning Specialist within OrganiX.
Your primary role is to tackle complex problems requiring advanced reasoning capabilities.
You excel at breaking down complicated scenarios into manageable components.
Use chain-of-thought reasoning, analogical thinking, and first-principles analysis in your responses.
When addressing complex topics, show your reasoning process explicitly and consider multiple perspectives."""
            )
        )
        
    def register_agent(self, agent_id, persona):
        """Register a new specialized agent"""
        self.agents[agent_id] = persona
        self.coordination_stats["agent_usage"][agent_id] = 0
        log.info(f"Registered agent: {persona.name} with ID {agent_id}")
        
    async def route_to_best_agent(self, query):
        """Route a query to the most appropriate agent"""
        # Analyze intent
        intent = ChatIntent(query)
        log.info(f"Detected intent: {intent.primary_intent} (confidence: {intent.confidence:.2f})")
        
        # Update stats
        self.coordination_stats["total_requests"] += 1
        if intent.primary_intent in self.coordination_stats["intent_distribution"]:
            self.coordination_stats["intent_distribution"][intent.primary_intent] += 1
        else:
            self.coordination_stats["intent_distribution"][intent.primary_intent] = 1
        
        start_time = time.time()
        
        # Route based on intent
        result = None
        if intent.primary_intent == "blockchain" and "blockchain" in self.agents:
            result = await self.process_with_agent("blockchain", query)
        elif intent.primary_intent == "web_search" and "researcher" in self.agents:
            result = await self.process_with_agent("researcher", query)
        elif intent.primary_intent in ["command", "agent_action"] and "coder" in self.agents:
            result = await self.process_with_agent("coder", query)
        elif "mcp" in query.lower() and "mcp_specialist" in self.agents:
            result = await self.process_with_agent("mcp_specialist", query)
        elif any(term in query.lower() for term in ["complex", "reasoning", "agi", "cognitive", "think", "analyze"]) and "agi_reasoner" in self.agents:
            result = await self.process_with_agent("agi_reasoner", query)
        
        # Default to researcher for questions or no clear intent
        if result is None:
            if "researcher" in self.agents:
                result = await self.process_with_agent("researcher", query)
            else:
                # Fallback to general processing
                result = await self.process_query(query)
        
        # Update response time stats
        elapsed_time = time.time() - start_time
        response_times = self.coordination_stats.get("response_times", [])
        response_times.append(elapsed_time)
        self.coordination_stats["response_times"] = response_times
        self.coordination_stats["avg_response_time"] = sum(response_times) / len(response_times)
        
        return result
    
    async def process_with_agent(self, agent_id, query):
        """Process a query with a specific agent"""
        if agent_id not in self.agents:
            return {
                "success": False,
                "message": f"Agent {agent_id} not found",
                "response": "I don't have that specialized agent available. Let me try to help you directly."
            }
        
        persona = self.agents[agent_id]
        
        # Update stats
        self.coordination_stats["agent_usage"][agent_id] += 1
        
        # Add agent information to memory
        memory_id = self.memory.add_memory(
            "episodic", 
            query, 
            {
                "type": "agent_query",
                "agent_id": agent_id,
                "agent_name": persona.name
            },
            importance=3
        )
        
        # Process with Claude using agent's system prompt
        try:
            response = await self.claude_client.send_message(
                query,
                system=persona.system_prompt,
                max_tokens=4096
            )
            
            # Store response in memory
            self.memory.add_memory(
                "episodic",
                response,
                {
                    "type": "agent_response",
                    "agent_id": agent_id,
                    "agent_name": persona.name,
                    "query_memory_id": memory_id
                },
                importance=3
            )
            
            return {
                "success": True,
                "agent_id": agent_id,
                "agent_name": persona.name,
                "response": response
            }
        except Exception as e:
            log.error(f"Error processing with agent {agent_id}: {str(e)}")
            return {
                "success": False,
                "message": f"Error processing with agent: {str(e)}",
                "response": "I encountered an error while processing your request. Please try again."
            }
    
    async def process_query(self, query, system_prompt=None):
        """Process a general query"""
        # Store query in memory
        memory_id = self.memory.add_memory(
            "episodic",
            query,
            {"type": "user_query"},
            importance=2
        )
        
        # Generate default system prompt if not provided
        if not system_prompt:
            system_prompt = """You are OrganiX, an advanced AI assistant with multiple specialized capabilities.
You can research information, generate code, and analyze a variety of inputs.
When responding, prioritize accuracy, clarity, and helpfulness."""
        
        # Process with Claude
        try:
            response = await self.claude_client.send_message(
                query,
                system=system_prompt,
                max_tokens=4096
            )
            
            # Store response in memory
            self.memory.add_memory(
                "episodic",
                response,
                {
                    "type": "agent_response",
                    "query_memory_id": memory_id
                },
                importance=2
            )
            
            return {
                "success": True,
                "response": response
            }
        except Exception as e:
            log.error(f"Error processing query: {str(e)}")
            return {
                "success": False,
                "message": f"Error processing query: {str(e)}",
                "response": "I encountered an error while processing your request. Please try again."
            }
    
    async def process_with_context_awareness(self, query, context=None):
        """Process a query with enhanced context awareness"""
        # Analyze intent
        intent = ChatIntent(query)
        
        # Build context from memory if not provided
        if not context:
            # Get relevant memories
            relevant_memories = self.memory.retrieve_relevant(query, limit=5)
            
            # Format for context
            context = "\nContext from previous interactions:\n"
            for memory, metadata in relevant_memories:
                memory_type = metadata.get("type", "general")
                timestamp = metadata.get("timestamp", "")
                
                if memory_type == "user_query":
                    context += f"User asked ({timestamp}): {memory}\n"
                elif memory_type in ["agent_response", "assistant_response"]:
                    context += f"Assistant responded ({timestamp}): {memory[:100]}...\n"
                else:
                    context += f"Related information ({memory_type}): {memory[:100]}...\n"
        
        # Combine query with context for enhanced processing
        enhanced_query = f"{query}\n\n{context}"
        
        # Route to best agent with context
        return await self.route_to_best_agent(enhanced_query)
    
    async def get_blockchain_data(self, address):
        """Get blockchain data for an address"""
        if not self.blockchain_available:
            return {
                "success": False,
                "message": "Blockchain integration not available"
            }
            
        try:
            # Parallel execution of blockchain queries
            balance_task = asyncio.create_task(solana_integration.get_solana_balance(address))
            tokens_task = asyncio.create_task(solana_integration.get_solana_token_accounts(address))
            nfts_task = asyncio.create_task(solana_integration.get_nfts_by_owner(address))
            
            # Wait for all tasks to complete
            balance = await balance_task
            tokens = await tokens_task
            nfts = await nfts_task
            
            # Combine results
            return {
                "success": True,
                "address": address,
                "balance": balance.get("balance", {}),
                "tokens": {
                    "count": len(tokens.get("token_accounts", [])),
                    "accounts": tokens.get("token_accounts", [])
                },
                "nfts": {
                    "count": len(nfts.get("nfts", [])),
                    "items": nfts.get("nfts", [])
                }
            }
        except Exception as e:
            log.error(f"Error getting blockchain data: {str(e)}")
            return {
                "success": False,
                "message": f"Error getting blockchain data: {str(e)}"
            }
    
    def get_phantom_connect_html(self, dapp_name="OrganiX Dashboard"):
        """Get HTML for Phantom wallet connection"""
        if not self.blockchain_available:
            return "<p>Blockchain integration not available</p>"
            
        return solana_integration.create_agent_wallet_button_html(dapp_name)
    
    async def create_zero_knowledge_proof(self, data_type, data):
        """Create a zero-knowledge proof"""
        if not self.blockchain_available:
            return {
                "success": False,
                "message": "ZK integration not available"
            }
            
        if data_type == "knowledge":
            return await zk_proofs.create_proof_of_knowledge(data)
        elif data_type == "ownership":
            # For ownership proofs, data should be a dict with address and asset_id
            if isinstance(data, dict) and "address" in data and "asset_id" in data:
                return await zk_proofs.create_proof_of_ownership(data["address"], data["asset_id"])
            else:
                return {
                    "success": False,
                    "message": "Invalid data format for ownership proof"
                }
        else:
            return {
                "success": False,
                "message": f"Unknown proof type: {data_type}"
            }
    
    async def verify_zero_knowledge_proof(self, proof, public_input=None):
        """Verify a zero-knowledge proof"""
        if not self.blockchain_available:
            return {
                "success": False,
                "message": "ZK integration not available"
            }
            
        return zk_proofs.verify_proof(proof, public_input)
    
    def get_coordination_stats(self):
        """Get statistics about agent coordination"""
        return self.coordination_stats
    
    async def collaborative_reasoning(self, query, agents=None):
        """Use multiple agents collaboratively for complex reasoning"""
        if not agents:
            # Default to using all available agents for collaborative reasoning
            agents = list(self.agents.keys())
        
        # Store query in memory
        memory_id = self.memory.add_memory(
            "episodic",
            query,
            {"type": "collaborative_query"},
            importance=4
        )
        
        # Get responses from each agent in parallel
        agent_tasks = {}
        for agent_id in agents:
            if agent_id in self.agents:
                # Create a task for each agent
                task = asyncio.create_task(self.process_with_agent(agent_id, query))
                agent_tasks[agent_id] = task
        
        # Wait for all agents to complete
        agent_responses = {}
        for agent_id, task in agent_tasks.items():
            result = await task
            agent_responses[agent_id] = result
        
        # Create a summary prompt combining all perspectives
        synthesis_prompt = f"""Original query: {query}

I have received perspectives from multiple specialized agents. Please synthesize these perspectives into a comprehensive response.

"""
        for agent_id, result in agent_responses.items():
            if result.get("success", False):
                agent_name = result.get("agent_name", agent_id)
                response = result.get("response", "No response")
                synthesis_prompt += f"\n{agent_name}'s perspective:\n{response[:500]}...\n"
        
        synthesis_prompt += "\nPlease create a unified response that incorporates the insights from all specialists and resolves any contradictions."
        
        # Get the agi_reasoner to synthesize if available, otherwise use general processing
        if "agi_reasoner" in self.agents:
            synthesis = await self.process_with_agent("agi_reasoner", synthesis_prompt)
        else:
            synthesis = await self.process_query(synthesis_prompt)
        
        # Store the collaborative result
        self.memory.add_memory(
            "episodic",
            synthesis.get("response", "Synthesis failed"),
            {
                "type": "collaborative_response",
                "query_memory_id": memory_id,
                "participating_agents": list(agent_responses.keys())
            },
            importance=4
        )
        
        return {
            "success": synthesis.get("success", False),
            "response": synthesis.get("response", "Collaborative reasoning failed"),
            "agent_responses": agent_responses
        }
    
    async def process_with_mcp_tools(self, query, tool_names=None):
        """Process a query using specific MCP tools"""
        if not self.composio_available:
            return {
                "success": False,
                "message": "Composio integration not available",
                "response": "I cannot access MCP tools at the moment. Let me try to help you directly."
            }
        
        # Use MCP specialist if available
        if "mcp_specialist" in self.agents:
            system_prompt = self.agents["mcp_specialist"].system_prompt
        else:
            system_prompt = """You are OrganiX, an advanced AI assistant that can use Model Context Protocol tools.
When using tools, clearly indicate which tool you're using and why.
Provide thoughtful, helpful responses based on the tool outputs."""
        
        # Store query in memory
        memory_id = self.memory.add_memory(
            "episodic",
            query,
            {
                "type": "mcp_query",
                "tools": tool_names
            },
            importance=3
        )
        
        try:
            # Get available tools
            tools_result = await composio_client.list_tools()
            available_tools = {t["name"]: t for t in tools_result.get("tools", [])}
            
            # Filter to requested tools if specified
            if tool_names:
                tools = {k: v for k, v in available_tools.items() if k in tool_names}
            else:
                tools = available_tools
            
            # If no tools available, fall back to regular processing
            if not tools:
                return await self.process_query(
                    query, 
                    system_prompt=f"{system_prompt}\nNote: No MCP tools are available for this request."
                )
            
            # Execute query with tools
            tool_descriptions = "\n".join([f"- {name}: {tool.get('description', 'No description')}" for name, tool in tools.items()])
            enhanced_system_prompt = f"{system_prompt}\n\nAvailable tools:\n{tool_descriptions}"
            
            # Use the MCP client to process with tools
            results = await composio_client.process_with_tools(query)
            
            # Process results with Claude for a coherent response
            result_prompt = f"""Original query: {query}

Tool results:
{json.dumps(results, indent=2)}

Please analyze these results and provide a helpful, coherent response to the original query."""
            
            response = await self.claude_client.send_message(
                result_prompt,
                system=enhanced_system_prompt,
                max_tokens=4096
            )
            
            # Store response in memory
            self.memory.add_memory(
                "episodic",
                response,
                {
                    "type": "mcp_response",
                    "query_memory_id": memory_id,
                    "tools_used": list(tools.keys())
                },
                importance=3
            )
            
            return {
                "success": True,
                "response": response,
                "tool_results": results
            }
        except Exception as e:
            log.error(f"Error processing with MCP tools: {str(e)}")
            return {
                "success": False,
                "message": f"Error processing with MCP tools: {str(e)}",
                "response": "I encountered an error while using tools to process your request. Please try again."
            }
    
    def get_agi_capabilities_info(self):
        """Get information about AGI capabilities"""
        capabilities = {
            "multi_agent_coordination": {
                "description": "Coordinates multiple specialized agents for optimal response generation",
                "agent_count": len(self.agents),
                "available_agents": list(self.agents.keys())
            },
            "context_awareness": {
                "description": "Maintains context across conversation turns using memory system",
                "memory_types": ["episodic", "semantic", "procedural"],
                "context_window": "Unlimited through memory retrieval"
            },
            "collaborative_reasoning": {
                "description": "Multiple agents collaborate on complex reasoning tasks",
                "synthesis": "AGI reasoner synthesizes perspectives"
            },
            "blockchain_integration": {
                "available": self.blockchain_available,
                "features": ["Solana account data", "NFT ownership", "Phantom wallet integration", "ZK proofs"]
            },
            "mcp_integration": {
                "available": self.composio_available,
                "description": "Model Context Protocol for tool integration"
            }
        }
        
        return capabilities

# Initialize coordinator for use
coordinator = MultiAgentCoordinator()

async def test_coordinator():
    """Test the multi-agent coordinator"""
    print("Testing multi-agent coordinator...")
    
    # Test basic query
    query = "What are the latest advancements in artificial intelligence?"
    print(f"Testing query: {query}")
    
    result = await coordinator.route_to_best_agent(query)
    print(f"Response from agent: {result.get('agent_name', 'Unknown')}")
    print(f"Response snippet: {result.get('response', 'No response')[:100]}...")
    
    # Test collaborative reasoning
    collab_query = "Compare and contrast traditional finance with DeFi on Solana"
    print(f"Testing collaborative reasoning: {collab_query}")
    
    collab_result = await coordinator.collaborative_reasoning(collab_query)
    print(f"Collaborative response snippet: {collab_result.get('response', 'No response')[:100]}...")
    
    # Print stats
    print("Coordination stats:")
    print(json.dumps(coordinator.get_coordination_stats(), indent=2))
    
    return {
        "basic_query": result,
        "collaborative_reasoning": collab_result,
        "stats": coordinator.get_coordination_stats()
    }

if __name__ == "__main__":
    # Test the coordinator when run directly
    asyncio.run(test_coordinator())
