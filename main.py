#!/usr/bin/env python3
"""
FLL-Sim Main Entry Point

This script demonstrates the complete FLL-Sim system with:
- Game map loading with FLL-specific missions
- Robot control using both low-level and Pybricks-style APIs
- Mission execution and scoring
- Real-time visualization
- AI-driven path planning example
"""

import argparse
import os
import sys

import pygame  # noqa: E402

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fll_sim.core.simulator import SimulationConfig, Simulator  # noqa: E402
from fll_sim.environment.game_map import GameMap, MapConfig  # noqa: E402
from fll_sim.environment.mission import MissionManager  # noqa: E402
from fll_sim.robot.pybricks_api import (FLLMissions,  # noqa: E402
                                        PybricksConfig, PybricksRobot)
from fll_sim.robot.robot import Robot, RobotConfig  # noqa: E402
from fll_sim.sensors.color_sensor import Color  # noqa: E402


def create_demo_robot() -> Robot:
    """Create a demo robot with standard FLL configuration."""
    config = RobotConfig(
        width=180.0,
        length=200.0,
        wheel_diameter=56.0,
        wheel_base=160.0,
        max_speed=400.0,
        max_angular_velocity=180.0,
        color=(255, 200, 0)  # Yellow robot
    )

    return Robot(x=100, y=100, angle=0, config=config)


def create_demo_map() -> GameMap:
    """Create a demo FLL game map with missions."""
    # Create base map with custom size
    config = MapConfig(width=2400, height=1200)
    game_map = GameMap(config)

    # Load official season map and missions
    game_map.load_fll_season_map("2024-SUBMERGED")

    return game_map


def demo_basic_movement(robot: Robot):
    """Demonstrate basic robot movement commands."""
    print("Demo: Basic Movement")

    # Queue movement commands
    robot.move_forward(200, 50)  # Forward 200mm at 50% speed
    robot.turn_right(90, 30)     # Turn right 90 degrees
    robot.move_forward(150, 40)  # Forward 150mm
    robot.turn_left(45, 30)      # Turn left 45 degrees
    robot.move_backward(100, 30)  # Backward 100mm
    robot.wait(1.0)              # Wait 1 second


def demo_pybricks_api(pybricks_robot: PybricksRobot):
    """Demonstrate Pybricks-style API usage."""
    print("Demo: Pybricks API")

    # Configure movement settings
    pybricks_robot.drive_base.settings(
        straight_speed=200,
        turn_rate=100
    )

    # Execute missions using familiar Pybricks commands
    FLLMissions.square_path(pybricks_robot, side_length=300, speed=150)

    # Color-based navigation
    print("Searching for red line...")
    FLLMissions.follow_line_until_color(pybricks_robot, Color.RED, speed=100)

    # Wall approach
    print("Approaching wall...")
    FLLMissions.navigate_to_wall(pybricks_robot, distance_mm=100, speed=80)

    # Search pattern
    print("Executing search pattern...")
    found = FLLMissions.search_pattern(pybricks_robot, search_distance=400)
    if found:
        pybricks_robot.ev3.speaker.say("Object found!")


def demo_mission_system(mission_manager: MissionManager, robot: Robot):
    """Demonstrate mission system with scoring."""
    print("Demo: Mission System")

    # Ensure missions are loaded
    if not mission_manager.missions:
        mission_manager.load_fll_season("2024-SUBMERGED")

    # Start first available mission
    missions = mission_manager.get_available_missions()
    if not missions:
        print("No available missions.")
        return

    mission = missions[0]
    print(f"Starting mission: {mission.name}")
    started = mission_manager.start_mission(mission.mission_id)
    if not started:
        print("Failed to start mission.")
        return

    # Simulate environment and robot state to satisfy conditions
    # Move coral_sample to target area for Coral Nursery mission
    env_objects = {k: v.copy() for k, v in getattr(
        getattr(robot, 'game_map', None), 'mission_objects', {}).items()}
    # Fallback to empty if robot has no reference to map
    if not env_objects:
        env_objects = {"coral_sample": {"x": 1800, "y": 900}}
    else:
        if "coral_sample" in env_objects:
            env_objects["coral_sample"].update({"x": 1800, "y": 900})

    robot_state = {
        'position': {'x': 1800, 'y': 900, 'angle': 0},
        'sensors': {'color': 'blue'},
        'speed': 100.0,
        'energy_used': 10.0,
        'distance_traveled': 500.0,
    }
    environment_state = {'objects': env_objects}

    import time as _time

    # Hold condition for > 2 seconds to satisfy duration
    start = _time.time()
    while _time.time() - start < 2.2:
        mission_manager.update_active_mission(robot_state, environment_state)
        _time.sleep(0.1)

    summary = mission_manager.get_session_summary()
    print("Session Summary:")
    print(f"  Total Score: {summary['total_score']}")
    print(f"  Missions Completed: {summary['completed_missions']}")
    if summary['session_time'] is not None:
        print(f"  Session Time: {summary['session_time']:.1f}s")


