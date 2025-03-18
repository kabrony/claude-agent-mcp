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

OrganiX implements a sophisticated multi-agent architecture that leverages MCP for coordination:

### Specialized Agents

The system includes several specialized agents:

- **Research Specialist**: Focused on information gathering and synthesis
- **Code Specialist**: Expert in generating and explaining code
- **Blockchain Specialist**: Handles blockchain interactions and explanations
- **MCP Specialist**: Manages tools and integrations
- **AGI Specialist**: Tackles complex, cross-domain problems

### Routing and Coordination

The `MultiAgentCoordinator` class handles:

1. **Intent Detection**: Analyzes queries to determine the most appropriate agent
2. **Agent Routing**: Directs queries to specialized agents
3. **Collaborative Processing**: Enables multiple agents to work together
4. **Response Synthesis**: Combines insights from different agents

```python
# Example: Multi-agent processing
from advanced_chat import coordinator

result = await coordinator.multi_agent_collaboration(
    "Create a Solana application that uses ZK proofs for privacy"
)
```

## Advanced Capabilities

### Zero-Knowledge Integration

OrganiX incorporates zero-knowledge proof technology, enabling:

- **Privacy-Preserving Verification**: Prove facts without revealing sensitive information
- **Ownership Verification**: Demonstrate ownership of assets without exposing private keys
- **Selective Disclosure**: Control what information is shared

```python
# Create a zero-knowledge proof
proof = await coordinator.create_zero_knowledge_proof(
    "knowledge", 
    {"secret_value": 42}
)

# Verify the proof
verification = await coordinator.verify_zero_knowledge_proof(proof)
```

### Blockchain Capabilities

The Solana integration provides:

- **Account Information**: Retrieve details about Solana accounts
- **Token Management**: Access token balances and transfers
- **NFT Integration**: View and manage NFT collections
- **Phantom Wallet Connection**: Connect to Phantom wallet for transactions

```python
# Get Solana account information
balance = await solana_integration.get_solana_balance("FxsqrtTMuAKYgNwiGRD3FwVr1FtsrfUJMPWq49dZVERP")

# Get Phantom wallet connection button
wallet_button = solana_integration.create_agent_wallet_button_html()
```

## Extending the System

### Adding New Tools

To add a new tool to the OrganiX MCP system:

1. Define the tool function:
```python
async def my_tool_function(param1, param2):
    # Tool implementation
    return result
```

2. Register with the MCP Manager:
```python
mcp.register_tool(
    "my_tool_name",
    "Description of what my tool does",
    my_tool_function
)
```

3. (Optional) Sync with Composio:
```python
await mcp.refresh_composio_tools()
```

### Creating Custom Agents

To add a new specialized agent:

1. Define the agent persona:
```python
from advanced_chat import ChatPersona

my_agent = ChatPersona(
    name="My Specialist",
    description="Specialized in specific domain tasks",
    system_prompt="You are a specialist agent within OrganiX..."
)
```

2. Register with the coordinator:
```python
from advanced_chat import coordinator

coordinator.register_agent("my_agent_id", my_agent)
```

## Best Practices

### Tool Design

- **Atomic Functionality**: Each tool should do one thing well
- **Clear Documentation**: Provide detailed descriptions and examples
- **Error Handling**: Implement robust error management
- **Input Validation**: Validate inputs to prevent issues
- **Asynchronous Design**: Use async/await for non-blocking operations

### Agent Integration

- **Specialized Personas**: Create focused agents for specific domains
- **Clear Intent Patterns**: Define clear patterns for routing queries
- **Context Management**: Properly handle conversation context
- **Memory Integration**: Leverage the memory system for continuity

### Security Considerations

- **Access Control**: Implement appropriate access controls for sensitive tools
- **Input Sanitization**: Sanitize inputs to prevent injection attacks
- **Rate Limiting**: Implement rate limiting for external API calls
- **Sensitive Data Handling**: Use secure methods for handling credentials

## Example Implementations

### Basic Tool Usage

```python
from mcp_manager import MCPManager

# Initialize the MCP manager
mcp = MCPManager()

# Register a simple tool
mcp.register_tool(
    "weather",
    "Get current weather for a location",
    async lambda location: await fetch_weather(location)
)

# Process a query using the tool
result = await mcp.process_with_tools("What's the weather in New York?")
```

### Advanced Multi-Agent Workflow

```python
from advanced_chat import coordinator

# Process with specific agents
blockchain_result = await coordinator.process_with_agent(
    "blockchain", 
    "How do I connect to a Solana wallet?"
)

# Collaborative processing
combined_result = await coordinator.multi_agent_collaboration(
    "Create a Python app that uses ZK proofs and MCP",
    agent_ids=["coder", "blockchain", "mcp"]
)

# Get explanation of the system
explanation = await coordinator.explain_multi_agent_system()
```

## Troubleshooting

### Common Issues

1. **Tool Not Found**: Ensure the tool is properly registered
2. **Composio Connection Failed**: Check API keys and network connectivity
3. **Agent Not Responding**: Verify Claude API credentials and quota
4. **Memory Retrieval Issues**: Check ChromaDB setup and permissions

### Debugging

The system includes comprehensive logging:

```python
from utils import log

# Enable debug logging
log.setLevel("DEBUG")

# Log a test message
log.debug("Testing debugging output")
```

## Resources

- [Composio Documentation](https://docs.composio.dev/)
- [Model Context Protocol Spec](https://github.com/anthropics/anthropic-cookbook/tree/main/api/model_context_protocol)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Solana Web3.js Documentation](https://solana-labs.github.io/solana-web3.js/)

## Contributing

To contribute to the OrganiX MCP integration:

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Submit a pull request

We welcome contributions in the following areas:
- New tools
- Improved agent personas
- Enhanced documentation
- Bug fixes
- Performance optimizations
