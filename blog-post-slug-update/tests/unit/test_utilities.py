#!/usr/bin/env python3
"""
Test utilities for Phase 2 components.
Extracted mock components and test helpers.
"""


class MockSlugGenerator:
    """Mock slug generator for testing configuration pipeline"""
    
    def __init__(self, config):
        self.config = config
    
    def is_valid_slug(self, slug: str) -> bool:
        """Validate slug using version-specific constraints"""
        words = slug.split('-')
        
        if len(words) > self.config.max_slug_words:
            return False
        if len(slug) > self.config.max_slug_chars:
            return False
        
        return True