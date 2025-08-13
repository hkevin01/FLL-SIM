"""
Mission Builder Tool for FLL-Sim

Allows educators to create, edit, and share custom FLL-style missions with
scoring criteria, objectives, and interactive elements.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from fll_sim.education.interactive_tutorial_system import \
    InteractiveTutorialSystem
from fll_sim.utils.logger import FLLLogger


class MissionType(Enum):
    """Types of mission objectives."""
    COLLECT = "collect"
    DELIVER = "deliver"
    ACTIVATE = "activate"
    NAVIGATE = "navigate"
    PRECISION = "precision"
    TIME_BASED = "time_based"
    SEQUENCE = "sequence"
    CONDITIONAL = "conditional"


class ObjectType(Enum):
    """Types of objects that can be placed on the field."""
    OBSTACLE = "obstacle"
    TARGET = "target"
    COLLECTIBLE = "collectible"
    TOOL = "tool"
    ZONE = "zone"
    TRIGGER = "trigger"
    DECORATION = "decoration"


class ScoringType(Enum):
    """Types of scoring mechanisms."""
    BINARY = "binary"  # Pass/fail
    INCREMENTAL = "incremental"  # Points per item
    MULTIPLIER = "multiplier"  # Base score * multiplier
    TIME_BONUS = "time_bonus"  # Bonus for speed
    TIME_PENALTY = "time_penalty"  # Penalty for slowness
    CONDITIONAL = "conditional"  # Based on other objectives


@dataclass
class FieldObject:
    """Represents an object on the mission field."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: ObjectType = ObjectType.OBSTACLE
    position: Tuple[float, float] = (0, 0)
    rotation: float = 0.0  # degrees
    size: Tuple[float, float] = (10, 10)  # cm
    color: str = "#808080"
    properties: Dict[str, Any] = field(default_factory=dict)
    collision_enabled: bool = True
    visible: bool = True
    interactive: bool = False
    description: str = ""


@dataclass
class ScoringCriterion:
    """Represents a scoring criterion for a mission."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    type: ScoringType = ScoringType.BINARY
    points: int = 0
    max_points: Optional[int] = None
    conditions: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)  # Other criteria IDs
    time_limit: Optional[int] = None  # seconds
    is_bonus: bool = False
    is_penalty: bool = False


@dataclass
class MissionObjective:
    """Represents a single mission objective."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    type: MissionType = MissionType.COLLECT
    target_objects: List[str] = field(default_factory=list)  # Object IDs
    success_conditions: Dict[str, Any] = field(default_factory=dict)
    scoring_criteria: List[str] = field(default_factory=list)  # Criterion IDs
    is_required: bool = True
    difficulty: int = 1  # 1-5 scale
    estimated_time: int = 30  # seconds
    hints: List[str] = field(default_factory=list)


@dataclass
class Mission:
    """Complete mission definition."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "New Mission"
    description: str = ""
    theme: str = "general"
    difficulty_level: int = 1  # 1-5 scale
    estimated_duration: int = 150  # seconds (2.5 minutes)

    # Field setup
    field_size: Tuple[int, int] = (240, 120)  # cm (standard FLL field)
    field_objects: Dict[str, FieldObject] = field(default_factory=dict)
    starting_position: Tuple[float, float] = (20, 20)
    starting_rotation: float = 0.0

    # Mission content
    objectives: Dict[str, MissionObjective] = field(default_factory=dict)
    scoring_criteria: Dict[str, ScoringCriterion] = field(default_factory=dict)

    # Metadata
    author: str = ""
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Educational content
    learning_objectives: List[str] = field(default_factory=list)
    prerequisite_skills: List[str] = field(default_factory=list)
    educational_notes: str = ""

    # Sharing and permissions
    is_public: bool = False
    is_template: bool = False
    license: str = "CC BY-SA 4.0"


@dataclass
class MissionAttempt:
    """Represents a student's attempt at a mission."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    mission_id: str = ""
    user_id: str = ""
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    # Results
    score: int = 0
    max_possible_score: int = 0
    completion_time: Optional[int] = None  # seconds
    objectives_completed: List[str] = field(default_factory=list)
    criteria_achieved: Dict[str, int] = field(default_factory=dict)

    # Program used
    program_code: str = ""
    block_program: Optional[Dict[str, Any]] = None

    # Performance data
    robot_path: List[Tuple[float, float, float]] = field(default_factory=list)
    sensor_readings: List[Dict[str, Any]] = field(default_factory=list)
    errors_encountered: List[str] = field(default_factory=list)

    # Feedback
    student_notes: str = ""
    instructor_feedback: str = ""


