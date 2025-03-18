"""
Brave Integration - Integration with Brave Search API and browser automation
"""
import os
import json
import asyncio
import aiohttp
import time
from datetime import datetime
from dotenv import load_dotenv
from utils import log

# Load environment variables
load_dotenv()

class BraveClient:
    def __init__(self):
        """Initialize Brave client with API keys and configuration"""
        self.api_key = os.getenv("BRAVE_API_KEY")
        self.base_url = "https://api.search.brave.com/res/v1"
        
        # Check if API key is set
        self.api_configured = bool(self.api_key)
        
        if not self.api_configured:
            log.warning("Brave API key not found in environment variables.")
            log.info("Set BRAVE_API_KEY in .env file to enable Brave search integration.")
            
        # Cache to store search results
        self.search_cache = {}
        self.cache_expiry = 3600  # 1 hour cache
        
    async def search(self, query, count=10, country="US", search_type="web"):
        """Search using Brave Search API"""
        if not self.api_configured:
            return {
                "success": False,
                "message": "Brave API key not configured"
            }
            
        # Check cache first
        cache_key = f"{query}_{count}_{country}_{search_type}"
        current_time = time.time()
        
        if cache_key in self.search_cache:
            cached_result, timestamp = self.search_cache[cache_key]
            if current_time - timestamp < self.cache_expiry:
                # Cache still valid
                return cached_result
        
        try:
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.api_key
            }
            
            params = {
                "q": query,
                "count": count,
                "country": country,
                "search_type": search_type
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/search",
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Format the response
                        formatted_result = {
                            "success": True,
                            "query": query,
                            "web": result.get("web", {}).get("results", []),
                            "news": result.get("news", {}).get("results", []),
                            "videos": result.get("videos", {}).get("results", [])
                        }
                        
                        # Add to cache
                        self.search_cache[cache_key] = (formatted_result, current_time)
                        
                        return formatted_result
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "message": f"API request failed with status {response.status}: {error_text}"
                        }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error searching with Brave: {str(e)}"
            }
            
    async def private_search(self, query, count=10):
        """Perform a search with enhanced privacy features"""
        if not self.api_configured:
            return {
                "success": False,
                "message": "Brave API key not configured"
            }
            
        try:
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.api_key,
                "X-Privacy-Level": "high"  # Request enhanced privacy
            }
            
            params = {
                "q": query,
                "count": count,
                "goggles_id": "https://github.com/brave/goggles-quickstart/blob/main/goggles/nojs.goggle",  # No JavaScript results
                "no_tracking": "true"  # Disable tracking
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/search",
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Format the response
                        return {
                            "success": True,
                            "query": query,
                            "web": result.get("web", {}).get("results", [])
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "message": f"API request failed with status {response.status}: {error_text}"
                        }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error during private search: {str(e)}"
            }
            
    async def suggest(self, query):
        """Get search suggestions from Brave"""
        if not self.api_configured:
            return {
                "success": False,
                "message": "Brave API key not configured"
            }
            
        try:
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.api_key
            }
            
            params = {
                "q": query
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/suggest",
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        return {
                            "success": True,
                            "query": query,
                            "suggestions": result.get("results", [])
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "message": f"API request failed with status {response.status}: {error_text}"
                        }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting suggestions: {str(e)}"
            }
            
    async def spell_check(self, query):
        """Check spelling of a query using Brave API"""
        if not self.api_configured:
            return {
                "success": False,
                "message": "Brave API key not configured"
            }
            
        try:
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.api_key
            }
            
            params = {
                "q": query
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/spellcheck",
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        return {
                            "success": True,
                            "query": query,
                            "corrected": result.get("corrected", query),
                            "corrections": result.get("corrections", [])
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "message": f"API request failed with status {response.status}: {error_text}"
                        }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error checking spelling: {str(e)}"
            }

# Initialize global client
brave_client = BraveClient()

