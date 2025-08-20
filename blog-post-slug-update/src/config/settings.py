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
    
    # SEO Optimization Settings
    MAX_WORDS = 6
    MAX_CHARS = 60
    MIN_WORDS = 3
    
    # Prompt Configuration
    DEFAULT_PROMPT_VERSION = "v5"  # Current production version
    
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
    def get_prompt_path(cls, version: str = None) -> str:
        """Get path to prompt file for specified version"""
        version = version or cls.DEFAULT_PROMPT_VERSION
        
        if version == "current" or version == cls.DEFAULT_PROMPT_VERSION:
            filename = "current.txt"
        else:
            filename = f"{version}_prompt.txt"
        
        config_dir = os.path.dirname(__file__)
        return os.path.join(config_dir, 'prompts', filename)
    
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