"""
Base sensor class for all robot sensors.

This module defines the common interface and behavior for all sensors
used in the FLL robot simulation.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple
import math


class Sensor(ABC):
    """
    Abstract base class for all robot sensors.
    
    All sensors must implement the basic interface defined here:
    - Reading sensor values
    - Updating sensor state
    - Rendering sensor visualization
    - Attaching to robots
    """
    
    def __init__(self, name: str, position: Tuple[float, float] = (0, 0), 
                 direction: float = 0):
        """
        Initialize the sensor.
        
        Args:
            name: Unique name for this sensor
            position: Position relative to robot center (x, y) in mm
            direction: Direction relative to robot heading in degrees
        """
        self.name = name
        self.position = position  # (x, y) offset from robot center
        self.direction = direction  # degrees relative to robot
        self.robot = None  # Will be set when attached
        self.enabled = True
        self.last_reading = None
    
    @abstractmethod
    def get_reading(self) -> Any:
        """
        Get the current sensor reading.
        
        Returns:
            The current sensor value (type depends on sensor)
        """
        pass
    
    @abstractmethod
    def update(self, dt: float):
        """
        Update the sensor state.
        
        Args:
            dt: Time delta in seconds
        """
        pass
    
    def attach_to_robot(self, robot):
        """
        Attach this sensor to a robot.
        
        Args:
            robot: The robot this sensor is attached to
        """
        self.robot = robot
    
    def get_world_position(self) -> Tuple[float, float]:
        """
        Get the sensor's world position based on robot position and orientation.
        
        Returns:
            (x, y) world coordinates of the sensor
        """
        if not self.robot:
            return self.position
        
        # Transform relative position to world coordinates
        robot_angle_rad = math.radians(self.robot.angle)
        cos_a = math.cos(robot_angle_rad)
        sin_a = math.sin(robot_angle_rad)
        
        # Rotate position offset by robot angle
        rel_x, rel_y = self.position
        world_x = self.robot.x + (rel_x * cos_a - rel_y * sin_a)
        world_y = self.robot.y + (rel_x * sin_a + rel_y * cos_a)
        
        return world_x, world_y
    
    def get_world_direction(self) -> float:
        """
        Get the sensor's world direction.
        
        Returns:
            Direction in degrees in world coordinates
        """
        if not self.robot:
            return self.direction
        
        return (self.robot.angle + self.direction) % 360
    
    def render(self, renderer):
        """
        Render the sensor (default implementation - can be overridden).
        
        Args:
            renderer: The renderer to draw with
        """
        if not self.enabled:
            return
        
        world_pos = self.get_world_position()
        
        # Draw a small circle to represent the sensor
        renderer.draw_circle(world_pos[0], world_pos[1], 5, (0, 255, 0))
        
        # Draw direction indicator for directional sensors
        if hasattr(self, 'max_range') or self.direction != 0:
            world_dir = self.get_world_direction()
            dir_rad = math.radians(world_dir)
            length = getattr(self, 'max_range', 50) / 10  # Scale down for visualization
            
            end_x = world_pos[0] + math.cos(dir_rad) * length
            end_y = world_pos[1] + math.sin(dir_rad) * length
            
            renderer.draw_line(world_pos, (end_x, end_y), (0, 255, 0), 1)
    
    def reset(self):
        """Reset the sensor to its initial state."""
        self.last_reading = None
    
    def enable(self):
        """Enable the sensor."""
        self.enabled = True
    
    def disable(self):
        """Disable the sensor."""
        self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if the sensor is enabled."""
        return self.enabled
