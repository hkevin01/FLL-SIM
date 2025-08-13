"""
Game map implementation for FLL challenges.

This module defines the game map/field where the robot operates,
including obstacles, missions, and scoring areas. Enhanced with
mission integration and FLL-specific features.
"""

import heapq
import json
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import pygame
import pymunk

from .mission import Mission, MissionManager


@dataclass
class MapConfig:
    """Configuration for the game map."""

    # Field dimensions (standard FLL field is 2400x1200mm)
    width: float = 2400.0  # mm
    height: float = 1200.0  # mm

    # Border properties
    border_thickness: float = 50.0  # mm
    border_color: Tuple[int, int, int] = (100, 100, 100)

    # Field surface
    surface_color: Tuple[int, int, int] = (255, 255, 255)  # White

    # Grid lines for measurement
    show_grid: bool = True
    grid_spacing: float = 100.0  # mm
    grid_color: Tuple[int, int, int] = (200, 200, 200)

    # Mission areas
    show_mission_areas: bool = True
    mission_area_alpha: int = 128  # Transparency for mission overlays


@dataclass
class Obstacle:
    """Physical obstacle on the game map."""

    name: str
    x: float  # Center X position in mm
    y: float  # Center Y position in mm
    width: float  # Width in mm
    height: float  # Height in mm
    angle: float = 0.0  # Rotation angle in degrees
    color: Tuple[int, int, int] = (100, 50, 0)  # Brown
    is_movable: bool = False  # Can be pushed by robot
    mass: float = 1.0  # kg (for movable objects)
    mission_related: bool = False  # Part of a mission
    object_id: Optional[str] = None  # Unique ID for mission tracking


@dataclass
class ColorZone:
    """Colored area on the game map for color sensor detection."""

    name: str
    x: float  # Center X position
    y: float  # Center Y position
    width: float  # Width in mm
    height: float  # Height in mm
    color: Tuple[int, int, int]  # RGB color
    angle: float = 0.0  # Rotation angle in degrees
    sensor_value: str = ""  # What color sensor should read


@dataclass
class MissionArea:
    """Visual representation of mission target areas."""

    mission_id: str
    area_type: str  # "circle", "rectangle", "polygon"
    parameters: Dict[str, Any]  # Area-specific parameters
    color: Tuple[int, int, int] = (0, 255, 0)  # Green
    active_color: Tuple[int, int, int] = (255, 255, 0)  # Yellow when active
    completed_color: Tuple[int, int, int] = (0, 255, 255)  # Cyan when completed


