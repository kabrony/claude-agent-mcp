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

OrganiX implements an advanced multi-agent architecture that leverages MCP for coordinated problem-solving. This system includes:

### Specialized Agents

- **Research Specialist**: Focused on information gathering and synthesis
- **Code Specialist**: Specialized in code generation and software development
- **Blockchain Specialist**: Expert in blockchain technologies and DApps
- **MCP Specialist**: Dedicated to tool management and integration
- **AGI Specialist**: Handles complex, multi-domain reasoning tasks

### Intent Detection and Routing

The system automatically analyzes user queries to determine intent and routes to the appropriate specialized agent:

```python
# Route query to the best agent based on intent
result = await coordinator.route_to_best_agent("How does Solana staking work?")
# System detects blockchain intent and routes to blockchain specialist
```

### Agent Collaboration

For complex queries, multiple agents can collaborate, with each contributing their expertise:

```python
# Process query with multiple agents collaborating
result = await coordinator.multi_agent_collaboration(
    "Create a Python app that connects to Solana and uses zero-knowledge proofs",
    agent_ids=["coder", "blockchain", "mcp"]
)
```

## Advanced Capabilities

### Context-Aware Processing

OrganiX's MCP integration can incorporate context from:

1. Previous conversations stored in memory
2. User-provided context
3. Blockchain state (for blockchain-related queries)
4. Tool execution history

```python
# Process with enhanced context awareness
result = await coordinator.process_with_context_awareness(
    "Improve the code from our last conversation"
)
```

### AGI Integration

The system features an Artificial General Intelligence (AGI) specialist that can:

- Decompose complex problems into manageable parts
- Coordinate multiple specialized agents
- Synthesize diverse information into coherent responses
- Apply high-level reasoning across domain boundaries

```python
# Process with AGI capabilities for complex reasoning
result = await coordinator.process_with_agent("agi", 
    "What are the ethical, technical, and economic implications of zero-knowledge proofs in blockchain governance?"
)
```

## Extending the System

OrganiX is designed for easy extension with new tools and capabilities:

### Adding Custom Tools

Custom tools can be added programmatically:

```python
# Create and register a custom tool
async def my_custom_tool(param1, param2):
    # Tool implementation
    return result

mcp.register_tool(
    "my_custom_tool",
    "Description of what the tool does",
    my_custom_tool
)
```

### Creating Custom Agents

New specialized agents can be created as needed:

```python
# Create a custom agent persona
custom_persona = ChatPersona(
    name="Finance Specialist",
    description="Expert in financial analysis and forecasting",
    system_prompt="You are a Finance Specialist agent within OrganiX..."
)

# Register the new agent
coordinator.register_agent("finance", custom_persona)
```

### Integration with External Systems

OrganiX can be connected to external systems through custom tool integrations:

```python
# Create tool that connects to an external API
async def external_api_tool(query):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.example.com/data?q={query}") as response:
            return await response.json()

mcp.register_tool(
    "external_api",
    "Query an external API for data",
    external_api_tool
)
```

## Zero-Knowledge Integration

OrganiX includes support for Zero-Knowledge (ZK) technology, which allows verification of information without revealing the underlying data.

### ZK Proof Creation

```python
# Create a ZK proof of knowledge
proof = await zk_proofs.create_proof_of_knowledge("sensitive data")

# Create a ZK proof of ownership
proof = await zk_proofs.create_proof_of_ownership("wallet_address", "asset_id")
```

### ZK Proof Verification

```python
# Verify a ZK proof
verification = zk_proofs.verify_proof(proof)
```

### Privacy-Preserving Computation

ZK proofs can be used for privacy-preserving operations such as:

- Verifying wallet ownership without exposing private keys
- Proving asset ownership without revealing the full portfolio
- Demonstrating transaction validity without exposing transaction details

## Blockchain Capabilities

OrganiX integrates deeply with blockchain technology, particularly Solana.

### Solana Integration

```python
# Get Solana account information
account = await solana_integration.get_solana_account("address")

# Get SOL balance
balance = await solana_integration.get_solana_balance("address")

# Get NFTs owned by an address
nfts = await solana_integration.get_nfts_by_owner("address")
```

### Phantom Wallet Connection

The system includes Phantom wallet integration for web interfaces:

```python
# Generate Phantom connection URL
connection_url = solana_integration.generate_phantom_connection_url("dapp_url", "redirect_url")

# Get HTML for Phantom wallet connect button
html = solana_integration.create_agent_wallet_button_html("OrganiX")
```

## Best Practices

When working with OrganiX and MCP, follow these best practices:

### Tool Design Principles

1. **Single Responsibility**: Each tool should do one thing well
2. **Clear Inputs/Outputs**: Define clear input parameters and return values
3. **Error Handling**: Include robust error handling and return meaningful error messages
4. **Documentation**: Provide clear descriptions and usage examples
5. **Security**: Implement appropriate security checks and validations

### Agent Interaction

1. **Intent Clarity**: Be clear about the intent of your queries
2. **Context Provision**: Provide relevant context when needed
3. **Feedback Loop**: Provide feedback on agent responses to improve future interactions
4. **Memory Usage**: Leverage the memory system for context continuity
5. **Tool Selection**: For complex tasks, explicitly mention tools that might be helpful

### Security Considerations

1. **Tool Permissions**: Carefully control what tools can access and modify
2. **Credential Management**: Use environment variables for storing sensitive credentials
3. **Input Validation**: Validate all inputs before processing
4. **Rate Limiting**: Implement rate limiting for external API calls
5. **Audit Logging**: Maintain logs of all tool usage and sensitive operations

## Troubleshooting

Common issues and their solutions:

### Tool Execution Failures

- **Symptom**: Tool returns error or fails to execute
- **Solutions**:
  - Check tool registration and function implementation
  - Verify input parameters match expected format
  - Ensure any required external services are available

### Composio Synchronization Issues

- **Symptom**: Tools not synchronizing with Composio
- **Solutions**:
  - Verify API key and connection details
  - Check network connectivity to Composio services
  - Ensure tool definitions are compatible with Composio format

### Agent Routing Problems

- **Symptom**: Queries routed to inappropriate agents
- **Solutions**:
  - Review intent detection patterns
  - Provide more specific queries with clear intent
  - Manually specify the desired agent when needed

## Conclusion

The OrganiX Model Context Protocol implementation provides a powerful, flexible framework for building advanced AI agents with tool usage capabilities. By leveraging MCP, OrganiX enables seamless integration with external systems, sophisticated multi-agent coordination, and context-aware processing that enhances the capabilities of the underlying Claude AI model.

This architecture creates a foundation for continuous extension and improvement, allowing OrganiX to evolve with new capabilities while maintaining a consistent, reliable interface for users and developers.
