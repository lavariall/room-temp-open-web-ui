"""
Tests for the server module.
"""
from unittest.mock import MagicMock, patch, AsyncMock
import pytest
from src.server import init_app, fetch_room_data

@pytest.mark.asyncio
async def test_index_route(aiohttp_client):
    """Test the main index route."""
    app = await init_app()
    client = await aiohttp_client(app)

    # Mock aggregation to avoid real network calls during test
    with patch('src.server.fetch_room_data', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = {"name": "Test Room", "temp": "25°C", "humidity": "50%", "status": "online"}

        resp = await client.get('/roomstemphum')
        assert resp.status == 200
        text = await resp.text()
        assert "Climate Control" in text

@pytest.mark.asyncio
async def test_fetch_room_data_success():
    """Test successful room data fetching."""
    room = {"name": "Test", "ip": "1.2.3.4", "token": "abc"}

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"temperature": "22.5", "humidity": "54"})

    # Context manager mock for session.get
    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response

    result = await fetch_room_data(mock_session, room)
    assert result['name'] == "Test"
    assert result['temp'] == "22.5°C"
    assert result['humidity'] == "54%"
    assert result['status'] == "online"

@pytest.mark.asyncio
async def test_fetch_room_data_failure():
    """Test room data fetching failure."""
    room = {"name": "Test", "ip": "1.2.3.4", "token": "abc"}

    mock_response = MagicMock()
    mock_response.status = 500

    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response

    result = await fetch_room_data(mock_session, room)
    assert result['status'] == "offline"
    assert "Status 500" in result['error']

@pytest.mark.asyncio
async def test_fetch_room_data_exception():
    """Test room data fetching exception handling."""
    room = {"name": "Test", "ip": "1.2.3.4", "token": "abc"}

    # Context manager mock that raises an exception
    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.side_effect = Exception("Connection error")

    result = await fetch_room_data(mock_session, room)
    assert result['status'] == "offline"
    assert "Connection error" in result['error']
