"""
State Management System for Simulation Engine

Provides a comprehensive state machine that handles simulation states:
initialization, running, paused, stopped, error recovery.
"""

import time
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set

from src.fll_sim.utils.enhanced_errors import ErrorSeverity, SimulationError
from src.fll_sim.utils.logger import FLLLogger


class SimulationState(Enum):
    """Enumeration of possible simulation states."""
    UNINITIALIZED = auto()
    INITIALIZING = auto()
    INITIALIZED = auto()
    STARTING = auto()
    RUNNING = auto()
    PAUSING = auto()
    PAUSED = auto()
    RESUMING = auto()
    STOPPING = auto()
    STOPPED = auto()
    ERROR = auto()
    RECOVERING = auto()
    SHUTTING_DOWN = auto()
    SHUTDOWN = auto()


@dataclass
class StateTransition:
    """Represents a state transition with conditions and callbacks."""
    from_state: SimulationState
    to_state: SimulationState
    condition: Optional[Callable[[], bool]] = None
    pre_transition: Optional[Callable[[], bool]] = None
    post_transition: Optional[Callable[[], None]] = None
    timeout: Optional[float] = None


@dataclass
class StateInfo:
    """Information about current state."""
    state: SimulationState
    entry_time: float
    data: Dict[str, Any]
    previous_state: Optional[SimulationState] = None


class StateChangeError(SimulationError):
    """Error raised when state transition fails."""

    def __init__(self, from_state: SimulationState, to_state: SimulationState,
                 reason: str):
        context = {
            'from_state': from_state.name,
            'to_state': to_state.name,
            'reason': reason
        }
        message = (f"State transition failed: {from_state.name} -> "
                   f"{to_state.name}: {reason}")
        super().__init__(message, ErrorSeverity.HIGH, context)


