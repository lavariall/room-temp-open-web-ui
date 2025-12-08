# Room Temp Hum Server

This project is a lightweight aggregation server for monitoring room temperature and humidity from distributed ESP32 devices. It uses `aiohttp` for the web server and `jinja2` for templating.

> **Note:** Previous integration with Open WebUI has been deprecated and removed.

## Project Setup

### Prerequisites
- Python 3.11+
- `uv` (recommended) or `pip`

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
    -   Create or update `utils/config.json`.
    -   The configuration should specify the list of rooms, their IPs, and authentication tokens.
    -   **Important:** Do not commit `config.json` if it contains private keys or tokens.

    Example `config.json` structure:
    ```json
    {
      "rooms": [
        {
          "name": "Living Room",
          "ip": "192.168.0.91",
          "token": "your_secret_token"
        },
        ...
      ]
    }
    ```

## Running the Server

### Running Locally

```bash
# Ensure you are in the project root
uv run python src/server.py
```

The server will be available at:
- `http://localhost:8000/roomstemphum`
- `http://localhost:8000/` (redirects to /roomstemphum)

### Running with Docker

1.  Build the image:
    ```bash
    docker build -t room-temp-hum-server .
    ```

2.  Run the container:
    ```bash
    docker run -p 8000:8000 -v $(pwd)/utils/config.json:/app/utils/config.json --name room-temp-server room-temp-hum-server
    ```

## Architecture

- **Backend:** Python `aiohttp` server.
- **Frontend:** HTML templates rendered with `jinja2`.
- **Data Source:** Fetches JSON data `{"temperature": "...", "humidity": "..."}` from configured device IPs.

## Tests

Run tests using `pytest`:

```bash
uv run pytest
```
