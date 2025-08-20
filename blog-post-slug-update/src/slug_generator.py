#!/usr/bin/env python3
"""
Blog Post Slug Generator with OpenAI Integration
Generates SEO-friendly slugs from blog post URLs using AI
"""

import os
import re
import json
import time
from typing import Dict, List, Optional
from dotenv import load_dotenv
import openai

from utils import extract_title_and_content, is_url, clean_slug, validate_slug

# Load environment variables
load_dotenv()


class SlugGenerator:
    """
    AI-powered blog post slug generator using OpenAI.
    """
    
    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize the SlugGenerator.
        
        Args:
            api_key: OpenAI API key. If None, will try to load from environment.
            max_retries: Maximum number of retry attempts for LLM calls.
            retry_delay: Base delay in seconds for exponential backoff.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter to SlugGenerator constructor."
            )
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Retry configuration
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Content limits (improved from content-analyzer)
        self.api_content_limit = 3000  # Increased from 2000
        self.prompt_preview_limit = 1500  # Increased from 500
        
        # LLM settings
        self.confidence_threshold = 0.5
        self.max_tags_per_category = 5
        
        # SEO optimization settings
        self.max_words = 6
        self.max_chars = 60
    
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
        """
        for attempt in range(self.max_retries + 1):
            try:
                return self._generate_with_openai(title, content, count)
            except Exception as e:
                if attempt == self.max_retries:
                    raise Exception(f"Failed to generate slug after {self.max_retries} retry attempts: {str(e)}")
                
                # Calculate exponential backoff delay
                delay = self.retry_delay * (2 ** attempt)
                
                # Handle different error types
                if "rate limit" in str(e).lower():
                    # Longer delay for rate limits
                    delay = delay * 2
                
                time.sleep(delay)
                continue
    
    def _generate_with_openai(self, title: str, content: str, count: int = 1) -> List[Dict]:
        """
        Use OpenAI to generate intelligent slug suggestions.
        """
        # Prepare content for analysis with improved limits
        analysis_content = content[:self.api_content_limit] if content else ""
        
        # Create prompt for OpenAI
        prompt = self._create_slug_prompt(title, analysis_content, count)
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # Upgraded model
            messages=[
                {"role": "system", "content": "You are an SEO expert specializing in creating URL-friendly blog post slugs for cross-border e-commerce content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,  # Increased for JSON response
            temperature=0.3,
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
                   slug_info.get("confidence", 0) >= self.confidence_threshold
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
    
    def _load_prompt(self, prompt_name: str) -> str:
        """
        Load prompt from external template file.
        """
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'config', 'prompts', f'{prompt_name}.txt'
        )
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    
    def _create_slug_prompt(self, title: str, content: str, count: int) -> str:
        """
        Create a well-structured prompt for OpenAI slug generation using external template.
        """
        # Load base prompt template
        base_prompt = self._load_prompt('slug_generation')
        
        # Prepare content with improved preview limit
        content_preview = content[:self.prompt_preview_limit] if content else ""
        
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
        Check if a slug meets validation criteria.
        """
        validation = validate_slug(slug)
        return validation['is_valid']
    
    def get_slug_validation(self, slug: str) -> Dict:
        """
        Get detailed validation information for a slug.
        """
        return validate_slug(slug)