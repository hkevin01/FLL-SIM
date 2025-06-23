"""
Mission system for FLL challenges.

This module defines missions that robots must complete during FLL competitions,
including scoring logic and progress tracking.
"""

import time
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field


class MissionType(Enum):
    """Types of FLL missions."""
    AREA_VISIT = "area_visit"           # Visit a specific area
    OBJECT_TRANSPORT = "object_transport"  # Move object to location
    BUTTON_PRESS = "button_press"       # Press a button/sensor
    LINE_FOLLOW = "line_follow"         # Follow a line
    COLOR_DETECTION = "color_detection"  # Detect specific colors
    PRECISION_PARKING = "precision_parking"  # Park in precise location
    OBSTACLE_NAVIGATION = "obstacle_navigation"  # Navigate around obstacles
    TIME_CHALLENGE = "time_challenge"   # Complete task within time limit
    CUSTOM = "custom"                   # Custom mission logic


class MissionStatus(Enum):
    """Mission completion status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class MissionCondition:
    """Condition that must be met for mission completion."""
    
    condition_type: str  # "robot_in_area", "object_in_area", "sensor_reading", etc.
    parameters: Dict[str, Any] = field(default_factory=dict)
    required: bool = True  # Must be true for mission completion
    duration: float = 0.0  # How long condition must be held (seconds)
    
    # Runtime state
    is_met: bool = False
    hold_start_time: Optional[float] = None


class Mission:
    """
    Represents a single mission in an FLL challenge.
    
    Missions track completion conditions, scoring, and provide
    feedback to the simulation system.
    """
    
    def __init__(self, name: str, description: str, mission_type: MissionType,
                 points: int = 0, time_limit: Optional[float] = None,
                 target_area: Optional[Tuple[float, float, float, float]] = None,
                 target_object: Optional[str] = None,
                 conditions: Optional[List[MissionCondition]] = None):
        """
        Initialize a mission.
        
        Args:
            name: Mission name
            description: Human-readable description
            mission_type: Type of mission
            points: Points awarded for completion
            time_limit: Time limit in seconds (None for no limit)
            target_area: Target area (x, y, width, height) for area-based missions
            target_object: Name of target object for object missions
            conditions: List of completion conditions
        """
        self.name = name
        self.description = description
        self.mission_type = mission_type
        self.points = points
        self.time_limit = time_limit
        self.target_area = target_area
        self.target_object = target_object
        
        # Mission state
        self.status = MissionStatus.NOT_STARTED
        self.progress = 0.0  # 0.0 to 1.0
        self.points_earned = 0
        self.start_time: Optional[float] = None
        self.completion_time: Optional[float] = None
        self.time_elapsed = 0.0
        
        # Conditions for completion
        self.conditions = conditions or []
        self._setup_default_conditions()
        
        # Event callbacks
        self.on_start: List[Callable] = []
        self.on_progress: List[Callable] = []
        self.on_complete: List[Callable] = []
        self.on_fail: List[Callable] = []
        
        # Mission-specific data
        self.data: Dict[str, Any] = {}
    
    def _setup_default_conditions(self):
        """Setup default conditions based on mission type."""
        if self.conditions:
            return  # Already have custom conditions
        
        if self.mission_type == MissionType.AREA_VISIT and self.target_area:
            self.conditions.append(MissionCondition(
                condition_type="robot_in_area",
                parameters={
                    "area": self.target_area,
                    "tolerance": 50.0  # mm
                },
                duration=2.0  # Must stay in area for 2 seconds
            ))
        
        elif self.mission_type == MissionType.OBJECT_TRANSPORT and self.target_object:
            self.conditions.append(MissionCondition(
                condition_type="object_in_area", 
                parameters={
                    "object_name": self.target_object,
                    "area": self.target_area,
                    "tolerance": 30.0
                },
                duration=1.0
            ))
        
        elif self.mission_type == MissionType.BUTTON_PRESS:
            self.conditions.append(MissionCondition(
                condition_type="touch_sensor_pressed",
                parameters={
                    "sensor_name": self.data.get("target_sensor", "touch_front"),
                    "press_count": self.data.get("required_presses", 1)
                }
            ))
        
        elif self.mission_type == MissionType.COLOR_DETECTION:
            self.conditions.append(MissionCondition(
                condition_type="color_detected",
                parameters={
                    "target_color": self.data.get("target_color", "red"),
                    "sensor_name": self.data.get("color_sensor", "color_down")
                },
                duration=1.0
            ))
    
    def start(self):
        """Start the mission."""
        if self.status != MissionStatus.NOT_STARTED:
            return
        
        self.status = MissionStatus.IN_PROGRESS
        self.start_time = time.time()
        self.time_elapsed = 0.0
        
        # Reset conditions
        for condition in self.conditions:
            condition.is_met = False
            condition.hold_start_time = None
        
        # Trigger callbacks
        for callback in self.on_start:
            callback(self)
    
    def update(self, dt: float, robot=None, game_map=None):
        """
        Update mission state and check completion conditions.
        
        Args:
            dt: Time delta in seconds
            robot: Robot instance for checking conditions
            game_map: Game map instance for checking conditions
        """
        if self.status != MissionStatus.IN_PROGRESS:
            return
        
        self.time_elapsed += dt
        
        # Check time limit
        if self.time_limit and self.time_elapsed >= self.time_limit:
            self.fail("Time limit exceeded")
            return
        
        # Check completion conditions
        self._check_conditions(robot, game_map, dt)
        
        # Update progress
        self._update_progress()
        
        # Check if all required conditions are met
        if self._all_conditions_met():
            self.complete()
    
    def _check_conditions(self, robot, game_map, dt: float):
        """Check all mission conditions."""
        current_time = time.time()
        
        for condition in self.conditions:
            # Check if condition is currently satisfied
            was_met = condition.is_met
            condition.is_met = self._evaluate_condition(condition, robot, game_map)
            
            # Handle duration requirements
            if condition.duration > 0:
                if condition.is_met and not was_met:
                    # Condition just became true - start timer
                    condition.hold_start_time = current_time
                elif condition.is_met and condition.hold_start_time:
                    # Check if held long enough
                    hold_duration = current_time - condition.hold_start_time
                    condition.is_met = hold_duration >= condition.duration
                elif not condition.is_met:
                    # Condition no longer met - reset timer
                    condition.hold_start_time = None
    
    def _evaluate_condition(self, condition: MissionCondition, robot, game_map) -> bool:
        """
        Evaluate a single mission condition.
        
        Args:
            condition: Condition to evaluate
            robot: Robot instance
            game_map: Game map instance
            
        Returns:
            True if condition is satisfied
        """
        condition_type = condition.condition_type
        params = condition.parameters
        
        if condition_type == "robot_in_area":
            return self._check_robot_in_area(robot, params)
        
        elif condition_type == "object_in_area":
            return self._check_object_in_area(game_map, params)
        
        elif condition_type == "touch_sensor_pressed":
            return self._check_touch_sensor(robot, params)
        
        elif condition_type == "color_detected":
            return self._check_color_detected(robot, params)
        
        elif condition_type == "distance_traveled":
            return self._check_distance_traveled(robot, params)
        
        elif condition_type == "custom":
            # Custom condition with user-provided function
            func = params.get("function")
            if func:
                return func(robot, game_map, params)
        
        return False
    
    def _check_robot_in_area(self, robot, params: Dict[str, Any]) -> bool:
        """Check if robot is in target area."""
        if not robot:
            return False
        
        area = params["area"]  # (x, y, width, height)
        tolerance = params.get("tolerance", 0.0)
        
        x, y, w, h = area
        min_x = x - w/2 - tolerance
        max_x = x + w/2 + tolerance
        min_y = y - h/2 - tolerance 
        max_y = y + h/2 + tolerance
        
        return (min_x <= robot.x <= max_x and 
                min_y <= robot.y <= max_y)
    
    def _check_object_in_area(self, game_map, params: Dict[str, Any]) -> bool:
        """Check if object is in target area."""
        # This would need to be implemented based on physics system
        # For now, return False as placeholder
        return False
    
    def _check_touch_sensor(self, robot, params: Dict[str, Any]) -> bool:
        """Check touch sensor state."""
        if not robot:
            return False
        
        sensor_name = params["sensor_name"]
        required_presses = params.get("press_count", 1)
        
        sensor = robot.get_sensor(sensor_name)
        if not sensor:
            return False
        
        return sensor.get_press_count() >= required_presses
    
    def _check_color_detected(self, robot, params: Dict[str, Any]) -> bool:
        """Check if specific color is detected."""
        if not robot:
            return False
        
        sensor_name = params["sensor_name"]
        target_color = params["target_color"]
        
        sensor = robot.get_sensor(sensor_name)
        if not sensor:
            return False
        
        # Convert target color name to sensor color enum
        from ..sensors.color_sensor import Color
        color_map = {
            "black": Color.BLACK,
            "blue": Color.BLUE,
            "green": Color.GREEN,
            "yellow": Color.YELLOW,
            "red": Color.RED,
            "white": Color.WHITE,
            "brown": Color.BROWN,
        }
        
        target_enum = color_map.get(target_color.lower())
        if not target_enum:
            return False
        
        return sensor.get_reading() == target_enum
    
    def _check_distance_traveled(self, robot, params: Dict[str, Any]) -> bool:
        """Check if robot has traveled minimum distance."""
        # This would need odometry tracking in the robot
        # For now, return False as placeholder
        return False
    
    def _update_progress(self):
        """Update mission progress based on conditions."""
        if not self.conditions:
            self.progress = 1.0 if self.status == MissionStatus.COMPLETED else 0.0
            return
        
        met_conditions = sum(1 for c in self.conditions if c.is_met and c.required)
        total_required = sum(1 for c in self.conditions if c.required)
        
        if total_required > 0:
            self.progress = met_conditions / total_required
        else:
            self.progress = 1.0
        
        # Trigger progress callbacks
        for callback in self.on_progress:
            callback(self)
    
    def _all_conditions_met(self) -> bool:
        """Check if all required conditions are met."""
        return all(c.is_met or not c.required for c in self.conditions)
    
    def complete(self):
        """Mark mission as completed."""
        if self.status != MissionStatus.IN_PROGRESS:
            return
        
        self.status = MissionStatus.COMPLETED
        self.completion_time = time.time()
        self.progress = 1.0
        self.points_earned = self.points
        
        # Trigger callbacks
        for callback in self.on_complete:
            callback(self)
    
    def fail(self, reason: str = ""):
        """Mark mission as failed."""
        if self.status != MissionStatus.IN_PROGRESS:
            return
        
        self.status = MissionStatus.FAILED
        self.completion_time = time.time()
        self.data["failure_reason"] = reason
        
        # Trigger callbacks
        for callback in self.on_fail:
            callback(self)
    
    def reset(self):
        """Reset mission to initial state."""
        self.status = MissionStatus.NOT_STARTED
        self.progress = 0.0
        self.points_earned = 0
        self.start_time = None
        self.completion_time = None
        self.time_elapsed = 0.0
        
        # Reset conditions
        for condition in self.conditions:
            condition.is_met = False
            condition.hold_start_time = None
    
    def add_condition(self, condition: MissionCondition):
        """Add a completion condition."""
        self.conditions.append(condition)
    
    def add_callback(self, event: str, callback: Callable):
        """Add an event callback."""
        if event == "start":
            self.on_start.append(callback)
        elif event == "progress":
            self.on_progress.append(callback)
        elif event == "complete":
            self.on_complete.append(callback)
        elif event == "fail":
            self.on_fail.append(callback)
    
    def get_status_text(self) -> str:
        """Get human-readable status text."""
        status_text = {
            MissionStatus.NOT_STARTED: "Not Started",
            MissionStatus.IN_PROGRESS: f"In Progress ({self.progress*100:.0f}%)",
            MissionStatus.COMPLETED: f"Completed ({self.points_earned} points)",
            MissionStatus.FAILED: "Failed",
            MissionStatus.TIMEOUT: "Timeout"
        }
        return status_text.get(self.status, "Unknown")
    
    def render(self, renderer):
        """Render mission visualization on the map."""
        if not self.target_area:
            return
        
        x, y, w, h = self.target_area
        
        # Choose color based on status
        if self.status == MissionStatus.COMPLETED:
            color = (0, 255, 0, 100)  # Green
        elif self.status == MissionStatus.IN_PROGRESS:
            color = (255, 255, 0, 100)  # Yellow
        elif self.status == MissionStatus.FAILED:
            color = (255, 0, 0, 100)  # Red
        else:
            color = (128, 128, 128, 100)  # Gray
        
        # Draw target area
        renderer.draw_rect(x, y, w, h, 0, color)
        
        # Draw mission info
        renderer.draw_text(
            f"{self.name} ({self.points} pts)",
            x, y - h/2 - 20,
            (255, 255, 255), size=12
        )
        
        if self.status == MissionStatus.IN_PROGRESS:
            renderer.draw_text(
                f"{self.progress*100:.0f}%",
                x, y + h/2 + 20,
                (255, 255, 255), size=10
            )
