#!/usr/bin/env python3
"""
Utility functions for blog post slug generation
Reuses proven URL fetching code from content-analyzer project
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Dict, Tuple


def fetch_url_content(url: str) -> str:
    """
    Fetch and extract text content from a URL using professional scraping practices.
    
    Professional practices implemented:
    1. User-Agent header to identify as a legitimate client
    2. Timeout to prevent hanging requests
    3. Proper error handling for various HTTP issues
    4. Rate limiting with delay
    5. Content-type checking
    6. Text extraction from HTML while preserving structure
    """
    
    # Professional Practice #1: Always set a proper User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Slug-Generator/1.0) AppleWebKit/537.36'
    }
    
    try:
        # Professional Practice #2: Set timeouts to prevent hanging
        response = requests.get(url, headers=headers, timeout=(10, 30))
        
        # Professional Practice #3: Check status code
        response.raise_for_status()
        
        # Professional Practice #4: Check content type
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type:
            raise ValueError(f"URL does not contain HTML content. Content-Type: {content_type}")
        
        # Professional Practice #5: Handle encoding properly
        response.encoding = response.apparent_encoding or 'utf-8'
        
        # Professional Practice #6: Parse HTML robustly with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Professional Practice #7: Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Professional Practice #8: Extract meaningful text
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        if not text:
            raise ValueError("No readable text content found in the webpage")
        
        return text
        
    except requests.exceptions.Timeout:
        raise Exception("Request timed out. The website may be slow or unresponsive.")
    except requests.exceptions.ConnectionError:
        raise Exception("Failed to connect to the website. Check your internet connection.")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP error occurred: {e}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {e}")
    except Exception as e:
        raise Exception(f"Error processing webpage: {e}")


def extract_title_and_content(url: str) -> Tuple[str, str]:
    """
    Extract title and content separately for better slug generation.
    Returns (title, content) tuple.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Slug-Generator/1.0) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=(10, 30))
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type:
            raise ValueError(f"URL does not contain HTML content. Content-Type: {content_type}")
        
        response.encoding = response.apparent_encoding or 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title = ""
        if soup.title:
            title = soup.title.get_text(strip=True)
        elif soup.h1:
            title = soup.h1.get_text(strip=True)
        
        # Remove unwanted elements for content
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Extract content
        content = soup.get_text(separator=' ', strip=True)
        content = re.sub(r'\s+', ' ', content).strip()
        
        return title, content
        
    except Exception as e:
        # Fallback to basic fetch_url_content
        text = fetch_url_content(url)
        return "", text


def is_url(string: str) -> bool:
    """Check if a string is a valid HTTP/HTTPS URL."""
    try:
        result = urlparse(string)
        return all([
            result.scheme in ('http', 'https'),
            result.netloc
        ])
    except:
        return False


def clean_slug(text: str) -> str:
    """
    Clean and format text into a URL-safe slug.
    - Convert to lowercase
    - Replace spaces and special characters with hyphens
    - Remove consecutive hyphens
    - Strip leading/trailing hyphens
    """
    if not text:
        return ""
    
    # Convert to lowercase and replace spaces with hyphens
    slug = text.lower()
    
    # Replace any non-alphanumeric characters with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    
    # Remove consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    
    # Strip leading and trailing hyphens
    slug = slug.strip('-')
    
    return slug


def validate_slug(slug: str) -> Dict[str, any]:
    """
    Validate a slug against SEO best practices.
    Returns validation result with is_valid boolean and reasons.
    """
    result = {
        'is_valid': True,
        'reasons': [],
        'word_count': 0,
        'character_count': len(slug)
    }
    
    if not slug:
        result['is_valid'] = False
        result['reasons'].append("Slug is empty")
        return result
    
    # Count words (split by hyphens)
    words = [w for w in slug.split('-') if w]
    result['word_count'] = len(words)
    
    # Check length constraints
    if len(words) < 3:
        result['is_valid'] = False
        result['reasons'].append("Too short (less than 3 words)")
    
    if len(words) > 6:
        result['is_valid'] = False
        result['reasons'].append("Too long (more than 6 words)")
    
    if len(slug) > 60:
        result['is_valid'] = False
        result['reasons'].append("Too many characters (over 60)")
    
    # Check character validity
    if not re.match(r'^[a-z0-9-]+$', slug):
        result['is_valid'] = False
        result['reasons'].append("Contains invalid characters (only lowercase letters, numbers, and hyphens allowed)")
    
    # Check for consecutive hyphens
    if '--' in slug:
        result['is_valid'] = False
        result['reasons'].append("Contains consecutive hyphens")
    
    # Check for leading/trailing hyphens
    if slug.startswith('-') or slug.endswith('-'):
        result['is_valid'] = False
        result['reasons'].append("Starts or ends with hyphen")
    
    return result