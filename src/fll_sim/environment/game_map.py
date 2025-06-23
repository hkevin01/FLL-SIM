"""
Game map implementation for FLL challenges.

This module defines the game map/field where the robot operates,
including obstacles, missions, and scoring areas.
"""

import math
import yaml
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import pymunk
import pygame

from .mission import Mission, MissionStatus


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


class GameMap:
    """
    Game map representing the FLL playing field.
    
    The map includes:
    - Physical boundaries and obstacles
    - Mission areas and scoring zones
    - Color-coded areas for sensor detection
    - Starting positions for robots
    """
    
    # Collision type for map obstacles
    obstacle_collision_type = 2
    
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
        self.missions: List[Mission] = []
        
        # Physics bodies (will be populated when added to space)
        self.border_bodies: List[pymunk.Body] = []
        self.obstacle_bodies: List[pymunk.Body] = []
        
        # Starting positions
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
        """Setup sample missions for demonstration."""
        from .mission import Mission, MissionType
        
        # Mission 1: Visit red zone
        mission1 = Mission(
            name="Visit Red Zone",
            description="Drive to and stop in the red zone",
            mission_type=MissionType.AREA_VISIT,
            target_area=(-600, -300, 300, 200),  # x, y, width, height
            points=20,
            time_limit=30.0
        )
        
        # Mission 2: Push object
        mission2 = Mission(
            name="Move Center Block", 
            description="Push the center block to the blue zone",
            mission_type=MissionType.OBJECT_TRANSPORT,
            target_object="Center Block",
            target_area=(600, -300, 300, 200),
            points=40,
            time_limit=60.0
        )
        
        self.add_mission(mission1)
        self.add_mission(mission2)
    
    def add_obstacle(self, obstacle: Obstacle):
        """Add an obstacle to the map."""
        self.obstacles.append(obstacle)
    
    def add_color_zone(self, zone: ColorZone):
        """Add a color zone to the map.""" 
        self.color_zones.append(zone)
    
    def add_mission(self, mission: Mission):
        """Add a mission to the map."""
        self.missions.append(mission)
    
    def get_starting_position(self, position_name: str = "home") -> Tuple[float, float, float]:
        """
        Get a starting position by name.
        
        Args:
            position_name: Name of starting position
            
        Returns:
            (x, y, angle) tuple
        """
        return self.start_positions.get(position_name, (0, 0, 0))
    
    def add_to_space(self, space: pymunk.Space):
        """Add map elements to the physics space."""
        # Add obstacles to physics
        for obstacle in self.obstacles:
            body, shape = self._create_obstacle_physics(obstacle)
            space.add(body, shape)
            self.obstacle_bodies.append(body)
    
    def _create_obstacle_physics(self, obstacle: Obstacle) -> Tuple[pymunk.Body, pymunk.Shape]:
        """
        Create physics body and shape for an obstacle.
        
        Args:
            obstacle: Obstacle to create physics for
            
        Returns:
            (body, shape) tuple
        """
        if obstacle.is_movable:
            # Dynamic body for movable objects
            moment = pymunk.moment_for_box(obstacle.mass, (obstacle.width, obstacle.height))
            body = pymunk.Body(obstacle.mass, moment)
        else:
            # Static body for fixed obstacles
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
        
        body.position = obstacle.x, obstacle.y
        body.angle = math.radians(obstacle.angle)
        
        # Create box shape
        shape = pymunk.Poly.create_box(body, (obstacle.width, obstacle.height))
        shape.friction = 0.7
        shape.collision_type = self.obstacle_collision_type
        
        return body, shape
    
    def get_color_at_position(self, x: float, y: float) -> Tuple[int, int, int]:
        """
        Get the color at a specific position on the map.
        
        Args:
            x: X coordinate in mm
            y: Y coordinate in mm
            
        Returns:
            RGB color tuple
        """
        # Check color zones
        for zone in self.color_zones:
            if self._point_in_rectangle(x, y, zone):
                return zone.color
        
        # Default to surface color
        return self.config.surface_color
    
    def _point_in_rectangle(self, x: float, y: float, rect) -> bool:
        """
        Check if a point is inside a rectangle.
        
        Args:
            x: Point X coordinate
            y: Point Y coordinate
            rect: Rectangle object with x, y, width, height, angle
            
        Returns:
            True if point is inside rectangle
        """
        # Transform point to rectangle's local coordinate system
        dx = x - rect.x
        dy = y - rect.y
        
        # Rotate by negative angle to align with rectangle
        angle_rad = -math.radians(rect.angle)
        local_x = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
        local_y = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
        
        # Check if inside axis-aligned rectangle
        return (abs(local_x) <= rect.width / 2 and 
                abs(local_y) <= rect.height / 2)
    
    def update(self, dt: float):
        """Update the map state (missions, animations, etc.)."""
        # Update missions
        for mission in self.missions:
            mission.update(dt)
    
    def render(self, renderer):
        """Render the game map."""
        # Render field surface
        self._render_surface(renderer)
        
        # Render grid if enabled
        if self.config.show_grid:
            self._render_grid(renderer)
        
        # Render color zones
        for zone in self.color_zones:
            self._render_color_zone(renderer, zone)
        
        # Render obstacles
        for obstacle in self.obstacles:
            self._render_obstacle(renderer, obstacle)
        
        # Render missions
        for mission in self.missions:
            mission.render(renderer)
        
        # Render starting positions
        self._render_start_positions(renderer)
    
    def _render_surface(self, renderer):
        """Render the field surface."""
        w = self.config.width
        h = self.config.height
        
        renderer.draw_rect(
            0, 0, w, h, 0,
            self.config.surface_color
        )
    
    def _render_grid(self, renderer):
        """Render measurement grid."""
        w = self.config.width
        h = self.config.height
        spacing = self.config.grid_spacing
        
        # Vertical lines
        x = -w/2
        while x <= w/2:
            renderer.draw_line(
                (x, -h/2), (x, h/2),
                self.config.grid_color, 1
            )
            x += spacing
        
        # Horizontal lines  
        y = -h/2
        while y <= h/2:
            renderer.draw_line(
                (-w/2, y), (w/2, y),
                self.config.grid_color, 1
            )
            y += spacing
    
    def _render_color_zone(self, renderer, zone: ColorZone):
        """Render a color zone."""
        renderer.draw_rect(
            zone.x, zone.y,
            zone.width, zone.height,
            zone.angle, zone.color
        )
        
        # Draw zone label
        renderer.draw_text(
            zone.name,
            zone.x, zone.y,
            (255, 255, 255), size=14
        )
    
    def _render_obstacle(self, renderer, obstacle: Obstacle):
        """Render an obstacle."""
        renderer.draw_rect(
            obstacle.x, obstacle.y,
            obstacle.width, obstacle.height,
            obstacle.angle, obstacle.color
        )
        
        # Draw obstacle label for non-border objects
        if not obstacle.name.endswith("_border"):
            renderer.draw_text(
                obstacle.name,
                obstacle.x, obstacle.y,
                (255, 255, 255), size=12
            )
    
    def _render_start_positions(self, renderer):
        """Render starting positions."""
        for name, (x, y, angle) in self.start_positions.items():
            # Draw start position marker
            renderer.draw_circle(x, y, 30, (0, 255, 0), filled=False, width=3)
            
            # Draw direction arrow
            angle_rad = math.radians(angle)
            end_x = x + math.cos(angle_rad) * 40
            end_y = y + math.sin(angle_rad) * 40
            renderer.draw_line((x, y), (end_x, end_y), (0, 255, 0), 3)
            
            # Draw label
            renderer.draw_text(name, x, y - 50, (0, 255, 0), size=14)
    
    def reset(self):
        """Reset the map to initial state.""" 
        # Reset missions
        for mission in self.missions:
            mission.reset()
        
        # Reset movable obstacles to initial positions
        # (This would need to store initial positions)
        pass
    
    def get_mission_states(self) -> Dict[str, Any]:
        """Get current state of all missions."""
        return {
            mission.name: {
                "status": mission.status,
                "progress": mission.progress,
                "points_earned": mission.points_earned,
                "time_elapsed": mission.time_elapsed
            }
            for mission in self.missions
        }
    
    def calculate_total_score(self) -> int:
        """Calculate total score from completed missions."""
        return sum(mission.points_earned for mission in self.missions)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'GameMap':
        """
        Load a game map from a YAML configuration file.
        
        Args:
            file_path: Path to YAML configuration file
            
        Returns:
            Loaded GameMap instance
        """
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Create map with loaded configuration
        game_map = cls()
        
        # Load basic properties
        game_map.name = data.get('name', 'Loaded Map')
        game_map.season = data.get('season', '2024')
        game_map.description = data.get('description', '')
        
        # Load obstacles
        for obs_data in data.get('obstacles', []):
            obstacle = Obstacle(**obs_data)
            game_map.add_obstacle(obstacle)
        
        # Load color zones
        for zone_data in data.get('color_zones', []):
            zone = ColorZone(**zone_data)
            game_map.add_color_zone(zone)
        
        # Load start positions
        game_map.start_positions = data.get('start_positions', {})
        
        return game_map
    
    @classmethod
    def load_season(cls, season_name: str) -> 'GameMap':
        """
        Load a predefined season map.
        
        Args:
            season_name: Name of the season (e.g., "2024-submerged")
            
        Returns:
            GameMap for the specified season
        """
        # For now, return a default map
        # In a full implementation, this would load from predefined configs
        return cls()
