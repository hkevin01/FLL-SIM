"""
Enhanced Configuration Management System

Provides robust configuration loading, validation, and type-safe access
for robot parameters, sensor settings, and simulation physics.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import yaml

from ..utils.errors import ConfigError
from ..utils.logger import FLLLogger

T = TypeVar('T')


class ConfigValidator(ABC):
    """Abstract base class for configuration validators."""

    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate configuration data."""
        pass

    @abstractmethod
    def get_errors(self) -> List[str]:
        """Get validation error messages."""
        pass


class RobotConfigValidator(ConfigValidator):
    """Validator for robot configuration data."""

    def __init__(self):
        self.errors = []

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate robot configuration data."""
        self.errors.clear()

        # Required fields
        required_fields = [
            'width', 'length', 'mass', 'wheel_diameter', 'wheel_base'
        ]
        for required_field in required_fields:
            if required_field not in data:
                self.errors.append(f"Missing required field: {required_field}")
            elif not isinstance(data[required_field], (int, float)):
                self.errors.append(
                    f"Field '{required_field}' must be numeric"
                )
            elif data[required_field] <= 0:
                self.errors.append(
                    f"Field '{required_field}' must be positive"
                )

        # Validate physical constraints
        if 'width' in data and 'length' in data:
            if data['width'] > 500 or data['length'] > 500:
                self.errors.append(
                    "Robot dimensions exceed maximum allowed (500mm)"
                )

        if 'mass' in data:
            if data['mass'] > 10.0:
                self.errors.append(
                    "Robot mass exceeds maximum allowed (10kg)"
                )

        if 'max_speed' in data:
            if data['max_speed'] > 2000:
                self.errors.append(
                    "Maximum speed exceeds safe limit (2000 mm/s)"
                )

        return len(self.errors) == 0

    def get_errors(self) -> List[str]:
        """Get validation error messages."""
        return self.errors.copy()


class SensorConfigValidator(ConfigValidator):
    """Validator for sensor configuration data."""

    def __init__(self):
        self.errors = []
        self.valid_sensor_types = ['color', 'ultrasonic', 'gyro', 'touch']

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate sensor configuration data."""
        self.errors.clear()

        # Check sensor type
        if 'type' not in data:
            self.errors.append("Missing required field: type")
        elif data['type'] not in self.valid_sensor_types:
            self.errors.append(f"Invalid sensor type: {data['type']}")

        # Check position
        if 'position' in data:
            pos = data['position']
            if not isinstance(pos, (list, tuple)) or len(pos) != 2:
                self.errors.append("Position must be [x, y] coordinates")
            elif not all(isinstance(coord, (int, float)) for coord in pos):
                self.errors.append("Position coordinates must be numeric")

        # Check port
        if 'port' in data:
            if not isinstance(data['port'], str):
                self.errors.append("Port must be a string")
            elif data['port'] not in [
                'S1', 'S2', 'S3', 'S4', '1', '2', '3', '4'
            ]:
                self.errors.append("Invalid port specification")

        return len(self.errors) == 0

    def get_errors(self) -> List[str]:
        """Get validation error messages."""
        return self.errors.copy()


