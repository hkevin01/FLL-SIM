"""
Pybricks-inspired high-level API for FLL-Sim robot control.

This module provides a familiar interface for students and educators
coming from LEGO MINDSTORMS and Pybricks, making the transition to
simulation seamless and educational.
"""

import math
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Optional, Tuple, Union

from ..core.simulator import Simulator
from ..robot.robot import Robot, RobotConfig
from ..sensors.color_sensor import Color


class Direction(Enum):
    """Movement directions."""
    CLOCKWISE = 1
    COUNTERCLOCKWISE = -1


class Stop(Enum):
    """Motor stop behaviors."""
    COAST = "coast"
    BRAKE = "brake" 
    HOLD = "hold"


class Port(Enum):
    """Sensor and motor ports."""
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    S4 = "S4"


@dataclass
class PybricksConfig:
    """Configuration for Pybricks-style robot."""
    wheel_diameter: float = 56  # mm
    axle_track: float = 104     # mm (distance between wheels)
    use_gyro: bool = True
    straight_speed: float = 200  # mm/s
    straight_acceleration: float = 400  # mm/s²
    turn_rate: float = 100      # deg/s
    turn_acceleration: float = 300  # deg/s²


class Motor:
    """
    Simulated motor with Pybricks-compatible API.
    
    Provides high-level motor control methods that match the
    LEGO MINDSTORMS and Pybricks motor API.
    """
    
    def __init__(self, robot: Robot, port: Port, positive_direction: Direction = Direction.CLOCKWISE):
        """
        Initialize motor.
        
        Args:
            robot: The robot instance
            port: Motor port (A, B, C, or D)
            positive_direction: Direction for positive speeds
        """
        self.robot = robot
        self.port = port
        self.positive_direction = positive_direction
        
        # Motor state
        self.speed = 0  # deg/s
        self.angle = 0  # degrees
        self.target_angle = None
        self.target_speed = None
        
        # Gear ratio (for advanced users)
        self.gear_ratio = 1.0
    
    def run(self, speed: float):
        """
        Run motor at constant speed.
        
        Args:
            speed: Speed in degrees per second
        """
        # Convert to robot motor speed (-100 to 100)
        motor_speed = speed / 360.0 * 100.0  # Rough conversion
        motor_speed = max(-100, min(100, motor_speed))
        
        if self.positive_direction == Direction.COUNTERCLOCKWISE:
            motor_speed = -motor_speed
        
        # Apply to appropriate motor
        if self.port in [Port.A, Port.B]:  # Left motor
            self.robot.set_motor_speeds(motor_speed, self.robot.target_right_speed)
        else:  # Right motor
            self.robot.set_motor_speeds(self.robot.target_left_speed, motor_speed)
        
        self.speed = speed
    
    def run_time(self, speed: float, time_ms: int, then: Stop = Stop.BRAKE, wait: bool = True):
        """
        Run motor for specified time.
        
        Args:
            speed: Speed in degrees per second
            time_ms: Time in milliseconds
            then: What to do after time expires
            wait: Whether to wait for completion
        """
        self.run(speed)
        
        if wait:
            time.sleep(time_ms / 1000.0)
            if then == Stop.BRAKE:
                self.brake()
            elif then == Stop.COAST:
                self.stop()
            elif then == Stop.HOLD:
                self.hold()
    
    def run_angle(self, speed: float, rotation_angle: float, then: Stop = Stop.BRAKE, wait: bool = True):
        """
        Run motor until it rotates by specified angle.
        
        Args:
            speed: Speed in degrees per second
            rotation_angle: Angle to rotate in degrees
            then: What to do after completion
            wait: Whether to wait for completion
        """
        # Convert angle to time based on speed
        if speed != 0:
            time_needed = abs(rotation_angle / speed)
            self.run_time(speed, int(time_needed * 1000), then, wait)
    
    def run_target(self, speed: float, target_angle: float, then: Stop = Stop.BRAKE, wait: bool = True):
        """
        Run motor until it reaches target angle.
        
        Args:
            speed: Speed in degrees per second
            target_angle: Target angle in degrees
            then: What to do after completion
            wait: Whether to wait for completion
        """
        angle_diff = target_angle - self.angle
        self.run_angle(speed, angle_diff, then, wait)
    
    def stop(self):
        """Stop motor (coast to stop)."""
        if self.port in [Port.A, Port.B]:
            self.robot.set_motor_speeds(0, self.robot.target_right_speed)
        else:
            self.robot.set_motor_speeds(self.robot.target_left_speed, 0)
        self.speed = 0
    
    def brake(self):
        """Brake motor (active stop)."""
        self.stop()  # In simulation, brake and stop are the same
    
    def hold(self):
        """Hold motor position."""
        self.stop()  # In simulation, hold and stop are the same
    
    def reset_angle(self, angle: float = 0):
        """Reset motor angle to specified value."""
        self.angle = angle
    
    def speed(self) -> float:
        """Get current motor speed in deg/s."""
        return self.speed
    
    def angle(self) -> float:
        """Get current motor angle in degrees."""
        return self.angle


