from pydantic import BaseModel, Field
from typing import List

class Esp32Server(BaseModel):
    name: str = Field(..., description="Name of the ESP32 server e.g. livingroom")
    url: str = Field(..., description="URL of the ESP32 server e.g. http://192.168.0.91:8080/mcp")
    token: str = Field(..., description="Token for the ESP32 server e.g. token")

class AppConfig(BaseModel):
    mcp_servers: List[Esp32Server]
