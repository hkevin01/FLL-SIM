"""
Interactive Tutorial System for FLL-Sim

Provides comprehensive step-by-step robot programming lessons with visual
programming interface, mission builder, and progress tracking.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from fll_sim.config.enhanced_config_manager import TypeSafeConfigLoader
from fll_sim.utils.logger import FLLLogger


class TutorialLevel(Enum):
    """Tutorial difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class TutorialCategory(Enum):
    """Tutorial categories for organization."""
    SENSORS = "sensors"
    MOVEMENT = "movement"
    MISSION_STRATEGY = "mission_strategy"
    COMPETITION_RULES = "competition_rules"
    PROGRAMMING_BASICS = "programming_basics"
    DEBUGGING = "debugging"
    ADVANCED_TECHNIQUES = "advanced_techniques"


class BlockType(Enum):
    """Types of programming blocks in visual interface."""
    MOVEMENT = "movement"
    SENSOR = "sensor"
    CONTROL = "control"
    LOGIC = "logic"
    VARIABLE = "variable"
    FUNCTION = "function"
    EVENT = "event"


@dataclass
class TutorialStep:
    """Enhanced tutorial step with interactive elements."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    content: str = ""
    instructions: str = ""
    hint: Optional[str] = None
    code_example: Optional[str] = None
    expected_output: Optional[str] = None
    validation_code: Optional[str] = None
    interactive_elements: Dict[str, Any] = field(default_factory=dict)
    completion_criteria: Dict[str, Any] = field(default_factory=dict)
    resources: List[str] = field(default_factory=list)
    estimated_time: int = 5  # minutes

    def is_completed(self, user_data: Dict[str, Any]) -> bool:
        """Check if step is completed based on user data."""
        if not self.completion_criteria:
            return True

        for criterion, expected in self.completion_criteria.items():
            if criterion not in user_data:
                return False
            if user_data[criterion] != expected:
                return False
        return True


@dataclass
class Tutorial:
    """Enhanced tutorial with metadata and progress tracking."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    category: TutorialCategory = TutorialCategory.PROGRAMMING_BASICS
    level: TutorialLevel = TutorialLevel.BEGINNER
    steps: List[TutorialStep] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    estimated_duration: int = 30  # minutes
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    author: str = "FLL-Sim"
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)

    def get_completion_percentage(self, completed_steps: List[str]) -> float:
        """Calculate completion percentage."""
        if not self.steps:
            return 0.0
        completed_count = sum(
            1 for step in self.steps if step.id in completed_steps
        )
        return (completed_count / len(self.steps)) * 100


@dataclass
class ProgrammingBlock:
    """Visual programming block definition."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: BlockType = BlockType.MOVEMENT
    name: str = ""
    description: str = ""
    category: str = ""
    icon: str = ""
    color: str = "#4CAF50"
    inputs: List[Dict[str, Any]] = field(default_factory=list)
    outputs: List[Dict[str, Any]] = field(default_factory=list)
    code_template: str = ""
    example_code: str = ""
    documentation: str = ""
    is_custom: bool = False

    def generate_code(self, input_values: Dict[str, Any]) -> str:
        """Generate Python code from block configuration."""
        code = self.code_template
        for input_name, value in input_values.items():
            placeholder = f"{{{input_name}}}"
            code = code.replace(placeholder, str(value))
        return code


@dataclass
class UserProgress:
    """Tracks user progress through tutorials."""
    user_id: str = ""
    tutorial_id: str = ""
    completed_steps: List[str] = field(default_factory=list)
    current_step_id: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    completion_percentage: float = 0.0
    time_spent: int = 0  # minutes
    achievements: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class Achievement:
    """User achievement definition."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    icon: str = ""
    category: str = ""
    criteria: Dict[str, Any] = field(default_factory=dict)
    points: int = 0
    is_hidden: bool = False
    unlock_date: Optional[datetime] = None


