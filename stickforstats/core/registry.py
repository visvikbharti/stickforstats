"""
Simplified Module Registry System for minimal testing
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class ModuleRegistry:
    """Simplified registry for StickForStats modules."""

    def __init__(self):
        self.modules = {}

    def register_module(self, module_name: str, module_info: Dict[str, Any]) -> None:
        """Register a new module with the registry."""
        self.modules[module_name] = module_info
        logger.info(f"Module {module_name} registered")

    def get_module(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific module."""
        return self.modules.get(module_name)

    def get_all_modules(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered modules."""
        return self.modules

# Create singleton instance
registry = ModuleRegistry()

def autodiscover_modules():
    """Stub for autodiscovery - disabled for simplified testing."""
    logger.info("Module autodiscovery is disabled for simplified testing")
    return

# Convenience methods for interacting with the registry
def get_registry() -> ModuleRegistry:
    """Get the module registry singleton instance."""
    return registry

def register_module(module_name: str, module_info: Dict[str, Any]) -> None:
    """Register a module with the registry."""
    registry.register_module(module_name, module_info)

def get_module(module_name: str) -> Optional[Dict[str, Any]]:
    """Get information about a specific module."""
    return registry.get_module(module_name)

def get_all_modules() -> Dict[str, Dict[str, Any]]:
    """Get information about all registered modules."""
    return registry.get_all_modules()

# Import module_integration here to avoid circular import
def get_integrator():
    """Get the module integrator singleton instance."""
    # Dynamic import to avoid circular import
    from .module_integration import module_integrator
    return module_integrator

# Export module_registry for backward compatibility
module_registry = registry