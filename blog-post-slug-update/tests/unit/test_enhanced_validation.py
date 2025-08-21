#!/usr/bin/env python3
"""
Tests for Enhanced Pre-Flight Validation System
Validates all V10 development enhancements addressing V9 insights
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from core.pre_flight_validator import create_enhanced_validator, EnhancedPreFlightValidator
from core.exceptions import ValidationError, ConfigurationError
from config.settings import SlugGeneratorConfig


@pytest.mark.validation
class TestEnhancedPreFlightValidator:
    """Test enhanced pre-flight validation system"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.validator = create_enhanced_validator(dev_mode=True)
    
    def test_validator_creation(self):
        """Test enhanced validator can be created"""
        validator = create_enhanced_validator(dev_mode=True)
        assert isinstance(validator, EnhancedPreFlightValidator)
        assert validator.dev_mode == True
        
        validator_prod = create_enhanced_validator(dev_mode=False)
        assert validator_prod.dev_mode == False
    
    def test_rapid_validation_success(self):
        """Test rapid validation returns True for valid setup"""
        with patch.object(self.validator, '_validate_version_mapping', return_value=True), \
             patch.object(Path, 'exists', return_value=True), \
             patch.object(self.validator, '_is_api_available', return_value=True), \
             patch.object(self.validator, '_get_prompt_content', return_value="Generate SEO slugs in JSON format"), \
             patch.object(self.validator, '_has_json_format_requirement', return_value=True):
            
            result = self.validator.rapid_validation('v10')
            assert result == True
    
    def test_rapid_validation_failure(self):
        """Test rapid validation returns False for invalid setup"""
        with patch.object(self.validator, '_validate_version_mapping', return_value=False):
            result = self.validator.rapid_validation('invalid_version')
            assert result == False


@pytest.mark.validation
class TestJSONCompatibilityValidation:
    """Test JSON format compatibility validation addressing V9's 2+ hour debugging issue"""
    
    def setup_method(self):
        self.validator = create_enhanced_validator(dev_mode=True)
    
    def test_json_compatibility_valid_prompt(self):
        """Test JSON compatibility validation passes for valid prompt"""
        mock_prompt = """
        You are an SEO expert. Generate slugs and respond in JSON format.
        Include 'analysis' and 'slugs' fields in your response.
        """
        
        with patch.object(self.validator, '_get_prompt_content', return_value=mock_prompt), \
             patch.object(self.validator, '_is_api_available', return_value=False):  # Skip API test
            
            result = self.validator.validate_json_compatibility('test_version')
            
            assert result['passed'] == True
            assert result['check'] == 'json_compatibility'
            assert len(result['errors']) == 0
    
    def test_json_compatibility_missing_json_format(self):
        """Test JSON compatibility validation fails when JSON format requirement missing"""
        mock_prompt = """
        You are an SEO expert. Generate slugs for content.
        Return the best possible slugs.
        """
        
        with patch.object(self.validator, '_get_prompt_content', return_value=mock_prompt):
            result = self.validator.validate_json_compatibility('test_version')
            
            assert result['passed'] == False
            assert any('JSON format requirement' in error for error in result['errors'])
    
    def test_json_compatibility_missing_required_fields(self):
        """Test JSON compatibility validation detects missing required fields"""
        mock_prompt = """
        Generate slugs in JSON format but only return the slug field.
        """
        
        with patch.object(self.validator, '_get_prompt_content', return_value=mock_prompt):
            result = self.validator.validate_json_compatibility('test_version')
            
            assert result['passed'] == False
            json_field_errors = [e for e in result['errors'] if 'JSON fields' in e]
            assert len(json_field_errors) > 0
    
    def test_json_compatibility_with_api_test(self):
        """Test JSON compatibility includes API test when available"""
        mock_prompt = """
        Generate slugs in JSON format with analysis and slugs fields.
        """
        
        with patch.object(self.validator, '_get_prompt_content', return_value=mock_prompt), \
             patch.object(self.validator, '_is_api_available', return_value=True), \
             patch.object(self.validator, '_test_minimal_json_api_call', return_value={'success': True, 'error': None}):
            
            result = self.validator.validate_json_compatibility('test_version')
            
            assert result['passed'] == True
            assert 'api_test' in result['details']
            assert result['details']['api_test']['success'] == True


