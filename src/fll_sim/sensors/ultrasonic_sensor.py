"""
Ultrasonic sensor simulation for distance measurement.

This sensor simulates the LEGO EV3/SPIKE ultrasonic sensor that measures
distance to objects using ultrasonic waves.
"""

import math
from typing import List, Optional, Tuple

import pymunk

from .sensor_base import Sensor


class UltrasonicSensor(Sensor):
    """
    Ultrasonic distance sensor with realistic beam characteristics.
    
    The sensor emits an ultrasonic beam and measures the time for echoes
    to return, calculating distance to the nearest obstacle.
    """
    
    def __init__(self, name: str, position: Tuple[float, float] = (0, 0),
                 direction: float = 0, max_range: float = 2550.0,
                 beam_width: float = 30.0, resolution: float = 1.0):
        """
        Initialize the ultrasonic sensor.
        
        Args:
            name: Sensor name
            position: Position relative to robot center
            direction: Direction sensor is pointing in degrees
            max_range: Maximum detection range in mm
            beam_width: Width of ultrasonic beam in degrees
            resolution: Distance resolution in mm
        """
        super().__init__(name, position, direction)
        self.max_range = max_range
        self.beam_width = beam_width
        self.resolution = resolution
        self.current_distance = max_range  # No object detected initially
        
        # Measurement parameters
        self.measurement_angle_step = 5.0  # Degrees between ray casts
        self.noise_factor = 0.02  # 2% noise in measurements
    
    def get_reading(self) -> float:
        """Get the current distance reading in mm."""
        return self.current_distance
    
    def get_distance_cm(self) -> float:
        """Get the current distance reading in cm.""" 
        return self.current_distance / 10.0
    
    def get_distance_inches(self) -> float:
        """Get the current distance reading in inches."""
        return self.current_distance / 25.4
    
    def is_object_present(self, threshold: float = 2550.0) -> bool:
        """
        Check if an object is detected within threshold distance.
        
        Args:
            threshold: Maximum distance to consider object present (mm)
            
        Returns:
            True if object detected within threshold
        """
        return self.current_distance < threshold
    
    def update(self, dt: float):
        """Update the ultrasonic sensor reading."""
        if not self.enabled or not self.robot:
            return
        
        # Perform distance measurement
        distance = self._measure_distance()
        
        # Add noise to simulate real sensor behavior
        if distance < self.max_range:
            noise = distance * self.noise_factor * (2 * (0.5 - abs(hash(str(distance)) % 1000) / 1000))
            distance += noise
        
        # Apply resolution limits
        distance = round(distance / self.resolution) * self.resolution
        
        # Clamp to valid range
        self.current_distance = max(0, min(self.max_range, distance))
        self.last_reading = self.current_distance
    
    def _measure_distance(self) -> float:
        """
        Perform ultrasonic distance measurement using ray casting.
        
        Returns:
            Measured distance in mm
        """
        if not self.robot or not hasattr(self.robot, 'body') or not self.robot.body:
            return self.max_range
        
        space = self.robot.body.space
        if not space:
            return self.max_range
        
        sensor_pos = self.get_world_position()
        sensor_dir = self.get_world_direction()
        
        # Cast multiple rays within the beam width to find closest obstacle
        min_distance = self.max_range
        
        # Calculate ray directions within beam
        half_beam = self.beam_width / 2.0
        num_rays = max(1, int(self.beam_width / self.measurement_angle_step))
        
        for i in range(num_rays):
            if num_rays == 1:
                ray_angle = sensor_dir
            else:
                # Distribute rays evenly across beam width
                angle_offset = (i / (num_rays - 1) - 0.5) * self.beam_width
                ray_angle = sensor_dir + angle_offset
            
            # Cast ray
            distance = self._cast_ray(space, sensor_pos, ray_angle)
            min_distance = min(min_distance, distance)
        
        return min_distance
    
    def _cast_ray(self, space: pymunk.Space, start_pos: Tuple[float, float], 
                  angle: float) -> float:
        """
        Cast a single ray to detect obstacles.
        
        Args:
            space: Physics space to ray cast in
            start_pos: Starting position of ray
            angle: Angle of ray in degrees
            
        Returns:
            Distance to first obstacle or max_range if none found
        """
        angle_rad = math.radians(angle)
        
        # Calculate end point of ray
        end_x = start_pos[0] + math.cos(angle_rad) * self.max_range
        end_y = start_pos[1] + math.sin(angle_rad) * self.max_range
        end_pos = (end_x, end_y)
        
        # Perform ray cast
        query_info = space.segment_query_first(start_pos, end_pos, 0.0, 
                                             pymunk.ShapeFilter())
        
        if query_info:
            # Calculate distance to hit point
            hit_point = query_info.point
            dx = hit_point[0] - start_pos[0]
            dy = hit_point[1] - start_pos[1]
            distance = math.sqrt(dx * dx + dy * dy)
            return distance
        else:
            return self.max_range
    
    def render(self, renderer):
        """Render the ultrasonic sensor."""
        if not self.enabled:
            return
        
        world_pos = self.get_world_position()
        world_dir = self.get_world_direction()
        
        # Draw sensor position
        renderer.draw_circle(world_pos[0], world_pos[1], 8, (0, 255, 255))
        
        # Draw detection beam
        self._render_beam(renderer, world_pos, world_dir)
        
        # Draw detected distance
        if self.current_distance < self.max_range:
            self._render_detection(renderer, world_pos, world_dir)
        
        # Draw sensor label
        renderer.draw_text(
            f"{self.name}: {self.current_distance:.0f}mm",
            world_pos[0], world_pos[1] - 25,
            color=(255, 255, 255), font_size='small'
        )
    
    def _render_beam(self, renderer, pos: Tuple[float, float], direction: float):
        """Render the ultrasonic beam visualization."""
        # Draw beam outline
        beam_length = min(200, self.max_range / 5)  # Scale for visualization
        half_beam = self.beam_width / 2.0
        
        # Calculate beam edges
        left_angle = math.radians(direction - half_beam)
        right_angle = math.radians(direction + half_beam)
        center_angle = math.radians(direction)
        
        left_end = (
            pos[0] + math.cos(left_angle) * beam_length,
            pos[1] + math.sin(left_angle) * beam_length
        )
        right_end = (
            pos[0] + math.cos(right_angle) * beam_length,
            pos[1] + math.sin(right_angle) * beam_length
        )
        center_end = (
            pos[0] + math.cos(center_angle) * beam_length,
            pos[1] + math.sin(center_angle) * beam_length
        )
        
        # Draw beam lines
        renderer.draw_line(pos, left_end, (0, 255, 255, 100), 1)
        renderer.draw_line(pos, right_end, (0, 255, 255, 100), 1)
        renderer.draw_line(pos, center_end, (0, 255, 255), 2)
        
        # Draw arc at end of beam
        renderer.draw_arc(pos[0], pos[1], beam_length, direction - half_beam, 
                         direction + half_beam, (0, 255, 255), width=2)
    
    def _render_detection(self, renderer, pos: Tuple[float, float], direction: float):
        """Render the detected object position."""
        # Calculate detected object position
        angle_rad = math.radians(direction)
        detected_x = pos[0] + math.cos(angle_rad) * self.current_distance
        detected_y = pos[1] + math.sin(angle_rad) * self.current_distance
        
        # Draw detection point
        renderer.draw_circle(detected_x, detected_y, 6, (255, 0, 0))
        
        # Draw distance line
        renderer.draw_line(pos, (detected_x, detected_y), (255, 255, 0), 2)
