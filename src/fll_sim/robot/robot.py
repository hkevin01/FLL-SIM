"""
FLL Robot simulation with physics and sensor integration.

This module implements a realistic LEGO robot simulation with:
- Differential drive mechanics
- Multiple sensor types
- Physics-based movement
- Customizable robot configurations
"""

import math
from typing import Dict, List, Optional, Tuple, Any
import pygame
import pymunk
from dataclasses import dataclass, field

from ..sensors.sensor_base import Sensor
from ..sensors.color_sensor import ColorSensor
from ..sensors.ultrasonic_sensor import UltrasonicSensor
from ..sensors.gyro_sensor import GyroSensor
from ..sensors.touch_sensor import TouchSensor


@dataclass
class RobotConfig:
    """Configuration for robot physical properties."""
    
    # Physical dimensions (in mm)
    width: float = 180.0    # Standard LEGO robot width
    length: float = 200.0   # Standard LEGO robot length
    mass: float = 1.0       # Robot mass in kg
    
    # Wheel properties
    wheel_diameter: float = 56.0  # Standard LEGO wheel diameter in mm
    wheel_base: float = 160.0     # Distance between wheels in mm
    
    # Motor properties
    max_speed: float = 500.0      # Max speed in mm/s
    max_angular_velocity: float = 360.0  # Max rotation speed in deg/s
    acceleration: float = 1000.0  # Acceleration in mm/s²
    
    # Physics properties
    friction: float = 0.7
    restitution: float = 0.1  # Bounciness
    
    # Appearance
    color: Tuple[int, int, int] = (255, 200, 0)  # Robot color (yellow)