class BrowserAutomation:
    """Browser automation capabilities using Playwright"""
    def __init__(self):
        self.playwright_available = False
        self.browser = None
        self.page = None
        
        # Try to import playwright
        try:
            import playwright
            self.playwright_available = True
        except ImportError:
            log.warning("Playwright not installed. Browser automation features will be disabled.")
            log.info("Install with: pip install playwright && playwright install")
    
    async def setup(self):
        """Set up the browser automation"""
        if not self.playwright_available:
            return False
            
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox']
            )
            self.page = await self.browser.new_page()
            return True
        except Exception as e:
            log.error(f"Error setting up browser automation: {str(e)}")
            return False
            
    async def navigate(self, url):
        """Navigate to a URL"""
        if not self.playwright_available or not self.page:
            if not await self.setup():
                return {
                    "success": False,
                    "message": "Browser automation not available"
                }
                
        try:
            await self.page.goto(url)
            return {
                "success": True,
                "url": url,
                "title": await self.page.title()
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error navigating to {url}: {str(e)}"
            }
            
    async def screenshot(self, selector=None):
        """Take a screenshot of the current page or element"""
        if not self.playwright_available or not self.page:
            if not await self.setup():
                return {
                    "success": False,
                    "message": "Browser automation not available"
                }
                
        try:
            if selector:
                element = await self.page.query_selector(selector)
                if not element:
                    return {
                        "success": False,
                        "message": f"Element not found: {selector}"
                    }
                screenshot = await element.screenshot()
            else:
                screenshot = await self.page.screenshot()
                
            # Save screenshot to temporary file
            filename = f"screenshot_{int(time.time())}.png"
            with open(filename, "wb") as f:
                f.write(screenshot)
                
            return {
                "success": True,
                "filename": filename,
                "size": len(screenshot)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error taking screenshot: {str(e)}"
            }
            
    async def fill_form(self, form_data, submit=False, form_selector=None):
        """Fill a form with data"""
        if not self.playwright_available or not self.page:
            if not await self.setup():
                return {
                    "success": False,
                    "message": "Browser automation not available"
                }
                
        try:
            # Fill each form field
            for selector, value in form_data.items():
                await self.page.fill(selector, value)
                
            # Submit the form if requested
            if submit:
                if form_selector:
                    await self.page.query_selector(form_selector).press("Enter")
                else:
                    # Try to find a submit button
                    submit_button = await self.page.query_selector("input[type=submit], button[type=submit]")
                    if submit_button:
                        await submit_button.click()
                    else:
                        # Press Enter on the last field
                        last_selector = list(form_data.keys())[-1]
                        await self.page.press(last_selector, "Enter")
                
            return {
                "success": True,
                "message": "Form filled successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error filling form: {str(e)}"
            }
            
    async def click(self, selector):
        """Click an element on the page"""
        if not self.playwright_available or not self.page:
            if not await self.setup():
                return {
                    "success": False,
                    "message": "Browser automation not available"
                }
                
        try:
            await self.page.click(selector)
            return {
                "success": True,
                "message": f"Clicked element: {selector}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error clicking element: {str(e)}"
            }
            
    async def extract_text(self, selector=None):
        """Extract text from the page or specific element"""
        if not self.playwright_available or not self.page:
            if not await self.setup():
                return {
                    "success": False,
                    "message": "Browser automation not available"
                }
                
        try:
            if selector:
                element = await self.page.query_selector(selector)
                if not element:
                    return {
                        "success": False,
                        "message": f"Element not found: {selector}"
                    }
                text = await element.text_content()
            else:
                text = await self.page.content()
                
            return {
                "success": True,
                "text": text
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error extracting text: {str(e)}"
            }
            
    async def close(self):
        """Close the browser"""
        if self.browser:
            await self.browser.close()
            await self.playwright.stop()
            self.browser = None
            self.page = None

# Initialize global browser automation
browser = BrowserAutomation()

async def test_brave_search():
    """Test Brave search functionality"""
    print("Testing Brave search...")
    
    result = await brave_client.search("zero knowledge proofs", count=5)
    
    if result.get("success"):
        web_results = result.get("web", [])
        print(f"Found {len(web_results)} web results")
        
        for i, result in enumerate(web_results[:3]):
            print(f"{i+1}. {result.get('title')}")
            print(f"   {result.get('url')}")
            print(f"   {result.get('description', '')[:100]}...")
            print()
    else:
        print(f"Search failed: {result.get('message')}")
        
    return result

if __name__ == "__main__":
    # Test search when run directly
    asyncio.run(test_brave_search())
