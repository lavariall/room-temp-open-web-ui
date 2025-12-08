"""
Manual test script for Ollama integration.
"""
# pylint: disable=duplicate-code
import asyncio
import ollama
from src.openwebui_bridge import Tools

async def run_test():
    """Run manual test against Ollama."""
    print("Initializing Tools...")
    tools_instance = Tools()

    # Define the tool manually for Ollama
    # (OpenWebUI usually does this based on the function signature)
    tool_def = {
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
    }

    print("Querying Ollama (model: qwen3:1.7b)...")
    messages = [{'role': 'user', 'content': 'What is the temperature in room_91?'}]

    try:
        response = ollama.chat(
            model='qwen3:1.7b',
            messages=messages,
            tools=[tool_def]
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Failed to call Ollama: {e}")
        return

    print("Response from Ollama:")
    print(response)

    # Check if the model decided to call the tool
    if response.get('message', {}).get('tool_calls'):
        for tool in response['message']['tool_calls']:
            fn_name = tool['function']['name']
            args = tool['function']['arguments']
            print(f"\nModel requested tool call: {fn_name} with args {args}")

            if fn_name == 'get_room_climate':
                print("Executing tool...")
                # Call the actual Python function from our bridge
                result = await tools_instance.get_room_climate(args['room_name'])
                print(f"Tool Result: {result}")

                # Verify logic: send result back to LLM
                messages.append(response['message'])
                messages.append({
                    'role': 'tool',
                    'content': str(result),
                })

                print("\nGenerating final response...")
                final_response = ollama.chat(
                    model='qwen3:1.7b',
                    messages=messages,
                )
                try:
                    print("Final Agent Response: " + final_response['message']['content'])
                except UnicodeEncodeError:
                    print(
                        "Final Agent Response: " +
                        final_response['message']['content'].encode(
                            'utf-8', errors='ignore'
                        ).decode('utf-8')
                    )
    else:
        print("The model did not call the tool. It might have hallucinated or refused.")

if __name__ == "__main__":
    asyncio.run(run_test())