class Robot:
    """
    Simulated LEGO robot with realistic physics and sensors.
    
    The robot supports:
    - Differential drive movement
    - Multiple sensor attachments
    - Physics-based interactions
    - Autonomous and manual control
    """
    
    # Collision type for physics
    collision_type = 1
    
    def __init__(self, x: float = 0, y: float = 0, angle: float = 0, 
                 config: Optional[RobotConfig] = None):
        """
        Initialize the robot.
        
        Args:
            x: Initial X position in mm
            y: Initial Y position in mm  
            angle: Initial angle in degrees
            config: Robot configuration
        """
        self.config = config or RobotConfig()
        
        # Position and orientation
        self.x = x
        self.y = y
        self.angle = angle  # degrees
        self.initial_x = x
        self.initial_y = y
        self.initial_angle = angle
        
        # Movement state
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.angular_velocity = 0.0  # degrees/second
        
        # Motor control
        self.left_motor_speed = 0.0   # -100 to 100
        self.right_motor_speed = 0.0  # -100 to 100
        self.target_left_speed = 0.0
        self.target_right_speed = 0.0
        
        # Physics body (will be set when added to space)
        self.body: Optional[pymunk.Body] = None
        self.shape: Optional[pymunk.Shape] = None
        
        # Sensors
        self.sensors: Dict[str, Sensor] = {}
        self._setup_default_sensors()
        
        # Control state
        self.manual_control = False
        self.key_states = {
            pygame.K_UP: False,
            pygame.K_DOWN: False,
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
        }
        
        # Movement commands queue for autonomous control
        self.command_queue: List[Dict[str, Any]] = []
        self.current_command: Optional[Dict[str, Any]] = None
        self.command_start_time = 0.0
    
    def _setup_default_sensors(self):
        """Setup default sensors for the robot."""
        # Color sensor pointing down
        self.add_sensor("color_down", ColorSensor(
            name="color_down",
            position=(0, 20),  # Slightly forward from center
            direction=270  # Pointing down
        ))
        
        # Ultrasonic sensor pointing forward
        self.add_sensor("ultrasonic_front", UltrasonicSensor(
            name="ultrasonic_front", 
            position=(0, -self.config.length/2),  # Front of robot
            direction=0,  # Pointing forward
            max_range=2550  # mm
        ))
        
        # Gyro sensor for orientation
        self.add_sensor("gyro", GyroSensor(name="gyro"))
        
        # Touch sensors on bumpers
        self.add_sensor("touch_left", TouchSensor(
            name="touch_left",
            position=(-self.config.width/2, -self.config.length/2),
            direction=315  # Front-left
        ))
        
        self.add_sensor("touch_right", TouchSensor(
            name="touch_right", 
            position=(self.config.width/2, -self.config.length/2),
            direction=45  # Front-right
        ))
    
    def add_sensor(self, name: str, sensor: Sensor):
        """Add a sensor to the robot."""
        self.sensors[name] = sensor
        sensor.attach_to_robot(self)
    
    def get_sensor(self, name: str) -> Optional[Sensor]:
        """Get a sensor by name."""
        return self.sensors.get(name)
    
    def add_to_space(self, space: pymunk.Space):
        """Add the robot to the physics space."""
        # Create body
        moment = pymunk.moment_for_box(self.config.mass, 
                                     (self.config.width, self.config.length))
        self.body = pymunk.Body(self.config.mass, moment)
        self.body.position = self.x, self.y
        self.body.angle = math.radians(self.angle)
        
        # Create shape
        self.shape = pymunk.Poly.create_box(self.body, 
                                          (self.config.width, self.config.length))
        self.shape.friction = self.config.friction
        self.shape.collision_type = self.collision_type
        
        # Add to space
        space.add(self.body, self.shape)
    
    def update(self, dt: float):
        """Update robot state."""
        # Update motor speeds towards target
        self._update_motor_speeds(dt)
        
        # Calculate wheel velocities
        left_vel = (self.left_motor_speed / 100.0) * self.config.max_speed
        right_vel = (self.right_motor_speed / 100.0) * self.config.max_speed
        
        # Differential drive kinematics
        linear_vel = (left_vel + right_vel) / 2.0
        angular_vel = (right_vel - left_vel) / self.config.wheel_base
        
        # Convert to world coordinates
        if self.body:
            # Update physics body
            angle_rad = self.body.angle
            vel_x = linear_vel * math.cos(angle_rad)
            vel_y = linear_vel * math.sin(angle_rad)
            
            self.body.velocity = vel_x, vel_y
            self.body.angular_velocity = angular_vel
            
            # Update position from physics
            self.x, self.y = self.body.position
            self.angle = math.degrees(self.body.angle) % 360
        else:
            # Update without physics (for testing)
            angle_rad = math.radians(self.angle)
            self.x += linear_vel * math.cos(angle_rad) * dt
            self.y += linear_vel * math.sin(angle_rad) * dt
            self.angle += math.degrees(angular_vel * dt)
            self.angle = self.angle % 360
        
        # Update sensors
        for sensor in self.sensors.values():
            sensor.update(dt)
        
        # Process autonomous commands
        self._update_autonomous_control(dt)
    
    def _update_motor_speeds(self, dt: float):
        """Update motor speeds with acceleration limits."""
        # Calculate acceleration per frame
        max_speed_change = self.config.acceleration * dt / self.config.max_speed * 100
        
        # Left motor
        speed_diff = self.target_left_speed - self.left_motor_speed
        if abs(speed_diff) <= max_speed_change:
            self.left_motor_speed = self.target_left_speed
        else:
            self.left_motor_speed += math.copysign(max_speed_change, speed_diff)
        
        # Right motor
        speed_diff = self.target_right_speed - self.right_motor_speed
        if abs(speed_diff) <= max_speed_change:
            self.right_motor_speed = self.target_right_speed
        else:
            self.right_motor_speed += math.copysign(max_speed_change, speed_diff)
    
    def _update_autonomous_control(self, dt: float):
        """Update autonomous command execution."""
        if not self.current_command and self.command_queue:
            # Start next command
            self.current_command = self.command_queue.pop(0)
            self.command_start_time = 0.0
        
        if self.current_command:
            self.command_start_time += dt
            
            # Execute current command
            command_type = self.current_command["type"]
            
            if command_type == "move_forward":
                self._execute_move_forward(self.current_command, dt)
            elif command_type == "move_backward":
                self._execute_move_backward(self.current_command, dt)
            elif command_type == "turn_left":
                self._execute_turn_left(self.current_command, dt)
            elif command_type == "turn_right":
                self._execute_turn_right(self.current_command, dt)
            elif command_type == "stop":
                self._execute_stop(self.current_command, dt)
            elif command_type == "wait":
                self._execute_wait(self.current_command, dt)
    
    def _execute_move_forward(self, command: dict, dt: float):
        """Execute move forward command."""
        distance = command["distance"]
        speed = command.get("speed", 50)
        
        # Calculate expected time to complete
        expected_time = distance / (speed / 100.0 * self.config.max_speed)
        
        if self.command_start_time < expected_time:
            self.set_motor_speeds(speed, speed)
        else:
            self.stop_motors()
            self.current_command = None
    
    def _execute_move_backward(self, command: dict, dt: float):
        """Execute move backward command."""
        distance = command["distance"]
        speed = command.get("speed", 50)
        
        expected_time = distance / (speed / 100.0 * self.config.max_speed)
        
        if self.command_start_time < expected_time:
            self.set_motor_speeds(-speed, -speed)
        else:
            self.stop_motors()
            self.current_command = None
    
    def _execute_turn_left(self, command: dict, dt: float):
        """Execute turn left command."""
        degrees = command["degrees"]
        speed = command.get("speed", 30)
        
        # Calculate turn time based on angular velocity
        angular_speed = speed / 100.0 * self.config.max_angular_velocity
        expected_time = degrees / angular_speed
        
        if self.command_start_time < expected_time:
            self.set_motor_speeds(-speed, speed)
        else:
            self.stop_motors()
            self.current_command = None
    
    def _execute_turn_right(self, command: dict, dt: float):
        """Execute turn right command."""
        degrees = command["degrees"] 
        speed = command.get("speed", 30)
        
        angular_speed = speed / 100.0 * self.config.max_angular_velocity
        expected_time = degrees / angular_speed
        
        if self.command_start_time < expected_time:
            self.set_motor_speeds(speed, -speed)
        else:
            self.stop_motors()
            self.current_command = None
    
    def _execute_stop(self, command: dict, dt: float):
        """Execute stop command."""
        self.stop_motors()
        self.current_command = None
    
    def _execute_wait(self, command: dict, dt: float):
        """Execute wait command."""
        duration = command["duration"]
        
        if self.command_start_time >= duration:
            self.current_command = None
    
    # Public movement API
    def set_motor_speeds(self, left_speed: float, right_speed: float):
        """Set motor speeds (-100 to 100)."""
        self.target_left_speed = max(-100, min(100, left_speed))
        self.target_right_speed = max(-100, min(100, right_speed))
    
    def stop_motors(self):
        """Stop both motors."""
        self.set_motor_speeds(0, 0)
    
    def move_forward(self, distance: float, speed: float = 50):
        """Queue a move forward command."""
        self.command_queue.append({
            "type": "move_forward",
            "distance": distance,
            "speed": speed
        })
    
    def move_backward(self, distance: float, speed: float = 50):
        """Queue a move backward command."""
        self.command_queue.append({
            "type": "move_backward", 
            "distance": distance,
            "speed": speed
        })
    
    def turn_left(self, degrees: float, speed: float = 30):
        """Queue a turn left command."""
        self.command_queue.append({
            "type": "turn_left",
            "degrees": degrees,
            "speed": speed
        })
    
    def turn_right(self, degrees: float, speed: float = 30):
        """Queue a turn right command."""
        self.command_queue.append({
            "type": "turn_right",
            "degrees": degrees, 
            "speed": speed
        })
    
    def wait(self, duration: float):
        """Queue a wait command."""
        self.command_queue.append({
            "type": "wait",
            "duration": duration
        })
    
    def handle_key_event(self, event):
        """Handle keyboard input for manual control."""
        if event.type == pygame.KEYDOWN:
            if event.key in self.key_states:
                self.key_states[event.key] = True
                self.manual_control = True
        elif event.type == pygame.KEYUP:
            if event.key in self.key_states:
                self.key_states[event.key] = False
        
        # Update motor speeds based on key states
        if self.manual_control:
            left_speed = 0
            right_speed = 0
            
            if self.key_states[pygame.K_UP]:
                left_speed = right_speed = 60
            elif self.key_states[pygame.K_DOWN]:
                left_speed = right_speed = -60
            
            if self.key_states[pygame.K_LEFT]:
                left_speed -= 30
                right_speed += 30
            elif self.key_states[pygame.K_RIGHT]:
                left_speed += 30
                right_speed -= 30
            
            self.set_motor_speeds(left_speed, right_speed)
            
            # Stop manual control if no keys pressed
            if not any(self.key_states.values()):
                self.manual_control = False
                self.stop_motors()
    
    def render(self, renderer):
        """Render the robot."""
        # Draw robot body
        renderer.draw_rect(
            self.x, self.y, 
            self.config.width, self.config.length,
            self.angle, self.config.color
        )
        
        # Draw direction indicator
        front_x = self.x + math.cos(math.radians(self.angle)) * self.config.length / 2
        front_y = self.y + math.sin(math.radians(self.angle)) * self.config.length / 2
        renderer.draw_line(
            (self.x, self.y), (front_x, front_y),
            (255, 0, 0), 3  # Red line pointing forward
        )
        
        # Draw sensors
        for sensor in self.sensors.values():
            sensor.render(renderer)
    
    def reset(self):
        """Reset robot to initial state."""
        self.x = self.initial_x
        self.y = self.initial_y
        self.angle = self.initial_angle
        
        if self.body:
            self.body.position = self.x, self.y
            self.body.angle = math.radians(self.angle)
            self.body.velocity = 0, 0
            self.body.angular_velocity = 0
        
        self.velocity_x = 0
        self.velocity_y = 0
        self.angular_velocity = 0
        self.left_motor_speed = 0
        self.right_motor_speed = 0
        self.target_left_speed = 0
        self.target_right_speed = 0
        
        # Clear command queue
        self.command_queue.clear()
        self.current_command = None
        self.command_start_time = 0
        
        # Reset sensors
        for sensor in self.sensors.values():
            sensor.reset()
    
    def get_state(self) -> dict:
        """Get current robot state."""
        return {
            "position": (self.x, self.y),
            "angle": self.angle,
            "motor_speeds": (self.left_motor_speed, self.right_motor_speed),
            "sensors": {name: sensor.get_reading() for name, sensor in self.sensors.items()},
            "command_queue_length": len(self.command_queue),
            "current_command": self.current_command,
        }
