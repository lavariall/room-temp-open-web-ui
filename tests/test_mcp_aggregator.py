
import pytest
import json
from unittest.mock import patch, mock_open
from src.mcp_aggregator import MCPAggregator

def test_load_config_success():
    """Test loading a valid configuration file."""
    mock_config = {
        "mcp_servers": [
            {"name": "test_server", "url": "http://localhost:8080/mcp"}
        ]
    }
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_config))):
        aggregator = MCPAggregator("dummy_config.json")
        assert len(aggregator.servers) == 1
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
