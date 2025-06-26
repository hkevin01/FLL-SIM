# FLL-Sim GUI User Guide

## Overview

The FLL-Sim GUI provides a comprehensive graphical interface for the First Lego League Simulator. Built with PyQt6, it offers a modern, cross-platform interface that makes robot programming and simulation accessible through an intuitive point-and-click interface.

## Getting Started

### Launching the GUI

There are several ways to launch the GUI:

#### Option 1: Using the Launch Script (Recommended)
```bash
./run_gui.sh
```

#### Option 2: Direct Python Execution
```bash
python -m fll_sim.gui.main_gui
```

#### Option 3: From Project Directory
```bash
cd /path/to/FLL-SIM
PYTHONPATH=src python src/fll_sim/gui/main_gui.py
```

## GUI Features

### Main Interface Tabs

#### 1. Quick Start Tab
- **Welcome Section**: Project overview and quick introduction
- **Quick Action Buttons**:
  - 🚀 Start Simulation: Launch the full simulation environment
  - 🎮 Run Demo: Try a quick demonstration with basic robot movement
  - 📚 View Examples: Browse example robot programs and missions
  - ⚙️ Configure Robot: Set up robot parameters and components
  - 🗺️ Load Mission: Choose from available FLL missions
  - 📊 Performance Monitor: View real-time performance metrics

#### 2. Configuration Tab
- **Simulation Profile**: Choose between beginner, intermediate, and advanced setups
- **Robot Configuration**: Select robot type and characteristics
- **FLL Season**: Choose the competition season (2024 SUBMERGED, 2023 CARGO CONNECT)
- **Advanced Settings**: Fine-tune simulation parameters

#### 3. Simulation Tab
- **Simulation Control**: Start, stop, pause, and reset simulations
- **Real-time Monitoring**: View simulation status and robot state
- **Mission Progress**: Track mission completion and scoring
- **Debug Tools**: Enable debug visualization and logging

#### 4. Missions Tab
- **Mission Browser**: View available FLL missions
- **Mission Details**: Read mission descriptions and requirements
- **Mission Editor**: Create and modify custom missions
- **Scoring System**: View scoring rules and current points

#### 5. Robot Tab
- **Robot Configuration**: Modify robot physical properties
- **Motor Setup**: Configure drive and auxiliary motors
- **Sensor Configuration**: Add and position sensors
- **Robot Designer**: Visual robot configuration tool

#### 6. Performance Monitor Tab
- **Real-time Metrics**: CPU usage, memory consumption, FPS
- **Mission Analytics**: Success rates, completion times, scores
- **Performance History**: Historical performance data and trends
- **Export Data**: Save performance data for analysis

### Menu Options

#### File Menu
- **New Simulation**: Create a new simulation configuration
- **Load Configuration**: Load saved simulation settings
- **Save Configuration**: Save current settings for later use
- **Exit**: Close the application

#### Simulation Menu
- **Start Simulation**: Launch the simulation with current settings
- **Stop Simulation**: Terminate running simulation
- **Run Demo**: Execute demonstration programs
- **Run Headless**: Run simulation without graphics

#### Tools Menu
- **Mission Editor**: Open the mission creation and editing interface
- **Robot Designer**: Open the visual robot configuration tool
- **Performance Monitor**: Switch to performance monitoring view

#### Help Menu
- **Documentation**: Access user documentation and guides
- **Examples**: Browse example programs and tutorials
- **About**: View application information and credits

## Advanced Features

### Mission Editor

The Mission Editor allows you to create custom FLL missions:

1. **Mission Information**:
   - Enter mission name and description
   - Select FLL season and difficulty level

2. **Mission Templates**:
   - Choose from pre-built mission templates
   - Load existing missions for modification

3. **Mission Elements**:
   - Add mission-specific objectives
   - Configure scoring rules
   - Set completion criteria

### Robot Designer

The Robot Designer provides visual robot configuration:

