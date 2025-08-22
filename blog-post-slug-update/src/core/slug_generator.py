#!/usr/bin/env python3
"""
Core LLM-powered blog post slug generator
Refactored for clean separation of concerns and maintainability
"""

import os
import json
import time
from typing import Dict, List, Optional

# Optional imports for graceful fallback in testing environments
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Graceful fallback for environments without python-dotenv
    # Production environments should have environment variables set directly
    pass

try:
    import openai
except ImportError:
    # Graceful fallback for testing environments without openai package
    # This allows testing of non-API functionality
    openai = None

from core.content_extractor import extract_title_and_content, is_url
from core.validators import clean_slug, validate_slug
from core.exceptions import (
    ErrorHandler, ConfigurationError, APIError, ContentError, 
    JSONFormatError, SlugValidationError
)
from config.settings import SlugGeneratorConfig


class SlugGenerator:
    """
    AI-powered blog post slug generator using OpenAI.
    Refactored for clean architecture and maintainability.
    """
    
    def __init__(self, api_key: Optional[str] = None, config: SlugGeneratorConfig = None, 
                 max_retries: int = None, retry_delay: float = None, prompt_version: str = None,
                 enable_validation: bool = True, dev_mode: bool = False):
        """
        Initialize the SlugGenerator with centralized configuration.
        
        Args:
            api_key: OpenAI API key. If None, will try to load from environment.
            config: Configuration object. If None, uses version-aware configuration.
            max_retries: Maximum retry attempts (backward compatibility)
            retry_delay: Base retry delay (backward compatibility)
            prompt_version: Prompt version to use (e.g., 'v7', 'current', 'v8')
            enable_validation: Enable pre-flight validation (default: True)
            dev_mode: Enable development mode with enhanced error reporting (default: False)
        """
        # Store prompt version and development mode for use throughout the class
        self.prompt_version = prompt_version
        self.dev_mode = dev_mode
        
        # Initialize error handler
        self.error_handler = ErrorHandler(dev_mode)
        
        # Use version-aware configuration if no config provided
        try:
            self.config = config or SlugGeneratorConfig.for_version(prompt_version)
        except Exception as e:
            config_error = self.error_handler.handle_configuration_error(e, prompt_version)
            if dev_mode:
                self.error_handler.log_error(config_error)
            raise config_error
        
        # Override config with backward compatibility parameters
        if max_retries is not None:
            self.config.MAX_RETRIES = max_retries
        if retry_delay is not None:
            self.config.RETRY_BASE_DELAY = retry_delay
        
        # Pre-flight validation (optional)
        if enable_validation:
            self._run_preflight_validation()
            
        self.api_key = api_key or self.config.get_api_key()
        
        # Initialize OpenAI client
        # Initialize OpenAI client with graceful fallback
        if openai is not None:
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None
            if dev_mode:
                print("⚠️  OpenAI package not available - API functionality disabled")
        
        # Backward compatibility properties
        self.max_retries = self.config.MAX_RETRIES
        self.retry_delay = self.config.RETRY_BASE_DELAY
    
    def _run_preflight_validation(self):
        """Run pre-flight validation to prevent runtime errors"""
        try:
            # Import validation here to avoid circular dependencies
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
            from tests.unit.test_validation_pipeline import PreFlightValidator
            
            validator = PreFlightValidator()
            results = validator.run_full_validation(self.prompt_version)
            
            if not results['passed']:
                error_messages = '; '.join(results['errors'])
                if self.dev_mode:
                    # In dev mode, provide detailed information
                    print(f"⚠️  Pre-flight validation issues found:")
                    for error in results['errors']:
                        print(f"  • {error}")
                    for warning in results['warnings']:
                        print(f"  ⚠️  {warning}")
                    raise RuntimeError(f"Pre-flight validation failed: {error_messages}")
                else:
                    # In production, fail fast with clear message
                    raise RuntimeError(f"Configuration validation failed: {error_messages}")
            
            if results['warnings'] and self.dev_mode:
                print(f"⚠️  Pre-flight validation warnings:")
                for warning in results['warnings']:
                    print(f"  • {warning}")
                    
        except ImportError:
            # Validation framework not available, skip silently in production
            if self.dev_mode:
                print("⚠️  Pre-flight validation framework not available")
        except Exception as e:
            if self.dev_mode:
                print(f"⚠️  Pre-flight validation error: {e}")
            # In production mode, don't fail startup for validation errors
            # unless they're critical configuration issues
            pass
    
    def quick_test(self, title: str, content: str = None) -> Dict:
        """
        Quick test method for development - single case testing with timing
        
        Args:
            title: Blog post title to test
            content: Optional content (uses title if not provided)
            
        Returns:
            Dict with result, timing, and development info
        """
        if not self.dev_mode:
            return self.generate_slug_from_content(title, content or title)
        
        start_time = time.time()
        try:
            result = self.generate_slug_from_content(title, content or title)
            execution_time = time.time() - start_time
            
            dev_info = {
                'success': True,
                'result': result,
                'execution_time': execution_time,
                'prompt_version': self.prompt_version,
                'config_summary': {
                    'max_words': self.config.MAX_WORDS,
                    'max_chars': self.config.MAX_CHARS,
                    'confidence_threshold': self.config.CONFIDENCE_THRESHOLD
                }
            }
            
            print(f"✅ Quick test completed in {execution_time:.2f}s")
            print(f"   Primary slug: {result['primary']}")
            print(f"   Version: {self.prompt_version or 'default'}")
            
            return dev_info
            
        except Exception as e:
            execution_time = time.time() - start_time
            dev_info = {
                'success': False,
                'error': str(e),
                'execution_time': execution_time,
                'prompt_version': self.prompt_version
            }
            
            print(f"❌ Quick test failed in {execution_time:.2f}s")
            print(f"   Error: {str(e)}")
            
            return dev_info
    
    def compare_versions(self, title: str, versions: List[str], content: str = None) -> Dict:
        """
        Compare multiple versions on the same content (development mode)
        
        Args:
            title: Blog post title to test
            versions: List of versions to compare
            content: Optional content (uses title if not provided)
            
        Returns:
            Dict with comparison results
        """
        if not self.dev_mode:
            # In production, just use current version
            return self.generate_slug_from_content(title, content or title)
        
        comparison_results = {
            'test_content': title[:50] + "..." if len(title) > 50 else title,
            'version_results': {},
            'best_version': None,
            'summary': {}
        }
        
        print(f"🔄 Comparing {len(versions)} versions...")
        
        for version in versions:
            try:
                # Create temporary generator with different version
                temp_generator = SlugGenerator(
                    api_key=self.api_key,
                    prompt_version=version,
                    enable_validation=False,  # Skip validation for comparison
                    dev_mode=False  # Disable dev output for cleaner comparison
                )
                
                start_time = time.time()
                result = temp_generator.generate_slug_from_content(title, content or title)
                execution_time = time.time() - start_time
                
                comparison_results['version_results'][version] = {
                    'success': True,
                    'result': result,
                    'execution_time': execution_time,
                    'primary_slug': result['primary']
                }
                
                print(f"  {version}: ✅ {result['primary']} ({execution_time:.2f}s)")
                
            except Exception as e:
                comparison_results['version_results'][version] = {
                    'success': False,
                    'error': str(e),
                    'execution_time': 0
                }
                
                print(f"  {version}: ❌ {str(e)}")
        
        # Determine best version (successful + fastest)
        successful_versions = [
            (v, r) for v, r in comparison_results['version_results'].items()
            if r['success']
        ]
        
        if successful_versions:
            best_version, best_result = min(successful_versions, key=lambda x: x[1]['execution_time'])
            comparison_results['best_version'] = best_version
            print(f"🏆 Best: {best_version} ({best_result['execution_time']:.2f}s)")
        
        return comparison_results
    
    def validate_configuration(self) -> Dict:
        """
        Validate current configuration and provide development insights
        
        Returns:
            Dict with validation results and configuration details
        """
        validation_info = {
            'prompt_version': self.prompt_version,
            'config': {
                'max_words': self.config.MAX_WORDS,
                'max_chars': self.config.MAX_CHARS,
                'confidence_threshold': self.config.CONFIDENCE_THRESHOLD,
                'max_retries': self.config.MAX_RETRIES
            },
            'validation_passed': True,
            'issues': []
        }
        
        # Run configuration checks
        try:
            prompt_path = self.config.get_prompt_path(self.prompt_version)
            validation_info['prompt_file'] = prompt_path
            validation_info['prompt_exists'] = os.path.exists(prompt_path)
            
            if not validation_info['prompt_exists']:
                validation_info['issues'].append(f"Prompt file not found: {prompt_path}")
                validation_info['validation_passed'] = False
                
        except Exception as e:
            validation_info['issues'].append(f"Configuration error: {e}")
            validation_info['validation_passed'] = False
        
        if self.dev_mode:
            status = "✅ Valid" if validation_info['validation_passed'] else "❌ Issues"
            print(f"🔧 Configuration: {status}")
            print(f"   Version: {self.prompt_version or 'default'}")
            print(f"   Max words: {self.config.MAX_WORDS}, Max chars: {self.config.MAX_CHARS}")
            
            if validation_info['issues']:
                for issue in validation_info['issues']:
                    print(f"   ⚠️  {issue}")
        
        return validation_info
    
    def generate_slug(self, url: str, count: int = 1) -> Dict:
        """
        Generate SEO-friendly slug(s) for a blog post URL.
        
        Args:
            url: The blog post URL to analyze
            count: Number of slug suggestions to generate (default: 1)
            
        Returns:
            Dict with 'primary' slug and optional 'alternatives' list
        """
        if not is_url(url):
            raise ValueError(f"Invalid URL format: {url}")
        
        try:
            # Extract title and content from URL
            title, content = extract_title_and_content(url)
            
            # Generate slug using OpenAI with retry logic
            slug_data = self._generate_with_openai_retry(title, content, count)
            
            # Validate and clean suggestions
            cleaned_suggestions = []
            for slug_info in slug_data:
                cleaned = clean_slug(slug_info['slug'])
                if cleaned and self.is_valid_slug(cleaned):
                    cleaned_suggestions.append(cleaned)
            
            if not cleaned_suggestions:
                raise Exception("No valid slugs generated")
            
            result = {
                'primary': cleaned_suggestions[0],
                'alternatives': cleaned_suggestions[1:] if len(cleaned_suggestions) > 1 else [],
                'url': url,
                'title': title
            }
            
            return result
            
        except Exception as e:
            if "Invalid URL format" in str(e):
                raise e
            else:
                raise Exception(f"Error generating slug for URL {url}: {str(e)}")
    
    def _generate_with_openai_retry(self, title: str, content: str, count: int = 1) -> List[Dict]:
        """
        Use OpenAI to generate intelligent slug suggestions with retry logic.
        Uses manual retry with configuration.
        """
        for attempt in range(self.config.MAX_RETRIES + 1):
            try:
                return self._generate_with_openai(title, content, count)
            except Exception as e:
                if attempt == self.config.MAX_RETRIES:
                    raise Exception(f"Failed after {self.config.MAX_RETRIES} retry attempts: {str(e)}")
                
                # Calculate exponential backoff delay
                delay = self.config.RETRY_BASE_DELAY * (2 ** attempt)
                
                # Handle different error types
                if "rate limit" in str(e).lower():
                    # Longer delay for rate limits
                    delay = delay * self.config.RATE_LIMIT_MULTIPLIER
                
                time.sleep(delay)
                continue
    
    def _generate_with_openai(self, title: str, content: str, count: int = 1) -> List[Dict]:
        """
        Use OpenAI to generate intelligent slug suggestions.
        """
        # Prepare content for analysis with configured limits
        analysis_content = content[:self.config.API_CONTENT_LIMIT] if content else ""
        
        # Create prompt for OpenAI
        prompt = self._create_slug_prompt(title, analysis_content, count)
        
        response = self.client.chat.completions.create(
            model=self.config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an SEO expert specializing in creating URL-friendly blog post slugs for cross-border e-commerce content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.config.MAX_TOKENS,
            temperature=self.config.TEMPERATURE,
            response_format={"type": "json_object"}  # Force JSON response
        )
        
        # Parse JSON response
        response_text = response.choices[0].message.content.strip()
        
        try:
            slug_data = json.loads(response_text)
            
            if "slugs" not in slug_data:
                raise Exception("Response missing 'slugs' key")
            
            # Filter by confidence threshold
            filtered_slugs = [
                slug_info for slug_info in slug_data["slugs"]
                if isinstance(slug_info, dict) and 
                   slug_info.get("confidence", 0) >= self.config.CONFIDENCE_THRESHOLD
            ]
            
            # If no slugs meet threshold, lower it or take best available
            if not filtered_slugs and slug_data["slugs"]:
                # Take the highest confidence slug even if below threshold
                filtered_slugs = sorted(
                    slug_data["slugs"], 
                    key=lambda x: x.get("confidence", 0), 
                    reverse=True
                )[:count]
            
            if not filtered_slugs:
                raise Exception("No slugs in response")
            
            return filtered_slugs[:count]
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse OpenAI response as JSON: {e}")
        except Exception as e:
            if "rate limit" in str(e).lower():
                raise Exception("OpenAI rate limit exceeded")
            else:
                raise Exception(f"OpenAI API request failed: {str(e)}")
    
    def _load_prompt(self, version: str = None) -> str:
        """
        Load prompt from external template file using centralized configuration.
        """
        prompt_path = self.config.get_prompt_path(version)
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    
    def _create_slug_prompt(self, title: str, content: str, count: int) -> str:
        """
        Create a well-structured prompt for OpenAI slug generation using external template.
        """
        # Load base prompt template with version support
        base_prompt = self._load_prompt(self.prompt_version)
        
        # Prepare content with configured preview limit
        content_preview = content[:self.config.PROMPT_PREVIEW_LIMIT] if content else ""
        
        # Build the complete prompt
        prompt = f"""{base_prompt}

BLOG POST INFORMATION:
Title: {title}
Content: {content_preview}

Generate {count} different slug options with confidence scores and reasoning.
"""
        return prompt.strip()
    
    def generate_slug_from_content(self, title: str, content: str, count: int = 1) -> Dict:
        """
        Generate slug directly from title and content (for testing).
        """
        try:
            # Generate slug using OpenAI with retry logic
            slug_data = self._generate_with_openai_retry(title, content, count)
            
            # Validate and clean suggestions
            cleaned_suggestions = []
            for slug_info in slug_data:
                cleaned = clean_slug(slug_info['slug'])
                if cleaned and self.is_valid_slug(cleaned):
                    cleaned_suggestions.append(cleaned)
            
            if not cleaned_suggestions:
                raise Exception("No valid slugs generated")
            
            result = {
                'primary': cleaned_suggestions[0],
                'alternatives': cleaned_suggestions[1:] if len(cleaned_suggestions) > 1 else [],
                'title': title
            }
            
            return result
            
        except Exception as e:
            if "No valid slugs" in str(e):
                raise e  # Re-raise with original message
            else:
                raise Exception(f"Error generating slug from content: {str(e)}")
    
    def is_valid_slug(self, slug: str) -> bool:
        """
        Check if a slug meets validation criteria using the generator's configuration.
        """
        validation = validate_slug(slug, self.config)
        return validation['is_valid']
    
    def get_slug_validation(self, slug: str) -> Dict:
        """
        Get detailed validation information for a slug using the generator's configuration.
        """
        return validate_slug(slug, self.config)