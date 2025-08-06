"""
Plugin Architecture for Extensible Robot Capabilities

Provides a comprehensive plugin system that allows third-party developers
to add custom sensors, actuators, and mission types to FLL-Sim.
"""

import importlib
import inspect
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type

from src.fll_sim.utils.errors import PluginError
from src.fll_sim.utils.logger import FLLLogger


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    name: str
    version: str
    author: str
    description: str
    category: str  # 'sensor', 'actuator', 'mission', 'visualization'
    dependencies: List[str]
    api_version: str = "1.0"
    enabled: bool = True


class PluginInterface(ABC):
    """Base interface for all plugins."""

    @abstractmethod
    def initialize(self, context: Dict[str, Any]) -> bool:
        """Initialize the plugin with simulation context."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up plugin resources."""
        pass

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        pass


class SensorPlugin(PluginInterface):
    """Base class for sensor plugins."""

    @abstractmethod
    def create_sensor(self, config: Dict[str, Any]) -> Any:
        """Create a sensor instance with given configuration."""
        pass

    @abstractmethod
    def get_sensor_types(self) -> List[str]:
        """Get list of sensor types provided by this plugin."""
        pass

    @abstractmethod
    def validate_sensor_config(self, config: Dict[str, Any]) -> bool:
        """Validate sensor configuration."""
        pass


class ActuatorPlugin(PluginInterface):
    """Base class for actuator plugins."""

    @abstractmethod
    def create_actuator(self, config: Dict[str, Any]) -> Any:
        """Create an actuator instance with given configuration."""
        pass

    @abstractmethod
    def get_actuator_types(self) -> List[str]:
        """Get list of actuator types provided by this plugin."""
        pass

    @abstractmethod
    def validate_actuator_config(self, config: Dict[str, Any]) -> bool:
        """Validate actuator configuration."""
        pass


class MissionPlugin(PluginInterface):
    """Base class for mission plugins."""

    @abstractmethod
    def create_mission(self, config: Dict[str, Any]) -> Any:
        """Create a mission instance with given configuration."""
        pass

    @abstractmethod
    def get_mission_types(self) -> List[str]:
        """Get list of mission types provided by this plugin."""
        pass

    @abstractmethod
    def validate_mission_config(self, config: Dict[str, Any]) -> bool:
        """Validate mission configuration."""
        pass


class VisualizationPlugin(PluginInterface):
    """Base class for visualization plugins."""

    @abstractmethod
    def render(self, renderer: Any, context: Dict[str, Any]) -> None:
        """Render plugin-specific visualization."""
        pass

    @abstractmethod
    def get_render_layers(self) -> List[str]:
        """Get list of render layers provided by this plugin."""
        pass


