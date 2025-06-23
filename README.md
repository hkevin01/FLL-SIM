# FLL-Sim: First Lego League Robot and Map Simulator

A comprehensive Python-based simulation environment for First Lego League competitions, featuring realistic robot physics, interactive game maps, and mission scenarios.

## 🎯 Overview

FLL-Sim provides a virtual environment for testing and developing strategies for First Lego League competitions. The simulator includes:

- **Robot Simulation**: Physics-based LEGO robot with customizable sensors and actuators
- **Map Environment**: Interactive game mat with missions and obstacles
- **Mission Framework**: Configurable challenges based on FLL seasons
- **Visualization**: Real-time 2D/3D visualization of robot and environment
- **Programming Interface**: Python API for robot control and autonomous programming

## 🚀 Features

- ✅ Realistic robot physics simulation
- ✅ Customizable robot configurations
- ✅ Interactive game mat with obstacles and missions
- ✅ Sensor simulation (color, ultrasonic, gyro, touch)
- ✅ Motor control and movement mechanics
- ✅ Mission scoring system
- ✅ Real-time visualization
- ✅ Educational programming interface
- ✅ Competition timer and rules enforcement

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd FLL-Sim
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package in development mode:
```bash
pip install -e .
```

## 🎮 Quick Start

```python
from fll_sim import Robot, GameMap, Simulator

# Create a robot
robot = Robot(x=100, y=100, angle=0)

# Load a game map
game_map = GameMap.load_season("2024-submerged")

# Create simulator
sim = Simulator(robot, game_map)

# Run simulation
sim.start()

# Program your robot
robot.move_forward(distance=500)  # Move 500mm forward
robot.turn_left(degrees=90)       # Turn 90 degrees left
robot.move_forward(distance=300)  # Move 300mm forward
```

## 📁 Project Structure

```
FLL-Sim/
├── src/fll_sim/           # Main source code
│   ├── core/              # Core simulation engine
│   ├── robot/             # Robot implementation
│   ├── environment/       # Game map and obstacles
│   ├── sensors/           # Sensor implementations
│   ├── missions/          # Mission definitions
│   └── visualization/     # Rendering and UI
├── tests/                 # Test suite
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── examples/              # Example programs
└── assets/                # Game assets and resources
```

## 📚 Documentation

- [Project Plan](docs/project_plan.md)
- [API Reference](docs/api_reference.md)
- [User Guide](docs/user_guide.md)
- [Developer Guide](docs/developer_guide.md)

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest tests/ --cov=src/fll_sim --cov-report=html
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- First Lego League organization for inspiration
- LEGO Education for the educational robotics platform
- The open-source robotics community

## 📞 Support

For questions and support:
- Open an issue on GitHub
- Check the [documentation](docs/)
- Join our community discussions

---

**Note**: This is an educational simulation and is not officially affiliated with FIRST or LEGO Group.
