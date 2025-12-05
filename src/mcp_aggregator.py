
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPAggregator:
    """
    Aggregates tools from multiple FastMCP servers defined in a configuration file.
    This class manages connections to multiple MCP servers and provides
    methods to list and execute tools across them.
    """

    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the aggregator with a path to the config file.

        Args:
            config_path (str): Path to the JSON configuration file containing server URLs.
        """
        self.config_path = config_path
        self.servers: List[Dict[str, str]] = self._load_config()

    def _load_config(self) -> List[Dict[str, str]]:
        """
        Load server configurations from the JSON file.

        Returns:
            List[Dict[str, str]]: A list of server configurations (name, url).
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                headers = data.get("mcp_servers", [])
                logger.info(f"Loaded {len(headers)} servers from config.")
                return headers
        except FileNotFoundError:
            logger.error(f"Config file not found at {self.config_path}")
            return []
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {self.config_path}")
            return []

    async def list_all_tools(self) -> Dict[str, List[Any]]:
        """
        Connects to all configured servers and lists available tools.

        Returns:
            Dict[str, List[Any]]: A dictionary mapping server names to their list of tools.
        """
        all_tools = {}
        for server in self.servers:
            name = server.get("name", "unknown")
            url = server.get("url")
            if not url:
                continue
            
            # Note: In a real app, we might want to cache clients or keep connections open
            # But FastMCP client is often used as a context manager
            try:
                transport = StreamableHttpTransport(url=url)
                async with Client(transport=transport) as client:
                    tools = await client.list_tools()
                    all_tools[name] = tools
                    logger.info(f"Retrieved {len(tools)} tools from {name}")
            except Exception as e:
                logger.error(f"Failed to list tools from {name} ({url}): {e}")
                all_tools[name] = []
        
        return all_tools

    async def call_tool_on_server(self, server_name: str, tool_name: str, arguments: Dict[str, Any] = None) -> Any:
        """
        Calls a specific tool on a specific server.

        Args:
            server_name (str): The name of the server to call.
            tool_name (str): The name of the tool to execute.
            arguments (Dict[str, Any], optional): Arguments for the tool. Defaults to None.

        Returns:
            Any: The result of the tool execution.
        """
        target_server = next((s for s in self.servers if s["name"] == server_name), None)
        if not target_server:
            raise ValueError(f"Server '{server_name}' not found in configuration.")

        url = target_server["url"]
        try:
            transport = StreamableHttpTransport(url=url)
            async with Client(transport=transport) as client:
                result = await client.call_tool(tool_name, arguments=arguments)
                return result
        except Exception as e:
            logger.error(f"Error calling tool {tool_name} on {server_name}: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    async def main():
        agg = MCPAggregator()
        tools = await agg.list_all_tools()
        print(json.dumps(str(tools), indent=2))

    asyncio.run(main())
