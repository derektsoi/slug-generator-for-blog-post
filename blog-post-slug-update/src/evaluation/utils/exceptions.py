"""
Custom Exception Classes for LLM Evaluation System

Clear error hierarchy to distinguish between different failure modes
and enable appropriate retry/fallback strategies.
"""


class EvaluationError(Exception):
    """Base exception for all evaluation system errors"""
    pass


class LLMUnavailableError(EvaluationError):
    """LLM service is unavailable - no qualitative analysis possible"""
    pass


class InvalidAPIKeyError(LLMUnavailableError):
    """Invalid or missing API key - permanent configuration error"""
    
    def __init__(self, message="Invalid API key provided"):
        super().__init__(message)


class APIRateLimitError(LLMUnavailableError):
    """API rate limit exceeded - temporary failure, retry possible"""
    
    def __init__(self, message="API rate limit exceeded", retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after


class TemporaryAPIError(LLMUnavailableError):
    """Temporary API failure - network issues, service unavailable"""
    
    def __init__(self, message="Temporary API error", original_error=None):
        super().__init__(message)
        self.original_error = original_error


class APIQuotaExceededError(LLMUnavailableError):
    """API quota exceeded - permanent failure until quota reset"""
    
    def __init__(self, message="API quota exceeded"):
        super().__init__(message)


class EvaluationParsingError(EvaluationError):
    """Error parsing LLM response into expected format"""
    
    def __init__(self, message="Failed to parse LLM response", response_content=None):
        super().__init__(message)
        self.response_content = response_content


def classify_api_error(error) -> LLMUnavailableError:
    """
    Classify generic API errors into specific exception types
    
    Args:
        error: Original exception from OpenAI API
        
    Returns:
        Specific LLMUnavailableError subclass
    """
    error_str = str(error).lower()
    
    # Invalid API key errors
    if 'incorrect api key' in error_str or 'invalid api key' in error_str:
        return InvalidAPIKeyError(str(error))
    
    # Rate limit errors
    if 'rate limit' in error_str or error_str.startswith('429'):
        return APIRateLimitError(str(error))
    
    # Quota exceeded errors  
    if 'quota exceeded' in error_str or 'billing' in error_str:
        return APIQuotaExceededError(str(error))
    
    # Temporary network/service errors
    if any(temp_indicator in error_str for temp_indicator in [
        'timeout', 'connection', 'service unavailable', '502', '503', '504'
    ]):
        return TemporaryAPIError(str(error), original_error=error)
    
    # Default to temporary error for unknown issues
    return TemporaryAPIError(f"Unknown API error: {error}", original_error=error)