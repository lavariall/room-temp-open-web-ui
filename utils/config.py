
import json
import os
from typing import Optional
from .models import AppConfig

class Config:
    """
    Configuration manager for the application.
    Encapsulates loading and accessing the configuration.
    """
    def __init__(self, config_path: Optional[str] = None):
        self._config_path = self._resolve_config_path(config_path)
        self._data: AppConfig = self._load_config()

    def _resolve_config_path(self, config_path: Optional[str]) -> str:
        """Resolve the path to the configuration file."""
        if config_path:
             return config_path

        # Check if we are in Docker or have ENV override
        env_path = os.getenv("MCP_CONFIG_PATH")
        if env_path and os.path.exists(env_path):
            return env_path
        
        # Default to config.json in the same directory as this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "config.json")

    def _load_config(self) -> AppConfig:
        """Internal method to load configuration from disk."""
        if not os.path.exists(self._config_path):
            print(f"Config file not found at {self._config_path}")
            return AppConfig(mcp_servers=[])

        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return AppConfig(**data)
        except Exception as e:
            print(f"Error loading config: {e}")
            return AppConfig(mcp_servers=[])

    @property
    def data(self) -> AppConfig:
        """Access the raw AppConfig model."""
        return self._data

    @property
    def mcp_servers(self):
        """Shortcut to access mcp_servers."""
        return self._data.mcp_servers
