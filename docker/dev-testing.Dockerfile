# Testing and QA Container
# Comprehensive testing environment for all project types
FROM ubuntu:22.04

# Avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

WORKDIR /testing

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
    xvfb \
    libgtk-3-dev \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libnss3 \
    libcups2 \
    libxss1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for JavaScript testing
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Python for Python testing
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Install Java for Java testing
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk maven gradle && \
    rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Install Go for Go testing
RUN wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz && \
    rm go1.21.5.linux-amd64.tar.gz
ENV PATH=$PATH:/usr/local/go/bin
ENV GOPATH=/testing/go
ENV GOBIN=$GOPATH/bin

# Install Rust for Rust testing
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install Python testing frameworks and tools
RUN pip3 install --no-cache-dir \
    # Core testing frameworks
    pytest \
    pytest-cov \
    pytest-xdist \
    pytest-mock \
    pytest-html \
    pytest-json-report \
    pytest-benchmark \
    pytest-timeout \
    pytest-asyncio \
    # Web testing
    selenium \
    playwright \
    requests \
    beautifulsoup4 \
    # API testing
    httpx \
    aiohttp \
    fastapi \
    flask \
    # Data testing
    pytest-datadir \
    pytest-csv \
    # Performance testing
    locust \
    py-spy \
    # BDD testing
    behave \
    pytest-bdd \
    # Property-based testing
    hypothesis \
    # Mocking
    responses \
    factory-boy \
    faker \
    # Database testing
    pytest-postgresql \
    pytest-mysql \
    pytest-redis \
    pytest-mongodb \
    # Test runners
    tox \
    nox \
    # Code coverage
    coverage \
    codecov \
    # Load testing
    artillery \
    # Visual testing
    pytest-playwright \
    # Contract testing
    pact-python

# Install JavaScript/TypeScript testing tools
RUN npm install -g \
    # Core testing frameworks
    jest \
    mocha \
    chai \
    jasmine \
    ava \
    tape \
    # End-to-end testing
    cypress \
    playwright \
    puppeteer \
    nightwatch \
    testcafe \
    # Web drivers
    chromedriver \
    geckodriver \
    # API testing
    newman \
    supertest \
    # Performance testing
    artillery \
    autocannon \
    clinic \
    0x \
    # BDD testing
    cucumber \
    # Visual testing
    storybook \
    chromatic \
    # Mock servers
    json-server \
    nock \
    # Test runners
    karma \
    # Code coverage
    nyc \
    c8 \
    istanbuljs \
    # Load testing
    k6 \
    # Contract testing
    @pact-foundation/pact \
    # Accessibility testing
    axe-core \
    pa11y \
    # Security testing
    retire \
    nsp

# Install Go testing tools
RUN go install github.com/onsi/ginkgo/v2/ginkgo@latest && \
    go install github.com/onsi/gomega/...@latest && \
    go install gotest.tools/gotestsum@latest && \
    go install github.com/rakyll/hey@latest && \
    go install github.com/dave/courtney@latest && \
    go install github.com/axw/gocov/gocov@latest && \
    go install github.com/AlekSi/gocov-xml@latest

# Install Rust testing tools
RUN cargo install cargo-tarpaulin && \
    cargo install cargo-nextest && \
    cargo install cargo-mutants && \
    cargo install cargo-fuzz && \
    rustup component add llvm-tools-preview

# Install Java testing tools
RUN mvn dependency:get -Dartifact=org.junit.jupiter:junit-jupiter:5.10.0 && \
    mvn dependency:get -Dartifact=org.testng:testng:7.8.0 && \
    mvn dependency:get -Dartifact=org.mockito:mockito-core:5.5.0 && \
    mvn dependency:get -Dartifact=org.springframework:spring-test:6.0.11 && \
    mvn dependency:get -Dartifact=io.rest-assured:rest-assured:5.3.1

# Install browser binaries for testing
RUN npx playwright install-deps && \
    npx playwright install

