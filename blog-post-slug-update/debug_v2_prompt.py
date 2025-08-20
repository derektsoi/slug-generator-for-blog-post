#!/usr/bin/env python3
"""
Debug V2 prompt issues found by optimization tool
"""

import sys
import os
import json

sys.path.insert(0, 'src')

from slug_generator import SlugGenerator

# Test URL that fails with V2
test_url = "https://www.buyandship.today/blog/2025/08/18/jojo-maman-bebe%e8%8b%b1%e5%9c%8b%e5%ae%98%e7%b6%b2%e6%8a%98%e6%89%a3%e5%8f%8a%e8%b3%bc%e8%b2%b7%e6%95%99%e5%ad%b8/"

api_key = os.getenv('OPENAI_API_KEY')
generator = SlugGenerator(api_key=api_key, confidence_threshold=0.0)  # No filtering

try:
    # Try to get raw response to see what's happening
    from utils import extract_title_and_content
    title, content = extract_title_and_content(test_url)
    
    print(f"Title: {title}")
    print(f"Content length: {len(content)} chars")
    print()
    
    # Try generating with no confidence filtering
    result = generator.generate_slug(test_url, count=3)
    print("✅ Success with confidence_threshold=0.0")
    print(f"Primary: {result['primary']}")
    print(f"Alternatives: {result.get('alternatives', [])}")
    
except Exception as e:
    print(f"❌ Still failed: {e}")