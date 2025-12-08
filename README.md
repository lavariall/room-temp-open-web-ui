# Room Temp Hum Server

This project integrates Open WebUI with local MCP servers to monitor room temperature and humidity.

## Project Setup

### Prerequisites
- Python 3.11 (Note: `open-webui` currently has issues with Python 3.13)
- `uv` (recommended) or `pip`
- Docker (optional)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd room-temp-hum-server
    ```

2.  **Install Dependencies using uv:**
    ```bash
    uv sync
    ```

3.  **Configuration:**
    -   `config.json` contains the list of MCP servers. **Do not commit this file if it contains private data.**
    -   The application looks for `config.json` in the current working directory or `/app/config.json` in Docker.

### Running Locally

```bash
# Set encoding to avoid issues on Windows
$env:PYTHONIOENCODING="utf-8"
uv run open-webui serve
```
Access the UI at `http://localhost:8080`.

### Running with Docker

1.  Build the image:
    ```bash
    docker build -t room-temp-hum-server .
    ```
2.  Run the container:
    ```bash
    docker run -p 8080:8080 -v $(pwd)/config.json:/app/config.json --name open-webui room-temp-hum-server
    ```

## Integrating with Open WebUI

To allow the LLM to access your MCP servers:

1.  Open Open WebUI in your browser (`http://localhost:8080`).
2.  Sign up (first user is admin).
3.  Go to **Workspace** -> **Tools**.
4.  Click **Create Tool**.
5.  Copy the content of `src/openwebui_bridge.py` and paste it into the code editor.
6.  (Optional) Rename the tool class or file if needed, but the provided script is structured to be compatible.
7.  Ensure the tool name is descriptive (e.g., `RoomClimate`).
8.  Enable the tool for your specific model (e.g., `qwen3:4b`) in the model settings or chat settings.

## Tests

Run tests using `pytest`:

```bash
uv run pytest
```

Check coverage:
```bash
uv run coverage run -m pytest
uv run coverage report
```