# Install Chrome for Selenium testing
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Install Firefox for testing
RUN apt-get update && \
    apt-get install -y firefox && \
    rm -rf /var/lib/apt/lists/*

# Install database clients for integration testing
RUN apt-get update && \
    apt-get install -y \
    postgresql-client \
    mysql-client \
    redis-tools \
    mongodb-clients \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI for container testing
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce-cli && \
    rm -rf /var/lib/apt/lists/*

# Install additional testing utilities
RUN npm install -g \
    # Screenshot testing
    resemblejs \
    pixelmatch \
    # Performance monitoring
    clinic \
    # API documentation testing
    dredd \
    # Load testing
    loadtest \
    # Security testing
    zap-baseline \
    # Accessibility testing
    lighthouse \
    # Cross-browser testing
    browserslist

# Install testing configuration generators
RUN pip3 install --no-cache-dir \
    cookiecutter \
    jinja2 \
    pyyaml \
    && npm install -g \
    yeoman-generator \
    generator-jest

# Setup testing user
RUN useradd -m -s /bin/bash -G sudo tester && \
    echo "tester:tester" | chpasswd && \
    mkdir -p /workspace && \
    mkdir -p /testing/reports && \
    mkdir -p /testing/screenshots && \
    mkdir -p /testing/videos && \
    mkdir -p /testing/coverage && \
    chown -R tester:tester /workspace /testing

# Create testing configuration directories
RUN mkdir -p /testing/config && \
    mkdir -p /testing/scripts && \
    mkdir -p /testing/fixtures && \
    mkdir -p /testing/mocks && \
    chown -R tester:tester /testing

# Copy testing configurations and scripts
COPY docker/config/testing/ /testing/config/
COPY docker/scripts/testing/ /testing/scripts/

# Make scripts executable
RUN chmod +x /testing/scripts/*.sh

# Setup environment variables
ENV PATH="/testing/scripts:$PATH"
ENV TESTING_HOME="/testing"
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/google-chrome
ENV FIREFOX_BIN=/usr/bin/firefox

# Setup Xvfb for headless browser testing
ENV DISPLAY=:99
RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &\nexec "$@"' > /testing/scripts/start-xvfb.sh && \
    chmod +x /testing/scripts/start-xvfb.sh

# Switch to testing user
USER tester
WORKDIR /workspace

# Setup user environment
RUN echo 'export PATH="/testing/scripts:$PATH"' >> ~/.bashrc && \
    echo 'export TESTING_HOME="/testing"' >> ~/.bashrc && \
    echo 'export DISPLAY=:99' >> ~/.bashrc && \
    echo 'alias test-unit="/testing/scripts/run-unit-tests.sh"' >> ~/.bashrc && \
    echo 'alias test-integration="/testing/scripts/run-integration-tests.sh"' >> ~/.bashrc && \
    echo 'alias test-e2e="/testing/scripts/run-e2e-tests.sh"' >> ~/.bashrc && \
    echo 'alias test-performance="/testing/scripts/run-performance-tests.sh"' >> ~/.bashrc && \
    echo 'alias test-security="/testing/scripts/run-security-tests.sh"' >> ~/.bashrc && \
    echo 'alias test-all="/testing/scripts/run-all-tests.sh"' >> ~/.bashrc

# Create default test configurations
RUN mkdir -p ~/.config/playwright && \
    echo '{ "use": { "headless": true, "viewport": { "width": 1280, "height": 720 } } }' > ~/.config/playwright/config.json && \
    mkdir -p ~/.config/cypress && \
    echo '{ "baseUrl": "http://localhost:3000", "video": false, "screenshotOnRunFailure": false }' > ~/.config/cypress/config.json

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ps aux | grep -v grep | grep -q Xvfb || exit 1

# Start Xvfb and bash
CMD ["/testing/scripts/start-xvfb.sh", "bash"]
