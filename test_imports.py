#!/usr/bin/env python3

import os
import sys

# Set up environment
project_root = "/home/kevin/Projects/FLL-SIM"
sys.path.insert(0, os.path.join(project_root, "src"))

# Test basic functionality
print("Testing basic imports...")

try:
    print("Testing core simulator...")
    from fll_sim.core.simulator import Simulator
    print("✓ Core simulator import successful")

    print("Testing GUI main module...")
    from fll_sim.gui.main_gui import FLLSimMainWindow
    print("✓ GUI main window import successful")

    print("All critical imports working!")

except ImportError as e:
    print(f"Import error: {e}")
    print("Checking for missing dependencies...")

    # Check what's missing
    missing = []
    try:
        import pygame
    except ImportError:
        missing.append("pygame")

    try:
        import PyQt6
    except ImportError:
        missing.append("PyQt6")

    try:
        import pymunk
    except ImportError:
        missing.append("pymunk")

    if missing:
        print(f"Missing dependencies: {missing}")
    else:
        print("All dependencies available, likely a path issue")

except Exception as e:
    print(f"Other error: {e}")
    import traceback
    traceback.print_exc()
