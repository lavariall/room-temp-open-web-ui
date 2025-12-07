
import pytest
import json
from unittest.mock import patch, mock_open, AsyncMock, MagicMock
from src.mcp_aggregator import MCPAggregator

# Mock data for config
MOCK_CONFIG = {
    "mcp_servers": [
        {"name": "test_server", "url": "http://localhost:8080/mcp"},
        {"name": "no_url_server", "url": ""}
    ]
}

def test_load_config_success():
    """Test loading a valid configuration file."""
    with patch("builtins.open", mock_open(read_data=json.dumps(MOCK_CONFIG))):
        aggregator = MCPAggregator("dummy_config.json")
        assert len(aggregator.servers) == 2
        assert aggregator.servers[0]["name"] == "test_server"
        assert aggregator.servers[0]["url"] == "http://localhost:8080/mcp"

def test_load_config_file_not_found():
    """Test behavior when config file is missing."""
    with patch("builtins.open", side_effect=FileNotFoundError):
        aggregator = MCPAggregator("non_existent.json")
        assert aggregator.servers == []

def test_load_config_invalid_json():
    """Test behavior when config file contains invalid JSON."""
    with patch("builtins.open", mock_open(read_data="{invalid_json")):
        aggregator = MCPAggregator("bad_config.json")
        assert aggregator.servers == []

@pytest.mark.asyncio
async def test_list_all_tools_success():
    with patch("builtins.open", mock_open(read_data=json.dumps(MOCK_CONFIG))):
        aggregator = MCPAggregator("dummy_config.json")
        
        with patch('src.mcp_aggregator.Client') as MockClient:
            mock_client_instance = AsyncMock()
            MockClient.return_value.__aenter__.return_value = mock_client_instance
            
            # mock list_tools
            mock_tools_response = [{"name": "tool1", "description": "desc"}]
            mock_client_instance.list_tools.return_value = mock_tools_response
            
            tools = await aggregator.list_all_tools()
            
            assert "test_server" in tools
            assert tools["test_server"] == mock_tools_response
            # The server with empty url should be skipped or result in no tools
            # In code: if not url: continue
            assert "no_url_server" not in tools

@pytest.mark.asyncio
async def test_list_all_tools_failure():
    with patch("builtins.open", mock_open(read_data=json.dumps(MOCK_CONFIG))):
        aggregator = MCPAggregator("dummy_config.json")
        
        with patch('src.mcp_aggregator.Client') as MockClient:
            mock_client_instance = AsyncMock()
            MockClient.return_value.__aenter__.return_value = mock_client_instance
            
            # mock failure
            mock_client_instance.list_tools.side_effect = Exception("Network Error")
            
            tools = await aggregator.list_all_tools()
            
            # Should be empty list for that server on error
            assert tools["test_server"] == []

@pytest.mark.asyncio
async def test_call_tool_on_server_success():
    with patch("builtins.open", mock_open(read_data=json.dumps(MOCK_CONFIG))):
        aggregator = MCPAggregator("dummy_config.json")
        
        with patch('src.mcp_aggregator.Client') as MockClient:
            mock_client_instance = AsyncMock()
            MockClient.return_value.__aenter__.return_value = mock_client_instance
            
            mock_result = "Tool Result"
            mock_client_instance.call_tool.return_value = mock_result
            
            result = await aggregator.call_tool_on_server("test_server", "tool1", {})
            assert result == mock_result

@pytest.mark.asyncio
async def test_call_tool_on_server_failure():
    with patch("builtins.open", mock_open(read_data=json.dumps(MOCK_CONFIG))):
        aggregator = MCPAggregator("dummy_config.json")
        
        with patch('src.mcp_aggregator.Client') as MockClient:
            mock_client_instance = AsyncMock()
            MockClient.return_value.__aenter__.return_value = mock_client_instance
            
            mock_client_instance.call_tool.side_effect = Exception("Tool Failure")
            
            with pytest.raises(Exception):
                await aggregator.call_tool_on_server("test_server", "tool1", {})

@pytest.mark.asyncio
async def test_call_tool_server_not_found():
    with patch("builtins.open", mock_open(read_data=json.dumps(MOCK_CONFIG))):
        aggregator = MCPAggregator("dummy_config.json")
        
        with pytest.raises(ValueError) as excinfo:
            await aggregator.call_tool_on_server("unknown_server", "tool1")
        
        assert "Server 'unknown_server' not found" in str(excinfo.value)
