# Module Registration System

## Overview

The StickForStats platform uses a module registration system to enable a modular architecture where statistical modules can be registered, discovered, and integrated at runtime. This document explains how this system works and how to add new modules to the platform.

## Architecture

The module registration system consists of several key components:

1. **Registry** - A centralized registry that keeps track of all modules and their capabilities
2. **Module Information Files** - Each module provides a `module_info.py` file that defines its capabilities and services
3. **Module Integrator** - Handles the validation, initialization, and integration of modules
4. **Auto-discovery** - Automatically discovers and registers modules during application startup

## Module Registration Flow

1. During Django application startup, the `CoreConfig.ready()` method is triggered
2. The method imports and registers the Core module first
3. It then discovers all StickForStats modules by scanning installed Django apps
4. For each discovered module, it tries to import its `module_info.py` file
5. If found, it calls the `register()` function in that file to register the module
6. The module integrator validates all registered modules
7. The module integrator initializes all validated modules

## Creating a New Module

### 1. Create Module Structure

Create a new Django app with the standard structure:

```
stickforstats/
└── your_module_name/
    ├── __init__.py
    ├── apps.py
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── api/
    │   ├── __init__.py
    │   ├── serializers.py
    │   ├── urls.py
    │   └── views.py
    ├── services/
    │   ├── __init__.py
    │   └── your_service.py
    └── module_info.py  # Key file for registration
```

### 2. Create Module Information File

The `module_info.py` file is the most important file for module registration. Here's a template:

```python
"""
Your Module Information

This module registers the Your Module with the central module registry.
"""

from typing import Dict, Any
from ..core.registry import ModuleRegistry

def register(registry: ModuleRegistry) -> None:
    """
    Register the Your Module with the registry.
    
    Args:
        registry: The module registry to register with
    """
    module_info = {
        'name': 'Your Module',
        'display_name': 'Your Module Display Name',
        'description': 'Description of what your module does.',
        'version': '1.0.0',
        'author': 'StickForStats Team',
        'entry_point': 'stickforstats.your_module.views.your_entry_point',
        'api_namespace': 'stickforstats.your_module.api.urls',
        'frontend_path': '/your-module',
        'capabilities': [
            'capability_1',
            'capability_2',
            'capability_3'
        ],
        'dependencies': ['core'],  # List modules this one depends on
        'icon': 'IconName',  # Material UI icon name
        'category': 'Your Category',
        'order': 50,  # Display order in navigation
        'enabled': True,
        'metadata': {
            'primary_color': '#HEXCOLOR',
            'supports_feature_1': True,
            'supports_feature_2': True
        },
        'services': {
            'your_service': {
                'service': 'stickforstats.your_module.services.your_service.YourService',
                'description': 'Description of your service'
            }
        },
        'documentation_url': '/docs/your-module',
        'tutorials': [
            {
                'title': 'Tutorial 1',
                'url': '/tutorials/your-module/tutorial-1'
            }
        ]
    }
    
    registry.register_module('your_module', module_info)
```

### 3. Update Django App Configuration

Ensure your module's `apps.py` is properly configured:

```python
from django.apps import AppConfig

class YourModuleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stickforstats.your_module'
    verbose_name = 'Your Module Name'
```

### 4. Add to INSTALLED_APPS

Add your module to `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    # ... existing apps
    'stickforstats.your_module.apps.YourModuleConfig',
]
```

## Manual Registration

If automatic registration fails, you can manually register modules using the `register_modules.py` script:

```bash
python register_modules.py
```

This script:
1. Sets up the Django environment
2. Discovers all StickForStats modules
3. Registers each module by importing its `module_info.py` file
4. Initializes the modules
5. Generates an integration report

## Module Information Structure

The module information dictionary can contain the following fields:

| Field | Description | Required |
|-------|-------------|----------|
| `name` | Internal name of the module | Yes |
| `display_name` | User-friendly display name | Yes |
| `description` | Detailed description of the module | Yes |
| `version` | Module version | Yes |
| `author` | Module author | Yes |
| `entry_point` | Function to call to initialize the module | No |
| `api_namespace` | Path to the module's API URLs | Yes |
| `frontend_path` | Frontend URL path for the module | Yes |
| `capabilities` | List of capabilities the module provides | Yes |
| `dependencies` | List of modules this module depends on | No |
| `icon` | Material UI icon name | No |
| `category` | Module category | Yes |
| `order` | Display order in navigation | No |
| `enabled` | Whether the module is enabled | Yes |
| `metadata` | Additional metadata | No |
| `services` | Dictionary of services provided by the module | Yes |
| `documentation_url` | URL to module documentation | No |
| `tutorials` | List of tutorials for the module | No |

## Troubleshooting

### Module Not Registered

If a module isn't being registered correctly:

1. Check that the module's `module_info.py` file exists
2. Ensure the `register` function is properly defined
3. Verify the module is included in `INSTALLED_APPS`
4. Run `python register_modules.py` to see detailed error messages

### Validation Errors

If a module fails validation:

1. Check the API namespace path - it should be importable
2. Verify service paths point to actual classes
3. Check that dependencies are registered
4. In development mode, set `DEBUG=True` for more lenient validation

### Dependency Errors

If you're encountering dependency issues:

1. Ensure all dependencies are listed in the `dependencies` field
2. Make sure dependencies are registered before dependent modules
3. Check for circular dependencies

## Module Registry API

### Core Registry Functions

```python
from stickforstats.core.registry import get_registry, register_module, get_module, get_all_modules

# Get registry singleton
registry = get_registry()

# Register a module
register_module('module_name', module_info)

# Get specific module info
module_info = get_module('module_name')

# Get all registered modules
all_modules = get_all_modules()
```

### Module Integrator Functions

```python
from stickforstats.core.module_integration import get_integrator, validate_modules, initialize_modules

# Get integrator singleton
integrator = get_integrator()

# Validate modules
validation_results = validate_modules()

# Initialize modules
initialization_results = initialize_modules()

# Generate report
report = integrator.generate_integration_report()

# Troubleshoot a specific module
details = integrator.troubleshoot_module('module_name')
```

## Conclusion

The module registration system provides a flexible architecture for extending the StickForStats platform with new statistical modules. By following the guidelines in this document, you can create and register new modules that seamlessly integrate with the platform.