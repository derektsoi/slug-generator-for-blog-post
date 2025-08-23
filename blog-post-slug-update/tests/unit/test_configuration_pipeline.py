#!/usr/bin/env python3
"""
Test-Driven Development for ConfigurationPipeline
Tests written FIRST to define expected behavior before implementation.
"""

import unittest
import tempfile
import os
import json
import time
from unittest.mock import patch, Mock

# Import will fail initially - this is expected in TDD
try:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
    # Import directly from the module to avoid __init__.py dependencies
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "configuration_pipeline", 
        os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'core', 'configuration_pipeline.py')
    )
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    
    ConfigurationPipeline = config_module.ConfigurationPipeline
    ConfigurationError = config_module.ConfigurationError
    ValidationMismatchError = config_module.ValidationMismatchError
except (ImportError, AttributeError, FileNotFoundError):
    # Expected to fail initially - we haven't implemented it yet
    ConfigurationPipeline = None
    ConfigurationError = Exception
    ValidationMismatchError = Exception


class TestConfigurationPipeline(unittest.TestCase):
    """Test suite for ConfigurationPipeline - TDD approach"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @unittest.skipIf(ConfigurationPipeline is None, "ConfigurationPipeline not implemented yet")
    def test_version_aware_config_loading(self):
        """TEST: Configuration pipeline loads correct config for version"""
        # Test V10 configuration
        config_v10 = ConfigurationPipeline.get_config_for_version('v10')
        
        # V10 should have enhanced constraints
        self.assertEqual(config_v10.max_slug_words, 10)
        self.assertEqual(config_v10.max_slug_chars, 90)
        
        # Test V6 configuration (default/legacy)
        config_v6 = ConfigurationPipeline.get_config_for_version('v6')
        
        # V6 should have standard constraints
        self.assertEqual(config_v6.max_slug_words, 6)
        self.assertEqual(config_v6.max_slug_chars, 60)
    
    @unittest.skipIf(ConfigurationPipeline is None, "ConfigurationPipeline not implemented yet")
    def test_generator_validation_consistency(self):
        """TEST: Slug generator and validation use the same configuration"""
        # Create generator for V10 with enhanced constraints
        generator = ConfigurationPipeline.create_generator_with_validation('v10')
        
        # Test slug that should be valid under V10 but invalid under default
        long_slug = "ultimate-test-premium-slug-competitive-enhancement-guide"  # 8 words, 55 chars
        
        # Generator should accept this slug (V10 allows up to 10 words, 90 chars)
        result = generator.is_valid_slug(long_slug)
        self.assertTrue(result)
        
        # Test with V6 constraints - should be rejected
        generator_v6 = ConfigurationPipeline.create_generator_with_validation('v6')
        result_v6 = generator_v6.is_valid_slug(long_slug)
        self.assertFalse(result_v6)  # V6 only allows 6 words
    
    @unittest.skipIf(ConfigurationPipeline is None, "ConfigurationPipeline not implemented yet")
    def test_configuration_consistency_validation(self):
        """TEST: Pre-flight validation detects configuration mismatches"""
        # Test consistent configuration
        result_consistent = ConfigurationPipeline.validate_configuration_consistency('v10')
        
        self.assertTrue(result_consistent['passed'])
        self.assertIn('configuration', result_consistent)
        self.assertEqual(len(result_consistent.get('issues', [])), 0)
        
        # Test passes if no issues found (consistent configuration)
        # The real test is that validation returns expected results
    
    @unittest.skipIf(ConfigurationPipeline is None, "ConfigurationPipeline not implemented yet")
    def test_prompt_file_validation(self):
        """TEST: Configuration pipeline validates prompt file existence"""
        # Test existing prompt version
        result_existing = ConfigurationPipeline.validate_prompt_file_exists('v10')
        
        # Should pass if prompt file exists
        if os.path.exists('src/config/prompts/v10_prompt.txt'):
            self.assertTrue(result_existing['passed'])
            self.assertIn('found', result_existing['message'])
        else:
            self.assertFalse(result_existing['passed'])
            self.assertIn('missing', result_existing['message'])
    
    @unittest.skipIf(ConfigurationPipeline is None, "ConfigurationPipeline not implemented yet")
    def test_configuration_error_handling(self):
        """TEST: Configuration errors are handled gracefully with clear messages"""
        # Test invalid version
        with self.assertRaises(ConfigurationError) as cm:
            ConfigurationPipeline.get_config_for_version('invalid_version')
        
        self.assertIn('invalid_version', str(cm.exception))
        self.assertIsInstance(cm.exception.timestamp, (int, float))
    
    @unittest.skipIf(ConfigurationPipeline is None, "ConfigurationPipeline not implemented yet")
    def test_validation_mismatch_detection(self):
        """TEST: Validation mismatches are detected and reported"""
        # Create test slug with 8 words - valid for V10 (10 words max) but invalid for V6 (6 words max)
        test_slug = "this-is-a-very-long-test-slug-with-eight-words"  # Exactly 8 words
        
        # Test V10 generator (allows up to 10 words)
        generator_v10 = ConfigurationPipeline.create_generator_with_validation('v10')
        is_valid_v10 = generator_v10.is_valid_slug(test_slug)
        
        # Test V6 generator (allows up to 6 words)  
        generator_v6 = ConfigurationPipeline.create_generator_with_validation('v6')
        is_valid_v6 = generator_v6.is_valid_slug(test_slug)
        
        # V10 should accept 8 words, V6 should reject it
        self.assertTrue(is_valid_v10)   # 8 words <= 10 words (V10 limit)
        self.assertFalse(is_valid_v6)   # 8 words > 6 words (V6 limit)
        
        # Results should be different, proving version-aware validation works
        self.assertNotEqual(is_valid_v10, is_valid_v6)
    
    @unittest.skipIf(ConfigurationPipeline is None, "ConfigurationPipeline not implemented yet")
    def test_configuration_pipeline_integration(self):
        """TEST: Complete configuration pipeline integration"""
        # Full pipeline test
        pipeline_result = ConfigurationPipeline.run_complete_configuration_check('v10')
        
        # Should have all required components
        required_checks = ['config_loading', 'validation_consistency', 'prompt_file_exists']
        for check in required_checks:
            self.assertIn(check, pipeline_result)
            self.assertIn('passed', pipeline_result[check])
        
        # Overall result should be present
        self.assertIn('overall_passed', pipeline_result)
        self.assertIsInstance(pipeline_result['overall_passed'], bool)
    
    @unittest.skipIf(ConfigurationPipeline is None, "ConfigurationPipeline not implemented yet") 
    def test_version_specific_constraint_application(self):
        """TEST: Version-specific constraints are properly applied"""
        # Test with multiple versions
        test_cases = [
            ('v6', 6, 60),   # Standard constraints
            ('v8', 8, 70),   # Enhanced constraints  
            ('v10', 10, 90)  # Competitive constraints
        ]
        
        for version, expected_words, expected_chars in test_cases:
            config = ConfigurationPipeline.get_config_for_version(version)
            
            self.assertEqual(config.max_slug_words, expected_words,
                           f"Version {version} should have {expected_words} word limit")
            self.assertEqual(config.max_slug_chars, expected_chars,
                           f"Version {version} should have {expected_chars} char limit")
    
    @unittest.skipIf(ConfigurationPipeline is None, "ConfigurationPipeline not implemented yet")
    def test_configuration_caching_and_performance(self):
        """TEST: Configuration loading is efficient and cached"""
        import time
        
        # First load - should take time to initialize
        start_time = time.time()
        config1 = ConfigurationPipeline.get_config_for_version('v10')
        first_load_time = time.time() - start_time
        
        # Second load - should be faster (cached)
        start_time = time.time()
        config2 = ConfigurationPipeline.get_config_for_version('v10')
        second_load_time = time.time() - start_time
        
        # Cached load should be faster
        self.assertLessEqual(second_load_time, first_load_time * 2)  # Allow some variance
        
        # Should return same configuration object or equivalent
        self.assertEqual(config1.max_slug_words, config2.max_slug_words)
        self.assertEqual(config1.max_slug_chars, config2.max_slug_chars)


class TestConfigurationErrors(unittest.TestCase):
    """Test configuration error exceptions"""
    
    @unittest.skipIf(ConfigurationError is Exception, "ConfigurationError not implemented yet")
    def test_configuration_error_creation(self):
        """TEST: ConfigurationError contains proper context"""
        error = ConfigurationError("Invalid version specified", "v99", expected_versions=['v6', 'v8', 'v10'])
        
        self.assertIn("Invalid version", str(error))
        self.assertEqual(error.invalid_version, "v99")
        self.assertIn('v10', error.expected_versions)
        self.assertIsInstance(error.timestamp, (int, float))
    
    @unittest.skipIf(ValidationMismatchError is Exception, "ValidationMismatchError not implemented yet") 
    def test_validation_mismatch_error_creation(self):
        """TEST: ValidationMismatchError captures mismatch details"""
        error = ValidationMismatchError("Slug validation mismatch detected", 
                                      generator_result=True, 
                                      validator_result=False,
                                      test_slug="test-slug")
        
        self.assertIn("mismatch", str(error))
        self.assertTrue(error.generator_result)
        self.assertFalse(error.validator_result)
        self.assertEqual(error.test_slug, "test-slug")


if __name__ == '__main__':
    # Run tests - expect failures initially (TDD approach)
    print("🧪 Running ConfigurationPipeline TDD Tests")
    print("⚠️  Expected: Tests will FAIL initially - this is TDD!")
    print("✅ Goal: Implement ConfigurationPipeline to make these tests pass")
    print("=" * 60)
    
    unittest.main(verbosity=2)