# coding:utf-8
"""Simple test script to test micromcp compatibility with fastmcp"""
# client.py (auf deinem Laptop)
import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

TOKEN = "token"

async def main():
    # Übergib die 'Host:Port'-Adresse und die Transport-Klasse
    transport = StreamableHttpTransport(
        url="http://192.168.0.91:8080/mcp",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "X-Custom-Header": "value"
        }
    )
    async with Client(transport=transport) as client:

        print("Warte auf client.list_tools()...")
        tools = await client.list_tools()
        print(f"Verfügbare Tools: {tools}")

        resources = await client.list_resources()
        print(f"Verfügbare Ressourcen: {resources}")

        result = await client.call_tool("get_temperature_and_humidity")
        print(f"Empfangene Temperatur und Luftfeuchtigkeit: {result.content}")

        version = await client.read_resource("get://temperature")
        print(f"Resource Temperatur: {version}")

        version = await client.read_resource("get://humidity")
        print(f"Resource Luftfeuchtigkeit: {version}")


if __name__ == "__main__":
    asyncio.run(main())

# Will produce the following output:
# Warte auf client.list_tools()...
# Verfügbare Tools: [Tool(name='initialize', title=None, description='Der Handshake für StreamableHttpTransport.', inputSchema={'properties': {}, 'required': [], 'type': 'object'}, outputSchema=None, icons=None, annotations=None, meta=None), Tool(name='get_temperature_and_humidity', title=None, description="Gibt die Temperatur und Luftfeuchtigkeit als JSON zurück.  :return: dict with following format: {'temperature': temp, 'humidity': hum, 'timestamp': time.time()}", inputSchema={'properties': {}, 'required': [], 'type': 'object'}, outputSchema=None, icons=None, annotations=None, meta=None)]
# Verfügbare Ressourcen: [Resource(name='get_temperature', title=None, uri=AnyUrl('get://temperature'), description="Gibt die Temperatur als String zurück.  :return: String with following format: '25.4'", mimeType=None, size=None, icons=None, annotations=None, meta=None, uri_pattern='get://temperature', readSchema={'properties': {}, 'required': [], 'type': 'object'}, outputSchema={'properties': {}, 'required': [], 'type': 'object'}), Resource(name='get_humidity', title=None, uri=AnyUrl('get://humidity'), description="Gibt die Luftfeuchtigkeit als String zurück.  :return: String with following format: '54'", mimeType=None, size=None, icons=None, annotations=None, meta=None, uri_pattern='get://humidity', readSchema={'properties': {}, 'required': [], 'type': 'object'}, outputSchema={'properties': {}, 'required': [], 'type': 'object'})]
# Empfangene Temperatur und Luftfeuchtigkeit: [TextContent(type='text', text="{'humidity': 57.9, 'timestamp': 34, 'temperature': 22.5}", annotations=None, meta=None, __type__='TextContent')]
# Resource Temperatur: [TextResourceContents(uri=AnyUrl('get://temperature'), mimeType=None, meta=None, text='22.5', __type__='TextContent', type='text')]
# Resource Luftfeuchtigkeit: [TextResourceContents(uri=AnyUrl('get://humidity'), mimeType=None, meta=None, text='57.9', __type__='TextContent', type='text')]

# Process finished with exit code 0