@pytest.mark.validation  
class TestConfigurationConsistencyValidation:
    """Test configuration consistency validation addressing V9's wrong prompt file issue"""
    
    def setup_method(self):
        self.validator = create_enhanced_validator(dev_mode=True)
    
    def test_configuration_consistency_valid_setup(self):
        """Test configuration consistency passes for valid setup"""
        mock_prompt = "You are an SEO expert generating slugs in JSON format with analysis and slugs fields."
        
        with patch.object(self.validator, '_validate_version_mapping', return_value=True), \
             patch.object(SlugGeneratorConfig, 'get_prompt_path', return_value='/path/to/prompt.txt'), \
             patch.object(Path, 'exists', return_value=True), \
             patch.object(self.validator, '_get_prompt_content', return_value=mock_prompt), \
             patch.object(self.validator, '_validate_prompt_content', return_value=[]), \
             patch.object(self.validator, '_validate_constraint_alignment', return_value=[]), \
             patch.object(self.validator, '_check_configuration_conflicts', return_value=[]):
            
            result = self.validator.validate_configuration_consistency('v10')
            
            assert result['passed'] == True
            assert result['check'] == 'configuration_consistency'
            assert len(result['errors']) == 0
    
    def test_configuration_consistency_invalid_version(self):
        """Test configuration consistency fails for invalid version"""
        with patch.object(self.validator, '_validate_version_mapping', return_value=False):
            result = self.validator.validate_configuration_consistency('invalid_version')
            
            assert result['passed'] == False
            assert any('Invalid version configuration' in error for error in result['errors'])
    
    def test_configuration_consistency_missing_file(self):
        """Test configuration consistency fails when prompt file missing"""
        with patch.object(self.validator, '_validate_version_mapping', return_value=True), \
             patch.object(SlugGeneratorConfig, 'get_prompt_path', return_value='/nonexistent/prompt.txt'), \
             patch.object(Path, 'exists', return_value=False):
            
            result = self.validator.validate_configuration_consistency('v10')
            
            assert result['passed'] == False
            assert any('not found' in error for error in result['errors'])
    
    def test_configuration_consistency_content_issues(self):
        """Test configuration consistency detects prompt content issues"""
        with patch.object(self.validator, '_validate_version_mapping', return_value=True), \
             patch.object(SlugGeneratorConfig, 'get_prompt_path', return_value='/path/to/prompt.txt'), \
             patch.object(Path, 'exists', return_value=True), \
             patch.object(self.validator, '_get_prompt_content', return_value="Short prompt"), \
             patch.object(self.validator, '_validate_prompt_content', return_value=['Prompt too short']):
            
            result = self.validator.validate_configuration_consistency('v10')
            
            assert result['passed'] == False
            assert 'Prompt too short' in result['errors']


@pytest.mark.validation
class TestRuntimeReadinessValidation:
    """Test runtime readiness validation to prevent V9's runtime failures"""
    
    def setup_method(self):
        self.validator = create_enhanced_validator(dev_mode=True)
    
    def test_runtime_readiness_all_systems_go(self):
        """Test runtime readiness passes when all systems are ready"""
        with patch.object(self.validator, '_test_api_connectivity', return_value={'success': True, 'error': None}), \
             patch.object(self.validator, '_test_model_availability', return_value={'success': True, 'error': None}), \
             patch.object(self.validator, '_check_rate_limit_status', return_value={'warning': False}), \
             patch.object(self.validator, '_test_response_time', return_value={'slow': False}):
            
            result = self.validator.validate_runtime_readiness('v10')
            
            assert result['passed'] == True
            assert result['check'] == 'runtime_readiness'
            assert len(result['errors']) == 0
    
    def test_runtime_readiness_api_auth_failure(self):
        """Test runtime readiness fails on API authentication error"""
        with patch.object(self.validator, '_test_api_connectivity', 
                         return_value={'success': False, 'error': 'Authentication failed'}):
            
            result = self.validator.validate_runtime_readiness('v10')
            
            assert result['passed'] == False
            assert any('authentication' in error.lower() for error in result['errors'])
    
    def test_runtime_readiness_with_warnings(self):
        """Test runtime readiness passes with warnings for non-critical issues"""
        with patch.object(self.validator, '_test_api_connectivity', return_value={'success': True, 'error': None}), \
             patch.object(self.validator, '_test_model_availability', 
                         return_value={'success': False, 'error': 'Model temporarily unavailable'}), \
             patch.object(self.validator, '_check_rate_limit_status', 
                         return_value={'warning': True, 'message': 'Rate limit approaching'}), \
             patch.object(self.validator, '_test_response_time', return_value={'slow': True, 'duration': 12.0}):
            
            result = self.validator.validate_runtime_readiness('v10')
            
            assert result['passed'] == True  # Should pass with warnings
            assert len(result['warnings']) >= 2  # Model + rate limit warnings


