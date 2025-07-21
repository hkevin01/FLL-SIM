# FLL-Sim: First Lego League Robot and Map Simulator

[![Build Status](https://img.shields.io/github/actions/workflow/status/hkevin01/FLL-SIM/ci.yml?branch=main)](https://github.com/hkevin01/FLL-SIM/actions)
[![Version](https://img.shields.io/badge/version-0.9.0-blue)](https://github.com/hkevin01/FLL-SIM/releases)
[![Coverage](https://img.shields.io/codecov/c/github/hkevin01/FLL-SIM?style=flat)](https://codecov.io/gh/hkevin01/FLL-SIM)
[![Phase](https://img.shields.io/badge/phase-Educational%20Platform%20%26%20Community-yellow)](docs/project_plan.md)
[![Educational Ready](https://img.shields.io/badge/educational-ready-brightgreen)](docs/project_plan.md)
[![Multi-Robot](https://img.shields.io/badge/multi--robot-supported-blue)](docs/project_plan.md)
[![AI Integration](https://img.shields.io/badge/AI-integration%20planned-purple)](docs/project_plan.md)

---

## 🚦 Current Status: Educational Platform & Community (Phase 4)
**Phase 3.5 Completed — July 2025**
**Phase 4 In Progress — Q1 2026**
- All core competition features implemented and tested.
- Multi-robot support, official timer, scoring, and advanced reliability simulation are live.
- Educational modules (tutorial system, guided exercises) under development.
- Ready for classroom, team, and tournament use. Community and curriculum features coming soon.

---

## 🎯 Overview

FLL-Sim provides a virtual environment for testing and developing strategies for First Lego League competitions. The simulator includes:

- **Robot Simulation**: Physics-based LEGO robot with customizable sensors and actuators
- **Map Environment**: Interactive game mat with missions and obstacles
- **Mission Framework**: Configurable challenges based on FLL seasons
- **Visualization**: Real-time 2D/3D visualization of robot and environment
- **Programming Interface**: Python API for robot control and autonomous programming
- **Competition Mode**: Official FLL timer, rules enforcement, scoring, and tournament features
- **Multi-Robot Support**: Simulate multiple robots, team coordination, and collision
- **Advanced Simulation**: Battery, hardware reliability, and performance analytics

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
- ✅ Multi-robot simulation and coordination
- ✅ Advanced reliability and performance analytics
- ✅ **New:** Modular tutorial system and guided programming exercises (Phase 4)
- ✅ **Planned:** Community content sharing, curriculum integration, and AI-driven features

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

## 📈 Roadmap & Milestones
- **Q4 2025:** Competition features and multi-robot support (v0.9)
- **Q1 2026:** Educational platform & community features (v1.0)
- **Q2-Q3 2026:** AI integration and advanced analytics
- **Q4 2026:** Enterprise platform and commercial features (v2.0)

For full details, see [Project Plan](docs/project_plan.md).
