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

### Custom Tool Example

Here's an example of creating a custom tool for sentiment analysis:

```python
from mcp_manager import MCPManager

# Initialize MCP Manager
mcp = MCPManager()

# Define a sentiment analysis function
async def analyze_sentiment(text):
    # Simple sentiment analysis (in a real implementation, use a proper NLP library)
    positive_words = ["good", "great", "excellent", "amazing", "wonderful", "happy"]
    negative_words = ["bad", "terrible", "awful", "horrible", "sad", "angry"]
    
    positive_count = sum(1 for word in positive_words if word in text.lower())
    negative_count = sum(1 for word in negative_words if word in text.lower())
    
    if positive_count > negative_count:
        sentiment = "positive"
    elif negative_count > positive_count:
        sentiment = "negative"
    else:
        sentiment = "neutral"
        
    return {
        "sentiment": sentiment,
        "positive_score": positive_count,
        "negative_score": negative_count,
        "text": text
    }

# Register the tool with MCP
mcp.register_tool(
    "analyze_sentiment",
    "Analyze the sentiment of a text as positive, negative, or neutral",
    analyze_sentiment
)

# Now the language model can use this tool when needed
```

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

### Composio Client

The Composio client provides a direct interface to the Composio API:

```python
from composio_integration import composio_client

# Check connection status
connection_status = await composio_client.check_connection()
print(f"Composio connection: {connection_status['status']}")

# List registered tools
tools = await composio_client.list_tools()
for tool in tools.get("tools", []):
    print(f"- {tool['name']}: {tool['description']}")
```

### Tool Execution Flow

When a tool is executed through Composio:

1. OrganiX identifies tool need from natural language
2. MCP Manager routes to Composio client for external tools
3. Composio executes the tool and returns results
4. MCP Manager formats results for Claude to consume
5. Claude incorporates tool output into its response

### Configuration

To enable Composio integration, add the following to your `.env` file:

```
COMPOSIO_API_KEY=your_composio_api_key
COMPOSIO_CONNECTION_ID=your_connection_id
COMPOSIO_INTEGRATION_ID=your_integration_id
COMPOSIO_BASE_URL=https://api.composio.dev
```

### Composio CLI Integration

The system includes Composio CLI support for command-line operations:

```python
# Install and configure CLI
composio_client.install_cli()
composio_client.configure_cli()

# Execute CLI commands
result = composio_client.run_cli_command("list connections")
print(result["stdout"])
```

## Multi-Agent Coordination

OrganiX implements a sophisticated multi-agent architecture that works alongside MCP to provide specialized capabilities:

### Agent Types

The system includes several specialized agents:

- **Research Specialist**: Focuses on information retrieval and synthesis
- **Code Specialist**: Handles code generation and analysis
- **Blockchain Specialist**: Manages blockchain interactions and data
- **MCP Specialist**: Optimizes tool selection and usage
- **AGI Specialist**: Handles complex reasoning across multiple domains

### Agent Coordination

The `MultiAgentCoordinator` handles routing queries to the most appropriate agent:

```python
from advanced_chat import MultiAgentCoordinator

# Initialize coordinator
coordinator = MultiAgentCoordinator()

# Process query with automatic routing
result = await coordinator.route_to_best_agent("How does the Solana blockchain work?")

# Process with a specific agent
result = await coordinator.process_with_agent("blockchain", "How do I connect my Phantom wallet?")

# Use multiple agents in collaboration
result = await coordinator.multi_agent_collaboration(
    "Create a Python app that connects to Solana and uses MCP",
    agent_ids=["coder", "blockchain", "mcp"]
)
```

### Intent Detection

The system analyzes queries to detect intent and route to the appropriate agent:

```python
from advanced_chat import ChatIntent

# Analyze intent
intent = ChatIntent("How do I connect my Phantom wallet to my Solana app?")
print(f"Primary intent: {intent.primary_intent}")
print(f"Confidence: {intent.confidence}")
print(f"Detected intents: {intent.detected_intents}")
```

### Context Awareness

Agents maintain context through the memory system:

```python
# Process with context awareness
result = await coordinator.process_with_context_awareness(
    "Tell me more about it",
    context="Previously discussed Solana blockchain fundamentals and token economics."
)
```

## Advanced Capabilities

OrganiX extends MCP with several advanced capabilities that enhance its functionality:

### Extended Thinking Mode

A specialized processing mode that enables more thorough reasoning for complex problems:

```python
from claude_client import ClaudeClient

# Initialize client
client = ClaudeClient()

# Use extended thinking mode for complex reasoning
response = await client.send_extended_thinking_message(
    "Explain the implications of zero-knowledge proofs for blockchain privacy"
)
```

### Response Analysis

Automatic analysis of responses for sentiment, key points, and structure:

```python
# Analyze response content
response = await client.send_message("What are the advantages of Solana?")
analysis = client.analyze_response(response)

print(f"Key points: {analysis['key_points']}")
print(f"Sentiment: {analysis['sentiment']}")
print(f"Readability score: {analysis['readability_score']}")
```

### Conversation Management

Save, load, and switch between conversations:

```python
# Save current conversation
filename = client.save_conversation_to_file("solana_discussion.json")

# Create a new conversation
client.start_new_conversation("Web3 Development")

# Load a previous conversation
client.load_conversation_from_file("solana_discussion.json")

# Get conversation summary
summary = client.summarize_conversation()
```

### Parallel Processing

Execute multiple agents or tools in parallel for efficiency:

```python
# Process with multiple agents in parallel
result = await coordinator.multi_agent_collaboration(
    "What are the implications of using Solana for decentralized finance?",
    agent_ids=["researcher", "blockchain", "agi"]
)
```

### Agent System Inspection

Get detailed information about the multi-agent system:

```python
# Get system explanation
system_info = await coordinator.explain_multi_agent_system()
print(system_info["explanation"])

# Get agent capabilities
for agent_id, info in system_info["system_info"]["agents"].items():
    print(f"{info['name']} ({agent_id}): {info['description']}")
```
