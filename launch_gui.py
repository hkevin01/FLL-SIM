#!/usr/bin/env python3
"""
Test script to launch FLL-Sim GUI with all fixes applied.
This runs in the virtual environment context.
"""

import os
import sys
from pathlib import Path

# Ensure we're using the right project root
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))
os.environ['PYTHONPATH'] = str(project_root / "src")

def test_gui_launch():
    """Test the GUI launch with all our fixes."""
    print("FLL-Sim GUI Test Launch")
    print("=" * 40)

    # Test imports first
    print("Testing critical imports...")

    try:
        print("  ✓ Testing pygame...")
        import pygame

        print("  ✓ Testing PyQt6...")
        from PyQt6.QtWidgets import QApplication

        print("  ✓ Testing pymunk...")
        import pymunk

        print("  ✓ Testing simulator...")
        from fll_sim.core.simulator import Simulator

        print("  ✓ Testing GUI main window...")
        from fll_sim.gui.main_gui import FLLSimMainWindow, main

        print("All imports successful!")
        print()

        # Now try to launch the GUI
        print("Launching FLL-Sim GUI...")
        main()

    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except Exception as e:
        print(f"Launch error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = test_gui_launch()
    if success:
        print("GUI test completed successfully!")
    else:
        print("GUI test failed!")
        sys.exit(1)
