"""
Configuration management for FLL-Sim.

This module provides configuration loading, validation, and management
for different simulation scenarios, robot setups, and FLL seasons.
"""

import yaml
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
import os

from ..robot.robot import RobotConfig
from ..core.simulator import SimulationConfig
from ..robot.pybricks_api import PybricksConfig


@dataclass
class SimulationProfile:
    """Complete simulation configuration profile."""
    name: str
    description: str
    robot_config: RobotConfig
    simulation_config: SimulationConfig
    pybricks_config: PybricksConfig
    fll_season: str = "2024"
    map_config: Dict[str, Any] = None
    mission_config: Dict[str, Any] = None


class ConfigManager:
    """
    Configuration manager for FLL-Sim.
    
    Handles loading, saving, and validation of simulation configurations.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory to store configuration files
        """
        if config_dir is None:
            # Default to configs directory in project root
            project_root = Path(__file__).parent.parent.parent.parent
            config_dir = project_root / "configs"
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.config_dir / "robots").mkdir(exist_ok=True)
        (self.config_dir / "simulations").mkdir(exist_ok=True)
        (self.config_dir / "maps").mkdir(exist_ok=True)
        (self.config_dir / "missions").mkdir(exist_ok=True)
        (self.config_dir / "profiles").mkdir(exist_ok=True)
        
        # Load default configurations
        self._create_default_configs()
    
    def _create_default_configs(self):
        """Create default configuration files if they don't exist."""
        
        # Default robot configurations
        default_robots = {
            "standard_fll": {
                "name": "Standard FLL Robot",
                "description": "Standard LEGO MINDSTORMS robot for FLL competitions",
                "width": 180.0,
                "length": 200.0,
                "mass": 1.0,
                "wheel_diameter": 56.0,
                "wheel_base": 160.0,
                "max_speed": 400.0,
                "max_angular_velocity": 180.0,
                "acceleration": 800.0,
                "friction": 0.7,
                "restitution": 0.1,
                "color": [255, 200, 0]
            },
            "compact_robot": {
                "name": "Compact Robot",
                "description": "Smaller, more maneuverable robot design",
                "width": 150.0,
                "length": 160.0,
                "mass": 0.8,
                "wheel_diameter": 43.0,
                "wheel_base": 120.0,
                "max_speed": 350.0,
                "max_angular_velocity": 200.0,
                "acceleration": 900.0,
                "friction": 0.8,
                "restitution": 0.1,
                "color": [0, 150, 255]
            },
            "heavy_pusher": {
                "name": "Heavy Pusher Robot",
                "description": "Larger robot designed for pushing missions",
                "width": 220.0,
                "length": 250.0,
                "mass": 1.5,
                "wheel_diameter": 62.0,
                "wheel_base": 180.0,
                "max_speed": 300.0,
                "max_angular_velocity": 150.0,
                "acceleration": 600.0,
                "friction": 0.9,
                "restitution": 0.05,
                "color": [255, 100, 100]
            }
        }
        
        self._save_config_file("robots/defaults.yaml", default_robots)
        
        # Default simulation configurations
        default_simulations = {
            "standard": {
                "name": "Standard Simulation",
                "description": "Standard simulation settings for FLL practice",
                "physics_fps": 60,
                "physics_dt": 0.016667,
                "gravity": [0, 0],
                "window_width": 1200,
                "window_height": 800,
                "fps": 60,
                "real_time_factor": 1.0,
                "show_debug_info": False,
                "show_physics_debug": False
            },
            "competition": {
                "name": "Competition Mode",
                "description": "Simulation settings matching competition conditions",
                "physics_fps": 60,
                "physics_dt": 0.016667,
                "gravity": [0, 0],
                "window_width": 1400,
                "window_height": 900,
                "fps": 60,
                "real_time_factor": 1.0,
                "show_debug_info": False,
                "show_physics_debug": False
            },
            "debug": {
                "name": "Debug Mode",
                "description": "Simulation with debug visualization enabled",
                "physics_fps": 60,
                "physics_dt": 0.016667,
                "gravity": [0, 0],
                "window_width": 1600,
                "window_height": 1000,
                "fps": 60,
                "real_time_factor": 0.5,
                "show_debug_info": True,
                "show_physics_debug": True
            }
        }
        
        self._save_config_file("simulations/defaults.yaml", default_simulations)
        
        # Default Pybricks configurations
        default_pybricks = {
            "standard": {
                "name": "Standard Pybricks Config",
                "description": "Standard configuration for Pybricks-style API",
                "wheel_diameter": 56.0,
                "axle_track": 160.0,
                "use_gyro": True,
                "straight_speed": 200.0,
                "straight_acceleration": 400.0,
                "turn_rate": 100.0,
                "turn_acceleration": 300.0
            },
            "fast": {
                "name": "Fast Robot Config",
                "description": "Higher speed configuration for experienced users",
                "wheel_diameter": 56.0,
                "axle_track": 160.0,
                "use_gyro": True,
                "straight_speed": 400.0,
                "straight_acceleration": 800.0,
                "turn_rate": 200.0,
                "turn_acceleration": 600.0
            },
            "precise": {
                "name": "Precision Config",
                "description": "Lower speed configuration for precise movements",
                "wheel_diameter": 56.0,
                "axle_track": 160.0,
                "use_gyro": True,
                "straight_speed": 100.0,
                "straight_acceleration": 200.0,
                "turn_rate": 50.0,
                "turn_acceleration": 150.0
            }
        }
        
        self._save_config_file("robots/pybricks_defaults.yaml", default_pybricks)
        
        # Default simulation profiles
        default_profiles = {
            "beginner": {
                "name": "Beginner Profile",
                "description": "Profile for new FLL teams and students",
                "robot_config": "standard_fll",
                "simulation_config": "debug",
                "pybricks_config": "precise",
                "fll_season": "2024",
                "features": {
                    "show_sensor_visualization": True,
                    "show_mission_hints": True,
                    "slow_motion_mode": True,
                    "guided_tutorials": True
                }
            },
            "intermediate": {
                "name": "Intermediate Profile", 
                "description": "Profile for teams with some FLL experience",
                "robot_config": "standard_fll",
                "simulation_config": "standard",
                "pybricks_config": "standard",
                "fll_season": "2024",
                "features": {
                    "show_sensor_visualization": True,
                    "show_mission_hints": False,
                    "slow_motion_mode": False,
                    "guided_tutorials": False
                }
            },
            "advanced": {
                "name": "Advanced Profile",
                "description": "Profile for experienced teams and competitions",
                "robot_config": "standard_fll",
                "simulation_config": "competition",
                "pybricks_config": "fast",
                "fll_season": "2024",
                "features": {
                    "show_sensor_visualization": False,
                    "show_mission_hints": False,
                    "slow_motion_mode": False,
                    "guided_tutorials": False,
                    "competition_timer": True,
                    "scoring_penalties": True
                }
            }
        }
        
        self._save_config_file("profiles/defaults.yaml", default_profiles)
        
        # FLL season configurations
        fll_seasons = {
            "2024": {
                "name": "SUBMERGED℠",
                "description": "2024-2025 FLL Challenge season",
                "theme": "Ocean exploration and conservation",
                "table_size": [2400, 1800],
                "mission_count": 15,
                "max_score": 400,
                "time_limit": 150,
                "missions": [
                    "coral_nursery",
                    "shark_delivery", 
                    "research_vessel",
                    "whale_migration",
                    "submarine_voyage",
                    "scuba_diver",
                    "treasure_hunt",
                    "ocean_cleanup",
                    "sonar_discovery",
                    "deep_sea_exploration"
                ]
            },
            "2023": {
                "name": "MASTERPIECE℠",
                "description": "2023-2024 FLL Challenge season",
                "theme": "Arts and creativity",
                "table_size": [2400, 1800],
                "mission_count": 14,
                "max_score": 380,
                "time_limit": 150
            }
        }
        
        self._save_config_file("missions/fll_seasons.yaml", fll_seasons)
    
    def _save_config_file(self, relative_path: str, data: Dict[str, Any]):
        """Save configuration data to file."""
        file_path = self.config_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not file_path.exists():
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    def load_robot_config(self, name: str) -> RobotConfig:
        """Load robot configuration by name."""
        # Try to load from custom configs first
        config_file = self.config_dir / "robots" / f"{name}.yaml"
        if not config_file.exists():
            # Try defaults
            config_file = self.config_dir / "robots" / "defaults.yaml"
        
        with open(config_file, 'r') as f:
            configs = yaml.safe_load(f)
        
        if name not in configs:
            raise ValueError(f"Robot configuration '{name}' not found")
        
        config_data = configs[name]
        return RobotConfig(
            width=config_data["width"],
            length=config_data["length"],
            mass=config_data["mass"],
            wheel_diameter=config_data["wheel_diameter"],
            wheel_base=config_data["wheel_base"],
            max_speed=config_data["max_speed"],
            max_angular_velocity=config_data["max_angular_velocity"],
            acceleration=config_data["acceleration"],
            friction=config_data["friction"],
            restitution=config_data["restitution"],
            color=tuple(config_data["color"])
        )
    
    def load_simulation_config(self, name: str) -> SimulationConfig:
        """Load simulation configuration by name."""
        config_file = self.config_dir / "simulations" / "defaults.yaml"
        
        with open(config_file, 'r') as f:
            configs = yaml.safe_load(f)
        
        if name not in configs:
            raise ValueError(f"Simulation configuration '{name}' not found")
        
        config_data = configs[name]
        return SimulationConfig(
            physics_fps=config_data["physics_fps"],
            physics_dt=config_data["physics_dt"],
            gravity=tuple(config_data["gravity"]),
            window_width=config_data["window_width"],
            window_height=config_data["window_height"],
            fps=config_data["fps"],
            real_time_factor=config_data["real_time_factor"],
            show_debug_info=config_data["show_debug_info"],
            show_physics_debug=config_data["show_physics_debug"]
        )
    
    def load_pybricks_config(self, name: str) -> PybricksConfig:
        """Load Pybricks configuration by name."""
        config_file = self.config_dir / "robots" / "pybricks_defaults.yaml"
        
        with open(config_file, 'r') as f:
            configs = yaml.safe_load(f)
        
        if name not in configs:
            raise ValueError(f"Pybricks configuration '{name}' not found")
        
        config_data = configs[name]
        return PybricksConfig(
            wheel_diameter=config_data["wheel_diameter"],
            axle_track=config_data["axle_track"],
            use_gyro=config_data["use_gyro"],
            straight_speed=config_data["straight_speed"],
            straight_acceleration=config_data["straight_acceleration"],
            turn_rate=config_data["turn_rate"],
            turn_acceleration=config_data["turn_acceleration"]
        )
    
    def load_profile(self, name: str) -> SimulationProfile:
        """Load complete simulation profile by name."""
        config_file = self.config_dir / "profiles" / "defaults.yaml"
        
        with open(config_file, 'r') as f:
            profiles = yaml.safe_load(f)
        
        if name not in profiles:
            raise ValueError(f"Profile '{name}' not found")
        
        profile_data = profiles[name]
        
        return SimulationProfile(
            name=profile_data["name"],
            description=profile_data["description"],
            robot_config=self.load_robot_config(profile_data["robot_config"]),
            simulation_config=self.load_simulation_config(profile_data["simulation_config"]),
            pybricks_config=self.load_pybricks_config(profile_data["pybricks_config"]),
            fll_season=profile_data["fll_season"]
        )
    
    def save_profile(self, profile: SimulationProfile, filename: Optional[str] = None):
        """Save a simulation profile to file."""
        if filename is None:
            filename = f"{profile.name.lower().replace(' ', '_')}.yaml"
        
        file_path = self.config_dir / "profiles" / filename
        
        profile_data = {
            "name": profile.name,
            "description": profile.description,
            "robot_config": asdict(profile.robot_config),
            "simulation_config": asdict(profile.simulation_config),
            "pybricks_config": asdict(profile.pybricks_config),
            "fll_season": profile.fll_season
        }
        
        with open(file_path, 'w') as f:
            yaml.dump(profile_data, f, default_flow_style=False, sort_keys=False)
    
    def list_available_configs(self) -> Dict[str, List[str]]:
        """List all available configuration names."""
        configs = {
            "robots": [],
            "simulations": [],
            "pybricks": [],
            "profiles": [],
            "seasons": []
        }
        
        # Load robot configs
        robot_file = self.config_dir / "robots" / "defaults.yaml"
        if robot_file.exists():
            with open(robot_file, 'r') as f:
                configs["robots"] = list(yaml.safe_load(f).keys())
        
        # Load simulation configs
        sim_file = self.config_dir / "simulations" / "defaults.yaml"
        if sim_file.exists():
            with open(sim_file, 'r') as f:
                configs["simulations"] = list(yaml.safe_load(f).keys())
        
        # Load Pybricks configs
        pybricks_file = self.config_dir / "robots" / "pybricks_defaults.yaml"
        if pybricks_file.exists():
            with open(pybricks_file, 'r') as f:
                configs["pybricks"] = list(yaml.safe_load(f).keys())
        
        # Load profiles
        profile_file = self.config_dir / "profiles" / "defaults.yaml"
        if profile_file.exists():
            with open(profile_file, 'r') as f:
                configs["profiles"] = list(yaml.safe_load(f).keys())
        
        # Load FLL seasons
        season_file = self.config_dir / "missions" / "fll_seasons.yaml"
        if season_file.exists():
            with open(season_file, 'r') as f:
                configs["seasons"] = list(yaml.safe_load(f).keys())
        
        return configs
    
    def get_fll_season_info(self, season: str) -> Dict[str, Any]:
        """Get information about a specific FLL season."""
        season_file = self.config_dir / "missions" / "fll_seasons.yaml"
        
        with open(season_file, 'r') as f:
            seasons = yaml.safe_load(f)
        
        if season not in seasons:
            raise ValueError(f"FLL season '{season}' not found")
        
        return seasons[season]
    
    def create_custom_robot(self, name: str, base_config: str, modifications: Dict[str, Any]):
        """Create a custom robot configuration based on an existing one."""
        base = self.load_robot_config(base_config)
        
        # Apply modifications
        for key, value in modifications.items():
            if hasattr(base, key):
                setattr(base, key, value)
        
        # Save as new configuration
        custom_file = self.config_dir / "robots" / f"{name}.yaml"
        config_data = {
            name: {
                "name": modifications.get("name", f"Custom {name}"),
                "description": modifications.get("description", f"Custom robot based on {base_config}"),
                **asdict(base)
            }
        }
        
        with open(custom_file, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
        
        return base