class PluginRegistry:
    """Registry for managing plugin types and instances."""

    def __init__(self):
        self.logger = FLLLogger('PluginRegistry')
        self.plugins: Dict[str, PluginInterface] = {}
        self.plugin_types: Dict[str, Type[PluginInterface]] = {}
        self.metadata: Dict[str, PluginMetadata] = {}

        # Register built-in plugin types
        self._register_builtin_types()

    def _register_builtin_types(self):
        """Register built-in plugin types."""
        self.plugin_types['sensor'] = SensorPlugin
        self.plugin_types['actuator'] = ActuatorPlugin
        self.plugin_types['mission'] = MissionPlugin
        self.plugin_types['visualization'] = VisualizationPlugin

    def register_plugin(self, plugin_id: str, plugin: PluginInterface):
        """Register a plugin instance."""
        if plugin_id in self.plugins:
            raise PluginError(f"Plugin already registered: {plugin_id}")

        metadata = plugin.get_metadata()

        # Validate plugin type
        if metadata.category not in self.plugin_types:
            raise PluginError(f"Unknown plugin category: {metadata.category}")

        expected_type = self.plugin_types[metadata.category]
        if not isinstance(plugin, expected_type):
            raise PluginError(
                f"Plugin {plugin_id} does not implement {expected_type.__name__}"
            )

        self.plugins[plugin_id] = plugin
        self.metadata[plugin_id] = metadata

        self.logger.info(f"Registered plugin: {plugin_id} ({metadata.category})")

    def unregister_plugin(self, plugin_id: str):
        """Unregister a plugin."""
        if plugin_id in self.plugins:
            plugin = self.plugins[plugin_id]
            plugin.cleanup()
            del self.plugins[plugin_id]
            del self.metadata[plugin_id]
            self.logger.info(f"Unregistered plugin: {plugin_id}")

    def get_plugin(self, plugin_id: str) -> Optional[PluginInterface]:
        """Get a plugin by ID."""
        return self.plugins.get(plugin_id)

    def get_plugins_by_category(self, category: str) -> Dict[str, PluginInterface]:
        """Get all plugins of a specific category."""
        return {
            plugin_id: plugin
            for plugin_id, plugin in self.plugins.items()
            if self.metadata[plugin_id].category == category
        }

    def list_plugins(self) -> List[str]:
        """List all registered plugin IDs."""
        return list(self.plugins.keys())

    def get_metadata(self, plugin_id: str) -> Optional[PluginMetadata]:
        """Get plugin metadata."""
        return self.metadata.get(plugin_id)


