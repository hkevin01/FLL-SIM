"""
Rendering system for FLL-Sim visualization.

This module provides a high-level rendering interface that abstracts
pygame drawing operations and provides utilities for 2D graphics,
coordinate transformations, and visual effects.
"""

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

import pygame
import pymunk
import pymunk.pygame_util


@dataclass
class Camera:
    """Camera configuration for viewport management."""
    x: float = 0.0
    y: float = 0.0
    zoom: float = 1.0
    follow_target: Optional[Tuple[float, float]] = None
    smooth_follow: bool = True
    follow_speed: float = 5.0


class Renderer:
    """
    Main rendering system for FLL-Sim.
    
    Provides high-level drawing functions with coordinate transformation,
    camera management, and visual effects for the simulation.
    """
    
    def __init__(self, screen: pygame.Surface, space: Optional[pymunk.Space] = None):
        """
        Initialize the renderer.
        
        Args:
            screen: Pygame display surface
            space: Optional pymunk physics space for debug rendering
        """
        self.screen = screen
        self.space = space
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Camera system
        self.camera = Camera()
        
        # Physics debug renderer
        if space:
            self.debug_options = pymunk.pygame_util.DrawOptions(screen)
        
        # Pre-loaded fonts for performance
        self.fonts = {
            'small': pygame.font.Font(None, 18),
            'medium': pygame.font.Font(None, 24),
            'large': pygame.font.Font(None, 36),
        }
        
        # Colors
        self.colors = {
            'background': (50, 50, 50),
            'grid': (80, 80, 80),
            'robot': (255, 200, 0),
            'obstacle': (150, 75, 0),
            'mission_area': (0, 255, 0, 100),
            'mission_complete': (0, 200, 0, 150),
            'sensor_range': (0, 100, 255, 50),
            'path': (255, 255, 0),
            'waypoint': (255, 100, 100),
            'text': (255, 255, 255),
            'debug': (255, 0, 255),
        }
    
    def update_camera(self, dt: float):
        """Update camera position and zoom."""
        if self.camera.follow_target and self.camera.smooth_follow:
            target_x, target_y = self.camera.follow_target
            
            # Smooth camera following
            dx = target_x - self.camera.x
            dy = target_y - self.camera.y
            
            speed = self.camera.follow_speed * dt
            self.camera.x += dx * speed
            self.camera.y += dy * speed
        elif self.camera.follow_target:
            # Instant camera following
            self.camera.x, self.camera.y = self.camera.follow_target
    
    def set_camera_follow(self, target: Tuple[float, float], smooth: bool = True):
        """Set camera to follow a target position."""
        self.camera.follow_target = target
        self.camera.smooth_follow = smooth
    
    def set_camera_position(self, x: float, y: float):
        """Set camera position directly."""
        self.camera.x = x
        self.camera.y = y
        self.camera.follow_target = None
    
    def set_camera_zoom(self, zoom: float):
        """Set camera zoom level."""
        self.camera.zoom = max(0.1, min(5.0, zoom))
    
    def world_to_screen(self, world_pos: Tuple[float, float]) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates."""
        world_x, world_y = world_pos
        
        # Apply camera transformation
        screen_x = (world_x - self.camera.x) * self.camera.zoom + self.width / 2
        screen_y = (world_y - self.camera.y) * self.camera.zoom + self.height / 2
        
        return int(screen_x), int(screen_y)
    
    def screen_to_world(self, screen_pos: Tuple[int, int]) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates."""
        screen_x, screen_y = screen_pos
        
        # Apply inverse camera transformation
        world_x = (screen_x - self.width / 2) / self.camera.zoom + self.camera.x
        world_y = (screen_y - self.height / 2) / self.camera.zoom + self.camera.y
        
        return world_x, world_y
    
    def draw_background(self):
        """Draw the background and grid."""
        self.screen.fill(self.colors['background'])
        
        # Draw grid if zoomed in enough
        if self.camera.zoom > 0.5:
            self._draw_grid()
    
    def _draw_grid(self):
        """Draw a coordinate grid."""
        grid_size = 100  # Grid spacing in world units
        
        # Calculate visible world bounds
        top_left = self.screen_to_world((0, 0))
        bottom_right = self.screen_to_world((self.width, self.height))
        
        # Draw vertical lines
        start_x = int(top_left[0] // grid_size) * grid_size
        end_x = int(bottom_right[0] // grid_size + 1) * grid_size
        
        for world_x in range(start_x, end_x + grid_size, grid_size):
            start_screen = self.world_to_screen((world_x, top_left[1]))
            end_screen = self.world_to_screen((world_x, bottom_right[1]))
            
            if 0 <= start_screen[0] <= self.width:
                pygame.draw.line(self.screen, self.colors['grid'],
                               (start_screen[0], 0), (end_screen[0], self.height))
        
        # Draw horizontal lines
        start_y = int(top_left[1] // grid_size) * grid_size
        end_y = int(bottom_right[1] // grid_size + 1) * grid_size
        
        for world_y in range(start_y, end_y + grid_size, grid_size):
            start_screen = self.world_to_screen((top_left[0], world_y))
            end_screen = self.world_to_screen((bottom_right[0], world_y))
            
            if 0 <= start_screen[1] <= self.height:
                pygame.draw.line(self.screen, self.colors['grid'],
                               (0, start_screen[1]), (self.width, end_screen[1]))
    
    def draw_rect(self, x: float, y: float, width: float, height: float,
                  angle: float = 0, color: Tuple[int, int, int] = None,
                  border_width: int = 0, border_color: Tuple[int, int, int] = None):
        """Draw a rectangle with optional rotation."""
        if color is None:
            color = self.colors['robot']
        
        # Create rectangle surface
        rect_surface = pygame.Surface((width * self.camera.zoom, height * self.camera.zoom), pygame.SRCALPHA)
        rect_surface.fill(color)
        
        # Add border if specified
        if border_width > 0 and border_color:
            pygame.draw.rect(rect_surface, border_color, rect_surface.get_rect(), border_width)
        
        # Rotate if needed
        if angle != 0:
            rect_surface = pygame.transform.rotate(rect_surface, -angle)  # Negative for correct rotation
        
        # Get screen position and blit
        screen_pos = self.world_to_screen((x, y))
        rect = rect_surface.get_rect(center=screen_pos)
        self.screen.blit(rect_surface, rect)
    
    def draw_circle(self, x: float, y: float, radius: float,
                    color: Tuple[int, int, int] = None,
                    border_width: int = 0, border_color: Tuple[int, int, int] = None):
        """Draw a circle."""
        if color is None:
            color = self.colors['robot']
        
        screen_pos = self.world_to_screen((x, y))
        screen_radius = max(1, int(radius * self.camera.zoom))
        
        pygame.draw.circle(self.screen, color, screen_pos, screen_radius)
        
        if border_width > 0 and border_color:
            pygame.draw.circle(self.screen, border_color, screen_pos, screen_radius, border_width)
    
    def draw_line(self, start: Tuple[float, float], end: Tuple[float, float],
                  color: Tuple[int, int, int], width: int = 1):
        """Draw a line between two points."""
        start_screen = self.world_to_screen(start)
        end_screen = self.world_to_screen(end)
        
        pygame.draw.line(self.screen, color, start_screen, end_screen, width)
    
    def draw_polygon(self, points: List[Tuple[float, float]],
                     color: Tuple[int, int, int], border_width: int = 0,
                     border_color: Tuple[int, int, int] = None):
        """Draw a polygon."""
        screen_points = [self.world_to_screen(point) for point in points]
        
        pygame.draw.polygon(self.screen, color, screen_points)
        
        if border_width > 0 and border_color:
            pygame.draw.polygon(self.screen, border_color, screen_points, border_width)
    
    def draw_arc(self, x: float, y: float, radius: float, start_angle: float,
                 end_angle: float, color: Tuple[int, int, int], width: int = 1):
        """Draw an arc (partial circle)."""
        screen_pos = self.world_to_screen((x, y))
        screen_radius = max(1, int(radius * self.camera.zoom))
        
        # Create rect for arc
        rect = pygame.Rect(
            screen_pos[0] - screen_radius,
            screen_pos[1] - screen_radius,
            screen_radius * 2,
            screen_radius * 2
        )
        
        pygame.draw.arc(self.screen, color, rect,
                       math.radians(start_angle), math.radians(end_angle), width)
    
    def draw_arrow(self, start: Tuple[float, float], end: Tuple[float, float],
                   color: Tuple[int, int, int], width: int = 2, head_size: float = 10):
        """Draw an arrow from start to end."""
        # Draw main line
        self.draw_line(start, end, color, width)
        
        # Calculate arrowhead
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.sqrt(dx*dx + dy*dy)
        
        if length > 0:
            # Normalize direction
            dx /= length
            dy /= length
            
            # Calculate arrowhead points
            head_x = end[0] - head_size * dx
            head_y = end[1] - head_size * dy
            
            # Perpendicular vector for arrowhead width
            perp_x = -dy * head_size * 0.5
            perp_y = dx * head_size * 0.5
            
            arrow_points = [
                end,
                (head_x + perp_x, head_y + perp_y),
                (head_x - perp_x, head_y - perp_y)
            ]
            
            self.draw_polygon(arrow_points, color)
    
    def draw_text(self, text: str, x: float, y: float, font_size: str = 'medium',
                  color: Tuple[int, int, int] = None, center: bool = False):
        """Draw text at world coordinates."""
        if color is None:
            color = self.colors['text']
        
        font = self.fonts.get(font_size, self.fonts['medium'])
        text_surface = font.render(str(text), True, color)
        
        screen_pos = self.world_to_screen((x, y))
        
        if center:
            rect = text_surface.get_rect(center=screen_pos)
            self.screen.blit(text_surface, rect)
        else:
            self.screen.blit(text_surface, screen_pos)
    
    def draw_text_screen(self, text: str, x: int, y: int, font_size: str = 'medium',
                         color: Tuple[int, int, int] = None, center: bool = False):
        """Draw text at screen coordinates (for UI elements)."""
        if color is None:
            color = self.colors['text']
        
        font = self.fonts.get(font_size, self.fonts['medium'])
        text_surface = font.render(str(text), True, color)
        
        if center:
            rect = text_surface.get_rect(center=(x, y))
            self.screen.blit(text_surface, rect)
        else:
            self.screen.blit(text_surface, (x, y))
    
    def draw_sensor_range(self, x: float, y: float, direction: float, range_distance: float,
                          cone_angle: float = 30, color: Tuple[int, int, int] = None):
        """Draw sensor detection range as a cone."""
        if color is None:
            color = self.colors['sensor_range']
        
        # Create transparent surface for alpha blending
        temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Calculate cone points
        angle_rad = math.radians(direction)
        half_cone = math.radians(cone_angle / 2)
        
        # Center point
        center = self.world_to_screen((x, y))
        
        # End points of cone
        end1_world = (
            x + range_distance * math.cos(angle_rad - half_cone),
            y + range_distance * math.sin(angle_rad - half_cone)
        )
        end2_world = (
            x + range_distance * math.cos(angle_rad + half_cone),
            y + range_distance * math.sin(angle_rad + half_cone)
        )
        
        end1 = self.world_to_screen(end1_world)
        end2 = self.world_to_screen(end2_world)
        
        # Draw cone as polygon
        points = [center, end1, end2]
        pygame.draw.polygon(temp_surface, color, points)
        
        # Blit with transparency
        self.screen.blit(temp_surface, (0, 0))
    
    def draw_path(self, points: List[Tuple[float, float]], color: Tuple[int, int, int] = None,
                  width: int = 3, show_direction: bool = True):
        """Draw a path as connected line segments with optional direction arrows."""
        if color is None:
            color = self.colors['path']
        
        if len(points) < 2:
            return
        
        # Draw path segments
        for i in range(len(points) - 1):
            self.draw_line(points[i], points[i + 1], color, width)
        
        # Draw direction arrows
        if show_direction and len(points) >= 2:
            for i in range(0, len(points) - 1, max(1, len(points) // 5)):  # Show ~5 arrows
                if i + 1 < len(points):
                    start = points[i]
                    end = points[i + 1]
                    
                    # Draw arrow at midpoint
                    mid_x = (start[0] + end[0]) / 2
                    mid_y = (start[1] + end[1]) / 2
                    
                    # Small arrow in direction of movement
                    dx = end[0] - start[0]
                    dy = end[1] - start[1]
                    length = math.sqrt(dx*dx + dy*dy)
                    
                    if length > 0:
                        arrow_end = (mid_x + dx/length * 15, mid_y + dy/length * 15)
                        self.draw_arrow((mid_x, mid_y), arrow_end, color, 1, 8)
    
    def draw_waypoint(self, x: float, y: float, label: str = "", 
                      color: Tuple[int, int, int] = None, radius: float = 8):
        """Draw a waypoint marker."""
        if color is None:
            color = self.colors['waypoint']
        
        self.draw_circle(x, y, radius, color, 2, (255, 255, 255))
        
        if label:
            self.draw_text(label, x, y - radius - 10, 'small', center=True)
    
    def draw_physics_debug(self):
        """Draw physics debug visualization."""
        if self.space and self.debug_options:
            self.space.debug_draw(self.debug_options)
    
    def draw_mission_area(self, x: float, y: float, width: float, height: float,
                          completed: bool = False, label: str = ""):
        """Draw a mission area rectangle."""
        color = self.colors['mission_complete'] if completed else self.colors['mission_area']
        
        # Create transparent surface
        temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Calculate screen coordinates
        top_left = self.world_to_screen((x - width/2, y - height/2))
        bottom_right = self.world_to_screen((x + width/2, y + height/2))
        
        screen_width = bottom_right[0] - top_left[0]
        screen_height = bottom_right[1] - top_left[1]
        
        # Draw rectangle
        rect = pygame.Rect(top_left[0], top_left[1], screen_width, screen_height)
        pygame.draw.rect(temp_surface, color, rect)
        pygame.draw.rect(temp_surface, (255, 255, 255), rect, 2)
        
        self.screen.blit(temp_surface, (0, 0))
        
        # Draw label
        if label:
            self.draw_text(label, x, y, 'small', center=True)
