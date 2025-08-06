#!/bin/bash
# Universal Development Environment Setup Script
# Supports any project type with automatic detection and configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'
BOLD='\033[1m'
RESET='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DOCKER_DIR="$PROJECT_ROOT/docker"
CONFIG_DIR="$PROJECT_ROOT/configs"

# Print colored output
print_color() {
    printf "${!1}%s${RESET}\n" "$2"
}

print_header() {
    echo ""
    print_color "CYAN" "=================================="
    print_color "CYAN" "$1"
    print_color "CYAN" "=================================="
}

print_step() {
    print_color "GREEN" "🚀 $1"
}

print_info() {
    print_color "BLUE" "ℹ️  $1"
}

print_warning() {
    print_color "YELLOW" "⚠️  $1"
}

print_error() {
    print_color "RED" "❌ $1"
}

print_success() {
    print_color "GREEN" "✅ $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command_exists apt-get; then
            echo "ubuntu"
        elif command_exists yum; then
            echo "rhel"
        elif command_exists pacman; then
            echo "arch"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Install Docker
install_docker() {
    local os=$(detect_os)

    if command_exists docker; then
        print_info "Docker is already installed"
        return 0
    fi

    print_step "Installing Docker for $os..."

    case $os in
        ubuntu)
            curl -fsSL https://get.docker.com | sh
            sudo usermod -aG docker $USER
            ;;
        macos)
            if command_exists brew; then
                brew install --cask docker
            else
                print_error "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
                return 1
            fi
            ;;
        windows)
            print_error "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
            return 1
            ;;
        *)
            print_error "Unsupported OS for automatic Docker installation"
            return 1
            ;;
    esac

    print_success "Docker installed successfully"
}

# Install Docker Compose
install_docker_compose() {
    if command_exists docker-compose || docker compose version >/dev/null 2>&1; then
        print_info "Docker Compose is already available"
        return 0
    fi

    print_step "Installing Docker Compose..."

    # Try to install via pip first
    if command_exists pip3; then
        pip3 install docker-compose
    elif command_exists pip; then
        pip install docker-compose
    else
        # Download binary
        local os=$(detect_os)
        case $os in
            linux)
                sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                sudo chmod +x /usr/local/bin/docker-compose
                ;;
            macos)
                if command_exists brew; then
                    brew install docker-compose
                else
                    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                    chmod +x /usr/local/bin/docker-compose
                fi
                ;;
            *)
                print_error "Please install Docker Compose manually"
                return 1
                ;;
        esac
    fi

    print_success "Docker Compose installed successfully"
}

# Install system dependencies
install_system_deps() {
    local os=$(detect_os)

    print_step "Installing system dependencies for $os..."

    case $os in
        ubuntu)
            sudo apt-get update
            sudo apt-get install -y curl wget git make build-essential
            ;;
        macos)
            if ! command_exists brew; then
                print_step "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            brew install curl wget git make
            ;;
        *)
            print_warning "Please install curl, wget, git, and make manually"
            ;;
    esac
}

# Detect project type
detect_project_type() {
    local types=()

    [[ -f "$PROJECT_ROOT/package.json" ]] && types+=("nodejs")
    [[ -f "$PROJECT_ROOT/pyproject.toml" ]] && types+=("python-modern")
    [[ -f "$PROJECT_ROOT/requirements.txt" ]] && types+=("python-classic")
    [[ -f "$PROJECT_ROOT/setup.py" ]] && types+=("python-classic")
    [[ -f "$PROJECT_ROOT/go.mod" ]] && types+=("go")
    [[ -f "$PROJECT_ROOT/Cargo.toml" ]] && types+=("rust")
    [[ -f "$PROJECT_ROOT/pom.xml" ]] && types+=("java-maven")
    [[ -f "$PROJECT_ROOT/build.gradle" ]] && types+=("java-gradle")
    [[ -f "$PROJECT_ROOT/composer.json" ]] && types+=("php")
    [[ -f "$PROJECT_ROOT/.csproj" ]] && types+=("dotnet")

    echo "${types[@]}"
}

