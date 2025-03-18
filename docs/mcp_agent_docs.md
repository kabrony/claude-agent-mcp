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

OrganiX implements a sophisticated multi-agent system that leverages MCP for coordination:

### Agent Types

The system includes several specialized agents:

- **Research Specialist**: Deep research and information synthesis
- **Code Specialist**: High-quality code generation and analysis
- **Blockchain Specialist**: Blockchain expertise and integration
- **MCP Specialist**: Tool management and protocol expertise
- **AGI Specialist**: Advanced reasoning and cross-domain problem solving

### Routing and Coordination

The `MultiAgentCoordinator` handles:

1. **Intent Detection**: Analyzing user queries to determine the most appropriate agent
2. **Agent Routing**: Directing queries to specialized agents based on intent
3. **Collaborative Processing**: Combining insights from multiple agents
4. **Synthesis**: Merging responses into coherent, comprehensive answers

```python
# Example of multi-agent coordination
from advanced_chat import coordinator

# Route to best agent automatically
result = await coordinator.route_to_best_agent("How can I create a Solana dApp?")

# Use multiple agents in collaboration
result = await coordinator.multi_agent_collaboration(
    "Design a system that uses blockchain for identity verification with ZK proofs"
)
```

### Agent Communication

Agents communicate through a standardized message format that includes:

- The original query
- Context from memory and previous interactions
- Tool usage results
- Confidence scores
- Reasoning steps

## Advanced Capabilities

OrganiX extends basic MCP functionality with several advanced capabilities:

### Context Awareness

The system maintains context across interactions through:

- **Memory Integration**: Retrieving relevant past interactions
- **Importance Ratings**: Prioritizing critical information
- **Temporal Awareness**: Understanding time-based relationships between queries

```python
# Process a query with context awareness
result = await coordinator.process_with_context_awareness(
    "Follow up on our previous discussion about blockchain security"
)
```

### Intent Detection

The `ChatIntent` class analyzes user queries to:

- Identify the primary intent
- Detect secondary intents
- Calculate confidence scores
- Track intent patterns over time

```python
from advanced_chat import ChatIntent

# Analyze intent
intent = ChatIntent("Can you find information about Solana NFT marketplaces?")
print(f"Primary intent: {intent.primary_intent}")
print(f"Confidence: {intent.confidence}")
print(f"All detected intents: {intent.detected_intents}")
```

### Tool Usage Analytics

The MCP Manager tracks:

- Tool usage frequency
- Success/failure rates
- Execution times
- Common input patterns

```python
# Get tool usage statistics
stats = mcp.get_tool_usage_stats()
print(stats)
```

## Zero-Knowledge Integration

OrganiX incorporates zero-knowledge proof technology for enhanced privacy and security:

### ZK Proof Creation

The system can generate ZK proofs for:

- **Knowledge Proofs**: Proving you know something without revealing it
- **Ownership Proofs**: Proving you own an asset without revealing your identity
- **Computation Proofs**: Proving a computation was performed correctly

```python
# Create a ZK proof of knowledge
proof = await coordinator.create_zero_knowledge_proof(
    "knowledge",
    {"secret_data": "sensitive information"}
)

# Create a ZK proof of ownership
proof = await coordinator.create_zero_knowledge_proof(
    "ownership",
    {"address": "FxsqrtTMuAKYgNwiGRD3FwVr1FtsrfUJMPWq49dZVERP", "asset_id": "asset123"}
)
```

### ZK Proof Verification

The system can verify ZK proofs:

```python
# Verify a ZK proof
result = await coordinator.verify_zero_knowledge_proof(proof)
if result["verified"]:
    print("Proof verified successfully")
else:
    print("Invalid proof")
```

### Privacy-Preserving Computations

Zero-knowledge proofs enable:

- Verifiable computations without revealing inputs
- Identity verification without revealing personal information
- Data sharing with cryptographic guarantees

## Blockchain Capabilities

OrganiX integrates with blockchain technology, particularly Solana, to provide:

### Wallet Integration

The system supports Phantom wallet integration:

```python
# Generate HTML for Phantom wallet connection
html = solana_integration.create_agent_wallet_button_html("OrganiX Dashboard")
```

### Blockchain Data Access