class InteractiveTutorialSystem:
    """Enhanced interactive tutorial system with visual programming."""

    def __init__(self, config_path: Optional[str] = None):
        self.logger = FLLLogger('InteractiveTutorialSystem')
        self.config_loader = TypeSafeConfigLoader()

        # Core data structures
        self.tutorials: Dict[str, Tutorial] = {}
        self.programming_blocks: Dict[str, ProgrammingBlock] = {}
        self.user_progress: Dict[str, Dict[str, UserProgress]] = {}
        self.achievements: Dict[str, Achievement] = {}

        # Configuration
        self.config = self._load_config(config_path)

        # Initialize default content
        self._initialize_default_blocks()
        self._initialize_default_tutorials()
        self._initialize_achievements()

        self.logger.info("Interactive Tutorial System initialized")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load tutorial system configuration."""
        if config_path:
            try:
                return self.config_loader.load_config(config_path)
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")

        return {
            'tutorial_settings': {
                'auto_save_progress': True,
                'show_hints': True,
                'enable_achievements': True,
                'max_hint_frequency': 3
            },
            'visual_programming': {
                'enabled': True,
                'auto_generate_code': True,
                'show_generated_code': True,
                'enable_custom_blocks': True
            },
            'progress_tracking': {
                'track_time_spent': True,
                'enable_analytics': True,
                'save_user_notes': True
            }
        }

    def _initialize_default_blocks(self):
        """Initialize default programming blocks."""
        # Movement blocks
        self.add_programming_block(ProgrammingBlock(
            type=BlockType.MOVEMENT,
            name="Move Forward",
            description="Move robot forward by specified distance",
            category="basic_movement",
            icon="arrow-up",
            color="#2196F3",
            inputs=[
                {
                    "name": "distance",
                    "type": "number",
                    "default": 10,
                    "unit": "cm"
                }
            ],
            code_template="robot.move_forward({distance})",
            example_code="robot.move_forward(10)  # Move 10cm forward"
        ))

        self.add_programming_block(ProgrammingBlock(
            type=BlockType.MOVEMENT,
            name="Turn Left",
            description="Turn robot left by specified degrees",
            category="basic_movement",
            icon="rotate-left",
            color="#2196F3",
            inputs=[
                {"name": "degrees", "type": "number", "default": 90, "unit": "°"}
            ],
            code_template="robot.turn_left({degrees})",
            example_code="robot.turn_left(90)  # Turn 90 degrees left"
        ))

        self.add_programming_block(ProgrammingBlock(
            type=BlockType.MOVEMENT,
            name="Turn Right",
            description="Turn robot right by specified degrees",
            category="basic_movement",
            icon="rotate-right",
            color="#2196F3",
            inputs=[
                {"name": "degrees", "type": "number", "default": 90, "unit": "°"}
            ],
            code_template="robot.turn_right({degrees})",
            example_code="robot.turn_right(90)  # Turn 90 degrees right"
        ))

        # Sensor blocks
        self.add_programming_block(ProgrammingBlock(
            type=BlockType.SENSOR,
            name="Color Sensor",
            description="Read color from color sensor",
            category="sensors",
            icon="eye",
            color="#FF9800",
            inputs=[
                {"name": "port", "type": "select", "options": [1, 2, 3, 4], "default": 1}
            ],
            outputs=[
                {"name": "color", "type": "string"}
            ],
            code_template="color = robot.color_sensor({port}).read()",
            example_code="color = robot.color_sensor(1).read()"
        ))

        self.add_programming_block(ProgrammingBlock(
            type=BlockType.SENSOR,
            name="Ultrasonic Sensor",
            description="Measure distance using ultrasonic sensor",
            category="sensors",
            icon="radar",
            color="#FF9800",
            inputs=[
                {"name": "port", "type": "select", "options": [1, 2, 3, 4], "default": 2}
            ],
            outputs=[
                {"name": "distance", "type": "number", "unit": "cm"}
            ],
            code_template="distance = robot.ultrasonic_sensor({port}).read()",
            example_code="distance = robot.ultrasonic_sensor(2).read()"
        ))

        # Control blocks
        self.add_programming_block(ProgrammingBlock(
            type=BlockType.CONTROL,
            name="Wait",
            description="Wait for specified time",
            category="control",
            icon="clock",
            color="#9C27B0",
            inputs=[
                {"name": "seconds", "type": "number", "default": 1, "unit": "s"}
            ],
            code_template="time.sleep({seconds})",
            example_code="time.sleep(1)  # Wait 1 second"
        ))

        self.add_programming_block(ProgrammingBlock(
            type=BlockType.CONTROL,
            name="Repeat",
            description="Repeat actions specified number of times",
            category="control",
            icon="repeat",
            color="#9C27B0",
            inputs=[
                {"name": "times", "type": "number", "default": 3}
            ],
            code_template="for i in range({times}):",
            example_code="for i in range(3):\n    # Actions to repeat"
        ))

        # Logic blocks
        self.add_programming_block(ProgrammingBlock(
            type=BlockType.LOGIC,
            name="If Color",
            description="Execute actions if color matches",
            category="conditionals",
            icon="branch",
            color="#4CAF50",
            inputs=[
                {"name": "color", "type": "select", "options": ["red", "blue", "green", "yellow", "black", "white"], "default": "red"}
            ],
            code_template="if color == '{color}':",
            example_code="if color == 'red':\n    # Actions for red color"
        ))

        self.logger.info(f"Initialized {len(self.programming_blocks)} default programming blocks")

    def _initialize_default_tutorials(self):
        """Initialize default tutorial content."""
        # Basic Movement Tutorial
        basic_movement = Tutorial(
            name="Basic Robot Movement",
            description="Learn fundamental robot movement commands",
            category=TutorialCategory.MOVEMENT,
            level=TutorialLevel.BEGINNER,
            learning_objectives=[
                "Understand robot coordinate system",
                "Control robot movement with basic commands",
                "Combine movements to create paths"
            ],
            estimated_duration=20,
            steps=[
                TutorialStep(
                    title="Introduction to Robot Movement",
                    content="Welcome to robot programming! In this tutorial, you'll learn how to make your robot move.",
                    instructions="Click 'Next' to continue to the first programming exercise.",
                    interactive_elements={
                        "simulation_view": True,
                        "visual_programming": True
                    }
                ),
                TutorialStep(
                    title="Move Forward",
                    content="Let's start with the most basic movement: moving forward.",
                    instructions="Drag the 'Move Forward' block to the workspace and set distance to 20cm.",
                    code_example="robot.move_forward(20)",
                    completion_criteria={
                        "blocks_used": ["move_forward"],
                        "forward_distance": 20
                    },
                    interactive_elements={
                        "required_blocks": ["Move Forward"],
                        "simulation_reset": True
                    }
                ),
                TutorialStep(
                    title="Turn Left and Right",
                    content="Now let's learn how to turn the robot.",
                    instructions="Add a 'Turn Left' block after the forward movement. Set it to 90 degrees.",
                    code_example="robot.move_forward(20)\nrobot.turn_left(90)",
                    completion_criteria={
                        "blocks_used": ["move_forward", "turn_left"],
                        "turn_degrees": 90
                    },
                    interactive_elements={
                        "required_blocks": ["Move Forward", "Turn Left"],
                        "show_robot_orientation": True
                    }
                ),
                TutorialStep(
                    title="Create a Square Path",
                    content="Combine movements to create more complex paths.",
                    instructions="Create a program that makes the robot move in a square pattern.",
                    hint="You'll need: Move Forward (4 times) and Turn Left (4 times, 90 degrees each)",
                    completion_criteria={
                        "pattern": "square",
                        "return_to_start": True
                    },
                    interactive_elements={
                        "path_visualization": True,
                        "success_animation": True
                    }
                )
            ]
        )

        # Sensor Tutorial
        sensor_tutorial = Tutorial(
            name="Working with Sensors",
            description="Learn to use robot sensors for environmental awareness",
            category=TutorialCategory.SENSORS,
            level=TutorialLevel.BEGINNER,
            prerequisites=["Basic Robot Movement"],
            learning_objectives=[
                "Understand different sensor types",
                "Read sensor values",
                "Make decisions based on sensor data"
            ],
            estimated_duration=25,
            steps=[
                TutorialStep(
                    title="Introduction to Sensors",
                    content="Sensors allow your robot to perceive its environment.",
                    instructions="Let's explore the color sensor and ultrasonic sensor.",
                    interactive_elements={
                        "sensor_demo": True,
                        "sensor_visualization": True
                    }
                ),
                TutorialStep(
                    title="Reading Color Values",
                    content="The color sensor can detect different colors.",
                    instructions="Use the Color Sensor block to read the color below the robot.",
                    code_example="color = robot.color_sensor(1).read()\nprint(f'Detected color: {color}')",
                    completion_criteria={
                        "sensor_read": True,
                        "color_detected": True
                    },
                    interactive_elements={
                        "color_objects": True,
                        "sensor_feedback": True
                    }
                ),
                TutorialStep(
                    title="Color-Based Navigation",
                    content="Use color detection to control robot behavior.",
                    instructions="Create a program that stops when the robot detects a red object.",
                    hint="Use the 'If Color' block combined with movement blocks",
                    completion_criteria={
                        "conditional_logic": True,
                        "stops_on_red": True
                    },
                    interactive_elements={
                        "colored_obstacles": True,
                        "logic_visualization": True
                    }
                )
            ]
        )

        # Competition Rules Tutorial
        competition_tutorial = Tutorial(
            name="FLL Competition Basics",
            description="Learn the fundamentals of FIRST LEGO League competitions",
            category=TutorialCategory.COMPETITION_RULES,
            level=TutorialLevel.BEGINNER,
            learning_objectives=[
                "Understand FLL competition format",
                "Learn scoring mechanisms",
                "Practice mission strategies"
            ],
            estimated_duration=30,
            steps=[
                TutorialStep(
                    title="Competition Overview",
                    content="FLL competitions involve autonomous robot missions on a themed game board.",
                    instructions="Explore the competition field and understand the mission objectives.",
                    interactive_elements={
                        "field_tour": True,
                        "mission_overview": True
                    }
                ),
                TutorialStep(
                    title="Mission Strategy",
                    content="Successful teams plan their robot's mission sequence carefully.",
                    instructions="Analyze the sample mission and identify the optimal path.",
                    interactive_elements={
                        "strategy_planner": True,
                        "path_optimizer": True
                    }
                ),
                TutorialStep(
                    title="Scoring System",
                    content="Each mission has specific scoring criteria and point values.",
                    instructions="Calculate the potential score for different mission approaches.",
                    interactive_elements={
                        "score_calculator": True,
                        "mission_simulator": True
                    }
                )
            ]
        )

        # Add tutorials to system
        self.add_tutorial(basic_movement)
        self.add_tutorial(sensor_tutorial)
        self.add_tutorial(competition_tutorial)

        self.logger.info(f"Initialized {len(self.tutorials)} default tutorials")

    def _initialize_achievements(self):
        """Initialize achievement system."""
        achievements = [
            Achievement(
                name="First Steps",
                description="Complete your first tutorial",
                icon="baby-steps",
                category="beginner",
                criteria={"tutorials_completed": 1},
                points=10
            ),
            Achievement(
                name="Block Builder",
                description="Use 10 different programming blocks",
                icon="blocks",
                category="programming",
                criteria={"unique_blocks_used": 10},
                points=25
            ),
            Achievement(
                name="Sensor Master",
                description="Complete all sensor tutorials",
                icon="sensor",
                category="sensors",
                criteria={"sensor_tutorials_completed": True},
                points=50
            ),
            Achievement(
                name="Mission Accomplished",
                description="Successfully complete a competition mission",
                icon="trophy",
                category="competition",
                criteria={"mission_completed": True},
                points=100
            ),
            Achievement(
                name="Speed Demon",
                description="Complete a tutorial in under 10 minutes",
                icon="lightning",
                category="speed",
                criteria={"tutorial_time_under": 10},
                points=30,
                is_hidden=True
            )
        ]

        for achievement in achievements:
            self.achievements[achievement.id] = achievement

        self.logger.info(f"Initialized {len(self.achievements)} achievements")

    # Tutorial Management Methods
    def add_tutorial(self, tutorial: Tutorial) -> str:
        """Add a new tutorial to the system."""
        self.tutorials[tutorial.id] = tutorial
        self.logger.info(f"Added tutorial: {tutorial.name}")
        return tutorial.id

    def get_tutorial(self, tutorial_id: str) -> Optional[Tutorial]:
        """Get tutorial by ID."""
        return self.tutorials.get(tutorial_id)

    def get_tutorials_by_category(self, category: TutorialCategory) -> List[Tutorial]:
        """Get all tutorials in a category."""
        return [t for t in self.tutorials.values() if t.category == category]

    def get_tutorials_by_level(self, level: TutorialLevel) -> List[Tutorial]:
        """Get all tutorials at a difficulty level."""
        return [t for t in self.tutorials.values() if t.level == level]

    def search_tutorials(self, query: str) -> List[Tutorial]:
        """Search tutorials by name, description, or tags."""
        query_lower = query.lower()
        results = []

        for tutorial in self.tutorials.values():
            if (query_lower in tutorial.name.lower() or
                query_lower in tutorial.description.lower() or
                any(query_lower in tag.lower() for tag in tutorial.tags)):
                results.append(tutorial)

        return results

    # Programming Block Management
    def add_programming_block(self, block: ProgrammingBlock) -> str:
        """Add a new programming block."""
        self.programming_blocks[block.id] = block
        return block.id

    def get_programming_block(self, block_id: str) -> Optional[ProgrammingBlock]:
        """Get programming block by ID."""
        return self.programming_blocks.get(block_id)

    def get_blocks_by_type(self, block_type: BlockType) -> List[ProgrammingBlock]:
        """Get all blocks of a specific type."""
        return [b for b in self.programming_blocks.values() if b.type == block_type]

    def get_blocks_by_category(self, category: str) -> List[ProgrammingBlock]:
        """Get all blocks in a category."""
        return [b for b in self.programming_blocks.values() if b.category == category]

    # User Progress Management
    def start_tutorial(self, user_id: str, tutorial_id: str) -> Optional[TutorialStep]:
        """Start a tutorial for a user."""
        tutorial = self.get_tutorial(tutorial_id)
        if not tutorial or not tutorial.steps:
            return None

        if user_id not in self.user_progress:
            self.user_progress[user_id] = {}

        progress = UserProgress(
            user_id=user_id,
            tutorial_id=tutorial_id,
            current_step_id=tutorial.steps[0].id
        )

        self.user_progress[user_id][tutorial_id] = progress
        self.logger.info(f"User {user_id} started tutorial: {tutorial.name}")

        return tutorial.steps[0]

    def get_current_step(self, user_id: str, tutorial_id: str) -> Optional[TutorialStep]:
        """Get user's current tutorial step."""
        progress = self.user_progress.get(user_id, {}).get(tutorial_id)
        if not progress or not progress.current_step_id:
            return None

        tutorial = self.get_tutorial(tutorial_id)
        if not tutorial:
            return None

        for step in tutorial.steps:
            if step.id == progress.current_step_id:
                return step

        return None

    def complete_step(self, user_id: str, tutorial_id: str, step_id: str,
                     user_data: Dict[str, Any]) -> Optional[TutorialStep]:
        """Mark a step as completed and advance to next step."""
        progress = self.user_progress.get(user_id, {}).get(tutorial_id)
        tutorial = self.get_tutorial(tutorial_id)

        if not progress or not tutorial:
            return None

        # Find current step and validate completion
        current_step = None
        for step in tutorial.steps:
            if step.id == step_id:
                current_step = step
                break

        if not current_step or not current_step.is_completed(user_data):
            return None

        # Mark step as completed
        if step_id not in progress.completed_steps:
            progress.completed_steps.append(step_id)

        # Find next step
        step_index = next(i for i, s in enumerate(tutorial.steps) if s.id == step_id)
        if step_index < len(tutorial.steps) - 1:
            next_step = tutorial.steps[step_index + 1]
            progress.current_step_id = next_step.id
            progress.last_accessed = datetime.now()

            # Update completion percentage
            progress.completion_percentage = tutorial.get_completion_percentage(
                progress.completed_steps
            )

            self.logger.info(f"User {user_id} completed step: {current_step.title}")
            return next_step
        else:
            # Tutorial completed
            progress.completion_percentage = 100.0
            progress.current_step_id = None
            self._check_achievements(user_id, tutorial_id)
            self.logger.info(f"User {user_id} completed tutorial: {tutorial.name}")
            return None

    def get_user_progress(self, user_id: str, tutorial_id: str) -> Optional[UserProgress]:
        """Get user's progress for a specific tutorial."""
        return self.user_progress.get(user_id, {}).get(tutorial_id)

    def get_all_user_progress(self, user_id: str) -> Dict[str, UserProgress]:
        """Get all tutorial progress for a user."""
        return self.user_progress.get(user_id, {})

    # Visual Programming Methods
    def generate_code_from_blocks(self, blocks: List[Dict[str, Any]]) -> str:
        """Generate Python code from visual programming blocks."""
        code_lines = []
        indent_level = 0

        for block_data in blocks:
            block_id = block_data.get('block_id')
            input_values = block_data.get('inputs', {})

            block = self.get_programming_block(block_id)
            if not block:
                continue

            # Generate code for this block
            block_code = block.generate_code(input_values)

            # Handle indentation for control structures
            if block.type == BlockType.CONTROL:
                if block.name in ["Repeat", "If Color"]:
                    code_lines.append("    " * indent_level + block_code)
                    indent_level += 1
                else:
                    code_lines.append("    " * indent_level + block_code)
            else:
                code_lines.append("    " * indent_level + block_code)

        return "\n".join(code_lines)

    def validate_block_sequence(self, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a sequence of programming blocks."""
        errors = []
        warnings = []

        # Check for common issues
        has_movement = any(
            self.get_programming_block(b.get('block_id', '')).type == BlockType.MOVEMENT
            for b in blocks
            if self.get_programming_block(b.get('block_id', ''))
        )

        if not has_movement:
            warnings.append("No movement blocks detected. Robot will not move.")

        # Check for sensor usage without conditional logic
        has_sensors = any(
            self.get_programming_block(b.get('block_id', '')).type == BlockType.SENSOR
            for b in blocks
            if self.get_programming_block(b.get('block_id', ''))
        )

        has_logic = any(
            self.get_programming_block(b.get('block_id', '')).type == BlockType.LOGIC
            for b in blocks
            if self.get_programming_block(b.get('block_id', ''))
        )

        if has_sensors and not has_logic:
            warnings.append("Sensor blocks used without conditional logic. Consider using 'If' blocks.")

        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    # Achievement System
    def _check_achievements(self, user_id: str, tutorial_id: str):
        """Check and award achievements for user."""
        user_tutorials = self.get_all_user_progress(user_id)
        completed_tutorials = sum(1 for p in user_tutorials.values()
                                if p.completion_percentage == 100.0)

        # Check each achievement
        for achievement in self.achievements.values():
            if achievement.id in self.user_progress.get(user_id, {}).get('achievements', []):
                continue  # Already unlocked

            criteria = achievement.criteria
            unlocked = False

            if 'tutorials_completed' in criteria:
                if completed_tutorials >= criteria['tutorials_completed']:
                    unlocked = True

            if 'sensor_tutorials_completed' in criteria:
                sensor_tutorials = [t for t in self.tutorials.values()
                                  if t.category == TutorialCategory.SENSORS]
                completed_sensor = sum(1 for t in sensor_tutorials
                                     if user_tutorials.get(t.id, UserProgress()).completion_percentage == 100.0)
                if completed_sensor == len(sensor_tutorials):
                    unlocked = True

            if unlocked:
                self._award_achievement(user_id, achievement.id)

    def _award_achievement(self, user_id: str, achievement_id: str):
        """Award an achievement to a user."""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {}

        if 'achievements' not in self.user_progress[user_id]:
            self.user_progress[user_id]['achievements'] = []

        if achievement_id not in self.user_progress[user_id]['achievements']:
            self.user_progress[user_id]['achievements'].append(achievement_id)
            achievement = self.achievements[achievement_id]
            self.logger.info(f"Achievement unlocked for {user_id}: {achievement.name}")

    def get_user_achievements(self, user_id: str) -> List[Achievement]:
        """Get all achievements for a user."""
        achievement_ids = self.user_progress.get(user_id, {}).get('achievements', [])
        return [self.achievements[aid] for aid in achievement_ids if aid in self.achievements]

    # Data Export/Import
    def export_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Export user progress data."""
        user_data = self.user_progress.get(user_id, {})
        return {
            'user_id': user_id,
            'tutorials': {tid: {
                'completion_percentage': progress.completion_percentage,
                'completed_steps': progress.completed_steps,
                'time_spent': progress.time_spent,
                'last_accessed': progress.last_accessed.isoformat()
            } for tid, progress in user_data.items() if isinstance(progress, UserProgress)},
            'achievements': user_data.get('achievements', []),
            'exported_at': datetime.now().isoformat()
        }

    def import_user_progress(self, user_data: Dict[str, Any]):
        """Import user progress data."""
        user_id = user_data['user_id']

        if user_id not in self.user_progress:
            self.user_progress[user_id] = {}

        # Import tutorial progress
        for tutorial_id, tutorial_data in user_data.get('tutorials', {}).items():
            if tutorial_id in self.tutorials:
                progress = UserProgress(
                    user_id=user_id,
                    tutorial_id=tutorial_id,
                    completed_steps=tutorial_data['completed_steps'],
                    completion_percentage=tutorial_data['completion_percentage'],
                    time_spent=tutorial_data['time_spent'],
                    last_accessed=datetime.fromisoformat(tutorial_data['last_accessed'])
                )
                self.user_progress[user_id][tutorial_id] = progress

        # Import achievements
        self.user_progress[user_id]['achievements'] = user_data.get('achievements', [])

        self.logger.info(f"Imported progress data for user: {user_id}")

    # Statistics and Analytics
    def get_tutorial_statistics(self, tutorial_id: str) -> Dict[str, Any]:
        """Get statistics for a tutorial."""
        tutorial = self.get_tutorial(tutorial_id)
        if not tutorial:
            return {}

        all_progress = [
            progress for user_data in self.user_progress.values()
            for tid, progress in user_data.items()
            if tid == tutorial_id and isinstance(progress, UserProgress)
        ]

        if not all_progress:
            return {
                'total_users': 0,
                'completion_rate': 0.0,
                'average_time': 0,
                'step_completion_rates': {}
            }

        completed_users = sum(1 for p in all_progress if p.completion_percentage == 100.0)
        average_time = sum(p.time_spent for p in all_progress) / len(all_progress)

        # Step completion rates
        step_rates = {}
        for step in tutorial.steps:
            completed_step = sum(1 for p in all_progress if step.id in p.completed_steps)
            step_rates[step.title] = (completed_step / len(all_progress)) * 100

        return {
            'total_users': len(all_progress),
            'completion_rate': (completed_users / len(all_progress)) * 100,
            'average_time': average_time,
            'step_completion_rates': step_rates
        }

    def get_system_statistics(self) -> Dict[str, Any]:
        """Get overall system statistics."""
        total_users = len(self.user_progress)
        total_tutorials = len(self.tutorials)
        total_blocks = len(self.programming_blocks)

        all_progress = [
            progress for user_data in self.user_progress.values()
            for progress in user_data.values()
            if isinstance(progress, UserProgress)
        ]

        completed_tutorials = sum(1 for p in all_progress if p.completion_percentage == 100.0)

        return {
            'total_users': total_users,
            'total_tutorials': total_tutorials,
            'total_programming_blocks': total_blocks,
            'total_tutorial_attempts': len(all_progress),
            'completed_tutorials': completed_tutorials,
            'completion_rate': (completed_tutorials / len(all_progress) * 100) if all_progress else 0,
            'most_popular_tutorial': self._get_most_popular_tutorial(),
            'average_tutorial_time': sum(p.time_spent for p in all_progress) / len(all_progress) if all_progress else 0
        }

    def _get_most_popular_tutorial(self) -> Optional[str]:
        """Get the most popular tutorial by user count."""
        tutorial_counts = {}

        for user_data in self.user_progress.values():
            for tutorial_id, progress in user_data.items():
                if isinstance(progress, UserProgress):
                    tutorial_counts[tutorial_id] = tutorial_counts.get(tutorial_id, 0) + 1

        if not tutorial_counts:
            return None

        most_popular_id = max(tutorial_counts, key=tutorial_counts.get)
        tutorial = self.get_tutorial(most_popular_id)
        return tutorial.name if tutorial else None
