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
    # System-wide limits - prompts can tune within these bounds
    SYSTEM_MAX_WORDS = 20      # Higher constraint for complex multi-brand scenarios
    SYSTEM_MAX_CHARS = 300     # Flexible upper bound for descriptive content
    SYSTEM_MIN_WORDS = 1       # Minimum viable slug length
    
    # Default prompt constraints (V6 stable defaults)
    MAX_WORDS = 6
    MAX_CHARS = 60
    MIN_WORDS = 3
    
    # Prompt Configuration
    DEFAULT_PROMPT_VERSION = "v6"  # V6 Cultural Enhanced - stable production version
    
    # Version-specific settings (constraints must be within system bounds)
    VERSION_SETTINGS = {
        'v8': {
            'MAX_WORDS': 8,      # Relaxed from 6 to 8 for complex multi-brand (BREAKTHROUGH)
            'MAX_CHARS': 70,     # Relaxed from 60 to 70 for longer descriptive slugs
            'CONFIDENCE_THRESHOLD': 0.75,  # Higher threshold for V8's enhanced complexity
        },
        'v9': {
            'MAX_WORDS': 8,      # Maintain V8's flexibility
            'MAX_CHARS': 70,     # Maintain V8's character limits
            'CONFIDENCE_THRESHOLD': 0.7,   # LLM-guided improvements should meet high standards
        },
        'v10': {
            'MAX_WORDS': 10,     # V8's 8 + 2 for competitive enhancements + compound brands
            'MAX_CHARS': 90,     # V8's 70 + 20 for competitive terms + compound brands
            'CONFIDENCE_THRESHOLD': 0.75,  # High threshold for quality assurance
        },
        # Future versions can experiment within system bounds (1-20 words, 1-300 chars)
        'experimental': {
            'MAX_WORDS': 12,     # Example: More flexible for complex content
            'MAX_CHARS': 120,    # Example: Longer for detailed descriptions
            'MIN_WORDS': 2,      # Example: Slightly relaxed minimum
            'CONFIDENCE_THRESHOLD': 0.6,
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
    def validate_constraints(cls, max_words: int = None, max_chars: int = None, min_words: int = None) -> bool:
        """Validate that constraints are within system bounds"""
        if max_words is not None and (max_words < 1 or max_words > cls.SYSTEM_MAX_WORDS):
            return False
        if max_chars is not None and (max_chars < 1 or max_chars > cls.SYSTEM_MAX_CHARS):
            return False
        if min_words is not None and (min_words < cls.SYSTEM_MIN_WORDS or min_words > cls.SYSTEM_MAX_WORDS):
            return False
        
        # Logical constraint validation
        if max_words is not None and min_words is not None and min_words > max_words:
            return False
        
        return True
    
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
        config = config.apply_version_settings(version)
        
        # Validate version-specific constraints are within system bounds
        if not cls.validate_constraints(config.MAX_WORDS, config.MAX_CHARS, config.MIN_WORDS):
            raise ValueError(f"Version {version} constraints exceed system bounds "
                           f"(words: 1-{cls.SYSTEM_MAX_WORDS}, chars: 1-{cls.SYSTEM_MAX_CHARS})")
        
        return config
    
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
            'default_prompt_version': cls.DEFAULT_PROMPT_VERSION,
            # System bounds
            'system_max_words': cls.SYSTEM_MAX_WORDS,
            'system_max_chars': cls.SYSTEM_MAX_CHARS,
            'system_min_words': cls.SYSTEM_MIN_WORDS
        }
    
    @classmethod
    def get_constraint_info(cls, version: str = None) -> Dict[str, Any]:
        """Get detailed constraint information for a version"""
        config = cls.for_version(version) if version else cls()
        return {
            'version': version or cls.DEFAULT_PROMPT_VERSION,
            'constraints': {
                'words': {'min': config.MIN_WORDS, 'max': config.MAX_WORDS},
                'chars': {'max': config.MAX_CHARS}
            },
            'system_bounds': {
                'words': {'min': cls.SYSTEM_MIN_WORDS, 'max': cls.SYSTEM_MAX_WORDS},
                'chars': {'max': cls.SYSTEM_MAX_CHARS}
            },
            'constraint_reasoning': {
                'v8_breakthrough': 'V8 relaxed from 3-6 to 3-8 words and 60 to 70 chars to solve multi-brand failures',
                'system_bounds': 'Up to 20 words and 300 chars allows prompt experimentation for complex content'
            }
        }