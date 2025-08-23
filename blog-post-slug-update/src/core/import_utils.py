#!/usr/bin/env python3
"""
Import utilities for handling both relative and absolute imports.
Extracted from Phase 2 components to eliminate code duplication.
"""

import importlib.util
import os
from typing import Any


def safe_import_module(module_name: str, file_name: str, relative_import_path: str = None) -> Any:
    """
    Safely import module with fallback for direct module loading.
    
    Args:
        module_name: Name for the module
        file_name: Python file name (e.g., "file_operations.py") 
        relative_import_path: Optional relative import path (e.g., ".file_operations")
        
    Returns:
        Imported module object
    """
    # Try relative import first
    if relative_import_path:
        try:
            module = __import__(relative_import_path, fromlist=[''])
            return module
        except ImportError:
            pass
    
    # Fallback to direct module loading (used by tests)
    spec = importlib.util.spec_from_file_location(
        module_name,
        os.path.join(os.path.dirname(__file__), file_name)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def import_from_core(module_name: str, *attribute_names: str) -> tuple:
    """
    Import specific attributes from core modules with fallback handling.
    
    Args:
        module_name: Core module name (without .py extension)
        *attribute_names: Names of attributes to import
        
    Returns:
        Tuple of imported attributes in order requested
    """
    try:
        # Try relative import
        module = __import__(f'.{module_name}', package='core', level=1)
    except ImportError:
        # Fallback to direct loading
        module = safe_import_module(
            module_name,
            f"{module_name}.py"
        )
    
    # Return requested attributes
    attributes = []
    for attr_name in attribute_names:
        attributes.append(getattr(module, attr_name))
    
    return tuple(attributes) if len(attributes) > 1 else attributes[0]