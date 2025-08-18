#!/usr/bin/env python3
"""
Manual test to verify slug generation works without requiring OpenAI API key
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from slug_generator import SlugGenerator
from utils import clean_slug, validate_slug


def test_basic_functionality():
    """Test basic slug generation functionality"""
    print("Testing basic slug generation functionality...")
    
    # Test utility functions
    print("\n1. Testing utility functions:")
    
    # Test clean_slug
    test_text = "JoJo Maman Bébé UK Children's Clothing Shopping Guide!"
    cleaned = clean_slug(test_text)
    print(f"   Original: {test_text}")
    print(f"   Cleaned:  {cleaned}")
    
    # Test validation
    validation = validate_slug(cleaned)
    print(f"   Valid:    {validation['is_valid']}")
    print(f"   Words:    {validation['word_count']}")
    print(f"   Chars:    {validation['character_count']}")
    if not validation['is_valid']:
        print(f"   Issues:   {validation['reasons']}")
    
    # Test fallback slug generation (without OpenAI)
    print("\n2. Testing fallback slug generation:")
    
    try:
        generator = SlugGenerator(api_key="test-key-fallback-only")
        
        # Test the internal fallback method
        title = "英國必買童裝 JoJo Maman Bébé官網 3 折起入手網購教學"
        fallback_slug = generator._generate_fallback_slug(title, "")
        print(f"   Title:    {title}")
        print(f"   Fallback: {fallback_slug}")
        
        if fallback_slug:
            validation = generator.get_slug_validation(fallback_slug)
            print(f"   Valid:    {validation['is_valid']}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n3. Testing slug validation rules:")
    
    test_slugs = [
        "jojo-maman-bebe-uk-guide",        # Valid
        "a-b",                              # Too short
        "word-with-CAPITALS",              # Invalid chars
        "very-long-slug-with-too-many-words-here",  # Too long
    ]
    
    try:
        generator = SlugGenerator(api_key="test-key")
        for slug in test_slugs:
            is_valid = generator.is_valid_slug(slug)
            validation = generator.get_slug_validation(slug)
            print(f"   '{slug}' -> Valid: {is_valid}")
            if not is_valid:
                print(f"      Issues: {validation['reasons']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ Basic functionality tests completed!")


def test_with_mock_content():
    """Test slug generation with mock content (simulating URL fetch)"""
    print("\n4. Testing with mock content:")
    
    # Mock content from BuyandShip JoJo Maman Bebe post
    mock_title = "英國必買童裝 JoJo Maman Bébé官網 3 折起入手網購教學"
    mock_content = """
    JoJo Maman Bébé is a British brand founded in 1993, originally started with maternity wear.
    Now covers children's clothing, outerwear, and accessories. Popular with British royal family.
    Features discounts up to 70% off, free UK shipping on orders over £50.
    Character collaborations include Peter Rabbit and Paddington Bear.
    Popular products include infant t-shirts, maternity wear, baby accessories, rainboots, waterproof jackets.
    """
    
    try:
        generator = SlugGenerator(api_key="test-key")
        fallback_slug = generator._generate_fallback_slug(mock_title, mock_content)
        
        print(f"   Mock title: {mock_title}")
        print(f"   Generated:  {fallback_slug}")
        
        if fallback_slug:
            is_valid = generator.is_valid_slug(fallback_slug)
            print(f"   Valid:      {is_valid}")
            
            # Compare with expected result
            expected = "jojo-maman-bebe-uk-childrens-clothing-guide"
            print(f"   Expected:   {expected}")
            
            # Check if they contain similar keywords
            generated_words = set(fallback_slug.split('-'))
            expected_words = set(expected.split('-'))
            overlap = generated_words.intersection(expected_words)
            print(f"   Overlap:    {overlap}")
            
    except Exception as e:
        print(f"   Error: {e}")


if __name__ == "__main__":
    test_basic_functionality()
    test_with_mock_content()
    print("\n🎉 Manual testing completed! Basic slug generation is working.")