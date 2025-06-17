#!/usr/bin/env python
"""
Module Validation Debug Script
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
logger = logging.getLogger('validation_debug')

def setup_django():
    """Setup Django environment if not already done."""
    if not settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stickforstats.settings')
        django.setup()
        logger.info("Django environment initialized")

def debug_module_validation(module_name):
    """
    Debug validation for a specific module.
    
    Args:
        module_name: Name of the module to validate
    """
    from stickforstats.core.registry import get_registry
    from stickforstats.core.module_integration import get_integrator
    
    registry = get_registry()
    integrator = get_integrator()
    
    # Get module info
    module_info = registry.get_module(module_name)
    
    if not module_info:
        logger.error(f"Module {module_name} not found in registry")
        return
    
    logger.info(f"Debugging validation for module: {module_name}")
    logger.info(f"Module info: {module_info}")
    
    # Check API namespace
    api_namespace = module_info.get('api_namespace')
    if api_namespace:
        logger.info(f"Checking API namespace: {api_namespace}")
        try:
            importlib.import_module(api_namespace)
            logger.info(f"API namespace {api_namespace} imported successfully")
        except ImportError as e:
            logger.error(f"Failed to import API namespace: {str(e)}")
            # Try to find the correct namespace
            possible_api_paths = []
            for app_config in apps.get_app_configs():
                if app_config.name.startswith(f'stickforstats.{module_name}'):
                    for root, dirs, files in os.walk(app_config.path):
                        for file in files:
                            if file == 'urls.py' and 'api' in root:
                                rel_path = os.path.relpath(os.path.join(root, file), 
                                                           os.path.dirname(app_config.path))
                                module_path = f"{app_config.name}.{rel_path.replace('/', '.').replace('.py', '')}"
                                possible_api_paths.append(module_path)
            
            if possible_api_paths:
                logger.info(f"Possible API namespaces found: {possible_api_paths}")
    
    # Check services
    services = module_info.get('services', {})
    for service_name, service_info in services.items():
        service_path = service_info.get('service')
        if service_path:
            logger.info(f"Checking service: {service_name} ({service_path})")
            try:
                module_path, class_name = service_path.rsplit('.', 1)
                module = importlib.import_module(module_path)
                service_class = getattr(module, class_name)
                logger.info(f"Service {service_name} found and loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load service {service_name}: {str(e)}")
                # Try to find the correct service class
                class_found = False
                for app_config in apps.get_app_configs():
                    if app_config.name.startswith(f'stickforstats.{module_name}'):
                        for root, dirs, files in os.walk(app_config.path):
                            for file in files:
                                if file.endswith('.py') and class_name.lower() in file.lower():
                                    logger.info(f"Possible service file found: {os.path.join(root, file)}")
                                    try:
                                        rel_path = os.path.relpath(os.path.join(root, file), 
                                                                 os.path.dirname(app_config.path))
                                        module_path = f"{app_config.name}.{rel_path.replace('/', '.').replace('.py', '')}"
                                        test_module = importlib.import_module(module_path)
                                        
                                        # Check for similar class names
                                        for attr_name in dir(test_module):
                                            if attr_name.lower() == class_name.lower() or \
                                               (class_name.lower() in attr_name.lower() and 'service' in attr_name.lower()):
                                                logger.info(f"Possible service class found: {module_path}.{attr_name}")
                                                class_found = True
                                    except Exception as e:
                                        logger.warning(f"Error checking possible service file: {str(e)}")
                
                if not class_found:
                    logger.warning(f"No possible service class found for {service_name}")

def main():
    """Main function."""
    # Setup Django environment
    setup_django()
    
    # Get all modules to debug
    from stickforstats.core.registry import get_registry
    registry = get_registry()
    
    # Check if we should debug specific modules or all
    if len(sys.argv) > 1:
        module_names = sys.argv[1:]
    else:
        # Debug all registered modules
        module_names = registry.get_all_modules().keys()
    
    for module_name in module_names:
        debug_module_validation(module_name)

if __name__ == '__main__':
    main()