"""
Configuration management module for FLL-Sim.

This module provides configuration loading, saving, and management
for different simulation scenarios, robot setups, and FLL seasons.
"""

from .config_manager import ConfigManager, SimulationProfile

__all__ = ["ConfigManager", "SimulationProfile"]
