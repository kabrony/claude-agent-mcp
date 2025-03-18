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
