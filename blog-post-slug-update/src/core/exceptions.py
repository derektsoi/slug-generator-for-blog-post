#!/usr/bin/env python3
"""
Structured error handling for the slug generator
Provides clear error classification and actionable error messages
"""

from typing import Optional, Dict, Any


class SlugGeneratorError(Exception):
    """Base exception for all slug generator errors"""
    
    def __init__(self, message: str, error_code: str = None, context: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for structured logging/debugging"""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'context': self.context
        }


class ConfigurationError(SlugGeneratorError):
    """Configuration-related errors (validation, setup, file access)"""
    
    def __init__(self, message: str, version: str = None, config_issue: str = None):
        context = {}
        if version:
            context['version'] = version
        if config_issue:
            context['config_issue'] = config_issue
        
        super().__init__(message, "CONFIG_ERROR", context)


class ValidationError(SlugGeneratorError):
    """Pre-flight validation errors"""
    
    def __init__(self, message: str, validation_type: str = None, failed_checks: list = None):
        context = {}
        if validation_type:
            context['validation_type'] = validation_type
        if failed_checks:
            context['failed_checks'] = failed_checks
        
        super().__init__(message, "VALIDATION_ERROR", context)


class APIError(SlugGeneratorError):
    """OpenAI API-related errors"""
    
    def __init__(self, message: str, api_error_type: str = None, retry_attempt: int = None):
        context = {}
        if api_error_type:
            context['api_error_type'] = api_error_type
        if retry_attempt is not None:
            context['retry_attempt'] = retry_attempt
        
        super().__init__(message, "API_ERROR", context)


class ContentError(SlugGeneratorError):
    """Content extraction and processing errors"""
    
    def __init__(self, message: str, url: str = None, content_issue: str = None):
        context = {}
        if url:
            context['url'] = url
        if content_issue:
            context['content_issue'] = content_issue
        
        super().__init__(message, "CONTENT_ERROR", context)


class JSONFormatError(SlugGeneratorError):
    """JSON parsing and format errors"""
    
    def __init__(self, message: str, raw_response: str = None, parsing_issue: str = None):
        context = {}
        if raw_response:
            context['raw_response'] = raw_response[:500]  # Truncate for logging
        if parsing_issue:
            context['parsing_issue'] = parsing_issue
        
        super().__init__(message, "JSON_FORMAT_ERROR", context)


class SlugValidationError(SlugGeneratorError):
    """Slug validation and quality errors"""
    
    def __init__(self, message: str, slug: str = None, validation_issue: str = None):
        context = {}
        if slug:
            context['slug'] = slug
        if validation_issue:
            context['validation_issue'] = validation_issue
        
        super().__init__(message, "SLUG_VALIDATION_ERROR", context)


class ErrorHandler:
    """Centralized error handling with development vs production modes"""
    
    def __init__(self, dev_mode: bool = False):
        self.dev_mode = dev_mode
    
    def handle_configuration_error(self, error: Exception, version: str = None) -> ConfigurationError:
        """Handle and classify configuration errors"""
        if "Invalid or unsupported version" in str(error):
            return ConfigurationError(
                f"Unsupported prompt version: {version}",
                version=version,
                config_issue="invalid_version"
            )
        elif "Prompt file not found" in str(error):
            return ConfigurationError(
                f"Missing prompt file for version: {version}",
                version=version,
                config_issue="missing_file"
            )
        elif "API key" in str(error):
            return ConfigurationError(
                "OpenAI API key not configured",
                config_issue="missing_api_key"
            )
        else:
            return ConfigurationError(
                f"Configuration error: {str(error)}",
                version=version,
                config_issue="unknown"
            )
    
    def handle_api_error(self, error: Exception, retry_attempt: int = None) -> APIError:
        """Handle and classify API errors"""
        error_str = str(error).lower()
        
        if "rate limit" in error_str:
            return APIError(
                "API rate limit exceeded",
                api_error_type="rate_limit",
                retry_attempt=retry_attempt
            )
        elif "timeout" in error_str:
            return APIError(
                "API request timeout",
                api_error_type="timeout",
                retry_attempt=retry_attempt
            )
        elif "authentication" in error_str or "unauthorized" in error_str:
            return APIError(
                "API authentication failed",
                api_error_type="auth_error"
            )
        elif "quota" in error_str or "billing" in error_str:
            return APIError(
                "API quota exceeded or billing issue",
                api_error_type="quota_exceeded"
            )
        else:
            return APIError(
                f"API error: {str(error)}",
                api_error_type="unknown",
                retry_attempt=retry_attempt
            )
    
    def handle_json_error(self, error: Exception, raw_response: str = None) -> JSONFormatError:
        """Handle and classify JSON parsing errors"""
        error_str = str(error).lower()
        
        if "json" in error_str and "decode" in error_str:
            return JSONFormatError(
                "Failed to parse JSON response from API",
                raw_response=raw_response,
                parsing_issue="invalid_json"
            )
        elif "missing" in error_str and "key" in error_str:
            return JSONFormatError(
                "Missing required key in JSON response",
                raw_response=raw_response,
                parsing_issue="missing_key"
            )
        else:
            return JSONFormatError(
                f"JSON format error: {str(error)}",
                raw_response=raw_response,
                parsing_issue="unknown"
            )
    
    def handle_content_error(self, error: Exception, url: str = None) -> ContentError:
        """Handle and classify content extraction errors"""
        error_str = str(error).lower()
        
        if "invalid url" in error_str:
            return ContentError(
                f"Invalid URL format: {url}",
                url=url,
                content_issue="invalid_url"
            )
        elif "connection" in error_str or "network" in error_str:
            return ContentError(
                f"Network error accessing URL: {url}",
                url=url,
                content_issue="network_error"
            )
        elif "timeout" in error_str:
            return ContentError(
                f"Timeout accessing URL: {url}",
                url=url,
                content_issue="timeout"
            )
        else:
            return ContentError(
                f"Content extraction error: {str(error)}",
                url=url,
                content_issue="unknown"
            )
    
    def handle_slug_validation_error(self, error: Exception, slug: str = None) -> SlugValidationError:
        """Handle and classify slug validation errors"""
        error_str = str(error).lower()
        
        if "confidence" in error_str:
            return SlugValidationError(
                f"Slug confidence too low: {slug}",
                slug=slug,
                validation_issue="low_confidence"
            )
        elif "length" in error_str or "too long" in error_str:
            return SlugValidationError(
                f"Slug too long: {slug}",
                slug=slug,
                validation_issue="too_long"
            )
        elif "words" in error_str:
            return SlugValidationError(
                f"Slug word count invalid: {slug}",
                slug=slug,
                validation_issue="word_count"
            )
        else:
            return SlugValidationError(
                f"Slug validation error: {str(error)}",
                slug=slug,
                validation_issue="unknown"
            )
    
    def format_error_for_user(self, error: SlugGeneratorError) -> str:
        """Format error message for user display"""
        if not self.dev_mode:
            # Production mode: concise, actionable messages
            if isinstance(error, ConfigurationError):
                if error.context.get('config_issue') == 'missing_api_key':
                    return "Please set your OpenAI API key in the environment"
                elif error.context.get('config_issue') == 'invalid_version':
                    return f"Unsupported version '{error.context.get('version')}'. Use v6, v7, v8, or v9"
                else:
                    return "Configuration error. Please check your setup"
            
            elif isinstance(error, APIError):
                if error.context.get('api_error_type') == 'rate_limit':
                    return "API rate limit exceeded. Please try again in a moment"
                elif error.context.get('api_error_type') == 'auth_error':
                    return "API authentication failed. Please check your API key"
                else:
                    return "API service temporarily unavailable"
            
            elif isinstance(error, ContentError):
                if error.context.get('content_issue') == 'invalid_url':
                    return "Please provide a valid URL"
                else:
                    return "Unable to access the provided URL"
            
            else:
                return "An error occurred. Please try again"
        
        else:
            # Development mode: detailed information
            return f"{error.__class__.__name__}: {error.message}\nContext: {error.context}"
    
    def log_error(self, error: SlugGeneratorError) -> None:
        """Log error for debugging (in dev mode)"""
        if self.dev_mode:
            print(f"🐛 {error.__class__.__name__}: {error.message}")
            if error.context:
                for key, value in error.context.items():
                    print(f"   {key}: {value}")


def create_error_handler(dev_mode: bool = False) -> ErrorHandler:
    """Factory function to create error handler"""
    return ErrorHandler(dev_mode)