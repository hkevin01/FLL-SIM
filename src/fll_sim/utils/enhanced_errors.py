"""
Comprehensive Error Handling and Custom Exception Classes

Provides custom exception classes for different simulation scenarios
and comprehensive error handling throughout the simulation engine.
"""

import traceback
from enum import Enum
from typing import Any, Dict, List, Optional

from ..utils.logger import FLLLogger


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SimulationError(Exception):
    """Base exception for all simulation-related errors."""

    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.context = context or {}
        self.timestamp = None
        self._log_error()

    def _log_error(self):
        """Log the error with appropriate severity level."""
        logger = FLLLogger('SimulationError')

        log_message = f"{self.__class__.__name__}: {self.message}"
        if self.context:
            log_message += f" Context: {self.context}"

        if self.severity == ErrorSeverity.LOW:
            logger.debug(log_message)
        elif self.severity == ErrorSeverity.MEDIUM:
            logger.info(log_message)
        elif self.severity == ErrorSeverity.HIGH:
            logger.warning(log_message)
        else:  # CRITICAL
            logger.error(log_message)


class RobotCollisionError(SimulationError):
    """Exception raised when robot collides with obstacles or boundaries."""

    def __init__(self, collision_type: str, robot_position: tuple,
                 obstacle_info: Optional[Dict[str, Any]] = None):
        context = {
            'collision_type': collision_type,
            'robot_position': robot_position,
            'obstacle_info': obstacle_info
        }
        message = f"Robot collision detected: {collision_type} at {robot_position}"
        super().__init__(message, ErrorSeverity.HIGH, context)


class SensorFailureError(SimulationError):
    """Exception raised when sensor operations fail."""

    def __init__(self, sensor_name: str, sensor_type: str,
                 failure_reason: str, sensor_data: Optional[Dict] = None):
        context = {
            'sensor_name': sensor_name,
            'sensor_type': sensor_type,
            'failure_reason': failure_reason,
            'sensor_data': sensor_data
        }
        message = f"Sensor failure: {sensor_name} ({sensor_type}) - {failure_reason}"
        super().__init__(message, ErrorSeverity.MEDIUM, context)


class MissionTimeoutError(SimulationError):
    """Exception raised when mission times out."""

    def __init__(self, mission_id: str, time_limit: float,
                 elapsed_time: float, progress: float = 0.0):
        context = {
            'mission_id': mission_id,
            'time_limit': time_limit,
            'elapsed_time': elapsed_time,
            'progress': progress
        }
        message = (f"Mission timeout: {mission_id} exceeded {time_limit}s "
                  f"(elapsed: {elapsed_time:.2f}s, progress: {progress:.1%})")
        super().__init__(message, ErrorSeverity.HIGH, context)


class PhysicsEngineError(SimulationError):
    """Exception raised when physics engine encounters problems."""

    def __init__(self, operation: str, physics_state: Optional[Dict] = None):
        context = {
            'operation': operation,
            'physics_state': physics_state
        }
        message = f"Physics engine error during: {operation}"
        super().__init__(message, ErrorSeverity.CRITICAL, context)


class ConfigurationError(SimulationError):
    """Exception raised for configuration-related errors."""

    def __init__(self, config_type: str, invalid_values: List[str],
                 config_path: Optional[str] = None):
        context = {
            'config_type': config_type,
            'invalid_values': invalid_values,
            'config_path': config_path
        }
        message = f"Configuration error in {config_type}: {', '.join(invalid_values)}"
        super().__init__(message, ErrorSeverity.HIGH, context)


class RobotControlError(SimulationError):
    """Exception raised for robot control system errors."""

    def __init__(self, command_type: str, robot_state: Dict[str, Any],
                 error_details: str):
        context = {
            'command_type': command_type,
            'robot_state': robot_state,
            'error_details': error_details
        }
        message = f"Robot control error: {command_type} - {error_details}"
        super().__init__(message, ErrorSeverity.MEDIUM, context)


class VisualizationError(SimulationError):
    """Exception raised for rendering and visualization errors."""

    def __init__(self, render_operation: str, display_info: Dict[str, Any]):
        context = {
            'render_operation': render_operation,
            'display_info': display_info
        }
        message = f"Visualization error during: {render_operation}"
        super().__init__(message, ErrorSeverity.LOW, context)


class PluginError(SimulationError):
    """Exception raised for plugin system errors."""

    def __init__(self, plugin_name: str, operation: str,
                 plugin_info: Optional[Dict] = None):
        context = {
            'plugin_name': plugin_name,
            'operation': operation,
            'plugin_info': plugin_info
        }
        message = f"Plugin error: {plugin_name} during {operation}"
        super().__init__(message, ErrorSeverity.MEDIUM, context)