class SimulationStateMachine:
    """State machine for managing simulation lifecycle."""

    def __init__(self):
        self.logger = FLLLogger('SimulationStateMachine')
        self.current_state = SimulationState.UNINITIALIZED
        self.state_info = StateInfo(
            state=SimulationState.UNINITIALIZED,
            entry_time=time.time(),
            data={}
        )

        # State transition table
        self.transitions: Dict[SimulationState, Set[SimulationState]] = {}
        self.transition_handlers: Dict[tuple, StateTransition] = {}

        # State event callbacks
        self.state_enter_callbacks: Dict[SimulationState, List[Callable]] = {}
        self.state_exit_callbacks: Dict[SimulationState, List[Callable]] = {}
        self.state_change_callbacks: List[Callable] = []

        # State history
        self.state_history: List[StateInfo] = []
        self.max_history_size = 100

        # Setup default transitions
        self._setup_default_transitions()

    def _setup_default_transitions(self):
        """Setup default state transitions."""
        # Define valid transitions
        valid_transitions = [
            # Initialization flow
            (SimulationState.UNINITIALIZED, SimulationState.INITIALIZING),
            (SimulationState.INITIALIZING, SimulationState.INITIALIZED),
            (SimulationState.INITIALIZING, SimulationState.ERROR),

            # Startup flow
            (SimulationState.INITIALIZED, SimulationState.STARTING),
            (SimulationState.STARTING, SimulationState.RUNNING),
            (SimulationState.STARTING, SimulationState.ERROR),

            # Runtime flow
            (SimulationState.RUNNING, SimulationState.PAUSING),
            (SimulationState.PAUSING, SimulationState.PAUSED),
            (SimulationState.PAUSED, SimulationState.RESUMING),
            (SimulationState.RESUMING, SimulationState.RUNNING),

            # Stopping flow
            (SimulationState.RUNNING, SimulationState.STOPPING),
            (SimulationState.PAUSED, SimulationState.STOPPING),
            (SimulationState.STOPPING, SimulationState.STOPPED),

            # Error handling
            (SimulationState.RUNNING, SimulationState.ERROR),
            (SimulationState.PAUSED, SimulationState.ERROR),
            (SimulationState.ERROR, SimulationState.RECOVERING),
            (SimulationState.RECOVERING, SimulationState.RUNNING),
            (SimulationState.RECOVERING, SimulationState.STOPPED),
            (SimulationState.RECOVERING, SimulationState.ERROR),

            # Shutdown flow
            (SimulationState.STOPPED, SimulationState.SHUTTING_DOWN),
            (SimulationState.ERROR, SimulationState.SHUTTING_DOWN),
            (SimulationState.SHUTTING_DOWN, SimulationState.SHUTDOWN),

            # Emergency transitions (can happen from any state)
            (SimulationState.INITIALIZING, SimulationState.SHUTTING_DOWN),
            (SimulationState.INITIALIZED, SimulationState.SHUTTING_DOWN),
            (SimulationState.STARTING, SimulationState.SHUTTING_DOWN),
            (SimulationState.RUNNING, SimulationState.SHUTTING_DOWN),
            (SimulationState.PAUSING, SimulationState.SHUTTING_DOWN),
            (SimulationState.PAUSED, SimulationState.SHUTTING_DOWN),
            (SimulationState.RESUMING, SimulationState.SHUTTING_DOWN),
            (SimulationState.STOPPING, SimulationState.SHUTTING_DOWN),
            (SimulationState.RECOVERING, SimulationState.SHUTTING_DOWN),
        ]

        # Register transitions
        for from_state, to_state in valid_transitions:
            self.add_transition(from_state, to_state)

    def add_transition(self, from_state: SimulationState,
                       to_state: SimulationState,
                       condition: Optional[Callable[[], bool]] = None,
                       pre_transition: Optional[Callable[[], bool]] = None,
                       post_transition: Optional[Callable[[], None]] = None,
                       timeout: Optional[float] = None):
        """Add a valid state transition."""
        if from_state not in self.transitions:
            self.transitions[from_state] = set()

        self.transitions[from_state].add(to_state)

        # Store transition handler
        transition = StateTransition(
            from_state=from_state,
            to_state=to_state,
            condition=condition,
            pre_transition=pre_transition,
            post_transition=post_transition,
            timeout=timeout
        )
        self.transition_handlers[(from_state, to_state)] = transition

        self.logger.debug(
            f"Added transition: {from_state.name} -> {to_state.name}"
        )

    def can_transition_to(self, target_state: SimulationState) -> bool:
        """Check if transition to target state is valid."""
        return (self.current_state in self.transitions and
                target_state in self.transitions[self.current_state])

    def transition_to(self, target_state: SimulationState,
                      force: bool = False, **kwargs) -> bool:
        """
        Transition to a new state.

        Args:
            target_state: The target state to transition to
            force: If True, bypass transition validation
            **kwargs: Additional data to pass to transition handlers

        Returns:
            True if transition was successful, False otherwise

        Raises:
            StateChangeError: If transition is invalid or fails
        """
        if not force and not self.can_transition_to(target_state):
            raise StateChangeError(
                self.current_state, target_state,
                "Invalid state transition"
            )

        # Get transition handler
        transition_key = (self.current_state, target_state)
        transition = self.transition_handlers.get(transition_key)

        self.logger.info(
            f"Transitioning: {self.current_state.name} -> {target_state.name}"
        )

        try:
            # Check transition condition
            if transition and transition.condition:
                if not transition.condition():
                    raise StateChangeError(
                        self.current_state, target_state,
                        "Transition condition not met"
                    )

            # Execute pre-transition callback
            if transition and transition.pre_transition:
                if not transition.pre_transition():
                    raise StateChangeError(
                        self.current_state, target_state,
                        "Pre-transition callback failed"
                    )

            # Call state exit callbacks
            self._call_state_callbacks(
                self.state_exit_callbacks, self.current_state
            )

            # Save current state to history
            self._save_to_history()

            # Update state
            previous_state = self.current_state
            self.current_state = target_state
            self.state_info = StateInfo(
                state=target_state,
                entry_time=time.time(),
                data=kwargs,
                previous_state=previous_state
            )

            # Call state enter callbacks
            self._call_state_callbacks(
                self.state_enter_callbacks, target_state
            )

            # Call state change callbacks
            for callback in self.state_change_callbacks:
                try:
                    callback(previous_state, target_state, self.state_info)
                except Exception as e:
                    self.logger.error(f"Error in state change callback: {e}")

            # Execute post-transition callback
            if transition and transition.post_transition:
                transition.post_transition()

            self.logger.info(
                f"Successfully transitioned to {target_state.name}"
            )
            return True

        except Exception as e:
            if isinstance(e, StateChangeError):
                raise
            else:
                raise StateChangeError(
                    self.current_state, target_state,
                    f"Transition failed: {e}"
                )

    def _call_state_callbacks(self,
                              callback_dict,
                              state: SimulationState):
        """Call callbacks for a specific state."""
        if state in callback_dict:
            for callback in callback_dict[state]:
                try:
                    callback(self.state_info)
                except Exception as e:
                    self.logger.error(
                        f"Error in state callback for {state.name}: {e}"
                    )

    def _save_to_history(self):
        """Save current state to history."""
        self.state_history.append(self.state_info)

        # Trim history if too large
        if len(self.state_history) > self.max_history_size:
            self.state_history = self.state_history[-self.max_history_size:]

    def add_state_enter_callback(self, state: SimulationState,
                                 callback: Callable):
        """Add callback for when entering a specific state."""
        if state not in self.state_enter_callbacks:
            self.state_enter_callbacks[state] = []
        self.state_enter_callbacks[state].append(callback)

    def add_state_exit_callback(self, state: SimulationState,
                                callback: Callable):
        """Add callback for when exiting a specific state."""
        if state not in self.state_exit_callbacks:
            self.state_exit_callbacks[state] = []
        self.state_exit_callbacks[state].append(callback)

    def add_state_change_callback(self, callback: Callable):
        """Add callback for any state change."""
        self.state_change_callbacks.append(callback)

    def get_current_state(self) -> SimulationState:
        """Get the current state."""
        return self.current_state

    def get_state_info(self) -> StateInfo:
        """Get current state information."""
        return self.state_info

    def get_time_in_state(self) -> float:
        """Get time elapsed in current state."""
        return time.time() - self.state_info.entry_time

    def get_state_history(self) -> List[StateInfo]:
        """Get state history."""
        return self.state_history.copy()

    def is_in_state(self, *states: SimulationState) -> bool:
        """Check if current state is one of the specified states."""
        return self.current_state in states

    def is_operational(self) -> bool:
        """Check if simulation is in an operational state."""
        return self.current_state in {
            SimulationState.RUNNING,
            SimulationState.PAUSED
        }

    def is_transitioning(self) -> bool:
        """Check if simulation is currently transitioning between states."""
        return self.current_state in {
            SimulationState.INITIALIZING,
            SimulationState.STARTING,
            SimulationState.PAUSING,
            SimulationState.RESUMING,
            SimulationState.STOPPING,
            SimulationState.RECOVERING,
            SimulationState.SHUTTING_DOWN
        }

    def has_error(self) -> bool:
        """Check if simulation is in error state."""
        return self.current_state == SimulationState.ERROR

    def reset(self):
        """Reset state machine to initial state."""
        self.logger.info("Resetting state machine")
        self.current_state = SimulationState.UNINITIALIZED
        self.state_info = StateInfo(
            state=SimulationState.UNINITIALIZED,
            entry_time=time.time(),
            data={}
        )
        # Don't clear history - keep for debugging


