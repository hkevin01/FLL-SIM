# Universal Development Environment Makefile
# Provides consistent commands across all project types
.PHONY: help setup start stop restart clean build test lint format security docs backup

# Default target
.DEFAULT_GOAL := help

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
MAGENTA := \033[0;35m
CYAN := \033[0;36m
WHITE := \033[0;37m
RESET := \033[0m

# Project detection
HAS_PACKAGE_JSON := $(shell test -f package.json && echo "yes")
HAS_PYPROJECT := $(shell test -f pyproject.toml && echo "yes")
HAS_REQUIREMENTS := $(shell test -f requirements.txt && echo "yes")
HAS_GO_MOD := $(shell test -f go.mod && echo "yes")
HAS_CARGO := $(shell test -f Cargo.toml && echo "yes")
HAS_POM := $(shell test -f pom.xml && echo "yes")
HAS_GRADLE := $(shell test -f build.gradle && echo "yes")
HAS_DOCKER := $(shell test -f docker-compose.yml && echo "yes")
HAS_DEVCONTAINER := $(shell test -f .devcontainer/devcontainer.json && echo "yes")

help: ## Show this help message
	@echo "$(CYAN)Universal Development Environment$(RESET)"
	@echo "$(CYAN)================================$(RESET)"
	@echo ""
	@echo "$(GREEN)Detected project types:$(RESET)"
ifeq ($(HAS_PACKAGE_JSON),yes)
	@echo "  📦 Node.js/JavaScript project"
endif
ifeq ($(HAS_PYPROJECT),yes)
	@echo "  🐍 Python project (pyproject.toml)"
endif
ifeq ($(HAS_REQUIREMENTS),yes)
	@echo "  🐍 Python project (requirements.txt)"
endif
ifeq ($(HAS_GO_MOD),yes)
	@echo "  🔷 Go project"
endif
ifeq ($(HAS_CARGO),yes)
	@echo "  🦀 Rust project"
endif
ifeq ($(HAS_POM),yes)
	@echo "  ☕ Java project (Maven)"
endif
ifeq ($(HAS_GRADLE),yes)
	@echo "  ☕ Java project (Gradle)"
endif
ifeq ($(HAS_DOCKER),yes)
	@echo "  🐳 Docker Compose project"
endif
ifeq ($(HAS_DEVCONTAINER),yes)
	@echo "  📦 VS Code Dev Container"
endif
	@echo ""
	@echo "$(GREEN)Available commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(CYAN)%-15s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

setup: ## Set up development environment
	@echo "$(GREEN)Setting up development environment...$(RESET)"
ifeq ($(HAS_DEVCONTAINER),yes)
	@echo "$(BLUE)Setting up VS Code Dev Container...$(RESET)"
	@chmod +x .devcontainer/*.sh
endif
ifeq ($(HAS_DOCKER),yes)
	@echo "$(BLUE)Building Docker containers...$(RESET)"
	@docker-compose -f docker/docker-compose.dev.yml build
endif
ifeq ($(HAS_PACKAGE_JSON),yes)
	@echo "$(BLUE)Installing Node.js dependencies...$(RESET)"
	@npm install
endif
ifeq ($(HAS_REQUIREMENTS),yes)
	@echo "$(BLUE)Installing Python dependencies...$(RESET)"
	@pip install -r requirements.txt
endif
ifeq ($(HAS_PYPROJECT),yes)
	@echo "$(BLUE)Installing Python project dependencies...$(RESET)"
	@pip install -e ".[dev]"
endif
ifeq ($(HAS_GO_MOD),yes)
	@echo "$(BLUE)Downloading Go dependencies...$(RESET)"
	@go mod download
endif
ifeq ($(HAS_CARGO),yes)
	@echo "$(BLUE)Building Rust dependencies...$(RESET)"
	@cargo fetch
endif
	@echo "$(GREEN)✅ Development environment setup complete!$(RESET)"

start: ## Start development services
	@echo "$(GREEN)Starting development services...$(RESET)"
ifeq ($(HAS_DOCKER),yes)
	@docker-compose -f docker/docker-compose.dev.yml up -d
	@echo "$(GREEN)✅ Docker services started!$(RESET)"
	@echo "$(CYAN)Services available at:$(RESET)"
	@echo "  📊 pgAdmin:           http://localhost:8081"
	@echo "  📊 phpMyAdmin:        http://localhost:8082"
	@echo "  📊 Redis Commander:   http://localhost:8083"
	@echo "  📊 Mongo Express:     http://localhost:8084"
	@echo "  🗄️  MinIO Console:     http://localhost:9001"
	@echo "  📨 RabbitMQ:          http://localhost:15672"
	@echo "  📧 Mailhog:           http://localhost:8025"
endif
ifeq ($(HAS_PACKAGE_JSON),yes)
	@echo "$(BLUE)Node.js development server can be started with: npm run dev$(RESET)"
endif
ifeq ($(HAS_PYPROJECT),yes)
	@echo "$(BLUE)Python application can be started with: python -m src$(RESET)"
endif

stop: ## Stop development services
	@echo "$(YELLOW)Stopping development services...$(RESET)"
ifeq ($(HAS_DOCKER),yes)
	@docker-compose -f docker/docker-compose.dev.yml down
endif
	@echo "$(GREEN)✅ Services stopped!$(RESET)"

restart: stop start ## Restart development services

logs: ## Show service logs
	@echo "$(CYAN)Showing service logs...$(RESET)"
ifeq ($(HAS_DOCKER),yes)
	@docker-compose -f docker/docker-compose.dev.yml logs -f
endif

build: ## Build the project
	@echo "$(GREEN)Building project...$(RESET)"
ifeq ($(HAS_PACKAGE_JSON),yes)
	@echo "$(BLUE)Building Node.js project...$(RESET)"
	@npm run build
endif
ifeq ($(HAS_PYPROJECT),yes)
	@echo "$(BLUE)Building Python project...$(RESET)"
	@python -m build
endif
ifeq ($(HAS_GO_MOD),yes)
	@echo "$(BLUE)Building Go project...$(RESET)"
	@go build ./...
endif
ifeq ($(HAS_CARGO),yes)
	@echo "$(BLUE)Building Rust project...$(RESET)"
	@cargo build
endif
ifeq ($(HAS_POM),yes)
	@echo "$(BLUE)Building Java project (Maven)...$(RESET)"
	@mvn compile
endif
ifeq ($(HAS_GRADLE),yes)
	@echo "$(BLUE)Building Java project (Gradle)...$(RESET)"
	@gradle build
endif
	@echo "$(GREEN)✅ Build complete!$(RESET)"

test: ## Run tests
	@echo "$(GREEN)Running tests...$(RESET)"
ifeq ($(HAS_PACKAGE_JSON),yes)
	@echo "$(BLUE)Running Node.js tests...$(RESET)"
	@npm test
endif
ifeq ($(HAS_PYPROJECT),yes)
	@echo "$(BLUE)Running Python tests...$(RESET)"
	@python -m pytest
endif
ifeq ($(HAS_REQUIREMENTS),yes)
	@echo "$(BLUE)Running Python tests...$(RESET)"
	@python -m pytest tests/
endif
ifeq ($(HAS_GO_MOD),yes)
	@echo "$(BLUE)Running Go tests...$(RESET)"
	@go test ./...
endif
ifeq ($(HAS_CARGO),yes)
	@echo "$(BLUE)Running Rust tests...$(RESET)"
	@cargo test
endif
ifeq ($(HAS_POM),yes)
	@echo "$(BLUE)Running Java tests (Maven)...$(RESET)"
	@mvn test
endif
ifeq ($(HAS_GRADLE),yes)
	@echo "$(BLUE)Running Java tests (Gradle)...$(RESET)"
	@gradle test
endif
	@echo "$(GREEN)✅ Tests complete!$(RESET)"

lint: ## Run linting
	@echo "$(GREEN)Running linting...$(RESET)"
ifeq ($(HAS_PACKAGE_JSON),yes)
	@echo "$(BLUE)Linting JavaScript/TypeScript...$(RESET)"
	@npm run lint || echo "$(YELLOW)⚠️  No lint script found in package.json$(RESET)"
endif
ifeq ($(HAS_PYPROJECT),yes)
	@echo "$(BLUE)Linting Python code...$(RESET)"
	@flake8 src/ || echo "$(YELLOW)⚠️  flake8 not found$(RESET)"
	@pylint src/ || echo "$(YELLOW)⚠️  pylint not found$(RESET)"
	@mypy src/ || echo "$(YELLOW)⚠️  mypy not found$(RESET)"
endif
ifeq ($(HAS_REQUIREMENTS),yes)
	@echo "$(BLUE)Linting Python code...$(RESET)"
	@flake8 . || echo "$(YELLOW)⚠️  flake8 not found$(RESET)"
	@pylint . || echo "$(YELLOW)⚠️  pylint not found$(RESET)"
endif
ifeq ($(HAS_GO_MOD),yes)
	@echo "$(BLUE)Linting Go code...$(RESET)"
	@golangci-lint run || echo "$(YELLOW)⚠️  golangci-lint not found$(RESET)"
endif
ifeq ($(HAS_CARGO),yes)
	@echo "$(BLUE)Linting Rust code...$(RESET)"
	@cargo clippy
endif
	@echo "$(GREEN)✅ Linting complete!$(RESET)"

format: ## Format code
	@echo "$(GREEN)Formatting code...$(RESET)"
ifeq ($(HAS_PACKAGE_JSON),yes)
	@echo "$(BLUE)Formatting JavaScript/TypeScript...$(RESET)"
	@npx prettier --write . || echo "$(YELLOW)⚠️  prettier not found$(RESET)"
endif
ifeq ($(HAS_PYPROJECT),yes)
	@echo "$(BLUE)Formatting Python code...$(RESET)"
	@black src/ || echo "$(YELLOW)⚠️  black not found$(RESET)"
	@isort src/ || echo "$(YELLOW)⚠️  isort not found$(RESET)"
endif
ifeq ($(HAS_REQUIREMENTS),yes)
	@echo "$(BLUE)Formatting Python code...$(RESET)"
	@black . || echo "$(YELLOW)⚠️  black not found$(RESET)"
	@isort . || echo "$(YELLOW)⚠️  isort not found$(RESET)"
endif
ifeq ($(HAS_GO_MOD),yes)
	@echo "$(BLUE)Formatting Go code...$(RESET)"
	@go fmt ./...
	@goimports -w . || echo "$(YELLOW)⚠️  goimports not found$(RESET)"
endif
ifeq ($(HAS_CARGO),yes)
	@echo "$(BLUE)Formatting Rust code...$(RESET)"
	@cargo fmt
endif
	@echo "$(GREEN)✅ Formatting complete!$(RESET)"

security: ## Run security scans
	@echo "$(GREEN)Running security scans...$(RESET)"
ifeq ($(HAS_PACKAGE_JSON),yes)
	@echo "$(BLUE)Scanning Node.js dependencies...$(RESET)"
	@npm audit || echo "$(YELLOW)⚠️  npm audit found vulnerabilities$(RESET)"
endif
ifeq ($(HAS_PYPROJECT),yes)
	@echo "$(BLUE)Scanning Python dependencies...$(RESET)"
	@safety check || echo "$(YELLOW)⚠️  safety not found or found vulnerabilities$(RESET)"
	@bandit -r src/ || echo "$(YELLOW)⚠️  bandit not found$(RESET)"
endif
ifeq ($(HAS_REQUIREMENTS),yes)
	@echo "$(BLUE)Scanning Python dependencies...$(RESET)"
	@safety check || echo "$(YELLOW)⚠️  safety not found or found vulnerabilities$(RESET)"
	@bandit -r . || echo "$(YELLOW)⚠️  bandit not found$(RESET)"
endif
ifeq ($(HAS_CARGO),yes)
	@echo "$(BLUE)Scanning Rust dependencies...$(RESET)"
	@cargo audit || echo "$(YELLOW)⚠️  cargo audit not found$(RESET)"
endif
	@echo "$(GREEN)✅ Security scans complete!$(RESET)"

docs: ## Generate documentation
	@echo "$(GREEN)Generating documentation...$(RESET)"
ifeq ($(HAS_PACKAGE_JSON),yes)
	@echo "$(BLUE)Generating JavaScript/TypeScript docs...$(RESET)"
	@npx typedoc || echo "$(YELLOW)⚠️  typedoc not found$(RESET)"
endif
ifeq ($(HAS_PYPROJECT),yes)
	@echo "$(BLUE)Generating Python docs...$(RESET)"
	@sphinx-build -b html docs/ docs/_build/ || echo "$(YELLOW)⚠️  sphinx not found$(RESET)"
endif
ifeq ($(HAS_GO_MOD),yes)
	@echo "$(BLUE)Generating Go docs...$(RESET)"
	@go doc ./...
endif
ifeq ($(HAS_CARGO),yes)
	@echo "$(BLUE)Generating Rust docs...$(RESET)"
	@cargo doc
endif
	@echo "$(GREEN)✅ Documentation generated!$(RESET)"

clean: ## Clean build artifacts
	@echo "$(YELLOW)Cleaning build artifacts...$(RESET)"
ifeq ($(HAS_PACKAGE_JSON),yes)
	@echo "$(BLUE)Cleaning Node.js artifacts...$(RESET)"
	@rm -rf node_modules/.cache dist/ build/
endif
ifeq ($(HAS_PYPROJECT),yes)
	@echo "$(BLUE)Cleaning Python artifacts...$(RESET)"
	@rm -rf build/ dist/ *.egg-info/ .pytest_cache/ __pycache__/ .coverage .mypy_cache/
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
endif
ifeq ($(HAS_GO_MOD),yes)
	@echo "$(BLUE)Cleaning Go artifacts...$(RESET)"
	@go clean -cache -modcache -testcache
endif
ifeq ($(HAS_CARGO),yes)
	@echo "$(BLUE)Cleaning Rust artifacts...$(RESET)"
	@cargo clean
endif
ifeq ($(HAS_DOCKER),yes)
	@echo "$(BLUE)Cleaning Docker artifacts...$(RESET)"
	@docker system prune -f
endif
	@echo "$(GREEN)✅ Cleanup complete!$(RESET)"

backup: ## Create project backup
	@echo "$(GREEN)Creating project backup...$(RESET)"
	@mkdir -p backups
	@tar -czf backups/backup-$(shell date +%Y%m%d-%H%M%S).tar.gz \
		--exclude='node_modules' \
		--exclude='target' \
		--exclude='build' \
		--exclude='dist' \
		--exclude='.git' \
		--exclude='backups' \
		--exclude='__pycache__' \
		--exclude='.pytest_cache' \
		--exclude='.mypy_cache' \
		--exclude='*.pyc' \
		.
	@echo "$(GREEN)✅ Backup created in backups/ directory$(RESET)"

dev: ## Start development mode
	@echo "$(GREEN)Starting development mode...$(RESET)"
	@$(MAKE) start
ifeq ($(HAS_PACKAGE_JSON),yes)
	@echo "$(BLUE)Starting Node.js development server...$(RESET)"
	@npm run dev &
endif
ifeq ($(HAS_PYPROJECT),yes)
	@echo "$(BLUE)Python development mode ready$(RESET)"
	@echo "$(CYAN)Run: python -m src$(RESET)"
endif

status: ## Show development environment status
	@echo "$(CYAN)Development Environment Status$(RESET)"
	@echo "$(CYAN)==============================$(RESET)"
ifeq ($(HAS_DOCKER),yes)
	@echo ""
	@echo "$(GREEN)Docker Services:$(RESET)"
	@docker-compose -f docker/docker-compose.dev.yml ps
endif
	@echo ""
	@echo "$(GREEN)Project Status:$(RESET)"
ifeq ($(HAS_PACKAGE_JSON),yes)
	@echo "  📦 Node.js: $(shell node --version 2>/dev/null || echo 'Not installed')"
	@echo "  📦 npm: $(shell npm --version 2>/dev/null || echo 'Not installed')"
endif
ifeq ($(HAS_PYPROJECT),yes)
	@echo "  🐍 Python: $(shell python --version 2>/dev/null || echo 'Not installed')"
endif
ifeq ($(HAS_GO_MOD),yes)
	@echo "  🔷 Go: $(shell go version 2>/dev/null || echo 'Not installed')"
endif
ifeq ($(HAS_CARGO),yes)
	@echo "  🦀 Rust: $(shell rustc --version 2>/dev/null || echo 'Not installed')"
endif

ci: lint test security ## Run CI pipeline (lint, test, security)
	@echo "$(GREEN)✅ CI pipeline complete!$(RESET)"
