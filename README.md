# OrganiX Claude Agent

OrganiX is a powerful personal agent with cross-platform capabilities and Model Context Protocol (MCP) integration using the Claude 3.7 API.

## Features

- 🧠 **Advanced Memory System**: Utilizes ChromaDB for episodic, semantic, and procedural memory
- 🔄 **Cross-Platform Operations**: Seamlessly works across Windows and Linux environments
- 🔍 **Web Research Capabilities**: Integrated with Exa for comprehensive web search and content extraction
- 🧰 **Tool Integration**: Full MCP support for extensible tool usage
- 📊 **Rich Terminal Interface**: Beautifully formatted outputs using Rich
- 🔄 **Streaming Support**: Real-time streaming responses from Claude API
- 💻 **Remote System Connectivity**: SSH integration for remote Ubuntu systems

## Quick Start

### Windows

1. Clone this repository
2. Run `install_dependencies.bat` to set up the environment
3. Create a `.env` file with your API keys (see Environment Variables section)
4. Activate the virtual environment: `venv\Scripts\activate`
5. Run the agent: `python agent.py --query "Your question here"`

### Linux/Mac

1. Clone this repository
2. Make the installation script executable: `chmod +x install_dependencies.sh`
3. Run `./install_dependencies.sh` to set up the environment
4. Create a `.env` file with your API keys (see Environment Variables section)
5. Activate the virtual environment: `source venv/bin/activate`
6. Run the agent: `python agent.py --query "Your question here"`

## Environment Variables

Create a `.env` file in the project root with the following variables:

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
EXA_API_KEY=your_exa_api_key_here
```

You can obtain these API keys from:
- [Anthropic Console](https://console.anthropic.com/)
- [Exa Dashboard](https://exa.ai/)

## Usage

### Terminal Dashboard

OrganiX includes a rich terminal dashboard for interactive use:

```bash
# Launch the dashboard
python dashboard.py

# Start dashboard with initial query
python dashboard.py --query "What's the latest news on AI?"
```

The dashboard provides:
- Real-time conversation history
- System information monitoring
- Memory statistics
- Interactive query input

### Basic Commands

```bash
# Process a query
python agent.py --query "What is the weather today?"

# Stream a response (real-time output)
python agent.py --query "Tell me about quantum computing" --stream

# Research a topic
python agent.py --research "Climate change solutions"

# Display agent information
python agent.py
```

### Advanced Usage

```python
# Using the agent in your own code
import asyncio
from agent import ClaudeAgent

async def main():
    agent = ClaudeAgent()
    
    # Process a query
    response = await agent.process_query("What is the meaning of life?")
    print(response)
    
    # Research a topic
    research = await agent.research_topic("Artificial intelligence ethics")
    print(research)
    
    # Connect to remote system
    result = await agent.connect_to_remote("your-server.com", "username", password="password")
    print(result)

asyncio.run(main())
```

## Architecture

The agent is built on a modular architecture with the following components:

- **Claude Client**: Handles communication with the Claude API
- **Memory System**: Manages different types of memory using ChromaDB
- **System Bridge**: Provides cross-platform operation capabilities
- **MCP Manager**: Implements the Model Context Protocol for tool usage
- **Web Researcher**: Handles web search and information extraction

## Tool Integration

The agent comes with several built-in tools:

| Tool | Description |
|------|-------------|
| `list_files` | Lists files in a directory |
| `web_search` | Searches the web for information |
| `extract_url` | Extracts content from a specific URL |
| `execute_command` | Executes commands on the local system |
| `retrieve_memory` | Retrieves memories relevant to a query |

## Development

### Project Structure

```
claude-agent-mcp/
├── agent.py            # Main agent implementation
├── claude_client.py    # Claude API client
├── dashboard.py        # Terminal dashboard interface
├── memory_system.py    # Memory management
├── mcp_manager.py      # Model Context Protocol integration
├── system_bridge.py    # Cross-platform functionality
├── web_research.py     # Web search capabilities
├── utils.py            # Utility functions
├── requirements.txt    # Dependencies
├── install_dependencies.bat  # Windows setup
└── install_dependencies.sh   # Linux/Mac setup
```

### Adding New Tools

To add a new tool to the agent, edit the `_register_tools` method in `agent.py`:

```python
def _register_tools(self):
    # ... existing tools
    
    # Add your new tool
    self.mcp.register_tool(
        "your_tool_name",
        "Description of what your tool does",
        your_tool_function
    )
```

### Extending the Dashboard

The terminal dashboard can be customized by modifying `dashboard.py`. Here are some example extensions:

- Add new panels for specific tools
- Customize the appearance with Rich styles
- Add keyboard shortcuts for common actions
- Implement visualizations for memory statistics

## Requirements

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

## License

MIT License

## Acknowledgments

- Built with [Anthropic Claude 3.7](https://www.anthropic.com/claude)
- Utilizes [ChromaDB](https://github.com/chroma-core/chroma) for vector storage
- Enhanced with [Exa](https://exa.ai) for web search capabilities
- Terminal UI powered by [Rich](https://github.com/Textualize/rich)
