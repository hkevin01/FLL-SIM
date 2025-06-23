"""
FLL-Sim: First Lego League Robot and Map Simulator

A comprehensive Python-based simulation environment for First Lego League competitions.
"""

__version__ = "0.1.0"
__author__ = "FLL-Sim Development Team"
__email__ = "dev@fll-sim.org"

from .core.simulator import Simulator
from .robot.robot import Robot
from .environment.game_map import GameMap
from .environment.mission import Mission
from .sensors.sensor_base import Sensor
from .sensors.color_sensor import ColorSensor
from .sensors.ultrasonic_sensor import UltrasonicSensor
from .sensors.gyro_sensor import GyroSensor
from .sensors.touch_sensor import TouchSensor

__all__ = [
    "Simulator",
    "Robot",
    "GameMap",
    "Mission",
    "Sensor",
    "ColorSensor",
    "UltrasonicSensor", 
    "GyroSensor",
    "TouchSensor",
]
