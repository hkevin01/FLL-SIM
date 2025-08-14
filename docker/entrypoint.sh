#!/usr/bin/env bash
set -euo pipefail

# Detect headless mode
if [[ "${FLL_SIM_HEADLESS:-0}" == "1" ]]; then
  export QT_QPA_PLATFORM=${QT_QPA_PLATFORM:-offscreen}
  echo "[entrypoint] Headless mode enabled (QT_QPA_PLATFORM=$QT_QPA_PLATFORM)"
  exec "$@"
else
  # If DISPLAY unset we fallback to Xvfb
  if [[ -z "${DISPLAY:-}" ]]; then
    export DISPLAY=":99"
    echo "[entrypoint] No DISPLAY detected – starting Xvfb on :99"
    Xvfb :99 -screen 0 1920x1080x24 &
    sleep 2
  else
    echo "[entrypoint] Using host DISPLAY=$DISPLAY"
  fi
  # Ensure we are not stuck on offscreen platform in non-headless mode
  if [[ "${QT_QPA_PLATFORM:-}" == "offscreen" || -z "${QT_QPA_PLATFORM:-}" ]]; then
    export QT_QPA_PLATFORM=xcb
    echo "[entrypoint] Forcing QT_QPA_PLATFORM=xcb for GUI"
  fi
  exec "$@"
fi
