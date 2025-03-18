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

## Extending the System

OrganiX is designed to be extended with new tools and capabilities:

### Creating Custom Tools

You can create custom tools for specific needs:

```python
# Create a custom tool
async def sentiment_analysis(text):
    # Implement sentiment analysis
    # This could use a local model or API
    sentiment_score = calculate_sentiment(text)
    return {
        "score": sentiment_score,
        "classification": "positive" if sentiment_score > 0 else "negative"
    }

# Register the tool
mcp.register_tool(
    "analyze_sentiment",
    "Analyze sentiment of text",
    sentiment_analysis
)
```

### Tool Schema Definition

For more complex tools, define input schemas:

```python
# Define schema for a tool
schema = {
    "type": "object",
    "properties": {
        "text": {
            "type": "string",
            "description": "The text to analyze"
        },
        "detailed": {
            "type": "boolean",
            "description": "Whether to return detailed analysis"
        }
    },
    "required": ["text"]
}

# Register with schema
mcp.register_tool_with_schema(
    "advanced_analysis",
    "Perform advanced text analysis",
    analyze_text_function,
    schema
)
```

### External API Integration

Connect to external APIs:

```python
# Create a tool that uses an external API
async def weather_forecast(location):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://weather-api.example.com/forecast?location={location}"
        ) as response:
            data = await response.json()
            return {
                "forecast": data["forecast"],
                "temperature": data["temperature"],
                "precipitation": data["precipitation"]
            }

# Register the tool
mcp.register_tool(
    "get_weather_forecast",
    "Get weather forecast for a location",
    weather_forecast
)
```

### Custom Agent Creation

Create specialized agents for specific domains:

```python
# Create a custom agent
from advanced_chat import ChatPersona, coordinator

finance_agent = ChatPersona(
    name="Finance Specialist",
    description="Specialized in financial analysis and advice",
    system_prompt="""You are a Finance Specialist agent within OrganiX.
Your primary role is to provide financial analysis and advice.
You excel at interpreting market data, evaluating investments,
and explaining financial concepts in clear terms."""
)

# Register the agent
coordinator.register_agent("finance", finance_agent)
```

## Zero-Knowledge Integration

OrganiX integrates zero-knowledge proof capabilities for enhanced privacy and security:

### Creating ZK Proofs

Zero-knowledge proofs allow proving knowledge without revealing the underlying information:

```python
# Create a proof of knowledge
proof = await zk_proofs.create_proof_of_knowledge("secret_information")

# Share proof without revealing secret
share_proof(proof)
```

### Proof of Ownership

Prove ownership of assets without revealing identity:

```python
# Prove ownership of an NFT
proof = await zk_proofs.create_proof_of_ownership(
    "FxsqrtTMuAKYgNwiGRD3FwVr1FtsrfUJMPWq49dZVERP",  # Address
    "NFT1234"  # Asset ID
)
```

### Verification

Verify proofs without accessing the original data:

```python
# Verify a proof
verification_result = zk_proofs.verify_proof(proof)
if verification_result["verified"]:
    # Grant access or privileges
    grant_access(user)
```

## Blockchain Capabilities

OrganiX provides comprehensive blockchain integration, focusing on Solana:

### Wallet Connection

Connect to Phantom wallet:

```python
# Generate wallet connection link or button
html = solana_integration.create_agent_wallet_button_html("OrganiX DApp")

# In web interface
display_html(html)
```

### Account Information

Retrieve account information:

```python
# Get Solana account balance
balance = await solana_integration.get_solana_balance("FxsqrtTMuAKYgNwiGRD3FwVr1FtsrfUJMPWq49dZVERP")
print(f"SOL Balance: {balance['balance']['sol']}")

# Get token accounts
tokens = await solana_integration.get_solana_token_accounts("FxsqrtTMuAKYgNwiGRD3FwVr1FtsrfUJMPWq49dZVERP")
```

### NFT Integration

Work with NFTs:

```python
# Get NFTs owned by address
nfts = await solana_integration.get_nfts_by_owner("FxsqrtTMuAKYgNwiGRD3FwVr1FtsrfUJMPWq49dZVERP")

# Display NFT information
for nft in nfts["nfts"]:
    display_nft(nft)
```

### Transaction History

Access transaction history:

```python
# Get recent transactions
transactions = await solana_integration.get_recent_solana_transactions(
    "FxsqrtTMuAKYgNwiGRD3FwVr1FtsrfUJMPWq49dZVERP",
    limit=5
)
```

## Best Practices

To get the most out of OrganiX MCP, follow these best practices:

### Tool Design

- **Simple Responsibility**: Each tool should do one thing well
- **Clear Description**: Provide descriptive names and documentation
- **Error Handling**: Include robust error handling in tool implementations
- **Validation**: Validate inputs before processing
- **Asynchronous Design**: Use async functions for I/O-bound operations

### Agent Interaction

- **Be Specific**: When querying, be specific about your needs
- **Use Natural Language**: No need for special syntax
- **Leverage Context**: References to previous interactions work naturally
- **Specify Agent**: You can request a specific agent with "I'd like the Finance Specialist to help with..."

### Security Considerations

- **Credential Management**: Store API keys and secrets securely in .env
- **Permission Scoping**: Limit tool capabilities to necessary functions
- **Input Sanitization**: Validate and sanitize all inputs
- **Audit Tool Usage**: Regularly review tool usage patterns

### Performance Optimization

- **Cache Results**: Cache frequently used results
- **Parallel Execution**: Use asyncio to parallelize operations
- **Resource Management**: Close connections and resources when done
- **Selective Memory**: Store only important information in memory

### Extending the System

- **Test New Tools**: Thoroughly test tools before deployment
- **Document Everything**: Document tool purpose, inputs, outputs, and examples
- **Version Control**: Maintain version control for tool definitions
- **Modular Design**: Keep tools modular for easier maintenance
