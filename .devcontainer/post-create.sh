#!/bin/bash
# Post-create script for development container setup
set -e

echo "🚀 Setting up development environment..."

# Create workspace directories
mkdir -p /workspace/{src,tests,docs,configs,scripts,data,logs}
mkdir -p /workspace/go/{src,bin,pkg}
mkdir -p /workspace/.cargo
mkdir -p /workspace/node_modules
mkdir -p /workspace/.vscode

# Set up Git configuration if not already configured
if [ ! -f /home/developer/.gitconfig ]; then
    echo "⚙️  Setting up Git configuration..."
    git config --global init.defaultBranch main
    git config --global core.autocrlf input
    git config --global pull.rebase false
    git config --global user.name "Developer"
    git config --global user.email "developer@localhost"
fi

# Initialize project if package.json doesn't exist
if [ ! -f /workspace/package.json ] && [ ! -f /workspace/pyproject.toml ] && [ ! -f /workspace/go.mod ]; then
    echo "📦 Initializing new project..."

    # Create basic package.json
    cat > /workspace/package.json << 'EOF'
{
  "name": "workspace-project",
  "version": "1.0.0",
  "description": "Universal development workspace",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "dev": "nodemon index.js",
    "test": "jest",
    "lint": "eslint .",
    "format": "prettier --write ."
  },
  "keywords": [],
  "author": "",
  "license": "MIT",
  "devDependencies": {
    "nodemon": "^3.0.0",
    "jest": "^29.0.0",
    "eslint": "^8.0.0",
    "prettier": "^3.0.0"
  }
}
EOF

    # Create basic Python project structure
    cat > /workspace/pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "workspace-project"
version = "1.0.0"
description = "Universal development workspace"
authors = [
    {name = "Developer", email = "developer@localhost"}
]
license = {text = "MIT"}
requires-python = ">=3.8"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=1.0.0",
    "isort>=5.0.0"
]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.isort]
profile = "black"

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
EOF

    # Create basic requirements.txt
    cat > /workspace/requirements.txt << 'EOF'
# Development dependencies
pytest>=7.0.0
black>=22.0.0
flake8>=5.0.0
mypy>=1.0.0
isort>=5.0.0
EOF

    # Create basic Go module
    if command -v go >/dev/null 2>&1; then
        cd /workspace && go mod init workspace-project
    fi
fi

# Install dependencies based on what's available
echo "📦 Installing dependencies..."

# Install Node.js dependencies
if [ -f /workspace/package.json ]; then
    echo "Installing Node.js dependencies..."
    cd /workspace && npm install
fi

# Install Python dependencies
if [ -f /workspace/requirements.txt ]; then
    echo "Installing Python dependencies..."
    pip3 install -r /workspace/requirements.txt
fi

# Install Python dev dependencies from pyproject.toml
if [ -f /workspace/pyproject.toml ]; then
    echo "Installing Python project dependencies..."
    cd /workspace && pip3 install -e ".[dev]"
fi

# Download Go dependencies
if [ -f /workspace/go.mod ]; then
    echo "Downloading Go dependencies..."
    cd /workspace && go mod download
fi

# Set up pre-commit hooks if available
if command -v pre-commit >/dev/null 2>&1 && [ -f /workspace/.pre-commit-config.yaml ]; then
    echo "Installing pre-commit hooks..."
    cd /workspace && pre-commit install
fi

# Create default VS Code workspace settings
if [ ! -f /workspace/.vscode/settings.json ]; then
    echo "⚙️  Creating VS Code workspace settings..."
    mkdir -p /workspace/.vscode
    cat > /workspace/.vscode/settings.json << 'EOF'
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": "explicit",
    "source.organizeImports": "explicit"
  },
  "python.defaultInterpreterPath": "/usr/bin/python3",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.testing.pytestEnabled": true,
  "eslint.validate": ["javascript", "typescript"],
  "go.formatTool": "goimports",
  "rust-analyzer.check.command": "clippy"
}
EOF
fi

# Create sample files if they don't exist
if [ ! -f /workspace/README.md ]; then
    echo "📝 Creating README.md..."
    cat > /workspace/README.md << 'EOF'
# Universal Development Workspace

This is a universal development workspace that supports multiple programming languages and frameworks.

## Getting Started

This workspace includes support for:
- Python 3.12
- Node.js 20
- Go 1.21
- Rust (latest)
- Java 17

## Development

Use the integrated terminal or VS Code tasks to run commands:

```bash
# Python
python3 -m pytest tests/
black .
flake8 .

# Node.js
npm test
npm run lint
npm run format

# Go
go test ./...
go fmt ./...
golangci-lint run

# Rust
cargo test
cargo clippy
cargo fmt
```

## Database Access

The development environment includes:
- PostgreSQL (localhost:5432)
- MySQL (localhost:3306)
- Redis (localhost:6379)
- MongoDB (localhost:27017)
- Elasticsearch (localhost:9200)

## Services

- pgAdmin: http://localhost:8081
- phpMyAdmin: http://localhost:8082
- Redis Commander: http://localhost:8083
- Mongo Express: http://localhost:8084
- MinIO Console: http://localhost:9001
- RabbitMQ Management: http://localhost:15672
- Mailhog: http://localhost:8025
EOF
fi

# Set proper permissions
sudo chown -R developer:developer /workspace
sudo chmod -R 755 /workspace

echo "✅ Development environment setup complete!"
echo "🎉 Happy coding!"