class PhysicsConfigValidator(ConfigValidator):
    """Validator for physics configuration data."""

    def __init__(self):
        self.errors = []

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate physics configuration data."""
        self.errors.clear()

        # Check FPS
        if 'physics_fps' in data:
            fps = data['physics_fps']
            if not isinstance(fps, int) or fps <= 0 or fps > 240:
                self.errors.append("physics_fps must be between 1 and 240")

        # Check gravity
        if 'gravity' in data:
            gravity = data['gravity']
            if not isinstance(gravity, (list, tuple)) or len(gravity) != 2:
                self.errors.append("gravity must be [x, y] vector")

        # Check real-time factor
        if 'real_time_factor' in data:
            factor = data['real_time_factor']
            if (not isinstance(factor, (int, float)) or
                    factor <= 0 or factor > 10):
                self.errors.append(
                    "real_time_factor must be between 0 and 10"
                )

        return len(self.errors) == 0

    def get_errors(self) -> List[str]:
        """Get validation error messages."""
        return self.errors.copy()


@dataclass
class ConfigSchema:
    """Schema definition for configuration validation."""
    validator: ConfigValidator
    required_version: str = "1.0"
    description: str = ""


class TypeSafeConfigLoader:
    """Type-safe configuration loader with validation."""

    def __init__(self):
        self.logger = FLLLogger('TypeSafeConfigLoader')
        self.schemas: Dict[str, ConfigSchema] = {}
        self._register_default_schemas()

    def _register_default_schemas(self):
        """Register default configuration schemas."""
        self.schemas['robot'] = ConfigSchema(
            validator=RobotConfigValidator(),
            description="Robot physical and motor configuration"
        )
        self.schemas['sensor'] = ConfigSchema(
            validator=SensorConfigValidator(),
            description="Sensor configuration and positioning"
        )
        self.schemas['physics'] = ConfigSchema(
            validator=PhysicsConfigValidator(),
            description="Physics simulation parameters"
        )

    def register_schema(self, name: str, schema: ConfigSchema):
        """Register a custom configuration schema."""
        self.schemas[name] = schema
        self.logger.info(f"Registered configuration schema: {name}")

    def load_config(self, file_path: Union[str, Path],
                    schema_name: Optional[str] = None,
                    data_class: Optional[Type[T]] = None
                    ) -> Union[Dict[str, Any], T]:
        """
        Load and validate configuration from file.

        Args:
            file_path: Path to configuration file (YAML or JSON)
            schema_name: Name of schema to validate against
            data_class: Dataclass to deserialize into

        Returns:
            Configuration data as dict or dataclass instance

        Raises:
            ConfigError: If file cannot be loaded or validation fails
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise ConfigError(f"Configuration file not found: {file_path}")

        try:
            # Load file based on extension
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                raise ConfigError(f"Unsupported file format: {file_path.suffix}")

            if data is None:
                raise ConfigError(f"Empty configuration file: {file_path}")

            # Validate against schema if provided
            if schema_name:
                self._validate_config(data, schema_name)

            # Convert to dataclass if requested
            if data_class:
                try:
                    return data_class(**data)
                except TypeError as e:
                    raise ConfigError(f"Failed to create {data_class.__name__}: {e}")

            self.logger.info(f"Successfully loaded configuration from {file_path}")
            return data

        except yaml.YAMLError as e:
            raise ConfigError(f"YAML parsing error in {file_path}: {e}")
        except json.JSONDecodeError as e:
            raise ConfigError(f"JSON parsing error in {file_path}: {e}")
        except Exception as e:
            raise ConfigError(f"Failed to load configuration from {file_path}: {e}")

    def save_config(self, data: Union[Dict[str, Any], Any],
                   file_path: Union[str, Path],
                   schema_name: Optional[str] = None):
        """
        Save configuration to file with validation.

        Args:
            data: Configuration data or dataclass instance
            file_path: Path to save configuration file
            schema_name: Name of schema to validate against

        Raises:
            ConfigError: If validation fails or file cannot be saved
        """
        file_path = Path(file_path)

        # Convert dataclass to dict if needed
        if hasattr(data, '__dataclass_fields__'):
            data = asdict(data)

        # Validate against schema if provided
        if schema_name:
            self._validate_config(data, schema_name)

        try:
            # Create parent directory if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Save file based on extension
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, sort_keys=False)
            else:
                raise ConfigError(f"Unsupported file format: {file_path.suffix}")

            self.logger.info(f"Successfully saved configuration to {file_path}")

        except Exception as e:
            raise ConfigError(f"Failed to save configuration to {file_path}: {e}")

    def _validate_config(self, data: Dict[str, Any], schema_name: str):
        """Validate configuration data against schema."""
        if schema_name not in self.schemas:
            raise ConfigError(f"Unknown schema: {schema_name}")

        schema = self.schemas[schema_name]
        if not schema.validator.validate(data):
            errors = schema.validator.get_errors()
            error_msg = f"Configuration validation failed for schema '{schema_name}':\n"
            error_msg += "\n".join(f"  - {error}" for error in errors)
            raise ConfigError(error_msg)

    def get_available_schemas(self) -> Dict[str, str]:
        """Get list of available schemas with descriptions."""
        return {name: schema.description for name, schema in self.schemas.items()}


