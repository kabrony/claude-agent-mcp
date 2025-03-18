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
            
        # MCP agent for Model-Context Protocol
        self.register_agent(
            "mcp",
            ChatPersona(
                name="MCP Specialist",
                description="Specialized in Model Context Protocol and tool usage",
                system_prompt="""You are an MCP Specialist agent within OrganiX.
Your primary role is to manage tool usage through the Model Context Protocol.
You can help select the right tools for tasks, synchronize tools with Composio,
and facilitate communication between models and external systems.
When using tools, prioritize clear input/output handling and error management."""
            )
        )
        
        # AGI-aware agent
        self.register_agent(
            "agi",
            ChatPersona(
                name="AGI Specialist",
                description="Specialized in advanced reasoning and multi-domain problem solving",
                system_prompt="""You are an AGI Specialist agent within OrganiX.
Your primary role is to tackle complex, multi-domain problems that require
integrated reasoning across different fields of knowledge. You excel at
decomposing complex problems, exploring multiple solution pathways,
and combining insights from different disciplines.
When solving problems, prioritize creative thinking, systematic reasoning,
and clear explanation of your thought process."""
            )
        )
        
    def register_agent(self, agent_id, persona):
        """Register a new specialized agent"""
        self.agents[agent_id] = persona
        log.info(f"Registered agent: {persona.name} with ID {agent_id}")
        
    async def route_to_best_agent(self, query):
        """Route a query to the most appropriate agent"""
        # Analyze intent
        intent = ChatIntent(query)
        log.info(f"Detected intent: {intent.primary_intent} (confidence: {intent.confidence:.2f})")
        
        # Route based on intent
        if intent.primary_intent == "blockchain" and "blockchain" in self.agents:
            return await self.process_with_agent("blockchain", query)
        elif intent.primary_intent == "web_search" and "researcher" in self.agents:
            return await self.process_with_agent("researcher", query)
        elif intent.primary_intent in ["command", "agent_action"] and "coder" in self.agents:
            return await self.process_with_agent("coder", query)
            
        # Check for MCP and AGI specific keywords
        if re.search(r'\b(?:mcp|model context protocol|tool|tools|composio)\b', query, re.IGNORECASE) and "mcp" in self.agents:
            return await self.process_with_agent("mcp", query)
        elif re.search(r'\b(?:agi|artificial general intelligence|multi-domain|reasoning|cognitive|think|complex problem)\b', query, re.IGNORECASE) and "agi" in self.agents:
            return await self.process_with_agent("agi", query)
        
        # Default to researcher for questions or no clear intent
        if "researcher" in self.agents:
            return await self.process_with_agent("researcher", query)
        
        # Fallback to general processing
        return await self.process_query(query)
    
    async def process_with_agent(self, agent_id, query):
        """Process a query with a specific agent"""
        if agent_id not in self.agents:
            return {
                "success": False,
                "message": f"Agent {agent_id} not found",
                "response": "I don't have that specialized agent available. Let me try to help you directly."
            }
        
        persona = self.agents[agent_id]
        
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
                "message": f"Unsupported proof type: {data_type}"
            }
            
    async def verify_zero_knowledge_proof(self, proof, public_input=None):
        """Verify a zero-knowledge proof"""
        if not self.blockchain_available:
            return {
                "success": False,
                "message": "ZK integration not available"
            }
            
        return zk_proofs.verify_proof(proof, public_input)
    
    async def multi_agent_collaboration(self, query, agent_ids=None):
        """Process a query using multiple agents in collaboration"""
        # Use default set of agents if not specified
        if not agent_ids:
            agent_ids = ["researcher", "coder", "agi"]
            
            # Add blockchain if available
            if self.blockchain_available and "blockchain" in self.agents:
                agent_ids.append("blockchain")
                
            # Add MCP if available
            if self.composio_available and "mcp" in self.agents:
                agent_ids.append("mcp")
        
        # Filter to only include available agents
        agent_ids = [agent_id for agent_id in agent_ids if agent_id in self.agents]
        
        if not agent_ids:
            return await self.process_query(query)
            
        # Create tasks to process with each agent in parallel
        tasks = []
        for agent_id in agent_ids:
            tasks.append(asyncio.create_task(self.process_with_agent(agent_id, query)))
            
        # Wait for all agents to complete
        results = await asyncio.gather(*tasks)
        
        # Extract responses
        agent_responses = {}
        for result in results:
            if result.get("success"):
                agent_id = result.get("agent_id")
                agent_name = result.get("agent_name")
                agent_responses[agent_id] = {
                    "name": agent_name,
                    "response": result.get("response")
                }
        
        # Combine responses using a meta-agent (AGI if available, otherwise general)
        meta_agent_id = "agi" if "agi" in self.agents else None
        
        if not meta_agent_id:
            # Just return the most relevant response based on agent priority
            priority_order = ["agi", "researcher", "blockchain", "coder", "mcp"]
            for agent_id in priority_order:
                if agent_id in agent_responses:
                    return {
                        "success": True,
                        "agent_id": agent_id,
                        "agent_name": agent_responses[agent_id]["name"],
                        "response": agent_responses[agent_id]["response"],
                        "collaboration": True,
                        "contributing_agents": list(agent_responses.keys())
                    }
            
            # Fallback to first available
            first_agent_id = list(agent_responses.keys())[0]
            return {
                "success": True,
                "agent_id": first_agent_id,
                "agent_name": agent_responses[first_agent_id]["name"],
                "response": agent_responses[first_agent_id]["response"],
                "collaboration": True,
                "contributing_agents": list(agent_responses.keys())
            }
        
        # Use the AGI agent to synthesize a response
        synthesis_prompt = f"""User query: {query}

Multiple agents have provided responses to this query. Your task is to synthesize these responses into a coherent, comprehensive answer.

Available agent responses:

"""
        
        for agent_id, info in agent_responses.items():
            synthesis_prompt += f"## {info['name']} (Agent ID: {agent_id})\n\n{info['response']}\n\n---\n\n"
            
        synthesis_prompt += "\nSynthesize these responses into a single, coherent answer that addresses the user's query comprehensively."
        
        synthesis_result = await self.process_with_agent(meta_agent_id, synthesis_prompt)
        
        if synthesis_result.get("success"):
            return {
                "success": True,
                "agent_id": meta_agent_id,
                "agent_name": synthesis_result.get("agent_name"),
                "response": synthesis_result.get("response"),
                "collaboration": True,
                "contributing_agents": list(agent_responses.keys())
            }
        else:
            # Fallback to researcher or first available
            fallback_id = "researcher" if "researcher" in agent_responses else list(agent_responses.keys())[0]
            return {
                "success": True,
                "agent_id": fallback_id,
                "agent_name": agent_responses[fallback_id]["name"],
                "response": agent_responses[fallback_id]["response"],
                "collaboration": True,
                "contributing_agents": list(agent_responses.keys())
            }
            
    async def explain_multi_agent_system(self):
        """Generate an explanation of the multi-agent system"""
        info = {
            "agents": {},
            "integrations": {
                "blockchain": self.blockchain_available,
                "composio": self.composio_available
            },
            "capabilities": [
                "Multi-agent routing and coordination",
                "Context-aware processing",
                "Memory integration with importance ratings",
                "Real-time blockchain data access (if enabled)",
                "Zero-knowledge proof creation and verification (if enabled)",
                "Tool usage through Model Context Protocol",
                "Intent detection and analysis"
            ]
        }
        
        # Add agent information
        for agent_id, persona in self.agents.items():
            info["agents"][agent_id] = {
                "name": persona.name,
                "description": persona.description
            }
            
        explanation = f"""# OrganiX Multi-Agent System

OrganiX implements an advanced multi-agent coordination system that routes queries to specialized agents based on detected intent.

## Available Agents

Currently, the system has {len(self.agents)} specialized agents:

"""

        for agent_id, persona in self.agents.items():
            explanation += f"- **{persona.name}** ({agent_id}): {persona.description}\n"
            
        explanation += f"""
## Integrations

- **Blockchain Integration**: {'Enabled' if self.blockchain_available else 'Disabled'}
- **Composio/MCP Integration**: {'Enabled' if self.composio_available else 'Disabled'}

## Key Capabilities

- **Intent Detection**: Analyzes user queries to determine the most appropriate agent
- **Context Awareness**: Incorporates relevant memories and context into processing
- **Multi-Agent Collaboration**: Can combine insights from multiple specialized agents
- **Memory Management**: Stores interactions with importance ratings for future retrieval
- **Tool Usage**: Leverages the Model Context Protocol for external tool integration
- **ZK Proofs**: {'Supports' if self.blockchain_available else 'Does not support'} zero-knowledge proof creation and verification

## How It Works

1. When you submit a query, the system analyzes it for intent
2. Based on the detected intent, your query is routed to the most appropriate agent
3. For complex queries, multiple agents can collaborate to generate a comprehensive response
4. All interactions are stored in the memory system for future context

For optimal results, clearly state your need or question, and the system will automatically route to the best specialized agent.
"""
            
        return {
            "success": True,
            "explanation": explanation,
            "system_info": info
        }
            
