#!/usr/bin/env python3
"""
FLL-Sim Setup and Configuration Script

This script helps users set up FLL-Sim, configure their environment,
and get started with the simulator quickly.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("Error: FLL-Sim requires Python 3.8 or higher")
        print(f"Current Python version: {sys.version}")
        return False
    return True


def install_dependencies(dev_mode=False):
    """Install required dependencies."""
    print("Installing dependencies...")
    
    try:
        # Install main dependencies
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        if dev_mode:
            print("Installing development dependencies...")
            dev_packages = [
                "pytest>=7.0.0",
                "pytest-cov>=4.0.0", 
                "black>=22.0.0",
                "flake8>=5.0.0",
                "mypy>=1.0.0",
                "pre-commit>=2.20.0"
            ]
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + dev_packages)
        
        print("Dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False


def setup_project_structure():
    """Set up project directory structure."""
    print("Setting up project structure...")
    
    directories = [
        "configs",
        "configs/robots",
        "configs/simulations", 
        "configs/maps",
        "configs/missions",
        "configs/profiles",
        "data",
        "data/maps",
        "data/missions",
        "data/logs",
        "examples",
        "scripts"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  Created: {directory}/")
    
    print("Project structure created!")


def create_launcher_script():
    """Create a convenient launcher script."""
    print("Creating launcher script...")
    
    launcher_content = '''#!/usr/bin/env python3
"""
FLL-Sim Launcher Script

Convenient script to launch FLL-Sim with various options.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Import and run main
from main import main

if __name__ == "__main__":
    sys.exit(main())
'''
    
    with open("fll-sim", "w") as f:
        f.write(launcher_content)
    
    # Make executable on Unix systems
    if os.name != "nt":
        os.chmod("fll-sim", 0o755)
    
    print("Launcher script created: ./fll-sim")


def create_example_scripts():
    """Create example scripts for different use cases."""
    print("Creating example scripts...")
    
    examples = {
        "examples/basic_robot_control.py": '''#!/usr/bin/env python3
"""
Basic Robot Control Example

This example demonstrates basic robot movement and sensor usage.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from fll_sim.robot.pybricks_api import PybricksRobot, FLLMissions
from fll_sim.sensors.color_sensor import Color

def main():
    # Create robot
    robot = PybricksRobot()
    
    print("Starting basic robot control demo...")
    
    # Move in a square
    FLLMissions.square_path(robot, side_length=200, speed=100)
    
    # Search for objects
    if FLLMissions.search_pattern(robot, search_distance=300):
        robot.ev3.speaker.say("Found something!")
    
    print("Demo completed!")

if __name__ == "__main__":
    main()
''',
        
        "examples/mission_programming.py": '''#!/usr/bin/env python3
"""
Mission Programming Example

This example shows how to program a robot to complete FLL missions.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from fll_sim.robot.pybricks_api import PybricksRobot, FLLMissions, Color

def coral_nursery_mission(robot):
    """Complete the coral nursery mission."""
    print("Starting coral nursery mission...")
    
    # Navigate to coral area
    robot.drive_base.straight(300)
    robot.drive_base.turn(45)
    
    # Look for coral (red objects)
    FLLMissions.follow_line_until_color(robot, Color.RED)
    
    # Deliver coral pieces
    robot.drive_base.straight(100)
    robot.wait(1000)  # Simulate coral placement
    
    # Return to base
    robot.drive_base.turn(180)
    robot.drive_base.straight(400)
    
    print("Coral nursery mission completed!")

def main():
    robot = PybricksRobot()
    
    # Configure for mission run
    robot.drive_base.settings(
        straight_speed=200,
        turn_rate=90
    )
    
    # Execute mission
    coral_nursery_mission(robot)

if __name__ == "__main__":
    main()
''',

        "examples/sensor_calibration.py": '''#!/usr/bin/env python3
