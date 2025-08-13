##############################
# FLL-Sim Production Dockerfile
# Multi-stage build supporting:
#  * Deterministic, cached dependency layer
#  * Headless mode via Xvfb (FLL_SIM_HEADLESS=1)
#  * GUI passthrough via mounted X11 / Wayland socket
#  * Non-root runtime user
##############################

ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim AS base

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLL_SIM_HEADLESS=0 \
    FLL_SIM_DETERMINISTIC=0

# Use an isolated virtual environment inside the container
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

WORKDIR /app

# System deps for PyQt6 + fonts + Xvfb + misc build tools
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    build-essential \
    wget curl git \
    xvfb xauth x11-apps \
    libxcb-xinerama0 libxkbcommon-x11-0 libgl1 libglib2.0-0 libx11-xcb1 \
    libxkbcommon0 libdbus-1-3 libxrender1 libxi6 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxrandr2 \
    libatk1.0-0 libatk-bridge2.0-0 libpango-1.0-0 libfontconfig1 libfreetype6 libx11-6 \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Copy lock / requirements first for caching
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install package in editable mode (source copied later for dev caching)
COPY pyproject.toml setup.py README.md ./
RUN pip install -e . || true

# ---- Runtime stage ----
FROM base AS runtime

# Add non-root user
ARG APP_USER=fllsim
RUN useradd -m -u 1000 -s /bin/bash ${APP_USER}
USER ${APP_USER}

WORKDIR /app

# Copy source (after dependency layers cached)
COPY --chown=${APP_USER}:${APP_USER} . .

# Default to headless tests (override with command / env)
ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["fll-sim", "--headless", "--exit-after", "5"]

# Provide a healthcheck (basic python import)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s CMD python -c "import fll_sim" || exit 1

##############################
# Optional test stage (can be invoked separately)
FROM runtime AS test
CMD ["python", "-m", "unittest", "-v", "tests"]
