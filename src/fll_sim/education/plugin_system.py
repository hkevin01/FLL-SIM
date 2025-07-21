"""
Plugin System Module

Provides a framework for loading, managing, and validating plugins for missions, robots, and educational modules in FLL-Sim.
Designed for extensibility and community content ecosystem.
"""

from typing import Dict, Any, List
import os
import json

class PluginValidationError(Exception):
    """Custom exception for plugin validation errors."""
    pass

class PluginManager:
    """Manages plugins for missions, robots, and educational modules."""
    def __init__(self):
        self.plugins: Dict[str, Any] = {}

    def load_plugin(self, plugin_id: str, plugin_data: dict) -> None:
        self.plugins[plugin_id] = plugin_data

    def get_plugin(self, plugin_id: str) -> Any:
        return self.plugins.get(plugin_id)

    def list_plugins(self) -> List[str]:
        return list(self.plugins.keys())

    def validate_plugin(self, plugin_id: str) -> bool:
        # Example validation: check required fields
        plugin = self.plugins.get(plugin_id)
        if not plugin or 'type' not in plugin or 'name' not in plugin:
            raise PluginValidationError(f"Plugin {plugin_id} missing required fields.")
        return True

    def load_plugins_from_directory(self, directory: str) -> None:
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                plugin_id = filename[:-5]
                with open(os.path.join(directory, filename), 'r', encoding='utf-8') as f:
                    plugin_data = json.load(f)
                self.load_plugin(plugin_id, plugin_data)

    def load_marketplace_plugins(self, marketplace_dir: str) -> None:
        """Load plugins from a marketplace directory."""
        import os, json
        for filename in os.listdir(marketplace_dir):
            if filename.endswith('.json'):
                plugin_id = filename[:-5]
                with open(os.path.join(marketplace_dir, filename), 'r', encoding='utf-8') as f:
                    plugin_data = json.load(f)
                self.load_plugin(plugin_id, plugin_data)
        self.logger.info(f"Marketplace plugins loaded from {marketplace_dir}")

    def remove_plugin(self, plugin_id: str) -> None:
        if plugin_id in self.plugins:
            del self.plugins[plugin_id]
