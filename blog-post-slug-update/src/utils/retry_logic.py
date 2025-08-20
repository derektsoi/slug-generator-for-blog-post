#!/usr/bin/env python3
"""
Retry logic utilities with exponential backoff
Intelligent retry patterns for API calls and network requests
"""

import time
from typing import Callable, Any, Optional
from functools import wraps


def exponential_backoff_retry(max_retries: int = 3, base_delay: float = 1.0, rate_limit_multiplier: float = 2.0):
    """
    Decorator for exponential backoff retry logic
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
        rate_limit_multiplier: Extra multiplier for rate limit errors
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        raise Exception(f"Failed after {max_retries} retry attempts: {str(e)}")
                    
                    # Calculate exponential backoff delay
                    delay = base_delay * (2 ** attempt)
                    
                    # Handle different error types
                    if "rate limit" in str(e).lower():
                        # Longer delay for rate limits
                        delay = delay * rate_limit_multiplier
                    
                    time.sleep(delay)
                    continue
            
        return wrapper
    return decorator


def retry_with_backoff(func: Callable, max_retries: int = 3, base_delay: float = 1.0) -> Any:
    """
    Function-based retry with exponential backoff
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
    
    Returns:
        Result of the function call
    """
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries:
                raise Exception(f"Failed after {max_retries} retry attempts: {str(e)}")
            
            # Calculate exponential backoff delay
            delay = base_delay * (2 ** attempt)
            
            # Handle different error types
            if "rate limit" in str(e).lower():
                # Longer delay for rate limits
                delay = delay * 2
            
            time.sleep(delay)
            continue