"""
Sensor Calibration Example

This example demonstrates sensor reading and calibration.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from fll_sim.robot.pybricks_api import PybricksRobot
import time

def calibrate_sensors(robot):
    """Calibrate all robot sensors."""
    print("Starting sensor calibration...")
    
    # Color sensor calibration
    print("\\nColor Sensor Calibration:")
    print("Place robot over different colors and observe readings...")
    
    for i in range(10):
        color = robot.color_sensor.color()
        reflection = robot.color_sensor.reflection()
        rgb = robot.color_sensor.rgb()
        
        print(f"  Reading {i+1}: Color={color}, Reflection={reflection}, RGB={rgb}")
        time.sleep(1)
    
    # Ultrasonic sensor calibration
    print("\\nUltrasonic Sensor Calibration:")
    print("Move obstacles in front of robot and observe readings...")
    
    for i in range(10):
        distance = robot.ultrasonic_sensor.distance()
        presence = robot.ultrasonic_sensor.presence()
        
        print(f"  Reading {i+1}: Distance={distance}mm, Presence={presence}")
        time.sleep(1)
    
    # Gyro sensor calibration
    if hasattr(robot, 'gyro_sensor'):
        print("\\nGyro Sensor Calibration:")
        print("Rotate robot and observe angle readings...")
        
        robot.gyro_sensor.reset_angle(0)
        
        for i in range(10):
            angle = robot.gyro_sensor.angle()
            speed = robot.gyro_sensor.speed()
            
            print(f"  Reading {i+1}: Angle={angle}°, Speed={speed}°/s")
            time.sleep(1)
    
    print("\\nSensor calibration completed!")

def main():
    robot = PybricksRobot()
    calibrate_sensors(robot)

if __name__ == "__main__":
    main()
'''
    }
    
    # Create example files
    for filename, content in examples.items():
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "w") as f:
            f.write(content)
        
        # Make executable on Unix systems
        if os.name != "nt":
            os.chmod(filename, 0o755)
        
        print(f"  Created: {filename}")
    
    print("Example scripts created!")


def run_initial_tests():
    """Run basic tests to verify installation."""
    print("Running initial tests...")
    
    try:
        # Test imports
        sys.path.insert(0, "src")
        
        print("  Testing core imports...")
        from fll_sim.core.simulator import Simulator, SimulationConfig
        from fll_sim.robot.robot import Robot, RobotConfig
        from fll_sim.robot.pybricks_api import PybricksRobot
        from fll_sim.environment.game_map import GameMap
        from fll_sim.environment.mission import MissionManager
        
        print("  Testing configuration system...")
        from fll_sim.config.config_manager import ConfigManager
        config_manager = ConfigManager()
        
        print("  Testing robot creation...")
        robot_config = config_manager.load_robot_config("standard_fll")
        robot = Robot(0, 0, 0, robot_config)
        
        print("  Testing Pybricks API...")
        pybricks_robot = PybricksRobot()
        
        print("✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def setup_development_tools(install_hooks=True):
    """Set up development tools and pre-commit hooks."""
    print("Setting up development tools...")
    
    if install_hooks:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pre-commit"])
            subprocess.check_call(["pre-commit", "install"])
            print("  Pre-commit hooks installed")
        except subprocess.CalledProcessError:
            print("  Warning: Could not install pre-commit hooks")
    
    # Create .vscode settings
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    settings = {
        "python.defaultInterpreterPath": sys.executable,
        "python.linting.enabled": True,
        "python.linting.flake8Enabled": True,
        "python.formatting.provider": "black",
        "python.testing.pytestEnabled": True,
        "python.testing.pytestArgs": ["tests"],
        "files.associations": {
            "*.yaml": "yaml"
        }
    }
    
    import json
    with open(vscode_dir / "settings.json", "w") as f:
        json.dump(settings, f, indent=2)
    
    print("  VS Code settings created")


def print_getting_started():
    """Print getting started information."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          FLL-Sim Setup Complete!                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎉 FLL-Sim has been successfully set up!

Quick Start:
  1. Run the simulator:
     ./fll-sim

  2. Run with specific profile:
     ./fll-sim --profile beginner

  3. Try the examples:
     python examples/basic_robot_control.py
     python examples/mission_programming.py

  4. Explore configurations:
     ls configs/

Useful Commands:
  • ./fll-sim --help                 - Show all options
  • ./fll-sim --headless             - Run without graphics
  • ./fll-sim --demo basic           - Run basic demo
  • python main.py                   - Direct Python execution

Documentation:
  • docs/project_plan.md             - Project overview
  • docs/project_progress.md         - Current progress
  • examples/                        - Example scripts
  • configs/                         - Configuration files

Need Help?
  • Check the documentation in docs/
  • Run examples to see the system in action
  • Use --debug flag for troubleshooting

Happy robot programming! 🤖
""")


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="FLL-Sim Setup Script")
    parser.add_argument("--dev", action="store_true", 
                       help="Set up development environment")
    parser.add_argument("--skip-deps", action="store_true",
                       help="Skip dependency installation")
    parser.add_argument("--skip-tests", action="store_true",
                       help="Skip initial tests")
    parser.add_argument("--no-examples", action="store_true",
                       help="Don't create example scripts")
    
    args = parser.parse_args()
    
    print("FLL-Sim Setup Starting...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install dependencies
    if not args.skip_deps:
        if not install_dependencies(dev_mode=args.dev):
            return 1
    
    # Set up project structure
    setup_project_structure()
    
    # Create launcher script
    create_launcher_script()
    
    # Create example scripts
    if not args.no_examples:
        create_example_scripts()
    
    # Set up development tools
    if args.dev:
        setup_development_tools()
    
    # Run tests
    if not args.skip_tests:
        if not run_initial_tests():
            print("\nWarning: Some tests failed. FLL-Sim may not work correctly.")
            print("Try running setup again or check the error messages above.")
            return 1
    
    # Print getting started info
    print_getting_started()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
