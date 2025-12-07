
"""
OpenWebUI Tool Bridge for MCP Servers
Content of this file can be pasted into OpenWebUI Tools section,
or used as a module if properly configured.
"""

import asyncio
import os
import sys
from typing import Optional  # pylint: disable=unused-import

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

# Ensure we can import from utils if running as a script or module in project
# If pasted into OpenWebUI, 'utils' needs to be available or this logic adjusted.
# We assume this file is in 'src/' and 'utils/' is in project root.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from utils.config import Config  # pylint: disable=wrong-import-position

class Tools:
    """
    Bridge class for OpenWebUI to interact with MCP servers.
    """
    # pylint: disable=too-few-public-methods
    def __init__(self):
        try:
            self.config_manager = Config()
            self.servers = self.config_manager.mcp_servers
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.servers = []
            print(f"Configuration could not be loaded: {e}")

    async def get_room_climate(self, room_name: str) -> str:
        """
        Get the temperature and humidity for a specific room.

        :param room_name: The name of the room (e.g., 'room_91', 'livingroom').
                        Currently mapped to names in config.json.
                        Available default keys: room_91, room_92, room_93, room_94, room_95.
        :return: JSON string with temperature and humidity or error message.
        """
        if not self.servers:
            return "Error: No server configuration loaded."

        # Find the server url for the given room_name
        target_server = next((s for s in self.servers if s.name == room_name), None)

        if not target_server:
            available = [s.name for s in self.servers]
            return f"Error: Room '{room_name}' not found. Available rooms: {', '.join(available)}"

        url = target_server.url
        token = target_server.token

        attempts = 3
        timeout_seconds = 5
        last_error = None

        for attempt in range(attempts):
            try:
                # Using fastmcp client to call the tool 'get_temperature_and_humidity'
                transport = StreamableHttpTransport(
                    url=url,
                    headers={
                        "Authorization": f"Bearer {token}"
                    }
                )

                async with Client(transport=transport) as client:
                    # Enforce timeout on the tool call
                    result = await asyncio.wait_for(
                        client.call_tool("get_temperature_and_humidity"),
                        timeout=timeout_seconds
                    )
                    return f"Climate data for {room_name}: {result.content}"

            except Exception as e:  # pylint: disable=broad-exception-caught
                last_error = e
                # Don't wait after the last attempt
                if attempt < attempts - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s...
                    print(
                        f"Attempt {attempt + 1}/{attempts} failed for {room_name}: {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)

        return (
            f"Error connecting to {room_name} ({url}) after {attempts} attempts: {str(last_error)}"
        )

# For testing functionality without OpenWebUI
if __name__ == "__main__":
    async def main():
        """Test the Tools class functionality."""
        tools = Tools()
        if tools.servers:
            print(f"Loaded servers: {[s.name for s in tools.servers]}")
            # Test call
            res = await tools.get_room_climate("room_91")
            print(res)
        else:
            print("No servers loaded.")

    asyncio.run(main())
