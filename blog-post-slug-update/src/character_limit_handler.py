import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CharacterLimitHandler:
    """Handle character limit enforcement with various strategies"""
    
    def __init__(self, mode: str = "retry_shorter"):
        """
        Initialize handler with specified mode.
        
        Modes:
        - 'retry_shorter': Ask LLM to make it shorter
        - 'truncate': Cut off at limit
        - 'hard_fail': Raise exception if over limit
        - 'warning_only': Log warning but continue
        """
        self.mode = mode
        
    def handle_over_limit(self, content: str, limit: int, content_type: str) -> str:
        """Handle content that exceeds character limit"""
        if len(content) <= limit:
            return content
            
        if self.mode == 'retry_shorter':
            return self._retry_with_shorter_target(content, limit, content_type)
        elif self.mode == 'truncate':
            return self._truncate_content(content, limit)
        elif self.mode == 'hard_fail':
            raise ValueError(f"{content_type} exceeds {limit} characters: {len(content)}")
        else:  # warning_only
            logger.warning(f"{content_type} exceeds limit: {len(content)}/{limit}")
            return content
    
    def _retry_with_shorter_target(self, content: str, limit: int, content_type: str) -> str:
        """Ask LLM to make content shorter"""
        target_length = int(limit * 0.85)  # Aim for 15% under limit
        
        # Import here to avoid circular imports
        try:
            from seo_generator import llm_call_with_retry
            
            prompt = f"""
            Shorten this {content_type} to maximum {target_length} characters while keeping the meaning:
            
            Original ({len(content)} chars): "{content}"
            Target: {target_length} characters maximum
            
            Return only the shortened version.
            """
            
            return llm_call_with_retry(prompt, max_retries=2)
        except ImportError:
            # Fallback to simple shortening if LLM not available
            if content_type == "slug":
                # For slugs, remove words and unnecessary parts
                words = content.split('-')
                while len('-'.join(words)) > target_length and len(words) > 2:
                    words = words[:-1]
                return '-'.join(words)
            else:
                # For titles/meta, truncate smartly
                return self._truncate_content(content, target_length)
    
    def _truncate_content(self, content: str, limit: int) -> str:
        """Truncate content at limit with smart handling"""
        if len(content) <= limit:
            return content
            
        truncated = content[:limit]
        
        # For slugs, don't end with hyphen
        if truncated.endswith('-'):
            truncated = truncated.rstrip('-')
            
        # For sentences, try to end at word boundary
        if ' ' in truncated:
            last_space = truncated.rfind(' ')
            if last_space > limit * 0.8:  # Only if we don't lose too much
                truncated = truncated[:last_space]
                
        return truncated