"""
Lightweight aiohttp server for aggregating room temperature and humidity.
"""
import asyncio
import json
import os
import aiohttp
import aiohttp_jinja2
import jinja2
from aiohttp import web

# Configuration
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'utils', 'config.json')
STATIC_PATH = os.path.join(os.path.dirname(__file__), 'templates')

def load_config():
    """Load configuration from JSON file."""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

async def fetch_room_data(session, room):
    """Fetch temperature and humidity from a single room."""
    url = f"http://{room['ip']}/temphum" # User specified path
    headers = {"Authorization": f"Bearer {room['token']}"}
    try:
        async with session.get(url, headers=headers, timeout=5) as response:
            if response.status == 200:
                data = await response.json()
                # Expected: {"temperature": "22.5", "humidity": "54"}
                return {
                    "name": room['name'],
                    "temp": f"{data.get('temperature', '?')}°C",
                    "humidity": f"{data.get('humidity', '?')}%",
                    "status": "online"
                }
            return {"name": room['name'], "status": "offline", "error": f"Status {response.status}"}
    except Exception as e:
        return {"name": room['name'], "status": "offline", "error": str(e)}

async def handle_index(request):
    """Handle the main page request by aggregating data."""
    config = request.app['config']
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_room_data(session, room) for room in config['rooms']]
        rooms_data = await asyncio.gather(*tasks)
    
    return aiohttp_jinja2.render_template('index.html', request, {'rooms': rooms_data})

async def init_app():
    """Initialize the aiohttp application."""
    app = web.Application()
    
    # Load config
    app['config'] = load_config()
    
    # Setup Jinja2
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
    
    # Routes
    app.router.add_get('/', lambda r: web.HTTPFound('/roomstemphum'))
    app.router.add_get('/roomstemphum', handle_index)
    
    # Static files
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    if os.path.exists(static_dir):
        app.router.add_static('/static/', static_dir, name='static')

    return app

if __name__ == '__main__':
    web.run_app(init_app(), host='0.0.0.0', port=8000)
