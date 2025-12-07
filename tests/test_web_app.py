
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
import pytest
from src.web_app import app

client = TestClient(app)

@pytest.fixture
def mock_tools():
    with patch('src.web_app.tools') as mock:
        mock.get_room_climate = AsyncMock()
        yield mock

def test_read_root_success(mock_tools):
    # Mock the tools.get_room_climate to return valid JSON-like strings
    mock_tools.get_room_climate.side_effect = [
        'Climate data for room_91: {"temperature": 22.5, "humidity": 45}',
        'Climate data for room_92: {"temperature": 21.0, "humidity": 40}',
        'Error: Room not found',
        'Error: Connection failed',
        'Climate data for room_95: {"temperature": 23.0, "humidity": 50}'
    ]

    response = client.get("/")
    assert response.status_code == 200
    assert "Climate Control" in response.text
    
    # Check if data is rendered
    assert "22.5°C" in response.text
    assert "21.0°C" in response.text
    
    # Check error handling rendering
    # We expect "N/A" or offline status for errors
    assert "N/A" in response.text 

def test_chat_endpoint_no_tool(mock_tools):
    # Mock ollama to return a plain response without tool calls
    with patch('src.web_app.ollama.chat') as mock_ollama:
        mock_ollama.return_value = {
            'message': {'content': 'The weather is fine outside.', 'tool_calls': None}
        }
        
        response = client.post("/chat", json={"message": "Hello"})
        assert response.status_code == 200
        assert response.json() == {"response": "The weather is fine outside."}

def test_chat_endpoint_with_tool(mock_tools):
    # Mock ollama to return a tool call first, then a final response
    with patch('src.web_app.ollama.chat') as mock_ollama:
        
        # Setup the sequence of returns for ollama.chat
        # 1st call: returns a tool call
        # 2nd call: returns the final answer using the tool result
        mock_ollama.side_effect = [
            {
                'message': {
                    'content': '',
                    'tool_calls': [{
                        'function': {
                            'name': 'get_room_climate',
                            'arguments': {'room_name': 'room_91'}
                        }
                    }]
                }
            },
            {
                'message': {'content': 'The temperature in room_91 is 22.5°C.'}
            }
        ]
        
        # Mock the tool execution itself
        mock_tools.get_room_climate.return_value = 'Climate data for room_91: {"temperature": 22.5, "humidity": 45}'
        
        response = client.post("/chat", json={"message": "What is the temp in room_91?"})
        assert response.status_code == 200
        # We assume the code invokes get_room_climate correctly
        mock_tools.get_room_climate.assert_called_with('room_91')
        assert response.json() == {"response": "The temperature in room_91 is 22.5°C."}

