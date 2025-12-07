from pydantic import BaseModel, Field
from typing import List

class McpServer(BaseModel):
    name: str = Field(..., description="Name of the MCP server e.g. livingroom")
    url: str = Field(..., description="URL of the MCP server e.g. http://192.168.0.91:8080/mcp")
    token: str = Field(..., description="Token for the MCP server e.g. token")

class AppConfig(BaseModel):
    mcp_servers: List[McpServer]
