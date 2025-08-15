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

echo -e "${BLUE}FLL-Sim GUI Launcher (Enhanced)${NC}"
echo "=================================="

# Optional overrides
SEASON=${SEASON:-latest}
MAT_URL=${MAT_URL:-}
MAT_PDF_URL=${MAT_PDF_URL:-}
MAT_PDF_PAGE=${MAT_PDF_PAGE:-0}
MAT_PDF_DPI=${MAT_PDF_DPI:-300}
MAT_PDF_PAGE_LABEL=${MAT_PDF_PAGE_LABEL:-}
MAT_PDF_TOC_TITLE=${MAT_PDF_TOC_TITLE:-}

## Prefer Docker unless FORCE_LOCAL is set; if image missing, fall back to local
if [ -z "$FORCE_LOCAL" ] && command -v docker >/dev/null 2>&1; then
        if docker image inspect fll-sim:latest >/dev/null 2>&1; then
                echo -e "${BLUE}Docker detected. Starting Enhanced GUI in a container...${NC}"
                # Allow local X11 connections for containers (best-effort, ignore failures)
                if command -v xhost >/dev/null 2>&1; then
                        xhost +local:root >/dev/null 2>&1 || true
                        xhost +local:$(id -un) >/dev/null 2>&1 || true
                fi
                # Build enhanced launcher command
                ENH_ARGS=("launch_gui_enhanced.py" "--season" "$SEASON")
                if [ -n "$MAT_PDF_URL" ]; then
                    ENH_ARGS+=("--mat-pdf-url" "$MAT_PDF_URL" "--mat-pdf-page" "$MAT_PDF_PAGE" "--mat-pdf-dpi" "$MAT_PDF_DPI")
                    [ -n "$MAT_PDF_PAGE_LABEL" ] && ENH_ARGS+=("--mat-pdf-page-label" "$MAT_PDF_PAGE_LABEL")
                    [ -n "$MAT_PDF_TOC_TITLE" ] && ENH_ARGS+=("--mat-pdf-toc-title" "$MAT_PDF_TOC_TITLE")
                elif [ -n "$MAT_URL" ]; then
                    ENH_ARGS+=("--mat-url" "$MAT_URL")
                fi
                # Pass through any extra args
                ENH_ARGS+=("$@")
                docker run --rm \
                    -e DISPLAY=$DISPLAY \
                    -v /tmp/.X11-unix:/tmp/.X11-unix \
                    -v "$PROJECT_DIR":"/app" \
                    -w /app \
                    fll-sim:latest \
                    bash -lc \
                        ". venv/bin/activate 2>/dev/null || true; export PYTHONPATH=/app/src:$PYTHONPATH; python -u ${ENH_ARGS[@]}"
                echo -e "${GREEN}FLL-Sim GUI session ended.${NC}"
                exit 0
        else
                echo -e "${YELLOW}Docker image 'fll-sim:latest' not found. Falling back to local mode.${NC}"
        fi
fi

## Local fallback
    echo -e "${YELLOW}Docker not available. Using local virtual environment...${NC}"
    # Local venv fallback
    if [ ! -d "$PROJECT_DIR/fll-sim-env" ]; then
        echo -e "${YELLOW}Virtual environment not found. Creating one...${NC}"
        python3 -m venv "$PROJECT_DIR/fll-sim-env"
        echo -e "${GREEN}Virtual environment created.${NC}"
    fi
    echo -e "${BLUE}Activating virtual environment...${NC}"
    # shellcheck source=/dev/null
    source "$PROJECT_DIR/fll-sim-env/bin/activate"
    echo -e "${BLUE}Checking dependencies...${NC}"
    if ! python -c "import pygame, pymunk, PyQt6" 2>/dev/null; then
        echo -e "${YELLOW}Installing missing dependencies...${NC}"
        pip install -r "$PROJECT_DIR/requirements.txt"
        echo -e "${GREEN}Dependencies installed.${NC}"
    fi
        export PYTHONPATH="$PROJECT_DIR/src:$PYTHONPATH"
        echo -e "${GREEN}Launching FLL-Sim Enhanced GUI...${NC}"
        echo -e "${BLUE}You can close this terminal window after the GUI opens.${NC}"
        # Build enhanced launcher arguments
        ENH_ARGS=("--season" "$SEASON")
        if [ -n "$MAT_PDF_URL" ]; then
            ENH_ARGS+=("--mat-pdf-url" "$MAT_PDF_URL" "--mat-pdf-page" "$MAT_PDF_PAGE" "--mat-pdf-dpi" "$MAT_PDF_DPI")
            [ -n "$MAT_PDF_PAGE_LABEL" ] && ENH_ARGS+=("--mat-pdf-page-label" "$MAT_PDF_PAGE_LABEL")
            [ -n "$MAT_PDF_TOC_TITLE" ] && ENH_ARGS+=("--mat-pdf-toc-title" "$MAT_PDF_TOC_TITLE")
        elif [ -n "$MAT_URL" ]; then
            ENH_ARGS+=("--mat-url" "$MAT_URL")
        fi
        # Pass through any extra args (e.g., --exit-after)
        ENH_ARGS+=("$@")
    cd "$PROJECT_DIR" && python -u launch_gui_enhanced.py "${ENH_ARGS[@]}"

echo -e "${GREEN}FLL-Sim GUI session ended.${NC}"
