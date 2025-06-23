"""
Mission system for FLL challenges.

This module defines missions that robots must complete during FLL competitions,
including scoring logic and progress tracking. Inspired by real FLL competition
missions and Pybricks robot control patterns.
"""

import logging
import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)


class MissionType(Enum):
    """Types of FLL missions based on common FLL challenge patterns."""
    AREA_VISIT = "area_visit"                    # ✅ Visit a specific area
    OBJECT_TRANSPORT = "object_transport"        # ✅ Move object to location  
    BUTTON_PRESS = "button_press"               # ✅ Press a button/sensor
    LINE_FOLLOW = "line_follow"                 # ✅ Follow a line
    COLOR_DETECTION = "color_detection"         # ✅ Detect specific colors
    PRECISION_PARKING = "precision_parking"     # ✅ Park in precise location
    OBSTACLE_NAVIGATION = "obstacle_navigation" # ✅ Navigate around obstacles
    TIME_CHALLENGE = "time_challenge"           # ✅ Complete task within time limit
    DISTANCE_ACCURACY = "distance_accuracy"     # ✅ Travel exact distance
    ANGLE_ACCURACY = "angle_accuracy"           # ✅ Turn to exact angle
    SENSOR_THRESHOLD = "sensor_threshold"       # ✅ Sensor reading above/below value
    SEQUENCE_COMPLETION = "sequence_completion" # ✅ Complete ordered sequence
    SPEED_CONTROL = "speed_control"             # ✅ Maintain specific speed
    ENERGY_EFFICIENCY = "energy_efficiency"     # ✅ Complete with minimal energy
    CUSTOM = "custom"                           # ✅ Custom mission logic


class MissionStatus(Enum):
    """Mission completion status."""
    NOT_STARTED = "not_started"    # ❌ Mission not yet attempted
    IN_PROGRESS = "in_progress"    # 🚧 Mission currently being attempted
    COMPLETED = "completed"        # ✅ Mission successfully completed
    FAILED = "failed"              # ❌ Mission failed (conditions not met)
    TIMEOUT = "timeout"            # ⏰ Mission timed out
    BONUS_ACHIEVED = "bonus"       # 🌟 Mission completed with bonus points


class MissionDifficulty(Enum):
    """Mission difficulty levels affecting scoring."""
    BEGINNER = "beginner"      # 5-10 points
    INTERMEDIATE = "intermediate"  # 15-25 points
    ADVANCED = "advanced"      # 30-50 points
    EXPERT = "expert"          # 60+ points


@dataclass
class MissionCondition:
    """
    Condition that must be met for mission completion.
    
    Examples:
    - Robot position in area: {"type": "robot_in_area", "area": {"x": 100, "y": 200, "radius": 50}}
    - Object moved: {"type": "object_moved", "object_id": "cube1", "target": {"x": 300, "y": 400}}
    - Sensor reading: {"type": "sensor_reading", "sensor": "color", "value": "red", "operator": "equals"}
    """
    
    condition_type: str  # Type of condition to check
    parameters: Dict[str, Any] = field(default_factory=dict)  # Condition parameters
    required: bool = True  # Must be true for mission completion
    duration: float = 0.0  # How long condition must be held (seconds)
    tolerance: float = 0.0  # Tolerance for numeric comparisons
    
    # Runtime state
    is_met: bool = False
    hold_start_time: Optional[float] = None
    first_met_time: Optional[float] = None
    
    def reset(self):
        """Reset condition state."""
        self.is_met = False
        self.hold_start_time = None
        self.first_met_time = None


@dataclass
class MissionReward:
    """Reward structure for mission completion."""
    
    base_points: int = 10                    # Base points for completion
    bonus_points: int = 0                    # Bonus points for excellence
    time_bonus: bool = False                 # Award bonus for fast completion
    efficiency_bonus: bool = False           # Award bonus for energy efficiency
    precision_bonus: bool = False            # Award bonus for precision
    
    # Time-based scoring
    target_time: Optional[float] = None      # Target completion time (seconds)
    time_penalty: float = 0.0                # Points lost per second over target
    
    # Efficiency scoring
    max_energy: Optional[float] = None       # Maximum allowed energy usage
    energy_penalty: float = 0.0              # Points lost per unit over max
    
    # Multipliers
    difficulty_multiplier: float = 1.0       # Multiply by difficulty
    first_attempt_multiplier: float = 1.2   # Bonus for first attempt success


@dataclass  
class MissionHint:
    """Helpful hints for mission completion."""
    
    strategy: str = ""                       # Suggested strategy
    common_mistakes: List[str] = field(default_factory=list)  # Things to avoid
    tips: List[str] = field(default_factory=list)  # Helpful tips
    reference_code: Optional[str] = None     # Example code snippet


