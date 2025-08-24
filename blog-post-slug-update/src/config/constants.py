"""
Configuration Constants for SEO Evaluation System

Centralized constants to avoid duplication across modules.
"""

from typing import List

# Standard SEO scoring dimensions used across the system (V2.1 Enhanced)
DEFAULT_SCORING_DIMENSIONS: List[str] = [
    'brand_hierarchy_accuracy',
    'red_flag_pattern_avoidance', 
    'cultural_authenticity',
    'cross_border_service_clarity',
    'search_intent_alignment',
    'technical_seo_compliance'
]

# Default evaluation prompt version (Updated to V2.1)
DEFAULT_EVALUATION_PROMPT_VERSION: str = "enhanced_seo_focused_v2.1"

# Default model for OpenAI evaluation
DEFAULT_MODEL: str = "gpt-4o-mini"