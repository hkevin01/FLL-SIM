"""
Error Handling Utility Module

Provides centralized exception handling and custom error types for FLL-Sim modules.
"""

class FLLSimError(Exception):
    """Base exception for FLL-Sim errors."""
    pass

class ConfigError(FLLSimError):
    """Exception for configuration-related errors."""
    pass

class PluginError(FLLSimError):
    """Exception for plugin-related errors."""
    pass

class I18nError(FLLSimError):
    """Exception for internationalization errors."""
    pass

class AccessibilityError(FLLSimError):
    """Exception for accessibility errors."""
    pass
