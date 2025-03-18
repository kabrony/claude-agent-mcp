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

OrganiX implements an advanced multi-agent system that leverages MCP for coordination and collaboration:

### Agent Types

The system includes specialized agents that focus on different domains:

- **Research Specialist**: Information retrieval and synthesis
- **Code Specialist**: Programming and technical implementation
- **Blockchain Specialist**: Blockchain and cryptocurrency operations
- **MCP Specialist**: Tool selection and integration
- **AGI Specialist**: Complex reasoning and multi-domain problem solving

### Intent-Based Routing

Queries are analyzed for intent and routed to the most appropriate agent:

```python
# Automatic routing based on intent
from advanced_chat import coordinator

result = await coordinator.route_to_best_agent("How does Solana's proof of history work?")
# This will automatically route to the Blockchain Specialist
```

### Collaborative Problem Solving

For complex problems, multiple agents can collaborate:

```python
# Multi-agent collaboration
result = await coordinator.multi_agent_collaboration(
    "Create a Python app that integrates with Solana and uses MCP for tool access"
)
# This will involve the Code Specialist, Blockchain Specialist, and MCP Specialist
```

The collaboration system:
1. Routes the query to multiple relevant agents
2. Collects responses from each specialist
3. Uses the AGI Specialist to synthesize a comprehensive response
4. Returns the unified solution with attribution to contributing agents

### Context-Aware Processing

Agents maintain context across interactions:

```python
# Process with context awareness
result = await coordinator.process_with_context_awareness(
    "How would I implement that?"  # Ambiguous query that needs context
)
# The system will incorporate relevant prior conversations to understand "that"
```

## Advanced Capabilities

OrganiX MCP offers several advanced capabilities:

### Tool Usage Analytics

Track and analyze how tools are being used:

```python
# Get tool usage statistics
stats = mcp.get_tool_usage_stats()
print(f"Most used tool: {max(stats.items(), key=lambda x: x[1]['usage_count'])[0]}")
```

### Automatic Tool Selection

The system can automatically select the appropriate tools for a task:

```python
# Let MCP select the right tools
result = await mcp.process_with_tools(
    "What's the current price of SOL and how many people own more than 1000 SOL?"
)
# MCP will identify and use blockchain tools without explicit specification
```

### Composable Tool Chains

Tools can be combined into chains for complex workflows:

```python
# Define a tool chain
mcp.register_tool(
    "research_and_summarize",
    "Research a topic and provide a summary",
    lambda topic: {
        "research": mcp.execute_tool("web_search", {"query": topic}),
        "summary": mcp.execute_tool("summarize", {"text": research["results"]})
    }
)
```