# Setup development environment for detected project types
setup_project_environment() {
    local project_types=($(detect_project_type))

    if [[ ${#project_types[@]} -eq 0 ]]; then
        print_warning "No recognized project files found. Setting up universal environment..."
        project_types=("universal")
    fi

    print_info "Detected project types: ${project_types[*]}"

    for project_type in "${project_types[@]}"; do
        print_step "Setting up $project_type environment..."

        case $project_type in
            nodejs)
                setup_nodejs_environment
                ;;
            python-modern|python-classic)
                setup_python_environment
                ;;
            go)
                setup_go_environment
                ;;
            rust)
                setup_rust_environment
                ;;
            java-maven|java-gradle)
                setup_java_environment
                ;;
            universal)
                setup_universal_environment
                ;;
        esac
    done
}

# Setup Node.js environment
setup_nodejs_environment() {
    if ! command_exists node; then
        print_step "Installing Node.js..."
        local os=$(detect_os)
        case $os in
            ubuntu)
                curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
                sudo apt-get install -y nodejs
                ;;
            macos)
                if command_exists brew; then
                    brew install node
                else
                    print_warning "Please install Node.js from https://nodejs.org"
                fi
                ;;
            *)
                print_warning "Please install Node.js from https://nodejs.org"
                ;;
        esac
    fi

    if [[ -f "$PROJECT_ROOT/package.json" ]]; then
        print_step "Installing Node.js dependencies..."
        cd "$PROJECT_ROOT"
        npm install
    fi
}

# Setup Python environment
setup_python_environment() {
    if ! command_exists python3; then
        print_step "Installing Python..."
        local os=$(detect_os)
        case $os in
            ubuntu)
                sudo apt-get install -y python3 python3-pip python3-venv
                ;;
            macos)
                if command_exists brew; then
                    brew install python
                else
                    print_warning "Please install Python from https://python.org"
                fi
                ;;
            *)
                print_warning "Please install Python from https://python.org"
                ;;
        esac
    fi

    # Create virtual environment if it doesn't exist
    if [[ ! -d "$PROJECT_ROOT/venv" ]]; then
        print_step "Creating Python virtual environment..."
        cd "$PROJECT_ROOT"
        python3 -m venv venv
    fi

    # Install dependencies
    if [[ -f "$PROJECT_ROOT/requirements.txt" ]]; then
        print_step "Installing Python dependencies..."
        cd "$PROJECT_ROOT"
        source venv/bin/activate
        pip install -r requirements.txt
    fi

    if [[ -f "$PROJECT_ROOT/pyproject.toml" ]]; then
        print_step "Installing Python project dependencies..."
        cd "$PROJECT_ROOT"
        source venv/bin/activate
        pip install -e ".[dev]"
    fi
}

# Setup Go environment
setup_go_environment() {
    if ! command_exists go; then
        print_step "Installing Go..."
        local os=$(detect_os)
        case $os in
            ubuntu)
                wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz
                sudo tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz
                echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
                export PATH=$PATH:/usr/local/go/bin
                rm go1.21.5.linux-amd64.tar.gz
                ;;
            macos)
                if command_exists brew; then
                    brew install go
                else
                    print_warning "Please install Go from https://golang.org"
                fi
                ;;
            *)
                print_warning "Please install Go from https://golang.org"
                ;;
        esac
    fi

    if [[ -f "$PROJECT_ROOT/go.mod" ]]; then
        print_step "Downloading Go dependencies..."
        cd "$PROJECT_ROOT"
        go mod download
    fi
}

# Setup Rust environment
setup_rust_environment() {
    if ! command_exists rustc; then
        print_step "Installing Rust..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
        source ~/.cargo/env
    fi

    if [[ -f "$PROJECT_ROOT/Cargo.toml" ]]; then
        print_step "Building Rust dependencies..."
        cd "$PROJECT_ROOT"
        cargo fetch
    fi
}

