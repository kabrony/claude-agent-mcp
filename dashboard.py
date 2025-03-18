"""
Enhanced Terminal Dashboard for Claude Agent
"""
import os
import sys
import time
import asyncio
import argparse
import json
from datetime import datetime, timedelta
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree
from rich.columns import Columns
from rich import box
from dotenv import load_dotenv

# Import agent components
from agent import ClaudeAgent
from utils import Timer, setup_environment, log

# Initialize console
console = Console()

class EnhancedDashboard:
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
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]Initializing agent...[/]"),
                console=console
            ) as progress:
                progress.add_task("init", total=None)
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
        
        # Split info panel vertically
        self.layout["info"].split(
            Layout(name="system_info", size=12),
            Layout(name="memory_stats", ratio=1),
            Layout(name="tools", size=10)
        )
        
        # Conversation history
        self.conversation = []
        
        # Active conversation ID
        self.active_conversation_id = None
        
        # Status information
        self.status = {
            "last_query_time": None,
            "memory_stats": {},
            "system_info": {},
            "tools_available": [],
            "use_extended_thinking": False,
            "use_tools": True
        }
        
        # Query in progress flag
        self.query_in_progress = False
        
        # Update system info
        if self.agent_initialized:
            self.update_system_info()
            # Load any recent conversations
            self.load_conversations()

    def load_conversations(self):
        """Load agent's existing conversations"""
        if self.agent_initialized:
            conversations = self.agent.claude.get_conversations()
            if conversations and len(conversations) > 0:
                # Set most recent conversation as active
                latest = max(conversations, key=lambda x: x["updated_at"])
                self.active_conversation_id = latest["id"]
                self.agent.claude.switch_conversation(self.active_conversation_id)
                
                # Populate conversation history
                messages = self.agent.claude.conversations[self.active_conversation_id]["messages"]
                for msg in messages:
                    self.conversation.append({
                        "role": msg.get("role"),
                        "content": msg.get("content")
                    })
        
    def make_header(self):
        """Create the header panel"""
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="center", ratio=2)
        grid.add_column(justify="right")
        
        # Add settings indicators
        settings = []
        if self.status["use_extended_thinking"]:
            settings.append("[bold green]Extended Thinking ON[/]")
        else:
            settings.append("[dim]Extended Thinking off[/]")
            
        if self.status["use_tools"]:
            settings.append("[bold green]Tools ON[/]")
        else:
            settings.append("[dim]Tools off[/]")
        
        grid.add_row(
            f"[bold blue]OrganiX[/bold blue]",
            f"[bold blue]Claude Agent[/bold blue] [dim]v1.0.0[/dim]",
            f"{' | '.join(settings)} | {datetime.now().strftime('[dim]%Y-%m-%d %H:%M:%S[/dim]')}"
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
        grid.add_column(justify="center")
        grid.add_column(justify="right")
        grid.add_row(
            status,
            f"Memory: {sum(self.status['memory_stats'].get(k, {}).get('count', 0) for k in ['episodic', 'semantic', 'procedural'])} items",
            "[T]oggle settings | [C]lear conversation | [S]ave | [Q]uit"
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
            
            # Skip system messages
            if role == "system":
                continue
                
            # Style differently based on role
            role_style = "blue" if role == "user" else "green"
            role_display = "You" if role == "user" else "Claude"
            
            # For markdown rendering, only do it for assistant responses
            if role == "assistant":
                content_display = Markdown(content)
            else:
                content_display = Text(content)
                
            conversation_table.add_row(f"[{role_style}]{role_display}[/{role_style}]", content_display)
        
        # Add title with conversation info if available
        title = "Conversation"
        if self.active_conversation_id and self.agent_initialized:
            if self.active_conversation_id in self.agent.claude.conversations:
                conv = self.agent.claude.conversations[self.active_conversation_id]
                title = f"Conversation: {conv['title']}"
        
        return Panel(
            conversation_table,
            title=title,
            border_style="green"
        )
        
    def make_system_info_panel(self):
        """Create the system info panel"""
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
        
        # Add Claude model info
        info_table.add_row("Claude Model", self.agent.claude.model)
        
        # Add API usage info
        analytics = self.agent.get_conversation_analytics()
        info_table.add_row("API Requests", str(analytics.get("total_requests", 0)))
        info_table.add_row("Total Tokens", f"{analytics.get('total_tokens', 0):,}")
        
        # Last Query Time
        if self.status["last_query_time"]:
            elapsed = time.time() - self.status["last_query_time"]
            info_table.add_row("Last Query", f"{elapsed:.2f} seconds ago")
        
        return Panel(
            info_table,
            title="System Information",
            border_style="yellow"
        )
        
    def make_memory_stats_panel(self):
        """Create the memory statistics panel"""
        if not self.agent_initialized:
            return Panel(
                Text("Agent not initialized", style="dim"),
                title="Memory Statistics",
                border_style="magenta"
            )
            
        # Memory statistics as a tree
        memory_tree = Tree("📊 [bold]Memory Stats[/]")
        
        for memory_type in ["episodic", "semantic", "procedural"]:
            stats = self.status["memory_stats"].get(memory_type, {})
            count = stats.get("count", 0)
            
            # Skip if no memories of this type
            if count == 0:
                memory_tree.add(f"[dim]{memory_type.title()}: Empty[/]")
                continue
                
            mem_node = memory_tree.add(f"[bold]{memory_type.title()}[/]: {count} items")
            
            # Add categories if available
            categories = stats.get("categories", {})
            if categories:
                for category, cat_count in categories.items():
                    mem_node.add(f"[dim]{category}[/]: {cat_count}")
                    
            # Add average importance
            avg_importance = stats.get("avg_importance", 0)
            if avg_importance:
                mem_node.add(f"[yellow]Avg Importance[/]: {avg_importance:.1f}/5.0")
                
        # Add cache info
        cache_hits = self.status["memory_stats"].get("episodic", {}).get("cache_hits", 0)
        cache_misses = self.status["memory_stats"].get("episodic", {}).get("cache_misses", 0)
        
        if cache_hits or cache_misses:
            cache_node = memory_tree.add("[bold cyan]Cache Stats[/]")
            total = cache_hits + cache_misses
            hit_rate = (cache_hits / total) * 100 if total > 0 else 0
            cache_node.add(f"Hit Rate: {hit_rate:.1f}% ({cache_hits}/{total})")
            
        # Add memory maintenance info
        if hasattr(self, "last_maintenance"):
            days_ago = (datetime.now() - self.last_maintenance).days
            memory_tree.add(f"[dim]Last maintenance: {days_ago} days ago[/]")
            
        return Panel(
            memory_tree,
            title="Memory Statistics",
            border_style="magenta"
        )
        
    def make_tools_panel(self):
        """Create the tools panel"""
        if not self.agent_initialized:
            return Panel(
                Text("Agent not initialized", style="dim"),
                title="Available Tools",
                border_style="cyan"
            )
            
        tools = self.status["tools_available"]
        
        if not tools:
            return Panel(
                Text("No tools available", style="dim"),
                title="Available Tools",
                border_style="cyan"
            )
            
        tools_table = Table(show_header=False, expand=True, box=None)
        tools_table.add_column("Tool", style="bold cyan")
        
        for tool in tools:
            tools_table.add_row(tool)
            
        return Panel(
            tools_table,
            title=f"Available Tools ({len(tools)})",
            border_style="cyan"
        )
        
    def update_system_info(self):
        """Update system information"""
        if self.agent_initialized:
            self.status["system_info"] = self.agent.system.get_system_info()
            self.status["memory_stats"] = self.agent.get_memory_stats()
            self.status["tools_available"] = self.agent.mcp.get_registered_tools()
        
    def update_display(self):
        """Update all panels in the layout"""
        self.layout["header"].update(self.make_header())
        self.layout["conversation"].update(self.make_conversation_panel())
        self.layout["system_info"].update(self.make_system_info_panel())
        self.layout["memory_stats"].update(self.make_memory_stats_panel())
        self.layout["tools"].update(self.make_tools_panel())
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
            if self.status["use_tools"]:
                response = await self.agent.process_query_with_tools(
                    query, 
                    max_tokens=4096
                )
            else:
                response = await self.agent.process_query(
                    query, 
                    max_tokens=4096,
                    extended_thinking=self.status["use_extended_thinking"]
                )
            
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
            
    async def handle_key_command(self, key):
        """Handle keyboard commands"""
        key = key.lower()
        
        if key == "t":
            # Show settings toggle menu
            self.update_display()
            console.print("\n[bold]Settings:[/]")
            console.print("1. Toggle Extended Thinking (currently: {})".format(
                "ON" if self.status["use_extended_thinking"] else "OFF"))
            console.print("2. Toggle Tool Usage (currently: {})".format(
                "ON" if self.status["use_tools"] else "OFF"))
            console.print("3. Back to dashboard")
            
            choice = await asyncio.to_thread(Prompt.ask, "[bold]Select option[/]", choices=["1", "2", "3"])
            
            if choice == "1":
                self.status["use_extended_thinking"] = not self.status["use_extended_thinking"]
                console.print("[green]Extended thinking mode: {}[/]".format(
                    "Enabled" if self.status["use_extended_thinking"] else "Disabled"))
            elif choice == "2":
                self.status["use_tools"] = not self.status["use_tools"]
                console.print("[green]Tool usage: {}[/]".format(
                    "Enabled" if self.status["use_tools"] else "Disabled"))
                
        elif key == "c":
            # Clear conversation
            if len(self.conversation) > 0:
                if await asyncio.to_thread(Confirm.ask, "Clear the current conversation?"):
                    self.conversation = []
                    self.agent.claude.clear_conversation()
                    console.print("[green]Conversation cleared[/]")
                    
        elif key == "s":
            # Save conversation
            if len(self.conversation) > 0:
                filename = await asyncio.to_thread(Prompt.ask, 
                    "[bold]Enter filename to save conversation[/]", 
                    default="conversation_{}.json".format(
                        datetime.now().strftime("%Y%m%d_%H%M%S")
                    )
                )
                
                saved_file = self.agent.save_conversation(filename)
                if saved_file:
                    console.print(f"[green]Conversation saved to {saved_file}[/]")
                else:
                    console.print("[red]Failed to save conversation[/]")
                    
        elif key == "m":
            # Memory maintenance
            if await asyncio.to_thread(Confirm.ask, "Perform memory maintenance? This will prune old, less important memories."):
                pruned = self.agent.maintain_memory()
                self.last_maintenance = datetime.now()
                console.print(f"[green]Memory maintenance complete. Pruned {pruned} memories.[/]")
                self.update_system_info()
                
        elif key == "l":
            # Load conversation
            filename = await asyncio.to_thread(Prompt.ask, "[bold]Enter filename to load conversation[/]")
            
            if os.path.exists(filename):
                if self.agent.load_conversation(filename):
                    self.active_conversation_id = self.agent.claude.current_conversation_id
                    # Update conversation history
                    self.conversation = []
                    for msg in self.agent.claude.messages:
                        self.conversation.append({
                            "role": msg.get("role"),
                            "content": msg.get("content")
                        })
                    console.print(f"[green]Conversation loaded from {filename}[/]")
                else:
                    console.print("[red]Failed to load conversation[/]")
            else:
                console.print(f"[red]File not found: {filename}[/]")
                
        elif key == "n":
            # New conversation
            if await asyncio.to_thread(Confirm.ask, "Start a new conversation?"):
                title = await asyncio.to_thread(Prompt.ask, 
                    "[bold]Enter conversation title[/]", 
                    default=f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
                
                self.agent.create_new_conversation(title)
                self.active_conversation_id = self.agent.claude.current_conversation_id
                self.conversation = []
                console.print(f"[green]New conversation started: {title}[/]")
            
    async def run(self):
        """Run the dashboard"""
        with Live(self.layout, refresh_per_second=4, screen=True) as live:
            self.update_display()
            
            try:
                while True:
                    # Get query from user
                    self.update_display()
                    query = await asyncio.to_thread(
                        Prompt.ask, 
                        "\n[bold blue]Enter your query[/bold blue] [dim](or command: /t=toggle, /c=clear, /s=save, /m=maintenance, /l=load, /n=new, /q=quit)[/dim]"
                    )
                    
                    # Handle commands
                    if query.startswith("/"):
                        command = query[1:].lower()
                        if command == "q":
                            console.print("\n[bold]Exiting Claude Agent Dashboard[/bold]")
                            break
                        
                        await self.handle_key_command(command[0])
                        continue
                    
                    # Handle the query
                    await self.handle_query(query)
                    self.update_display()
                    
            except KeyboardInterrupt:
                console.print("\n[bold]Exiting Claude Agent Dashboard[/bold]")
                sys.exit(0)

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Enhanced Claude Agent Dashboard")
    parser.add_argument("--query", "-q", help="Initial query to process")
    args = parser.parse_args()
    
    # Initialize dashboard
    dashboard = EnhancedDashboard()
    
    # Handle initial query if provided
    if args.query:
        await dashboard.handle_query(args.query)
    
    # Run the dashboard
    await dashboard.run()

if __name__ == "__main__":
    asyncio.run(main())
