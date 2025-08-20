#!/usr/bin/env python3
"""
Content extraction and web scraping functionality
Professional web scraping practices for blog post content extraction
"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Tuple


def fetch_url_content(url: str) -> str:
    """
    Fetch and extract text content from a URL using professional scraping practices.
    
    Professional practices implemented:
    1. User-Agent header to identify as a legitimate client
    2. Timeout to prevent hanging requests
    3. Proper error handling for various HTTP issues
    4. Content-type checking
    5. Text extraction from HTML while preserving structure
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