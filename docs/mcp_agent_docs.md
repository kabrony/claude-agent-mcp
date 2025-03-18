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

OrganiX implements a sophisticated multi-agent system that works seamlessly with MCP:

### Agent Specialization

Different agents specialize in different domains:

- **Research Specialist**: Handles information gathering and synthesis
- **Code Specialist**: Generates and analyzes code
- **Blockchain Specialist**: Manages blockchain interactions
- **MCP Specialist**: Optimizes tool selection and usage
- **AGI Specialist**: Tackles complex, multi-domain problems

### Coordination Patterns

The multi-agent system uses several coordination patterns:

#### 1. Intent-Based Routing

Queries are routed to specialized agents based on detected intent:

```python
intent = ChatIntent(query)
if intent.primary_intent == "blockchain":
    # Route to blockchain specialist
    return await process_with_agent("blockchain", query)
```

#### 2. Collaborative Problem Solving

For complex queries, multiple agents work together:

```python
# Get perspectives from multiple agents
responses = await gather_agent_responses(["researcher", "coder", "blockchain"], query)

# Synthesize a comprehensive response
synthesis = await synthesize_responses(responses, query)
```

#### 3. Context Augmentation

Each agent can access and contribute to a shared memory:

```python
# Get relevant memories
relevant_memories = memory.retrieve_relevant(query)

# Add new insights to memory
memory.add_memory("semantic", new_insight, importance=4)
```

## Advanced Capabilities

### Zero-Knowledge Integration

OrganiX incorporates zero-knowledge proofs for privacy-preserving operations:

```python
# Create a proof that you know something without revealing it
proof = await zk_proofs.create_proof_of_knowledge(sensitive_data)

# Verify a proof
verification = zk_proofs.verify_proof(proof)
```

### Blockchain Capabilities

The platform offers rich blockchain integration, focusing on Solana:

```python
# Get account balance
balance = await solana.get_solana_balance(address)

# Get NFTs owned by an address
nfts = await solana.get_nfts_by_owner(address)

# Connect Phantom wallet
phantom_button = solana.create_agent_wallet_button_html()
```

### Phantom Wallet Integration

OrganiX provides seamless integration with Phantom wallet:

```html
<!-- Add wallet connection button to web interface -->
<div id="wallet-container">
    <!-- This renders the Phantom connect button -->
    {{ phantom_connect_button_html | safe }}
</div>
```

## Extending the System

### Adding New Tools

You can extend OrganiX by adding new tools:

```python
# Register a custom tool
mcp.register_tool(
    "translate_text",
    "Translate text between languages",
    async_translate_function,
    source="custom"
)
```

### Creating Specialized Agents

Add new specialized agents to handle specific domains:

```python
coordinator.register_agent(
    "medical",
    ChatPersona(
        name="Medical Specialist",
        description="Specialized in medical information and health data",
        system_prompt="You are a Medical Specialist agent within OrganiX..."
    )
)
```

### Custom Integrations

Integrate with additional services and platforms:

```python
# Register a custom integration
class CustomIntegration:
    def __init__(self, api_key):
        self.api_key = api_key
        # Initialize connection
        
    async def perform_action(self, params):
        # Implement custom functionality
        
# Register with MCP
custom_tool = CustomIntegration(api_key)
mcp.register_tool("custom_action", "Perform a custom action", custom_tool.perform_action)
```

## Best Practices

### Tool Design

When creating tools for OrganiX MCP:

1. **Clear Naming**: Use descriptive, action-oriented names
2. **Comprehensive Descriptions**: Provide detailed descriptions of functionality
3. **Input Validation**: Validate inputs before processing
4. **Error Handling**: Implement robust error handling
5. **Async Support**: Use async functions for non-blocking operations
6. **Documentation**: Document parameters and return values

### Security Considerations

When implementing MCP tools:

1. **Input Sanitization**: Always sanitize inputs to prevent injection attacks
2. **Permission Scoping**: Limit tool capabilities to necessary operations
3. **Rate Limiting**: Implement rate limiting for external API calls
4. **Credentials Management**: Use environment variables for sensitive credentials
5. **Audit Logging**: Log tool usage for security auditing

### Performance Optimization

For optimal performance:

1. **Caching**: Cache frequently used results
2. **Parallel Execution**: Run independent tools concurrently
3. **Lazy Loading**: Load resources only when needed
4. **Response Streaming**: Stream large responses rather than waiting for completion
5. **Resource Cleanup**: Properly close connections and free resources

## Getting Started with MCP

To begin using OrganiX MCP capabilities:

1. Set up your environment with necessary credentials
2. Initialize the MCP Manager
3. Register any custom tools you need
4. Connect to Composio if using external tools
5. Integrate with the multi-agent system for enhanced capabilities

```python
# Example initialization
from mcp_manager import MCPManager
from composio_integration import composio_client
from advanced_chat import MultiAgentCoordinator

# Initialize MCP
mcp = MCPManager()

# Register custom tools
mcp.register_tool("custom_tool", "Custom functionality", custom_function)

# Sync with Composio
await mcp.refresh_composio_tools()

# Initialize multi-agent system
coordinator = MultiAgentCoordinator()

# Process a query
result = await coordinator.process_query("How can I use MCP to build an agent?")
```

For more detailed examples and advanced usage patterns, see the OrganiX examples directory.
