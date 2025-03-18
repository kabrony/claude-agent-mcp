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
10. [AI Model Integration](#ai-model-integration)
11. [Browser Integration](#browser-integration)
12. [Best Practices](#best-practices)

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

OrganiX implements a sophisticated multi-agent coordination system that allows specialized agents to collaborate on complex tasks.

### Agent Types

The system includes several specialized agents:

- **Research Specialist**: Expert in information gathering and synthesis
- **Code Specialist**: Expert in code generation and analysis
- **Blockchain Specialist**: Expert in blockchain technologies and operations
- **MCP Specialist**: Expert in tool usage and integration
- **AGI Specialist**: Expert in complex reasoning across domains

### Coordination Mechanisms

Agents collaborate through several mechanisms:

1. **Intent-based routing**: Queries are automatically routed to the most appropriate agent
2. **Multi-agent collaboration**: Multiple agents can work on a single query
3. **Synthesis**: The AGI specialist can synthesize insights from multiple agents

```python
# Example: Multi-agent collaboration
from advanced_chat import coordinator

result = await coordinator.multi_agent_collaboration(
    "How can I build a Solana dApp that uses AI for predictive analytics?"
)
```

## Advanced Capabilities

### Zero-Knowledge Integration

OrganiX supports zero-knowledge proofs for privacy-preserving operations:

```python
# Create a zero-knowledge proof of knowledge
proof = await coordinator.create_zero_knowledge_proof(
    "knowledge", 
    {"secret_data": "sensitive information"}
)

# Verify the proof
verification = await coordinator.verify_zero_knowledge_proof(proof)
```

### Blockchain Capabilities

The system offers comprehensive blockchain capabilities with Solana integration:

```python
# Get blockchain data for an address
data = await coordinator.get_blockchain_data("FxsqrtTMuAKYgNwiGRD3FwVr1FtsrfUJMPWq49dZVERP")

# Generate Phantom wallet connection HTML
connect_button = coordinator.get_phantom_connect_html("My dApp")
```

## AI Model Integration

OrganiX supports integration with multiple AI models to leverage their unique capabilities.

### Claude Integration

Claude is the primary AI model powering OrganiX, with deep integration:

```python
from claude_client import ClaudeClient

# Initialize client
client = ClaudeClient()

# Send a message
response = await client.send_message("What are the benefits of MCP?")

# Use streaming for real-time responses
async for chunk in client.stream_message("Tell me about Solana..."):
    print(chunk, end="")
```

### Perplexity Integration

Perplexity AI is integrated for enhanced search and knowledge retrieval:

```python
from perplexity_integration import perplexity_client

# Search with Perplexity
results = await perplexity_client.search("Latest developments in ZK proofs")

# Focus search on academic sources
academic_results = await perplexity_client.academic_search("quantum computing advances")
```

### OpenAI Integration

OpenAI models can be used for specialized tasks:

```python
from openai_integration import openai_client

# Generate embeddings
embeddings = await openai_client.create_embeddings("Text to embed")

# Use GPT for specific tasks
response = await openai_client.generate(
    "Summarize this technical paper",
    model="gpt-4"
)
```

### DeepSeek Integration

DeepSeek models are available for code generation and analysis:

```python
from deepseek_integration import deepseek_client

# Generate code
code = await deepseek_client.generate_code(
    "Create a sorting algorithm that works in O(n log n) time"
)
```

## Browser Integration

OrganiX supports deep integration with browsers for enhanced web interaction.

### Brave Integration

The Brave browser integration allows for privacy-focused web operations:

```python
from brave_integration import brave_client

# Search with Brave
results = await brave_client.search("Privacy-preserving technologies")

# Use Brave's privacy features
private_results = await brave_client.private_search("My sensitive query")
```

### Browser Automation

OrganiX can automate browser interactions for complex workflows:

```python
from browser_automation import browser

# Navigate to a page
await browser.navigate("https://example.com")

# Fill a form
await browser.fill_form({
    "username": "user",
    "password": "pass"
})

# Click a button
await browser.click("#submit-button")
```

## Extending the System

OrganiX is designed for easy extension with new tools, agents, and capabilities.

### Adding New Tools

```python
# Add a custom tool
mcp.register_tool(
    "sentiment_analysis",
    "Analyze sentiment of text",
    lambda text: analyze_sentiment(text)
)
```

### Creating Custom Agents

```python
from advanced_chat import ChatPersona, coordinator

# Create a custom agent
finance_agent = ChatPersona(
    name="Finance Specialist",
    description="Expert in financial analysis and advice",
    system_prompt="You are a financial expert specializing in cryptocurrency..."
)

# Register the agent
coordinator.register_agent("finance", finance_agent)
```

### Integrating New Services

The system can be extended with new external services:

```python
# Register a new service client
service_client = ExternalServiceClient(api_key="your_api_key")

# Create a tool that uses the service
mcp.register_tool(
    "external_service",
    "Use the external service API",
    service_client.make_request
)
```

## Best Practices

### Security Considerations

- Always validate user inputs before passing to tools
- Use environment variables for API keys and secrets
- Implement rate limiting for external API calls
- Apply proper error handling for all tool executions

### Performance Optimization

- Use the memory cache for frequently accessed data
- Implement parallel processing for independent operations
- Optimize token usage in AI model calls
- Consider streaming responses for long outputs

### Development Workflow

1. Create a feature branch for new capabilities
2. Test tools in isolation before registration
3. Update documentation with new features
4. Follow the pull request workflow for contributions

## Troubleshooting

### Common Issues

- **Tool Execution Failures**: Verify API keys and network connectivity
- **Memory Errors**: Check disk space for persistent memory store
- **Model Integration Issues**: Ensure API key permissions are correct
- **Browser Integration Problems**: Check WebDriver compatibility

### Logging and Monitoring

OrganiX includes comprehensive logging:

```python
from utils import log

# Log different levels
log.debug("Detailed debug information")
log.info("General information")
log.warning("Warning message")
log.error("Error message")
```

### Getting Help

For issues, questions, or feature requests:

- Create an issue on the GitHub repository
- Contact the OrganiX development team
- Check the FAQ in the project wiki

---

*This documentation is maintained by the OrganiX team and is updated regularly to reflect the latest capabilities and best practices.*
