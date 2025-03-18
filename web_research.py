"""
Web Research - Handles web search and information retrieval
"""
import os
import json
import aiohttp
import asyncio
from dotenv import load_dotenv
from memory_system import MemorySystem

# Load environment variables
load_dotenv()

class WebResearcher:
    def __init__(self, memory_system=None):
        self.exa_api_key = os.getenv("EXA_API_KEY")
        if not self.exa_api_key:
            print("Warning: EXA_API_KEY not found in environment variables")
            
        self.memory = memory_system or MemorySystem()
        
    async def search(self, query, num_results=5):
        """Search the web using Exa API"""
        if not self.exa_api_key:
            return {"error": "EXA_API_KEY not configured"}
            
        headers = {
            "x-api-key": self.exa_api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "numResults": num_results,
            "useAutoprompt": True,
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.exa.ai/search",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return {"error": f"API request failed with status {response.status}: {error_text}"}
                        
                    result = await response.json()
                    
                    # Store results in memory
                    search_content = json.dumps({
                        "query": query,
                        "results": [
                            {
                                "title": r.get("title", ""),
                                "url": r.get("url", ""),
                                "text": r.get("text", "")[:500] + "..." if r.get("text") else ""
                            }
                            for r in result.get("results", [])
                        ]
                    })
                    
                    self.memory.add_memory("semantic", search_content, {"type": "web_search", "query": query})
                    
                    return result
        except Exception as e:
            return {"error": f"Error during search: {str(e)}"}
            
    async def extract_content(self, url):
        """Extract content from a specific URL"""
        if not self.exa_api_key:
            return {"error": "EXA_API_KEY not configured"}
            
        headers = {
            "x-api-key": self.exa_api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "url": url,
            "extractLinks": True
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.exa.ai/extract",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return {"error": f"API request failed with status {response.status}: {error_text}"}
                        
                    result = await response.json()
                    
                    # Store extracted content in memory
                    extract_content = json.dumps({
                        "url": url,
                        "title": result.get("title", ""),
                        "text": result.get("text", "")[:1000] + "..." if len(result.get("text", "")) > 1000 else result.get("text", ""),
                        "links": result.get("links", [])[:10]
                    })
                    
                    self.memory.add_memory("semantic", extract_content, {"type": "web_extract", "url": url})
                    
                    return result
        except Exception as e:
            return {"error": f"Error during extraction: {str(e)}"}
            
    async def summarize_research(self, query, num_results=5):
        """Search and summarize research on a topic"""
        search_results = await self.search(query, num_results)
        
        if "error" in search_results:
            return search_results
            
        summaries = []
        for result in search_results.get("results", [])[:3]:  # Process top 3 results
            url = result.get("url")
            if url:
                content = await self.extract_content(url)
                if "error" not in content:
                    summaries.append({
                        "title": content.get("title", ""),
                        "url": url,
                        "summary": content.get("text", "")[:500] + "..." if len(content.get("text", "")) > 500 else content.get("text", "")
                    })
        
        return {
            "query": query,
            "summaries": summaries
        }
