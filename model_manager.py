"""
Model Manager - Utility for switching between Claude models and environments
"""
import os
import json
import asyncio
import argparse
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.markdown import Markdown
from dotenv import load_dotenv, set_key, find_dotenv

# Initialize console
console = Console()

# Model information
AVAILABLE_MODELS = {
    "claude-3-7-sonnet-20250219": {
        "name": "Claude 3.7 Sonnet",
        "description": "Latest Claude model with enhanced reasoning",
        "context_window": 200000,
        "recommended_for": "General purpose, complex reasoning tasks",
        "token_limit": 200000
    },
    "claude-3-opus-20240229": {
        "name": "Claude 3 Opus",
        "description": "Most capable Claude model for complex tasks",
        "context_window": 200000,
        "recommended_for": "Complex reasoning, advanced coding, detailed analysis",
        "token_limit": 200000
    },
    "claude-3-sonnet-20240229": {
        "name": "Claude 3 Sonnet",
        "description": "Balanced Claude model for general tasks",
        "context_window": 180000,
        "recommended_for": "General purpose, good balance of capability and cost",
        "token_limit": 180000
    },
    "claude-3-haiku-20240307": {
        "name": "Claude 3 Haiku",
        "description": "Fast, efficient Claude model",
        "context_window": 150000,
        "recommended_for": "Quick responses, chat, simple tasks",
        "token_limit": 150000
    }
}