The system can retrieve and analyze various blockchain data:

```python
# Get SOL balance
balance = await solana_integration.get_solana_balance("FxsqrtTMuAKYgNwiGRD3FwVr1FtsrfUJMPWq49dZVERP")

# Get token accounts
tokens = await solana_integration.get_solana_token_accounts("FxsqrtTMuAKYgNwiGRD3FwVr1FtsrfUJMPWq49dZVERP")

# Get NFTs
nfts = await solana_integration.get_nfts_by_owner("FxsqrtTMuAKYgNwiGRD3FwVr1FtsrfUJMPWq49dZVERP")

# Get recent transactions
txs = await solana_integration.get_recent_solana_transactions("FxsqrtTMuAKYgNwiGRD3FwVr1FtsrfUJMPWq49dZVERP")

# Get comprehensive blockchain data
data = await coordinator.get_blockchain_data("FxsqrtTMuAKYgNwiGRD3FwVr1FtsrfUJMPWq49dZVERP")
```

### Solana Agents

The system incorporates Solana Agents, a next-generation technology that combines AI with blockchain:

- Autonomous agents that can operate on-chain
- Secure, verifiable execution of AI-driven operations
- Integration with Solana's Account Model
- Support for Program-Derived Addresses (PDAs)

## Extending the System

OrganiX is designed to be highly extensible. Here's how to extend the system with new capabilities:

### Adding New Tools

To add a new tool:

```python
# Define the tool function
async def my_tool_function(param1, param2):
    # Tool implementation
    result = process_data(param1, param2)
    return result

# Register with MCP Manager
mcp.register_tool(
    "my_new_tool",
    "Description of what my tool does",
    my_tool_function
)
```

### Creating New Agents

To create a new specialized agent:

```python
# Define the agent persona
new_agent = ChatPersona(
    name="My Specialist",
    description="Specialized in my particular domain",
    system_prompt="""You are a specialist agent within OrganiX.
Your primary role is to provide expertise on your domain.
When responding, prioritize accuracy and clarity."""
)

# Register with the coordinator
coordinator.register_agent("my_agent", new_agent)
```

### Custom Memory Types

To add custom memory handling:

```python
# Add memory with custom type and metadata
memory_id = memory_system.add_memory(
    "semantic",  # Memory type
    content,     # The content to store
    {
        "type": "my_custom_type",
        "source": "custom_source",
        "custom_field": "custom_value"
    },
    importance=4  # Higher importance (1-5)
)
```

## Best Practices

When working with OrganiX MCP, follow these best practices:

### Tool Design

1. **Keep tools simple and focused**: Each tool should do one thing well
2. **Provide clear descriptions**: Make it easy for the system to understand when to use the tool
3. **Handle errors gracefully**: Return clear error messages that the AI can interpret
4. **Include validation**: Validate inputs before execution
5. **Document schema**: Clearly document the expected inputs and outputs

### Agent Routing

1. **Use appropriate system prompts**: Each specialist agent should have a clear, focused system prompt
2. **Test routing logic**: Verify that queries are routed to the appropriate agents
3. **Combine agents when needed**: Use multi-agent collaboration for complex queries
4. **Track routing performance**: Monitor how effectively queries are routed to identify improvements

### Memory Management

1. **Use appropriate importance ratings**: Reserve high importance (4-5) for critical information
2. **Include rich metadata**: Add detailed metadata to help with retrieval
3. **Regularly maintain memory**: Prune old, low-importance memories periodically
4. **Optimize retrieval queries**: Be specific when retrieving memories

### Security Considerations

1. **Limit command execution**: Restrict system command execution to safe operations
2. **Validate blockchain addresses**: Always validate addresses before querying blockchain data
3. **Use ZK proofs for sensitive data**: Leverage zero-knowledge proofs when handling private information
4. **Sanitize inputs and outputs**: Validate all inputs and sanitize outputs to prevent injection attacks

## Conclusion

The OrganiX Model Context Protocol integration provides a powerful, flexible framework for building advanced AI agents. By leveraging MCP, Composio, and specialized agents, OrganiX enables sophisticated interactions with tools, blockchain systems, and more.

For further assistance or to report issues, please contact the OrganiX development team or visit our GitHub repository.
