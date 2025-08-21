#!/usr/bin/env python3
"""
Slug validation and cleaning functionality
SEO-compliant validation rules for URL slugs
"""

import re
from typing import Dict

# Handle imports for both direct execution and package import
try:
    from ..config.settings import SlugGeneratorConfig
except ImportError:
    from config.settings import SlugGeneratorConfig


def clean_slug(text: str) -> str:
    """
    Clean and format text into a URL-safe slug.
    - Convert to lowercase
    - Replace spaces and special characters with hyphens
    - Remove consecutive hyphens
    - Strip leading/trailing hyphens
    """
    if not text:
        return ""
    
    # Convert to lowercase and replace spaces with hyphens
    slug = text.lower()
    
    # Replace any non-alphanumeric characters with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    
    # Remove consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    
    # Strip leading and trailing hyphens
    slug = slug.strip('-')
    
    return slug


def validate_slug(slug: str, config: SlugGeneratorConfig = None) -> Dict[str, any]:
    """
    Validate a slug against SEO best practices with configurable constraints.
    Returns validation result with is_valid boolean and reasons.
    
    Args:
        slug: The slug to validate
        config: Configuration with constraint settings (uses defaults if None)
    """
    if config is None:
        config = SlugGeneratorConfig()
    result = {
        'is_valid': True,
        'reasons': [],
        'word_count': 0,
        'character_count': len(slug)
    }
    
    if not slug:
        result['is_valid'] = False
        result['reasons'].append("Slug is empty")
        return result
    
    # Count words (split by hyphens)
    words = [w for w in slug.split('-') if w]
    result['word_count'] = len(words)
    
    # Check length constraints using configuration
    if len(words) < config.MIN_WORDS:
        result['is_valid'] = False
        result['reasons'].append(f"Too short (less than {config.MIN_WORDS} words)")
    
    if len(words) > config.MAX_WORDS:
        result['is_valid'] = False
        result['reasons'].append(f"Too long (more than {config.MAX_WORDS} words)")
    
    if len(slug) > config.MAX_CHARS:
        result['is_valid'] = False
        result['reasons'].append(f"Too many characters (over {config.MAX_CHARS})")
    
    # Check character validity
    if not re.match(r'^[a-z0-9-]+$', slug):
        result['is_valid'] = False
        result['reasons'].append("Contains invalid characters (only lowercase letters, numbers, and hyphens allowed)")
    
    # Check for consecutive hyphens
    if '--' in slug:
        result['is_valid'] = False
        result['reasons'].append("Contains consecutive hyphens")
    
    # Check for leading/trailing hyphens
    if slug.startswith('-') or slug.endswith('-'):
        result['is_valid'] = False
        result['reasons'].append("Starts or ends with hyphen")
    
    return result


def validate_slug_system_bounds(slug: str) -> Dict[str, any]:
    """
    Validate a slug against absolute system-wide bounds (1-20 words, 1-300 chars).
    This is used for pre-validation before any prompt-specific constraints.
    """
    result = {
        'is_valid': True,
        'reasons': [],
        'word_count': 0,
        'character_count': len(slug)
    }
    
    if not slug:
        result['is_valid'] = False
        result['reasons'].append("Slug is empty")
        return result
    
    # Count words (split by hyphens)
    words = [w for w in slug.split('-') if w]
    result['word_count'] = len(words)
    
    # Check system-wide absolute bounds
    if len(words) < SlugGeneratorConfig.SYSTEM_MIN_WORDS:
        result['is_valid'] = False
        result['reasons'].append(f"Below system minimum ({SlugGeneratorConfig.SYSTEM_MIN_WORDS} words)")
    
    if len(words) > SlugGeneratorConfig.SYSTEM_MAX_WORDS:
        result['is_valid'] = False
        result['reasons'].append(f"Exceeds system maximum ({SlugGeneratorConfig.SYSTEM_MAX_WORDS} words)")
    
    if len(slug) > SlugGeneratorConfig.SYSTEM_MAX_CHARS:
        result['is_valid'] = False
        result['reasons'].append(f"Exceeds system character limit ({SlugGeneratorConfig.SYSTEM_MAX_CHARS} chars)")
    
    # Basic format validation (same as regular validation)
    if not re.match(r'^[a-z0-9-]+$', slug):
        result['is_valid'] = False
        result['reasons'].append("Contains invalid characters (only lowercase letters, numbers, and hyphens allowed)")
    
    if '--' in slug:
        result['is_valid'] = False
        result['reasons'].append("Contains consecutive hyphens")
    
    if slug.startswith('-') or slug.endswith('-'):
        result['is_valid'] = False
        result['reasons'].append("Starts or ends with hyphen")
    
    return result