class GameMap:
    """
    Game map representing the FLL playing field.

    Enhanced with mission integration, real-time scoring,
    and FLL-specific features based on competition requirements.

    The map includes:
    - Physical boundaries and obstacles
    - Mission areas and scoring zones
    - Color-coded areas for sensor detection
    - Starting positions for robots
    - Real-time mission progress tracking
    """

    # Collision types
    BORDER_COLLISION_TYPE = 1
    OBSTACLE_COLLISION_TYPE = 2
    MISSION_OBJECT_COLLISION_TYPE = 3

    def __init__(self, config: Optional[MapConfig] = None):
        """
        Initialize the game map.

        Args:
            config: Map configuration settings
        """
        self.config = config or MapConfig()

        # Map elements
        self.obstacles: List[Obstacle] = []
        self.color_zones: List[ColorZone] = []
        self.mission_areas: List[MissionArea] = []

        # Mission management
        self.mission_manager = MissionManager()

        # Physics bodies (will be populated when added to space)
        self.border_bodies: List[pymunk.Body] = []
        self.obstacle_bodies: List[pymunk.Body] = []
        self.mission_object_bodies: Dict[str, pymunk.Body] = {}

        # Starting positions
        self.robot_start_positions: List[Tuple[float, float, float]] = [
            (200, 600, 0),  # Default start position (x, y, angle)
        ]

        # Mission tracking
        self.mission_objects: Dict[str, Dict[str, Any]] = {}  # Track movable mission objects

        # Rendering surfaces
        self.base_surface: Optional[pygame.Surface] = None
        self.mission_overlay: Optional[pygame.Surface] = None
        self.start_positions: Dict[str, Tuple[float, float, float]] = {}

        # Map metadata
        self.name = "Default Map"
        self.season = "2024"
        self.description = "A basic FLL game map"

        # Setup default map
        self._setup_default_map()

    def _setup_default_map(self):
        """Setup a default map with basic elements."""
        # Add border walls
        self._create_borders()

        # Add some sample obstacles
        self.add_obstacle(Obstacle(
            name="Center Block",
            x=0, y=0,
            width=200, height=100,
            color=(139, 69, 19)  # Brown
        ))

        self.add_obstacle(Obstacle(
            name="Left Barrier",
            x=-800, y=200,
            width=300, height=50,
            angle=45,
            color=(100, 100, 100)  # Gray
        ))

        # Add color zones
        self.add_color_zone(ColorZone(
            name="Red Zone",
            x=-600, y=-300,
            width=300, height=200,
            color=(255, 0, 0)
        ))

        self.add_color_zone(ColorZone(
            name="Blue Zone",
            x=600, y=-300,
            width=300, height=200,
            color=(0, 0, 255)
        ))

        self.add_color_zone(ColorZone(
            name="Green Line",
            x=0, y=400,
            width=1000, height=50,
            color=(0, 255, 0)
        ))

        # Add starting positions
        self.start_positions["home"] = (-1000, -400, 0)  # x, y, angle
        self.start_positions["away"] = (1000, 400, 180)

        # Add sample missions
        self._setup_sample_missions()

    def _create_borders(self):
        """Create border walls around the field."""
        thickness = self.config.border_thickness
        w = self.config.width
        h = self.config.height

        # Border obstacles (will be added to physics when map is added to space)
        borders = [
            # Top wall
            Obstacle("top_border", 0, h/2 + thickness/2, w + 2*thickness, thickness),
            # Bottom wall
            Obstacle("bottom_border", 0, -h/2 - thickness/2, w + 2*thickness, thickness),
            # Left wall
            Obstacle("left_border", -w/2 - thickness/2, 0, thickness, h),
            # Right wall
            Obstacle("right_border", w/2 + thickness/2, 0, thickness, h),
        ]

        for border in borders:
            border.color = self.config.border_color
            self.obstacles.append(border)

    def _setup_sample_missions(self):
        """Setup sample missions for demonstration (disabled)."""
        # Sample missions used a legacy Mission API and are disabled to
        # avoid conflicts with the unified mission system. Use the
        # season loader instead via load_fll_season_map.
        return None

    def load_fll_season_map(self, season: str = "2024-SUBMERGED") -> None:
        """
        Load a complete FLL season map with missions and obstacles.

        Args:
            season: FLL season identifier
        """
        if season == "2024-SUBMERGED":
            self._create_submerged_2024_map()
        else:
            raise ValueError(f"Unknown FLL season: {season}")

        # Load corresponding missions
        self.mission_manager.load_fll_season(season)

        # Create mission area overlays
        self._create_mission_overlays()

    def _create_submerged_2024_map(self) -> None:
        """Create the 2024 SUBMERGED season game map."""

        # Clear existing elements
        self.obstacles.clear()
        self.color_zones.clear()
        self.mission_areas.clear()

        # Add FLL 2024 SUBMERGED obstacles and features

        # Base Station area (starting area)
        self.add_color_zone(ColorZone(
            name="base_station",
            x=200, y=600, width=400, height=400,
            color=(240, 240, 240),  # Light gray
            sensor_value="white"
        ))

        # Coral Nursery area
        self.add_obstacle(Obstacle(
            name="coral_nursery_walls",
            x=1800, y=900, width=200, height=200,
            color=(139, 69, 19),  # Brown
            is_movable=False
        ))

        # Coral samples (movable mission objects)
        self.add_obstacle(Obstacle(
            name="coral_sample_1",
            x=1200, y=800, width=50, height=50,
            color=(255, 127, 80),  # Coral color
            is_movable=True,
            mass=0.2,
            mission_related=True,
            object_id="coral_sample"
        ))

        # Shark area
        self.add_obstacle(Obstacle(
            name="shark_obstacle",
            x=600, y=400, width=100, height=200,
            color=(70, 70, 70),  # Dark gray
            is_movable=True,
            mass=0.5,
            mission_related=True,
            object_id="shark"
        ))

        # Underwater obstacles
        obstacles_positions = [
            (800, 300, 80, 60),
            (1000, 500, 60, 100),
            (1400, 700, 90, 70),
            (1600, 300, 70, 80)
        ]

        for i, (x, y, w, h) in enumerate(obstacles_positions):
            self.add_obstacle(Obstacle(
                name=f"underwater_obstacle_{i+1}",
                x=x, y=y, width=w, height=h,
                color=(0, 100, 150),  # Deep blue
                is_movable=False
            ))

        # Color zones for navigation
        color_zones = [
            ("red_zone", 1000, 200, 100, 100, (255, 0, 0), "red"),
            ("blue_zone", 1200, 400, 100, 100, (0, 0, 255), "blue"),
            ("green_zone", 1400, 600, 100, 100, (0, 255, 0), "green"),
            ("yellow_zone", 1600, 800, 100, 100, (255, 255, 0), "yellow")
        ]

        for name, x, y, w, h, color, sensor_val in color_zones:
            self.add_color_zone(ColorZone(
                name=name, x=x, y=y, width=w, height=h,
                color=color, sensor_value=sensor_val
            ))

        # Kraken treasure area (precision parking)
        self.add_color_zone(ColorZone(
            name="treasure_marker",
            x=1200, y=400, width=30, height=30,
            color=(0, 0, 255),  # Blue treasure marker
            sensor_value="blue"
        ))

    def _create_mission_overlays(self) -> None:
        """Create visual overlays for mission areas."""

        # Get missions from mission manager
        for mission in self.mission_manager.missions.values():

            # Extract mission areas from conditions
            for condition in mission.conditions:
                if condition.condition_type in ["robot_in_area", "object_in_area", "robot_at_position"]:

                    area_params = self._extract_area_from_condition(condition)
                    if area_params:
                        mission_area = MissionArea(
                            mission_id=mission.mission_id,
                            area_type=area_params["type"],
                            parameters=area_params,
                            color=self._get_mission_color(mission.difficulty)
                        )
                        self.mission_areas.append(mission_area)

    def _extract_area_from_condition(self, condition) -> Optional[Dict[str, Any]]:
        """Extract area parameters from mission condition."""
        params = condition.parameters

        if "circle" in params:
            return {
                "type": "circle",
                "x": params["circle"]["x"],
                "y": params["circle"]["y"],
                "radius": params["circle"]["radius"]
            }
        elif "rectangle" in params:
            return {
                "type": "rectangle",
                "x": params["rectangle"]["x"],
                "y": params["rectangle"]["y"],
                "width": params["rectangle"]["width"],
                "height": params["rectangle"]["height"]
            }
        elif "x" in params and "y" in params:
            return {
                "type": "point",
                "x": params["x"],
                "y": params["y"],
                "tolerance": params.get("tolerance", 10.0)
            }

        return None

    def _get_mission_color(self, difficulty) -> Tuple[int, int, int]:
        """Get color based on mission difficulty."""
        from .mission import MissionDifficulty

        color_map = {
            MissionDifficulty.BEGINNER: (0, 255, 0),     # Green
            MissionDifficulty.INTERMEDIATE: (255, 165, 0), # Orange
            MissionDifficulty.ADVANCED: (255, 0, 0),     # Red
            MissionDifficulty.EXPERT: (128, 0, 128)      # Purple
        }
        return color_map.get(difficulty, (128, 128, 128))

    def add_obstacle(self, obstacle: Obstacle) -> None:
        """Add an obstacle to the map."""
        self.obstacles.append(obstacle)

        # Track mission-related objects
        if obstacle.mission_related and obstacle.object_id:
            self.mission_objects[obstacle.object_id] = {
                "x": obstacle.x,
                "y": obstacle.y,
                "width": obstacle.width,
                "height": obstacle.height,
                "is_movable": obstacle.is_movable,
                "name": obstacle.name
            }

    def add_color_zone(self, zone: ColorZone) -> None:
        """Add a color zone to the map."""
        self.color_zones.append(zone)

    def add_mission(self, mission: Mission) -> None:
        """
        Add a mission to the map via the mission manager and refresh
        overlays.
        """
        self.mission_manager.add_mission(mission)
        # Rebuild overlays to include areas derived from mission conditions
        self.mission_areas.clear()
        self._create_mission_overlays()

    def get_color_at_position(self, x: float, y: float) -> Optional[str]:
        """
        Get the color sensor reading at a specific position.

        Args:
            x, y: Position coordinates in mm

        Returns:
            Color name if position is in a color zone, None otherwise
        """
        for zone in self.color_zones:
            # Check if position is within zone
            left = zone.x - zone.width / 2
            right = zone.x + zone.width / 2
            top = zone.y - zone.height / 2
            bottom = zone.y + zone.height / 2

            if left <= x <= right and top <= y <= bottom:
                return zone.sensor_value or "unknown"

        return None

    def get_obstacles_near_position(self, x: float, y: float, radius: float) -> List[Obstacle]:
        """
        Get obstacles within a certain radius of a position.

        Args:
            x, y: Center position
            radius: Search radius in mm

        Returns:
            List of nearby obstacles
        """
        nearby = []
        for obstacle in self.obstacles:
            distance = math.sqrt((obstacle.x - x)**2 + (obstacle.y - y)**2)
            if distance <= radius:
                nearby.append(obstacle)
        return nearby

    def is_position_valid(self, x: float, y: float, robot_radius: float = 50.0) -> bool:
        """
        Check if a position is valid for robot placement (no collisions).

        Args:
            x, y: Position to check
            robot_radius: Robot collision radius

        Returns:
            True if position is valid
        """
        # Check boundaries
        if (x - robot_radius < 0 or x + robot_radius > self.config.width or
            y - robot_radius < 0 or y + robot_radius > self.config.height):
            return False

        # Check obstacle collisions
        for obstacle in self.obstacles:
            if not obstacle.is_movable:  # Only check fixed obstacles
                # Simple box collision check
                obstacle_left = obstacle.x - obstacle.width / 2
                obstacle_right = obstacle.x + obstacle.width / 2
                obstacle_top = obstacle.y - obstacle.height / 2
                obstacle_bottom = obstacle.y + obstacle.height / 2

                robot_left = x - robot_radius
                robot_right = x + robot_radius
                robot_top = y - robot_radius
                robot_bottom = y + robot_radius

                if (robot_right >= obstacle_left and robot_left <= obstacle_right and
                    robot_bottom >= obstacle_top and robot_top <= obstacle_bottom):
                    return False

        return True

    def get_optimal_path(self, start: Tuple[float, float],
                        end: Tuple[float, float]) -> List[Tuple[float, float]]:
        """
        Calculate optimal path between two points avoiding obstacles using A*.
        Args:
            start: Starting position (x, y)
            end: Target position (x, y)
        Returns:
            List of waypoints forming optimal path
        """
        # Grid parameters
        grid_size = 50.0  # mm per cell
        width = int(self.config.width // grid_size)
        height = int(self.config.height // grid_size)

        def to_grid(pos):
            return (int(pos[0] // grid_size), int(pos[1] // grid_size))
        def to_world(cell):
            return (cell[0] * grid_size + grid_size/2, cell[1] * grid_size + grid_size/2)

        start_cell = to_grid(start)
        end_cell = to_grid(end)

        # Build obstacle set
        obstacle_cells = set()
        for obs in self.obstacles:
            if not obs.is_movable:
                min_x = int((obs.x - obs.width/2) // grid_size)
                max_x = int((obs.x + obs.width/2) // grid_size)
                min_y = int((obs.y - obs.height/2) // grid_size)
                max_y = int((obs.y + obs.height/2) // grid_size)
                for x in range(min_x, max_x+1):
                    for y in range(min_y, max_y+1):
                        obstacle_cells.add((x, y))

        def neighbors(cell):
            x, y = cell
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in obstacle_cells:
                    yield (nx, ny)

        # A* search
        open_set = []
        heapq.heappush(open_set, (0, start_cell))
        came_from = {}
        g_score = {start_cell: 0}
        f_score = {start_cell: abs(start_cell[0]-end_cell[0]) + abs(start_cell[1]-end_cell[1])}

        while open_set:
            _, current = heapq.heappop(open_set)
            if current == end_cell:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return [to_world(cell) for cell in path]
            for neighbor in neighbors(current):
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + abs(neighbor[0]-end_cell[0]) + abs(neighbor[1]-end_cell[1])
                    f_score[neighbor] = f
                    heapq.heappush(open_set, (f, neighbor))
        # No path found
        return [start, end]

    def export_map_config(self, filename: str) -> None:
        """Export current map configuration to file."""
        config_data = {
            "config": {
                "width": self.config.width,
                "height": self.config.height,
                "border_thickness": self.config.border_thickness
            },
            "obstacles": [
                {
                    "name": obs.name,
                    "x": obs.x, "y": obs.y,
                    "width": obs.width, "height": obs.height,
                    "angle": obs.angle,
                    "color": obs.color,
                    "is_movable": obs.is_movable,
                    "mass": obs.mass,
                    "mission_related": obs.mission_related,
                    "object_id": obs.object_id
                }
                for obs in self.obstacles
            ],
            "color_zones": [
                {
                    "name": zone.name,
                    "x": zone.x, "y": zone.y,
                    "width": zone.width, "height": zone.height,
                    "color": zone.color,
                    "sensor_value": zone.sensor_value
                }
                for zone in self.color_zones
            ],
            "robot_start_positions": self.robot_start_positions
        }

        with open(filename, 'w') as f:
            json.dump(config_data, f, indent=2)

    def load_map_config(self, filename: str) -> None:
        """Load map configuration from file."""
        with open(filename, 'r') as f:
            config_data = json.load(f)

        # Update config
        config_dict = config_data.get("config", {})
        self.config.width = config_dict.get("width", self.config.width)
        self.config.height = config_dict.get("height", self.config.height)

        # Load obstacles
        self.obstacles.clear()
        for obs_data in config_data.get("obstacles", []):
            obstacle = Obstacle(
                name=obs_data["name"],
                x=obs_data["x"], y=obs_data["y"],
                width=obs_data["width"], height=obs_data["height"],
                angle=obs_data.get("angle", 0.0),
                color=tuple(obs_data["color"]),
                is_movable=obs_data.get("is_movable", False),
                mass=obs_data.get("mass", 1.0),
                mission_related=obs_data.get("mission_related", False),
                object_id=obs_data.get("object_id")
            )
            self.add_obstacle(obstacle)

        # Load color zones
        self.color_zones.clear()
        for zone_data in config_data.get("color_zones", []):
            zone = ColorZone(
                name=zone_data["name"],
                x=zone_data["x"], y=zone_data["y"],
                width=zone_data["width"], height=zone_data["height"],
                color=tuple(zone_data["color"]),
                sensor_value=zone_data.get("sensor_value", "")
            )
            self.add_color_zone(zone)

        # Load start positions
        self.robot_start_positions = config_data.get("robot_start_positions", [(200, 600, 0)])

    def add_to_space(self, space: pymunk.Space) -> None:
        """
        Add map elements to the physics space.

        Args:
            space: Pymunk physics space to add elements to
        """
        # Add border walls
        border_walls = [
            # Top wall
            ((0, 0), (self.config.width, 0)),
            # Bottom wall
            ((0, self.config.height), (self.config.width, self.config.height)),
            # Left wall
            ((0, 0), (0, self.config.height)),
            # Right wall
            ((self.config.width, 0), (self.config.width, self.config.height))
        ]

        for start, end in border_walls:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            shape = pymunk.Segment(body, start, end, self.config.border_thickness/2)
            shape.friction = 0.7
            shape.collision_type = self.BORDER_COLLISION_TYPE
            space.add(body, shape)
            self.border_bodies.append(body)

        # Add obstacles to physics space
        for obstacle in self.obstacles:
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            # Create a box shape for the obstacle
            shape = pymunk.Poly.create_box(body, (obstacle.width, obstacle.height))
            shape.body.position = obstacle.x + obstacle.width/2, obstacle.y + obstacle.height/2
            shape.friction = 0.7
            shape.collision_type = self.OBSTACLE_COLLISION_TYPE
            space.add(body, shape)
            self.obstacle_bodies.append(body)

    def update(self, dt: float) -> None:
        """
        Update the game map state.

        Args:
            dt: Time delta in seconds
        """
        # Update mission manager if available
        if hasattr(self, 'mission_manager') and self.mission_manager:
            # Update mission timers and states
            pass

        # Update any animated elements
        # (placeholder for future animation system)
        pass

    def reset(self) -> None:
        """Reset the game map to initial state."""
        # Reset mission states
        if hasattr(self, 'mission_manager') and self.mission_manager:
            self.mission_manager.reset_session()

        # Reset any movable objects to initial positions
        self.mission_objects.clear()

        # Reset start positions if needed
        pass

    def render(self, renderer) -> None:
        """
        Render the game map using the provided renderer.

        Args:
            renderer: Rendering system to draw the map
        """
        # Render base map surface
        if hasattr(renderer, 'draw_map'):
            renderer.draw_map(self)

        # Render obstacles
        for obstacle in self.obstacles:
            if hasattr(renderer, 'draw_obstacle'):
                renderer.draw_obstacle(obstacle)

        # Render color zones
        for zone in self.color_zones:
            if hasattr(renderer, 'draw_color_zone'):
                renderer.draw_color_zone(zone)

        # Render mission areas
        for area in self.mission_areas:
            if hasattr(renderer, 'draw_mission_area'):
                renderer.draw_mission_area(area)

    def get_mission_states(self) -> Dict[str, Any]:
        """
        Get current mission states and progress.

        Returns:
            Dictionary containing mission state information
        """
        if hasattr(self, 'mission_manager') and self.mission_manager:
            return {
                'active_missions': len(self.mission_manager.missions),
                'completed_missions': 0,  # Placeholder
                'total_score': 0,  # Placeholder
                'time_remaining': 150.0  # Standard FLL match time
            }

        return {
            'active_missions': 0,
            'completed_missions': 0,
            'total_score': 0,
            'time_remaining': 150.0
        }

    def __repr__(self) -> str:
        return (f"GameMap(size={self.config.width}x{self.config.height}, "
                f"obstacles={len(self.obstacles)}, "
                f"color_zones={len(self.color_zones)}, "
                f"missions={len(self.mission_manager.missions)})")


# Example usage
if __name__ == "__main__":
    # Create a game map
    game_map = GameMap()

    # Load FLL 2024 SUBMERGED season
    game_map.load_fll_season_map("2024-SUBMERGED")

    print(f"Loaded map: {game_map}")
    print(f"Available missions: {[m.name for m in game_map.get_available_missions()]}")

    # Start a mission
    available_missions = game_map.get_available_missions()
    if available_missions:
        mission = available_missions[0]
        game_map.start_mission(mission.mission_id)
        print(f"Started mission: {mission.name}")

        # Simulate robot movement
        robot_state = {
            'position': {'x': 1800, 'y': 900, 'angle': 0},
            'sensors': {'color': game_map.get_color_at_position(1800, 900)},
            'speed': 100.0,
            'energy_used': 10.0,
            'distance_traveled': 200.0
        }

        # Update mission progress
        game_map.update_mission_progress(robot_state)

        # Check progress
        progress = game_map.get_mission_progress()
        print(f"Mission progress: {progress['active_mission']}")

    # Export map configuration
    game_map.export_map_config("submerged_2024_map.json")
    print("Map configuration exported!")
