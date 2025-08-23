"""
Configuration Constants for SEO Evaluation System

Centralized constants to avoid duplication across modules.
"""

from typing import List

# Standard SEO scoring dimensions used across the system
DEFAULT_SCORING_DIMENSIONS: List[str] = [
    'user_intent_match',
    'brand_hierarchy', 
    'cultural_authenticity',
    'click_through_potential',
    'competitive_differentiation',
    'technical_seo'
]

# Default evaluation prompt version
DEFAULT_EVALUATION_PROMPT_VERSION: str = "current"

# Default model for OpenAI evaluation
DEFAULT_MODEL: str = "gpt-4o-mini"