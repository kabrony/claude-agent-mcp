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

OrganiX implements a sophisticated multi-agent coordination system that leverages MCP for tool access across specialized agents:

### Agent Types

The system includes several specialized agents:

- **Researcher Agent**: Focuses on information retrieval and synthesis
- **Coder Agent**: Specializes in code generation and analysis
- **Blockchain Agent**: Handles blockchain interactions and data
- **MCP Specialist**: Manages tool selection and usage
- **AGI Specialist**: Tackles complex, multi-domain problems

### Coordination Flow

1. User queries are analyzed for intent
2. The appropriate specialized agent is selected
3. The agent leverages MCP tools as needed
4. Results are processed and returned to the user

For complex queries, multiple agents can collaborate:

```python
# Multi-agent collaboration
result = await coordinator.multi_agent_collaboration(
    "Create a Python app that analyzes Solana NFTs with zero-knowledge proofs"
)
```

## Advanced Capabilities

### Intent Detection

The system automatically detects user intent to route queries appropriately:

```python
intent = ChatIntent("What's the current price of Solana?")
print(intent.primary_intent)  # "blockchain"
print(intent.confidence)      # 0.75
```

### Context Awareness

All tools have access to relevant context from the memory system:

```python
result = await coordinator.process_with_context_awareness(
    "Tell me more about that blockchain project we discussed"
)
```

### Tool Usage Analytics

The MCP Manager tracks detailed analytics about tool usage:

```python
stats = mcp.get_tool_usage_stats()
print(f"Most used tool: {max(stats.items(), key=lambda x: x[1]['usage_count'])[0]}")
```

## Extending the System

### Adding New Tools

Adding new tools to OrganiX is straightforward:

```python
# Add a custom tool
mcp.register_tool(
    "translate_text",
    "Translate text between languages",
    async_translation_function,
    source="custom"
)
```

### Creating Custom Agents

You can create custom specialized agents:

```python
# Create a custom agent
coordinator.register_agent(
    "financial_advisor",
    ChatPersona(
        name="Financial Advisor",
        description="Specialized in financial analysis and advice",
        system_prompt="You are a financial advisor specialized in..."
    )
)
```

### Tool Development Guidelines

When developing new tools:

1. Make tools atomic and focused on a single capability
2. Include clear error handling and input validation
3. Add comprehensive documentation
4. Test with a variety of inputs
5. Consider performance implications

## Zero-Knowledge Integration

OrganiX includes zero-knowledge capabilities that protect privacy while enabling verification:

### Creating ZK Proofs

```python
# Create a proof of knowledge
proof = await zk_proofs.create_proof_of_knowledge(sensitive_data)

# Create a proof of ownership
proof = await zk_proofs.create_proof_of_ownership(wallet_address, asset_id)
```

### Verifying ZK Proofs

```python
# Verify a proof
verification = await zk_proofs.verify_proof(proof)
```

## Blockchain Capabilities

OrganiX integrates deeply with the Solana blockchain:

### Wallet Integration

```python
# Generate a Phantom wallet connection button
html = solana_integration.create_agent_wallet_button_html("OrganiX DApp")
```

### Blockchain Data Access

```python
# Get account data
balance = await solana_integration.get_solana_balance(address)
tokens = await solana_integration.get_solana_token_accounts(address)
nfts = await solana_integration.get_nfts_by_owner(address)
```

### Transaction Analysis

```python
# Get recent transactions
txs = await solana_integration.get_recent_solana_transactions(address)
```

## Best Practices

### Security Considerations

1. Never expose private keys or sensitive credentials through tools
2. Implement proper permission checks on system-level tools
3. Sanitize all user inputs before execution
4. Use zero-knowledge proofs when handling sensitive data
5. Implement rate limiting on resource-intensive tools

### Performance Optimization

1. Cache frequent tool results when appropriate
2. Use asynchronous execution for I/O-bound operations
3. Batch similar operations when possible
4. Monitor tool execution times and optimize slow tools
5. Implement timeout mechanisms for external API calls

### Reliability

1. Implement proper error handling for all tools
2. Add retry logic for network-dependent operations
3. Provide fallback mechanisms when primary tools fail
4. Log detailed error information for debugging
5. Regularly test tools with edge cases

## Conclusion

The OrganiX MCP integration provides a powerful framework for extending AI capabilities through standardized tool access. By following the guidelines and best practices in this documentation, you can leverage these capabilities to build sophisticated agent systems that integrate with blockchain, zero-knowledge technology, and other advanced features.

For additional help or to report issues, contact the OrganiX development team or open an issue on GitHub.
