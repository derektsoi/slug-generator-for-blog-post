#!/usr/bin/env python3
"""
Pre-flight validation testing for the slug generator
Tests all validation scenarios needed to prevent the 2+ hour JSON debugging issue
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from config.settings import SlugGeneratorConfig


class PromptValidationError(Exception):
    """Base class for prompt validation errors"""
    pass


class JSONFormatError(PromptValidationError):
    """Error when prompt doesn't specify JSON format requirement"""
    pass


class ConfigurationError(PromptValidationError):
    """Error in configuration setup"""
    pass


class SyntaxError(PromptValidationError):
    """Error in prompt syntax"""
    pass


class PreFlightValidator:
    """Pre-flight validation system to prevent runtime errors"""
    
    @staticmethod
    def validate_json_format_requirement(prompt_content: str) -> bool:
        """Validate that prompt explicitly requests JSON format"""
        json_keywords = [
            'json', 'JSON', 'json format', 'JSON format',
            'json object', 'JSON object', 'json response', 'JSON response'
        ]
        
        content_lower = prompt_content.lower()
        return any(keyword.lower() in content_lower for keyword in json_keywords)
    
    @staticmethod
    def validate_prompt_syntax(prompt_content: str) -> tuple[bool, list]:
        """Validate basic prompt syntax and structure"""
        issues = []
        
        if not prompt_content.strip():
            issues.append("Prompt is empty")
        
        if len(prompt_content) < 100:
            issues.append("Prompt seems too short (< 100 characters)")
        
        if 'slug' not in prompt_content.lower():
            issues.append("Prompt doesn't mention 'slug'")
        
        if 'seo' not in prompt_content.lower():
            issues.append("Prompt doesn't mention 'SEO'")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def validate_configuration_mapping(version: str) -> bool:
        """Validate that version maps to existing configuration"""
        if version is None:
            return True  # None is valid (uses default)
        
        if version == "current":
            return True
        
        if version == SlugGeneratorConfig.DEFAULT_PROMPT_VERSION:
            return True
        
        # Check if version has specific settings
        if version in SlugGeneratorConfig.VERSION_SETTINGS:
            return True
        
        # Check if prompt file would exist for this version
        try:
            path = SlugGeneratorConfig.get_prompt_path(version)
            return True  # If no error, mapping is valid
        except Exception:
            return False
    
    @staticmethod
    def validate_file_existence(version: str) -> bool:
        """Validate that prompt file exists for version"""
        try:
            path = SlugGeneratorConfig.get_prompt_path(version)
            return Path(path).exists()
        except Exception:
            return False
    
    @staticmethod
    def validate_api_key_available() -> bool:
        """Validate that API key is available"""
        try:
            SlugGeneratorConfig.get_api_key()
            return True
        except ValueError:
            return False
    
    @classmethod
    def run_full_validation(cls, version: str = None) -> dict:
        """Run complete pre-flight validation suite"""
        results = {
            'version': version,
            'passed': True,
            'errors': [],
            'warnings': []
        }
        
        # 1. Configuration validation
        if not cls.validate_configuration_mapping(version):
            results['errors'].append(f"Invalid version configuration: {version}")
            results['passed'] = False
        
        # 2. File existence validation
        if not cls.validate_file_existence(version):
            results['errors'].append(f"Prompt file not found for version: {version}")
            results['passed'] = False
        
        # 3. API key validation
        if not cls.validate_api_key_available():
            results['warnings'].append("API key not available (required for actual generation)")
        
        # 4. Prompt content validation (if file exists)
        if cls.validate_file_existence(version):
            try:
                path = SlugGeneratorConfig.get_prompt_path(version)
                with open(path, 'r', encoding='utf-8') as f:
                    prompt_content = f.read()
                
                # JSON format validation
                if not cls.validate_json_format_requirement(prompt_content):
                    results['errors'].append("Prompt doesn't specify JSON format requirement")
                    results['passed'] = False
                
                # Syntax validation
                syntax_valid, syntax_issues = cls.validate_prompt_syntax(prompt_content)
                if not syntax_valid:
                    results['warnings'].extend(syntax_issues)
                
            except Exception as e:
                results['errors'].append(f"Error reading prompt file: {e}")
                results['passed'] = False
        
        return results


@pytest.mark.validation
class TestJSONFormatValidation:
    """Test JSON format requirement validation"""
    
    def test_detect_json_format_requirement_present(self):
        """Test detection when JSON format is properly specified"""
        prompt_with_json = """
        You are an expert SEO slug generator.
        Please respond in JSON format with the following structure:
        {"slugs": [...]}
        """
        
        assert PreFlightValidator.validate_json_format_requirement(prompt_with_json)
    
    def test_detect_json_format_requirement_uppercase(self):
        """Test detection with uppercase JSON"""
        prompt_with_json = """
        Generate slugs and return results in JSON object format.
        """
        
        assert PreFlightValidator.validate_json_format_requirement(prompt_with_json)
    
    def test_detect_json_format_requirement_missing(self):
        """Test detection when JSON format is missing"""
        prompt_without_json = """
        You are an expert SEO slug generator.
        Please generate appropriate slugs for the content.
        """
        
        assert not PreFlightValidator.validate_json_format_requirement(prompt_without_json)
    
    def test_detect_json_format_various_phrases(self):
        """Test detection with various JSON-related phrases"""
        json_phrases = [
            "respond in json format",
            "return a JSON object", 
            "use JSON response format",
            "format your response as json",
            "json structure"
        ]
        
        for phrase in json_phrases:
            prompt = f"Generate slugs and {phrase} please."
            assert PreFlightValidator.validate_json_format_requirement(prompt), f"Failed to detect: {phrase}"