class DriveBase:
    """
    Simulated drive base with Pybricks-compatible API.
    
    Provides high-level movement commands for differential drive robots.
    """
    
    def __init__(self, robot: Robot, left_motor: Motor, right_motor: Motor,
                 wheel_diameter: float = 56, axle_track: float = 104):
        """
        Initialize drive base.
        
        Args:
            robot: Robot instance
            left_motor: Left wheel motor
            right_motor: Right wheel motor
            wheel_diameter: Wheel diameter in mm
            axle_track: Distance between wheels in mm
        """
        self.robot = robot
        self.left_motor = left_motor
        self.right_motor = right_motor
        self.wheel_diameter = wheel_diameter
        self.axle_track = axle_track
        
        # Movement settings
        self.straight_speed = 200  # mm/s
        self.straight_acceleration = 400  # mm/s²
        self.turn_rate = 100  # deg/s
        self.turn_acceleration = 300  # deg/s²
    
    def settings(self, straight_speed: Optional[float] = None,
                 straight_acceleration: Optional[float] = None,
                 turn_rate: Optional[float] = None,
                 turn_acceleration: Optional[float] = None):
        """
        Configure drive base settings.
        
        Args:
            straight_speed: Speed for straight movements in mm/s
            straight_acceleration: Acceleration for straight movements in mm/s²
            turn_rate: Turn rate in deg/s
            turn_acceleration: Turn acceleration in deg/s²
        """
        if straight_speed is not None:
            self.straight_speed = straight_speed
        if straight_acceleration is not None:
            self.straight_acceleration = straight_acceleration
        if turn_rate is not None:
            self.turn_rate = turn_rate
        if turn_acceleration is not None:
            self.turn_acceleration = turn_acceleration
    
    def straight(self, distance: float, then: Stop = Stop.BRAKE, wait: bool = True):
        """
        Drive straight for specified distance.
        
        Args:
            distance: Distance in millimeters (positive = forward)
            then: What to do after completion
            wait: Whether to wait for completion
        """
        speed = self.straight_speed if distance > 0 else -self.straight_speed
        
        # Convert to robot commands
        if distance > 0:
            self.robot.move_forward(abs(distance), abs(speed) / self.robot.config.max_speed * 100)
        else:
            self.robot.move_backward(abs(distance), abs(speed) / self.robot.config.max_speed * 100)
        
        if wait:
            # Wait for command to complete
            while self.robot.command_queue or self.robot.current_command:
                time.sleep(0.01)
    
    def turn(self, angle: float, then: Stop = Stop.BRAKE, wait: bool = True):
        """
        Turn by specified angle.
        
        Args:
            angle: Angle in degrees (positive = clockwise)
            then: What to do after completion
            wait: Whether to wait for completion
        """
        # Convert to robot commands
        if angle > 0:
            self.robot.turn_right(abs(angle), self.turn_rate / self.robot.config.max_angular_velocity * 100)
        else:
            self.robot.turn_left(abs(angle), self.turn_rate / self.robot.config.max_angular_velocity * 100)
        
        if wait:
            # Wait for command to complete
            while self.robot.command_queue or self.robot.current_command:
                time.sleep(0.01)
    
    def curve(self, radius: float, angle: float, then: Stop = Stop.BRAKE, wait: bool = True):
        """
        Drive in a curve.
        
        Args:
            radius: Curve radius in mm
            angle: Angle to turn in degrees
            then: What to do after completion
            wait: Whether to wait for completion
        """
        # Calculate arc length
        arc_length = abs(radius * math.radians(angle))
        
        # Calculate wheel speeds for curve
        if angle > 0:  # Right turn
            left_speed = self.straight_speed
            right_speed = left_speed * (radius - self.axle_track/2) / (radius + self.axle_track/2)
        else:  # Left turn
            right_speed = self.straight_speed
            left_speed = right_speed * (radius - self.axle_track/2) / (radius + self.axle_track/2)
        
        # Convert to motor speeds and execute
        left_motor_speed = left_speed / self.robot.config.max_speed * 100
        right_motor_speed = right_speed / self.robot.config.max_speed * 100
        
        # Calculate time needed
        time_needed = arc_length / self.straight_speed
        
        # Execute curve
        self.robot.set_motor_speeds(left_motor_speed, right_motor_speed)
        
        if wait:
            time.sleep(time_needed)
            if then == Stop.BRAKE:
                self.stop()
    
    def drive(self, speed: float, turn_rate: float):
        """
        Drive with speed and turn rate.
        
        Args:
            speed: Forward speed in mm/s
            turn_rate: Turn rate in deg/s (positive = clockwise)
        """
        # Convert to differential drive
        left_speed = speed - (turn_rate * self.axle_track / 2)
        right_speed = speed + (turn_rate * self.axle_track / 2)
        
        # Convert to motor speeds
        left_motor_speed = left_speed / self.robot.config.max_speed * 100
        right_motor_speed = right_speed / self.robot.config.max_speed * 100
        
        self.robot.set_motor_speeds(left_motor_speed, right_motor_speed)
    
    def stop(self):
        """Stop the drive base."""
        self.robot.stop_motors()
    
    def distance(self) -> float:
        """Get distance traveled since last reset."""
        # This would need odometry integration
        return 0.0
    
    def angle(self) -> float:
        """Get angle turned since last reset."""
        # This would use gyro sensor
        gyro = self.robot.get_sensor("gyro")
        if gyro:
            return gyro.get_reading()
        return 0.0
    
    def reset(self):
        """Reset distance and angle measurements."""
        # Reset odometry
        pass


