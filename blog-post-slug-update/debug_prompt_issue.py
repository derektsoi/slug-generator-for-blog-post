#!/usr/bin/env python3
"""
Debug prompt configuration issues
"""

import sys
import os

sys.path.insert(0, 'src')

from slug_generator import SlugGenerator

# Simple test
api_key = os.getenv('OPENAI_API_KEY')
generator = SlugGenerator(api_key=api_key)

# Test with simple content
test_title = "英國必買童裝 JoJo Maman Bébé官網購買教學"
test_content = "Blog post about UK baby clothes shopping guide from JoJo Maman Bebe website"

print("Testing current production setup...")
print(f"Title: {test_title}")
print(f"Content: {test_content}")
print()

try:
    # Test current prompt (which should be v2)
    result = generator.generate_slug_from_content(test_title, test_content, count=2)
    print("✅ SUCCESS with current prompt:")
    print(f"Primary: {result['primary']}")
    print(f"Alternatives: {result.get('alternatives', [])}")
    
except Exception as e:
    print(f"❌ Current prompt failed: {e}")
    
    # Try with much lower confidence threshold
    print("\nTrying with confidence_threshold = 0.1...")
    generator.confidence_threshold = 0.1
    
    try:
        result = generator.generate_slug_from_content(test_title, test_content, count=2)
        print("✅ SUCCESS with lowered threshold:")
        print(f"Primary: {result['primary']}")
        print(f"Alternatives: {result.get('alternatives', [])}")
    except Exception as e:
        print(f"❌ Still failed with low threshold: {e}")
        
        # Try with no filtering at all
        print("\nTrying with confidence_threshold = 0.0...")
        generator.confidence_threshold = 0.0
        
        try:
            result = generator.generate_slug_from_content(test_title, test_content, count=2)
            print("✅ SUCCESS with no threshold:")
            print(f"Primary: {result['primary']}")
            print(f"Alternatives: {result.get('alternatives', [])}")
        except Exception as e:
            print(f"❌ Complete failure: {e}")
            print("Issue is not confidence threshold - deeper problem with prompt format")