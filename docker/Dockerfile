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
    libegl1 libgles2 libopengl0 libglx0 libgl1-mesa-dev libegl1-mesa-dev \
    libgles-dev libglvnd-dev libglx-dev libopengl-dev \
    x11proto-dev libx11-dev libxcb1-dev \
    libegl1-mesa-dev libgl1-mesa-dev \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for headless OpenGL/EGL
ENV DISPLAY=:99 \
    QT_GRAPHICSSYSTEM=software \
    QT_QPA_PLATFORM=offscreen \
    LIBGL_ALWAYS_INDIRECT=1 \
    MESA_GL_VERSION_OVERRIDE=3.3

# Copy lock / requirements first for caching
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install package in editable mode - copy source files first
COPY pyproject.toml setup.py README.md ./
COPY src/ ./src/
RUN pip install -e . || true

# ---- Runtime stage ----
FROM base AS runtime

# Add non-root user
ARG APP_USER=fllsim
RUN useradd -m -u 1000 -s /bin/bash ${APP_USER}

WORKDIR /app

# Copy source (after dependency layers cached)
COPY --chown=${APP_USER}:${APP_USER} . .

# Copy entrypoint with correct permissions for non-root user
COPY --chown=${APP_USER}:${APP_USER} --chmod=755 docker/entrypoint.sh /app/docker/entrypoint.sh

USER ${APP_USER}

# Default to headless tests (override with command / env)
ENTRYPOINT ["/bin/bash", "/app/docker/entrypoint.sh"]
CMD ["python", "-m", "fll_sim.cli", "--headless", "--exit-after", "5"]

# Provide a healthcheck (basic python import)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s CMD python -c "import fll_sim" || exit 1

##############################
# Optional test stage (can be invoked separately)
FROM runtime AS test
CMD ["python", "-m", "unittest", "-v", "tests"]