# Initialize global coordinator
coordinator = MultiAgentCoordinator()

async def test_multi_agent():
    """Test the multi-agent coordination system"""
    test_queries = [
        "How does the Solana blockchain work?",
        "Write a Python function to calculate Fibonacci numbers",
        "What are the latest developments in artificial intelligence?",
        "How can I integrate MCP into my application?",
        "What's the difference between AGI and narrow AI?"
    ]
    
    for query in test_queries:
        print(f"\n\nTesting query: {query}")
        response = await coordinator.route_to_best_agent(query)
        print(f"Routed to agent: {response.get('agent_name', 'Unknown')}")
        print(f"Response (snippet): {response.get('response', '')[:150]}...")
        
    # Test collaborative response
    print("\n\nTesting multi-agent collaboration...")
    collab_query = "Create a Python application that connects to the Solana blockchain and uses MCP for tool integration"
    result = await coordinator.multi_agent_collaboration(collab_query)
    print(f"Collaboration result - Synthesized by: {result.get('agent_name', 'Unknown')}")
    print(f"Contributing agents: {result.get('contributing_agents', [])}")
    print(f"Response (snippet): {result.get('response', '')[:150]}...")
    
    return "Tests completed"

if __name__ == "__main__":
    # Run test
    asyncio.run(test_multi_agent())
