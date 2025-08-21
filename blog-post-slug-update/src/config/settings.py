#!/usr/bin/env python3
"""
Centralized configuration settings for the slug generator
All configurable parameters in one place
"""

import os
from typing import Dict, Any


class SlugGeneratorConfig:
    """Centralized configuration for slug generation"""
    
    # API Configuration
    OPENAI_MODEL = "gpt-4o-mini"
    MAX_TOKENS = 500
    TEMPERATURE = 0.3
    
    # Retry Configuration
    MAX_RETRIES = 3
    RETRY_BASE_DELAY = 1.0
    RATE_LIMIT_MULTIPLIER = 2.0
    
    # Content Limits (improved from content-analyzer)
    API_CONTENT_LIMIT = 3000     # Increased from 2000
    PROMPT_PREVIEW_LIMIT = 1500  # Increased from 500
    
    # Quality Thresholds
    CONFIDENCE_THRESHOLD = 0.5
    MAX_TAGS_PER_CATEGORY = 5
    
    # SEO Optimization Settings (version-aware)
    MAX_WORDS = 6
    MAX_CHARS = 60
    MIN_WORDS = 3
    
    # Prompt Configuration
    DEFAULT_PROMPT_VERSION = "v6"  # V6 Cultural Enhanced - stable production version
    
    # Version-specific settings
    VERSION_SETTINGS = {
        'v8': {
            'MAX_WORDS': 8,      # Relaxed from 6 to 8 for complex multi-brand
            'MAX_CHARS': 70,     # Relaxed from 60 to 70 for longer descriptive slugs
            'CONFIDENCE_THRESHOLD': 0.75,  # Higher threshold for V8's enhanced complexity
        },
        'v9': {
            'MAX_WORDS': 8,      # Maintain V8's flexibility
            'MAX_CHARS': 70,     # Maintain V8's character limits
            'CONFIDENCE_THRESHOLD': 0.7,   # LLM-guided improvements should meet high standards
        }
    }
    
    @classmethod
    def get_api_key(cls) -> str:
        """Get OpenAI API key from environment"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable."
            )
        return api_key
    
    @classmethod
    def validate_version(cls, version: str = None) -> bool:
        """Validate that version exists and is properly configured"""
        if version is None:
            return True
        
        if version == "current":
            return True
        
        if version == cls.DEFAULT_PROMPT_VERSION:
            return True
        
        # Check if version has specific settings or prompt file
        if version in cls.VERSION_SETTINGS:
            return True
        
        # Check if prompt file exists
        try:
            path = cls.get_prompt_path(version)
            return os.path.exists(path)
        except Exception:
            return False
    
    @classmethod
    def get_prompt_path(cls, version: str = None) -> str:
        """Get path to prompt file for specified version"""
        version = version or cls.DEFAULT_PROMPT_VERSION
        
        if version == "current" or version == cls.DEFAULT_PROMPT_VERSION:
            filename = "current.txt"
        else:
            filename = f"{version}_prompt.txt"
        
        config_dir = os.path.dirname(__file__)
        path = os.path.join(config_dir, 'prompts', filename)
        
        # Validation layer - ensure file exists
        if not os.path.exists(path):
            raise FileNotFoundError(f"Prompt file not found: {path}")
        
        return path
    
    def apply_version_settings(self, version: str = None) -> 'SlugGeneratorConfig':
        """Apply version-specific settings and return configured instance"""
        if version and version in self.VERSION_SETTINGS:
            settings = self.VERSION_SETTINGS[version]
            for key, value in settings.items():
                setattr(self, key, value)
        return self
    
    @classmethod
    def for_version(cls, version: str = None) -> 'SlugGeneratorConfig':
        """Create a configuration instance with version-specific settings applied"""
        # Validate version before creating configuration
        if not cls.validate_version(version):
            raise ValueError(f"Invalid or unsupported version: {version}")
        
        config = cls()
        return config.apply_version_settings(version)
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'openai_model': cls.OPENAI_MODEL,
            'max_tokens': cls.MAX_TOKENS,
            'temperature': cls.TEMPERATURE,
            'max_retries': cls.MAX_RETRIES,
            'retry_base_delay': cls.RETRY_BASE_DELAY,
            'api_content_limit': cls.API_CONTENT_LIMIT,
            'prompt_preview_limit': cls.PROMPT_PREVIEW_LIMIT,
            'confidence_threshold': cls.CONFIDENCE_THRESHOLD,
            'max_words': cls.MAX_WORDS,
            'max_chars': cls.MAX_CHARS,
            'min_words': cls.MIN_WORDS,
            'default_prompt_version': cls.DEFAULT_PROMPT_VERSION
        }