class Mission:
    """
    FLL Mission representing a specific challenge task.
    
    Based on real FLL competition missions like:
    - SUBMERGED (2024): Coral Nursery, Shark, Kraken, etc.
    - CARGO CONNECT (2023): Transportation missions
    - REPLAY (2020): Innovative sports missions
    """
    
    def __init__(
        self,
        mission_id: str,
        name: str,
        description: str,
        mission_type: MissionType,
        conditions: List[MissionCondition],
        reward: MissionReward,
        difficulty: MissionDifficulty = MissionDifficulty.INTERMEDIATE,
        time_limit: Optional[float] = None,
        prerequisite_missions: Optional[List[str]] = None,
        hint: Optional[MissionHint] = None,
        fll_season: str = "2024-SUBMERGED"
    ):
        """
        Initialize a new mission.
        
        Args:
            mission_id: Unique identifier for this mission
            name: Human-readable mission name
            description: Detailed mission description
            mission_type: Type of mission
            conditions: List of conditions that must be met
            reward: Point values and bonuses
            difficulty: Mission difficulty level
            time_limit: Maximum time allowed (seconds)
            prerequisite_missions: Required completed missions
            hint: Helpful information for students
            fll_season: FLL season this mission belongs to
        """
        self.mission_id = mission_id
        self.name = name
        self.description = description
        self.mission_type = mission_type
        self.conditions = conditions
        self.reward = reward
        self.difficulty = difficulty
        self.time_limit = time_limit
        self.prerequisite_missions = prerequisite_missions or []
        self.hint = hint
        self.fll_season = fll_season
        
        # Runtime state
        self.status = MissionStatus.NOT_STARTED
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.attempt_count = 0
        self.total_energy_used = 0.0
        self.max_speed_achieved = 0.0
        self.completion_time: Optional[float] = None
        self.score = 0
        
        # Event callbacks
        self.on_start: Optional[Callable] = None
        self.on_complete: Optional[Callable] = None
        self.on_fail: Optional[Callable] = None
        
        # Performance metrics
        self.precision_score = 0.0  # How precisely mission was completed
        self.efficiency_score = 0.0  # Energy/time efficiency
        self.style_score = 0.0      # Elegance of solution
        
        # AI training data
        self.robot_path: List[Tuple[float, float, float]] = []  # x, y, timestamp
        self.sensor_data: List[Dict[str, Any]] = []
        self.decision_points: List[Dict[str, Any]] = []
        
        logger.info(f"Created mission: {self.name} ({self.mission_id})")

    def start(self) -> bool:
        """
        Start the mission.
        
        Returns:
            True if mission started successfully, False if prerequisites not met
        """
        if self.status != MissionStatus.NOT_STARTED:
            logger.warning(f"Mission {self.name} already started or completed")
            return False
            
        # Check prerequisites
        if not self._check_prerequisites():
            logger.error(f"Prerequisites not met for mission {self.name}")
            return False
            
        self.status = MissionStatus.IN_PROGRESS
        self.start_time = time.time()
        self.attempt_count += 1
        
        # Reset all conditions
        for condition in self.conditions:
            condition.reset()
            
        # Reset tracking data
        self.robot_path.clear()
        self.sensor_data.clear()
        self.decision_points.clear()
        
        if self.on_start:
            self.on_start(self)
            
        logger.info(f"Mission {self.name} started (attempt #{self.attempt_count})")
        return True

    def update(self, robot_state: Dict[str, Any], environment_state: Dict[str, Any]) -> None:
        """
        Update mission progress based on current robot and environment state.
        
        Args:
            robot_state: Current robot position, sensors, etc.
            environment_state: Current environment objects, etc.
        """
        if self.status != MissionStatus.IN_PROGRESS:
            return
            
        current_time = time.time()
        
        # Check time limit
        if self.time_limit and (current_time - self.start_time) > self.time_limit:
            self._fail_mission(MissionStatus.TIMEOUT)
            return
            
        # Record robot path for AI training
        if 'position' in robot_state:
            pos = robot_state['position']
            self.robot_path.append((pos['x'], pos['y'], current_time))
            
        # Record sensor data
        if 'sensors' in robot_state:
            sensor_snapshot = {
                'timestamp': current_time,
                'sensors': robot_state['sensors'].copy()
            }
            self.sensor_data.append(sensor_snapshot)
            
        # Update energy tracking
        if 'energy_used' in robot_state:
            self.total_energy_used = robot_state['energy_used']
            
        # Update max speed
        if 'speed' in robot_state:
            self.max_speed_achieved = max(self.max_speed_achieved, robot_state['speed'])
            
        # Check all conditions
        all_required_met = True
        for condition in self.conditions:
            was_met = condition.is_met
            condition.is_met = self._check_condition(condition, robot_state, environment_state)
            
            # Track first time condition was met
            if condition.is_met and not was_met:
                condition.first_met_time = current_time
                
            # Handle duration requirements
            if condition.duration > 0:
                if condition.is_met:
                    if condition.hold_start_time is None:
                        condition.hold_start_time = current_time
                    elif (current_time - condition.hold_start_time) < condition.duration:
                        # Still need to hold longer
                        if condition.required:
                            all_required_met = False
                else:
                    condition.hold_start_time = None
                    if condition.required:
                        all_required_met = False
            else:
                # No duration requirement
                if condition.required and not condition.is_met:
                    all_required_met = False
                    
        # Check for mission completion
        if all_required_met:
            self._complete_mission()

    def _check_condition(self, condition: MissionCondition, robot_state: Dict[str, Any], 
                        environment_state: Dict[str, Any]) -> bool:
        """Check if a specific condition is currently met."""
        
        try:
            condition_type = condition.condition_type
            params = condition.parameters
            tolerance = condition.tolerance
            
            if condition_type == "robot_in_area":
                return self._check_robot_in_area(robot_state, params, tolerance)
                
            elif condition_type == "robot_at_position":
                return self._check_robot_at_position(robot_state, params, tolerance)
                
            elif condition_type == "object_in_area":
                return self._check_object_in_area(environment_state, params, tolerance)
                
            elif condition_type == "sensor_reading":
                return self._check_sensor_reading(robot_state, params, tolerance)
                
            elif condition_type == "distance_traveled":
                return self._check_distance_traveled(robot_state, params, tolerance)
                
            elif condition_type == "angle_achieved":
                return self._check_angle_achieved(robot_state, params, tolerance)
                
            elif condition_type == "speed_maintained":
                return self._check_speed_maintained(robot_state, params, tolerance)
                
            elif condition_type == "time_elapsed":
                return self._check_time_elapsed(params, tolerance)
                
            elif condition_type == "energy_limit":
                return self._check_energy_limit(robot_state, params, tolerance)
                
            elif condition_type == "sequence_completed":
                return self._check_sequence_completed(robot_state, environment_state, params)
                
            elif condition_type == "custom":
                # Custom condition with user-provided function
                custom_func = params.get('function')
                if custom_func and callable(custom_func):
                    return custom_func(robot_state, environment_state, params)
                    
            else:
                logger.warning(f"Unknown condition type: {condition_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error checking condition {condition_type}: {e}")
            return False
            
    def _check_robot_in_area(self, robot_state: Dict[str, Any], params: Dict[str, Any], 
                           tolerance: float) -> bool:
        """Check if robot is within specified area."""
        if 'position' not in robot_state:
            return False
            
        pos = robot_state['position']
        robot_x, robot_y = pos['x'], pos['y']
        
        if 'circle' in params:
            # Circular area
            circle = params['circle']
            center_x, center_y = circle['x'], circle['y']
            radius = circle['radius'] + tolerance
            
            distance = math.sqrt((robot_x - center_x)**2 + (robot_y - center_y)**2)
            return distance <= radius
            
        elif 'rectangle' in params:
            # Rectangular area
            rect = params['rectangle']
            left = rect['x'] - rect['width']/2 - tolerance
            right = rect['x'] + rect['width']/2 + tolerance
            top = rect['y'] - rect['height']/2 - tolerance
            bottom = rect['y'] + rect['height']/2 + tolerance
            
            return left <= robot_x <= right and top <= robot_y <= bottom
            
        return False

    def _check_robot_at_position(self, robot_state: Dict[str, Any], params: Dict[str, Any],
                                tolerance: float) -> bool:
        """Check if robot is at specific position."""
        if 'position' not in robot_state:
            return False
            
        pos = robot_state['position']
        robot_x, robot_y = pos['x'], pos['y']
        target_x, target_y = params['x'], params['y']
        
        distance = math.sqrt((robot_x - target_x)**2 + (robot_y - target_y)**2)
        return distance <= (params.get('tolerance', 10.0) + tolerance)

    def _check_object_in_area(self, environment_state: Dict[str, Any], params: Dict[str, Any],
                            tolerance: float) -> bool:
        """Check if specified object is in target area."""
        objects = environment_state.get('objects', {})
        object_id = params['object_id']
        
        if object_id not in objects:
            return False
            
        obj = objects[object_id]
        obj_x, obj_y = obj['x'], obj['y']
        
        target_area = params['target_area']
        if 'circle' in target_area:
            circle = target_area['circle']
            center_x, center_y = circle['x'], circle['y']
            radius = circle['radius'] + tolerance
            
            distance = math.sqrt((obj_x - center_x)**2 + (obj_y - center_y)**2)
            return distance <= radius
            
        return False

    def _check_sensor_reading(self, robot_state: Dict[str, Any], params: Dict[str, Any],
                            tolerance: float) -> bool:
        """Check sensor reading against expected value."""
        sensors = robot_state.get('sensors', {})
        sensor_name = params['sensor']
        
        if sensor_name not in sensors:
            return False
            
        sensor_value = sensors[sensor_name]
        expected_value = params['value']
        operator = params.get('operator', 'equals')
        
        if operator == 'equals':
            if isinstance(expected_value, str):
                return sensor_value == expected_value
            else:
                return abs(sensor_value - expected_value) <= (params.get('tolerance', 0.1) + tolerance)
                
        elif operator == 'greater_than':
            return sensor_value > (expected_value - tolerance)
            
        elif operator == 'less_than':
            return sensor_value < (expected_value + tolerance)
            
        elif operator == 'in_range':
            min_val, max_val = expected_value
            return (min_val - tolerance) <= sensor_value <= (max_val + tolerance)
            
        return False

    def _check_distance_traveled(self, robot_state: Dict[str, Any], params: Dict[str, Any],
                               tolerance: float) -> bool:
        """Check if robot has traveled required distance."""
        distance_traveled = robot_state.get('distance_traveled', 0.0)
        required_distance = params['distance']
        
        return abs(distance_traveled - required_distance) <= (params.get('tolerance', 5.0) + tolerance)

    def _check_angle_achieved(self, robot_state: Dict[str, Any], params: Dict[str, Any],
                            tolerance: float) -> bool:
        """Check if robot has achieved required angle."""
        if 'position' not in robot_state:
            return False
            
        current_angle = robot_state['position'].get('angle', 0.0)
        target_angle = params['angle']
        
        # Normalize angles to [-180, 180]
        angle_diff = ((current_angle - target_angle + 180) % 360) - 180
        
        return abs(angle_diff) <= (params.get('tolerance', 2.0) + tolerance)

    def _check_speed_maintained(self, robot_state: Dict[str, Any], params: Dict[str, Any],
                              tolerance: float) -> bool:
        """Check if robot maintains required speed."""
        current_speed = robot_state.get('speed', 0.0)
        target_speed = params['speed']
        speed_tolerance = params.get('tolerance', 5.0) + tolerance
        
        return abs(current_speed - target_speed) <= speed_tolerance

    def _check_time_elapsed(self, params: Dict[str, Any], tolerance: float) -> bool:
        """Check if required time has elapsed."""
        if self.start_time is None:
            return False
            
        elapsed = time.time() - self.start_time
        required_time = params['time']
        
        return elapsed >= (required_time - tolerance)

    def _check_energy_limit(self, robot_state: Dict[str, Any], params: Dict[str, Any],
                          tolerance: float) -> bool:
        """Check if energy usage is within limit."""
        energy_used = robot_state.get('energy_used', 0.0)
        energy_limit = params['limit']
        
        return energy_used <= (energy_limit + tolerance)

    def _check_sequence_completed(self, robot_state: Dict[str, Any], 
                                environment_state: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """Check if required sequence of actions was completed."""
        # This would require more complex state tracking
        # For now, return simple implementation
        completed_sequence = robot_state.get('completed_sequence', [])
        required_sequence = params['sequence']
        
        return len(completed_sequence) >= len(required_sequence)

    def _check_prerequisites(self) -> bool:
        """Check if all prerequisite missions are completed."""
        # This would be implemented by the mission manager
        # For now, always return True
        return True

    def _complete_mission(self) -> None:
        """Complete the mission and calculate score."""
        if self.status != MissionStatus.IN_PROGRESS:
            return
            
        self.status = MissionStatus.COMPLETED
        self.end_time = time.time()
        self.completion_time = self.end_time - self.start_time
        
        # Calculate score
        self.score = self._calculate_score()
        
        # Calculate performance metrics
        self._calculate_performance_metrics()
        
        if self.on_complete:
            self.on_complete(self)
            
        logger.info(f"Mission {self.name} completed! Score: {self.score} points")

    def _fail_mission(self, failure_status: MissionStatus = MissionStatus.FAILED) -> None:
        """Fail the mission."""
        if self.status != MissionStatus.IN_PROGRESS:
            return
            
        self.status = failure_status
        self.end_time = time.time()
        self.score = 0  # No points for failed missions
        
        if self.on_fail:
            self.on_fail(self)
            
        logger.info(f"Mission {self.name} failed with status: {failure_status.value}")

    def _calculate_score(self) -> int:
        """Calculate mission score based on completion and performance."""
        if self.status != MissionStatus.COMPLETED:
            return 0
            
        # Base score
        score = self.reward.base_points
        
        # Apply difficulty multiplier
        score = int(score * self.reward.difficulty_multiplier)
        
        # Time bonus
        if self.reward.time_bonus and self.reward.target_time and self.completion_time:
            if self.completion_time <= self.reward.target_time:
                score += self.reward.bonus_points
            else:
                # Time penalty
                overtime = self.completion_time - self.reward.target_time
                penalty = int(overtime * self.reward.time_penalty)
                score = max(0, score - penalty)
                
        # Efficiency bonus
        if self.reward.efficiency_bonus and self.reward.max_energy:
            if self.total_energy_used <= self.reward.max_energy:
                score += int(self.reward.bonus_points * 0.5)
                
        # First attempt bonus
        if self.attempt_count == 1:
            score = int(score * self.reward.first_attempt_multiplier)
            
        # Precision bonus
        if self.reward.precision_bonus and self.precision_score > 0.8:
            score += int(self.reward.bonus_points * 0.3)
            
        return max(0, score)

    def _calculate_performance_metrics(self) -> None:
        """Calculate detailed performance metrics for analysis."""
        if not self.robot_path or self.completion_time is None:
            return
            
        # Calculate precision score (how close to optimal path)
        self.precision_score = self._calculate_precision_score()
        
        # Calculate efficiency score (energy and time efficiency)
        self.efficiency_score = self._calculate_efficiency_score()
        
        # Calculate style score (smoothness of movement)
        self.style_score = self._calculate_style_score()

    def _calculate_precision_score(self) -> float:
        """Calculate how precisely the mission was completed (0.0 to 1.0)."""
        # Simplified implementation - would be mission-specific
        # Could analyze deviation from optimal path, accuracy of final position, etc.
        return 0.85  # Placeholder

    def _calculate_efficiency_score(self) -> float:
        """Calculate efficiency score based on time and energy usage."""
        if self.completion_time is None:
            return 0.0
            
        # Time efficiency
        time_efficiency = 1.0
        if self.reward.target_time:
            time_efficiency = min(1.0, self.reward.target_time / self.completion_time)
            
        # Energy efficiency  
        energy_efficiency = 1.0
        if self.reward.max_energy and self.total_energy_used > 0:
            energy_efficiency = min(1.0, self.reward.max_energy / self.total_energy_used)
            
        return (time_efficiency + energy_efficiency) / 2.0

    def _calculate_style_score(self) -> float:
        """Calculate style score based on smoothness of robot movement."""
        if len(self.robot_path) < 3:
            return 0.0
            
        # Analyze path smoothness by looking at direction changes
        direction_changes = 0
        for i in range(1, len(self.robot_path) - 1):
            prev_point = self.robot_path[i-1]
            curr_point = self.robot_path[i]
            next_point = self.robot_path[i+1]
            
            # Calculate angles
            angle1 = math.atan2(curr_point[1] - prev_point[1], curr_point[0] - prev_point[0])
            angle2 = math.atan2(next_point[1] - curr_point[1], next_point[0] - curr_point[0])
            
            # Check for significant direction change
            angle_diff = abs(angle2 - angle1)
            if angle_diff > math.pi:
                angle_diff = 2 * math.pi - angle_diff
                
            if angle_diff > math.pi / 4:  # 45 degree threshold
                direction_changes += 1
                
        # Fewer direction changes = higher style score
        max_changes = len(self.robot_path) // 5  # Allow some direction changes
        style_score = max(0.0, 1.0 - (direction_changes / max(1, max_changes)))
        
        return style_score

    def get_progress_summary(self) -> Dict[str, Any]:
        """Get detailed progress summary for the mission."""
        return {
            'mission_id': self.mission_id,
            'name': self.name,
            'status': self.status.value,
            'score': self.score,
            'attempt_count': self.attempt_count,
            'completion_time': self.completion_time,
            'energy_used': self.total_energy_used,
            'precision_score': self.precision_score,
            'efficiency_score': self.efficiency_score,
            'style_score': self.style_score,
            'conditions': [
                {
                    'type': condition.condition_type,
                    'is_met': condition.is_met,
                    'required': condition.required,
                    'first_met_time': condition.first_met_time
                }
                for condition in self.conditions
            ],
            'robot_path_length': len(self.robot_path),
            'sensor_data_points': len(self.sensor_data)
        }

    def reset(self) -> None:
        """Reset mission to initial state."""
        self.status = MissionStatus.NOT_STARTED
        self.start_time = None
        self.end_time = None
        self.completion_time = None
        self.score = 0
        self.total_energy_used = 0.0
        self.max_speed_achieved = 0.0
        
        # Reset all conditions
        for condition in self.conditions:
            condition.reset()
            
        # Clear tracking data
        self.robot_path.clear()
        self.sensor_data.clear()
        self.decision_points.clear()
        
        # Reset performance metrics
        self.precision_score = 0.0
        self.efficiency_score = 0.0
        self.style_score = 0.0
        
        logger.info(f"Mission {self.name} reset to initial state")

    def __repr__(self) -> str:
        return f"Mission(id='{self.mission_id}', name='{self.name}', status='{self.status.value}', score={self.score})"
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


class FLLMissionFactory:
    """Factory for creating standard FLL missions based on real competition challenges."""
    
    @staticmethod
    def create_submerged_2024_missions() -> List[Mission]:
        """Create missions from the 2024 SUBMERGED season."""
        missions = []
        
        # Mission 1: Coral Nursery (Beginner)
        coral_nursery = Mission(
            mission_id="coral_nursery",
            name="Coral Nursery",
            description="Transport coral samples to the nursery area for cultivation",
            mission_type=MissionType.OBJECT_TRANSPORT,
            conditions=[
                MissionCondition(
                    condition_type="object_in_area",
                    parameters={
                        "object_id": "coral_sample",
                        "target_area": {
                            "circle": {"x": 1800, "y": 900, "radius": 100}
                        }
                    },
                    duration=2.0  # Must stay in area for 2 seconds
                )
            ],
            reward=MissionReward(
                base_points=20,
                bonus_points=10,
                time_bonus=True,
                target_time=30.0,
                first_attempt_multiplier=1.3
            ),
            difficulty=MissionDifficulty.BEGINNER,
            time_limit=120.0,
            hint=MissionHint(
                strategy="Use precise movements to carefully transport coral without dropping it",
                tips=[
                    "Approach the coral slowly to avoid knocking it over",
                    "Use the color sensor to detect the nursery area boundary",
                    "Gentle acceleration and deceleration are key"
                ],
                common_mistakes=[
                    "Moving too fast and losing the coral",
                    "Not centering the coral in the target area",
                    "Forgetting to wait for the 2-second confirmation"
                ]
            ),
            fll_season="2024-SUBMERGED"
        )
        missions.append(coral_nursery)
        
        # Mission 2: Shark (Intermediate)
        shark_mission = Mission(
            mission_id="shark_protection",
            name="Shark Protection",
            description="Guide the shark to safe waters while avoiding obstacles",
            mission_type=MissionType.OBSTACLE_NAVIGATION,
            conditions=[
                MissionCondition(
                    condition_type="robot_in_area",
                    parameters={
                        "circle": {"x": 600, "y": 600, "radius": 80}
                    },
                    required=True
                ),
                MissionCondition(
                    condition_type="object_in_area", 
                    parameters={
                        "object_id": "shark",
                        "target_area": {
                            "rectangle": {"x": 500, "y": 500, "width": 200, "height": 150}
                        }
                    },
                    required=True,
                    duration=3.0
                )
            ],
            reward=MissionReward(
                base_points=35,
                bonus_points=15,
                precision_bonus=True,
                efficiency_bonus=True,
                target_time=45.0,
                max_energy=50.0
            ),
            difficulty=MissionDifficulty.INTERMEDIATE,
            time_limit=90.0,
            hint=MissionHint(
                strategy="Use ultrasonic sensor to navigate around obstacles while guiding shark",
                tips=[
                    "Maintain safe distance from obstacles",
                    "Use smooth movements to guide shark naturally",
                    "Monitor energy usage to earn efficiency bonus"
                ],
                common_mistakes=[
                    "Colliding with underwater obstacles",
                    "Losing track of shark position",
                    "Using too much energy with aggressive movements"
                ]
            ),
            fll_season="2024-SUBMERGED"
        )
        missions.append(shark_mission)
        
        # Mission 3: Kraken Adventure (Advanced)
        kraken_mission = Mission(
            mission_id="kraken_adventure",
            name="Kraken Adventure",
            description="Navigate through the kraken's tentacles to reach the treasure",
            mission_type=MissionType.PRECISION_PARKING,
            conditions=[
                MissionCondition(
                    condition_type="robot_at_position",
                    parameters={"x": 1200, "y": 400, "tolerance": 15.0}
                ),
                MissionCondition(
                    condition_type="angle_achieved",
                    parameters={"angle": 90.0, "tolerance": 5.0}
                ),
                MissionCondition(
                    condition_type="sensor_reading",
                    parameters={
                        "sensor": "color",
                        "value": "blue",
                        "operator": "equals"
                    }
                )
            ],
            reward=MissionReward(
                base_points=50,
                bonus_points=25,
                precision_bonus=True,
                time_bonus=True,
                target_time=60.0,
                time_penalty=0.5
            ),
            difficulty=MissionDifficulty.ADVANCED,
            time_limit=120.0,
            prerequisite_missions=["coral_nursery"],
            hint=MissionHint(
                strategy="Use precise navigation and color detection to reach exact position",
                tips=[
                    "Approach slowly for maximum precision",
                    "Use gyro sensor for accurate angle alignment",
                    "Color sensor must detect blue treasure marker"
                ],
                common_mistakes=[
                    "Final position not precise enough",
                    "Wrong final orientation",
                    "Missing the color detection requirement"
                ],
                reference_code="""
# Example approach for precision parking
robot.straight(800)  # Approach treasure area
robot.turn(90)       # Turn to correct orientation
robot.straight(50)   # Fine positioning
# Check color sensor for blue
"""
            ),
            fll_season="2024-SUBMERGED"
        )
        missions.append(kraken_mission)
        
        # Mission 4: Speed Challenge (Expert)
        speed_mission = Mission(
            mission_id="underwater_speed",
            name="Underwater Speed Challenge", 
            description="Navigate underwater course at high speed while maintaining control",
            mission_type=MissionType.SPEED_CONTROL,
            conditions=[
                MissionCondition(
                    condition_type="speed_maintained",
                    parameters={"speed": 200.0, "tolerance": 20.0},
                    duration=10.0
                ),
                MissionCondition(
                    condition_type="distance_traveled",
                    parameters={"distance": 1500.0, "tolerance": 50.0}
                ),
                MissionCondition(
                    condition_type="robot_in_area",
                    parameters={
                        "rectangle": {"x": 2000, "y": 600, "width": 100, "height": 100}
                    }
                )
            ],
            reward=MissionReward(
                base_points=75,
                bonus_points=35,
                time_bonus=True,
                efficiency_bonus=True,
                target_time=20.0,
                max_energy=30.0,
                difficulty_multiplier=1.5
            ),
            difficulty=MissionDifficulty.EXPERT,
            time_limit=45.0,
            prerequisite_missions=["shark_protection", "kraken_adventure"],
            hint=MissionHint(
                strategy="Maintain high speed while navigating precisely to target area",
                tips=[
                    "Use PID control for speed regulation",
                    "Plan path to minimize direction changes",
                    "Energy efficiency is crucial at high speeds"
                ],
                common_mistakes=[
                    "Speed too variable during challenge",
                    "Overshooting the target area",
                    "Excessive energy usage at high speed"
                ]
            ),
            fll_season="2024-SUBMERGED"
        )
        missions.append(speed_mission)
        
        return missions
    
    @staticmethod
    def create_custom_mission(
        mission_id: str,
        name: str,
        description: str,
        custom_logic: Callable[[Dict[str, Any], Dict[str, Any]], bool],
        base_points: int = 25,
        time_limit: float = 60.0
    ) -> Mission:
        """Create a custom mission with user-defined logic."""
        
        return Mission(
            mission_id=mission_id,
            name=name,
            description=description,
            mission_type=MissionType.CUSTOM,
            conditions=[
                MissionCondition(
                    condition_type="custom",
                    parameters={"function": custom_logic}
                )
            ],
            reward=MissionReward(base_points=base_points),
            difficulty=MissionDifficulty.INTERMEDIATE,
            time_limit=time_limit,
            fll_season="CUSTOM"
        )
    
    @staticmethod
    def create_line_following_mission(
        mission_id: str = "line_follow_basic",
        line_color: str = "black",
        track_length: float = 1000.0,
        max_deviation: float = 50.0
    ) -> Mission:
        """Create a line following mission."""
        
        return Mission(
            mission_id=mission_id,
            name="Line Following Challenge",
            description=f"Follow the {line_color} line for {track_length}mm with max deviation {max_deviation}mm",
            mission_type=MissionType.LINE_FOLLOW,
            conditions=[
                MissionCondition(
                    condition_type="distance_traveled",
                    parameters={"distance": track_length, "tolerance": 30.0}
                ),
                MissionCondition(
                    condition_type="sensor_reading",
                    parameters={
                        "sensor": "color",
                        "value": line_color,
                        "operator": "equals"
                    },
                    duration=0.8  # 80% of the time
                )
            ],
            reward=MissionReward(
                base_points=30,
                bonus_points=15,
                precision_bonus=True,
                efficiency_bonus=True
            ),
            difficulty=MissionDifficulty.INTERMEDIATE,
            time_limit=90.0
        )


class MissionManager:
    """Manages multiple missions and tracks overall progress."""
    
    def __init__(self):
        """Initialize the mission manager."""
        self.missions: Dict[str, Mission] = {}
        self.active_mission: Optional[Mission] = None
        self.completed_missions: List[str] = []
        self.total_score = 0
        self.session_start_time: Optional[float] = None
        
    def add_mission(self, mission: Mission) -> None:
        """Add a mission to the manager."""
        self.missions[mission.mission_id] = mission
        logger.info(f"Added mission: {mission.name}")
        
    def load_fll_season(self, season: str = "2024-SUBMERGED") -> None:
        """Load missions for a specific FLL season."""
        if season == "2024-SUBMERGED":
            missions = FLLMissionFactory.create_submerged_2024_missions()
            for mission in missions:
                self.add_mission(mission)
        else:
            logger.warning(f"Unknown FLL season: {season}")
            
    def start_mission(self, mission_id: str) -> bool:
        """Start a specific mission."""
        if mission_id not in self.missions:
            logger.error(f"Mission not found: {mission_id}")
            return False
            
        # Stop current mission if any
        if self.active_mission and self.active_mission.status == MissionStatus.IN_PROGRESS:
            logger.warning(f"Stopping current mission: {self.active_mission.name}")
            self.active_mission._fail_mission()
            
        mission = self.missions[mission_id]
        if mission.start():
            self.active_mission = mission
            if self.session_start_time is None:
                self.session_start_time = time.time()
            return True
            
        return False
        
    def update_active_mission(self, robot_state: Dict[str, Any], 
                            environment_state: Dict[str, Any]) -> None:
        """Update the currently active mission."""
        if self.active_mission and self.active_mission.status == MissionStatus.IN_PROGRESS:
            self.active_mission.update(robot_state, environment_state)
            
            # Check if mission just completed
            if self.active_mission.status == MissionStatus.COMPLETED:
                self.completed_missions.append(self.active_mission.mission_id)
                self.total_score += self.active_mission.score
                logger.info(f"Mission completed! Total score: {self.total_score}")
                
    def get_available_missions(self) -> List[Mission]:
        """Get list of missions that can be started (prerequisites met)."""
        available = []
        for mission in self.missions.values():
            if mission.status == MissionStatus.NOT_STARTED:
                # Check prerequisites
                prerequisites_met = all(
                    prereq in self.completed_missions 
                    for prereq in mission.prerequisite_missions
                )
                if prerequisites_met:
                    available.append(mission)
        return available
        
    def get_session_summary(self) -> Dict[str, Any]:
        """Get overall session performance summary."""
        session_time = None
        if self.session_start_time:
            session_time = time.time() - self.session_start_time
            
        return {
            'total_score': self.total_score,
            'completed_missions': len(self.completed_missions),
            'total_missions': len(self.missions),
            'session_time': session_time,
            'active_mission': self.active_mission.mission_id if self.active_mission else None,
            'completion_rate': len(self.completed_missions) / len(self.missions) if self.missions else 0.0,
            'mission_details': [
                mission.get_progress_summary() 
                for mission in self.missions.values()
            ]
        }
        
    def reset_all_missions(self) -> None:
        """Reset all missions to initial state."""
        for mission in self.missions.values():
            mission.reset()
        self.completed_missions.clear()
        self.total_score = 0
        self.active_mission = None
        self.session_start_time = None
        logger.info("All missions reset")


# Example usage and testing
if __name__ == "__main__":
    # Create mission manager
    manager = MissionManager()
    
    # Load FLL 2024 missions
    manager.load_fll_season("2024-SUBMERGED")
    
    # Show available missions
    available = manager.get_available_missions()
    print(f"Available missions: {[m.name for m in available]}")
    
    # Start first mission
    if available:
        manager.start_mission(available[0].mission_id)
        print(f"Started mission: {available[0].name}")
        
    # Simulate robot state update
    robot_state = {
        'position': {'x': 1800, 'y': 900, 'angle': 0},
        'sensors': {'color': 'blue'},
        'speed': 100.0,
        'energy_used': 15.0,
        'distance_traveled': 500.0
    }
    
    environment_state = {
        'objects': {
            'coral_sample': {'x': 1800, 'y': 900}
        }
    }
    
    # Update mission
    manager.update_active_mission(robot_state, environment_state)
    
    # Show session summary
    summary = manager.get_session_summary()
    print(f"Session summary: {summary}")
