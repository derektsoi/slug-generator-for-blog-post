#!/usr/bin/env python3
"""
Blog Post Slug Generator with OpenAI Integration
Generates SEO-friendly slugs from blog post URLs using AI
"""

import os
import re
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
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the SlugGenerator.
        
        Args:
            api_key: OpenAI API key. If None, will try to load from environment.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter to SlugGenerator constructor."
            )
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # SEO optimization settings
        self.max_words = 6
        self.max_chars = 60
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
    
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
            
            # Generate slug using OpenAI
            slug_suggestions = self._generate_with_openai(title, content, count)
            
            # Validate and clean suggestions
            cleaned_suggestions = []
            for suggestion in slug_suggestions:
                cleaned = clean_slug(suggestion)
                if cleaned and self.is_valid_slug(cleaned):
                    cleaned_suggestions.append(cleaned)
            
            if not cleaned_suggestions:
                # Fallback to basic generation if OpenAI fails
                fallback_slug = self._generate_fallback_slug(title, content)
                cleaned_suggestions = [fallback_slug] if fallback_slug else []
            
            if not cleaned_suggestions:
                raise Exception("Unable to generate valid slug from content")
            
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
    
    def _generate_with_openai(self, title: str, content: str, count: int = 1) -> List[str]:
        """
        Use OpenAI to generate intelligent slug suggestions.
        """
        # Prepare content for analysis (limit length to avoid token limits)
        analysis_content = content[:2000] if content else ""
        
        # Create prompt for OpenAI
        prompt = self._create_slug_prompt(title, analysis_content, count)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an SEO expert specializing in creating URL-friendly blog post slugs."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            # Parse response
            suggestions_text = response.choices[0].message.content.strip()
            
            # Extract individual suggestions (assuming they're separated by newlines or commas)
            suggestions = []
            for line in suggestions_text.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-'):
                    # Remove any numbering or bullets
                    line = re.sub(r'^\d+[\.\)]\s*', '', line)
                    line = re.sub(r'^[\-\*]\s*', '', line)
                    suggestions.append(line.strip())
            
            # If no newlines, try comma separation
            if len(suggestions) <= 1 and ',' in suggestions_text:
                suggestions = [s.strip() for s in suggestions_text.split(',')]
            
            return suggestions[:count] if suggestions else [suggestions_text]
            
        except Exception as e:
            if "rate limit" in str(e).lower():
                raise Exception("OpenAI rate limit exceeded. Please try again later.")
            else:
                raise Exception(f"OpenAI API request failed: {str(e)}")
    
    def _create_slug_prompt(self, title: str, content: str, count: int) -> str:
        """
        Create a well-structured prompt for OpenAI slug generation.
        """
        prompt = f"""
Generate {count} SEO-friendly URL slug{'s' if count > 1 else ''} for this blog post.

REQUIREMENTS:
- 3-6 words maximum
- Lowercase with hyphens (e.g., "best-react-hooks-guide")
- Under 60 characters total
- Descriptive and keyword-rich
- No stop words like "the", "a", "and", "of", "in"
- Focus on the main topic/value proposition

BLOG POST INFORMATION:
Title: {title}
Content Preview: {content[:500]}...

{"Please provide " + str(count) + " different slug options, one per line:" if count > 1 else "Provide the best slug:"}
"""
        return prompt.strip()
    
    def _generate_fallback_slug(self, title: str, content: str) -> Optional[str]:
        """
        Fallback slug generation without OpenAI (enhanced keyword extraction).
        """
        # Combine title and some content for better keyword extraction
        combined_text = title
        if content:
            combined_text += " " + content[:300]
        
        if not combined_text:
            return None
        
        # Enhanced keyword extraction that handles mixed languages
        # Extract English words (3+ letters) and brand names
        english_words = re.findall(r'\b[a-zA-Z]{3,}\b', combined_text)
        
        # Also extract common brand patterns and important terms
        brand_patterns = re.findall(r'\b(?:jojo|maman|bebe|kindle|amazon|uk|japan|korea)\b', combined_text.lower())
        
        # Combine and clean
        all_words = [w.lower() for w in english_words] + brand_patterns
        
        # Filter out stop words and duplicates
        keywords = []
        seen = set()
        for word in all_words:
            if word not in self.stop_words and word not in seen and len(word) >= 3:
                keywords.append(word)
                seen.add(word)
        
        # Prioritize brand names and important terms
        priority_terms = ['jojo', 'maman', 'bebe', 'kindle', 'amazon', 'uk', 'japan', 'guide', 'shopping']
        priority_keywords = [k for k in keywords if k in priority_terms]
        other_keywords = [k for k in keywords if k not in priority_terms]
        
        # Combine with priority terms first
        selected_keywords = priority_keywords[:4] + other_keywords[:2]
        
        # Ensure we have at least 3 words
        if len(selected_keywords) < 3:
            selected_keywords = keywords[:5]  # Take more if needed
        
        if not selected_keywords:
            return None
        
        # Create and clean slug
        slug = '-'.join(selected_keywords[:6])  # Max 6 words
        return clean_slug(slug)
    
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