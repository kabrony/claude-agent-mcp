"""
Terminal Dashboard for Claude Agent
"""
import os
import sys
import time
import asyncio
import argparse
from datetime import datetime
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.syntax import Syntax
from dotenv import load_dotenv

# Import agent components
from agent import ClaudeAgent
from utils import Timer, setup_environment

# Initialize console
console = Console()

class Dashboard:
    def __init__(self):
        """Initialize the dashboard"""
        # Setup environment
        setup_environment()
        load_dotenv()
        
        # Check for API keys
        self.api_key_warning = ""
        if not os.getenv("ANTHROPIC_API_KEY"):
            self.api_key_warning = "⚠️ Missing ANTHROPIC_API_KEY in .env file"
            
        # Initialize agent
        try:
            self.agent = ClaudeAgent()
            self.agent_initialized = True
        except Exception as e:
            self.agent_initialized = False
            self.agent_error = str(e)
        
        # Create layout
        self.layout = Layout(name="root")
        
        # Split the main layout
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        
        # Split the main area
        self.layout["main"].split_row(
            Layout(name="conversation", ratio=2),
            Layout(name="info", ratio=1),
        )
        
        # Conversation history
        self.conversation = []
        
        # Status information
        self.status = {
            "last_query_time": None,
            "memory_stats": {},
            "system_info": {}
        }
        
        # Query in progress flag
        self.query_in_progress = False
        
        # Update system info
        if self.agent_initialized:
            self.update_system_info()

    def make_header(self):
        """Create the header panel"""
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right")
        grid.add_row(
            f"[bold blue]OrganiX Claude Agent[/bold blue] [dim]v1.0.0[/dim]",
            datetime.now().strftime("[dim]%Y-%m-%d %H:%M:%S[/dim]")
        )
        
        return Panel(grid, style="blue")
        
    def make_footer(self):
        """Create the footer panel"""
        status = "✅ Ready" if not self.query_in_progress else "⏳ Processing query..."
        
        if not self.agent_initialized:
            status = f"❌ Agent initialization failed: {self.agent_error}"
        elif self.api_key_warning:
            status = self.api_key_warning
            
        grid = Table.grid(expand=True)
        grid.add_column(justify="left")
        grid.add_column(justify="right")
        grid.add_row(
            status,
            "Press Ctrl+C to exit"
        )
        
        return Panel(grid, style="blue")

    def make_conversation_panel(self):
        """Create the conversation panel"""
        if not self.conversation:
            return Panel(
                Text("Type your query below to start interacting with the agent.", style="dim"),
                title="Conversation",
                border_style="green"
            )
            
        # Create a table to display the conversation
        conversation_table = Table(show_header=False, expand=True, box=None)
        conversation_table.add_column("Role", style="bold", width=8)
        conversation_table.add_column("Content")
        
        for entry in self.conversation:
            role = entry["role"]
            content = entry["content"]
            
            # Style differently based on role
            role_style = "blue" if role == "user" else "green"
            role_display = "You" if role == "user" else "Claude"
            
            # For markdown rendering, only do it for assistant responses
            if role == "assistant":
                content_display = Markdown(content)
            else:
                content_display = Text(content)
                
            conversation_table.add_row(f"[{role_style}]{role_display}[/{role_style}]", content_display)
        
        return Panel(
            conversation_table,
            title="Conversation",
            border_style="green"
        )
        
    def make_info_panel(self):
        """Create the info panel with system and memory information"""
        if not self.agent_initialized:
            return Panel(
                Text("Agent not initialized", style="dim"),
                title="System Information",
                border_style="yellow"
            )
            
        # Create a table for the information
        info_table = Table(show_header=False, expand=True, box=None)
        info_table.add_column("Property", style="bold", width=15)
        info_table.add_column("Value")
        
        # System Information
        info_table.add_row("Platform", self.status["system_info"].get("platform", "Unknown"))
        info_table.add_row("Python", self.status["system_info"].get("python_version", "Unknown"))
        info_table.add_row("Connections", ", ".join(self.status["system_info"].get("connections", [])) or "None")
        
        # Add separator
        info_table.add_row("", "")
        
        # Memory Statistics
        info_table.add_row("[bold]Memory Stats[/bold]", "")
        for memory_type, count in self.status["memory_stats"].items():
            info_table.add_row(memory_type.title(), str(count))
            
        # Add separator
        info_table.add_row("", "")
        
        # Last Query Time
        if self.status["last_query_time"]:
            elapsed = time.time() - self.status["last_query_time"]
            info_table.add_row("Last Query", f"{elapsed:.2f} seconds ago")
        
        return Panel(
            info_table,
            title="System Information",
            border_style="yellow"
        )
        
    def update_system_info(self):
        """Update system information"""
        if self.agent_initialized:
            self.status["system_info"] = self.agent.system.get_system_info()
            self.status["memory_stats"] = self.agent.get_memory_stats()
        
    def update_display(self):
        """Update all panels in the layout"""
        self.layout["header"].update(self.make_header())
        self.layout["conversation"].update(self.make_conversation_panel())
        self.layout["info"].update(self.make_info_panel())
        self.layout["footer"].update(self.make_footer())
        
    async def handle_query(self, query):
        """Handle a user query"""
        if not query.strip():
            return
            
        # Add user query to conversation
        self.conversation.append({"role": "user", "content": query})
        
        if not self.agent_initialized:
            self.conversation.append({
                "role": "assistant", 
                "content": f"⚠️ Agent not initialized: {self.agent_error}"
            })
            return
            
        # Update status
        self.query_in_progress = True
        self.status["last_query_time"] = time.time()
        
        try:
            # Process the query
            response = await self.agent.process_query(query)
            
            # Add response to conversation
            self.conversation.append({"role": "assistant", "content": response})
            
            # Update system info
            self.update_system_info()
        except Exception as e:
            # Handle errors
            error_message = f"Error processing query: {str(e)}"
            self.conversation.append({"role": "assistant", "content": error_message})
        finally:
            # Reset status
            self.query_in_progress = False
            
    async def run(self):
        """Run the dashboard"""
        with Live(self.layout, refresh_per_second=4, screen=True):
            self.update_display()
            
            try:
                while True:
                    # Get query from user
                    self.update_display()
                    query = await asyncio.to_thread(Prompt.ask, "\n[bold blue]Enter your query[/bold blue]")
                    
                    # Handle the query
                    await self.handle_query(query)
                    self.update_display()
            except KeyboardInterrupt:
                console.print("\n[bold]Exiting Claude Agent Dashboard[/bold]")
                sys.exit(0)

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Claude Agent Dashboard")
    parser.add_argument("--query", "-q", help="Initial query to process")
    args = parser.parse_args()
    
    # Initialize dashboard
    dashboard = Dashboard()
    
    # Handle initial query if provided
    if args.query:
        await dashboard.handle_query(args.query)
    
    # Run the dashboard
    await dashboard.run()

if __name__ == "__main__":
    asyncio.run(main())
