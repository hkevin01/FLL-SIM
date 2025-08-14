#!/usr/bin/env bash
set -euo pipefail

# Install pygame into the system Python environment.
# Tries apt (Debian/Ubuntu) first, then dnf/yum, then falls back to pip with --break-system-packages.

if command -v apt-get >/dev/null 2>&1; then
  echo "[system] Detected apt-get; installing python3-pygame via APT (requires sudo)."
  sudo apt-get update
  sudo apt-get install -y python3-pygame
  echo "[system] Installed python3-pygame via APT."
  exit 0
fi

if command -v dnf >/dev/null 2>&1; then
  echo "[system] Detected dnf; installing python3-pygame via DNF (requires sudo)."
  sudo dnf install -y python3-pygame || sudo dnf install -y python-pygame
  echo "[system] Installed python3-pygame via DNF."
  exit 0
fi

if command -v yum >/dev/null 2>&1; then
  echo "[system] Detected yum; installing python3-pygame via YUM (requires sudo)."
  sudo yum install -y python3-pygame || sudo yum install -y pygame
  echo "[system] Installed python3-pygame via YUM."
  exit 0
fi

# Fallback: pip install (PEP 668 environments may require --break-system-packages)
if command -v python3 >/dev/null 2>&1; then
  echo "[system] Falling back to pip; attempting system install with --break-system-packages."
  python3 -m pip install --upgrade pip || true
  python3 -m pip install pygame --break-system-packages
  echo "[system] Installed pygame via pip."
  exit 0
fi

echo "[system] Could not detect package manager or python3. Please install pygame manually."
exit 1
