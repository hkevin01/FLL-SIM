"""
Integration module for enhanced FLL-Sim systems

This module provides integration points for the enhanced configuration
management, error handling, plugin architecture, and state management systems.
"""

import os
from typing import Any, Dict, Optional

from fll_sim.config.enhanced_config_manager import (ConfigProfileManager,
                                                    ConfigValidator,
                                                    TypeSafeConfigLoader)
from fll_sim.core.state_management import SimulationStateManager
from fll_sim.plugins.plugin_system import PluginManager
from fll_sim.utils.enhanced_errors import (ConfigurationError, ErrorContext,
                                           ErrorRecoveryManager,
                                           SimulationError)
from fll_sim.utils.logger import FLLLogger


class EnhancedFLLSimulator:
    """
    Enhanced FLL Simulator with integrated configuration management,
    error handling, plugin architecture, and state management.
    """

    def __init__(self, config_path: Optional[str] = None):
        self.logger = FLLLogger('EnhancedFLLSimulator')

        # Initialize core systems
        self.config_loader = TypeSafeConfigLoader()
        self.config_validator = ConfigValidator()
        self.profile_manager = ConfigProfileManager()
        self.error_recovery = ErrorRecoveryManager()
        self.plugin_manager = PluginManager()
        self.state_manager = SimulationStateManager()

        # Configuration
        self.config: Dict[str, Any] = {}
        self.config_path = config_path or self._get_default_config_path()

        # Simulation components
        self.robot = None
        self.physics_engine = None
        self.sensors = {}
        self.actuators = {}

        # Setup integration
        self._setup_integration()

        self.logger.info("Enhanced FLL Simulator initialized")

    def _get_default_config_path(self) -> str:
        """Get default configuration path."""
        return os.path.join(
            os.path.dirname(__file__), '..', '..', '..', 'configs'
        )

    def _setup_integration(self):
        """Setup integration between systems."""
        # Register simulator with state manager
        self.state_manager.register_component('simulator', self)
        self.state_manager.register_component(
            'config_loader', self.config_loader
        )
        self.state_manager.register_component(
            'plugin_manager', self.plugin_manager
        )

        # Setup initialization steps
        self.state_manager.add_initialization_step(self._load_configuration)
        self.state_manager.add_initialization_step(self._setup_error_handling)
        self.state_manager.add_initialization_step(self._load_plugins)
        self.state_manager.add_initialization_step(
            self._initialize_simulation_components
        )

        # Setup shutdown steps
        self.state_manager.add_shutdown_step(
            self._cleanup_simulation_components
        )
        self.state_manager.add_shutdown_step(self._unload_plugins)

        # Register error handlers with plugin manager
        self.plugin_manager.set_error_handler(self._handle_plugin_error)

        self.logger.debug("System integration completed")

    def initialize(self, profile: Optional[str] = None) -> bool:
        """
        Initialize the enhanced simulator.

        Args:
            profile: Optional configuration profile to use

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            with ErrorContext(
                "Simulator initialization",
                self.error_recovery,
                retry_limit=3
            ):
                # Set active profile if provided
                if profile:
                    self.profile_manager.set_active_profile(profile)

                # Initialize through state manager
                success = self.state_manager.initialize()

                if success:
                    self.logger.info(
                        "Enhanced FLL Simulator initialized successfully"
                    )
                else:
                    self.logger.error(
                        "Failed to initialize Enhanced FLL Simulator"
                    )

                return success

        except Exception as e:
            self.logger.error(f"Initialization error: {e}")
            return False

    def start(self) -> bool:
        """
        Start the simulation.

        Returns:
            True if startup successful, False otherwise
        """
        try:
            success = self.state_manager.start()

            if success:
                self.logger.info("Simulation started successfully")
            else:
                self.logger.error("Failed to start simulation")

            return success

        except Exception as e:
            self.logger.error(f"Startup error: {e}")
            return False

    def pause(self) -> bool:
        """Pause the simulation."""
        return self.state_manager.pause()

    def resume(self) -> bool:
        """Resume the simulation."""
        return self.state_manager.resume()

    def stop(self) -> bool:
        """Stop the simulation."""
        return self.state_manager.stop()

    def shutdown(self) -> bool:
        """Shutdown the simulation system."""
        success = self.state_manager.shutdown()

        if success:
            self.logger.info("Enhanced FLL Simulator shutdown completed")
        else:
            self.logger.error("Simulator shutdown encountered errors")

        return success

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive simulator status."""
        base_status = self.state_manager.get_status()

        return {
            **base_status,
            'config_loaded': bool(self.config),
            'active_profile': self.profile_manager.get_active_profile(),
            'loaded_plugins': list(
                self.plugin_manager.get_loaded_plugins().keys()
            ),
            'available_sensors': list(self.sensors.keys()),
            'available_actuators': list(self.actuators.keys()),
            'robot_initialized': self.robot is not None,
            'physics_engine_initialized': self.physics_engine is not None,
        }

    def _load_configuration(self):
        """Load and validate configuration."""
        self.logger.info("Loading configuration...")

        try:
            # Load main configuration
            config_file = os.path.join(self.config_path, 'defaults.yaml')
            if os.path.exists(config_file):
                self.config = self.config_loader.load_config(config_file)

                # Apply profile overrides if active profile is set
                active_profile = self.profile_manager.get_active_profile()
                if active_profile:
                    profile_config = self.profile_manager.load_profile(
                        active_profile
                    )
                    self.config = self.config_loader.merge_configs(
                        self.config, profile_config
                    )

                # Validate configuration
                if not self.config_validator.validate_config(self.config):
                    raise ConfigurationError(
                        "Configuration validation failed",
                        context={'config_path': config_file}
                    )

                self.logger.info("Configuration loaded and validated successfully")
            else:
                self.logger.warning(
                    f"Configuration file not found: {config_file}"
                )
                # Use default configuration
                self.config = self._get_default_config()

        except Exception as e:
            raise ConfigurationError(
                f"Failed to load configuration: {e}",
                context={'config_path': self.config_path}
            )

    def _setup_error_handling(self):
        """Setup error handling strategies."""
        self.logger.info("Setting up error handling...")

        # Configure error recovery strategies based on configuration
        error_config = self.config.get('error_handling', {})

        strategies = error_config.get('strategies', {})
        for error_type, strategy_config in strategies.items():
            self.error_recovery.register_strategy(
                error_type,
                strategy_config.get('handler'),
                max_retries=strategy_config.get('max_retries', 3),
                backoff=strategy_config.get('backoff', 1.0)
            )

        self.logger.info("Error handling setup completed")

    def _load_plugins(self):
        """Load and initialize plugins."""
        self.logger.info("Loading plugins...")

        try:
            # Get plugin configuration
            plugin_config = self.config.get('plugins', {})

            # Load plugins from directories
            plugin_dirs = plugin_config.get('directories', ['plugins'])
            for plugin_dir in plugin_dirs:
                full_path = os.path.join(self.config_path, '..', plugin_dir)
                if os.path.exists(full_path):
                    self.plugin_manager.load_plugins_from_directory(full_path)

            # Enable specific plugins
            enabled_plugins = plugin_config.get('enabled', [])
            for plugin_name in enabled_plugins:
                self.plugin_manager.enable_plugin(plugin_name)

            self.logger.info(
                f"Loaded {len(self.plugin_manager.get_loaded_plugins())} plugins"
            )

        except Exception as e:
            raise SimulationError(
                f"Failed to load plugins: {e}",
                context={'plugin_config': plugin_config}
            )

    def _initialize_simulation_components(self):
        """Initialize simulation components with plugin support."""
        self.logger.info("Initializing simulation components...")

        try:
            # Initialize robot with plugin enhancements
            robot_config = self.config.get('robot', {})
            self._initialize_robot(robot_config)

            # Initialize physics engine
            physics_config = self.config.get('physics', {})
            self._initialize_physics_engine(physics_config)

            # Initialize sensors (including plugin sensors)
            sensor_configs = self.config.get('sensors', {})
            self._initialize_sensors(sensor_configs)

            # Initialize actuators (including plugin actuators)
            actuator_configs = self.config.get('actuators', {})
            self._initialize_actuators(actuator_configs)

            self.logger.info("Simulation components initialized successfully")

        except Exception as e:
            raise SimulationError(
                f"Failed to initialize simulation components: {e}"
            )

    def _initialize_robot(self, config: Dict[str, Any]):
        """Initialize robot with configuration."""
        # This would integrate with existing robot initialization
        # For now, just log that we would initialize the robot
        self.logger.debug("Robot initialization would happen here")

        # Example integration point:
    # from fll_sim.robot.robot import Robot
        # self.robot = Robot(config)

    def _initialize_physics_engine(self, config: Dict[str, Any]):
        """Initialize physics engine with configuration."""
        self.logger.debug("Physics engine initialization would happen here")

        # Example integration point:
    # from fll_sim.physics.engine import PhysicsEngine
        # self.physics_engine = PhysicsEngine(config)

    def _initialize_sensors(self, configs: Dict[str, Any]):
        """Initialize sensors including plugin sensors."""
        self.logger.debug("Sensor initialization would happen here")

        # Initialize standard sensors
        for sensor_name, sensor_config in configs.items():
            sensor_type = sensor_config.get('type')

            # Check if plugin provides this sensor type
            plugin_sensor = self.plugin_manager.get_sensor_plugin(sensor_type)
            if plugin_sensor:
                self.sensors[sensor_name] = plugin_sensor.create_sensor(sensor_config)
                self.logger.debug(f"Created plugin sensor: {sensor_name}")
            else:
                # Use standard sensor creation
                self.logger.debug(f"Would create standard sensor: {sensor_name}")

    def _initialize_actuators(self, configs: Dict[str, Any]):
        """Initialize actuators including plugin actuators."""
        self.logger.debug("Actuator initialization would happen here")

        # Initialize standard actuators
        for actuator_name, actuator_config in configs.items():
            actuator_type = actuator_config.get('type')

            # Check if plugin provides this actuator type
            plugin_actuator = self.plugin_manager.get_actuator_plugin(actuator_type)
            if plugin_actuator:
                self.actuators[actuator_name] = plugin_actuator.create_actuator(
                    actuator_config
                )
                self.logger.debug(f"Created plugin actuator: {actuator_name}")
            else:
                # Use standard actuator creation
                self.logger.debug(f"Would create standard actuator: {actuator_name}")

    def _cleanup_simulation_components(self):
        """Cleanup simulation components."""
        self.logger.info("Cleaning up simulation components...")

        # Cleanup sensors
        for sensor in self.sensors.values():
            if hasattr(sensor, 'cleanup'):
                sensor.cleanup()
        self.sensors.clear()

        # Cleanup actuators
        for actuator in self.actuators.values():
            if hasattr(actuator, 'cleanup'):
                actuator.cleanup()
        self.actuators.clear()

        # Cleanup robot
        if self.robot and hasattr(self.robot, 'cleanup'):
            self.robot.cleanup()
        self.robot = None

        # Cleanup physics engine
        if self.physics_engine and hasattr(self.physics_engine, 'cleanup'):
            self.physics_engine.cleanup()
        self.physics_engine = None

        self.logger.info("Simulation components cleanup completed")

    def _unload_plugins(self):
        """Unload all plugins."""
        self.logger.info("Unloading plugins...")

        try:
            # Unload all plugins
            for plugin_name in list(self.plugin_manager.get_loaded_plugins().keys()):
                self.plugin_manager.unload_plugin(plugin_name)

            self.logger.info("All plugins unloaded successfully")

        except Exception as e:
            self.logger.error(f"Error unloading plugins: {e}")

    def _handle_plugin_error(self, plugin_name: str, error: Exception):
        """Handle plugin errors."""
        self.logger.error(f"Plugin error in {plugin_name}: {error}")

        # Create appropriate error and handle through error recovery
        plugin_error = SimulationError(
            f"Plugin {plugin_name} encountered an error: {error}",
            context={'plugin_name': plugin_name, 'original_error': str(error)}
        )

        self.state_manager.handle_error(plugin_error)

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration when no config file is found."""
        return {
            'robot': {
                'type': 'standard',
                'dimensions': {'width': 0.18, 'height': 0.18, 'length': 0.18}
            },
            'physics': {
                'engine': 'pymunk',
                'gravity': [0, -981],  # cm/s^2
                'timestep': 1/60
            },
            'sensors': {},
            'actuators': {},
            'plugins': {
                'directories': ['plugins'],
                'enabled': []
            },
            'error_handling': {
                'strategies': {}
            }
        }


# Compatibility function for existing code
def create_enhanced_simulator(config_path: Optional[str] = None) -> EnhancedFLLSimulator:
    """
    Create an enhanced FLL simulator instance.

    Args:
        config_path: Optional path to configuration directory

    Returns:
        EnhancedFLLSimulator instance
    """
    return EnhancedFLLSimulator(config_path)


# Integration helpers for existing codebase
class SimulatorIntegration:
    """Helper class for integrating with existing simulator code."""

    @staticmethod
    def wrap_existing_simulator(existing_simulator, config_path: Optional[str] = None):
        """
        Wrap an existing simulator with enhanced capabilities.

        Args:
            existing_simulator: Existing simulator instance
            config_path: Optional configuration path

        Returns:
            Enhanced simulator wrapper
        """
        enhanced = EnhancedFLLSimulator(config_path)

        # Register existing simulator as a component
        enhanced.state_manager.register_component('legacy_simulator', existing_simulator)

        return enhanced

    @staticmethod
    def get_migration_guide() -> Dict[str, str]:
        """Get migration guide for existing code."""
        return {
            'configuration': 'Replace direct config loading with TypeSafeConfigLoader',
            'error_handling': 'Use ErrorContext for error-prone operations',
            'plugins': 'Register custom components as plugins',
            'state_management': 'Use SimulationStateManager for lifecycle management',
            'initialization': 'Use enhanced initialization with validation'
        }
