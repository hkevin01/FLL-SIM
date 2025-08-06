# Multi-Purpose Backend Development Container
# Supports Python, Node.js, Go, Java, and more with development tools
FROM ubuntu:22.04

# Avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Set up working directory
WORKDIR /workspace

# Install system dependencies and development tools
RUN apt-get update && apt-get install -y \
    # Basic tools
    curl \
    wget \
    git \
    vim \
    nano \
    unzip \
    zip \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    # Network tools
    net-tools \
    telnet \
    netcat \
    dnsutils \
    # Development utilities
    jq \
    tree \
    htop \
    tmux \
    zsh \
    fish \
    # Database clients
    postgresql-client \
    mysql-client \
    redis-tools \
    mongodb-clients \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install Python 3.11 and 3.12 with development tools
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    # Python development tools
    python3-pytest \
    python3-black \
    python3-flake8 \
    python3-mypy \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry for Python dependency management
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Install Node.js LTS (20.x) and package managers
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    # Install package managers
    npm install -g npm@latest && \
    npm install -g yarn@latest && \
    npm install -g pnpm@latest && \
    # Install development tools
    npm install -g \
    typescript \
    ts-node \
    @typescript-eslint/cli \
    prettier \
    eslint \
    jest \
    nodemon \
    pm2 \
    @angular/cli \
    @vue/cli \
    create-react-app \
    vite \
    webpack-cli

# Install Go
RUN wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz && \
    rm go1.21.5.linux-amd64.tar.gz
ENV PATH=$PATH:/usr/local/go/bin
ENV GOPATH=/workspace/go
ENV GOBIN=$GOPATH/bin

# Install Go development tools
RUN go install golang.org/x/tools/gopls@latest && \
    go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest && \
    go install github.com/go-delve/delve/cmd/dlv@latest

# Install Java (OpenJDK 17) and Maven
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk maven gradle && \
    rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN rustup component add clippy rustfmt

# Install Docker CLI for container management
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce-cli && \
    rm -rf /var/lib/apt/lists/*

# Install kubectl for Kubernetes
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install development databases (lightweight versions)
RUN apt-get update && \
    apt-get install -y \
    sqlite3 \
    redis-server \
    && rm -rf /var/lib/apt/lists/*

# Install Oh My Zsh for better terminal experience
RUN sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended && \
    chsh -s $(which zsh)

# Set up development user (non-root)
RUN useradd -m -s /bin/zsh -G sudo developer && \
    echo "developer:developer" | chpasswd && \
    usermod -aG docker developer 2>/dev/null || true

# Create workspace directories
RUN mkdir -p /workspace/projects && \
    mkdir -p /workspace/tools && \
    mkdir -p /workspace/data && \
    chown -R developer:developer /workspace

# Install code quality tools
RUN pip3 install --no-cache-dir \
    black \
    flake8 \
    mypy \
    pytest \
    pytest-cov \
    bandit \
    safety \
    pre-commit \
    autopep8 \
    isort

# Install performance and monitoring tools
RUN npm install -g \
    clinic \
    0x \
    autocannon \
    lighthouse \
    webpack-bundle-analyzer

# Health check script
COPY docker/scripts/backend-healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh

# Set up environment
ENV NODE_ENV=development
ENV PYTHONPATH=/workspace
ENV PATH="/workspace/node_modules/.bin:$PATH"

# Switch to development user
USER developer
WORKDIR /workspace

# Install user-level tools
RUN pip3 install --user \
    jupyterlab \
    ipython \
    requests \
    fastapi \
    uvicorn \
    django \
    flask

# Setup shell configuration
RUN echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && \
    echo 'export EDITOR=vim' >> ~/.zshrc && \
    echo 'alias ll="ls -la"' >> ~/.zshrc && \
    echo 'alias gs="git status"' >> ~/.zshrc && \
    echo 'alias gp="git pull"' >> ~/.zshrc

# Expose common development ports
EXPOSE 3000 5000 8000 8080 9000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

# Default command
CMD ["zsh"]