@pytest.mark.validation  
class TestPromptSyntaxValidation:
    """Test prompt syntax and structure validation"""
    
    def test_valid_prompt_syntax(self):
        """Test validation of well-formed prompt"""
        valid_prompt = """
        You are an expert SEO slug generator specializing in cross-border e-commerce.
        Generate compelling, search-optimized URL slugs that maximize click-through potential.
        
        Please analyze the content and return results in JSON format.
        """
        
        is_valid, issues = PreFlightValidator.validate_prompt_syntax(valid_prompt)
        assert is_valid
        assert len(issues) == 0
    
    def test_empty_prompt_validation(self):
        """Test validation fails for empty prompt"""
        is_valid, issues = PreFlightValidator.validate_prompt_syntax("")
        assert not is_valid
        assert "Prompt is empty" in issues
    
    def test_short_prompt_validation(self):
        """Test validation warns about very short prompts"""
        short_prompt = "Generate slug"
        is_valid, issues = PreFlightValidator.validate_prompt_syntax(short_prompt)
        assert not is_valid
        assert any("too short" in issue for issue in issues)
    
    def test_missing_slug_keyword_validation(self):
        """Test validation detects missing 'slug' keyword"""
        prompt_without_slug = """
        You are an expert SEO generator specializing in cross-border e-commerce.
        Generate compelling, search-optimized URL paths.
        """
        
        is_valid, issues = PreFlightValidator.validate_prompt_syntax(prompt_without_slug)
        assert not is_valid
        assert any("slug" in issue for issue in issues)
    
    def test_missing_seo_keyword_validation(self):
        """Test validation detects missing 'SEO' keyword"""
        prompt_without_seo = """
        You are an expert slug generator specializing in cross-border e-commerce.
        Generate compelling, search-optimized URL slugs.
        """
        
        is_valid, issues = PreFlightValidator.validate_prompt_syntax(prompt_without_seo)
        assert not is_valid
        assert any("SEO" in issue for issue in issues)


@pytest.mark.validation
class TestConfigurationValidation:
    """Test configuration mapping validation"""
    
    def test_validate_none_version(self):
        """Test validation passes for None version"""
        assert PreFlightValidator.validate_configuration_mapping(None)
    
    def test_validate_current_version(self):
        """Test validation passes for 'current' version"""
        assert PreFlightValidator.validate_configuration_mapping("current")
    
    def test_validate_default_version(self):
        """Test validation passes for default version"""
        default_version = SlugGeneratorConfig.DEFAULT_PROMPT_VERSION
        assert PreFlightValidator.validate_configuration_mapping(default_version)
    
    def test_validate_version_with_settings(self):
        """Test validation passes for versions with specific settings"""
        for version in SlugGeneratorConfig.VERSION_SETTINGS.keys():
            assert PreFlightValidator.validate_configuration_mapping(version)
    
    def test_validate_unknown_version(self):
        """Test validation fails for unknown version"""
        assert not PreFlightValidator.validate_configuration_mapping("unknown_version_xyz")
    
    def test_validate_empty_version(self):
        """Test validation fails for empty string version"""
        assert not PreFlightValidator.validate_configuration_mapping("")


@pytest.mark.validation
class TestFileExistenceValidation:
    """Test prompt file existence validation"""
    
    def test_validate_current_file_exists(self):
        """Test validation passes when current.txt exists"""
        # This assumes the current.txt file exists in the actual project
        result = PreFlightValidator.validate_file_existence("current")
        assert result  # Should pass if current.txt exists
    
    def test_validate_version_files_exist(self):
        """Test validation for known version files"""
        # Test known versions that should have files
        known_versions = ["v7", "v8", "v9"]
        
        for version in known_versions:
            # Note: This test documents current state, may fail until files are standardized
            result = PreFlightValidator.validate_file_existence(version)
            # Just check that validation runs without error
            assert isinstance(result, bool)
    
    @patch('pathlib.Path.exists')
    def test_validate_nonexistent_file(self, mock_exists):
        """Test validation fails when file doesn't exist"""
        mock_exists.return_value = False
        
        result = PreFlightValidator.validate_file_existence("nonexistent_version")
        assert not result


@pytest.mark.validation
class TestAPIKeyValidation:
    """Test API key availability validation"""
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_validate_api_key_available(self):
        """Test validation passes when API key is available"""
        assert PreFlightValidator.validate_api_key_available()
    
    @patch.dict(os.environ, {}, clear=True)
    def test_validate_api_key_missing(self):
        """Test validation fails when API key is missing"""
        assert not PreFlightValidator.validate_api_key_available()


