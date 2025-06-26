"""
Touch sensor simulation for contact detection.

This sensor simulates the LEGO EV3/SPIKE touch sensor that detects
physical contact with objects or surfaces.
"""

import math
from typing import Optional, Tuple

import pymunk

from .sensor_base import Sensor


class TouchSensor(Sensor):
    """
    Touch sensor for detecting physical contact.
    
    The sensor detects when the robot makes contact with objects
    and provides pressed/released state information.
    """
    
    def __init__(self, name: str, position: Tuple[float, float] = (0, 0),
                 direction: float = 0, detection_radius: float = 5.0):
        """
        Initialize the touch sensor.
        
        Args:
            name: Sensor name
            position: Position relative to robot center
            direction: Direction sensor is facing in degrees
            detection_radius: Detection radius in mm
        """
        super().__init__(name, position, direction)
        self.detection_radius = detection_radius
        self.is_pressed = False
        self.was_pressed = False  # Previous state for edge detection
        self.press_count = 0  # Number of times pressed
        
        # Contact detection parameters
        self.contact_threshold = 1.0  # Minimum contact force
        self.debounce_time = 0.1  # Debounce time in seconds
        self.last_state_change = 0.0
    
    def get_reading(self) -> bool:
        """Get the current touch sensor state."""
        return self.is_pressed
    
    def is_button_pressed(self) -> bool:
        """Check if touch sensor is currently pressed."""
        return self.is_pressed
    
    def was_button_pressed(self) -> bool:
        """Check if touch sensor was just pressed (rising edge)."""
        return self.is_pressed and not self.was_pressed
    
    def was_button_released(self) -> bool:
        """Check if touch sensor was just released (falling edge)."""
        return not self.is_pressed and self.was_pressed
    
    def get_press_count(self) -> int:
        """Get the number of times the sensor has been pressed."""
        return self.press_count
    
    def reset_press_count(self):
        """Reset the press count to zero."""
        self.press_count = 0
    
    def update(self, dt: float):
        """Update the touch sensor state."""
        if not self.enabled or not self.robot:
            return
        
        # Store previous state
        self.was_pressed = self.is_pressed
        
        # Check for contact
        self.is_pressed = self._detect_contact()
        
        # Handle debouncing
        current_time = getattr(self, 'simulation_time', 0.0)
        if self.is_pressed != self.was_pressed:
            if current_time - self.last_state_change >= self.debounce_time:
                self.last_state_change = current_time
                
                # Count button presses (rising edge)
                if self.is_pressed and not self.was_pressed:
                    self.press_count += 1
            else:
                # Too soon - revert to previous state
                self.is_pressed = self.was_pressed
        
        self.last_reading = self.is_pressed
    
    def _detect_contact(self) -> bool:
        """
        Detect if the sensor is in contact with an object.
        
        Returns:
            True if contact is detected
        """
        if not self.robot or not hasattr(self.robot, 'body') or not self.robot.body:
            return False
        
        space = self.robot.body.space
        if not space:
            return False
        
        # Get sensor world position
        sensor_pos = self.get_world_position()
        
        # Check for objects within detection radius
        return self._check_point_collision(space, sensor_pos)
    
    def _check_point_collision(self, space: pymunk.Space, 
                              position: Tuple[float, float]) -> bool:
        """
        Check if a point collides with any objects in the space.
        
        Args:
            space: Physics space
            position: Point to check
            
        Returns:
            True if collision detected
        """
        # Use a small circle for point collision detection
        query_info = space.point_query_nearest(position, 0.0, pymunk.ShapeFilter())
        
        if query_info and query_info.shape:
            # Check if the collision is with something other than the robot itself
            if query_info.shape != self.robot.shape:
                return True
        
        return False
    
    def _check_area_collision(self, space: pymunk.Space, 
                             position: Tuple[float, float]) -> bool:
        """
        Check for collisions in a circular area around the sensor.
        
        Args:
            space: Physics space
            position: Center position to check
            
        Returns:
            True if collision detected in area
        """
        # Query for shapes in the detection area
        query_infos = space.point_query(position, self.detection_radius, 
                                       pymunk.ShapeFilter())
        
        for query_info in query_infos:
            if query_info.shape and query_info.shape != self.robot.shape:
                return True
        
        return False
    
    def wait_for_press(self) -> bool:
        """
        Check if sensor was just pressed (for use in control loops).
        
        Returns:
            True when button is pressed
        """
        return self.was_button_pressed()
    
    def wait_for_release(self) -> bool:
        """
        Check if sensor was just released (for use in control loops).
        
        Returns:
            True when button is released
        """
        return self.was_button_released()
    
    def wait_for_bump(self) -> bool:
        """
        Check for a complete press-release cycle (bump).
        
        Returns:
            True when a bump is detected
        """
        return self.was_button_released() and self.press_count > 0
    
    def render(self, renderer):
        """Render the touch sensor."""
        if not self.enabled:
            return
        
        world_pos = self.get_world_position()
        
        # Choose color based on sensor state
        if self.is_pressed:
            color = (255, 0, 0)  # Red when pressed
            fill_color = (255, 100, 100)
        else:
            color = (0, 255, 0)  # Green when not pressed
            fill_color = (100, 255, 100)
        
        # Draw detection area
        renderer.draw_circle(
            world_pos[0], world_pos[1],
            self.detection_radius,
            fill_color
        )
        
        # Draw sensor outline
        renderer.draw_circle(
            world_pos[0], world_pos[1],
            self.detection_radius + 1,
            color=None, border_width=2, border_color=color
        )
        
        # Draw sensor center
        renderer.draw_circle(
            world_pos[0], world_pos[1],
            2, color
        )
        
        # Draw direction indicator if sensor has orientation
        if self.direction != 0:
            world_dir = self.get_world_direction()
            angle_rad = math.radians(world_dir)
            length = self.detection_radius + 5
            
            end_x = world_pos[0] + math.cos(angle_rad) * length
            end_y = world_pos[1] + math.sin(angle_rad) * length
            
            renderer.draw_line(world_pos, (end_x, end_y), color, 2)
        
        # Draw sensor label and state
        state_text = "PRESSED" if self.is_pressed else "RELEASED"
        renderer.draw_text(
            f"{self.name}: {state_text}",
            world_pos[0], world_pos[1] - self.detection_radius - 15,
            color=(255, 255, 255), font_size='small'
        )
        
        # Draw press count if non-zero
        if self.press_count > 0:
            renderer.draw_text(
                f"Count: {self.press_count}",
                world_pos[0], world_pos[1] + self.detection_radius + 15,
                color=(255, 255, 255), font_size='small'
            )
    
    def reset(self):
        """Reset the touch sensor to initial state."""
        super().reset()
        self.is_pressed = False
        self.was_pressed = False
        self.press_count = 0
        self.last_state_change = 0.0
