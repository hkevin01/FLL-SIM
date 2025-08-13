#!/bin/bash

# Test if we can run the GUI with proper virtual environment setup
set -e

PROJECT_DIR="/home/kevin/Projects/FLL-SIM"

echo "Setting up virtual environment..."
cd "$PROJECT_DIR"

# Activate virtual environment
source "$PROJECT_DIR/fll-sim-env/bin/activate"

# Install dependencies using the venv pip directly
echo "Installing dependencies..."
"$PROJECT_DIR/fll-sim-env/bin/pip" install pygame pymunk numpy matplotlib pillow pyyaml PyQt6

# Set Python path
export PYTHONPATH="$PROJECT_DIR/src:$PYTHONPATH"

# Test import
echo "Testing imports..."
python -c "
import sys
sys.path.insert(0, 'src')
import pygame
import PyQt6
from fll_sim.core.simulator import Simulator
print('All imports successful!')
"

echo "Environment setup complete!"
