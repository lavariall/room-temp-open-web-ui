
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import os
import asyncio
from src.openwebui_bridge import Tools

app = FastAPI()

# Setup templates
base_dir = os.path.dirname(os.path.abspath(__file__))
# Ensure directories exist
templates_dir = os.path.join(base_dir, "templates")
static_dir = os.path.join(base_dir, "static")

if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

templates = Jinja2Templates(directory=templates_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

tools = Tools()

# List of rooms to display
# We can fetch this from config or hardcode the expected ones as per requirements
ROOMS = ["room_91", "room_92", "room_93", "room_94", "room_95"]

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the dashboard with room temperatures."""
    room_data = []
    
    # Fetch data for all rooms concurrently
    tasks = [tools.get_room_climate(room) for room in ROOMS]
    results = await asyncio.gather(*tasks)
    
    for room_name, result in zip(ROOMS, results):
        # Result string format is usually: "Climate data for {room_name}: {json_content}" or "Error..."
        # We need to parse this slightly brittle string from the Bridge, 
        # or better yet, refactor Bridge to return structured data. 
        # For now, we parse.
        
        display_data = {
            "name": room_name,
            "temp": "n/a",
            "humidity": "n/a",
            "status": "offline"
        }

        if "Error" in result:
             display_data["status"] = "offline"
        else:
            try:
                # Extract the JSON part. 
                # Expected format: Climate data for room_91: {"temperature": 22.5, "humidity": 45}
                if ": " in result:
                    json_part = result.split(": ", 1)[1]
                    data = json.loads(json_part)
                    if isinstance(data, str):
                         # Handle double encoded json if necessary
                         data = json.loads(data)
                    
                    display_data["temp"] = f"{data.get('temperature', 'n/a')}°C"
                    display_data["humidity"] = f"{data.get('humidity', 'n/a')}%"
                    display_data["status"] = "online"
            except Exception as e:
                print(f"Error parsing result for {room_name}: {e}")
        
        room_data.append(display_data)

    return templates.TemplateResponse(request=request, name="index.html", context={"rooms": room_data})

from pydantic import BaseModel
import ollama

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Handle chat messages using Ollama with tool access."""
    user_message = request.message
    
    # Define the tool definitions for Ollama
    tool_defs = [{
        'type': 'function',
        'function': {
            'name': 'get_room_climate',
            'description': 'Get the temperature and humidity for a specific room.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'room_name': {
                        'type': 'string',
                        'description': 'The name of the room (e.g., room_91, room_92)',
                    },
                },
                'required': ['room_name'],
            },
        },
    }]

    messages = [{'role': 'user', 'content': user_message}]

    try:
        # 1. Ask Ollama (using a small, fast model if available, user mentioned qwen3:4b previously)
        # We'll default to a generic model name or env var suitable for the user's setup
        model_name = os.getenv("OLLAMA_MODEL", "qwen2.5:3b") 
        
        response = ollama.chat(
            model=model_name,
            messages=messages,
            tools=tool_defs
        )
        
        # 2. Check for tool calls
        if response.get('message', {}).get('tool_calls'):
            for tool in response['message']['tool_calls']:
                fn_name = tool['function']['name']
                args = tool['function']['arguments']
                
                if fn_name == 'get_room_climate':
                    # Execute the tool
                    result = await tools.get_room_climate(args.get('room_name'))
                    
                    # Add tool result to conversation
                    messages.append(response['message'])
                    messages.append({
                        'role': 'tool',
                        'content': str(result),
                    })
            
            # 3. Get final response after tool execution
            final_response = ollama.chat(
                model=model_name,
                messages=messages
            )
            return {"response": final_response['message']['content']}
        
        else:
            # No tool call, just return the text
            return {"response": response['message']['content']}

    except Exception as e:
        print(f"Chat Error: {e}")
        # Fallback simple logic if Ollama fails or not connected
        return {"response": "I'm having trouble connecting to my brain. But I can tell you I am monitoring the rooms."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