class SimulationStateManager:
    """High-level manager for simulation state operations."""

    def __init__(self):
        self.logger = FLLLogger('SimulationStateManager')
        self.state_machine = SimulationStateMachine()
        self.components: Dict[str, Any] = {}
        self.initialization_steps: List[Callable] = []
        self.shutdown_steps: List[Callable] = []

        # Setup state handlers
        self._setup_state_handlers()

    def _setup_state_handlers(self):
        """Setup state-specific handlers."""
        # Initialization handlers
        self.state_machine.add_state_enter_callback(
            SimulationState.INITIALIZING, self._handle_initialization
        )

        # Startup handlers
        self.state_machine.add_state_enter_callback(
            SimulationState.STARTING, self._handle_startup
        )

        # Shutdown handlers
        self.state_machine.add_state_enter_callback(
            SimulationState.SHUTTING_DOWN, self._handle_shutdown
        )

        # Error recovery handlers
        self.state_machine.add_state_enter_callback(
            SimulationState.RECOVERING, self._handle_error_recovery
        )

    def register_component(self, name: str, component: Any):
        """Register a simulation component."""
        self.components[name] = component
        self.logger.debug(f"Registered component: {name}")

    def add_initialization_step(self, step: Callable):
        """Add an initialization step."""
        self.initialization_steps.append(step)

    def add_shutdown_step(self, step: Callable):
        """Add a shutdown step."""
        self.shutdown_steps.append(step)

    def initialize(self) -> bool:
        """Initialize the simulation."""
        try:
            self.state_machine.transition_to(SimulationState.INITIALIZING)
            # Initialization logic is handled in _handle_initialization
            return self.state_machine.get_current_state() == SimulationState.INITIALIZED
        except StateChangeError as e:
            self.logger.error(f"Initialization failed: {e}")
            return False

    def start(self) -> bool:
        """Start the simulation."""
        try:
            if self.state_machine.get_current_state() == SimulationState.INITIALIZED:
                self.state_machine.transition_to(SimulationState.STARTING)
                # Startup logic is handled in _handle_startup
                return self.state_machine.get_current_state() == SimulationState.RUNNING
            else:
                self.logger.error("Cannot start simulation: not initialized")
                return False
        except StateChangeError as e:
            self.logger.error(f"Startup failed: {e}")
            return False

    def pause(self) -> bool:
        """Pause the simulation."""
        try:
            if self.state_machine.get_current_state() == SimulationState.RUNNING:
                self.state_machine.transition_to(SimulationState.PAUSING)
                self.state_machine.transition_to(SimulationState.PAUSED)
                return True
            else:
                self.logger.warning("Cannot pause: simulation not running")
                return False
        except StateChangeError as e:
            self.logger.error(f"Pause failed: {e}")
            return False

    def resume(self) -> bool:
        """Resume the simulation."""
        try:
            if self.state_machine.get_current_state() == SimulationState.PAUSED:
                self.state_machine.transition_to(SimulationState.RESUMING)
                self.state_machine.transition_to(SimulationState.RUNNING)
                return True
            else:
                self.logger.warning("Cannot resume: simulation not paused")
                return False
        except StateChangeError as e:
            self.logger.error(f"Resume failed: {e}")
            return False

    def stop(self) -> bool:
        """Stop the simulation."""
        try:
            current_state = self.state_machine.get_current_state()
            if current_state in {SimulationState.RUNNING, SimulationState.PAUSED}:
                self.state_machine.transition_to(SimulationState.STOPPING)
                self.state_machine.transition_to(SimulationState.STOPPED)
                return True
            else:
                self.logger.warning(f"Cannot stop from state: {current_state.name}")
                return False
        except StateChangeError as e:
            self.logger.error(f"Stop failed: {e}")
            return False

    def shutdown(self) -> bool:
        """Shutdown the simulation system."""
        try:
            self.state_machine.transition_to(SimulationState.SHUTTING_DOWN)
            # Shutdown logic is handled in _handle_shutdown
            return self.state_machine.get_current_state() == SimulationState.SHUTDOWN
        except StateChangeError as e:
            self.logger.error(f"Shutdown failed: {e}")
            return False

    def handle_error(self, error: SimulationError) -> bool:
        """Handle a simulation error."""
        try:
            self.logger.error(f"Handling simulation error: {error}")
            self.state_machine.transition_to(SimulationState.ERROR, error=error)

            # Attempt recovery
            self.state_machine.transition_to(SimulationState.RECOVERING)

            # Recovery logic is handled in _handle_error_recovery
            return not self.state_machine.has_error()
        except StateChangeError as e:
            self.logger.error(f"Error handling failed: {e}")
            return False

    def _handle_initialization(self, state_info):
        """Handle initialization state."""
        _ = state_info  # Unused parameter
        self.logger.info("Starting initialization...")

        try:
            for i, step in enumerate(self.initialization_steps):
                self.logger.debug(f"Executing initialization step {i+1}/{len(self.initialization_steps)}")
                step()

            # All initialization steps completed
            self.state_machine.transition_to(SimulationState.INITIALIZED)
            self.logger.info("Initialization completed successfully")

        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            self.state_machine.transition_to(SimulationState.ERROR, error=e)

    def _handle_startup(self, state_info):
        """Handle startup state."""
        _ = state_info  # Unused parameter
        self.logger.info("Starting simulation...")

        try:
            # Start all components
            for name, component in self.components.items():
                if hasattr(component, 'start'):
                    self.logger.debug(f"Starting component: {name}")
                    component.start()

            # Transition to running state
            self.state_machine.transition_to(SimulationState.RUNNING)
            self.logger.info("Simulation started successfully")

        except Exception as e:
            self.logger.error(f"Startup failed: {e}")
            self.state_machine.transition_to(SimulationState.ERROR, error=e)

    def _handle_shutdown(self, state_info):
        """Handle shutdown state."""
        _ = state_info  # Unused parameter
        self.logger.info("Shutting down simulation...")

        try:
            # Execute shutdown steps in reverse order
            for i, step in enumerate(reversed(self.shutdown_steps)):
                self.logger.debug(
                    f"Executing shutdown step {i+1}/{len(self.shutdown_steps)}"
                )
                step()

            # Stop all components
            for name, component in self.components.items():
                if hasattr(component, 'stop'):
                    self.logger.debug(f"Stopping component: {name}")
                    component.stop()

            # Transition to shutdown state
            self.state_machine.transition_to(SimulationState.SHUTDOWN)
            self.logger.info("Shutdown completed successfully")

        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")
            # Force transition to shutdown even if there are errors
            self.state_machine.transition_to(
                SimulationState.SHUTDOWN, force=True
            )

    def _handle_error_recovery(self, state_info: StateInfo):
        """Handle error recovery state."""
        self.logger.info("Attempting error recovery...")

        error = state_info.data.get('error')

        try:
            # Basic recovery strategy
            # 1. Reset components that support it
            for name, component in self.components.items():
                if hasattr(component, 'reset'):
                    self.logger.debug(f"Resetting component: {name}")
                    component.reset()

            # 2. Clear error conditions
            if hasattr(error, 'clear'):
                error.clear()

            # 3. Attempt to return to operational state
            self.state_machine.transition_to(SimulationState.STOPPED)
            self.logger.info("Error recovery completed")

        except Exception as e:
            self.logger.error(f"Error recovery failed: {e}")
            # Recovery failed, stay in error state
            self.state_machine.transition_to(
                SimulationState.ERROR, recovery_error=e
            )

    def get_status(self) -> Dict[str, Any]:
        """Get current simulation status."""
        state_info = self.state_machine.get_state_info()

        return {
            'current_state': state_info.state.name,
            'time_in_state': self.state_machine.get_time_in_state(),
            'previous_state': (
                state_info.previous_state.name
                if state_info.previous_state else None
            ),
            'is_operational': self.state_machine.is_operational(),
            'is_transitioning': self.state_machine.is_transitioning(),
            'has_error': self.state_machine.has_error(),
            'registered_components': list(self.components.keys()),
            'state_data': state_info.data
        }
