"""
Simple web server for the OrganiX dashboard
"""
import os
import json
import asyncio
import argparse
from aiohttp import web
from agent import ClaudeAgent
from utils import setup_environment, log

# Initialize agent (will be done when the server starts)
agent = None

async def index(request):
    """Serve the dashboard HTML"""
    return web.FileResponse('web_dashboard/index.html')

async def api_query(request):
    """Handle API query requests"""
    if agent is None:
        return web.json_response({
            "error": "Agent not initialized"
        }, status=500)
        
    try:
        data = await request.json()
        query = data.get('query')
        
        if not query:
            return web.json_response({
                "error": "No query provided"
            }, status=400)
            
        # Process the query
        response = await agent.process_query(query)
        
        return web.json_response({
            "response": response
        })
    except Exception as e:
        return web.json_response({
            "error": str(e)
        }, status=500)

async def api_system_info(request):
    """Get system information"""
    if agent is None:
        return web.json_response({
            "error": "Agent not initialized"
        }, status=500)
        
    try:
        system_info = agent.system.get_system_info()
        memory_stats = agent.get_memory_stats()
        
        return web.json_response({
            "system_info": system_info,
            "memory_stats": memory_stats
        })
    except Exception as e:
        return web.json_response({
            "error": str(e)
        }, status=500)
        
async def api_research(request):
    """Research a topic"""
    if agent is None:
        return web.json_response({
            "error": "Agent not initialized"
        }, status=500)
        
    try:
        data = await request.json()
        topic = data.get('topic')
        
        if not topic:
            return web.json_response({
                "error": "No topic provided"
            }, status=400)
            
        # Research the topic
        results = await agent.research_topic(topic)
        
        return web.json_response({
            "results": results
        })
    except Exception as e:
        return web.json_response({
            "error": str(e)
        }, status=500)

async def initialize_agent():
    """Initialize the agent"""
    global agent
    try:
        agent = ClaudeAgent()
        log.info("Agent initialized successfully")
        return True
    except Exception as e:
        log.error(f"Failed to initialize agent: {str(e)}")
        return False

async def start_server(host='localhost', port=8080):
    """Start the web server"""
    # Initialize the agent
    await initialize_agent()
    
    # Create the application
    app = web.Application()
    
    # Add routes
    app.router.add_get('/', index)
    app.router.add_post('/api/query', api_query)
    app.router.add_get('/api/system_info', api_system_info)
    app.router.add_post('/api/research', api_research)
    
    # Add static file serving (for dashboard assets)
    app.router.add_static('/static/', path='web_dashboard/static')
    
    # Start the server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    
    log.info(f"Starting web server at http://{host}:{port}")
    await site.start()
    
    return runner, site

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="OrganiX Web Dashboard")
    parser.add_argument("--host", default="localhost", help="Host to bind (default: localhost)")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind (default: 8080)")
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    # Start the server
    runner, site = await start_server(args.host, args.port)
    
    # Keep the server running
    try:
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour
    except KeyboardInterrupt:
        log.info("Shutting down server...")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
