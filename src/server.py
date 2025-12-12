"""
Lightweight aiohttp server for aggregating room temperature and humidity.
"""
import asyncio
import json
import os
from datetime import datetime, timedelta
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
                temp_val = data.get('temperature', '?')
                hum_val = data.get('humidity', '?')
                
                # Try to cast to float for history, keep string if fails
                try:
                    raw_temp = float(temp_val)
                except (ValueError, TypeError):
                    raw_temp = None
                    
                try:
                    raw_hum = float(hum_val)
                except (ValueError, TypeError):
                    raw_hum = None

                return {
                    "name": room['name'],
                    "temp": f"{temp_val}°C",
                    "humidity": f"{hum_val}%",
                    "raw_temp": raw_temp,
                    "raw_humidity": raw_hum,
                    "status": "online"
                }
            return {"name": room['name'], "status": "offline", "error": f"Status {response.status}"}
    except Exception as e:
        return {"name": room['name'], "status": "offline", "error": str(e)}

async def poll_data(app):
    """Background task to poll data every 5 minutes."""
    while True:
        try:
            config = app['config']
            async with aiohttp.ClientSession() as session:
                tasks = [fetch_room_data(session, room) for room in config['rooms']]
                results = await asyncio.gather(*tasks)
            
            now = datetime.now()
            for res in results:
                r_name = res['name']
                if r_name not in app['history']:
                    app['history'][r_name] = []
                
                # Store data
                app['history'][r_name].append({
                    'timestamp': now,
                    'data': res
                })
                
                # Prune old data (older than 4 hours)
                cutoff = now - timedelta(hours=4)
                app['history'][r_name] = [
                    entry for entry in app['history'][r_name] 
                    if entry['timestamp'] > cutoff
                ]
                
        except asyncio.CancelledError:
            raise
        except Exception as e:
            print(f"Error in background polling: {e}")
            
        await asyncio.sleep(300) # 5 minutes

async def start_background_tasks(app):
    """Start background tasks."""
    app['poll_task'] = asyncio.create_task(poll_data(app))

async def cleanup_background_tasks(app):
    """Cleanup background tasks."""
    app['poll_task'].cancel()
    try:
        await app['poll_task']
    except asyncio.CancelledError:
        pass

async def handle_index(request):
    """Handle the main page request by aggregating data."""
    app = request.app
    config = app['config']
    
    rooms_data = []
    for room in config['rooms']:
        r_name = room['name']
        history = app['history'].get(r_name, [])
        if history:
            # Get the latest data point
            latest = history[-1]['data']
            rooms_data.append(latest)
        else:
            # No data yet
            rooms_data.append({
                "name": r_name, 
                "temp": "?", 
                "humidity": "?", 
                "status": "Waiting for data..."
            })
    
    return aiohttp_jinja2.render_template('index.html', request, {'rooms': rooms_data})

async def handle_history(request):
    """Return JSON history for a specific room."""
    room_name = request.match_info['room_name']
    app = request.app
    
    if room_name not in app['history']:
        return web.json_response({'error': 'Room not found or no history yet'}, status=404)
        
    # Format history for the frontend
    # We want a list of {timestamp: ISO8601, temp: float, humidity: float}
    history_data = []
    for entry in app['history'][room_name]:
        # Only include valid data points
        if entry['data'].get('status') == 'online' and entry['data'].get('raw_temp') is not None:
             history_data.append({
                 'timestamp': entry['timestamp'].isoformat(),
                 'temp': entry['data']['raw_temp'],
                 'humidity': entry['data'].get('raw_humidity')
             })
             
    return web.json_response({'room': room_name, 'history': history_data})


async def init_app():
    """Initialize the aiohttp application."""
    app = web.Application()
    
    # Load config
    app['config'] = load_config()
    app['history'] = {} # In-memory buffer for room data
    
    # Background tasks
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    
    # Setup Jinja2
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
    
    # Routes
    app.router.add_get('/', lambda r: web.HTTPFound('/roomstemphum'))
    app.router.add_get('/roomstemphum', handle_index)
    app.router.add_get('/roomstemphum/history/{room_name}', handle_history)
    
    # Static files
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    if os.path.exists(static_dir):
        app.router.add_static('/static/', static_dir, name='static')

    return app

if __name__ == '__main__': # pragma: no cover
    web.run_app(init_app(), host='0.0.0.0', port=8000)
