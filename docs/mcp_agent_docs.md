# OrganiX Model Context Protocol (MCP) Integration

## Overview

The Model Context Protocol (MCP) is a powerful framework that enables AI models to access external tools and capabilities through a standardized interface. OrganiX leverages MCP to create a flexible, extensible agent system that can interact with various tools, services, and data sources.

This document provides comprehensive documentation on how MCP is integrated into OrganiX, how to leverage its capabilities, and how to extend it with new tools and functionality.

## Table of Contents

1. [Architecture](#architecture)
2. [Core Components](#core-components)
3. [Tool Integration](#tool-integration)
4. [Composio Integration](#composio-integration)
5. [Multi-Agent Coordination](#multi-agent-coordination)
6. [Advanced Capabilities](#advanced-capabilities)
7. [Extending the System](#extending-the-system)
8. [Zero-Knowledge Integration](#zero-knowledge-integration)
9. [Blockchain Capabilities](#blockchain-capabilities)
10. [Best Practices](#best-practices)

## Architecture

The OrganiX MCP architecture follows a modular design that separates concerns between various components:

```
┌─────────────────────┐      ┌─────────────────────┐
│                     │      │                     │
│    User Interface   │◄────►│   Agent Controller  │
│                     │      │                     │
└─────────────────────┘      └──────────┬──────────┘
                                        │
                                        ▼
┌─────────────────────┐      ┌─────────────────────┐
│                     │      │                     │
│    Memory System    │◄────►│   Claude Client     │
│                     │      │                     │
└─────────────────────┘      └──────────┬──────────┘
                                        │
                                        ▼
┌─────────────────────┐      ┌─────────────────────┐
│                     │      │                     │
│  Blockchain/ZK      │◄────►│    MCP Manager      │
│                     │      │                     │
└─────────────────────┘      └──────────┬──────────┘
                                        │
                                        ▼
                             ┌─────────────────────┐
                             │                     │
                             │  Composio Client    │
                             │                     │
                             └─────────────────────┘
```

The MCP Manager is the central component that handles tool registration, execution, and coordination. It integrates with the Composio platform for enhanced tool management and connects to the broader OrganiX ecosystem.

## Core Components

### MCP Manager

The `MCPManager` class is the heart of the MCP integration. It:

- Registers tools with unique identifiers and descriptions
- Tracks tool usage and statistics
- Handles tool execution and error management
- Synchronizes with Composio for external tool integration
- Provides analytics on tool performance and usage patterns

```python
# Example: Creating and using MCP Manager
from mcp_manager import MCPManager

# Initialize manager
mcp = MCPManager()

# Register a tool
mcp.register_tool(
    "calculate_average",
    "Calculate the average of a list of numbers",
    lambda numbers: sum(numbers) / len(numbers)
)

# Use the tool
result = await mcp.process_with_tools("What's the average of 10, 20, and 30?")
print(result)  # The MCP will identify the tool need and execute it
```

### Tool Registration

Tools in OrganiX MCP follow a standard format:

- **Name**: Unique identifier for the tool
- **Description**: Human-readable description of the tool's functionality
- **Function**: The actual implementation that executes when the tool is called
- **Metadata**: Optional additional information about the tool

Each tool can have optional input validation, error handling, and usage tracking.

## Tool Integration

OrganiX comes with several built-in tools:

### System Tools
- `list_files` - List files in a directory
- `execute_command` - Execute system commands (with security restrictions)

### Web Research Tools
- `web_search` - Search the web for information
- `extract_url` - Extract content from a specific URL

### Memory Tools
- `retrieve_memory` - Retrieve relevant memories
- `retrieve_memory_by_timeframe` - Get memories from a specific time period
- `summarize_memories` - Generate summaries of recent memories

### Blockchain Tools
- `get_solana_balance` - Get SOL balance for an address
- `get_token_accounts` - Get token accounts for an address
- `get_nfts` - Get NFTs owned by an address

### Advanced Tools
- `create_zk_proof` - Create zero-knowledge proofs
- `verify_zk_proof` - Verify zero-knowledge proofs

## Composio Integration

OrganiX features deep integration with Composio, a platform that extends MCP with additional capabilities:

### Synchronization

The MCP Manager automatically synchronizes with Composio to:

1. Register local tools with the Composio platform
2. Import tools from Composio to the local environment
3. Maintain consistent tool definitions across environments

```python
# Sync tools with Composio
await mcp.refresh_composio_tools()
```

### Composio CLI

The integration includes support for the Composio CLI, allowing command-line operations:

```bash
# Install Composio CLI
composio_client.install_cli()

# Configure CLI with credentials
composio_client.configure_cli()

# Run CLI commands
result = composio_client.run_cli_command("list tools")
```

## Multi-Agent Coordination

OrganiX implements an advanced multi-agent system that leverages MCP for coordinated problem-solving.

### Agent Architecture

The multi-agent system consists of:

1. **Specialized Agents** - Domain-specific experts (research, code, blockchain, MCP, AGI)
2. **Coordinator** - Routes queries to appropriate agents based on intent
3. **Meta-Agent** - Synthesizes responses from multiple agents (typically AGI agent)

```python
# Example: Using the multi-agent system
from advanced_chat import coordinator

# Route to best agent automatically
result = await coordinator.route_to_best_agent("How does zero-knowledge proof work in blockchain?")

# Force routing to a specific agent
result = await coordinator.process_with_agent("blockchain", "Explain Solana token creation")

# Use multiple agents in collaboration
result = await coordinator.multi_agent_collaboration(
    "Create a Python app that uses MCP to access blockchain data",
    agent_ids=["coder", "blockchain", "mcp"]
)
```

### Agent Specializations

The system includes several specialized agents:

- **Research Specialist**: Deep research and information synthesis
- **Code Specialist**: Programming and software development
- **Blockchain Specialist**: Blockchain technology and cryptocurrency
- **MCP Specialist**: Tool integration and Model Context Protocol
- **AGI Specialist**: Multi-domain reasoning and complex problem solving

Each agent has specialized knowledge and capabilities optimized for specific types of tasks.

### Intent Detection

The system uses natural language processing to detect intent and route queries appropriately:

```python
from advanced_chat import ChatIntent

# Analyze intent
intent = ChatIntent("How do I connect Phantom wallet to my Solana app?")
print(f"Primary intent: {intent.primary_intent}")  # "blockchain"
print(f"Confidence: {intent.confidence}")         # e.g., 0.75
print(f"All detected intents: {intent.detected_intents}")
```

### Collaborative Problem-Solving

For complex queries, the system can engage multiple agents in parallel:

1. The query is sent to multiple relevant agents
2. Each agent processes the query independently
3. The AGI agent synthesizes the individual contributions
4. A unified response is generated that leverages the specialized knowledge of each agent

This approach combines the strengths of different agents for more comprehensive responses.

## Advanced Capabilities

### Context-Aware Processing

The OrganiX MCP system maintains context awareness through:

1. **Memory Integration**: All interactions are stored in the memory system with importance ratings
2. **Context Retrieval**: Relevant past interactions are retrieved to provide context for new queries
3. **Agent State**: Specialized agents maintain state across interactions

```python
# Process with enhanced context awareness
result = await coordinator.process_with_context_awareness(
    "Continue with the previous implementation",
    context=None  # Automatically retrieves relevant context
)
```

### Extended Reasoning

For complex reasoning tasks, the system supports extended thinking:

```python
# Enable extended reasoning for complex problems
result = await agent.process_query(
    "What are the philosophical implications of artificial general intelligence?",
    extended_thinking=True
)
```

### Tool Usage Analytics

The MCP Manager tracks detailed analytics on tool usage:

```python
# Get tool usage statistics
stats = mcp.get_tool_usage_stats()

# Example output
{
    "web_search": {
        "usage_count": 27,
        "source": "local"
    },
    "retrieve_memory": {
        "usage_count": 15,
        "source": "local"
    },
    "get_solana_balance": {
        "usage_count": 3,
        "source": "composio"
    }
}
```

## Extending the System

### Creating Custom Tools

You can extend OrganiX by creating and registering custom tools:

```python
# Define a custom tool function
async def sentiment_analysis(text):
    # Implement sentiment analysis logic
    import re
    positive_words = ["good", "great", "excellent", "positive"]
    negative_words = ["bad", "poor", "negative", "terrible"]
    
    positive_count = sum(1 for word in positive_words if re.search(r'\b' + word + r'\b', text.lower()))
    negative_count = sum(1 for word in negative_words if re.search(r'\b' + word + r'\b', text.lower()))
    
    if positive_count > negative_count:
        return {"sentiment": "positive", "score": positive_count - negative_count}
    elif negative_count > positive_count:
        return {"sentiment": "negative", "score": negative_count - positive_count}
    else:
        return {"sentiment": "neutral", "score": 0}

# Register the custom tool
mcp.register_tool(
    "analyze_sentiment",
    "Analyze the sentiment of a text",
    sentiment_analysis
)
```

### Creating Custom Agents

You can create custom specialized agents for specific domains:

```python
from advanced_chat import ChatPersona, coordinator

# Create a custom agent persona
finance_persona = ChatPersona(
    name="Finance Specialist",
    description="Specialized in financial analysis and investment strategies",
    system_prompt="""You are a Finance Specialist agent within OrganiX.
Your primary role is to provide expertise on financial topics, investment strategies,
market analysis, and economic trends. When discussing financial matters,
prioritize accuracy, clarity, and balanced perspective."""
)

# Register the custom agent
coordinator.register_agent("finance", finance_persona)

# Use the custom agent
result = await coordinator.process_with_agent("finance", "How should I allocate my 401k investments?")
```

### Extending Composio Integration

You can extend the Composio integration with custom connection logic:

```python
from composio_integration import composio_client

# Define custom Composio tool schema
custom_schema = {
    "type": "object",
    "properties": {
        "input_text": {
            "type": "string",
            "description": "The text to analyze"
        }
    },
    "required": ["input_text"]
}

# Register with Composio
result = await composio_client.register_mcp_tool(
    "custom_text_analysis",
    "Custom text analysis tool",
    custom_schema
)
```

## Zero-Knowledge Integration

OrganiX includes zero-knowledge proof integration for privacy-preserving operations:

### Creating ZK Proofs

```python
from blockchain_integration import zk_proofs

# Create a proof of knowledge
proof = await zk_proofs.create_proof_of_knowledge(
    "sensitive data that remains private"
)

# Create a proof of ownership
proof = await zk_proofs.create_proof_of_ownership(
    "wallet_address",
    "asset_id"
)
```

### Verifying ZK Proofs

```python
# Verify a proof
result = zk_proofs.verify_proof(proof)
if result["verified"]:
    print("Proof successfully verified")
else:
    print("Proof verification failed")
```

### Privacy-Preserving Operations

ZK proofs can be used for:

1. **Authentication**: Prove identity without revealing credentials
2. **Ownership Verification**: Prove ownership without revealing the owner
3. **Knowledge Proofs**: Prove knowledge of information without revealing it
4. **Compliance**: Demonstrate regulatory compliance while preserving privacy

## Blockchain Capabilities

OrganiX integrates with Solana blockchain for advanced capabilities:

### Wallet Integration

The system supports Phantom wallet integration with a simple connector:

```html
<!-- HTML for Phantom wallet connection -->
<div id="phantom-connect">
    <!-- This will render the connection button -->
    <script>
        document.getElementById('phantom-connect').innerHTML = 
            solana_integration.create_agent_wallet_button_html("OrganiX Agent");
    </script>
</div>
```

### Blockchain Data Access

Access on-chain data directly:

```python
from blockchain_integration import solana_integration

# Get account balance
balance = await solana_integration.get_solana_balance("wallet_address")

# Get NFTs owned by an address
nfts = await solana_integration.get_nfts_by_owner("wallet_address")

# Get transaction history
txs = await solana_integration.get_recent_solana_transactions("wallet_address")
```

### Agent-Blockchain Integration

Specialized blockchain agent capabilities:

1. **Transaction Analysis**: Understand and explain transaction history
2. **Token Information**: Get details about tokens and NFTs
3. **Wallet Management**: Assist with wallet connections and transactions
4. **DeFi Integration**: Interact with decentralized finance protocols

## Best Practices

### Security Considerations

When working with MCP and tools:

1. **Input Validation**: Always validate inputs to tools to prevent injection attacks
2. **Authentication**: Ensure proper authentication for sensitive operations
3. **API Keys**: Store API keys securely, never in code repositories
4. **Permission Boundaries**: Limit tool capabilities to necessary operations
5. **Monitoring**: Track tool usage for unusual patterns

### Performance Optimization

To optimize performance:

1. **Parallel Execution**: Use `asyncio.gather()` for parallel tool execution
2. **Caching**: Cache frequently used tool results
3. **Memory Pruning**: Regularly prune low-importance memories
4. **Tool Selection**: Choose the most efficient tools for each task
5. **Timeouts**: Implement timeouts for external tool calls

```python
# Example: Parallel tool execution
async def execute_tools_in_parallel(query):
    # Create tasks for parallel execution
    search_task = asyncio.create_task(
        mcp.tools["web_search"].function(query)
    )
    memory_task = asyncio.create_task(
        mcp.tools["retrieve_memory"].function(query)
    )
    
    # Wait for all tasks to complete
    search_result, memory_result = await asyncio.gather(
        search_task, memory_task
    )
    
    # Combine results
    return {
        "search": search_result,
        "memory": memory_result
    }
```

### Development Workflow

When extending the OrganiX MCP system:

1. **Tool Testing**: Test tools in isolation before integration
2. **Intent Coverage**: Ensure intent detection covers new capabilities
3. **Agent Specialization**: Keep agents focused on specific domains
4. **Documentation**: Document tool inputs, outputs, and behaviors
5. **Error Handling**: Implement robust error handling for tools

### Conversational Design

For effective agent interactions:

1. **Clear Feedback**: Provide clear feedback on tool usage
2. **Explicit Reasoning**: Make reasoning transparent to users
3. **Tool Selection Explanation**: Explain why specific tools were selected
4. **Confidence Signaling**: Indicate confidence level in responses
5. **Knowledge Boundaries**: Clearly communicate limitations
