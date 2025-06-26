"""
Color sensor simulation for detecting surface colors.

This sensor simulates the LEGO EV3/SPIKE color sensor that can detect
colors and light intensity on the game mat.
"""

import math
from enum import Enum
from typing import Optional, Tuple

from .sensor_base import Sensor


class Color(Enum):
    """Standard LEGO color values."""
    NO_COLOR = 0
    BLACK = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4
    RED = 5
    WHITE = 6
    BROWN = 7


class ColorSensor(Sensor):
    """
    Color sensor that detects surface colors and light intensity.
    
    The sensor can operate in different modes:
    - Color detection: Returns discrete color values
    - Ambient light: Returns light intensity (0-100)
    - Reflected light: Returns reflected light intensity (0-100)
    """
    
    def __init__(self, name: str, position: Tuple[float, float] = (0, 0),
                 direction: float = 270, detection_radius: float = 10.0):
        """
        Initialize the color sensor.
        
        Args:
            name: Sensor name
            position: Position relative to robot center
            direction: Direction sensor is pointing (270 = down)
            detection_radius: Radius of color detection area in mm
        """
        super().__init__(name, position, direction)
        self.detection_radius = detection_radius
        self.current_color = Color.NO_COLOR
        self.ambient_light = 50  # 0-100
        self.reflected_light = 50  # 0-100
        
        # Color RGB mappings for detection
        self.color_mappings = {
            Color.BLACK: (0, 0, 0),
            Color.BLUE: (0, 0, 255),
            Color.GREEN: (0, 255, 0),
            Color.YELLOW: (255, 255, 0),
            Color.RED: (255, 0, 0),
            Color.WHITE: (255, 255, 255),
            Color.BROWN: (139, 69, 19),
        }
    
    def get_reading(self) -> Color:
        """Get the current color reading."""
        return self.current_color
    
    def get_color_id(self) -> int:
        """Get the color as an integer ID."""
        return self.current_color.value
    
    def get_ambient_light(self) -> int:
        """Get ambient light reading (0-100)."""
        return int(self.ambient_light)
    
    def get_reflected_light(self) -> int:
        """Get reflected light reading (0-100)."""
        return int(self.reflected_light)
    
    def get_rgb(self) -> Tuple[int, int, int]:
        """Get RGB values of detected color."""
        return self.color_mappings.get(self.current_color, (0, 0, 0))
    
    def update(self, dt: float):
        """Update the color sensor reading."""
        if not self.enabled or not self.robot:
            return
        
        # Get world position of the sensor
        world_pos = self.get_world_position()
        
        # Sample color from the game map at sensor position
        detected_color = self._sample_color_at_position(world_pos)
        self.current_color = detected_color
        
        # Update light readings based on detected color
        self._update_light_readings(detected_color)
        
        self.last_reading = self.current_color
    
    def _sample_color_at_position(self, position: Tuple[float, float]) -> Color:
        """
        Sample the color at the given world position.
        
        Args:
            position: (x, y) world coordinates
            
        Returns:
            Detected color
        """
        if not self.robot or not hasattr(self.robot, 'game_map'):
            # Default to white if no game map available
            return Color.WHITE
        
        # In a real implementation, this would sample from the game map
        # For now, we'll implement a simple pattern for testing
        x, y = position
        
        # Create a simple test pattern
        if x < 0 and y < 0:
            return Color.BLACK
        elif x > 0 and y < 0:
            return Color.RED
        elif x < 0 and y > 0:
            return Color.BLUE
        elif x > 0 and y > 0:
            return Color.GREEN
        else:
            return Color.WHITE
    
    def _update_light_readings(self, color: Color):
        """
        Update ambient and reflected light based on detected color.
        
        Args:
            color: The detected color
        """
        # Simulate light readings based on color brightness
        brightness_map = {
            Color.NO_COLOR: 50,
            Color.BLACK: 5,
            Color.BLUE: 25,
            Color.GREEN: 45,
            Color.YELLOW: 85,
            Color.RED: 35,
            Color.WHITE: 95,
            Color.BROWN: 20,
        }
        
        base_brightness = brightness_map.get(color, 50)
        
        # Add some variation
        import random
        variation = random.uniform(-5, 5)
        
        self.ambient_light = max(0, min(100, base_brightness + variation))
        self.reflected_light = max(0, min(100, base_brightness + variation * 0.5))
    
    def calibrate_white(self):
        """Calibrate the sensor for white color detection."""
        # In a real sensor, this would calibrate the white reference
        # For simulation, we just store current reading as white reference
        self.current_color = Color.WHITE
        self.reflected_light = 95
    
    def calibrate_black(self):
        """Calibrate the sensor for black color detection."""
        # In a real sensor, this would calibrate the black reference
        self.current_color = Color.BLACK
        self.reflected_light = 5
    
    def render(self, renderer):
        """Render the color sensor."""
        if not self.enabled:
            return
        
        world_pos = self.get_world_position()
        
        # Draw detection area
        color_rgb = self.color_mappings.get(self.current_color, (128, 128, 128))
        renderer.draw_circle(
            world_pos[0], world_pos[1], 
            self.detection_radius, 
            color_rgb
        )
        
        # Draw sensor outline
        renderer.draw_circle(
            world_pos[0], world_pos[1],
            self.detection_radius + 2,
            color=None, border_width=2, border_color=(255, 255, 255)
        )
        
        # Draw sensor name
        renderer.draw_text(
            self.name, 
            world_pos[0], world_pos[1] - self.detection_radius - 15,
            color=(255, 255, 255), font_size='small'
        )