# Setup Java environment
setup_java_environment() {
    if ! command_exists java; then
        print_step "Installing Java..."
        local os=$(detect_os)
        case $os in
            ubuntu)
                sudo apt-get install -y openjdk-17-jdk
                ;;
            macos)
                if command_exists brew; then
                    brew install openjdk@17
                else
                    print_warning "Please install Java from https://adoptium.net"
                fi
                ;;
            *)
                print_warning "Please install Java from https://adoptium.net"
                ;;
        esac
    fi

    if [[ -f "$PROJECT_ROOT/pom.xml" ]] && ! command_exists mvn; then
        print_step "Installing Maven..."
        local os=$(detect_os)
        case $os in
            ubuntu)
                sudo apt-get install -y maven
                ;;
            macos)
                if command_exists brew; then
                    brew install maven
                fi
                ;;
        esac
    fi

    if [[ -f "$PROJECT_ROOT/build.gradle" ]] && ! command_exists gradle; then
        print_step "Installing Gradle..."
        local os=$(detect_os)
        case $os in
            ubuntu)
                sudo apt-get install -y gradle
                ;;
            macos)
                if command_exists brew; then
                    brew install gradle
                fi
                ;;
        esac
    fi
}

# Setup universal environment (creates basic project structure)
setup_universal_environment() {
    print_step "Setting up universal project structure..."

    # Create basic directories
    mkdir -p "$PROJECT_ROOT"/{src,tests,docs,configs,scripts,data,logs}

    # Create basic files if they don't exist
    if [[ ! -f "$PROJECT_ROOT/README.md" ]]; then
        cat > "$PROJECT_ROOT/README.md" << 'EOF'
# Universal Development Project

This project has been set up with the Universal Development Environment.

## Getting Started

```bash
# Start development environment
make start

# Build the project
make build

# Run tests
make test

# Format code
make format

# Run linting
make lint

# Run security scans
make security
```

## Available Services

When using Docker development environment:

- PostgreSQL: localhost:5432
- MySQL: localhost:3306
- Redis: localhost:6379
- MongoDB: localhost:27017
- Elasticsearch: localhost:9200

## Admin Interfaces

- pgAdmin: http://localhost:8081
- phpMyAdmin: http://localhost:8082
- Redis Commander: http://localhost:8083
- Mongo Express: http://localhost:8084
- MinIO Console: http://localhost:9001
- RabbitMQ Management: http://localhost:15672
- Mailhog: http://localhost:8025
EOF
    fi

    # Create .gitignore if it doesn't exist
    if [[ ! -f "$PROJECT_ROOT/.gitignore" ]]; then
        cat > "$PROJECT_ROOT/.gitignore" << 'EOF'
# Dependencies
node_modules/
venv/
target/
build/
dist/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Environment
.env
.env.local

# Cache
.cache/
.pytest_cache/
__pycache__/
*.pyc

# Coverage
coverage/
.coverage
.nyc_output/
EOF
    fi
}

# Setup Docker development environment
setup_docker_environment() {
    print_step "Setting up Docker development environment..."

    # Build Docker images
    if [[ -f "$DOCKER_DIR/docker-compose.dev.yml" ]]; then
        cd "$PROJECT_ROOT"
        docker-compose -f docker/docker-compose.dev.yml build
        print_success "Docker images built successfully"
    else
        print_warning "Docker compose file not found, skipping Docker setup"
    fi
}

# Setup VS Code development container
setup_vscode_devcontainer() {
    if [[ -d "$PROJECT_ROOT/.devcontainer" ]]; then
        print_step "Setting up VS Code development container..."
        chmod +x "$PROJECT_ROOT/.devcontainer"/*.sh
        print_success "VS Code development container configured"
    fi
}

# Main setup function
main() {
    print_header "Universal Development Environment Setup"

    print_info "Project root: $PROJECT_ROOT"
    print_info "Operating system: $(detect_os)"

    # Install system dependencies
    install_system_deps

    # Install Docker if not present
    install_docker
    install_docker_compose

    # Setup project-specific environments
    setup_project_environment

    # Setup Docker environment
    if command_exists docker && command_exists docker-compose; then
        setup_docker_environment
    fi

    # Setup VS Code dev container
    setup_vscode_devcontainer

    print_header "Setup Complete!"
    print_success "Universal development environment is ready!"

    echo ""
    print_info "Next steps:"
    echo "  1. Run 'make start' to start development services"
    echo "  2. Run 'make status' to check environment status"
    echo "  3. Run 'make help' to see available commands"
    echo ""

    if command_exists code && [[ -d "$PROJECT_ROOT/.devcontainer" ]]; then
        print_info "💡 Tip: Run 'code .' and select 'Reopen in Container' for VS Code development"
    fi

    echo ""
    print_success "Happy coding! 🎉"
}

# Run main function
main "$@"
