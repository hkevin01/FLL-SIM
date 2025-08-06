"""
Universal Docker Development Strategy for FLL-Sim

Provides comprehensive containerization solutions for development, testing,
and deployment across different environments and project types.
"""

import shutil
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.fll_sim.utils.logger import FLLLogger


class ProjectType(Enum):
    """Supported project types for containerization."""
    PYTHON_BASIC = "python_basic"
    PYTHON_DJANGO = "python_django"
    PYTHON_FLASK = "python_flask"
    PYTHON_FASTAPI = "python_fastapi"
    NODEJS_BASIC = "nodejs_basic"
    NODEJS_EXPRESS = "nodejs_express"
    NODEJS_REACT = "nodejs_react"
    NODEJS_NEXT = "nodejs_next"
    NODEJS_VUE = "nodejs_vue"
    JAVA_MAVEN = "java_maven"
    JAVA_GRADLE = "java_gradle"
    DOTNET_CORE = "dotnet_core"
    GO_MODULE = "go_module"
    RUST_CARGO = "rust_cargo"
    PHP_COMPOSER = "php_composer"
    RUBY_RAILS = "ruby_rails"
    CPP_CMAKE = "cpp_cmake"
    MULTI_LANGUAGE = "multi_language"


class EnvironmentType(Enum):
    """Types of development environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    CI_CD = "ci_cd"


@dataclass
class DockerConfiguration:
    """Docker configuration for a project."""
    project_type: ProjectType
    base_image: str
    working_dir: str = "/app"
    exposed_ports: List[int] = None
    environment_vars: Dict[str, str] = None
    volumes: List[Tuple[str, str]] = None  # (host_path, container_path)
    dependencies_file: str = ""
    install_command: str = ""
    start_command: str = ""
    build_command: str = ""
    test_command: str = ""
    additional_packages: List[str] = None

    def __post_init__(self):
        if self.exposed_ports is None:
            self.exposed_ports = []
        if self.environment_vars is None:
            self.environment_vars = {}
        if self.volumes is None:
            self.volumes = []
        if self.additional_packages is None:
            self.additional_packages = []


class UniversalDockerStrategy:
    """Universal Docker development strategy implementation."""

    def __init__(self, project_root: str = "."):
        self.logger = FLLLogger('DockerStrategy')
        self.project_root = Path(project_root).resolve()

        # Pre-defined configurations for different project types
        self.configurations = self._initialize_configurations()

        # Docker templates
        self.dockerfile_templates = self._initialize_dockerfile_templates()
        self.compose_templates = self._initialize_compose_templates()

        self.logger.info("Universal Docker Strategy initialized")

    def _initialize_configurations(self) -> Dict[ProjectType, DockerConfiguration]:
        """Initialize pre-defined Docker configurations."""
        configs = {}

        # Python configurations
        configs[ProjectType.PYTHON_BASIC] = DockerConfiguration(
            project_type=ProjectType.PYTHON_BASIC,
            base_image="python:3.12-slim",
            exposed_ports=[8000],
            dependencies_file="requirements.txt",
            install_command="pip install --no-cache-dir -r requirements.txt",
            start_command="python main.py",
            test_command="python -m pytest",
            additional_packages=["git", "curl"]
        )

        configs[ProjectType.PYTHON_DJANGO] = DockerConfiguration(
            project_type=ProjectType.PYTHON_DJANGO,
            base_image="python:3.12-slim",
            exposed_ports=[8000],
            dependencies_file="requirements.txt",
            install_command="pip install --no-cache-dir -r requirements.txt",
            start_command="python manage.py runserver 0.0.0.0:8000",
            build_command="python manage.py collectstatic --noinput",
            test_command="python manage.py test",
            environment_vars={"DJANGO_SETTINGS_MODULE": "settings"},
            additional_packages=["postgresql-client", "git"]
        )

        configs[ProjectType.PYTHON_FLASK] = DockerConfiguration(
            project_type=ProjectType.PYTHON_FLASK,
            base_image="python:3.12-slim",
            exposed_ports=[5000],
            dependencies_file="requirements.txt",
            install_command="pip install --no-cache-dir -r requirements.txt",
            start_command="flask run --host=0.0.0.0",
            test_command="python -m pytest",
            environment_vars={"FLASK_ENV": "development"},
            additional_packages=["git"]
        )

        configs[ProjectType.PYTHON_FASTAPI] = DockerConfiguration(
            project_type=ProjectType.PYTHON_FASTAPI,
            base_image="python:3.12-slim",
            exposed_ports=[8000],
            dependencies_file="requirements.txt",
            install_command="pip install --no-cache-dir -r requirements.txt",
            start_command="uvicorn main:app --host 0.0.0.0 --port 8000 --reload",
            test_command="python -m pytest",
            additional_packages=["git"]
        )

        # Node.js configurations
        configs[ProjectType.NODEJS_BASIC] = DockerConfiguration(
            project_type=ProjectType.NODEJS_BASIC,
            base_image="node:18-alpine",
            exposed_ports=[3000],
            dependencies_file="package.json",
            install_command="npm install",
            start_command="npm start",
            build_command="npm run build",
            test_command="npm test",
            additional_packages=["git"]
        )

        configs[ProjectType.NODEJS_EXPRESS] = DockerConfiguration(
            project_type=ProjectType.NODEJS_EXPRESS,
            base_image="node:18-alpine",
            exposed_ports=[3000],
            dependencies_file="package.json",
            install_command="npm install",
            start_command="npm run dev",
            build_command="npm run build",
            test_command="npm test",
            environment_vars={"NODE_ENV": "development"},
            additional_packages=["git"]
        )

        configs[ProjectType.NODEJS_REACT] = DockerConfiguration(
            project_type=ProjectType.NODEJS_REACT,
            base_image="node:18-alpine",
            exposed_ports=[3000],
            dependencies_file="package.json",
            install_command="npm install",
            start_command="npm start",
            build_command="npm run build",
            test_command="npm test",
            additional_packages=["git"]
        )

        configs[ProjectType.NODEJS_NEXT] = DockerConfiguration(
            project_type=ProjectType.NODEJS_NEXT,
            base_image="node:18-alpine",
            exposed_ports=[3000],
            dependencies_file="package.json",
            install_command="npm install",
            start_command="npm run dev",
            build_command="npm run build",
            test_command="npm test",
            additional_packages=["git"]
        )

        # Java configurations
        configs[ProjectType.JAVA_MAVEN] = DockerConfiguration(
            project_type=ProjectType.JAVA_MAVEN,
            base_image="openjdk:17-jdk-slim",
            exposed_ports=[8080],
            dependencies_file="pom.xml",
            install_command="mvn dependency:go-offline",
            start_command="mvn spring-boot:run",
            build_command="mvn clean package",
            test_command="mvn test",
            additional_packages=["maven", "git"]
        )

        configs[ProjectType.JAVA_GRADLE] = DockerConfiguration(
            project_type=ProjectType.JAVA_GRADLE,
            base_image="openjdk:17-jdk-slim",
            exposed_ports=[8080],
            dependencies_file="build.gradle",
            install_command="./gradlew build --exclude-task test",
            start_command="./gradlew bootRun",
            build_command="./gradlew build",
            test_command="./gradlew test",
            additional_packages=["git"]
        )

        # .NET Core configuration
        configs[ProjectType.DOTNET_CORE] = DockerConfiguration(
            project_type=ProjectType.DOTNET_CORE,
            base_image="mcr.microsoft.com/dotnet/sdk:8.0",
            exposed_ports=[5000, 5001],
            dependencies_file="*.csproj",
            install_command="dotnet restore",
            start_command="dotnet run",
            build_command="dotnet build",
            test_command="dotnet test",
            additional_packages=["git"]
        )

        # Go configuration
        configs[ProjectType.GO_MODULE] = DockerConfiguration(
            project_type=ProjectType.GO_MODULE,
            base_image="golang:1.21-alpine",
            exposed_ports=[8080],
            dependencies_file="go.mod",
            install_command="go mod download",
            start_command="go run .",
            build_command="go build -o main .",
            test_command="go test ./...",
            additional_packages=["git"]
        )

        # Rust configuration
        configs[ProjectType.RUST_CARGO] = DockerConfiguration(
            project_type=ProjectType.RUST_CARGO,
            base_image="rust:1.75",
            exposed_ports=[8000],
            dependencies_file="Cargo.toml",
            install_command="cargo fetch",
            start_command="cargo run",
            build_command="cargo build --release",
            test_command="cargo test",
            additional_packages=["git"]
        )

        # PHP configuration
        configs[ProjectType.PHP_COMPOSER] = DockerConfiguration(
            project_type=ProjectType.PHP_COMPOSER,
            base_image="php:8.2-apache",
            exposed_ports=[80],
            dependencies_file="composer.json",
            install_command="composer install",
            start_command="apache2-foreground",
            test_command="./vendor/bin/phpunit",
            additional_packages=["git", "zip", "unzip"]
        )

        # Ruby Rails configuration
        configs[ProjectType.RUBY_RAILS] = DockerConfiguration(
            project_type=ProjectType.RUBY_RAILS,
            base_image="ruby:3.2",
            exposed_ports=[3000],
            dependencies_file="Gemfile",
            install_command="bundle install",
            start_command="rails server -b 0.0.0.0",
            build_command="rails assets:precompile",
            test_command="bundle exec rspec",
            additional_packages=["postgresql-client", "git", "nodejs", "npm"]
        )

        # C++ configuration
        configs[ProjectType.CPP_CMAKE] = DockerConfiguration(
            project_type=ProjectType.CPP_CMAKE,
            base_image="gcc:latest",
            exposed_ports=[8080],
            dependencies_file="CMakeLists.txt",
            install_command="cmake . && make",
            start_command="./main",
            build_command="cmake . && make",
            test_command="ctest",
            additional_packages=["cmake", "git"]
        )

        return configs

    def _initialize_dockerfile_templates(self) -> Dict[ProjectType, str]:
        """Initialize Dockerfile templates for different project types."""
        templates = {}

        # Python template
        python_template = '''# Auto-generated Dockerfile for {project_type}
FROM {base_image}

# Set working directory
WORKDIR {working_dir}

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    {additional_packages} \\
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY {dependencies_file} .

# Install dependencies
RUN {install_command}

# Copy application code
COPY . .

# Expose ports
{expose_ports}

# Set environment variables
{env_vars}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{primary_port}/health || exit 1

# Default command
CMD ["{start_command}"]
'''

        # Node.js template
        nodejs_template = '''# Auto-generated Dockerfile for {project_type}
FROM {base_image}

# Set working directory
WORKDIR {working_dir}

# Install system dependencies
RUN apk add --no-cache {additional_packages}

# Copy package files
COPY package*.json ./

# Install dependencies
RUN {install_command}

# Copy application code
COPY . .

# Build application (if needed)
{build_command_line}

# Expose ports
{expose_ports}

# Set environment variables
{env_vars}

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \\
    adduser -S nextjs -u 1001

USER nextjs

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD wget --no-verbose --tries=1 --spider http://localhost:{primary_port} || exit 1

# Default command
CMD ["{start_command}"]
'''

        # Java template
        java_template = '''# Auto-generated Dockerfile for {project_type}
FROM {base_image}

# Set working directory
WORKDIR {working_dir}

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    {additional_packages} \\
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY {dependencies_file} .

# Install dependencies
RUN {install_command}

# Copy application code
COPY . .

# Build application
RUN {build_command}

# Expose ports
{expose_ports}

# Set environment variables
{env_vars}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{primary_port}/health || exit 1

# Default command
CMD ["{start_command}"]
'''

        # Assign templates to project types
        for project_type in ProjectType:
            if "PYTHON" in project_type.name:
                templates[project_type] = python_template
            elif "NODEJS" in project_type.name:
                templates[project_type] = nodejs_template
            elif "JAVA" in project_type.name:
                templates[project_type] = java_template
            else:
                # Generic template for other languages
                templates[project_type] = python_template  # Use as fallback

        return templates

    def _initialize_compose_templates(self) -> Dict[EnvironmentType, str]:
        """Initialize Docker Compose templates for different environments."""
        templates = {}

        # Development environment
        templates[EnvironmentType.DEVELOPMENT] = '''# Auto-generated docker-compose.yml for development
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    container_name: {container_name}-dev
    ports:
      {port_mappings}
    volumes:
      - .:{working_dir}
      - /app/node_modules  # Prevent overwriting node_modules
    environment:
      {environment_vars}
    env_file:
      - .env.development
    restart: unless-stopped
    networks:
      - dev-network
    depends_on:
      {dependencies}

  # Database service (if needed)
  database:
    image: postgres:15-alpine
    container_name: {container_name}-db-dev
    environment:
      POSTGRES_DB: {db_name}
      POSTGRES_USER: {db_user}
      POSTGRES_PASSWORD: {db_password}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - dev-network

  # Redis cache (optional)
  redis:
    image: redis:7-alpine
    container_name: {container_name}-redis-dev
    ports:
      - "6379:6379"
    networks:
      - dev-network

networks:
  dev-network:
    driver: bridge

volumes:
  postgres_data:
'''

        # Testing environment
        templates[EnvironmentType.TESTING] = '''# Auto-generated docker-compose.test.yml
version: '3.8'

services:
  app-test:
    build:
      context: .
      dockerfile: Dockerfile.test
    container_name: {container_name}-test
    environment:
      {test_environment_vars}
    env_file:
      - .env.test
    volumes:
      - .:{working_dir}
      - test_reports:/app/test-reports
    networks:
      - test-network
    depends_on:
      - test-database
    command: {test_command}

  test-database:
    image: postgres:15-alpine
    container_name: {container_name}-test-db
    environment:
      POSTGRES_DB: {test_db_name}
      POSTGRES_USER: {test_db_user}
      POSTGRES_PASSWORD: {test_db_password}
    tmpfs:
      - /var/lib/postgresql/data  # Use tmpfs for faster tests
    networks:
      - test-network

networks:
  test-network:
    driver: bridge

volumes:
  test_reports:
'''

        # Production environment
        templates[EnvironmentType.PRODUCTION] = '''# Auto-generated docker-compose.prod.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    container_name: {container_name}-prod
    ports:
      {port_mappings}
    environment:
      {prod_environment_vars}
    env_file:
      - .env.production
    restart: always
    networks:
      - prod-network
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{primary_port}/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    container_name: {container_name}-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl:ro
    depends_on:
      - app
    networks:
      - prod-network

  watchtower:
    image: containrrr/watchtower
    container_name: {container_name}-watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command: --interval 30

networks:
  prod-network:
    driver: bridge
'''

        return templates

    def detect_project_type(self, project_path: Optional[str] = None) -> ProjectType:
        """Auto-detect project type based on files present."""
        if project_path is None:
            project_path = self.project_root
        else:
            project_path = Path(project_path)

        # Check for specific files to determine project type
        files_in_project = [f.name for f in project_path.iterdir() if f.is_file()]

        # Python detection
        if "requirements.txt" in files_in_project or "pyproject.toml" in files_in_project:
            if "manage.py" in files_in_project:
                return ProjectType.PYTHON_DJANGO
            elif "app.py" in files_in_project or any("flask" in f.lower() for f in files_in_project):
                return ProjectType.PYTHON_FLASK
            elif "main.py" in files_in_project:
                # Check for FastAPI imports
                main_content = ""
                main_file = project_path / "main.py"
                if main_file.exists():
                    main_content = main_file.read_text()
                    if "fastapi" in main_content.lower():
                        return ProjectType.PYTHON_FASTAPI
                return ProjectType.PYTHON_BASIC
            else:
                return ProjectType.PYTHON_BASIC

        # Node.js detection
        elif "package.json" in files_in_project:
            package_json_path = project_path / "package.json"
            if package_json_path.exists():
                try:
                    import json
                    with open(package_json_path, 'r') as f:
                        package_data = json.load(f)

                    dependencies = package_data.get("dependencies", {})
                    dev_dependencies = package_data.get("devDependencies", {})
                    all_deps = {**dependencies, **dev_dependencies}

                    if "next" in all_deps:
                        return ProjectType.NODEJS_NEXT
                    elif "react" in all_deps:
                        return ProjectType.NODEJS_REACT
                    elif "vue" in all_deps:
                        return ProjectType.NODEJS_VUE
                    elif "express" in all_deps:
                        return ProjectType.NODEJS_EXPRESS
                    else:
                        return ProjectType.NODEJS_BASIC
                except:
                    return ProjectType.NODEJS_BASIC
            else:
                return ProjectType.NODEJS_BASIC

        # Java detection
        elif "pom.xml" in files_in_project:
            return ProjectType.JAVA_MAVEN
        elif "build.gradle" in files_in_project or "build.gradle.kts" in files_in_project:
            return ProjectType.JAVA_GRADLE

        # .NET detection
        elif any(f.endswith(".csproj") for f in files_in_project):
            return ProjectType.DOTNET_CORE

        # Go detection
        elif "go.mod" in files_in_project:
            return ProjectType.GO_MODULE

        # Rust detection
        elif "Cargo.toml" in files_in_project:
            return ProjectType.RUST_CARGO

        # PHP detection
        elif "composer.json" in files_in_project:
            return ProjectType.PHP_COMPOSER

        # Ruby detection
        elif "Gemfile" in files_in_project:
            return ProjectType.RUBY_RAILS

        # C++ detection
        elif "CMakeLists.txt" in files_in_project:
            return ProjectType.CPP_CMAKE

        # Default fallback
        else:
            self.logger.warning("Could not detect project type, defaulting to Python")
            return ProjectType.PYTHON_BASIC

    def generate_dockerfile(
        self,
        project_type: Optional[ProjectType] = None,
        environment: EnvironmentType = EnvironmentType.DEVELOPMENT,
        custom_config: Optional[DockerConfiguration] = None,
        output_path: Optional[str] = None
    ) -> str:
        """Generate a Dockerfile for the project."""
        if project_type is None:
            project_type = self.detect_project_type()

        config = custom_config or self.configurations.get(project_type)
        if not config:
            raise ValueError(f"No configuration found for project type: {project_type}")

        template = self.dockerfile_templates.get(project_type, "")
        if not template:
            raise ValueError(f"No Dockerfile template found for project type: {project_type}")

        # Format template
        primary_port = config.exposed_ports[0] if config.exposed_ports else 8000

        expose_ports = "\\n".join(f"EXPOSE {port}" for port in config.exposed_ports)
        env_vars = "\\n".join(f"ENV {key}={value}" for key, value in config.environment_vars.items())
        additional_packages = " ".join(config.additional_packages)

        # Handle build command
        build_command_line = ""
        if config.build_command:
            build_command_line = f"RUN {config.build_command}"

        dockerfile_content = template.format(
            project_type=project_type.value,
            base_image=config.base_image,
            working_dir=config.working_dir,
            dependencies_file=config.dependencies_file,
            install_command=config.install_command,
            start_command=config.start_command,
            build_command_line=build_command_line,
            expose_ports=expose_ports,
            env_vars=env_vars,
            additional_packages=additional_packages,
            primary_port=primary_port
        )

        # Write to file if output path specified
        if output_path:
            dockerfile_path = Path(output_path)
            dockerfile_path.parent.mkdir(parents=True, exist_ok=True)
            dockerfile_path.write_text(dockerfile_content)
            self.logger.info(f"Generated Dockerfile: {dockerfile_path}")

        return dockerfile_content

    def generate_docker_compose(
        self,
        environment: EnvironmentType = EnvironmentType.DEVELOPMENT,
        project_type: Optional[ProjectType] = None,
        custom_config: Optional[DockerConfiguration] = None,
        output_path: Optional[str] = None
    ) -> str:
        """Generate a docker-compose.yml file."""
        if project_type is None:
            project_type = self.detect_project_type()

        config = custom_config or self.configurations.get(project_type)
        if not config:
            raise ValueError(f"No configuration found for project type: {project_type}")

        template = self.compose_templates.get(environment, "")
        if not template:
            raise ValueError(f"No compose template found for environment: {environment}")

        # Generate configuration values
        container_name = self.project_root.name.lower().replace("_", "-")
        primary_port = config.exposed_ports[0] if config.exposed_ports else 8000

        port_mappings = "\\n      ".join(
            f'- "{port}:{port}"' for port in config.exposed_ports
        )

        environment_vars = "\\n      ".join(
            f"{key}: {value}" for key, value in config.environment_vars.items()
        )

        # Database configuration
        db_name = f"{container_name}_db"
        db_user = "postgres"
        db_password = "postgres"

        test_environment_vars = environment_vars.replace("development", "test")
        prod_environment_vars = environment_vars.replace("development", "production")

        compose_content = template.format(
            container_name=container_name,
            working_dir=config.working_dir,
            port_mappings=port_mappings,
            environment_vars=environment_vars,
            test_environment_vars=test_environment_vars,
            prod_environment_vars=prod_environment_vars,
            primary_port=primary_port,
            db_name=db_name,
            db_user=db_user,
            db_password=db_password,
            test_db_name=f"{db_name}_test",
            test_db_user=db_user,
            test_db_password=db_password,
            test_command=config.test_command,
            dependencies=""  # Will be populated based on services needed
        )

        # Write to file if output path specified
        if output_path:
            compose_path = Path(output_path)
            compose_path.parent.mkdir(parents=True, exist_ok=True)
            compose_path.write_text(compose_content)
            self.logger.info(f"Generated docker-compose.yml: {compose_path}")

        return compose_content

    def generate_development_environment(
        self,
        project_type: Optional[ProjectType] = None,
        include_database: bool = True,
        include_cache: bool = False,
        output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate complete development environment with Docker."""
        if project_type is None:
            project_type = self.detect_project_type()

        if output_dir is None:
            output_dir = self.project_root / "docker"
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        generated_files = {}

        # Generate different Dockerfiles for different environments
        environments = [
            (EnvironmentType.DEVELOPMENT, "Dockerfile.dev"),
            (EnvironmentType.TESTING, "Dockerfile.test"),
            (EnvironmentType.PRODUCTION, "Dockerfile.prod")
        ]

        for env, filename in environments:
            dockerfile_path = output_dir / filename
            dockerfile_content = self.generate_dockerfile(
                project_type=project_type,
                environment=env,
                output_path=dockerfile_path
            )
            generated_files[filename] = dockerfile_content

        # Generate docker-compose files
        compose_environments = [
            (EnvironmentType.DEVELOPMENT, "docker-compose.yml"),
            (EnvironmentType.TESTING, "docker-compose.test.yml"),
            (EnvironmentType.PRODUCTION, "docker-compose.prod.yml")
        ]

        for env, filename in compose_environments:
            compose_path = output_dir / filename
            compose_content = self.generate_docker_compose(
                environment=env,
                project_type=project_type,
                output_path=compose_path
            )
            generated_files[filename] = compose_content

        # Generate additional configuration files
        generated_files.update(self._generate_additional_configs(output_dir, project_type))

        # Generate development scripts
        generated_files.update(self._generate_dev_scripts(output_dir, project_type))

        self.logger.info(f"Generated complete development environment in {output_dir}")
        return generated_files

    def _generate_additional_configs(self, output_dir: Path, project_type: ProjectType) -> Dict[str, str]:
        """Generate additional configuration files."""
        configs = {}

        # .dockerignore file
        dockerignore_content = '''# Dependencies
node_modules/
venv/
env/
.env
__pycache__/
*.pyc
.pytest_cache/
.coverage

# Build outputs
dist/
build/
target/
*.jar
*.war

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Git
.git/
.gitignore

# Docker
Dockerfile*
docker-compose*.yml

# Logs
*.log
logs/

# Temporary files
tmp/
temp/
*.tmp

# Database files
*.db
*.sqlite
*.sqlite3

# Secrets and keys
*.key
*.pem
*.crt
secrets/
'''

        dockerignore_path = output_dir / ".dockerignore"
        dockerignore_path.write_text(dockerignore_content)
        configs[".dockerignore"] = dockerignore_content

        # Health check script
        healthcheck_content = '''#!/bin/bash
# Health check script

set -e

# Check if application is responding
if command -v curl &> /dev/null; then
    curl -f http://localhost:${PORT:-8000}/health
elif command -v wget &> /dev/null; then
    wget --no-verbose --tries=1 --spider http://localhost:${PORT:-8000}/health
else
    echo "Neither curl nor wget is available for health check"
    exit 1
fi
'''

        healthcheck_path = output_dir / "healthcheck.sh"
        healthcheck_path.write_text(healthcheck_content)
        healthcheck_path.chmod(0o755)
        configs["healthcheck.sh"] = healthcheck_content

        # Environment template files
        env_dev_content = '''# Development environment variables
NODE_ENV=development
FLASK_ENV=development
DEBUG=true
LOG_LEVEL=debug

# Database
DATABASE_URL=postgresql://postgres:postgres@database:5432/myapp_dev

# Redis
REDIS_URL=redis://redis:6379/0

# Security (use strong values in production)
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET=dev-jwt-secret

# External services (development)
API_BASE_URL=http://localhost:3000
'''

        env_dev_path = output_dir / ".env.development"
        env_dev_path.write_text(env_dev_content)
        configs[".env.development"] = env_dev_content

        return configs

    def _generate_dev_scripts(self, output_dir: Path, project_type: ProjectType) -> Dict[str, str]:
        """Generate development helper scripts."""
        scripts = {}
        scripts_dir = output_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)

        # Development startup script
        dev_up_content = '''#!/bin/bash
# Start development environment

set -e

echo "🚀 Starting development environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build and start services
docker-compose -f docker-compose.yml up --build -d

echo "✅ Development environment started!"
echo "📱 Application: http://localhost:3000"
echo "🗄️  Database: localhost:5432"
echo "📊 Logs: docker-compose logs -f"
'''

        dev_up_path = scripts_dir / "dev-up.sh"
        dev_up_path.write_text(dev_up_content)
        dev_up_path.chmod(0o755)
        scripts["scripts/dev-up.sh"] = dev_up_content

        # Development teardown script
        dev_down_content = '''#!/bin/bash
# Stop development environment

set -e

echo "🛑 Stopping development environment..."

docker-compose -f docker-compose.yml down

if [ "$1" = "--volumes" ]; then
    echo "🗑️  Removing volumes..."
    docker-compose -f docker-compose.yml down -v
fi

echo "✅ Development environment stopped!"
'''

        dev_down_path = scripts_dir / "dev-down.sh"
        dev_down_path.write_text(dev_down_content)
        dev_down_path.chmod(0o755)
        scripts["scripts/dev-down.sh"] = dev_down_content

        # Test runner script
        test_content = '''#!/bin/bash
# Run tests in Docker

set -e

echo "🧪 Running tests..."

docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# Cleanup
docker-compose -f docker-compose.test.yml down

echo "✅ Tests completed!"
'''

        test_path = scripts_dir / "test.sh"
        test_path.write_text(test_content)
        test_path.chmod(0o755)
        scripts["scripts/test.sh"] = test_content

        # Production deployment script
        deploy_content = '''#!/bin/bash
# Deploy to production

set -e

echo "🚀 Deploying to production..."

# Build production image
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d

echo "✅ Production deployment completed!"
echo "🌐 Application: http://localhost"
'''

        deploy_path = scripts_dir / "deploy.sh"
        deploy_path.write_text(deploy_content)
        deploy_path.chmod(0o755)
        scripts["scripts/deploy.sh"] = deploy_content

        return scripts

    def setup_project_containerization(
        self,
        project_path: Optional[str] = None,
        project_type: Optional[ProjectType] = None,
        force: bool = False
    ) -> bool:
        """Set up containerization for an existing project."""
        if project_path:
            project_path = Path(project_path)
        else:
            project_path = self.project_root

        # Check if Docker files already exist
        docker_files = [
            project_path / "Dockerfile",
            project_path / "docker-compose.yml",
            project_path / "docker" / "Dockerfile.dev"
        ]

        if not force and any(f.exists() for f in docker_files):
            self.logger.warning("Docker files already exist. Use force=True to overwrite.")
            return False

        # Detect project type if not provided
        if project_type is None:
            original_root = self.project_root
            self.project_root = project_path
            project_type = self.detect_project_type()
            self.project_root = original_root

        # Generate development environment
        docker_dir = project_path / "docker"
        try:
            self.generate_development_environment(
                project_type=project_type,
                output_dir=docker_dir
            )

            # Copy main Dockerfile to project root
            main_dockerfile = docker_dir / "Dockerfile.dev"
            if main_dockerfile.exists():
                shutil.copy2(main_dockerfile, project_path / "Dockerfile")

            # Copy main docker-compose to project root
            main_compose = docker_dir / "docker-compose.yml"
            if main_compose.exists():
                shutil.copy2(main_compose, project_path / "docker-compose.yml")

            self.logger.info(f"Successfully set up containerization for {project_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to set up containerization: {e}")
            return False

    def validate_docker_setup(self, project_path: Optional[str] = None) -> Dict[str, Any]:
        """Validate Docker setup for a project."""
        if project_path:
            project_path = Path(project_path)
        else:
            project_path = self.project_root

        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'recommendations': []
        }

        # Check for required files
        required_files = [
            'Dockerfile',
            'docker-compose.yml',
            '.dockerignore'
        ]

        for filename in required_files:
            file_path = project_path / filename
            if not file_path.exists():
                validation_results['errors'].append(f"Missing required file: {filename}")
                validation_results['valid'] = False

        # Check Docker file syntax
        dockerfile_path = project_path / "Dockerfile"
        if dockerfile_path.exists():
            try:
                dockerfile_content = dockerfile_path.read_text()
                if not dockerfile_content.strip().startswith('FROM'):
                    validation_results['errors'].append("Dockerfile must start with FROM instruction")
                    validation_results['valid'] = False
            except Exception as e:
                validation_results['errors'].append(f"Error reading Dockerfile: {e}")
                validation_results['valid'] = False

        # Check docker-compose syntax
        compose_path = project_path / "docker-compose.yml"
        if compose_path.exists():
            try:
                import yaml
                compose_content = compose_path.read_text()
                yaml.safe_load(compose_content)
            except yaml.YAMLError as e:
                validation_results['errors'].append(f"Invalid docker-compose.yml syntax: {e}")
                validation_results['valid'] = False
            except Exception as e:
                validation_results['errors'].append(f"Error reading docker-compose.yml: {e}")
                validation_results['valid'] = False

        # Check for common issues
        if dockerfile_path.exists():
            dockerfile_content = dockerfile_path.read_text()

            # Check for security issues
            if 'USER root' in dockerfile_content:
                validation_results['warnings'].append(
                    "Running as root user is not recommended for security"
                )

            # Check for health checks
            if 'HEALTHCHECK' not in dockerfile_content:
                validation_results['recommendations'].append(
                    "Consider adding a HEALTHCHECK instruction"
                )

            # Check for multi-stage builds for production
            if dockerfile_content.count('FROM') == 1:
                validation_results['recommendations'].append(
                    "Consider using multi-stage builds for smaller production images"
                )

        return validation_results

    def get_project_info(self, project_path: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a project's containerization setup."""
        if project_path:
            project_path = Path(project_path)
        else:
            project_path = self.project_root

        detected_type = self.detect_project_type(project_path)
        config = self.configurations.get(detected_type)

        # Check for existing Docker files
        docker_files = {}
        docker_file_paths = [
            'Dockerfile',
            'docker-compose.yml',
            '.dockerignore',
            'docker/Dockerfile.dev',
            'docker/Dockerfile.prod',
            'docker/docker-compose.test.yml'
        ]

        for file_path in docker_file_paths:
            full_path = project_path / file_path
            docker_files[file_path] = {
                'exists': full_path.exists(),
                'size': full_path.stat().st_size if full_path.exists() else 0
            }

        return {
            'project_path': str(project_path),
            'detected_type': detected_type.value,
            'configuration': {
                'base_image': config.base_image if config else None,
                'exposed_ports': config.exposed_ports if config else [],
                'dependencies_file': config.dependencies_file if config else None
            },
            'docker_files': docker_files,
            'validation': self.validate_docker_setup(project_path)
        }
