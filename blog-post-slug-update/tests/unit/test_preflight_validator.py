#!/usr/bin/env python3
"""
Test-Driven Development for PreFlightValidator
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
        "preflight_validator", 
        os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'core', 'preflight_validator.py')
    )
    preflight_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(preflight_module)
    
    PreFlightValidator = preflight_module.PreFlightValidator
    ValidationFailureError = preflight_module.ValidationFailureError
except (ImportError, AttributeError, FileNotFoundError):
    # Expected to fail initially - we haven't implemented it yet
    PreFlightValidator = None
    ValidationFailureError = Exception


class TestPreFlightValidator(unittest.TestCase):
    """Test suite for PreFlightValidator - TDD approach"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @unittest.skipIf(PreFlightValidator is None, "PreFlightValidator not implemented yet")
    def test_comprehensive_preflight_validation(self):
        """TEST: Complete pre-flight validation covers all critical checks"""
        validator = PreFlightValidator(prompt_version='v10', output_dir=self.test_dir)
        
        result = validator.run_full_validation()
        
        # Should have all required validation components
        required_checks = [
            'prompt_config',
            'file_permissions', 
            'dependencies',
            'configuration_consistency',
            'resume_capability'
        ]
        
        for check in required_checks:
            self.assertIn(check, result['results'])
            self.assertIn('passed', result['results'][check])
            self.assertIn('message', result['results'][check])
        
        # Should have overall assessment
        self.assertIn('overall_passed', result)
        self.assertIn('recommendation', result)
        self.assertIn(result['recommendation'], ['PROCEED', 'FIX_ISSUES'])
    
    @unittest.skipIf(PreFlightValidator is None, "PreFlightValidator not implemented yet")
    def test_prompt_config_validation(self):
        """TEST: Prompt configuration validation detects missing files"""
        validator = PreFlightValidator(prompt_version='v10', output_dir=self.test_dir)
        
        # Test with existing prompt file
        result_existing = validator.validate_prompt_config()
        
        # Check if V10 prompt exists
        v10_prompt_path = 'src/config/prompts/v10_prompt.txt'
        if os.path.exists(v10_prompt_path):
            self.assertTrue(result_existing['passed'])
            self.assertIn('found', result_existing['message'])
            self.assertIn('v10_prompt.txt', result_existing['message'])
        else:
            self.assertFalse(result_existing['passed'])
            self.assertIn('missing', result_existing['message'])
            self.assertIn('fix', result_existing)
        
        # Test with non-existent prompt version
        validator_invalid = PreFlightValidator(prompt_version='v99', output_dir=self.test_dir)
        result_invalid = validator_invalid.validate_prompt_config()
        
        self.assertFalse(result_invalid['passed'])
        self.assertIn('missing', result_invalid['message'])
    
    @unittest.skipIf(PreFlightValidator is None, "PreFlightValidator not implemented yet")
    def test_file_permissions_validation(self):
        """TEST: File permissions validation ensures write access"""
        validator = PreFlightValidator(prompt_version='v10', output_dir=self.test_dir)
        
        result = validator.validate_file_permissions()
        
        # Should validate output directory write permissions
        self.assertIn('passed', result)
        self.assertIn('message', result)
        
        # Should pass for writable test directory
        self.assertTrue(result['passed'])
        
        # Test with read-only directory (simulate permission issue)
        readonly_dir = os.path.join(self.test_dir, 'readonly')
        os.makedirs(readonly_dir, exist_ok=True)
        os.chmod(readonly_dir, 0o444)  # Read-only
        
        validator_readonly = PreFlightValidator(prompt_version='v10', output_dir=readonly_dir)
        result_readonly = validator_readonly.validate_file_permissions()
        
        # Should detect permission issue
        self.assertFalse(result_readonly['passed'])
        self.assertIn('permission', result_readonly['message'].lower())
    
    @unittest.skipIf(PreFlightValidator is None, "PreFlightValidator not implemented yet")
    def test_dependencies_validation(self):
        """TEST: Dependencies validation checks for required modules"""
        validator = PreFlightValidator(prompt_version='v10', output_dir=self.test_dir)
        
        result = validator.validate_dependencies()
        
        # Should check for required dependencies
        self.assertIn('passed', result)
        self.assertIn('message', result)
        
        # Core dependencies should be available
        required_deps = ['json', 'os', 'openai']  # Basic requirements
        if result['passed']:
            self.assertIn('available', result['message'])
        else:
            self.assertIn('missing', result['message'])
            self.assertIn('dependencies', result)
    
    @unittest.skipIf(PreFlightValidator is None, "PreFlightValidator not implemented yet")
    def test_configuration_consistency_validation(self):
        """TEST: Configuration consistency validation detects mismatches"""
        validator = PreFlightValidator(prompt_version='v10', output_dir=self.test_dir)
        
        result = validator.validate_configuration_consistency()
        
        self.assertIn('passed', result)
        self.assertIn('message', result)
        
        if not result['passed']:
            self.assertIn('issues', result)
            self.assertIn('fix_suggestions', result)
    
    @unittest.skipIf(PreFlightValidator is None, "PreFlightValidator not implemented yet")
    def test_resume_capability_validation(self):
        """TEST: Resume capability validation checks checkpoint functionality"""
        validator = PreFlightValidator(prompt_version='v10', output_dir=self.test_dir)
        
        result = validator.validate_resume_capability()
        
        self.assertIn('passed', result)
        self.assertIn('message', result)
        
        # Should test checkpoint creation/loading
        if result['passed']:
            self.assertIn('checkpoint', result['message'].lower())
        else:
            self.assertIn('checkpoint', result['message'].lower())
            self.assertIn('fix', result)
    
    @unittest.skipIf(PreFlightValidator is None, "PreFlightValidator not implemented yet")
    def test_validation_failure_aggregation(self):
        """TEST: Multiple validation failures are properly aggregated"""
        # Create validator with conditions likely to fail
        invalid_dir = '/root/nonexistent_dir'  # Should fail permissions
        validator = PreFlightValidator(prompt_version='v99', output_dir=invalid_dir)
        
        result = validator.run_full_validation()
        
        # Should fail overall
        self.assertFalse(result['overall_passed'])
        self.assertEqual(result['recommendation'], 'FIX_ISSUES')
        
        # Should have multiple failures
        failed_checks = [check for check, res in result['results'].items() 
                        if not res.get('passed', True)]
        self.assertGreater(len(failed_checks), 0)
    
    @unittest.skipIf(PreFlightValidator is None, "PreFlightValidator not implemented yet")
    def test_validation_performance(self):
        """TEST: Pre-flight validation completes quickly"""
        validator = PreFlightValidator(prompt_version='v10', output_dir=self.test_dir)
        
        start_time = time.time()
        result = validator.run_full_validation()
        duration = time.time() - start_time
        
        # Should complete within reasonable time
        self.assertLess(duration, 5.0)  # 5 seconds max
        
        # Should still provide comprehensive results
        self.assertIn('overall_passed', result)
        self.assertIn('results', result)
    
    @unittest.skipIf(PreFlightValidator is None, "PreFlightValidator not implemented yet")
    def test_validation_with_mock_failures(self):
        """TEST: Validation handles individual component failures gracefully"""
        validator = PreFlightValidator(prompt_version='v10', output_dir=self.test_dir)
        
        # Mock one validation to fail
        with patch.object(validator, 'validate_dependencies') as mock_deps:
            mock_deps.return_value = {
                'passed': False,
                'message': 'Missing required dependency: openai',
                'fix': 'Run: pip install openai'
            }
            
            result = validator.run_full_validation()
            
            # Should still complete other validations
            self.assertIn('prompt_config', result['results'])
            self.assertIn('file_permissions', result['results'])
            
            # Should fail overall due to dependency issue
            self.assertFalse(result['overall_passed'])
            self.assertEqual(result['recommendation'], 'FIX_ISSUES')
    
    @unittest.skipIf(PreFlightValidator is None, "PreFlightValidator not implemented yet")
    def test_custom_validation_extensions(self):
        """TEST: Pre-flight validator supports custom validation extensions"""
        validator = PreFlightValidator(prompt_version='v10', output_dir=self.test_dir)
        
        # Test custom validation addition
        def custom_api_key_check():
            return {
                'passed': os.getenv('OPENAI_API_KEY') is not None,
                'message': 'API key check',
                'fix': 'Set OPENAI_API_KEY environment variable'
            }
        
        # Should be able to add custom validation
        if hasattr(validator, 'add_custom_validation'):
            validator.add_custom_validation('api_key_check', custom_api_key_check)
            
            result = validator.run_full_validation()
            self.assertIn('api_key_check', result['results'])


class TestValidationFailureError(unittest.TestCase):
    """Test validation failure error exception"""
    
    @unittest.skipIf(ValidationFailureError is Exception, "ValidationFailureError not implemented yet")
    def test_validation_failure_error_creation(self):
        """TEST: ValidationFailureError captures failure context"""
        failed_checks = ['prompt_config', 'file_permissions']
        error = ValidationFailureError("Pre-flight validation failed", 
                                     failed_checks=failed_checks,
                                     total_checks=5)
        
        self.assertIn("validation failed", str(error))
        self.assertEqual(error.failed_checks, failed_checks)
        self.assertEqual(error.total_checks, 5)
        self.assertEqual(error.failure_count, 2)
        self.assertIsInstance(error.timestamp, (int, float))


if __name__ == '__main__':
    # Run tests - expect failures initially (TDD approach)
    print("🧪 Running PreFlightValidator TDD Tests")
    print("⚠️  Expected: Tests will FAIL initially - this is TDD!")
    print("✅ Goal: Implement PreFlightValidator to make these tests pass")
    print("=" * 60)
    
    unittest.main(verbosity=2)