@pytest.mark.validation
class TestV10DevelopmentSetupValidation:
    """Test V10-specific development setup validation"""
    
    def setup_method(self):
        self.validator = create_enhanced_validator(dev_mode=True)
    
    def test_v10_development_setup_success(self):
        """Test V10 development setup validation passes for proper setup"""
        with patch.object(self.validator, '_test_dual_mode_capability', 
                         return_value={'success': True, 'error': None}), \
             patch.object(self.validator, '_test_enhanced_constraints',
                         return_value={'success': True, 'error': None}), \
             patch.object(self.validator, '_test_fallback_mechanism',
                         return_value={'success': True, 'warning': None}), \
             patch.object(self.validator, '_test_rapid_iteration_mode',
                         return_value={'success': True, 'warning': None}):
            
            result = self.validator.validate_v10_development_setup()
            
            assert result['passed'] == True
            assert result['check'] == 'v10_development_setup'
            assert len(result['errors']) == 0
    
    def test_v10_development_setup_dual_mode_failure(self):
        """Test V10 development setup fails when dual-mode capability missing"""
        with patch.object(self.validator, '_test_dual_mode_capability',
                         return_value={'success': False, 'error': 'Dual-mode not supported'}):
            
            result = self.validator.validate_v10_development_setup()
            
            assert result['passed'] == False
            assert any('dual-mode' in error.lower() for error in result['errors'])
    
    def test_v10_development_setup_constraints_failure(self):
        """Test V10 development setup fails on enhanced constraints issues"""
        with patch.object(self.validator, '_test_dual_mode_capability',
                         return_value={'success': True, 'error': None}), \
             patch.object(self.validator, '_test_enhanced_constraints',
                         return_value={'success': False, 'error': 'Constraints exceed system limits'}):
            
            result = self.validator.validate_v10_development_setup()
            
            assert result['passed'] == False
            assert any('constraints' in error.lower() for error in result['errors'])


@pytest.mark.validation
class TestComprehensiveValidation:
    """Test comprehensive validation combining all checks"""
    
    def setup_method(self):
        self.validator = create_enhanced_validator(dev_mode=True)
    
    def test_comprehensive_validation_all_pass(self):
        """Test comprehensive validation when all checks pass"""
        with patch.object(self.validator, 'validate_json_compatibility',
                         return_value={'passed': True, 'errors': [], 'warnings': []}), \
             patch.object(self.validator, 'validate_configuration_consistency',
                         return_value={'passed': True, 'errors': [], 'warnings': []}), \
             patch.object(self.validator, 'validate_runtime_readiness',
                         return_value={'passed': True, 'errors': [], 'warnings': []}), \
             patch.object(self.validator, 'validate_v10_development_setup',
                         return_value={'passed': True, 'errors': [], 'warnings': []}):
            
            result = self.validator.comprehensive_validation('v10')
            
            assert result['overall_passed'] == True
            assert result['summary']['total_checks'] == 4
            assert result['summary']['passed_checks'] == 4
            assert result['summary']['failed_checks'] == 0
            assert 'validation_time' in result
    
    def test_comprehensive_validation_some_fail(self):
        """Test comprehensive validation when some checks fail"""
        with patch.object(self.validator, 'validate_json_compatibility',
                         return_value={'passed': False, 'errors': ['JSON error'], 'warnings': []}), \
             patch.object(self.validator, 'validate_configuration_consistency',
                         return_value={'passed': True, 'errors': [], 'warnings': ['Config warning']}), \
             patch.object(self.validator, 'validate_runtime_readiness',
                         return_value={'passed': True, 'errors': [], 'warnings': []}), \
             patch.object(self.validator, 'validate_v10_development_setup',
                         return_value={'passed': True, 'errors': [], 'warnings': []}):
            
            result = self.validator.comprehensive_validation('v10')
            
            assert result['overall_passed'] == False
            assert result['summary']['total_checks'] == 4
            assert result['summary']['passed_checks'] == 3
            assert result['summary']['failed_checks'] == 1
            assert result['summary']['warnings_count'] == 1
    
    def test_comprehensive_validation_exception_handling(self):
        """Test comprehensive validation handles check exceptions gracefully"""
        with patch.object(self.validator, 'validate_json_compatibility',
                         side_effect=Exception("Test exception")), \
             patch.object(self.validator, 'validate_configuration_consistency',
                         return_value={'passed': True, 'errors': [], 'warnings': []}):
            
            result = self.validator.comprehensive_validation('v10')
            
            assert result['overall_passed'] == False
            assert 'json_compatibility' in result['checks']
            assert result['checks']['json_compatibility']['passed'] == False
            assert any('execution failed' in error for error in result['checks']['json_compatibility']['errors'])