class PluginLoader:
    """Loads plugins from files and directories."""

    def __init__(self, registry: PluginRegistry):
        self.registry = registry
        self.logger = FLLLogger('PluginLoader')
        self.loaded_modules: Dict[str, Any] = {}

    def load_plugin_from_file(self, plugin_file: Path) -> str:
        """
        Load a plugin from a Python file.

        Args:
            plugin_file: Path to the plugin Python file

        Returns:
            Plugin ID if successful

        Raises:
            PluginError: If plugin loading fails
        """
        if not plugin_file.exists():
            raise PluginError(f"Plugin file not found: {plugin_file}")

        try:
            # Load the module
            spec = importlib.util.spec_from_file_location(
                plugin_file.stem, plugin_file
            )
            if spec is None or spec.loader is None:
                raise PluginError(f"Could not load plugin spec from {plugin_file}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find plugin class
            plugin_class = self._find_plugin_class(module)
            if plugin_class is None:
                raise PluginError(f"No plugin class found in {plugin_file}")

            # Create plugin instance
            plugin_instance = plugin_class()

            # Generate plugin ID
            plugin_id = f"{plugin_file.stem}_{plugin_instance.get_metadata().name}"

            # Register plugin
            self.registry.register_plugin(plugin_id, plugin_instance)

            # Store module reference
            self.loaded_modules[plugin_id] = module

            self.logger.info(f"Successfully loaded plugin from {plugin_file}")
            return plugin_id

        except Exception as e:
            raise PluginError(f"Failed to load plugin from {plugin_file}: {e}")

    def load_plugin_from_package(self, package_dir: Path) -> str:
        """
        Load a plugin from a package directory.

        Args:
            package_dir: Path to the plugin package directory

        Returns:
            Plugin ID if successful

        Raises:
            PluginError: If plugin loading fails
        """
        if not package_dir.is_dir():
            raise PluginError(f"Plugin package directory not found: {package_dir}")

        # Look for plugin.json metadata file
        metadata_file = package_dir / "plugin.json"
        if not metadata_file.exists():
            raise PluginError(f"Plugin metadata file not found: {metadata_file}")

        try:
            # Load metadata
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata_dict = json.load(f)

            # Find main plugin file
            main_file = package_dir / metadata_dict.get('main', '__init__.py')
            if not main_file.exists():
                raise PluginError(f"Main plugin file not found: {main_file}")

            # Load the plugin
            return self.load_plugin_from_file(main_file)

        except json.JSONDecodeError as e:
            raise PluginError(f"Invalid plugin metadata JSON: {e}")
        except Exception as e:
            raise PluginError(f"Failed to load plugin package from {package_dir}: {e}")

    def load_plugins_from_directory(self, plugins_dir: Path) -> List[str]:
        """
        Load all plugins from a directory.

        Args:
            plugins_dir: Directory containing plugins

        Returns:
            List of loaded plugin IDs
        """
        if not plugins_dir.exists():
            self.logger.warning(f"Plugin directory not found: {plugins_dir}")
            return []

        loaded_plugins = []

        for item in plugins_dir.iterdir():
            try:
                if item.is_file() and item.suffix == '.py':
                    # Single file plugin
                    plugin_id = self.load_plugin_from_file(item)
                    loaded_plugins.append(plugin_id)
                elif item.is_dir():
                    # Package plugin
                    plugin_id = self.load_plugin_from_package(item)
                    loaded_plugins.append(plugin_id)
            except PluginError as e:
                self.logger.error(f"Failed to load plugin from {item}: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error loading plugin from {item}: {e}")

        self.logger.info(f"Loaded {len(loaded_plugins)} plugins from {plugins_dir}")
        return loaded_plugins

    def _find_plugin_class(self, module: Any) -> Optional[Type[PluginInterface]]:
        """Find the plugin class in a module."""
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (issubclass(obj, PluginInterface) and
                obj is not PluginInterface and
                not inspect.isabstract(obj)):
                return obj
        return None

    def unload_plugin(self, plugin_id: str):
        """Unload a plugin and clean up resources."""
        self.registry.unregister_plugin(plugin_id)
        if plugin_id in self.loaded_modules:
            del self.loaded_modules[plugin_id]
            self.logger.info(f"Unloaded plugin: {plugin_id}")


class PluginManager:
    """Main plugin management system."""

    def __init__(self, plugins_dir: Optional[Path] = None):
        self.logger = FLLLogger('PluginManager')
        self.registry = PluginRegistry()
        self.loader = PluginLoader(self.registry)
        self.plugins_dir = plugins_dir or Path("plugins")
        self.simulation_context: Dict[str, Any] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}

    def initialize(self, simulation_context: Dict[str, Any]):
        """Initialize the plugin system with simulation context."""
        self.simulation_context = simulation_context

        # Initialize all registered plugins
        for plugin_id, plugin in self.registry.plugins.items():
            try:
                success = plugin.initialize(simulation_context)
                if success:
                    self.logger.info(f"Initialized plugin: {plugin_id}")
                else:
                    self.logger.warning(f"Plugin initialization failed: {plugin_id}")
            except Exception as e:
                self.logger.error(f"Error initializing plugin {plugin_id}: {e}")

    def load_all_plugins(self):
        """Load all plugins from the plugins directory."""
        if self.plugins_dir.exists():
            loaded = self.loader.load_plugins_from_directory(self.plugins_dir)
            self.logger.info(f"Loaded {len(loaded)} plugins")
            return loaded
        else:
            self.logger.info("No plugins directory found")
            return []

    def create_sensor(self, sensor_type: str, config: Dict[str, Any]) -> Any:
        """Create a sensor using appropriate plugin."""
        sensor_plugins = self.registry.get_plugins_by_category('sensor')

        for plugin_id, plugin in sensor_plugins.items():
            if sensor_type in plugin.get_sensor_types():
                if plugin.validate_sensor_config(config):
                    return plugin.create_sensor(config)
                else:
                    raise PluginError(f"Invalid sensor config for {sensor_type}")

        raise PluginError(f"No plugin found for sensor type: {sensor_type}")

    def create_actuator(self, actuator_type: str, config: Dict[str, Any]) -> Any:
        """Create an actuator using appropriate plugin."""
        actuator_plugins = self.registry.get_plugins_by_category('actuator')

        for plugin_id, plugin in actuator_plugins.items():
            if actuator_type in plugin.get_actuator_types():
                if plugin.validate_actuator_config(config):
                    return plugin.create_actuator(config)
                else:
                    raise PluginError(f"Invalid actuator config for {actuator_type}")

        raise PluginError(f"No plugin found for actuator type: {actuator_type}")

    def create_mission(self, mission_type: str, config: Dict[str, Any]) -> Any:
        """Create a mission using appropriate plugin."""
        mission_plugins = self.registry.get_plugins_by_category('mission')

        for plugin_id, plugin in mission_plugins.items():
            if mission_type in plugin.get_mission_types():
                if plugin.validate_mission_config(config):
                    return plugin.create_mission(config)
                else:
                    raise PluginError(f"Invalid mission config for {mission_type}")

        raise PluginError(f"No plugin found for mission type: {mission_type}")

    def get_available_types(self, category: str) -> List[str]:
        """Get all available types for a plugin category."""
        plugins = self.registry.get_plugins_by_category(category)
        available_types = []

        for plugin in plugins.values():
            if category == 'sensor':
                available_types.extend(plugin.get_sensor_types())
            elif category == 'actuator':
                available_types.extend(plugin.get_actuator_types())
            elif category == 'mission':
                available_types.extend(plugin.get_mission_types())

        return list(set(available_types))  # Remove duplicates

    def register_event_handler(self, event_name: str, handler: Callable):
        """Register an event handler."""
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)

    def trigger_event(self, event_name: str, *args, **kwargs):
        """Trigger an event and call all registered handlers."""
        if event_name in self.event_handlers:
            for handler in self.event_handlers[event_name]:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    self.logger.error(f"Error in event handler for {event_name}: {e}")

    def render_plugins(self, renderer: Any):
        """Render all visualization plugins."""
        viz_plugins = self.registry.get_plugins_by_category('visualization')

        for plugin_id, plugin in viz_plugins.items():
            try:
                plugin.render(renderer, self.simulation_context)
            except Exception as e:
                self.logger.error(f"Error rendering plugin {plugin_id}: {e}")

    def shutdown(self):
        """Shutdown the plugin system and clean up resources."""
        for plugin_id in list(self.registry.plugins.keys()):
            try:
                self.loader.unload_plugin(plugin_id)
            except Exception as e:
                self.logger.error(f"Error unloading plugin {plugin_id}: {e}")

        self.logger.info("Plugin system shutdown complete")

    def get_plugin_info(self) -> Dict[str, Any]:
        """Get information about all loaded plugins."""
        info = {
            'total_plugins': len(self.registry.plugins),
            'plugins_by_category': {},
            'plugin_details': {}
        }

        # Count by category
        for plugin_id, metadata in self.registry.metadata.items():
            category = metadata.category
            if category not in info['plugins_by_category']:
                info['plugins_by_category'][category] = 0
            info['plugins_by_category'][category] += 1

            # Plugin details
            info['plugin_details'][plugin_id] = {
                'name': metadata.name,
                'version': metadata.version,
                'author': metadata.author,
                'description': metadata.description,
                'category': metadata.category,
                'enabled': metadata.enabled
            }

        return info


# Example plugin implementations for reference
class ExampleSensorPlugin(SensorPlugin):
    """Example sensor plugin implementation."""

    def initialize(self, context: Dict[str, Any]) -> bool:
        """Initialize the plugin."""
        return True

    def cleanup(self) -> None:
        """Clean up plugin resources."""
        pass

    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="Example Sensor Plugin",
            version="1.0.0",
            author="FLL-Sim Team",
            description="Example plugin for demonstration",
            category="sensor",
            dependencies=[]
        )

    def create_sensor(self, config: Dict[str, Any]) -> Any:
        """Create a sensor instance."""
        # Implementation would create actual sensor
        return None

    def get_sensor_types(self) -> List[str]:
        """Get sensor types."""
        return ["example_sensor"]

    def validate_sensor_config(self, config: Dict[str, Any]) -> bool:
        """Validate sensor configuration."""
        return 'type' in config and config['type'] == 'example_sensor'
