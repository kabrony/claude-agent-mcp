"""
Configuration Manager - Centralized configuration system for API keys and settings
"""
import os
import json
import yaml
import shutil
import getpass
from pathlib import Path
from dotenv import load_dotenv, set_key, find_dotenv
from utils import log

class ConfigManager:
    def __init__(self, app_name="OrganiX"):
        self.app_name = app_name
        self.config_dir = self._get_config_dir()
        self.env_file = find_dotenv() or ".env"
        self.config_file = os.path.join(self.config_dir, "config.yaml")
        self.secrets_file = os.path.join(self.config_dir, "secrets.json")
        
        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Load configurations
        self.env_vars = self._load_env_vars()
        self.config = self._load_config()
        self.secrets = self._load_secrets()
        
        # Default API configurations
        self.default_apis = {
            "anthropic": {
                "api_key_env": "ANTHROPIC_API_KEY",
                "model_env": "CLAUDE_MODEL",
                "default_model": "claude-3-7-sonnet-20250219",
                "api_url": "https://api.anthropic.com/v1"
            },
            "exa": {
                "api_key_env": "EXA_API_KEY",
                "api_url": "https://api.exa.ai"
            },
            "composio": {
                "api_key_env": "COMPOSIO_API_KEY",
                "connection_id_env": "COMPOSIO_CONNECTION_ID",
                "integration_id_env": "COMPOSIO_INTEGRATION_ID",
                "api_url_env": "COMPOSIO_BASE_URL",
                "default_url": "https://api.composio.dev"
            },
            "solana": {
                "rpc_url_env": "SOLANA_RPC_URL",
                "network_env": "SOLANA_NETWORK",
                "private_key_env": "SOLANA_PRIVATE_KEY",
                "default_network": "mainnet-beta",
                "default_url": "https://api.mainnet-beta.solana.com"
            },
            "twitter": {
                "bearer_token_env": "TWITTER_BEARER_TOKEN",
                "api_key_env": "TWITTER_API_KEY",
                "api_secret_env": "TWITTER_API_SECRET",
                "access_token_env": "TWITTER_ACCESS_TOKEN",
                "access_secret_env": "TWITTER_ACCESS_SECRET"
            }
        }
        
    def _get_config_dir(self):
        """Get the appropriate configuration directory based on OS"""
        home = Path.home()
        
        if os.name == 'nt':  # Windows
            return os.path.join(home, "AppData", "Local", self.app_name)
        else:  # macOS / Linux
            return os.path.join(home, f".{self.app_name.lower()}")
            
    def _load_env_vars(self):
        """Load environment variables from .env file"""
        load_dotenv()
        
        # Get all environment variables
        env_vars = {}
        for api, config in self.default_apis.items():
            for key, env_var in config.items():
                if key.endswith('_env'):
                    env_value = os.environ.get(env_var)
                    if env_value:
                        env_vars[env_var] = env_value
                        
        return env_vars
        
    def _load_config(self):
        """Load configuration from YAML file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                log.error(f"Error loading config file: {e}")
        
        # Create default config if it doesn't exist
        default_config = {
            "app_name": self.app_name,
            "version": "1.0.0",
            "api_settings": {
                api_name: {
                    "enabled": True,
                    "use_local": True,
                    "timeout": 30
                } 
                for api_name in self.default_apis.keys()
            },
            "ui_settings": {
                "theme": "dark",
                "dashboard_layout": "default"
            },
            "memory_settings": {
                "max_memory_age_days": 30,
                "cache_enabled": True
            }
        }
        
        # Save default config
        self._save_config(default_config)
        
        return default_config
        
    def _load_secrets(self):
        """Load secrets from JSON file (more secure than env for some platforms)"""
        if os.path.exists(self.secrets_file):
            try:
                with open(self.secrets_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                log.error(f"Error loading secrets file: {e}")
        
        return {}
        
    def _save_config(self, config=None):
        """Save configuration to YAML file"""
        if config is None:
            config = self.config
            
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            return True
        except Exception as e:
            log.error(f"Error saving config file: {e}")
            return False
            
    def _save_secrets(self, secrets=None):
        """Save secrets to JSON file"""
        if secrets is None:
            secrets = self.secrets
            
        try:
            with open(self.secrets_file, 'w') as f:
                json.dump(secrets, f, indent=2)
            return True
        except Exception as e:
            log.error(f"Error saving secrets file: {e}")
            return False
            
    def _update_env_file(self, key, value):
        """Update a value in the .env file"""
        try:
            dotenv_file = find_dotenv()
            if not dotenv_file:
                # Create .env file if it doesn't exist
                with open(".env", "w") as f:
                    f.write(f"{key}={value}\n")
                dotenv_file = find_dotenv()
                
            set_key(dotenv_file, key, value)
            os.environ[key] = value
            self.env_vars[key] = value
            return True
        except Exception as e:
            log.error(f"Error updating .env file: {e}")
            return False
            
    def get_api_key(self, api_name):
        """Get API key for a specific service, with fallbacks"""
        if api_name not in self.default_apis:
            return None
            
        api_config = self.default_apis[api_name]
        env_var = api_config.get("api_key_env")
        
        # Check environment first
        if env_var in self.env_vars:
            return self.env_vars[env_var]
            
        # Then check secrets
        if api_name in self.secrets and "api_key" in self.secrets[api_name]:
            return self.secrets[api_name]["api_key"]
            
        # Prompt if not found
        if self.config.get("api_settings", {}).get(api_name, {}).get("prompt_for_missing", True):
            log.warning(f"{api_name} API key not found. Please enter it now.")
            return None
            
        return None
        
    def set_api_key(self, api_name, api_key, save_method="env"):
        """Set API key for a specific service"""
        if api_name not in self.default_apis:
            return False
            
        api_config = self.default_apis[api_name]
        env_var = api_config.get("api_key_env")
        
        if save_method == "env":
            # Save to .env file
            return self._update_env_file(env_var, api_key)
        elif save_method == "secrets":
            # Save to secrets file
            if api_name not in self.secrets:
                self.secrets[api_name] = {}
            self.secrets[api_name]["api_key"] = api_key
            return self._save_secrets()
        else:
            log.error(f"Invalid save method: {save_method}")
            return False
            
    def get_api_setting(self, api_name, setting, default=None):
        """Get a specific setting for an API"""
        return self.config.get("api_settings", {}).get(api_name, {}).get(setting, default)
        
    def set_api_setting(self, api_name, setting, value):
        """Set a specific setting for an API"""
        if "api_settings" not in self.config:
            self.config["api_settings"] = {}
            
        if api_name not in self.config["api_settings"]:
            self.config["api_settings"][api_name] = {}
            
        self.config["api_settings"][api_name][setting] = value
        return self._save_config()
        
    def get_app_setting(self, section, setting, default=None):
        """Get a general application setting"""
        return self.config.get(section, {}).get(setting, default)
        
    def set_app_setting(self, section, setting, value):
        """Set a general application setting"""
        if section not in self.config:
            self.config[section] = {}
            
        self.config[section][setting] = value
        return self._save_config()
        
    def prompt_for_api_keys(self, api_names=None):
        """Prompt for missing API keys"""
        if api_names is None:
            api_names = list(self.default_apis.keys())
            
        results = {}
        
        for api_name in api_names:
            if api_name not in self.default_apis:
                continue
                
            api_config = self.default_apis[api_name]
            env_var = api_config.get("api_key_env")
            
            # Check if API key already exists
            existing_key = self.get_api_key(api_name)
            if existing_key:
                display_key = f"{existing_key[:4]}...{existing_key[-4:]}" if len(existing_key) > 8 else "****"
                print(f"{api_name} API Key: {display_key} (already configured)")
                results[api_name] = True
                continue
                
            # Prompt for API key
            print(f"\nEnter your {api_name} API key (leave empty to skip):")
            api_key = getpass.getpass(f"{api_name} API Key: ")
            
            if not api_key:
                results[api_name] = False
                continue
                
            # Choose save method
            save_method = "env"
            print(f"Save {api_name} API key to:")
            print("1. Environment file (.env) - Good for development")
            print("2. Secrets file (secrets.json) - More secure for some setups")
            choice = input("Choice (1/2, default 1): ")
            
            if choice == "2":
                save_method = "secrets"
                
            # Save API key
            success = self.set_api_key(api_name, api_key, save_method)
            results[api_name] = success
            
            if success:
                print(f"{api_name} API key saved successfully.")
            else:
                print(f"Failed to save {api_name} API key.")
                
        return results
        
    def check_api_keys(self):
        """Check which API keys are configured"""
        results = {}
        
        for api_name in self.default_apis:
            api_key = self.get_api_key(api_name)
            results[api_name] = bool(api_key)
            
        return results
        
    def export_config(self, export_file=None):
        """Export configuration (for backup or transfer)"""
        if export_file is None:
            export_file = f"{self.app_name.lower()}_config_export.zip"
            
        try:
            # Create a temporary directory
            import tempfile
            import zipfile
            
            temp_dir = tempfile.mkdtemp()
            
            # Copy config and secrets files
            if os.path.exists(self.config_file):
                shutil.copy(self.config_file, os.path.join(temp_dir, "config.yaml"))
                
            # Export environment variables
            with open(os.path.join(temp_dir, "env_export.json"), 'w') as f:
                json.dump(self.env_vars, f, indent=2)
                
            # Create zip file
            with zipfile.ZipFile(export_file, 'w') as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        zipf.write(
                            os.path.join(root, file),
                            os.path.relpath(os.path.join(root, file), temp_dir)
                        )
                        
            # Clean up
            shutil.rmtree(temp_dir)
            
            return {
                "success": True,
                "file": export_file
            }
        except Exception as e:
            log.error(f"Error exporting configuration: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    def import_config(self, import_file, overwrite=False):
        """Import configuration from export file"""
        try:
            # Extract to temporary directory
            import tempfile
            import zipfile
            
            temp_dir = tempfile.mkdtemp()
            
            with zipfile.ZipFile(import_file, 'r') as zipf:
                zipf.extractall(temp_dir)
                
            # Import config
            config_path = os.path.join(temp_dir, "config.yaml")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    imported_config = yaml.safe_load(f)
                    
                if overwrite:
                    self.config = imported_config
                else:
                    # Merge configurations
                    self._merge_dict(self.config, imported_config)
                    
                self._save_config()
                
            # Import environment variables
            env_path = os.path.join(temp_dir, "env_export.json")
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    imported_env = json.load(f)
                    
                for key, value in imported_env.items():
                    if overwrite or key not in self.env_vars:
                        self._update_env_file(key, value)
                        
            # Clean up
            shutil.rmtree(temp_dir)
            
            return {
                "success": True,
                "message": "Configuration imported successfully"
            }
        except Exception as e:
            log.error(f"Error importing configuration: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    def _merge_dict(self, target, source):
        """Recursively merge source dict into target dict"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_dict(target[key], value)
            else:
                target[key] = value
                
    def get_model_info(self, model_id=None):
        """Get information about available Claude models"""
        models = {
            "claude-3-7-sonnet-20250219": {
                "name": "Claude 3.7 Sonnet",
                "description": "Latest Claude model with enhanced reasoning",
                "context_window": 200000,
                "tokens_per_minute": 15000
            },
            "claude-3-opus-20240229": {
                "name": "Claude 3 Opus",
                "description": "Most capable Claude model for complex tasks",
                "context_window": 200000,
                "tokens_per_minute": 10000
            },
            "claude-3-sonnet-20240229": {
                "name": "Claude 3 Sonnet",
                "description": "Balanced Claude model for general tasks",
                "context_window": 180000,
                "tokens_per_minute": 20000
            },
            "claude-3-haiku-20240307": {
                "name": "Claude 3 Haiku",
                "description": "Fast, efficient Claude model",
                "context_window": 150000,
                "tokens_per_minute": 40000
            }
        }
        
        if model_id:
            return models.get(model_id, {})
        
        return models
        
    def get_current_model(self):
        """Get the current Claude model ID"""
        env_var = self.default_apis["anthropic"]["model_env"]
        default_model = self.default_apis["anthropic"]["default_model"]
        
        return os.environ.get(env_var, default_model)
        
    def set_current_model(self, model_id):
        """Set the current Claude model ID"""
        env_var = self.default_apis["anthropic"]["model_env"]
        return self._update_env_file(env_var, model_id)

# Initialize global config manager
config_manager = ConfigManager()

if __name__ == "__main__":
    # Test configuration manager
    print("\nOrganiX Configuration Manager\n")
    print(f"Config directory: {config_manager.config_dir}")
    
    # Check API keys
    api_status = config_manager.check_api_keys()
    print("\nAPI Status:")
    for api, status in api_status.items():
        print(f"- {api}: {'Configured' if status else 'Not configured'}")
        
    # Prompt to configure missing APIs
    missing_apis = [api for api, status in api_status.items() if not status]
    
    if missing_apis:
        print(f"\nYou have {len(missing_apis)} unconfigured APIs:")
        for api in missing_apis:
            print(f"- {api}")
            
        configure = input("\nWould you like to configure these now? (y/n): ")
        if configure.lower() == 'y':
            config_manager.prompt_for_api_keys(missing_apis)
    
    print("\nCurrent Claude model:", config_manager.get_current_model())
    
    # Display all models
    print("\nAvailable Claude models:")
    for model_id, info in config_manager.get_model_info().items():
        print(f"- {info['name']} ({model_id})")
        print(f"  {info['description']}")
        print(f"  Context: {info['context_window']} tokens, Speed: {info['tokens_per_minute']} tokens/min")
        print()