class ModelManager:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get current model
        self.current_model = os.getenv("CLAUDE_MODEL", "claude-3-7-sonnet-20250219")
        
        # Check for API key
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.has_api_key = bool(self.api_key)
        
        # Environment profiles
        self.env_file = ".env"
        self.profiles_file = "env_profiles.json"
        self.profiles = self._load_profiles()
        
    def _load_profiles(self):
        """Load environment profiles from file"""
        if os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, 'r') as f:
                    return json.load(f)
            except:
                console.print("[yellow]Warning: Could not load profiles file. Using defaults.[/]")
                
        # Default profiles
        return {
            "default": {
                "name": "Default",
                "model": "claude-3-7-sonnet-20250219",
                "description": "Standard configuration"
            },
            "development": {
                "name": "Development",
                "model": "claude-3-haiku-20240307",
                "description": "Fast responses for development"
            },
            "production": {
                "name": "Production",
                "model": "claude-3-opus-20240229",
                "description": "High quality for production use"
            }
        }
        
    def _save_profiles(self):
        """Save environment profiles to file"""
        try:
            with open(self.profiles_file, 'w') as f:
                json.dump(self.profiles, f, indent=2)
            return True
        except:
            console.print("[red]Error: Could not save profiles file.[/]")
            return False
            
    def _update_env_file(self, key, value):
        """Update a value in the .env file"""
        dotenv_file = find_dotenv()
        if not dotenv_file:
            # Create .env file if it doesn't exist
            with open(".env", "w") as f:
                f.write(f"{key}={value}\n")
            return True
            
        try:
            set_key(dotenv_file, key, value)
            return True
        except:
            console.print(f"[red]Error: Could not update {key} in .env file.[/]")
            return False
            
    def list_models(self):
        """Display information about available models"""
        table = Table(title="Available Claude Models")
        
        table.add_column("Model ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Description", style="")
        table.add_column("Context Window", style="magenta")
        table.add_column("Recommended For", style="yellow")
        
        for model_id, info in AVAILABLE_MODELS.items():
            current = "➡️ " if model_id == self.current_model else ""
            table.add_row(
                f"{current}{model_id}",
                info["name"],
                info["description"],
                f"{info['context_window']:,}",
                info["recommended_for"]
            )
            
        console.print(table)
        
    def set_model(self, model_id):
        """Set the current model"""
        if model_id not in AVAILABLE_MODELS:
            console.print(f"[red]Error: Unknown model '{model_id}'[/]")
            return False
            
        # Update the environment variable
        if self._update_env_file("CLAUDE_MODEL", model_id):
            self.current_model = model_id
            console.print(f"[green]Model set to: {AVAILABLE_MODELS[model_id]['name']} ({model_id})[/]")
            return True
        return False
        
    def set_api_key(self, api_key=None):
        """Set the Anthropic API key"""
        if api_key is None:
            api_key = Prompt.ask("Enter your Anthropic API key", password=True)
            
        # Update the environment variable
        if self._update_env_file("ANTHROPIC_API_KEY", api_key):
            self.api_key = api_key
            self.has_api_key = bool(api_key)
            console.print("[green]API key updated successfully[/]")
            return True
        return False
        
    def list_profiles(self):
        """Display available environment profiles"""
        table = Table(title="Environment Profiles")
        
        table.add_column("Profile ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Model", style="magenta")
        table.add_column("Description", style="")
        
        current_profile = self._get_current_profile_id()
        
        for profile_id, info in self.profiles.items():
            current = "➡️ " if profile_id == current_profile else ""
            table.add_row(
                f"{current}{profile_id}",
                info["name"],
                info.get("model", "Not specified"),
                info.get("description", "")
            )
            
        console.print(table)
        
    def _get_current_profile_id(self):
        """Get the ID of the current profile based on model"""
        for profile_id, info in self.profiles.items():
            if info.get("model") == self.current_model:
                return profile_id
        return None
        
    def apply_profile(self, profile_id):
        """Apply an environment profile"""
        if profile_id not in self.profiles:
            console.print(f"[red]Error: Unknown profile '{profile_id}'[/]")
            return False
            
        profile = self.profiles[profile_id]
        
        # Update model
        if "model" in profile:
            self.set_model(profile["model"])
            
        # Update other environment variables
        for key, value in profile.items():
            if key not in ["name", "description", "model"]:
                self._update_env_file(key, value)
                
        console.print(f"[green]Applied profile: {profile['name']}[/]")
        return True
        
    def create_profile(self):
        """Create a new environment profile"""
        profile_id = Prompt.ask("Enter profile ID (lowercase, no spaces)")
        
        if profile_id in self.profiles:
            if not Confirm.ask(f"Profile '{profile_id}' already exists. Overwrite?"):
                return False
                
        name = Prompt.ask("Enter profile name", default=profile_id.title())
        
        # Choose a model
        console.print("\nAvailable models:")
        for i, (model_id, info) in enumerate(AVAILABLE_MODELS.items(), 1):
            console.print(f"{i}. {info['name']} ({model_id})")
            
        model_choice = Prompt.ask(
            "Choose model (enter number)", 
            choices=[str(i) for i in range(1, len(AVAILABLE_MODELS)+1)],
            default="1"
        )
        
        model_id = list(AVAILABLE_MODELS.keys())[int(model_choice)-1]
        
        description = Prompt.ask("Enter profile description", default=f"Profile using {AVAILABLE_MODELS[model_id]['name']}")
        
        # Create profile
        self.profiles[profile_id] = {
            "name": name,
            "model": model_id,
            "description": description
        }
        
        # Save profiles
        if self._save_profiles():
            console.print(f"[green]Profile '{profile_id}' created successfully[/]")
            
            # Ask if user wants to apply it
            if Confirm.ask("Apply this profile now?"):
                self.apply_profile(profile_id)
                
            return True
        return False
        
    def delete_profile(self, profile_id):
        """Delete an environment profile"""
        if profile_id not in self.profiles:
            console.print(f"[red]Error: Unknown profile '{profile_id}'[/]")
            return False
            
        if len(self.profiles) <= 1:
            console.print("[red]Error: Cannot delete the last profile[/]")
            return False
            
        if Confirm.ask(f"Are you sure you want to delete profile '{self.profiles[profile_id]['name']}'?"):
            del self.profiles[profile_id]
            
            # Save profiles
            if self._save_profiles():
                console.print(f"[green]Profile '{profile_id}' deleted successfully[/]")
                return True
                
        return False
        
    def check_environment(self):
        """Check the current environment configuration"""
        console.print(Panel(
            f"[bold]Current Environment[/]\n\n"
            f"Model: {AVAILABLE_MODELS.get(self.current_model, {}).get('name', 'Unknown')} ({self.current_model})\n"
            f"API Key: {'Configured' if self.has_api_key else '[red]Missing[/]'}\n"
            f"Profile: {self._get_current_profile_id() or 'Custom'}\n",
            title="Environment Check",
            border_style="green" if self.has_api_key else "red"
        ))
        
        if not self.has_api_key:
            console.print("[yellow]Warning: API key is not configured. Use 'set-api-key' to configure it.[/]")
            
        return self.has_api_key

