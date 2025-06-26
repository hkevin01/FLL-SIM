"""
Gyro sensor simulation for orientation and rotation measurement.

This sensor simulates the LEGO EV3/SPIKE gyroscopic sensor that measures
angular velocity and absolute orientation.
"""

import math
from typing import Tuple

from .sensor_base import Sensor


class GyroSensor(Sensor):
    """
    Gyroscopic sensor for measuring rotation and orientation.
    
    The sensor provides:
    - Absolute angle (degrees)
    - Angular velocity (degrees/second) 
    - Drift compensation
    - Calibration functionality
    """
    
    def __init__(self, name: str, position: Tuple[float, float] = (0, 0),
                 drift_rate: float = 0.1):
        """
        Initialize the gyro sensor.
        
        Args:
            name: Sensor name
            position: Position relative to robot center
            drift_rate: Drift rate in degrees per second
        """
        super().__init__(name, position, direction=0)
        self.drift_rate = drift_rate
        
        # Measurement state
        self.angle = 0.0  # Cumulative angle in degrees
        self.angular_velocity = 0.0  # Current angular velocity
        self.calibration_offset = 0.0  # Calibration offset
        self.drift_accumulator = 0.0  # Accumulated drift
        
        # Previous values for velocity calculation
        self.prev_robot_angle = 0.0
        self.prev_time = 0.0
        
        # Noise parameters
        self.angle_noise = 0.1  # Degrees
        self.velocity_noise = 0.5  # Degrees/second
    
    def get_reading(self) -> float:
        """Get the current angle reading in degrees."""
        return self.get_angle()
    
    def get_angle(self) -> float:
        """Get the current absolute angle in degrees."""
        return (self.angle - self.calibration_offset) % 360
    
    def get_angular_velocity(self) -> float:
        """Get the current angular velocity in degrees/second."""
        return self.angular_velocity
    
    def get_rotation_rate(self) -> float:
        """Get the current rotation rate (alias for angular velocity)."""
        return self.angular_velocity
    
    def reset_angle(self):
        """Reset the accumulated angle to zero."""
        self.angle = 0.0
        self.calibration_offset = 0.0
        self.drift_accumulator = 0.0
    
    def calibrate(self):
        """Calibrate the gyro sensor (set current angle as zero reference)."""
        self.calibration_offset = self.angle
        self.drift_accumulator = 0.0
    
    def update(self, dt: float):
        """Update the gyro sensor readings."""
        if not self.enabled or not self.robot:
            return
        
        # Get current robot angle
        current_robot_angle = self.robot.angle
        
        # Calculate angular velocity from robot motion
        if hasattr(self, 'prev_robot_angle'):
            angle_change = current_robot_angle - self.prev_robot_angle
            
            # Handle angle wraparound
            if angle_change > 180:
                angle_change -= 360
            elif angle_change < -180:
                angle_change += 360
            
            # Calculate angular velocity
            if dt > 0:
                self.angular_velocity = angle_change / dt
            
            # Update cumulative angle
            self.angle += angle_change
        
        # Add drift
        self.drift_accumulator += self.drift_rate * dt
        
        # Add noise
        angle_noise = self._generate_noise(self.angle_noise)
        velocity_noise = self._generate_noise(self.velocity_noise)
        
        # Apply noise and drift
        self.angle += angle_noise * dt
        self.angular_velocity += velocity_noise
        
        # Store for next update
        self.prev_robot_angle = current_robot_angle
        self.last_reading = self.get_angle()
    
    def _generate_noise(self, magnitude: float) -> float:
        """
        Generate sensor noise.
        
        Args:
            magnitude: Noise magnitude
            
        Returns:
            Random noise value
        """
        import random
        return random.uniform(-magnitude, magnitude)
    
    def get_absolute_heading(self) -> float:
        """
        Get absolute heading relative to starting orientation.
        
        Returns:
            Heading in degrees (0-360)
        """
        return self.get_angle() % 360
    
    def get_relative_heading(self, target_angle: float) -> float:
        """
        Get relative heading to a target angle.
        
        Args:
            target_angle: Target angle in degrees
            
        Returns:
            Relative angle (-180 to 180 degrees)
        """
        diff = target_angle - self.get_angle()
        
        # Normalize to -180 to 180 range
        while diff > 180:
            diff -= 360
        while diff < -180:
            diff += 360
        
        return diff
    
    def has_rotated(self, threshold: float = 1.0) -> bool:
        """
        Check if robot has rotated more than threshold since last check.
        
        Args:
            threshold: Rotation threshold in degrees
            
        Returns:
            True if rotation exceeds threshold
        """
        return abs(self.angular_velocity) > threshold
    
    def wait_for_rotation_stop(self, threshold: float = 0.5) -> bool:
        """
        Check if rotation has stopped (angular velocity below threshold).
        
        Args:
            threshold: Velocity threshold in degrees/second
            
        Returns:
            True if rotation has stopped
        """
        return abs(self.angular_velocity) < threshold
    
    def turn_to_heading(self, target_heading: float, tolerance: float = 2.0) -> bool:
        """
        Check if robot has reached target heading within tolerance.
        
        Args:
            target_heading: Target heading in degrees
            tolerance: Acceptable error in degrees
            
        Returns:
            True if at target heading
        """
        error = abs(self.get_relative_heading(target_heading))
        return error <= tolerance
    
    def render(self, renderer):
        """Render the gyro sensor."""
        if not self.enabled:
            return
        
        world_pos = self.get_world_position()
        
        # Draw gyro sensor symbol
        renderer.draw_circle(world_pos[0], world_pos[1], 6, (255, 0, 255))
        
        # Draw orientation indicator
        angle_rad = math.radians(self.get_angle())
        indicator_length = 15
        end_x = world_pos[0] + math.cos(angle_rad) * indicator_length
        end_y = world_pos[1] + math.sin(angle_rad) * indicator_length
        
        renderer.draw_line(world_pos, (end_x, end_y), (255, 0, 255), 3)
        
        # Draw angle readout
        renderer.draw_text(
            f"{self.name}: {self.get_angle():.1f}°",
            world_pos[0], world_pos[1] - 20,
            color=(255, 255, 255), font_size='small'
        )
        
        # Draw angular velocity if significant
        if abs(self.angular_velocity) > 1.0:
            renderer.draw_text(
                f"ω: {self.angular_velocity:.1f}°/s",
                world_pos[0], world_pos[1] + 20,
                color=(255, 0, 255), font_size='small'
            )
    
    def reset(self):
        """Reset the gyro sensor to initial state."""
        super().reset()
        self.angle = 0.0
        self.angular_velocity = 0.0
        self.calibration_offset = 0.0
        self.drift_accumulator = 0.0
        self.prev_robot_angle = 0.0 if self.robot else 0.0
