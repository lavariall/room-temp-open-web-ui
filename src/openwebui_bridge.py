
"""
OpenWebUI Tool Bridge for MCP Servers
Content of this file can be pasted into OpenWebUI Tools section,
or used as a module if properly configured.
"""

import json
import asyncio
import os
from typing import Dict, Any, Optional

try:
    from fastmcp import Client
    from fastmcp.client.transports import StreamableHttpTransport
except ImportError:
    # Fallback or error if fastmcp is not installed in the OpenWebUI environment
    print("fastmcp not installed")
    Client = None
    StreamableHttpTransport = None

class Tools:
    def __init__(self):
        # Path to config.json - adjust if necessary relative to where OpenWebUI runs
        # In Docker, we usually mount the project to /app
        self.config_path = os.getenv("MCP_CONFIG_PATH", "/app/config.json")
        self.servers = self._load_config()

    def _load_config(self) -> list:
        try:
            if not os.path.exists(self.config_path):
                # Try local relative path for testing
                local_path = "config.json"
                if os.path.exists(local_path):
                    self.config_path = local_path
                else:
                    return []
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("mcp_servers", [])
        except Exception as e:
            print(f"Error loading config: {e}")
            return []

    async def get_room_climate(self, room_name: str) -> str:
        """
        Get the temperature and humidity for a specific room.
        
        :param room_name: The name of the room (e.g., 'room_91', 'livingroom').
                        Currently mapped to names in config.json.
                        Available default keys: room_91, room_92, room_93, room_94, room_95.
        :return: JSON string with temperature and humidity or error message.
        """
        if not Client:
            return "Error: fastmcp library not installed."

        # Find the server url for the given room_name
        # Simple matching: checks if room_name is in the config name
        target_server = next((s for s in self.servers if s["name"] == room_name), None)
        
        # If not found, try fuzzy match or fallback (logic can be improved)
        if not target_server:
            # Fallback for "bathroom" -> "room_91" mapping logic if user hasn't updated config yet
            # For now, just return error to encourage correct usage
            available = [s["name"] for s in self.servers]
            return f"Error: Room '{room_name}' not found. Available rooms: {', '.join(available)}"

        url = target_server["url"]
        
        try:
            # Using fastmcp client to call the tool 'get_temperature_and_humidity'
            # We assume the MCP server provides this tool as per description
            transport = StreamableHttpTransport(url=url)
            async with Client(transport=transport) as client:
                result = await client.call_tool("get_temperature_and_humidity")
                # result.content should be the list of content blocks
                # We format it nicely
                return f"Climate data for {room_name}: {result.content}"
        except Exception as e:
            return f"Error connecting to {room_name} ({url}): {str(e)}"

# For testing functionality without OpenWebUI
if __name__ == "__main__":
    async def main():
        tools = Tools()
        print(f"Loaded servers: {[s['name'] for s in tools.servers]}")
        # Test call - assumes server is running, otherwise will error roughly
        res = await tools.get_room_climate("room_91")
        print(res)

    asyncio.run(main())