class ConfigProfileManager:
    """Manages configuration profiles and environments."""

    def __init__(self, config_dir: Union[str, Path]):
        self.config_dir = Path(config_dir)
        self.logger = FLLLogger('ConfigProfileManager')
        self.loader = TypeSafeConfigLoader()
        self.active_profile = None

    def create_profile(self, name: str, description: str = ""):
        """Create a new configuration profile."""
        profile_dir = self.config_dir / "profiles" / name
        profile_dir.mkdir(parents=True, exist_ok=True)

        # Create profile metadata
        metadata = {
            'name': name,
            'description': description,
            'created_at': str(Path().ctime()),
            'version': '1.0'
        }

        self.loader.save_config(metadata, profile_dir / "profile.yaml")
        self.logger.info(f"Created configuration profile: {name}")

    def load_profile(self, name: str) -> Dict[str, Any]:
        """Load a configuration profile."""
        profile_dir = self.config_dir / "profiles" / name
        if not profile_dir.exists():
            raise ConfigError(f"Profile not found: {name}")

        metadata_file = profile_dir / "profile.yaml"
        if not metadata_file.exists():
            raise ConfigError(f"Profile metadata not found: {metadata_file}")

        profile_data = self.loader.load_config(metadata_file)

        # Load all configuration files in profile
        config_files = {}
        for config_file in profile_dir.glob("*.yaml"):
            if config_file.name != "profile.yaml":
                config_name = config_file.stem
                config_files[config_name] = self.loader.load_config(config_file)

        profile_data['configs'] = config_files
        self.active_profile = name
        self.logger.info(f"Loaded configuration profile: {name}")
        return profile_data

    def save_profile_config(self, profile_name: str, config_name: str,
                           data: Dict[str, Any], schema_name: Optional[str] = None):
        """Save a configuration to a profile."""
        profile_dir = self.config_dir / "profiles" / profile_name
        if not profile_dir.exists():
            raise ConfigError(f"Profile not found: {profile_name}")

        config_file = profile_dir / f"{config_name}.yaml"
        self.loader.save_config(data, config_file, schema_name)
        self.logger.info(f"Saved {config_name} configuration to profile {profile_name}")

    def list_profiles(self) -> List[Dict[str, str]]:
        """List all available configuration profiles."""
        profiles = []
        profiles_dir = self.config_dir / "profiles"

        if profiles_dir.exists():
            for profile_dir in profiles_dir.iterdir():
                if profile_dir.is_dir():
                    metadata_file = profile_dir / "profile.yaml"
                    if metadata_file.exists():
                        try:
                            metadata = self.loader.load_config(metadata_file)
                            profiles.append({
                                'name': metadata.get('name', profile_dir.name),
                                'description': metadata.get('description', ''),
                                'path': str(profile_dir)
                            })
                        except Exception as e:
                            self.logger.warning(f"Failed to load profile metadata from {metadata_file}: {e}")

        return profiles

    def delete_profile(self, name: str):
        """Delete a configuration profile."""
        profile_dir = self.config_dir / "profiles" / name
        if not profile_dir.exists():
            raise ConfigError(f"Profile not found: {name}")

        import shutil
        shutil.rmtree(profile_dir)
        self.logger.info(f"Deleted configuration profile: {name}")
