"""
Utility functions for the Claude Agent
"""
import os
import json
import time
import asyncio
import logging
from datetime import datetime
from rich.console import Console
from rich.logging import RichHandler

# Setup rich console for better terminal output
console = Console()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("claude-agent")


def setup_environment():
    """Setup environment variables and directories"""
    # Check for .env file
    if not os.path.exists(".env"):
        console.print("[bold yellow]Warning: .env file not found, creating template...[/]")
        with open(".env", "w") as f:
            f.write("""# Claude Agent Environment Variables
ANTHROPIC_API_KEY=your_anthropic_api_key_here
EXA_API_KEY=your_exa_api_key_here
# Add other API keys as needed
""")
        console.print("[green]Created .env template file. Please edit with your API keys.[/]")
    
    # Create necessary directories
    directories = [
        "memory_store",
        "logs",
        "data"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            console.print(f"[green]Created directory: {directory}[/]")
            
    # Setup logging directory with date
    log_dir = os.path.join("logs", datetime.now().strftime("%Y-%m-%d"))
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f"claude_agent_{datetime.now().strftime('%H-%M-%S')}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    log.addHandler(file_handler)
    
    return True


async def retry_async(func, *args, retries=3, delay=1, backoff=2, **kwargs):
    """Retry an async function with exponential backoff"""
    last_exception = None
    current_delay = delay
    
    for attempt in range(retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            log.warning(f"Attempt {attempt+1}/{retries} failed: {str(e)}")
            if attempt < retries - 1:
                log.info(f"Retrying in {current_delay} seconds...")
                await asyncio.sleep(current_delay)
                current_delay *= backoff
    
    log.error(f"All {retries} attempts failed. Last error: {last_exception}")
    raise last_exception


def save_json(data, filepath):
    """Save data as JSON file"""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        log.error(f"Error saving JSON file: {str(e)}")
        return False


def load_json(filepath):
    """Load data from JSON file"""
    try:
        if not os.path.exists(filepath):
            return None
            
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        log.error(f"Error loading JSON file: {str(e)}")
        return None


class Timer:
    """Simple timer class for performance measurement"""
    def __init__(self, name=None):
        self.name = name or "Timer"
        self.start_time = None
        self.lap_time = None
        
    def start(self):
        """Start the timer"""
        self.start_time = time.time()
        self.lap_time = self.start_time
        return self
        
    def lap(self, label=None):
        """Record a lap time"""
        now = time.time()
        duration = now - self.lap_time
        self.lap_time = now
        
        if label:
            log.info(f"{label}: {duration:.4f}s")
        
        return duration
        
    def stop(self):
        """Stop the timer and return total duration"""
        if self.start_time is None:
            return 0
            
        duration = time.time() - self.start_time
        log.info(f"{self.name} total time: {duration:.4f}s")
        return duration
