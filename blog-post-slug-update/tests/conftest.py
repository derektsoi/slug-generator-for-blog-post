#!/usr/bin/env python3
"""
Centralized test configuration and fixtures for blog post slug generator tests
Ensures reliable test collection and provides common test utilities
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add src directory to Python path for all tests
project_root = Path(__file__).parent.parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

@pytest.fixture(scope="session")
def project_root_path():
    """Provide project root path for tests"""
    return project_root

@pytest.fixture(scope="session") 
def src_path_fixture():
    """Provide src path for tests"""
    return src_path

@pytest.fixture
def mock_api_key():
    """Provide mock API key for testing"""
    return "test-api-key-12345"

@pytest.fixture
def mock_openai_response():
    """Standard mock OpenAI response for testing"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = '''
    {
        "slugs": [
            {
                "slug": "test-slug-generator",
                "confidence": 0.85,
                "reasoning": "Clear and descriptive slug for testing"
            },
            {
                "slug": "example-blog-post-guide", 
                "confidence": 0.78,
                "reasoning": "Alternative option with good SEO potential"
            }
        ]
    }
    '''
    return mock_response

@pytest.fixture
def sample_test_content():
    """Sample content for testing slug generation"""
    return {
        "title": "Best Shopping Guide for Cross-Border E-commerce",
        "content": "Complete guide to shopping from international retailers. Learn about shipping, customs, and the best deals available for global shoppers.",
        "url": "https://example.com/blog/shopping-guide"
    }

@pytest.fixture
def config_test_data():
    """Test data for configuration testing"""
    return {
        "test_versions": ["v6", "v7", "v8", "v9"],
        "test_settings": {
            "v8": {
                "MAX_WORDS": 8,
                "MAX_CHARS": 70,
                "CONFIDENCE_THRESHOLD": 0.75
            },
            "v9": {
                "MAX_WORDS": 8,
                "MAX_CHARS": 70,
                "CONFIDENCE_THRESHOLD": 0.7
            }
        }
    }

@pytest.fixture
def prompt_files_test_data(project_root_path):
    """Test data for prompt file validation"""
    prompt_dir = project_root_path / 'src' / 'config' / 'prompts'
    return {
        "prompt_dir": prompt_dir,
        "expected_files": [
            "current.txt",
            "v6_prompt.txt",
            "v7_prompt.txt", 
            "v8_prompt.txt",
            "v9_prompt.txt"
        ],
        "archive_files": [
            "v1_baseline.txt",
            "v2_few_shot.txt", 
            "v3_experimental.txt",
            "v4_regression.txt",
            "v5_brand_focused.txt",
            "v6_cultural_enhanced.txt",
            "v7_multi_brand_hierarchy.txt"
        ]
    }

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Auto-setup for all tests"""
    # Ensure environment variables don't interfere
    original_env = os.environ.copy()
    
    # Set test-specific environment if needed
    os.environ.setdefault('OPENAI_API_KEY', 'test-key')
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)

class TestHelper:
    """Helper class for common test operations"""
    
    @staticmethod
    def create_mock_slug_generator(api_key="test-key", **kwargs):
        """Create a SlugGenerator instance with mock configuration"""
        try:
            from core import SlugGenerator
            return SlugGenerator(api_key=api_key, **kwargs)
        except ImportError:
            # Return mock if module not available
            mock_generator = Mock()
            mock_generator.api_key = api_key
            for key, value in kwargs.items():
                setattr(mock_generator, key, value)
            return mock_generator
    
    @staticmethod
    def validate_slug_format(slug):
        """Validate slug meets basic SEO requirements"""
        if not slug:
            return False, "Slug is empty"
        
        if len(slug.split('-')) < 3:
            return False, f"Slug '{slug}' has fewer than 3 words"
            
        if len(slug) > 70:
            return False, f"Slug '{slug}' exceeds 70 characters"
            
        if not slug.islower():
            return False, f"Slug '{slug}' contains uppercase characters"
            
        return True, "Valid slug format"

@pytest.fixture
def test_helper():
    """Provide TestHelper instance for tests"""
    return TestHelper()

# Configure pytest markers
pytest_plugins = []

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "requires_api: marks tests that require API access"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers", "configuration: marks tests for configuration validation"
    )
    config.addinivalue_line(
        "markers", "validation: marks tests for pre-flight validation"
    )