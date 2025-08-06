# VS Code Development Container
# Complete development environment with all tools and languages
FROM ubuntu:22.04

# Avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    build-essential \
    ca-certificates \
    curl \
    git \
    gnupg \
    htop \
    jq \
    lsb-release \
    software-properties-common \
    sudo \
    tree \
    unzip \
    vim \
    wget \
    zip \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Python
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-dev \
    python3-pip \
    python3-tk \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install Java
RUN apt-get update && \
    apt-get install -y gradle maven openjdk-17-jdk && \
    rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Install Go
RUN wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz && \
    rm go1.21.5.linux-amd64.tar.gz
ENV PATH=$PATH:/usr/local/go/bin

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Docker CLI
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce-cli && \
    rm -rf /var/lib/apt/lists/*

# Install database clients
RUN apt-get update && \
    apt-get install -y \
    mongodb-clients \
    mysql-client \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install --no-cache-dir \
    autopep8 \
    bandit \
    black \
    coverage \
    flake8 \
    isort \
    mypy \
    pylint \
    pytest \
    pytest-cov \
    pytest-mock

# Install Node.js packages
RUN npm install -g \
    @typescript-eslint/cli \
    eslint \
    jest \
    prettier \
    typescript

# Install Go tools
RUN go install golang.org/x/tools/gopls@latest && \
    go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# Install Rust tools
RUN rustup component add clippy rustfmt

# Create development user
RUN useradd -m -s /bin/bash -G sudo,docker developer && \
    echo "developer:developer" | chpasswd && \
    echo "developer ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Setup user directories
RUN mkdir -p /home/developer/.vscode-server && \
    mkdir -p /home/developer/.config && \
    chown -R developer:developer /home/developer

# Install Oh My Zsh for developer user
USER developer
RUN sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
USER root

# Setup environment
ENV GOPATH=/workspace/go
ENV GOBIN=$GOPATH/bin
ENV CARGO_HOME=/workspace/.cargo
ENV PATH="$PATH:$GOBIN:/home/developer/.cargo/bin"

# Copy development scripts
COPY docker/scripts/devcontainer/ /usr/local/bin/
RUN chmod +x /usr/local/bin/*.sh

# Switch back to development user
USER developer
WORKDIR /workspace

# Setup user environment
RUN echo 'export PATH="$PATH:/usr/local/bin"' >> ~/.bashrc && \
    echo 'export GOPATH=/workspace/go' >> ~/.bashrc && \
    echo 'export GOBIN=$GOPATH/bin' >> ~/.bashrc && \
    echo 'export CARGO_HOME=/workspace/.cargo' >> ~/.bashrc && \
    echo 'export PATH="$PATH:$GOBIN:$CARGO_HOME/bin"' >> ~/.bashrc

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command
CMD ["bash"]