@pytest.mark.validation
class TestValidationHelperMethods:
    """Test validation helper methods"""
    
    def setup_method(self):
        self.validator = create_enhanced_validator(dev_mode=True)
    
    def test_has_json_format_requirement(self):
        """Test JSON format requirement detection"""
        # Positive cases
        positive_cases = [
            "Return results in JSON format",
            "Respond with JSON object",
            "Use json response format",
            "Format as JSON",
            "json structure required"
        ]
        
        for case in positive_cases:
            assert self.validator._has_json_format_requirement(case), f"Failed to detect: {case}"
        
        # Negative cases
        negative_cases = [
            "Generate slugs for content",
            "Return the best results",
            "Use structured format"
        ]
        
        for case in negative_cases:
            assert not self.validator._has_json_format_requirement(case), f"False positive: {case}"
    
    def test_has_response_format_spec(self):
        """Test response format specification detection"""
        prompt_with_spec = """
        Return results in this format:
        ```json
        {
          "analysis": {...},
          "slugs": [...]
        }
        ```
        """
        
        assert self.validator._has_response_format_spec(prompt_with_spec)
        
        prompt_without_spec = "Generate slugs in JSON format"
        assert not self.validator._has_response_format_spec(prompt_without_spec)
    
    def test_validate_prompt_content(self):
        """Test prompt content validation"""
        # Valid prompt
        valid_prompt = "You are an SEO expert generating slugs with comprehensive analysis."
        issues = self.validator._validate_prompt_content(valid_prompt)
        assert len(issues) == 0
        
        # Invalid prompts
        empty_prompt = ""
        issues = self.validator._validate_prompt_content(empty_prompt)
        assert any('empty' in issue for issue in issues)
        
        short_prompt = "Generate"
        issues = self.validator._validate_prompt_content(short_prompt)
        assert any('too short' in issue for issue in issues)
        
        missing_keywords = "Generate content for users"
        issues = self.validator._validate_prompt_content(missing_keywords)
        assert any('slug' in issue for issue in issues)
        assert any('seo' in issue for issue in issues)
    
    def test_is_api_available(self):
        """Test API availability check"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            assert self.validator._is_api_available() == True
        
        with patch.dict(os.environ, {}, clear=True):
            assert self.validator._is_api_available() == False


@pytest.mark.validation
class TestValidationCaching:
    """Test validation result caching for performance"""
    
    def setup_method(self):
        self.validator = create_enhanced_validator(dev_mode=True)
    
    def test_api_test_caching(self):
        """Test API connectivity test uses caching"""
        # First call
        with patch('time.time', return_value=100):
            result1 = self.validator._test_api_connectivity()
        
        # Second call within cache window (should use cache)
        with patch('time.time', return_value=150):  # 50 seconds later
            result2 = self.validator._test_api_connectivity()
        
        # Results should be identical (from cache)
        assert result1 == result2
        
        # Third call outside cache window (should not use cache)  
        with patch('time.time', return_value=200):  # 100 seconds later (> 60s window)
            result3 = self.validator._test_api_connectivity()
        
        # This would be a new call, so we just verify it doesn't error
        assert isinstance(result3, dict)
        assert 'success' in result3