def demo_ai_pathfinding(robot: Robot, game_map: GameMap):
    """
    Demonstrate AI-driven pathfinding (placeholder for future
    implementation).
    """
    print("Demo: AI Pathfinding (Placeholder)")

    # This would integrate with actual AI pathfinding algorithms
    print("Planning optimal path to mission areas...")
    print("Avoiding obstacles using A* algorithm...")
    print("Optimizing for mission scoring efficiency...")

    # Simple waypoint following example
    waypoints = [
        (300, 200),
        (600, 400),
        (900, 300),
        (1200, 600)
    ]

    print(f"Following waypoint path: {waypoints}")
    for i, (x, y) in enumerate(waypoints):
        print(f"  Navigating to waypoint {i+1}: ({x}, {y})")

        # Calculate distance and direction
        dx = x - robot.x
        dy = y - robot.y
        distance = (dx**2 + dy**2)**0.5

        # Queue movement (simplified)
        robot.move_forward(distance, 40)
        robot.wait(0.5)


def run_simulation_demo(headless: bool = False):
    """Run the complete simulation demo."""
    print("Starting FLL-Sim Demo...")

    # Create components
    robot = create_demo_robot()
    game_map = create_demo_map()

    # Create mission manager
    mission_manager = game_map.mission_manager

    # Create Pybricks-style robot for high-level API demo
    pybricks_config = PybricksConfig(
        wheel_diameter=56,
        axle_track=160,
        use_gyro=True,
        straight_speed=200
    )
    pybricks_robot = PybricksRobot(pybricks_config)

    # Configure simulation
    sim_config = SimulationConfig(
        window_width=1400,
        window_height=900,
        fps=60,
        real_time_factor=1.0,
        show_debug_info=True
    )

    if headless:
        # Run without visualization for testing
        print("Running headless simulation...")

        # Demo basic movement
        demo_basic_movement(robot)

        # Demo mission system
        demo_mission_system(mission_manager, robot)

        # Demo AI pathfinding
        demo_ai_pathfinding(robot, game_map)

        print("Headless demo completed!")
        return

    # Create and start simulator
    simulator = Simulator(robot, game_map, sim_config)

    # Add mission callbacks
    def on_mission_complete(mission_id: str, success: bool):
        status = 'Success' if success else 'Failed'
        print(f"Mission {mission_id} completed: {status}")

    simulator.add_mission_callback(on_mission_complete)

    # Demo different robot control methods
    print("\nControls:")
    print("  Arrow Keys: Manual robot control")
    print("  SPACE: Pause/Resume simulation")
    print("  R: Reset simulation")
    print("  D: Toggle debug visualization")
    print("  Q: Quit simulation")
    print("  1: Demo basic movement")
    print("  2: Demo Pybricks API")
    print("  3: Demo mission system")
    print("  4: Demo AI pathfinding")

    # Enhanced input handling
    def handle_demo_keys(event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                demo_basic_movement(robot)
            elif event.key == pygame.K_2:
                demo_pybricks_api(pybricks_robot)
            elif event.key == pygame.K_3:
                demo_mission_system(mission_manager, robot)
            elif event.key == pygame.K_4:
                demo_ai_pathfinding(robot, game_map)

    # Add custom event handler
    def enhanced_handle_events():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                simulator.stop()
            elif event.type == pygame.KEYDOWN:
                if event.key in simulator.key_handlers:
                    simulator.key_handlers[event.key]()
                else:
                    handle_demo_keys(
                        pygame.event.Event(pygame.KEYDOWN, key=event.key)
                    )
                    robot.handle_key_event(event)
            elif event.type == pygame.KEYUP:
                robot.handle_key_event(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                simulator._handle_mouse_click(event)

    simulator._handle_events = enhanced_handle_events

    print("\nStarting interactive simulation...")
    print("Use the controls above to interact with the simulation.")

    # Start simulation
    simulator.start()


def main():
    """Main entry point with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="FLL-Sim - First Lego League Simulator"
    )
    parser.add_argument(
        "--headless", action="store_true",
        help="Run simulation without graphics (for testing)"
    )
    parser.add_argument(
        "--demo", choices=["basic", "pybricks", "missions", "ai"],
        help="Run specific demo"
    )
    parser.add_argument(
        "--gui", action="store_true",
        help="Launch the GUI interface"
    )
    parser.add_argument("--config", type=str, help="Load configuration file")
    parser.add_argument(
        "--season", type=str, default="2024",
        help="FLL season year (default: 2024)"
    )

    args = parser.parse_args()

    try:
        if args.gui:
            print("Launching FLL-Sim GUI...")
            try:
                from fll_sim.gui.main_gui import main as gui_main
                return gui_main()
            except ImportError as e:
                print(f"GUI not available: {e}")
                print("Make sure PyQt6 is installed: pip install PyQt6")
                return 1
        elif args.demo:
            print(f"Running {args.demo} demo...")
            # Run specific demo based on argument
            if args.demo == "basic":
                robot = create_demo_robot()
                demo_basic_movement(robot)
            elif args.demo == "pybricks":
                pybricks_robot = PybricksRobot()
                demo_pybricks_api(pybricks_robot)
            elif args.demo == "missions":
                robot = create_demo_robot()
                game_map = create_demo_map()
                mission_manager = game_map.mission_manager
                demo_mission_system(mission_manager, robot)
            elif args.demo == "ai":
                robot = create_demo_robot()
                game_map = create_demo_map()
                demo_ai_pathfinding(robot, game_map)
        else:
            # Run full simulation
            run_simulation_demo(headless=args.headless)

    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
if __name__ == "__main__":
    sys.exit(main())
