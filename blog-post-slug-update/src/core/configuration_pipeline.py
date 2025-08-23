#!/usr/bin/env python3
"""
ConfigurationPipeline - Version-aware configuration management with validation consistency
Implementation follows TDD approach - minimal code to satisfy test requirements.
"""

import os
import time
from typing import Dict, Any, Optional

# Handle both relative and absolute imports for test compatibility
try:
    from .file_operations import BaseTimestampedException
except ImportError:
    # Fallback for direct module loading (used by tests)
    import importlib.util
    import os
    spec = importlib.util.spec_from_file_location(
        "file_operations", 
        os.path.join(os.path.dirname(__file__), "file_operations.py")
    )
    file_ops_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(file_ops_module)
    BaseTimestampedException = file_ops_module.BaseTimestampedException


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
    """Version-aware configuration for slug generation"""
    
    def __init__(self, max_slug_words: int, max_slug_chars: int, version: str):
        self.max_slug_words = max_slug_words
        self.max_slug_chars = max_slug_chars
        self.version = version
    
    @classmethod
    def for_version(cls, version: str) -> 'SlugGeneratorConfig':
        """Get configuration for specific version"""
        version_configs = {
            'v6': cls(max_slug_words=6, max_slug_chars=60, version='v6'),
            'v8': cls(max_slug_words=8, max_slug_chars=70, version='v8'), 
            'v10': cls(max_slug_words=10, max_slug_chars=90, version='v10')
        }
        
        if version not in version_configs:
            raise ConfigurationError(
                f"Invalid version specified: {version}",
                invalid_version=version,
                expected_versions=list(version_configs.keys())
            )
        
        return version_configs[version]


class MockSlugGenerator:
    """Mock slug generator for testing configuration pipeline"""
    
    def __init__(self, config: SlugGeneratorConfig):
        self.config = config
    
    def is_valid_slug(self, slug: str) -> bool:
        """Validate slug using version-specific constraints"""
        words = slug.split('-')
        
        if len(words) > self.config.max_slug_words:
            return False
        if len(slug) > self.config.max_slug_chars:
            return False
        
        return True


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
    def create_generator_with_validation(cls, version: str) -> MockSlugGenerator:
        """Create slug generator with matching validation config"""
        config = cls.get_config_for_version(version)
        return MockSlugGenerator(config)
    
    @classmethod
    def validate_configuration_consistency(cls, version: str) -> Dict[str, Any]:
        """Pre-flight validation of configuration consistency"""
        try:
            config = cls.get_config_for_version(version)
            
            # Test validation consistency with a known slug
            test_slug = "ultimate-test-slug-with-many-words-for-validation"  # 8 words
            
            generator = MockSlugGenerator(config)
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
        
        return {
            'passed': exists,
            'message': f"Prompt file {'found' if exists else 'missing'}: {expected_file}",
            'fix': f"Ensure prompt file named exactly: {version}_prompt.txt" if not exists else None
        }
    
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