# OrganiX Multi-Agent System

## Overview

OrganiX implements an advanced multi-agent system that coordinates specialized AI agents to handle different types of tasks. This architecture enables more effective problem-solving, context-aware responses, and domain-specific expertise through agent specialization and collaboration.

## Table of Contents

1. [Architecture](#architecture)
2. [Agent Types](#agent-types)
3. [Intent Detection](#intent-detection)
4. [Routing Mechanism](#routing-mechanism)
5. [Multi-Agent Collaboration](#multi-agent-collaboration)
6. [Context Awareness](#context-awareness)
7. [Memory Integration](#memory-integration)
8. [Usage Examples](#usage-examples)
9. [Extending with Custom Agents](#extending-with-custom-agents)
10. [Best Practices](#best-practices)

## Architecture

The OrganiX multi-agent system uses a coordinator-based architecture:

```
┌──────────────────┐
│                  │
│  User Interface  │
│                  │
└────────┬─────────┘
         │
         ▼
┌────────────────────┐
│                    │
│ MultiAgentCoordinator │
│                    │
└──┬───────┬────────┬┘
   │       │        │
   ▼       ▼        ▼
┌──────┐ ┌──────┐ ┌──────┐
│Agent1│ │Agent2│ │Agent3│
└──────┘ └──────┘ └──────┘
```

The `MultiAgentCoordinator` serves as the central hub, analyzing incoming queries, detecting intent, and routing to the appropriate specialized agent. It can also facilitate collaboration between multiple agents to solve complex problems.

## Agent Types

OrganiX includes several built-in specialized agents:

### Research Specialist Agent

```python
researcher_agent = ChatPersona(
    name="Research Specialist",
    description="Specialized in deep research and information synthesis",
    system_prompt="""You are a Research Specialist agent within OrganiX.
Your primary role is to conduct thorough research on topics and provide comprehensive information.
Always cite your sources and consider multiple perspectives on complex topics.
When answering questions, prioritize accuracy, thoroughness, and objectivity."""
)
```

Handles: Information retrieval, fact-checking, research synthesis, academic topics

### Code Specialist Agent

```python
coder_agent = ChatPersona(
    name="Code Specialist",
    description="Specialized in generating high-quality code solutions",
    system_prompt="""You are a Code Specialist agent within OrganiX.
Your primary role is to generate efficient, well-documented code solutions.
When writing code, focus on best practices, maintainability, and performance.
Explain your approach clearly and provide context for your implementation decisions."""
)
```

Handles: Programming tasks, code generation, debugging, algorithm design

### Blockchain Specialist Agent

```python
blockchain_agent = ChatPersona(
    name="Blockchain Specialist",
    description="Specialized in blockchain technology and decentralized applications",
    system_prompt="""You are a Blockchain Specialist agent within OrganiX.
Your primary role is to provide expertise on blockchain technology, focusing on Solana.
You can help with wallet connections, NFTs, token information, and transaction analysis.
When discussing blockchain topics, prioritize technical accuracy and security."""
)
```

Handles: Blockchain questions, cryptocurrency topics, NFTs, wallet connectivity

### MCP Specialist Agent

```python
mcp_agent = ChatPersona(
    name="MCP Specialist",
    description="Specialized in Model Context Protocol and tool usage",
    system_prompt="""You are an MCP Specialist agent within OrganiX.
Your primary role is to manage tool usage through the Model Context Protocol.
You can help select the right tools for tasks, synchronize tools with Composio,
and facilitate communication between models and external systems.
When using tools, prioritize clear input/output handling and error management."""
)
```

Handles: Tool selection, MCP integration, tool chain creation, API connectivity

### AGI Specialist Agent

```python
agi_agent = ChatPersona(
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
```

Handles: Complex reasoning, multi-domain problems, creative problem-solving

## Intent Detection

The system uses intent analysis to determine which agent is best suited for a query:

```python
# ChatIntent class analyzes text to detect intent patterns
intent = ChatIntent(query)
primary_intent = intent.primary_intent  # E.g., "blockchain", "web_search", etc.
confidence = intent.confidence          # Confidence score for the detection
```

Intent patterns are detected using regular expression patterns matched against the query text. The current system can detect these intent types:

- `question`: General questions (who, what, when, why, how)
- `command`: Requests for action (please, can you, would you)
- `chat`: Social interaction (hello, hi, hey)
- `feedback`: User feedback (thanks, good, bad)
- `blockchain`: Blockchain topics (solana, wallet, nft)
- `web_search`: Information seeking (search, find, look up)
- `agent_action`: Action requests (run, execute, perform)

## Routing Mechanism

Based on detected intent, the coordinator routes to the best agent:

```python
# Route based on intent to the appropriate agent
if intent.primary_intent == "blockchain":
    return await process_with_agent("blockchain", query)
elif intent.primary_intent == "web_search":
    return await process_with_agent("researcher", query)
# etc.
```

The routing is also informed by specific keywords in the query. For example, MCP-related terms will route to the MCP specialist, while AGI-related terms route to the AGI specialist.

## Multi-Agent Collaboration

For complex queries, multiple agents can collaborate:

```python
async def multi_agent_collaboration(query, agent_ids=None):
    # Use default agents if not specified
    if not agent_ids:
        agent_ids = ["researcher", "coder", "agi"]
    
    # Process with each agent in parallel
    tasks = []
    for agent_id in agent_ids:
        tasks.append(process_with_agent(agent_id, query))
    
    # Gather all responses
    results = await asyncio.gather(*tasks)
    
    # Synthesize responses
    return synthesize_responses(results)
```

The collaboration process involves:

1. Processing the query with multiple specialized agents in parallel
2. Collecting all agent responses
3. Using a meta-agent (typically the AGI specialist) to synthesize a comprehensive response
4. Returning the synthesized response, with information about which agents contributed

## Context Awareness

All agent interactions incorporate contextual information:

```python
async def process_with_context_awareness(query, context=None):
    # Build context if not provided
    if not context:
        relevant_memories = memory.retrieve_relevant(query)
        context = format_context(relevant_memories)
    
    # Combine query with context
    enhanced_query = f"{query}\n\n{context}"
    
    # Process with appropriate agent
    return await route_to_best_agent(enhanced_query)
```

The context includes:
- Previous interactions
- Relevant memories
- User preferences
- Current conversation state
- External context (time, date, etc.)

## Memory Integration

The multi-agent system integrates deeply with the memory system:

```python
# Store agent interactions in memory
memory_id = memory.add_memory(
    "episodic",
    query,
    {"type": "agent_query", "agent_id": agent_id},
    importance=3
)

# Store response
memory.add_memory(
    "episodic",
    response,
    {"type": "agent_response", "agent_id": agent_id, "query_memory_id": memory_id},
    importance=3
)
```

Each agent interaction is stored with metadata about the agent involved, creating a rich memory system that can be used for future context and analytics.

## Usage Examples

### Basic Agent Routing

```python
from advanced_chat import coordinator

# Process a query with automatic routing
result = await coordinator.route_to_best_agent("How does Solana's proof of history work?")

print(f"Processed by: {result['agent_name']}")  # Should be "Blockchain Specialist"
print(result["response"])
```

### Multi-Agent Collaboration

```python
# Process with multiple agents
result = await coordinator.multi_agent_collaboration(
    "Create a Python application that connects to Solana blockchain and uses AI to analyze NFT trends",
    agent_ids=["coder", "blockchain", "researcher", "agi"]
)

print(f"Synthesized by: {result['agent_name']}")
print(f"Contributing agents: {result['contributing_agents']}")
print(result["response"])
```

### Context-Aware Processing

```python
# First query establishes context
await coordinator.process_query("Tell me about zero-knowledge proofs")

# Follow-up with context awareness
result = await coordinator.process_with_context_awareness(
    "How are they used in blockchain applications?"
)

print(result["response"])  # Will include context from previous interaction
```

## Extending with Custom Agents

You can extend the system with your own custom agents:

```python
from advanced_chat import coordinator, ChatPersona

# Create a custom agent persona
medical_agent = ChatPersona(
    name="Medical Specialist",
    description="Specialized in healthcare and medical information",
    system_prompt="""You are a Medical Specialist agent within OrganiX.
Your primary role is to provide accurate, evidence-based medical information.
Always clarify that you're not providing medical advice, and recommend
consulting with healthcare professionals for personal medical situations.
Focus on general medical knowledge, research findings, and health education."""
)

# Register the agent
coordinator.register_agent("medical", medical_agent)

# Use the custom agent
result = await coordinator.process_with_agent("medical", "How does the immune system work?")
print(result["response"])
```

## Best Practices

### Effective Query Formulation

For optimal routing:
- Be specific about what you're asking
- Include domain-specific keywords when possible
- For complex queries, explicitly request multiple agent collaboration

### Agent Design Principles

When creating custom agents:
1. **Clear Specialization**: Each agent should have a well-defined domain
2. **Distinct Personas**: Agents should have clearly differentiated personas
3. **Comprehensive Instructions**: Include detailed guidance in system prompts
4. **Example Handling**: Provide examples of how to handle common scenarios
5. **Error Boundaries**: Define what is and isn't in the agent's domain

### Collaboration Optimization

For effective multi-agent collaboration:
1. Select complementary agents with different expertise
2. Provide clear instructions about synthesis requirements
3. For sequential workflows, use the output of one agent as input to another
4. Consider using the AGI agent as synthesizer for complex collaborations

### Performance Considerations

- Agent routing adds overhead - use direct processing for simple queries
- Multi-agent collaboration increases token usage and processing time
- Context awareness requires memory retrieval, which has performance implications
- Cache frequently used agent responses when possible
