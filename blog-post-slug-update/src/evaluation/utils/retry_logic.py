"""
Enhanced Retry Logic Utilities

Provides intelligent retry logic with error classification for API calls.
Distinguishes between temporary and permanent failures.
"""

import time
import random
from typing import Callable, Any, Optional, Type, List
from .exceptions import (
    LLMUnavailableError, InvalidAPIKeyError, APIRateLimitError, 
    TemporaryAPIError, APIQuotaExceededError, classify_api_error
)


def smart_api_retry(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_multiplier: float = 2.0,
    jitter: bool = True,
    retry_on_rate_limit: bool = True
) -> Any:
    """
    Execute API function with intelligent retry based on error classification
    
    Args:
        func: Function to execute (should make API call)
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        backoff_multiplier: Multiplier for delay on each retry
        jitter: Add random jitter to prevent thundering herd
        retry_on_rate_limit: Whether to retry on rate limit errors
        
    Returns:
        Function result on success
        
    Raises:
        Specific LLMUnavailableError subclass based on failure type
    """
    
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            # Classify the error
            classified_error = classify_api_error(e)
            last_exception = classified_error
            
            # Permanent errors - don't retry
            if isinstance(classified_error, (InvalidAPIKeyError, APIQuotaExceededError)):
                raise classified_error
            
            # Rate limit errors - only retry if enabled
            if isinstance(classified_error, APIRateLimitError):
                if not retry_on_rate_limit or attempt == max_retries:
                    raise classified_error
                # Use longer delays for rate limits
                delay = min(base_delay * (backoff_multiplier ** (attempt + 2)), max_delay)
            
            # Temporary errors - retry with exponential backoff
            elif isinstance(classified_error, TemporaryAPIError):
                if attempt == max_retries:
                    raise classified_error
                delay = min(base_delay * (backoff_multiplier ** attempt), max_delay)
            
            # Unknown errors - classify as temporary and retry
            else:
                if attempt == max_retries:
                    raise TemporaryAPIError(f"Unknown error after {max_retries} retries: {e}")
                delay = min(base_delay * (backoff_multiplier ** attempt), max_delay)
            
            # Add jitter to prevent thundering herd
            if jitter:
                delay *= (0.5 + random.random() * 0.5)  # 50-100% of calculated delay
            
            time.sleep(delay)
    
    # Should never reach here, but just in case
    raise last_exception or TemporaryAPIError("Retry logic failed unexpectedly")


class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_multiplier: float = 2.0,
        jitter: bool = True,
        retry_on_rate_limit: bool = True
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter
        self.retry_on_rate_limit = retry_on_rate_limit
    
    def execute_with_retry(self, func: Callable) -> Any:
        """Execute function with this retry configuration"""
        return smart_api_retry(
            func=func,
            max_retries=self.max_retries,
            base_delay=self.base_delay,
            max_delay=self.max_delay,
            backoff_multiplier=self.backoff_multiplier,
            jitter=self.jitter,
            retry_on_rate_limit=self.retry_on_rate_limit
        )