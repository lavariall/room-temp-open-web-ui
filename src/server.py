
"""
OpenWebUI Bridge Entrypoint
Exposes the Tools class as a FastMCP server.
"""

from fastmcp import FastMCP
from src.openwebui_bridge import Tools

# Initialize FastMCP Server
mcp = FastMCP("room-temp-bridge")

# Initialize our Tools wrapper
bridge_tools = Tools()

@mcp.tool()
async def get_room_climate(room_name: str) -> str:
    """
    Get the temperature and humidity for a specific room.

    Args:
        room_name: The name of the room (e.g., 'room_91', 'livingroom').
                   Available default keys: room_91, room_92, room_93, room_94, room_95.
    Returns:
        JSON string with temperature and humidity or error message.
    """
    return await bridge_tools.get_room_climate(room_name)

if __name__ == "__main__":
    # fastmcp run will handle the execution loop if invoked via CLI
    # but we will run it programmatically
    mcp.run()