class ColorSensor:
    """Pybricks-compatible color sensor."""
    
    def __init__(self, robot: Robot, port: Port):
        """Initialize color sensor."""
        self.robot = robot
        self.port = port
        self.sensor = robot.get_sensor("color_down")  # Default color sensor
    
    def color(self) -> Color:
        """Get detected color."""
        if self.sensor:
            return self.sensor.get_reading()
        return Color.NONE
    
    def ambient(self) -> int:
        """Get ambient light level (0-100)."""
        if self.sensor:
            return self.sensor.get_ambient_light()
        return 0
    
    def reflection(self) -> int:
        """Get reflected light level (0-100)."""
        if self.sensor:
            return self.sensor.get_reflection()
        return 0
    
    def rgb(self) -> Tuple[int, int, int]:
        """Get RGB color values."""
        if self.sensor:
            return self.sensor.get_rgb()
        return (0, 0, 0)


class UltrasonicSensor:
    """Pybricks-compatible ultrasonic sensor."""
    
    def __init__(self, robot: Robot, port: Port):
        """Initialize ultrasonic sensor."""
        self.robot = robot
        self.port = port
        self.sensor = robot.get_sensor("ultrasonic_front")
    
    def distance(self) -> float:
        """Get distance in millimeters."""
        if self.sensor:
            return self.sensor.get_reading()
        return 2550  # Max range
    
    def presence(self) -> bool:
        """Check if object is present."""
        return self.distance() < 2550


class GyroSensor:
    """Pybricks-compatible gyro sensor."""
    
    def __init__(self, robot: Robot, port: Port):
        """Initialize gyro sensor."""
        self.robot = robot
        self.port = port
        self.sensor = robot.get_sensor("gyro")
    
    def speed(self) -> float:
        """Get angular velocity in deg/s."""
        if self.sensor:
            return self.sensor.get_angular_velocity()
        return 0.0
    
    def angle(self) -> float:
        """Get angle in degrees."""
        if self.sensor:
            return self.sensor.get_reading()
        return 0.0
    
    def reset_angle(self, angle: float = 0):
        """Reset angle to specified value."""
        if self.sensor:
            self.sensor.reset(angle)


class TouchSensor:
    """Pybricks-compatible touch sensor."""
    
    def __init__(self, robot: Robot, port: Port):
        """Initialize touch sensor."""
        self.robot = robot
        self.port = port
        
        # Map port to sensor name
        sensor_map = {
            Port.S1: "touch_left",
            Port.S2: "touch_right",
            Port.S3: "touch_left",  # Fallback
            Port.S4: "touch_right"  # Fallback
        }
        
        sensor_name = sensor_map.get(port, "touch_left")
        self.sensor = robot.get_sensor(sensor_name)
    
    def pressed(self) -> bool:
        """Check if touch sensor is pressed."""
        if self.sensor:
            return self.sensor.get_reading()
        return False


