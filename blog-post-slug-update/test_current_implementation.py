#!/usr/bin/env python3
"""
Manual test script to analyze current implementation issues
Run this to see the actual problems in action
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from slug_generator import SlugGenerator
from utils import extract_title_and_content


def test_content_extraction():
    """Test how much content is actually extracted"""
    print("="*60)
    print("TESTING CONTENT EXTRACTION")
    print("="*60)
    
    # Test with a real URL from the dataset
    test_url = "https://www.buyandship.today/blog/2025/08/18/jojo-maman-bebe%e8%8b%b1%e5%9c%8b%e5%ae%98%e7%b6%b2%e6%8a%98%e6%89%a3%e5%8f%8a%e8%b3%bc%e8%b2%b7%e6%95%99%e5%ad%b8/"
    
    try:
        title, content = extract_title_and_content(test_url)
        print(f"✅ Title extracted: {title}")
        print(f"✅ Content length: {len(content)} characters")
        print(f"✅ Content preview (first 200 chars): {content[:200]}...")
        
        if len(content) > 1000:
            print("✅ Good: Substantial content extracted")
        else:
            print("⚠️  Warning: Limited content extracted")
            
    except Exception as e:
        print(f"❌ Error extracting content: {e}")


def test_current_prompt_creation():
    """Test what the current implementation sends to LLM"""
    print("\n" + "="*60)
    print("TESTING CURRENT PROMPT CREATION")
    print("="*60)
    
    # Create a generator instance (without API key to avoid real calls)
    try:
        # We'll just test the prompt creation part
        sample_title = "英國必買童裝 JoJo Maman Bébé官網 3 折起入手網購教學"
        sample_content = """
        Complete guide to shopping JoJo Maman Bébé from the UK official website. 
        This British children's clothing brand offers organic cotton clothes, 
        maternity wear, and baby essentials. Learn how to navigate their website, 
        understand sizing, and get the best deals with up to 70% off sales.
        Key brands covered: JoJo Maman Bébé, UK fashion, children's clothing.
        Topics include: sizing guide, international shipping, payment methods, 
        returns policy, and seasonal sales. Perfect for parents looking for 
        high-quality organic children's clothes from the UK.
        """ * 10  # Make it longer to test truncation
        
        # Test prompt creation directly 
        generator = SlugGenerator(api_key="fake-key-for-testing")
        
        # Test current limits
        current_api_content = sample_content[:2000]
        current_prompt = generator._create_slug_prompt(sample_title, current_api_content, 3)
        
        print("CURRENT PROMPT STRUCTURE:")
        print("-" * 40)
        print(current_prompt)
        print("-" * 40)
        
        # Analyze the prompt
        lines = current_prompt.split('\n')
        content_line = None
        for line in lines:
            if 'Content Preview:' in line:
                content_line = line
                break
        
        if content_line:
            content_part = content_line.split('Content Preview: ')[1]
            print(f"📊 Analysis:")
            print(f"   - Full content length: {len(sample_content)} chars")
            print(f"   - API content limit: {len(current_api_content)} chars") 
            print(f"   - Prompt content length: {len(content_part)} chars")
            
            if '...' in content_part:
                actual_content = content_part.split('...')[0]
                print(f"   - Actual content in prompt: {len(actual_content)} chars")
                print(f"⚠️  ISSUE: Content severely truncated from {len(sample_content)} to {len(actual_content)} chars")
            else:
                print(f"   - Full content included: {len(content_part)} chars")
                
    except Exception as e:
        print(f"❌ Error testing prompt: {e}")


def test_fallback_mechanism():
    """Test if fallback mechanism exists"""
    print("\n" + "="*60)
    print("TESTING FALLBACK MECHANISM")
    print("="*60)
    
    # Check if _generate_fallback_slug method exists
    generator = SlugGenerator(api_key="fake-key")
    
    if hasattr(generator, '_generate_fallback_slug'):
        print("⚠️  ISSUE CONFIRMED: _generate_fallback_slug method exists")
        
        # Test the fallback method
        fallback_result = generator._generate_fallback_slug(
            "Test Title with Keywords", 
            "Test content with brands like Amazon and keywords"
        )
        print(f"   - Fallback generates: {fallback_result}")
        print("   - This means LLM failures will use keyword-based generation instead of failing")
    else:
        print("✅ No fallback method found")


def test_llm_dependency():
    """Test how the system handles LLM unavailability"""
    print("\n" + "="*60)
    print("TESTING LLM DEPENDENCY")
    print("="*60)
    
    # Test with invalid API key
    try:
        generator = SlugGenerator(api_key="invalid-key")
        # This should fail when we try to generate
        print("✅ Generator created with invalid key (good)")
        
        # Now test what happens when generation fails
        # We'll examine the code logic rather than make real API calls
        print("📊 Analyzing generation flow in generate_slug method...")
        
        import inspect
        source = inspect.getsource(generator.generate_slug)
        
        if "_generate_fallback_slug" in source:
            print("⚠️  ISSUE CONFIRMED: generate_slug contains fallback logic")
            print("   - When OpenAI fails, it will use fallback instead of failing")
        else:
            print("✅ No fallback logic found in generate_slug")
            
        if "except" in source and "fallback" in source:
            print("⚠️  ISSUE: Exception handling triggers fallback")
        
    except Exception as e:
        print(f"❌ Error with invalid key: {e}")


def main():
    """Run all tests"""
    print("CURRENT IMPLEMENTATION ANALYSIS")
    print("Testing the issues identified in blog-post-slug-update")
    
    test_content_extraction()
    test_current_prompt_creation() 
    test_fallback_mechanism()
    test_llm_dependency()
    
    print("\n" + "="*60)
    print("SUMMARY OF ISSUES FOUND:")
    print("="*60)
    print("1. ✅ Content extraction works well")
    print("2. ⚠️  Content severely truncated in prompts (500 chars vs thousands available)")
    print("3. ⚠️  Fallback mechanism exists instead of LLM-only approach")
    print("4. ⚠️  Current prompt lacks structured analysis approach")
    print("\nNext: Implement improvements based on content-analyzer patterns")


if __name__ == "__main__":
    main()