1. **Physical Properties Tab**:
   - Set robot dimensions (width, height)
   - Configure mass and moment of inertia
   - Adjust physical characteristics

2. **Motors Tab**:
   - Configure drive motor parameters
   - Set wheel diameter and separation
   - Add auxiliary motors (arms, lifts, etc.)

3. **Sensors Tab**:
   - Add sensors to specific ports
   - Position sensors on the robot
   - Configure sensor orientation and settings

### Performance Monitoring

Real-time performance tracking includes:

- **System Metrics**: CPU, memory, and FPS monitoring
- **Mission Metrics**: Success rates, scores, and completion times
- **Robot Metrics**: Motor usage, sensor readings, and battery level
- **Historical Data**: Performance trends over time
- **Data Export**: Save data in CSV or JSON formats

## Configuration Profiles

### Beginner Profile
- Simplified interface with essential features only
- Pre-configured robot with basic sensors
- Guided tutorials and examples
- Automatic error correction and assistance

### Intermediate Profile
- Full feature set with moderate complexity
- Configurable robot parameters
- Access to most missions and examples
- Performance monitoring enabled

### Advanced Profile
- Complete access to all features
- Full robot customization capabilities
- Advanced debugging and analysis tools
- Custom mission creation

## Tips and Best Practices

### Getting Started
1. Start with the **Quick Start** tab for an overview
2. Use **Run Demo** to see the simulator in action
3. Explore **Examples** to learn robot programming concepts
4. Configure your robot in the **Robot** tab before starting missions

### Mission Development
1. Use the **Mission Editor** to create custom challenges
2. Start with existing templates and modify them
3. Test missions thoroughly before using in competitions
4. Save mission configurations for later use

### Robot Configuration
1. Use the **Robot Designer** for visual configuration
2. Start with standard FLL robot dimensions
3. Add sensors gradually and test each addition
4. Save robot configurations as profiles

### Performance Optimization
1. Monitor performance in the **Performance Monitor** tab
2. Reduce simulation complexity if FPS drops below 30
3. Use headless mode for batch testing and analysis
4. Export performance data for detailed analysis

## Troubleshooting

### Common Issues

#### GUI Won't Start
- Ensure virtual environment is activated
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify Python path includes the src directory
- Check for conflicting GUI libraries

#### Simulation Crashes
- Reduce simulation complexity in Configuration tab
- Check robot configuration for invalid parameters
- Monitor system resources in Performance tab
- Review log files for error messages

#### Poor Performance
- Switch to a lower complexity profile
- Reduce the number of active sensors
- Disable debug visualization
- Close unnecessary applications

#### Mission Editor Issues
- Ensure mission templates are properly formatted
- Check that all required fields are filled
- Verify mission logic and scoring rules
- Save work frequently to prevent data loss

### Getting Help

1. **Documentation**: Check the help menu for detailed guides
2. **Examples**: Review example programs and configurations
3. **Log Files**: Check simulation logs for error details
4. **Community**: Join the FLL-Sim community for support

## Keyboard Shortcuts

- **Ctrl+N**: New simulation
- **Ctrl+O**: Open configuration
- **Ctrl+S**: Save configuration
- **F5**: Start simulation
- **F6**: Stop simulation
- **F11**: Toggle fullscreen
- **Ctrl+Q**: Quit application

## System Requirements

### Minimum Requirements
- Python 3.8 or higher
- 4 GB RAM
- Integrated graphics
- 1024x768 screen resolution

### Recommended Requirements
- Python 3.10 or higher
- 8 GB RAM
- Dedicated graphics card
- 1920x1080 screen resolution
- Multi-core processor

### Dependencies
- tkinter (GUI framework)
- pygame (graphics and input)
- pymunk (physics simulation)
- numpy (numerical computation)
- matplotlib (data visualization)
- PyYAML (configuration files)

---

*For more information, visit the FLL-Sim documentation or check the examples directory.*
