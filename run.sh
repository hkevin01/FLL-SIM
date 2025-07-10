#!/bin/bash

# FLL-Sim GUI Launcher Script
# This script provides a convenient way to launch the FLL-Sim GUI interface

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

echo -e "${BLUE}FLL-Sim GUI Launcher${NC}"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "$PROJECT_DIR/fll-sim-env" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"
    python3 -m venv "$PROJECT_DIR/fll-sim-env"
    echo -e "${GREEN}Virtual environment created.${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source "$PROJECT_DIR/fll-sim-env/bin/activate"

# Check if dependencies are installed
echo -e "${BLUE}Checking dependencies...${NC}"
if ! python -c "import pygame, pymunk, PyQt6" 2>/dev/null; then
    echo -e "${YELLOW}Installing missing dependencies...${NC}"
    pip install pygame pymunk numpy matplotlib pillow pyyaml PyQt6
    echo -e "${GREEN}Dependencies installed.${NC}"
fi

# Add project src to Python path
export PYTHONPATH="$PROJECT_DIR/src:$PYTHONPATH"

# Check for GUI module
GUI_MODULE="$PROJECT_DIR/src/fll_sim/gui/main_gui.py"
if [ ! -f "$GUI_MODULE" ]; then
    echo -e "${RED}GUI module not found at: $GUI_MODULE${NC}"
    echo -e "${YELLOW}Running setup to create GUI components...${NC}"
    python "$PROJECT_DIR/setup.py" --no-examples
fi

# Launch GUI
echo -e "${GREEN}Launching FLL-Sim GUI...${NC}"
echo -e "${BLUE}You can close this terminal window after the GUI opens.${NC}"

# Try to launch the GUI, fallback to command line if it fails
if [ -f "$GUI_MODULE" ]; then
    cd "$PROJECT_DIR" && python -c "
import sys
sys.path.insert(0, 'src')
from fll_sim.gui.main_gui import main
main()
" "$@"
else
    echo -e "${YELLOW}GUI not available, launching command line interface...${NC}"
    python "$PROJECT_DIR/main.py" "$@"
fi

echo -e "${GREEN}FLL-Sim GUI session ended.${NC}"
