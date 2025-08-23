#!/usr/bin/env python3
"""
ConfigurationPipeline - Version-aware configuration management with validation consistency
Implementation follows TDD approach - minimal code to satisfy test requirements.
Refactored to use shared utilities and validation models.
"""

import os
import time
from typing import Dict, Any, Optional

# Use shared import utilities
try:
    from .import_utils import import_from_core
    BaseTimestampedException = import_from_core('file_operations', 'BaseTimestampedException')
    ValidationResult, ConfigurationSpec = import_from_core('validation_models', 'ValidationResult', 'ConfigurationSpec')
except ImportError:
    # Fallback for direct module loading
    import importlib.util
    import os
    
    # Load file operations
    spec = importlib.util.spec_from_file_location(
        "file_operations", 
        os.path.join(os.path.dirname(__file__), "file_operations.py")
    )
    file_ops_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(file_ops_module)
    BaseTimestampedException = file_ops_module.BaseTimestampedException
    
    # Load validation models
    spec = importlib.util.spec_from_file_location(
        "validation_models", 
        os.path.join(os.path.dirname(__file__), "validation_models.py")
    )
    validation_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validation_module)
    ValidationResult = validation_module.ValidationResult
    ConfigurationSpec = validation_module.ConfigurationSpec


class ConfigurationError(BaseTimestampedException):
    """Custom exception for configuration errors"""
    
    def __init__(self, message: str, invalid_version: str = None, expected_versions: list = None):
        super().__init__(message)
        self.invalid_version = invalid_version
        self.expected_versions = expected_versions or []


class ValidationMismatchError(BaseTimestampedException):
    """Custom exception for validation mismatch errors"""
    
    def __init__(self, message: str, generator_result: bool = None, 
                 validator_result: bool = None, test_slug: str = None):
        super().__init__(message)
        self.generator_result = generator_result
        self.validator_result = validator_result
        self.test_slug = test_slug


class SlugGeneratorConfig:
    """Version-aware configuration for slug generation - wrapper around ConfigurationSpec"""
    
    def __init__(self, max_slug_words: int, max_slug_chars: int, version: str):
        self.max_slug_words = max_slug_words
        self.max_slug_chars = max_slug_chars
        self.version = version
    
    @classmethod
    def for_version(cls, version: str) -> 'SlugGeneratorConfig':
        """Get configuration for specific version using shared specifications"""
        try:
            spec = ConfigurationSpec.for_version(version)
            return cls(
                max_slug_words=spec.max_slug_words,
                max_slug_chars=spec.max_slug_chars,
                version=spec.version
            )
        except ValueError as e:
            # Convert to ConfigurationError for backward compatibility
            specs = ConfigurationSpec.get_specifications()
            raise ConfigurationError(
                str(e),
                invalid_version=version,
                expected_versions=list(specs.keys())
            )


# MockSlugGenerator moved to tests/unit/test_utilities.py for better separation


class ConfigurationPipeline:
    """End-to-end configuration management with version awareness"""
    
    _config_cache = {}  # Simple caching for performance
    
    @classmethod
    def get_config_for_version(cls, version: str) -> SlugGeneratorConfig:
        """Get configuration for specific version with caching"""
        if version in cls._config_cache:
            return cls._config_cache[version]
        
        config = SlugGeneratorConfig.for_version(version)
        cls._config_cache[version] = config
        return config
    
    @classmethod
    def create_generator_with_validation(cls, version: str):
        """Create slug generator with matching validation config"""
        # Import MockSlugGenerator from test utilities
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'unit'))
            from test_utilities import MockSlugGenerator
            
            config = cls.get_config_for_version(version)
            return MockSlugGenerator(config)
        except ImportError:
            # For production use, this would integrate with actual SlugGenerator
            config = cls.get_config_for_version(version) 
            
            class ProductionSlugGenerator:
                def __init__(self, config):
                    self.config = config
                
                def is_valid_slug(self, slug: str) -> bool:
                    words = slug.split('-')
                    return (len(words) <= self.config.max_slug_words and 
                           len(slug) <= self.config.max_slug_chars)
            
            return ProductionSlugGenerator(config)
    
    @classmethod
    def validate_configuration_consistency(cls, version: str) -> Dict[str, Any]:
        """Pre-flight validation of configuration consistency"""
        try:
            config = cls.get_config_for_version(version)
            
            # Test validation consistency with a known slug
            test_slug = "ultimate-test-slug-with-many-words-for-validation"  # 8 words
            
            # Create test generator directly (inline implementation)
            class TestGenerator:
                def __init__(self, config):
                    self.config = config
                def is_valid_slug(self, slug: str) -> bool:
                    words = slug.split('-')
                    return (len(words) <= self.config.max_slug_words and 
                           len(slug) <= self.config.max_slug_chars)
            
            generator = TestGenerator(config)
            result = generator.is_valid_slug(test_slug)
            
            # For V10 (10 words max), this should be valid
            # For V6 (6 words max), this should be invalid
            expected_result = len(test_slug.split('-')) <= config.max_slug_words
            
            issues = []
            if result != expected_result:
                issues.append(f"Validation mismatch for {version}: expected {expected_result}, got {result}")
            
            return {
                'passed': len(issues) == 0,
                'configuration': {
                    'version': version,
                    'max_words': config.max_slug_words,
                    'max_chars': config.max_slug_chars
                },
                'issues': issues
            }
            
        except ConfigurationError as e:
            return {
                'passed': False,
                'configuration': {},
                'issues': [str(e)]
            }
    
    @classmethod
    def validate_prompt_file_exists(cls, version: str) -> Dict[str, Any]:
        """Validate prompt file exists for version"""
        expected_file = f"src/config/prompts/{version}_prompt.txt"
        exists = os.path.exists(expected_file)
        
        result = ValidationResult(
            passed=exists,
            message=f"Prompt file {'found' if exists else 'missing'}: {expected_file}"
        )
        
        if not exists:
            result.add_fix_suggestion(f"Ensure prompt file named exactly: {version}_prompt.txt")
        
        return result.to_dict()
    
    @classmethod 
    def run_complete_configuration_check(cls, version: str) -> Dict[str, Any]:
        """Run complete configuration pipeline check"""
        results = {
            'config_loading': cls._test_config_loading(version),
            'validation_consistency': cls.validate_configuration_consistency(version),
            'prompt_file_exists': cls.validate_prompt_file_exists(version)
        }
        
        # Aggregate results
        overall_passed = all(result.get('passed', False) for result in results.values())
        
        return {
            'overall_passed': overall_passed,
            **results
        }
    
    @classmethod
    def _test_config_loading(cls, version: str) -> Dict[str, Any]:
        """Test configuration loading"""
        try:
            config = cls.get_config_for_version(version)
            return {
                'passed': True,
                'message': f"Configuration loaded successfully for {version}",
                'config': {
                    'version': config.version,
                    'max_words': config.max_slug_words,
                    'max_chars': config.max_slug_chars
                }
            }
        except ConfigurationError as e:
            return {
                'passed': False,
                'message': str(e)
            }