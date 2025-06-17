#!/usr/bin/env python
"""
Module Registration Script for StickForStats

This script automatically discovers and registers all available StickForStats modules
with the central module registry. It should be run during application initialization
to ensure that all modules are properly registered and available for use.
"""

import os
import sys
import importlib
import logging
import django
from django.apps import apps
from django.conf import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('module_registration')

def setup_django():
    """Setup Django environment if not already done."""
    if not settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stickforstats.settings')
        django.setup()
        logger.info("Django environment initialized")

def discover_and_register_modules():
    """
    Discover all StickForStats modules and register them with the registry.
    
    Returns:
        dict: Dictionary of registered modules
    """
    from stickforstats.core.registry import get_registry
    
    registry = get_registry()
    registered_modules = {}
    
    # Get all installed apps that are StickForStats modules
    for app_config in apps.get_app_configs():
        if app_config.name.startswith('stickforstats.'):
            module_name = app_config.name.split('.')[-1]
            module_info_path = f"{app_config.name}.module_info"
            
            try:
                # Try to import the module_info module
                logger.info(f"Attempting to import {module_info_path}")
                module_info = importlib.import_module(module_info_path)
                
                # Check if it has a register function
                if hasattr(module_info, 'register') and callable(module_info.register):
                    logger.info(f"Registering module: {module_name}")
                    module_info.register(registry)
                    registered_modules[module_name] = True
                else:
                    logger.warning(f"Module {module_name} has no register function in module_info.py")
                    registered_modules[module_name] = False
            except ImportError:
                logger.warning(f"No module_info.py found for {module_name}")
                registered_modules[module_name] = False
            except Exception as e:
                logger.error(f"Error registering module {module_name}: {str(e)}")
                registered_modules[module_name] = False
    
    # Log the results
    total_modules = len(registered_modules)
    successful_registrations = sum(1 for status in registered_modules.values() if status)
    
    logger.info(f"Module registration complete: {successful_registrations}/{total_modules} modules registered")
    logger.info(f"Registered modules: {list(registry.get_all_modules().keys())}")
    
    return registered_modules

def initialize_modules():
    """
    Initialize all registered modules.
    
    Returns:
        dict: Dictionary of module initialization results
    """
    from stickforstats.core.module_integration import get_integrator
    
    integrator = get_integrator()
    init_results = integrator.initialize_modules()
    
    # Log the results
    total_modules = len(init_results)
    ready_modules = sum(1 for status in init_results.values() if status == 'ready')
    
    logger.info(f"Module initialization complete: {ready_modules}/{total_modules} modules ready")
    
    return init_results

def main():
    """Main function to run the module registration process."""
    logger.info("Starting module registration process")
    
    # Setup Django environment
    setup_django()
    
    # Discover and register modules
    registered_modules = discover_and_register_modules()
    
    # Initialize modules
    init_results = initialize_modules()
    
    # Generate integration report
    from stickforstats.core.module_integration import generate_integration_report
    report = generate_integration_report()
    
    # Print summary
    logger.info(f"Module registry status: {report['registry_status']}")
    logger.info(f"Overall status: {report['status']}")
    
    if report['status'] == 'ERROR':
        logger.error("Errors encountered during module registration:")
        for error in report.get('errors', []):
            logger.error(f"- {error}")
    
    logger.info("Module registration process completed")
    
    return report

if __name__ == '__main__':
    report = main()
    
    # Exit with appropriate status code
    if report['status'] == 'ERROR':
        sys.exit(1)
    else:
        sys.exit(0)