class ErrorRecoveryManager:
    """Manages error recovery strategies for different types of errors."""

    def __init__(self):
        self.logger = FLLLogger('ErrorRecoveryManager')
        self.recovery_strategies = {
            RobotCollisionError: self._recover_from_collision,
            SensorFailureError: self._recover_from_sensor_failure,
            MissionTimeoutError: self._recover_from_timeout,
            PhysicsEngineError: self._recover_from_physics_error,
            ConfigurationError: self._recover_from_config_error,
            RobotControlError: self._recover_from_control_error,
            VisualizationError: self._recover_from_visualization_error,
            PluginError: self._recover_from_plugin_error
        }
        self.error_history: List[Dict[str, Any]] = []

    def handle_error(self, error: SimulationError, simulation_context: Dict[str, Any]) -> bool:
        """
        Handle an error and attempt recovery.

        Args:
            error: The simulation error to handle
            simulation_context: Current simulation state and context

        Returns:
            True if recovery was successful, False otherwise
        """
        self.logger.warning(f"Handling error: {error.__class__.__name__}")

        # Record error in history
        self._record_error(error, simulation_context)

        # Attempt recovery
        error_type = type(error)
        if error_type in self.recovery_strategies:
            try:
                recovery_success = self.recovery_strategies[error_type](
                    error, simulation_context
                )
                if recovery_success:
                    self.logger.info(f"Successfully recovered from {error_type.__name__}")
                else:
                    self.logger.error(f"Failed to recover from {error_type.__name__}")
                return recovery_success
            except Exception as recovery_error:
                self.logger.error(f"Recovery strategy failed: {recovery_error}")
                return False
        else:
            self.logger.warning(f"No recovery strategy for {error_type.__name__}")
            return False

    def _record_error(self, error: SimulationError, context: Dict[str, Any]):
        """Record error in history for analysis."""
        import time

        error_record = {
            'timestamp': time.time(),
            'error_type': error.__class__.__name__,
            'message': error.message,
            'severity': error.severity.value,
            'context': error.context,
            'simulation_context': context,
            'traceback': traceback.format_exc()
        }
        self.error_history.append(error_record)

        # Keep only last 100 errors
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]

    def _recover_from_collision(self, error: RobotCollisionError,
                               context: Dict[str, Any]) -> bool:
        """Recover from robot collision."""
        self.logger.info("Attempting collision recovery...")

        # Strategy: Move robot away from collision point
        if 'robot' in context:
            robot = context['robot']
            try:
                # Stop robot movement
                robot.stop()

                # Move robot backwards slightly
                robot.move_distance(-50)  # Move back 50mm

                # Clear any pending commands
                robot.clear_command_queue()

                return True
            except Exception as e:
                self.logger.error(f"Collision recovery failed: {e}")
                return False
        return False

    def _recover_from_sensor_failure(self, error: SensorFailureError,
                                    context: Dict[str, Any]) -> bool:
        """Recover from sensor failure."""
        self.logger.info("Attempting sensor failure recovery...")

        if 'robot' in context:
            robot = context['robot']
            sensor_name = error.context.get('sensor_name')

            try:
                # Try to reset the sensor
                if sensor_name and hasattr(robot, 'reset_sensor'):
                    robot.reset_sensor(sensor_name)
                    return True

                # Fallback: Use alternative sensors
                if hasattr(robot, 'enable_sensor_fallback'):
                    robot.enable_sensor_fallback(sensor_name)
                    return True

            except Exception as e:
                self.logger.error(f"Sensor recovery failed: {e}")

        return False

    def _recover_from_timeout(self, error: MissionTimeoutError,
                             context: Dict[str, Any]) -> bool:
        """Recover from mission timeout."""
        self.logger.info("Attempting timeout recovery...")

        # Strategy: Reset mission or extend time limit
        if 'mission' in context:
            mission = context['mission']
            try:
                # Reset mission to last checkpoint if available
                if hasattr(mission, 'reset_to_checkpoint'):
                    mission.reset_to_checkpoint()
                    return True

                # Or reset completely
                mission.reset()
                return True

            except Exception as e:
                self.logger.error(f"Timeout recovery failed: {e}")

        return False

    def _recover_from_physics_error(self, error: PhysicsEngineError,
                                   context: Dict[str, Any]) -> bool:
        """Recover from physics engine error."""
        self.logger.info("Attempting physics engine recovery...")

        # Strategy: Reset physics state or reduce complexity
        if 'simulator' in context:
            simulator = context['simulator']
            try:
                # Try to reset physics space
                if hasattr(simulator, 'reset_physics'):
                    simulator.reset_physics()
                    return True

                # Reduce physics complexity
                if hasattr(simulator, 'reduce_physics_complexity'):
                    simulator.reduce_physics_complexity()
                    return True

            except Exception as e:
                self.logger.error(f"Physics recovery failed: {e}")

        return False

    def _recover_from_config_error(self, error: ConfigurationError,
                                  context: Dict[str, Any]) -> bool:
        """Recover from configuration error."""
        self.logger.info("Attempting configuration recovery...")

        # Strategy: Load default configuration
        try:
            if 'config_manager' in context:
                config_manager = context['config_manager']
                config_type = error.context.get('config_type')

                if config_type and hasattr(config_manager, 'load_default_config'):
                    config_manager.load_default_config(config_type)
                    return True

        except Exception as e:
            self.logger.error(f"Configuration recovery failed: {e}")

        return False

    def _recover_from_control_error(self, error: RobotControlError,
                                   context: Dict[str, Any]) -> bool:
        """Recover from robot control error."""
        self.logger.info("Attempting control system recovery...")

        if 'robot' in context:
            robot = context['robot']
            try:
                # Reset robot control state
                robot.stop()
                robot.clear_command_queue()

                # Reinitialize control system
                if hasattr(robot, 'reinitialize_control'):
                    robot.reinitialize_control()

                return True
            except Exception as e:
                self.logger.error(f"Control recovery failed: {e}")

        return False

    def _recover_from_visualization_error(self, error: VisualizationError,
                                         context: Dict[str, Any]) -> bool:
        """Recover from visualization error."""
        self.logger.info("Attempting visualization recovery...")

        # Strategy: Disable problematic rendering features
        if 'renderer' in context:
            renderer = context['renderer']
            try:
                # Reduce rendering quality
                if hasattr(renderer, 'reduce_quality'):
                    renderer.reduce_quality()
                    return True

                # Disable debug rendering
                if hasattr(renderer, 'disable_debug_rendering'):
                    renderer.disable_debug_rendering()
                    return True

            except Exception as e:
                self.logger.error(f"Visualization recovery failed: {e}")

        return False

    def _recover_from_plugin_error(self, error: PluginError,
                                  context: Dict[str, Any]) -> bool:
        """Recover from plugin error."""
        self.logger.info("Attempting plugin recovery...")

        plugin_name = error.context.get('plugin_name')
        if plugin_name and 'plugin_manager' in context:
            try:
                plugin_manager = context['plugin_manager']

                # Disable problematic plugin
                if hasattr(plugin_manager, 'disable_plugin'):
                    plugin_manager.disable_plugin(plugin_name)
                    return True

            except Exception as e:
                self.logger.error(f"Plugin recovery failed: {e}")

        return False

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics and patterns."""
        if not self.error_history:
            return {'total_errors': 0}

        # Count errors by type
        error_counts = {}
        severity_counts = {}

        for error_record in self.error_history:
            error_type = error_record['error_type']
            severity = error_record['severity']

            error_counts[error_type] = error_counts.get(error_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            'total_errors': len(self.error_history),
            'error_counts': error_counts,
            'severity_counts': severity_counts,
            'recent_errors': self.error_history[-10:]  # Last 10 errors
        }

    def clear_error_history(self):
        """Clear the error history."""
        self.error_history.clear()
        self.logger.info("Error history cleared")


class ErrorContext:
    """Context manager for error handling in simulation operations."""

    def __init__(self, operation_name: str,
                 recovery_manager: ErrorRecoveryManager,
                 simulation_context: Dict[str, Any]):
        self.operation_name = operation_name
        self.recovery_manager = recovery_manager
        self.simulation_context = simulation_context
        self.logger = FLLLogger('ErrorContext')

    def __enter__(self):
        self.logger.debug(f"Starting operation: {self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_value, traceback_obj):
        if exc_type is not None:
            # An exception occurred
            if issubclass(exc_type, SimulationError):
                # Handle simulation errors
                self.logger.warning(f"Simulation error in {self.operation_name}: {exc_value}")

                # Attempt recovery
                recovery_success = self.recovery_manager.handle_error(
                    exc_value, self.simulation_context
                )

                if recovery_success:
                    self.logger.info(f"Recovered from error in {self.operation_name}")
                    return True  # Suppress the exception
                else:
                    self.logger.error(f"Could not recover from error in {self.operation_name}")
                    return False  # Re-raise the exception
            else:
                # Handle unexpected errors
                self.logger.error(f"Unexpected error in {self.operation_name}: {exc_value}")

                # Convert to simulation error and attempt recovery
                sim_error = SimulationError(
                    f"Unexpected error in {self.operation_name}: {exc_value}",
                    ErrorSeverity.HIGH,
                    {'operation': self.operation_name, 'original_error': str(exc_value)}
                )

                recovery_success = self.recovery_manager.handle_error(
                    sim_error, self.simulation_context
                )

                return recovery_success
        else:
            self.logger.debug(f"Operation completed successfully: {self.operation_name}")
            return False