class MissionBuilder:
    """Main mission builder interface for creating custom missions."""

    def __init__(
        self,
        tutorial_system: Optional[InteractiveTutorialSystem] = None
    ):
        self.logger = FLLLogger('MissionBuilder')
        self.tutorial_system = tutorial_system

        # Mission storage
        self.missions: Dict[str, Mission] = {}
        self.mission_attempts: Dict[str, List[MissionAttempt]] = {}

        # Templates and presets
        self.field_object_templates: Dict[str, FieldObject] = {}
        self.mission_templates: Dict[str, Mission] = {}

        # Current editing state
        self.current_mission: Optional[Mission] = None
        self.selected_objects: List[str] = []
        self.clipboard: List[FieldObject] = []

        # Initialize with default content
        self._initialize_default_templates()
        self._initialize_sample_missions()

        self.logger.info("Mission Builder initialized")

    def _initialize_default_templates(self):
        """Initialize default field object templates."""
        # Basic obstacles
        self.field_object_templates["wall"] = FieldObject(
            name="Wall",
            type=ObjectType.OBSTACLE,
            size=(50, 10),
            color="#8B4513",
            properties={"material": "wood", "height": 15},
            description="Standard wall obstacle"
        )

        self.field_object_templates["pillar"] = FieldObject(
            name="Pillar",
            type=ObjectType.OBSTACLE,
            size=(10, 10),
            color="#696969",
            properties={"material": "plastic", "height": 25},
            description="Cylindrical pillar obstacle"
        )

        # Collectible items
        self.field_object_templates["cargo"] = FieldObject(
            name="Cargo",
            type=ObjectType.COLLECTIBLE,
            size=(8, 8),
            color="#FF6B35",
            properties={"weight": 50, "fragile": False},
            interactive=True,
            description="Standard cargo item to collect"
        )

        self.field_object_templates["cargo_fragile"] = FieldObject(
            name="Fragile Cargo",
            type=ObjectType.COLLECTIBLE,
            size=(8, 8),
            color="#FFD700",
            properties={"weight": 30, "fragile": True},
            interactive=True,
            description="Fragile cargo that requires careful handling"
        )

        # Target zones
        self.field_object_templates["scoring_zone"] = FieldObject(
            name="Scoring Zone",
            type=ObjectType.ZONE,
            size=(30, 30),
            color="#32CD32",
            properties={"zone_type": "scoring", "multiplier": 1},
            collision_enabled=False,
            description="Zone where items can be scored"
        )

        self.field_object_templates["bonus_zone"] = FieldObject(
            name="Bonus Zone",
            type=ObjectType.ZONE,
            size=(20, 20),
            color="#FFD700",
            properties={"zone_type": "bonus", "multiplier": 2},
            collision_enabled=False,
            description="High-value scoring zone"
        )

        # Interactive elements
        self.field_object_templates["lever"] = FieldObject(
            name="Lever",
            type=ObjectType.TOOL,
            size=(5, 15),
            color="#FF4500",
            properties={"state": "inactive", "activation_force": 10},
            interactive=True,
            description="Lever that can be activated by the robot"
        )

        self.field_object_templates["button"] = FieldObject(
            name="Button",
            type=ObjectType.TRIGGER,
            size=(8, 8),
            color="#FF0000",
            properties={"state": "unpressed", "activation_pressure": 5},
            interactive=True,
            description="Pressure-sensitive button"
        )

        self.logger.info(
            f"Initialized {len(self.field_object_templates)} object templates"
        )

    def _initialize_sample_missions(self):
        """Initialize sample missions for demonstration."""
        # Simple cargo delivery mission
        cargo_mission = Mission(
            name="Cargo Delivery Challenge",
            description=("Collect cargo items and deliver them to the "
                         "scoring zone"),
            theme="logistics",
            difficulty_level=2,
            estimated_duration=120,
            learning_objectives=[
                "Practice precise robot movement",
                "Understand pickup and delivery mechanics",
                "Learn basic scoring strategies"
            ],
            prerequisite_skills=["Basic movement", "Sensor reading"]
        )

        # Add field objects
        cargo_mission.field_objects["cargo1"] = FieldObject(
            name="Cargo Item 1",
            type=ObjectType.COLLECTIBLE,
            position=(50, 50),
            size=(8, 8),
            color="#FF6B35",
            interactive=True
        )

        cargo_mission.field_objects["cargo2"] = FieldObject(
            name="Cargo Item 2",
            type=ObjectType.COLLECTIBLE,
            position=(100, 80),
            size=(8, 8),
            color="#FF6B35",
            interactive=True
        )

        cargo_mission.field_objects["scoring_zone"] = FieldObject(
            name="Delivery Zone",
            type=ObjectType.ZONE,
            position=(200, 100),
            size=(30, 30),
            color="#32CD32",
            collision_enabled=False
        )

        # Add objectives
        cargo_mission.objectives["collect_cargo"] = MissionObjective(
            name="Collect Cargo",
            description="Pick up both cargo items",
            type=MissionType.COLLECT,
            target_objects=["cargo1", "cargo2"],
            success_conditions={"items_collected": 2},
            is_required=True,
            difficulty=2,
            estimated_time=60
        )

        cargo_mission.objectives["deliver_cargo"] = MissionObjective(
            name="Deliver Cargo",
            description="Place cargo items in the delivery zone",
            type=MissionType.DELIVER,
            target_objects=["scoring_zone"],
            success_conditions={"items_delivered": 2},
            is_required=True,
            difficulty=3,
            estimated_time=60
        )

        # Add scoring criteria
        cargo_mission.scoring_criteria["cargo_points"] = ScoringCriterion(
            name="Cargo Collection",
            description="Points for each cargo item collected",
            type=ScoringType.INCREMENTAL,
            points=10,
            conditions={"per_item": True}
        )

        cargo_mission.scoring_criteria["delivery_bonus"] = ScoringCriterion(
            name="Delivery Bonus",
            description="Bonus for delivering cargo to the zone",
            type=ScoringType.INCREMENTAL,
            points=20,
            conditions={"per_item_delivered": True},
            dependencies=["cargo_points"]
        )

        cargo_mission.scoring_criteria["time_bonus"] = ScoringCriterion(
            name="Speed Bonus",
            description="Bonus points for completing under 90 seconds",
            type=ScoringType.TIME_BONUS,
            points=15,
            conditions={"time_limit": 90},
            is_bonus=True
        )

        self.add_mission(cargo_mission)

        # Navigation precision mission
        precision_mission = Mission(
            name="Precision Navigation",
            description="Navigate through a course without touching obstacles",
            theme="navigation",
            difficulty_level=3,
            estimated_duration=180,
            learning_objectives=[
                "Master precise robot control",
                "Use sensors for navigation",
                "Understand collision avoidance"
            ]
        )

        # Add obstacles for navigation course
        for i, pos in enumerate([(60, 40), (120, 80), (180, 40)]):
            precision_mission.field_objects[f"obstacle_{i+1}"] = FieldObject(
                name=f"Obstacle {i+1}",
                type=ObjectType.OBSTACLE,
                position=pos,
                size=(15, 15),
                color="#8B4513"
            )

        # Add checkpoints
        for i, pos in enumerate([(40, 60), (100, 60), (160, 60), (220, 60)]):
            precision_mission.field_objects[f"checkpoint_{i+1}"] = FieldObject(
                name=f"Checkpoint {i+1}",
                type=ObjectType.TARGET,
                position=pos,
                size=(10, 10),
                color="#00FF00",
                collision_enabled=False
            )

        precision_mission.objectives["navigate_course"] = MissionObjective(
            name="Navigate Course",
            description="Visit all checkpoints in order without collisions",
            type=MissionType.NAVIGATE,
            target_objects=[f"checkpoint_{i+1}" for i in range(4)],
            success_conditions={"checkpoints_visited": 4, "collisions": 0},
            difficulty=4,
            estimated_time=120
        )

        precision_mission.scoring_criteria[
            "navigation_points"] = ScoringCriterion(
            name="Navigation Points",
            description="Points for visiting checkpoints",
            type=ScoringType.INCREMENTAL,
            points=25,
            conditions={"per_checkpoint": True}
        )

        precision_mission.scoring_criteria[
            "collision_penalty"] = ScoringCriterion(
            name="Collision Penalty",
            description="Point deduction for each collision",
            type=ScoringType.INCREMENTAL,
            points=-10,
            conditions={"per_collision": True},
            is_penalty=True
        )

        self.add_mission(precision_mission)

        self.logger.info(f"Initialized {len(self.missions)} sample missions")

    # Mission Management
    def create_new_mission(self, name: str = "New Mission") -> str:
        """Create a new mission."""
        mission = Mission(name=name)
        self.current_mission = mission
        self.missions[mission.id] = mission

        self.logger.info(f"Created new mission: {name}")
        return mission.id

    def add_mission(self, mission: Mission) -> str:
        """Add a mission to the builder."""
        self.missions[mission.id] = mission
        self.logger.info(f"Added mission: {mission.name}")
        return mission.id

    def load_mission(self, mission_id: str) -> bool:
        """Load a mission for editing."""
        if mission_id not in self.missions:
            self.logger.error(f"Mission not found: {mission_id}")
            return False

        self.current_mission = self.missions[mission_id]
        self.selected_objects.clear()

        self.logger.info(f"Loaded mission: {self.current_mission.name}")
        return True

    def save_mission(self) -> bool:
        """Save the current mission."""
        if not self.current_mission:
            return False

        self.current_mission.updated_at = datetime.now()
        self.missions[self.current_mission.id] = self.current_mission

        self.logger.info(f"Saved mission: {self.current_mission.name}")
        return True

    def duplicate_mission(
        self, mission_id: str, new_name: str
    ) -> Optional[str]:
        """Duplicate an existing mission."""
        if mission_id not in self.missions:
            return None

        original = self.missions[mission_id]
        duplicate = Mission(
            name=new_name,
            description=f"Copy of {original.description}",
            theme=original.theme,
            difficulty_level=original.difficulty_level,
            estimated_duration=original.estimated_duration,
            field_size=original.field_size,
            starting_position=original.starting_position,
            starting_rotation=original.starting_rotation,
            learning_objectives=original.learning_objectives.copy(),
            prerequisite_skills=original.prerequisite_skills.copy(),
            educational_notes=original.educational_notes
        )

        # Deep copy field objects
        for obj_id, obj in original.field_objects.items():
            duplicate.field_objects[obj_id] = FieldObject(
                name=obj.name,
                type=obj.type,
                position=obj.position,
                rotation=obj.rotation,
                size=obj.size,
                color=obj.color,
                properties=obj.properties.copy(),
                collision_enabled=obj.collision_enabled,
                visible=obj.visible,
                interactive=obj.interactive,
                description=obj.description
            )

        # Deep copy objectives and criteria
        for obj_id, obj in original.objectives.items():
            duplicate.objectives[obj_id] = MissionObjective(
                name=obj.name,
                description=obj.description,
                type=obj.type,
                target_objects=obj.target_objects.copy(),
                success_conditions=obj.success_conditions.copy(),
                scoring_criteria=obj.scoring_criteria.copy(),
                is_required=obj.is_required,
                difficulty=obj.difficulty,
                estimated_time=obj.estimated_time,
                hints=obj.hints.copy()
            )

        for crit_id, crit in original.scoring_criteria.items():
            duplicate.scoring_criteria[crit_id] = ScoringCriterion(
                name=crit.name,
                description=crit.description,
                type=crit.type,
                points=crit.points,
                max_points=crit.max_points,
                conditions=crit.conditions.copy(),
                dependencies=crit.dependencies.copy(),
                time_limit=crit.time_limit,
                is_bonus=crit.is_bonus,
                is_penalty=crit.is_penalty
            )

        self.missions[duplicate.id] = duplicate
        self.logger.info(f"Duplicated mission: {new_name}")
        return duplicate.id

    # Field Object Management
    def add_field_object(
        self,
        template_name: str,
        position: Tuple[float, float],
        custom_properties: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Add a field object from a template."""
        if not self.current_mission:
            return None

        if template_name not in self.field_object_templates:
            self.logger.error(f"Template not found: {template_name}")
            return None

        template = self.field_object_templates[template_name]
        field_object = FieldObject(
            name=template.name,
            type=template.type,
            position=position,
            size=template.size,
            color=template.color,
            properties=template.properties.copy(),
            collision_enabled=template.collision_enabled,
            visible=template.visible,
            interactive=template.interactive,
            description=template.description
        )

        if custom_properties:
            field_object.properties.update(custom_properties)

        self.current_mission.field_objects[field_object.id] = field_object
        self.current_mission.updated_at = datetime.now()

        self.logger.debug(f"Added field object: {field_object.name}")
        return field_object.id

    def remove_field_object(self, object_id: str) -> bool:
        """Remove a field object."""
        if (not self.current_mission or
                object_id not in self.current_mission.field_objects):
            return False

        del self.current_mission.field_objects[object_id]

        # Remove from selection if selected
        if object_id in self.selected_objects:
            self.selected_objects.remove(object_id)

        self.current_mission.updated_at = datetime.now()
        return True

    def move_field_object(self, object_id: str, new_position: Tuple[float, float]) -> bool:
        """Move a field object to a new position."""
        if not self.current_mission or object_id not in self.current_mission.field_objects:
            return False

        self.current_mission.field_objects[object_id].position = new_position
        self.current_mission.updated_at = datetime.now()
        return True

    def rotate_field_object(self, object_id: str, rotation: float) -> bool:
        """Rotate a field object."""
        if not self.current_mission or object_id not in self.current_mission.field_objects:
            return False

        self.current_mission.field_objects[object_id].rotation = rotation % 360
        self.current_mission.updated_at = datetime.now()
        return True

    def update_field_object_properties(self, object_id: str,
                                     properties: Dict[str, Any]) -> bool:
        """Update field object properties."""
        if not self.current_mission or object_id not in self.current_mission.field_objects:
            return False

        field_object = self.current_mission.field_objects[object_id]
        field_object.properties.update(properties)
        self.current_mission.updated_at = datetime.now()
        return True

    # Mission Objective Management
    def add_objective(self, name: str, objective_type: MissionType,
                     description: str = "", target_objects: Optional[List[str]] = None) -> str:
        """Add a new mission objective."""
        if not self.current_mission:
            return ""

        objective = MissionObjective(
            name=name,
            description=description,
            type=objective_type,
            target_objects=target_objects or []
        )

        self.current_mission.objectives[objective.id] = objective
        self.current_mission.updated_at = datetime.now()

        self.logger.debug(f"Added objective: {name}")
        return objective.id

    def update_objective(self, objective_id: str, **kwargs) -> bool:
        """Update an existing objective."""
        if not self.current_mission or objective_id not in self.current_mission.objectives:
            return False

        objective = self.current_mission.objectives[objective_id]

        for key, value in kwargs.items():
            if hasattr(objective, key):
                setattr(objective, key, value)

        self.current_mission.updated_at = datetime.now()
        return True

    def remove_objective(self, objective_id: str) -> bool:
        """Remove a mission objective."""
        if not self.current_mission or objective_id not in self.current_mission.objectives:
            return False

        del self.current_mission.objectives[objective_id]
        self.current_mission.updated_at = datetime.now()
        return True

    # Scoring Criteria Management
    def add_scoring_criterion(self, name: str, scoring_type: ScoringType,
                            points: int, description: str = "",
                            conditions: Optional[Dict[str, Any]] = None) -> str:
        """Add a new scoring criterion."""
        if not self.current_mission:
            return ""

        criterion = ScoringCriterion(
            name=name,
            description=description,
            type=scoring_type,
            points=points,
            conditions=conditions or {}
        )

        self.current_mission.scoring_criteria[criterion.id] = criterion
        self.current_mission.updated_at = datetime.now()

        self.logger.debug(f"Added scoring criterion: {name}")
        return criterion.id

    def update_scoring_criterion(self, criterion_id: str, **kwargs) -> bool:
        """Update an existing scoring criterion."""
        if not self.current_mission or criterion_id not in self.current_mission.scoring_criteria:
            return False

        criterion = self.current_mission.scoring_criteria[criterion_id]

        for key, value in kwargs.items():
            if hasattr(criterion, key):
                setattr(criterion, key, value)

        self.current_mission.updated_at = datetime.now()
        return True

    def remove_scoring_criterion(self, criterion_id: str) -> bool:
        """Remove a scoring criterion."""
        if not self.current_mission or criterion_id not in self.current_mission.scoring_criteria:
            return False

        del self.current_mission.scoring_criteria[criterion_id]
        self.current_mission.updated_at = datetime.now()
        return True

    # Mission Validation
    def validate_mission(self, mission_id: Optional[str] = None) -> Dict[str, Any]:
        """Validate a mission for completeness and consistency."""
        mission = (self.missions.get(mission_id) if mission_id
                  else self.current_mission)

        if not mission:
            return {'is_valid': False, 'errors': ['No mission to validate']}

        errors = []
        warnings = []

        # Check basic mission properties
        if not mission.name.strip():
            errors.append("Mission name is required")

        if not mission.description.strip():
            warnings.append("Mission description is empty")

        if not mission.objectives:
            errors.append("Mission must have at least one objective")

        if not mission.scoring_criteria:
            warnings.append("Mission has no scoring criteria")

        # Validate field objects
        if not mission.field_objects:
            warnings.append("Mission has no field objects")

        # Check objective references
        for obj_id, objective in mission.objectives.items():
            for target_id in objective.target_objects:
                if target_id not in mission.field_objects:
                    errors.append(f"Objective '{objective.name}' references unknown object: {target_id}")

        # Check scoring criteria dependencies
        for crit_id, criterion in mission.scoring_criteria.items():
            for dep_id in criterion.dependencies:
                if dep_id not in mission.scoring_criteria:
                    errors.append(f"Scoring criterion '{criterion.name}' has unknown dependency: {dep_id}")

        # Check for circular dependencies in scoring criteria
        cycles = self._find_scoring_cycles(mission)
        if cycles:
            errors.append(f"Circular dependencies in scoring criteria: {len(cycles)}")

        # Calculate total possible score
        max_score = self._calculate_max_score(mission)
        if max_score <= 0:
            warnings.append("Mission has no positive scoring potential")

        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'max_possible_score': max_score,
            'estimated_duration': mission.estimated_duration
        }

    def _find_scoring_cycles(self, mission: Mission) -> List[List[str]]:
        """Find circular dependencies in scoring criteria."""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(crit_id: str, path: List[str]) -> bool:
            if crit_id in rec_stack:
                cycle_start = path.index(crit_id)
                cycles.append(path[cycle_start:] + [crit_id])
                return True

            if crit_id in visited:
                return False

            visited.add(crit_id)
            rec_stack.add(crit_id)
            path.append(crit_id)

            criterion = mission.scoring_criteria[crit_id]
            for dep_id in criterion.dependencies:
                if dep_id in mission.scoring_criteria:
                    if dfs(dep_id, path.copy()):
                        break

            rec_stack.remove(crit_id)
            return False

        for crit_id in mission.scoring_criteria:
            if crit_id not in visited:
                dfs(crit_id, [])

        return cycles

    def _calculate_max_score(self, mission: Mission) -> int:
        """Calculate the maximum possible score for a mission."""
        total_score = 0

        for criterion in mission.scoring_criteria.values():
            if criterion.is_penalty:
                continue  # Don't count penalties in max score

            if criterion.max_points is not None:
                total_score += criterion.max_points
            else:
                # Estimate based on conditions
                if criterion.type == ScoringType.INCREMENTAL:
                    # Estimate based on available objects
                    multiplier = 1
                    if "per_item" in criterion.conditions:
                        multiplier = len([obj for obj in mission.field_objects.values()
                                        if obj.type == ObjectType.COLLECTIBLE])
                    total_score += criterion.points * multiplier
                else:
                    total_score += criterion.points

        return total_score

    # Mission Testing and Simulation
    def test_mission(self, mission_id: Optional[str] = None) -> Dict[str, Any]:
        """Test a mission for playability."""
        mission = (self.missions.get(mission_id) if mission_id
                  else self.current_mission)

        if not mission:
            return {'success': False, 'error': 'No mission to test'}

        # Validate mission first
        validation = self.validate_mission()
        if not validation['is_valid']:
            return {
                'success': False,
                'error': 'Mission validation failed',
                'validation_errors': validation['errors']
            }

        # Check field layout
        layout_issues = self._check_field_layout(mission)

        # Check objective feasibility
        feasibility_issues = self._check_objective_feasibility(mission)

        # Estimate difficulty
        difficulty_rating = self._estimate_difficulty(mission)

        return {
            'success': True,
            'validation': validation,
            'layout_issues': layout_issues,
            'feasibility_issues': feasibility_issues,
            'difficulty_rating': difficulty_rating,
            'recommended_time': self._estimate_completion_time(mission)
        }

    def _check_field_layout(self, mission: Mission) -> List[str]:
        """Check field layout for potential issues."""
        issues = []

        # Check for overlapping objects
        objects = list(mission.field_objects.values())
        for i, obj1 in enumerate(objects):
            for obj2 in objects[i+1:]:
                if self._objects_overlap(obj1, obj2):
                    issues.append(f"Objects overlap: {obj1.name} and {obj2.name}")

        # Check starting position
        start_x, start_y = mission.starting_position
        for obj in objects:
            if obj.collision_enabled and self._point_in_object(start_x, start_y, obj):
                issues.append(f"Starting position conflicts with {obj.name}")

        # Check accessibility
        unreachable_objects = self._find_unreachable_objects(mission)
        if unreachable_objects:
            issues.append(f"Potentially unreachable objects: {len(unreachable_objects)}")

        return issues

    def _objects_overlap(self, obj1: FieldObject, obj2: FieldObject) -> bool:
        """Check if two objects overlap."""
        x1, y1 = obj1.position
        w1, h1 = obj1.size
        x2, y2 = obj2.position
        w2, h2 = obj2.size

        return not (x1 + w1/2 < x2 - w2/2 or x2 + w2/2 < x1 - w1/2 or
                   y1 + h1/2 < y2 - h2/2 or y2 + h2/2 < y1 - h1/2)

    def _point_in_object(self, x: float, y: float, obj: FieldObject) -> bool:
        """Check if a point is inside an object."""
        ox, oy = obj.position
        w, h = obj.size

        return (ox - w/2 <= x <= ox + w/2 and
                oy - h/2 <= y <= oy + h/2)

    def _find_unreachable_objects(self, mission: Mission) -> List[str]:
        """Find objects that may be unreachable due to obstacles."""
        # Simplified reachability check
        # In a full implementation, this would use pathfinding
        unreachable = []

        collectible_objects = [
            obj for obj in mission.field_objects.values()
            if obj.type in [ObjectType.COLLECTIBLE, ObjectType.TARGET]
        ]

        obstacles = [
            obj for obj in mission.field_objects.values()
            if obj.type == ObjectType.OBSTACLE and obj.collision_enabled
        ]

        # Very basic check: if an object is completely surrounded by obstacles
        for obj in collectible_objects:
            if self._is_surrounded_by_obstacles(obj, obstacles):
                unreachable.append(obj.id)

        return unreachable

    def _is_surrounded_by_obstacles(self, target: FieldObject,
                                  obstacles: List[FieldObject]) -> bool:
        """Check if an object is surrounded by obstacles."""
        # Simplified check - just see if there are obstacles in all 4 directions
        tx, ty = target.position
        directions = [(0, 20), (0, -20), (20, 0), (-20, 0)]  # N, S, E, W

        blocked_directions = 0
        for dx, dy in directions:
            check_point = (tx + dx, ty + dy)
            for obstacle in obstacles:
                if self._point_in_object(check_point[0], check_point[1], obstacle):
                    blocked_directions += 1
                    break

        return blocked_directions >= 3  # 3 or more directions blocked

    def _check_objective_feasibility(self, mission: Mission) -> List[str]:
        """Check if objectives are feasible."""
        issues = []

        for objective in mission.objectives.values():
            # Check if target objects exist
            missing_targets = [
                tid for tid in objective.target_objects
                if tid not in mission.field_objects
            ]
            if missing_targets:
                issues.append(f"Objective '{objective.name}' references missing objects")

            # Check time constraints
            if objective.estimated_time > mission.estimated_duration:
                issues.append(f"Objective '{objective.name}' time exceeds mission duration")

        return issues

    def _estimate_difficulty(self, mission: Mission) -> Dict[str, Any]:
        """Estimate the difficulty of a mission."""
        factors = {
            'object_count': len(mission.field_objects),
            'objective_count': len(mission.objectives),
            'precision_required': sum(1 for obj in mission.objectives.values()
                                    if obj.type == MissionType.PRECISION),
            'time_pressure': 1 if mission.estimated_duration < 120 else 0,
            'complex_scoring': len(mission.scoring_criteria)
        }

        # Simple difficulty calculation
        difficulty_score = (
            factors['object_count'] * 0.1 +
            factors['objective_count'] * 0.3 +
            factors['precision_required'] * 0.4 +
            factors['time_pressure'] * 0.2 +
            factors['complex_scoring'] * 0.1
        )

        if difficulty_score < 2:
            difficulty_level = "Beginner"
        elif difficulty_score < 4:
            difficulty_level = "Intermediate"
        elif difficulty_score < 6:
            difficulty_level = "Advanced"
        else:
            difficulty_level = "Expert"

        return {
            'score': difficulty_score,
            'level': difficulty_level,
            'factors': factors
        }

    def _estimate_completion_time(self, mission: Mission) -> int:
        """Estimate realistic completion time for a mission."""
        base_time = sum(obj.estimated_time for obj in mission.objectives.values())

        # Add overhead for complexity
        complexity_multiplier = 1.0 + len(mission.field_objects) * 0.05

        # Add time for potential retries based on difficulty
        difficulty = self._estimate_difficulty(mission)
        retry_multiplier = 1.0 + difficulty['score'] * 0.1

        estimated_time = int(base_time * complexity_multiplier * retry_multiplier)

        return max(estimated_time, 30)  # Minimum 30 seconds

    # Mission Sharing and Export
    def export_mission(self, mission_id: str, include_attempts: bool = False) -> Dict[str, Any]:
        """Export a mission to a dictionary for sharing."""
        if mission_id not in self.missions:
            return {}

        mission = self.missions[mission_id]

        exported = {
            'format_version': '1.0',
            'mission': {
                'id': mission.id,
                'name': mission.name,
                'description': mission.description,
                'theme': mission.theme,
                'difficulty_level': mission.difficulty_level,
                'estimated_duration': mission.estimated_duration,
                'field_size': mission.field_size,
                'starting_position': mission.starting_position,
                'starting_rotation': mission.starting_rotation,
                'learning_objectives': mission.learning_objectives,
                'prerequisite_skills': mission.prerequisite_skills,
                'educational_notes': mission.educational_notes,
                'author': mission.author,
                'version': mission.version,
                'tags': mission.tags,
                'created_at': mission.created_at.isoformat(),
                'updated_at': mission.updated_at.isoformat(),
                'license': mission.license
            },
            'field_objects': [
                {
                    'id': obj.id,
                    'name': obj.name,
                    'type': obj.type.value,
                    'position': obj.position,
                    'rotation': obj.rotation,
                    'size': obj.size,
                    'color': obj.color,
                    'properties': obj.properties,
                    'collision_enabled': obj.collision_enabled,
                    'visible': obj.visible,
                    'interactive': obj.interactive,
                    'description': obj.description
                }
                for obj in mission.field_objects.values()
            ],
            'objectives': [
                {
                    'id': obj.id,
                    'name': obj.name,
                    'description': obj.description,
                    'type': obj.type.value,
                    'target_objects': obj.target_objects,
                    'success_conditions': obj.success_conditions,
                    'scoring_criteria': obj.scoring_criteria,
                    'is_required': obj.is_required,
                    'difficulty': obj.difficulty,
                    'estimated_time': obj.estimated_time,
                    'hints': obj.hints
                }
                for obj in mission.objectives.values()
            ],
            'scoring_criteria': [
                {
                    'id': crit.id,
                    'name': crit.name,
                    'description': crit.description,
                    'type': crit.type.value,
                    'points': crit.points,
                    'max_points': crit.max_points,
                    'conditions': crit.conditions,
                    'dependencies': crit.dependencies,
                    'time_limit': crit.time_limit,
                    'is_bonus': crit.is_bonus,
                    'is_penalty': crit.is_penalty
                }
                for crit in mission.scoring_criteria.values()
            ]
        }

        if include_attempts and mission_id in self.mission_attempts:
            exported['attempts'] = [
                {
                    'id': attempt.id,
                    'user_id': attempt.user_id,
                    'started_at': attempt.started_at.isoformat(),
                    'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None,
                    'score': attempt.score,
                    'completion_time': attempt.completion_time,
                    'objectives_completed': attempt.objectives_completed
                }
                for attempt in self.mission_attempts[mission_id]
            ]

        return exported

    def import_mission(self, mission_data: Dict[str, Any]) -> Optional[str]:
        """Import a mission from exported data."""
        try:
            mission_info = mission_data['mission']

            mission = Mission(
                id=mission_info.get('id', str(uuid.uuid4())),
                name=mission_info['name'],
                description=mission_info.get('description', ''),
                theme=mission_info.get('theme', 'general'),
                difficulty_level=mission_info.get('difficulty_level', 1),
                estimated_duration=mission_info.get('estimated_duration', 150),
                field_size=tuple(mission_info.get('field_size', [240, 120])),
                starting_position=tuple(mission_info.get('starting_position', [20, 20])),
                starting_rotation=mission_info.get('starting_rotation', 0.0),
                learning_objectives=mission_info.get('learning_objectives', []),
                prerequisite_skills=mission_info.get('prerequisite_skills', []),
                educational_notes=mission_info.get('educational_notes', ''),
                author=mission_info.get('author', ''),
                version=mission_info.get('version', '1.0'),
                tags=mission_info.get('tags', []),
                license=mission_info.get('license', 'CC BY-SA 4.0')
            )

            # Import field objects
            for obj_data in mission_data.get('field_objects', []):
                field_object = FieldObject(
                    id=obj_data['id'],
                    name=obj_data['name'],
                    type=ObjectType(obj_data['type']),
                    position=tuple(obj_data['position']),
                    rotation=obj_data.get('rotation', 0.0),
                    size=tuple(obj_data['size']),
                    color=obj_data.get('color', '#808080'),
                    properties=obj_data.get('properties', {}),
                    collision_enabled=obj_data.get('collision_enabled', True),
                    visible=obj_data.get('visible', True),
                    interactive=obj_data.get('interactive', False),
                    description=obj_data.get('description', '')
                )
                mission.field_objects[field_object.id] = field_object

            # Import objectives
            for obj_data in mission_data.get('objectives', []):
                objective = MissionObjective(
                    id=obj_data['id'],
                    name=obj_data['name'],
                    description=obj_data.get('description', ''),
                    type=MissionType(obj_data['type']),
                    target_objects=obj_data.get('target_objects', []),
                    success_conditions=obj_data.get('success_conditions', {}),
                    scoring_criteria=obj_data.get('scoring_criteria', []),
                    is_required=obj_data.get('is_required', True),
                    difficulty=obj_data.get('difficulty', 1),
                    estimated_time=obj_data.get('estimated_time', 30),
                    hints=obj_data.get('hints', [])
                )
                mission.objectives[objective.id] = objective

            # Import scoring criteria
            for crit_data in mission_data.get('scoring_criteria', []):
                criterion = ScoringCriterion(
                    id=crit_data['id'],
                    name=crit_data['name'],
                    description=crit_data.get('description', ''),
                    type=ScoringType(crit_data['type']),
                    points=crit_data['points'],
                    max_points=crit_data.get('max_points'),
                    conditions=crit_data.get('conditions', {}),
                    dependencies=crit_data.get('dependencies', []),
                    time_limit=crit_data.get('time_limit'),
                    is_bonus=crit_data.get('is_bonus', False),
                    is_penalty=crit_data.get('is_penalty', False)
                )
                mission.scoring_criteria[criterion.id] = criterion

            self.missions[mission.id] = mission
            self.logger.info(f"Imported mission: {mission.name}")

            return mission.id

        except Exception as e:
            self.logger.error(f"Failed to import mission: {e}")
            return None

    # Utility Methods
    def get_mission_list(self) -> List[Dict[str, Any]]:
        """Get list of all missions with basic info."""
        return [
            {
                'id': mission.id,
                'name': mission.name,
                'description': mission.description,
                'theme': mission.theme,
                'difficulty_level': mission.difficulty_level,
                'estimated_duration': mission.estimated_duration,
                'author': mission.author,
                'created_at': mission.created_at,
                'updated_at': mission.updated_at,
                'is_public': mission.is_public
            }
            for mission in self.missions.values()
        ]

    def get_field_object_templates(self) -> Dict[str, FieldObject]:
        """Get available field object templates."""
        return self.field_object_templates.copy()

    def get_mission_statistics(self, mission_id: str) -> Dict[str, Any]:
        """Get statistics for a mission."""
        if mission_id not in self.missions:
            return {}

        attempts = self.mission_attempts.get(mission_id, [])

        if not attempts:
            return {
                'total_attempts': 0,
                'completion_rate': 0.0,
                'average_score': 0,
                'average_time': 0
            }

        completed_attempts = [a for a in attempts if a.completed_at is not None]
        completion_rate = (len(completed_attempts) / len(attempts)) * 100

        average_score = (sum(a.score for a in completed_attempts) /
                        len(completed_attempts)) if completed_attempts else 0

        average_time = (sum(a.completion_time for a in completed_attempts if a.completion_time) /
                       len([a for a in completed_attempts if a.completion_time])) if completed_attempts else 0

        return {
            'total_attempts': len(attempts),
            'completion_rate': completion_rate,
            'average_score': average_score,
            'average_time': average_time,
            'best_score': max(a.score for a in completed_attempts) if completed_attempts else 0,
            'fastest_time': min(a.completion_time for a in completed_attempts
                              if a.completion_time) if completed_attempts else 0
        }