class EV3Brick:
    """
    Simulated EV3 Brick with Pybricks-compatible API.
    
    Provides access to brick features like buttons, lights, speaker, etc.
    """
    
    def __init__(self, robot: Robot):
        """Initialize EV3 brick."""
        self.robot = robot
        self.light_color = Color.GREEN
        self.button_states = {
            'up': False,
            'down': False,
            'left': False,
            'right': False,
            'center': False
        }
    
    class light:
        """Control brick status light."""
        
        @staticmethod
        def on(color: Color):
            """Turn on light with specified color."""
            print(f"Light turned on with color: {color}")
            # TODO: Integrate with simulation renderer
        
        @staticmethod
        def off():
            """Turn off light."""
            print("Light turned off")
            # TODO: Integrate with simulation renderer
    
    class speaker:
        """Control brick speaker."""
        
        @staticmethod
        def beep(frequency: int = 1000, duration: int = 100):
            """Play a beep."""
            print(f"Speaker beep: {frequency}Hz for {duration}ms")
            # TODO: Integrate with simulation sound system
        
        @staticmethod
        def say(text: str):
            """Say text using text-to-speech."""
            print(f"Robot says: {text}")
    
    class buttons:
        """Read brick button states."""
        
        @staticmethod
        def pressed() -> List[str]:
            """Get list of currently pressed buttons."""
            return []  # Could integrate with keyboard input


class PybricksRobot:
    """
    High-level Pybricks-style robot interface.
    
    This class provides a familiar API for users coming from LEGO MINDSTORMS
    and Pybricks, making FLL-Sim accessible to students and educators.
    """
    
    def __init__(self, config: Optional[PybricksConfig] = None):
        """
        Initialize Pybricks-style robot.
        
        Args:
            config: Robot configuration
        """
        self.config = config or PybricksConfig()
        
        # Create underlying robot
        robot_config = RobotConfig(
            wheel_diameter=self.config.wheel_diameter,
            wheel_base=self.config.axle_track,
            max_speed=self.config.straight_speed * 2,  # Allow higher speeds
            max_angular_velocity=self.config.turn_rate * 2
        )
        
        self.robot = Robot(0, 0, 0, robot_config)
        
        # Create Pybricks-style components
        self.left_motor = Motor(self.robot, Port.A)
        self.right_motor = Motor(self.robot, Port.D)
        
        self.drive_base = DriveBase(
            self.robot, self.left_motor, self.right_motor,
            self.config.wheel_diameter, self.config.axle_track
        )
        
        # Sensors
        self.color_sensor = ColorSensor(self.robot, Port.S3)
        self.ultrasonic_sensor = UltrasonicSensor(self.robot, Port.S4)
        if self.config.use_gyro:
            self.gyro_sensor = GyroSensor(self.robot, Port.S2)
        self.touch_sensor = TouchSensor(self.robot, Port.S1)
        
        # Brick
        self.ev3 = EV3Brick(self.robot)
    
    def get_robot(self) -> Robot:
        """Get the underlying robot instance."""
        return self.robot
    
    def wait(self, time_ms: int):
        """Wait for specified time in milliseconds."""
        time.sleep(time_ms / 1000.0)


# Convenience functions
def wait(time_ms: int):
    """Wait for specified time in milliseconds."""
    time.sleep(time_ms / 1000.0)


def print_to_console(*args):
    """Print to console (for debugging)."""
    print(*args)


# Example usage and mission templates
class FLLMissions:
    """Pre-built mission templates for common FLL tasks."""
    
    @staticmethod
    def follow_line_until_color(robot: PybricksRobot, target_color: Color, speed: float = 100):
        """Follow a line until a specific color is detected."""
        robot.drive_base.drive(speed, 0)
        
        while robot.color_sensor.color() != target_color:
            wait(10)
        
        robot.drive_base.stop()
    
    @staticmethod
    def navigate_to_wall(robot: PybricksRobot, distance_mm: float = 50, speed: float = 100):
        """Navigate forward until close to a wall."""
        robot.drive_base.drive(speed, 0)
        
        while robot.ultrasonic_sensor.distance() > distance_mm:
            wait(10)
        
        robot.drive_base.stop()
    
    @staticmethod
    def turn_to_angle(robot: PybricksRobot, target_angle: float, speed: float = 50):
        """Turn to a specific absolute angle using gyro sensor."""
        if hasattr(robot, 'gyro_sensor'):
            current_angle = robot.gyro_sensor.angle()
            turn_amount = target_angle - current_angle
            robot.drive_base.turn(turn_amount)
    
    @staticmethod
    def square_path(robot: PybricksRobot, side_length: float = 200, speed: float = 100):
        """Drive in a square pattern."""
        for _ in range(4):
            robot.drive_base.straight(side_length)
            robot.drive_base.turn(90)
    
    @staticmethod
    def search_pattern(robot: PybricksRobot, search_distance: float = 300):
        """Execute a search pattern to find objects."""
        angles = [0, 45, -45, 90, -90, 180]
        
        for angle in angles:
            robot.drive_base.turn(angle)
            
            if robot.ultrasonic_sensor.distance() < 200:
                robot.ev3.speaker.beep()
                return True
            
            robot.drive_base.straight(search_distance / len(angles))
        
        return False
