#!/usr/bin/env python3
"""
Slug validation and cleaning functionality
SEO-compliant validation rules for URL slugs
"""

import re
from typing import Dict


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


def validate_slug(slug: str) -> Dict[str, any]:
    """
    Validate a slug against SEO best practices.
    Returns validation result with is_valid boolean and reasons.
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
    
    # Check length constraints
    if len(words) < 3:
        result['is_valid'] = False
        result['reasons'].append("Too short (less than 3 words)")
    
    if len(words) > 6:
        result['is_valid'] = False
        result['reasons'].append("Too long (more than 6 words)")
    
    if len(slug) > 60:
        result['is_valid'] = False
        result['reasons'].append("Too many characters (over 60)")
    
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