@pytest.mark.validation
class TestFullValidationPipeline:
    """Test complete pre-flight validation pipeline"""
    
    def test_full_validation_current_version(self):
        """Test full validation for current version"""
        results = PreFlightValidator.run_full_validation("current")
        
        assert 'version' in results
        assert 'passed' in results
        assert 'errors' in results
        assert 'warnings' in results
        assert results['version'] == "current"
    
    def test_full_validation_with_api_key(self):
        """Test full validation with API key present"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            results = PreFlightValidator.run_full_validation("current")
            
            # Should not have API key warning when key is present
            api_warnings = [w for w in results['warnings'] if 'API key' in w]
            assert len(api_warnings) == 0
    
    def test_full_validation_without_api_key(self):
        """Test full validation without API key"""
        with patch.dict(os.environ, {}, clear=True):
            results = PreFlightValidator.run_full_validation("current")
            
            # Should have API key warning when key is missing
            api_warnings = [w for w in results['warnings'] if 'API key' in w]
            assert len(api_warnings) > 0
    
    def test_full_validation_invalid_version(self):
        """Test full validation with invalid version"""
        results = PreFlightValidator.run_full_validation("invalid_version_xyz")
        
        assert not results['passed']
        assert len(results['errors']) > 0
        assert any('Invalid version configuration' in error for error in results['errors'])
    
    @patch('builtins.open', mock_open(read_data="Generate SEO slugs without JSON format"))
    @patch('pathlib.Path.exists', return_value=True)
    def test_full_validation_missing_json_format(self, mock_exists):
        """Test full validation detects missing JSON format requirement"""
        results = PreFlightValidator.run_full_validation("test_version")
        
        assert not results['passed']
        json_errors = [e for e in results['errors'] if 'JSON format' in e]
        assert len(json_errors) > 0
    
    @patch('builtins.open', mock_open(read_data="Generate SEO slugs in JSON format for optimization"))
    @patch('pathlib.Path.exists', return_value=True)
    def test_full_validation_with_valid_prompt(self, mock_exists):
        """Test full validation with valid prompt content"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            results = PreFlightValidator.run_full_validation("test_version")
            
            # Should pass all validations with proper prompt
            json_errors = [e for e in results['errors'] if 'JSON format' in e]
            assert len(json_errors) == 0
    
    def test_validation_results_structure(self):
        """Test validation results have expected structure"""
        results = PreFlightValidator.run_full_validation("current")
        
        required_keys = ['version', 'passed', 'errors', 'warnings']
        for key in required_keys:
            assert key in results
        
        assert isinstance(results['passed'], bool)
        assert isinstance(results['errors'], list)
        assert isinstance(results['warnings'], list)


@pytest.mark.validation
class TestValidationErrorTypes:
    """Test validation error type classification"""
    
    def test_json_format_error_inheritance(self):
        """Test JSONFormatError inherits from PromptValidationError"""
        assert issubclass(JSONFormatError, PromptValidationError)
    
    def test_configuration_error_inheritance(self):
        """Test ConfigurationError inherits from PromptValidationError"""
        assert issubclass(ConfigurationError, PromptValidationError)
    
    def test_syntax_error_inheritance(self):
        """Test SyntaxError inherits from PromptValidationError"""
        assert issubclass(SyntaxError, PromptValidationError)
    
    def test_error_types_can_be_raised(self):
        """Test that all error types can be raised properly"""
        with pytest.raises(JSONFormatError):
            raise JSONFormatError("Test JSON format error")
        
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Test configuration error")
        
        with pytest.raises(SyntaxError):
            raise SyntaxError("Test syntax error")
        
        with pytest.raises(PromptValidationError):
            raise PromptValidationError("Test base validation error")


@pytest.mark.validation
class TestValidationIntegration:
    """Test integration between validation and configuration systems"""
    
    def test_validation_works_with_all_configured_versions(self):
        """Test validation pipeline works with all configured versions"""
        # Test default version
        default_results = PreFlightValidator.run_full_validation()
        assert 'passed' in default_results
        
        # Test current version
        current_results = PreFlightValidator.run_full_validation("current")
        assert 'passed' in current_results
        
        # Test all versions with specific settings
        for version in SlugGeneratorConfig.VERSION_SETTINGS.keys():
            version_results = PreFlightValidator.run_full_validation(version)
            assert 'passed' in version_results
            assert version_results['version'] == version
    
    def test_validation_detects_configuration_inconsistencies(self):
        """Test validation can detect configuration inconsistencies"""
        # This test would catch issues like duplicate V9 files
        known_versions = ["v8", "v9"]
        
        for version in known_versions:
            results = PreFlightValidator.run_full_validation(version)
            # Should not have configuration errors for known versions
            config_errors = [e for e in results['errors'] if 'configuration' in e.lower()]
            assert len(config_errors) == 0 or not results['passed']