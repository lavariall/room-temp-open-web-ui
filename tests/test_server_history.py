
import pytest
from datetime import datetime, timedelta
from aiohttp import web
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from server import init_app, handle_history, fetch_room_data

@pytest.mark.asyncio
async def test_history_endpoint_success(aiohttp_client):
    app = await init_app()
    # Mock some history data
    now = datetime(2023, 1, 1, 12, 0, 0)
    app['history']['TestRoom'] = [
        {'timestamp': now - timedelta(minutes=10), 'data': {'status': 'online', 'raw_temp': 22.5, 'raw_humidity': 45.0}},
        {'timestamp': now - timedelta(minutes=5), 'data': {'status': 'online', 'raw_temp': 23.0, 'raw_humidity': 46.0}},
        {'timestamp': now, 'data': {'status': 'offline', 'error': 'timeout'}},
        {'timestamp': now + timedelta(minutes=5), 'data': {'status': 'online', 'raw_temp': 23.5, 'raw_humidity': 47.0}},
    ]
    client = await aiohttp_client(app)
    
    resp = await client.get('/roomstemphum/history/TestRoom')
    assert resp.status == 200
    data = await resp.json()
    assert data['room'] == 'TestRoom'
    assert len(data['history']) == 3
    assert data['history'][0]['temp'] == 22.5

@pytest.mark.asyncio
async def test_history_endpoint_not_found(aiohttp_client):
    app = await init_app()
    client = await aiohttp_client(app)
    resp = await client.get('/roomstemphum/history/UnknownRoom')
    assert resp.status == 404

@pytest.mark.asyncio
async def test_fetch_room_data_parsing():
    pass
