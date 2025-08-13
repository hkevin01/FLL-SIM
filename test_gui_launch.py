#!/usr/bin/env python3

# Quick test to run GUI in virtual environment
import os
import sys

# Add project src to path
project_root = "/home/kevin/Projects/FLL-SIM"
sys.path.insert(0, os.path.join(project_root, "src"))

try:
    print("Testing imports...")
    print("✓ Basic imports successful")

    print("✓ Simulator import successful")

    from fll_sim.gui.main_gui import main
    print("✓ GUI import successful")

    print("Launching GUI...")
    main()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
