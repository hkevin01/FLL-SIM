# Development Tools and CI/CD Container
# Comprehensive tooling environment for code quality, security, and automation
FROM ubuntu:22.04

# Avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

WORKDIR /tools

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    vim \
    unzip \
    zip \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    jq \
    tree \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for JavaScript tools
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Python for Python tools
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install Go for Go tools
RUN wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz && \
    rm go1.21.5.linux-amd64.tar.gz
ENV PATH=$PATH:/usr/local/go/bin
ENV GOPATH=/tools/go
ENV GOBIN=$GOPATH/bin

# Install Rust for Rust tools
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Java for Java tools
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk maven && \
    rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Install Docker CLI
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce-cli && \
    rm -rf /var/lib/apt/lists/*

# Install kubectl and helm
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl && \
    curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Terraform
RUN wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | tee /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list && \
    apt-get update && \
    apt-get install -y terraform && \
    rm -rf /var/lib/apt/lists/*

# Install Python code quality tools
RUN pip3 install --no-cache-dir \
    # Formatters
    black \
    autopep8 \
    isort \
    # Linters
    flake8 \
    pylint \
    mypy \
    bandit \
    # Testing
    pytest \
    pytest-cov \
    pytest-xdist \
    pytest-mock \
    # Security
    safety \
    semgrep \
    # Documentation
    sphinx \
    mkdocs \
    mkdocs-material \
    # Dependency management
    pip-tools \
    pipenv \
    poetry \
    # Git hooks
    pre-commit \
    # Code complexity
    radon \
    xenon \
    # Import sorting
    isort \
    # Type checking
    mypy \
    pyre-check

# Install JavaScript/TypeScript tools
RUN npm install -g \
    # Formatters
    prettier \
    # Linters
    eslint \
    @typescript-eslint/cli \
    tslint \
    stylelint \
    # Testing
    jest \
    mocha \
    cypress \
    playwright \
    # Security
    npm-audit \
    snyk \
    # Bundle analysis
    webpack-bundle-analyzer \
    # Documentation
    jsdoc \
    typedoc \
    # Build tools
    webpack \
    rollup \
    vite \
    # Package management
    npm-check-updates \
    # Code complexity
    complexity-report \
    # License checking
    license-checker

# Install Go tools
RUN go install golang.org/x/tools/gopls@latest && \
    go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest && \
    go install github.com/securecodewarrior/gosec/v2/cmd/gosec@latest && \
    go install golang.org/x/tools/cmd/goimports@latest && \
    go install github.com/fzipp/gocyclo/cmd/gocyclo@latest && \
    go install honnef.co/go/tools/cmd/staticcheck@latest

# Install Rust tools
RUN rustup component add clippy rustfmt && \
    cargo install cargo-audit && \
    cargo install cargo-outdated && \
    cargo install cargo-tree && \
    cargo install cargo-bloat

# Install additional security tools
RUN npm install -g \
    retire \
    nsp \
    && pip3 install --no-cache-dir \
    detect-secrets \
    truffleHog3

# Install container security tools
RUN wget https://github.com/aquasecurity/trivy/releases/latest/download/trivy_$(dpkg --print-architecture).deb && \
    dpkg -i trivy_$(dpkg --print-architecture).deb && \
    rm trivy_$(dpkg --print-architecture).deb

# Install performance testing tools
RUN npm install -g \
    artillery \
    autocannon \
    clinic \
    0x \
    && pip3 install --no-cache-dir \
    locust

# Install API documentation tools
RUN npm install -g \
    @apidevtools/swagger-cli \
    redoc-cli \
    && pip3 install --no-cache-dir \
    apispec \
    flask-apispec \
    fastapi

# Install database migration tools
RUN npm install -g \
    db-migrate \
    sequelize-cli \
    prisma \
    && pip3 install --no-cache-dir \
    alembic \
    django

# Install Git tools and hooks
RUN pip3 install --no-cache-dir \
    gitpython \
    pre-commit \
    commitizen \
    && npm install -g \
    husky \
    lint-staged \
    commitlint \
    conventional-changelog-cli

# Install monitoring and observability tools
RUN wget https://github.com/prometheus/node_exporter/releases/latest/download/node_exporter-1.6.1.linux-amd64.tar.gz && \
    tar xvfz node_exporter-1.6.1.linux-amd64.tar.gz && \
    cp node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin && \
    rm -rf node_exporter-1.6.1.linux-amd64*

# Install license and dependency checkers
RUN npm install -g \
    license-checker \
    npm-license-crawler \
    && pip3 install --no-cache-dir \
    pip-licenses \
    safety

# Install code coverage tools
RUN npm install -g \
    nyc \
    c8 \
    && pip3 install --no-cache-dir \
    coverage \
    codecov

# Setup development user
RUN useradd -m -s /bin/bash -G sudo devtools && \
    echo "devtools:devtools" | chpasswd && \
    mkdir -p /workspace && \
    chown -R devtools:devtools /workspace /tools

# Create tool configuration directories
RUN mkdir -p /tools/config && \
    mkdir -p /tools/scripts && \
    mkdir -p /tools/reports && \
    chown -R devtools:devtools /tools

# Copy configuration files
COPY docker/config/tools/ /tools/config/
COPY docker/scripts/tools/ /tools/scripts/

# Make scripts executable
RUN chmod +x /tools/scripts/*.sh

# Setup environment
ENV PATH="/tools/scripts:$PATH"
ENV TOOLS_HOME="/tools"

# Switch to development user
USER devtools
WORKDIR /workspace

# Setup user environment
RUN echo 'export PATH="/tools/scripts:$PATH"' >> ~/.bashrc && \
    echo 'export TOOLS_HOME="/tools"' >> ~/.bashrc && \
    echo 'alias lint-all="/tools/scripts/lint-all.sh"' >> ~/.bashrc && \
    echo 'alias test-all="/tools/scripts/test-all.sh"' >> ~/.bashrc && \
    echo 'alias security-scan="/tools/scripts/security-scan.sh"' >> ~/.bashrc

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command
CMD ["bash"]