async def main():
    """Main function to run the model manager"""
    parser = argparse.ArgumentParser(description="Claude Model Manager")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List models command
    list_parser = subparsers.add_parser("list-models", help="List available Claude models")
    
    # Set model command
    set_parser = subparsers.add_parser("set-model", help="Set the Claude model to use")
    set_parser.add_argument("model_id", help="Model ID to set")
    
    # Set API key command
    key_parser = subparsers.add_parser("set-api-key", help="Set the Anthropic API key")
    key_parser.add_argument("--key", help="API key (if not provided, will prompt)")
    
    # Profile commands
    list_profiles_parser = subparsers.add_parser("list-profiles", help="List available environment profiles")
    
    apply_parser = subparsers.add_parser("apply-profile", help="Apply an environment profile")
    apply_parser.add_argument("profile_id", help="Profile ID to apply")
    
    create_parser = subparsers.add_parser("create-profile", help="Create a new environment profile")
    
    delete_parser = subparsers.add_parser("delete-profile", help="Delete an environment profile")
    delete_parser.add_argument("profile_id", help="Profile ID to delete")
    
    # Check environment command
    check_parser = subparsers.add_parser("check", help="Check the current environment configuration")
    
    # Interactive mode
    interactive_parser = subparsers.add_parser("interactive", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # Initialize model manager
    manager = ModelManager()
    
    # Execute command
    if args.command == "list-models":
        manager.list_models()
    elif args.command == "set-model":
        manager.set_model(args.model_id)
    elif args.command == "set-api-key":
        manager.set_api_key(args.key)
    elif args.command == "list-profiles":
        manager.list_profiles()
    elif args.command == "apply-profile":
        manager.apply_profile(args.profile_id)
    elif args.command == "create-profile":
        manager.create_profile()
    elif args.command == "delete-profile":
        manager.delete_profile(args.profile_id)
    elif args.command == "check":
        manager.check_environment()
    elif args.command == "interactive" or not args.command:
        # Interactive mode
        while True:
            console.print("\n[bold cyan]Claude Model Manager[/] - Interactive Mode\n")
            console.print("1. List available models")
            console.print("2. Set model")
            console.print("3. Set API key")
            console.print("4. List environment profiles")
            console.print("5. Apply profile")
            console.print("6. Create profile")
            console.print("7. Delete profile")
            console.print("8. Check environment")
            console.print("9. Exit")
            
            choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9"])
            
            if choice == "1":
                manager.list_models()
            elif choice == "2":
                manager.list_models()
                model_id = Prompt.ask("Enter model ID to set")
                manager.set_model(model_id)
            elif choice == "3":
                manager.set_api_key()
            elif choice == "4":
                manager.list_profiles()
            elif choice == "5":
                manager.list_profiles()
                profile_id = Prompt.ask("Enter profile ID to apply")
                manager.apply_profile(profile_id)
            elif choice == "6":
                manager.create_profile()
            elif choice == "7":
                manager.list_profiles()
                profile_id = Prompt.ask("Enter profile ID to delete")
                manager.delete_profile(profile_id)
            elif choice == "8":
                manager.check_environment()
            elif choice == "9":
                break
                
            # Pause for user to read output
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    asyncio.run(main())
