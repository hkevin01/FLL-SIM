#!/bin/bash

cd /home/kevin/Projects/FLL-SIM

echo "Activating virtual environment..."
source fll-sim-env/bin/activate

echo "Setting Python path..."
export PYTHONPATH="/home/kevin/Projects/FLL-SIM/src:$PYTHONPATH"

echo "Testing basic import..."
python -c "
import sys
sys.path.insert(0, '/home/kevin/Projects/FLL-SIM/src')
from fll_sim.core.simulator import Simulator
print('✓ Simulator import works')
"

echo "Running GUI..."
python -c "
import sys
sys.path.insert(0, '/home/kevin/Projects/FLL-SIM/src')
from fll_sim.gui.main_gui import main
main()
"
