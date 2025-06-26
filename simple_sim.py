#!/usr/bin/env python3
"""
Simple FLL-Sim visualization test.

This script creates a basic simulation with a robot and game field
to test the visualization system.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pygame

from fll_sim.core.simulator import SimulationConfig, Simulator
from fll_sim.environment.game_map import GameMap, MapConfig
from fll_sim.robot.robot import Robot, RobotConfig


def create_demo_robot() -> Robot:
    """Create a demo robot."""
    config = RobotConfig(
        width=180.0,
        length=200.0,
        wheel_diameter=56.0,
        wheel_base=160.0,
        max_speed=400.0,
        max_angular_velocity=180.0,
        color=(255, 200, 0)  # Yellow robot
    )
    
    return Robot(x=300, y=300, angle=0, config=config)


def create_demo_map() -> GameMap:
    """Create a simple demo map."""
    config = MapConfig(
        width=1200,
        height=800,
        show_grid=True,
        surface_color=(240, 240, 240)
    )
    
    return GameMap(config)


def main():
    """Run the simple simulation."""
    print("Starting Simple FLL-Sim Visualization Test...")
    
    # Create robot and map
    robot = create_demo_robot()
    game_map = create_demo_map()
    
    # Configure simulation
    sim_config = SimulationConfig(
        window_width=1200,
        window_height=800,
        fps=60,
        real_time_factor=1.0,
        show_debug_info=True
    )
    
    # Create and start simulator
    simulator = Simulator(robot, game_map, sim_config)
    
    print("\nSimulation Controls:")
    print("  Arrow Keys: Manual robot control")
    print("  SPACE: Pause/Resume")
    print("  R: Reset robot position")
    print("  Q: Quit simulation")
    print("\nStarting visualization...")
    
    try:
        # Start simulation
        simulator.start()
    except Exception as e:
        print(f"Error running simulation: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
