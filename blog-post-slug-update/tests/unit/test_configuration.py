#!/usr/bin/env python3
"""
Comprehensive configuration testing for SlugGeneratorConfig
Tests all configuration scenarios needed for safe refactoring
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from config.settings import SlugGeneratorConfig


class TestSlugGeneratorConfigBasics:
    """Test basic configuration functionality"""
    
    def test_default_configuration_values(self):
        """Test default configuration values are set correctly"""
        config = SlugGeneratorConfig()
        
        assert config.OPENAI_MODEL == "gpt-4o-mini"
        assert config.MAX_TOKENS == 500
        assert config.TEMPERATURE == 0.3
        assert config.MAX_RETRIES == 3
        assert config.RETRY_BASE_DELAY == 1.0
        assert config.API_CONTENT_LIMIT == 3000
        assert config.PROMPT_PREVIEW_LIMIT == 1500
        assert config.CONFIDENCE_THRESHOLD == 0.5
        assert config.MAX_WORDS == 6
        assert config.MAX_CHARS == 60
        assert config.MIN_WORDS == 3
        assert config.DEFAULT_PROMPT_VERSION == "v6"
    
    def test_to_dict_conversion(self):
        """Test configuration can be converted to dictionary"""
        config_dict = SlugGeneratorConfig.to_dict()
        
        required_keys = [
            'openai_model', 'max_tokens', 'temperature',
            'max_retries', 'retry_base_delay', 'api_content_limit',
            'prompt_preview_limit', 'confidence_threshold',
            'max_words', 'max_chars', 'min_words', 'default_prompt_version'
        ]
        
        for key in required_keys:
            assert key in config_dict
        
        assert config_dict['openai_model'] == "gpt-4o-mini"
        assert config_dict['max_retries'] == 3
        assert config_dict['default_prompt_version'] == "v6"


class TestVersionSpecificSettings:
    """Test version-specific configuration settings"""
    
    def test_version_settings_structure(self):
        """Test VERSION_SETTINGS has correct structure"""
        assert 'v8' in SlugGeneratorConfig.VERSION_SETTINGS
        assert 'v9' in SlugGeneratorConfig.VERSION_SETTINGS
        
        v8_settings = SlugGeneratorConfig.VERSION_SETTINGS['v8']
        assert v8_settings['MAX_WORDS'] == 8
        assert v8_settings['MAX_CHARS'] == 70
        assert v8_settings['CONFIDENCE_THRESHOLD'] == 0.75
        
        v9_settings = SlugGeneratorConfig.VERSION_SETTINGS['v9']
        assert v9_settings['MAX_WORDS'] == 8
        assert v9_settings['MAX_CHARS'] == 70
        assert v9_settings['CONFIDENCE_THRESHOLD'] == 0.7
    
    def test_apply_version_settings_v8(self):
        """Test applying V8 version settings"""
        config = SlugGeneratorConfig()
        original_max_words = config.MAX_WORDS
        original_max_chars = config.MAX_CHARS
        original_threshold = config.CONFIDENCE_THRESHOLD
        
        updated_config = config.apply_version_settings('v8')
        
        # Should modify the same instance
        assert updated_config is config
        assert config.MAX_WORDS == 8
        assert config.MAX_CHARS == 70
        assert config.CONFIDENCE_THRESHOLD == 0.75
        
        # Verify changes from defaults
        assert config.MAX_WORDS != original_max_words
        assert config.MAX_CHARS != original_max_chars
        assert config.CONFIDENCE_THRESHOLD != original_threshold
    
    def test_apply_version_settings_v9(self):
        """Test applying V9 version settings"""
        config = SlugGeneratorConfig()
        updated_config = config.apply_version_settings('v9')
        
        assert updated_config is config
        assert config.MAX_WORDS == 8
        assert config.MAX_CHARS == 70
        assert config.CONFIDENCE_THRESHOLD == 0.7
    
    def test_apply_version_settings_unknown_version(self):
        """Test applying settings for unknown version does nothing"""
        config = SlugGeneratorConfig()
        original_max_words = config.MAX_WORDS
        original_max_chars = config.MAX_CHARS
        original_threshold = config.CONFIDENCE_THRESHOLD
        
        updated_config = config.apply_version_settings('unknown_version')
        
        # Should return same instance but no changes
        assert updated_config is config
        assert config.MAX_WORDS == original_max_words
        assert config.MAX_CHARS == original_max_chars
        assert config.CONFIDENCE_THRESHOLD == original_threshold
    
    def test_apply_version_settings_none(self):
        """Test applying None version does nothing"""
        config = SlugGeneratorConfig()
        original_max_words = config.MAX_WORDS
        
        updated_config = config.apply_version_settings(None)
        
        assert updated_config is config
        assert config.MAX_WORDS == original_max_words
    
    def test_for_version_class_method_v8(self):
        """Test for_version class method creates correctly configured instance"""
        config = SlugGeneratorConfig.for_version('v8')
        
        assert isinstance(config, SlugGeneratorConfig)
        assert config.MAX_WORDS == 8
        assert config.MAX_CHARS == 70
        assert config.CONFIDENCE_THRESHOLD == 0.75
    
    def test_for_version_class_method_v9(self):
        """Test for_version class method for V9"""
        config = SlugGeneratorConfig.for_version('v9')
        
        assert isinstance(config, SlugGeneratorConfig)
        assert config.MAX_WORDS == 8
        assert config.MAX_CHARS == 70
        assert config.CONFIDENCE_THRESHOLD == 0.7
    
    def test_for_version_class_method_none(self):
        """Test for_version with None returns default configuration"""
        config = SlugGeneratorConfig.for_version(None)
        
        assert isinstance(config, SlugGeneratorConfig)
        assert config.MAX_WORDS == 6  # Default value
        assert config.MAX_CHARS == 60  # Default value
        assert config.CONFIDENCE_THRESHOLD == 0.5  # Default value


class TestAPIKeyHandling:
    """Test API key configuration and validation"""
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-api-key-12345'})
    def test_get_api_key_from_environment(self):
        """Test getting API key from environment variable"""
        api_key = SlugGeneratorConfig.get_api_key()
        assert api_key == 'test-api-key-12345'
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_key_missing_raises_error(self):
        """Test missing API key raises ValueError"""
        with pytest.raises(ValueError, match="OpenAI API key is required"):
            SlugGeneratorConfig.get_api_key()
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': ''})
    def test_get_api_key_empty_raises_error(self):
        """Test empty API key raises ValueError"""
        with pytest.raises(ValueError, match="OpenAI API key is required"):
            SlugGeneratorConfig.get_api_key()


class TestPromptPathResolution:
    """Test prompt file path resolution logic"""
    
    def test_get_prompt_path_current(self):
        """Test getting path for current prompt"""
        path = SlugGeneratorConfig.get_prompt_path("current")
        
        assert path.endswith("prompts/current.txt")
        assert "config" in path
    
    def test_get_prompt_path_default_version(self):
        """Test getting path for default version"""
        path = SlugGeneratorConfig.get_prompt_path()  # No version specified
        
        # Should use DEFAULT_PROMPT_VERSION but resolve to current.txt
        assert path.endswith("prompts/current.txt")
    
    def test_get_prompt_path_specific_version(self):
        """Test getting path for specific version"""
        path = SlugGeneratorConfig.get_prompt_path("v8")
        
        assert path.endswith("prompts/v8_prompt.txt")
        assert "config" in path
    
    def test_get_prompt_path_v9(self):
        """Test getting path for V9 version"""
        path = SlugGeneratorConfig.get_prompt_path("v9")
        
        assert path.endswith("prompts/v9_prompt.txt")
    
    def test_get_prompt_path_matches_default(self):
        """Test path resolution when version matches DEFAULT_PROMPT_VERSION"""
        default_version = SlugGeneratorConfig.DEFAULT_PROMPT_VERSION
        path = SlugGeneratorConfig.get_prompt_path(default_version)
        
        # Should resolve to current.txt when matching default
        assert path.endswith("prompts/current.txt")


@pytest.mark.configuration
class TestConfigurationConsistency:
    """Test configuration consistency and validation"""
    
    def test_version_settings_keys_match_attributes(self):
        """Test that VERSION_SETTINGS keys match actual class attributes"""
        config = SlugGeneratorConfig()
        
        for version, settings in SlugGeneratorConfig.VERSION_SETTINGS.items():
            for setting_key in settings.keys():
                assert hasattr(config, setting_key), f"Setting {setting_key} not found in config"
    
    def test_all_versions_have_consistent_settings(self):
        """Test that all versions have the same setting keys"""
        all_versions = SlugGeneratorConfig.VERSION_SETTINGS.keys()
        if len(all_versions) > 1:
            reference_keys = set(SlugGeneratorConfig.VERSION_SETTINGS[list(all_versions)[0]].keys())
            
            for version in all_versions:
                version_keys = set(SlugGeneratorConfig.VERSION_SETTINGS[version].keys())
                assert version_keys == reference_keys, f"Version {version} has different setting keys"
    
    def test_version_settings_values_are_valid(self):
        """Test that version setting values are reasonable"""
        for version, settings in SlugGeneratorConfig.VERSION_SETTINGS.items():
            # MAX_WORDS should be reasonable
            assert 3 <= settings.get('MAX_WORDS', 6) <= 10, f"Invalid MAX_WORDS for {version}"
            
            # MAX_CHARS should be reasonable  
            assert 30 <= settings.get('MAX_CHARS', 60) <= 100, f"Invalid MAX_CHARS for {version}"
            
            # CONFIDENCE_THRESHOLD should be between 0 and 1
            threshold = settings.get('CONFIDENCE_THRESHOLD', 0.5)
            assert 0 <= threshold <= 1, f"Invalid CONFIDENCE_THRESHOLD for {version}"


@pytest.mark.configuration
class TestPromptFileValidation:
    """Test prompt file existence and naming consistency"""
    
    def test_current_prompt_file_exists(self, project_root_path):
        """Test that current.txt prompt file exists"""
        prompt_path = project_root_path / 'src' / 'config' / 'prompts' / 'current.txt'
        assert prompt_path.exists(), "current.txt prompt file should exist"
        assert prompt_path.is_file(), "current.txt should be a file"
    
    def test_versioned_prompt_files_exist(self, prompt_files_test_data):
        """Test that expected versioned prompt files exist"""
        prompt_dir = prompt_files_test_data["prompt_dir"]
        expected_files = prompt_files_test_data["expected_files"]
        
        for filename in expected_files:
            file_path = prompt_dir / filename
            assert file_path.exists(), f"Expected prompt file {filename} should exist"
    
    def test_no_duplicate_v9_files_issue(self, prompt_files_test_data):
        """Test for the duplicate V9 files issue identified in refactoring"""
        prompt_dir = prompt_files_test_data["prompt_dir"]
        
        v9_files = [
            "v9_prompt.txt",
            "v9_llm_guided.txt"
        ]
        
        existing_v9_files = []
        for filename in v9_files:
            file_path = prompt_dir / filename
            if file_path.exists():
                existing_v9_files.append(filename)
        
        # This test documents the current duplicate file issue
        # After refactoring, should only have one V9 file
        if len(existing_v9_files) > 1:
            pytest.fail(f"Duplicate V9 files found: {existing_v9_files}. Should consolidate to single file.")
    
    def test_archive_files_exist(self, prompt_files_test_data):
        """Test that archived prompt files exist"""
        prompt_dir = prompt_files_test_data["prompt_dir"]
        archive_dir = prompt_dir / "archive"
        archive_files = prompt_files_test_data["archive_files"]
        
        for filename in archive_files:
            file_path = archive_dir / filename
            assert file_path.exists(), f"Archived prompt file {filename} should exist"


class TestConfigurationEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_multiple_version_applications(self):
        """Test applying multiple version settings sequentially"""
        config = SlugGeneratorConfig()
        
        # Apply V8, then V9
        config.apply_version_settings('v8')
        assert config.CONFIDENCE_THRESHOLD == 0.75
        
        config.apply_version_settings('v9')
        assert config.CONFIDENCE_THRESHOLD == 0.7  # Should override V8 setting
    
    def test_for_version_creates_new_instances(self):
        """Test that for_version creates separate instances"""
        config1 = SlugGeneratorConfig.for_version('v8')
        config2 = SlugGeneratorConfig.for_version('v9')
        
        assert config1 is not config2
        assert config1.CONFIDENCE_THRESHOLD != config2.CONFIDENCE_THRESHOLD
    
    def test_config_immutability_of_defaults(self):
        """Test that modifying instance doesn't affect class defaults"""
        config = SlugGeneratorConfig()
        original_default = SlugGeneratorConfig.MAX_WORDS
        
        config.MAX_WORDS = 999
        
        # Class default should be unchanged
        assert SlugGeneratorConfig.MAX_WORDS == original_default
        
        # New instance should have original defaults
        new_config = SlugGeneratorConfig()
        assert new_config.MAX_WORDS == original_default