
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from src.openwebui_bridge import Tools

@pytest.fixture
def mock_config():
    with patch('src.openwebui_bridge.Config') as MockConfig:
        config_instance = MockConfig.return_value
        # Setup servers
        server_mock = MagicMock()
        server_mock.name = "room_91"
        server_mock.url = "http://fake"
        server_mock.token = "token"
        
        config_instance.mcp_servers = [server_mock]
        yield config_instance

@pytest.mark.asyncio
async def test_get_room_climate_success(mock_config):
    with patch('src.openwebui_bridge.Client') as MockClient:
        mock_client_instance = AsyncMock()
        MockClient.return_value.__aenter__.return_value = mock_client_instance
        
        mock_result = MagicMock()
        mock_result.content = '{"temperature": 20, "humidity": 50}'
        mock_client_instance.call_tool.return_value = mock_result
        
        tools = Tools()
        result = await tools.get_room_climate("room_91")
        
        assert "Climate data for room_91" in result
        assert '{"temperature": 20, "humidity": 50}' in result

@pytest.mark.asyncio
async def test_get_room_climate_retry_fail(mock_config):
     with patch('src.openwebui_bridge.Client') as MockClient:
         mock_client_instance = AsyncMock()
         MockClient.return_value.__aenter__.return_value = mock_client_instance
         
         mock_client_instance.call_tool.side_effect = Exception("Connection Error")
         
         tools = Tools()
         with patch('asyncio.sleep', new_callable=AsyncMock):
             result = await tools.get_room_climate("room_91")
             
         assert "Error connecting to room_91" in result
         assert "Connection Error" in result

@pytest.mark.asyncio
async def test_get_room_climate_room_not_found(mock_config):
    tools = Tools()
    result = await tools.get_room_climate("non_existent_room")
    assert "Error: Room 'non_existent_room' not found" in result

@pytest.mark.asyncio
async def test_no_servers_loaded():
    with patch('src.openwebui_bridge.Config') as MockConfig:
        config_instance = MockConfig.return_value
        config_instance.mcp_servers = []
        
        tools = Tools()
        result = await tools.get_room_climate("room_91")
        assert "Error: No server configuration loaded" in result

def test_config_load_exception():
    with patch('src.openwebui_bridge.Config') as MockConfig:
        MockConfig.side_effect = Exception("Config Load Fail")
        
        # Tools constructor catches exception and sets servers = []
        tools = Tools()
        assert tools.servers == []
