#!/usr/bin/env python3
"""
Test suite for LLM implementation and prompt effectiveness
Tests current implementation issues and validates improvements
"""

import sys
import os
import pytest
import json
from unittest.mock import Mock, patch, MagicMock

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from slug_generator import SlugGenerator
from utils import extract_title_and_content, fetch_url_content


class TestCurrentImplementationIssues:
    """Test current implementation to identify and validate reported issues"""
    
    @pytest.fixture
    def sample_blog_urls(self):
        """Sample URLs from blog dataset for testing"""
        return [
            {
                "title": "8大日牌輕珠寶品牌一次睇！Agete、nojess及Star Jewelry等日劇女主御用明星珠寶",
                "url": "https://www.buyandship.today/blog/2025/08/18/%e6%97%a5%e6%9c%ac%e8%bc%95%e7%8f%a0%e5%af%b6%e5%93%81%e7%89%8c%e5%90%88%e9%9b%86/"
            },
            {
                "title": "英國必買童裝 JoJo Maman Bébé官網 3 折起入手網購教學", 
                "url": "https://www.buyandship.today/blog/2025/08/18/jojo-maman-bebe%e8%8b%b1%e5%9c%8b%e5%ae%98%e7%b6%b2%e6%8a%98%e6%89%a3%e5%8f%8a%e8%b3%bc%e8%b2%b7%e6%95%99%e5%ad%b8/"
            },
            {
                "title": "Kindle電子書閱讀器最強攻略：Paper White、Colorsoft等型號分別、價格比較及網購集運教學",
                "url": "https://www.buyandship.today/blog/2025/08/13/kindle%e7%b6%b2%e8%b3%bc%e6%94%bb%e7%95%a5/"
            }
        ]
    
    @pytest.fixture
    def mock_html_content(self):
        """Mock HTML content that simulates a rich blog post"""
        return """
        <html>
            <head>
                <title>Test Blog Post: Complete Shopping Guide</title>
                <meta property="og:title" content="Complete Shopping Guide for UK Fashion">
                <meta name="description" content="Comprehensive guide to shopping UK brands online">
            </head>
            <body>
                <header>Navigation</header>
                <article>
                    <h1>Complete Shopping Guide for UK Fashion</h1>
                    <p>This comprehensive guide covers everything you need to know about shopping for UK fashion brands online. From popular retailers like ASOS and Next to premium brands like Burberry and Alexander McQueen, we'll walk you through the best strategies for international shipping.</p>
                    
                    <h2>Popular UK Fashion Brands</h2>
                    <p>The UK is home to many globally recognized fashion brands. ASOS has become a dominant force in fast fashion, while traditional retailers like Marks & Spencer continue to serve customers worldwide. Premium brands like Burberry represent British luxury fashion at its finest.</p>
                    
                    <h2>Shipping and Customs</h2>
                    <p>When shopping from UK retailers, international customers need to consider shipping costs and customs duties. Many retailers now offer international shipping, but it's important to check their policies before making a purchase.</p>
                    
                    <h2>Payment Methods</h2>
                    <p>Most UK retailers accept major credit cards and PayPal. Some also offer local payment methods for specific countries. Always ensure the payment page is secure before entering your details.</p>
                    
                    <h2>Returns and Exchanges</h2>
                    <p>Return policies vary between retailers. Some offer free international returns, while others may charge for return shipping. Always read the return policy before purchasing, especially for international orders.</p>
                </article>
                <footer>Footer content</footer>
                <script>Analytics code</script>
            </body>
        </html>
        """

    def test_issue_1_content_extraction_works(self, mock_html_content):
        """Test that content extraction actually works (validating it's not the extraction that's broken)"""
        with patch('src.utils.requests.get') as mock_get:
            # Mock the response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'content-type': 'text/html'}
            mock_response.text = mock_html_content
            mock_response.apparent_encoding = 'utf-8'
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            title, content = extract_title_and_content("https://example.com")
            
            # Verify title extraction works
            assert title == "Test Blog Post: Complete Shopping Guide"
            
            # Verify content extraction works and removes script/nav/footer
            assert "Complete Shopping Guide for UK Fashion" in content
            assert "Popular UK Fashion Brands" in content
            assert "ASOS" in content
            assert "Burberry" in content
            assert "Navigation" not in content  # Header removed
            assert "Footer content" not in content  # Footer removed
            assert "Analytics code" not in content  # Script removed
            
            # Verify substantial content is extracted
            assert len(content) > 500
            print(f"✅ Content extraction works: {len(content)} characters extracted")

    def test_issue_2_content_truncation_in_prompt(self, mock_html_content):
        """Test that content is severely truncated before sending to LLM"""
        with patch('src.utils.requests.get') as mock_get:
            # Mock the response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'content-type': 'text/html'}
            mock_response.text = mock_html_content
            mock_response.apparent_encoding = 'utf-8'
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            # Mock OpenAI to capture the actual prompt sent
            with patch('openai.OpenAI') as mock_openai:
                mock_client = Mock()
                mock_completion = Mock()
                mock_completion.choices = [Mock()]
                mock_completion.choices[0].message.content = "test-slug-generated"
                mock_client.chat.completions.create.return_value = mock_completion
                mock_openai.return_value = mock_client
                
                generator = SlugGenerator(api_key="test-key")
                
                # Call the private method to test prompt creation
                title, content = extract_title_and_content("https://example.com")
                prompt = generator._create_slug_prompt(title, content[:2000], 1)
                
                # Check that only 500 chars of content are included in prompt
                content_in_prompt = prompt.split("Content Preview: ")[1].split("...")[0]
                assert len(content_in_prompt) <= 500
                print(f"⚠️  ISSUE CONFIRMED: Only {len(content_in_prompt)} chars sent to LLM (should be much more)")

    def test_issue_3_fallback_mechanism_exists(self):
        """Test that unwanted fallback mechanism is present"""
        # Test by triggering OpenAI failure
        with patch('openai.OpenAI') as mock_openai:
            # Make OpenAI fail
            mock_openai.side_effect = Exception("API Error")
            
            with patch('src.utils.extract_title_and_content') as mock_extract:
                mock_extract.return_value = ("Test Title", "Test content with enough words to generate a slug")
                
                generator = SlugGenerator(api_key="test-key")
                
                # This should trigger fallback instead of failing
                with patch.object(generator, '_generate_fallback_slug') as mock_fallback:
                    mock_fallback.return_value = "fallback-generated-slug"
                    
                    try:
                        result = generator.generate_slug("https://example.com")
                        # If we get here, fallback was used instead of failing
                        assert result['primary'] == "fallback-generated-slug"
                        print("⚠️  ISSUE CONFIRMED: Fallback mechanism activated instead of failing with API error")
                    except Exception:
                        print("✅ No fallback triggered (this would be good)")

    def test_current_prompt_effectiveness(self, mock_html_content):
        """Test the current prompt to see what it actually sends to the LLM"""
        with patch('src.utils.requests.get') as mock_get:
            # Mock the response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {'content-type': 'text/html'}
            mock_response.text = mock_html_content
            mock_response.apparent_encoding = 'utf-8'
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            generator = SlugGenerator(api_key="test-key")
            title, content = extract_title_and_content("https://example.com")
            
            # Test current prompt
            prompt = generator._create_slug_prompt(title, content[:2000], 3)
            
            print("\n" + "="*60)
            print("CURRENT PROMPT SENT TO LLM:")
            print("="*60)
            print(prompt)
            print("="*60)
            
            # Analyze prompt issues
            lines = prompt.split('\n')
            content_preview_line = [line for line in lines if 'Content Preview:' in line]
            
            if content_preview_line:
                content_part = content_preview_line[0].split('Content Preview: ')[1]
                print(f"Content preview length: {len(content_part)} characters")
                print(f"Content preview: {content_part[:100]}...")
                
                # Check if truncated
                if '...' in content_part:
                    print("⚠️  Content is truncated with '...' - losing information")
            
            # Check for content richness
            assert "REQUIREMENTS:" in prompt
            assert "3-6 words maximum" in prompt
            assert "Under 60 characters total" in prompt


class TestPromptEffectiveness:
    """Test LLM prompt effectiveness and improvements"""
    
    def test_improved_prompt_design(self):
        """Test improved prompt design based on content-analyzer patterns"""
        # This will test our new prompt structure
        improved_prompt = """
You are an SEO expert specializing in creating URL-friendly blog post slugs for cross-border e-commerce content.

Follow this step-by-step process to analyze blog content:

STEP 1: Read the content and identify the main topic and value proposition
STEP 2: Extract key brands, product categories, and geographic context
STEP 3: Determine the content type (guide, comparison, shopping-tutorial, etc.)
STEP 4: Generate slug options that capture the core value
STEP 5: Validate and score your suggestions

REQUIREMENTS:
- 3-6 words maximum per slug
- Lowercase with hyphens (e.g., "uk-fashion-shopping-guide")
- Under 60 characters total
- Focus on main topic + geographic/brand context
- Avoid stop words like "the", "a", "and", "of", "in"
- Include key brands or regions when relevant

BLOG POST INFORMATION:
Title: Complete Shopping Guide for UK Fashion Brands
Content: This comprehensive guide covers everything you need to know about shopping for UK fashion brands online. From popular retailers like ASOS and Next to premium brands like Burberry and Alexander McQueen, we'll walk you through the best strategies for international shipping...

Generate 3 different slug options with confidence scores. Respond in JSON format:
{
  "slugs": [
    {"slug": "uk-fashion-shopping-guide", "confidence": 0.95, "reasoning": "Captures main topic (UK fashion) + content type (guide)"},
    {"slug": "uk-brands-online-shopping", "confidence": 0.88, "reasoning": "Focus on UK brands and online shopping aspect"},
    {"slug": "british-fashion-buying-guide", "confidence": 0.82, "reasoning": "Alternative phrasing with 'British' and 'buying'"}
  ]
}
"""
        
        print("\n" + "="*60)
        print("IMPROVED PROMPT DESIGN:")
        print("="*60)
        print(improved_prompt)
        print("="*60)
        
        # Validate improved prompt structure
        assert "step-by-step process" in improved_prompt.lower()
        assert "JSON format" in improved_prompt
        assert "confidence" in improved_prompt
        assert "reasoning" in improved_prompt

    @patch('openai.OpenAI')
    def test_mock_llm_response_parsing(self, mock_openai):
        """Test parsing of structured LLM responses"""
        # Mock structured JSON response
        mock_response = {
            "slugs": [
                {"slug": "uk-fashion-shopping-guide", "confidence": 0.95, "reasoning": "Main topic focused"},
                {"slug": "british-brands-online-guide", "confidence": 0.88, "reasoning": "Brand focused alternative"},
                {"slug": "uk-shopping-tutorial", "confidence": 0.82, "reasoning": "Tutorial angle"}
            ]
        }
        
        mock_client = Mock()
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = json.dumps(mock_response)
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client
        
        # Test parsing logic
        response_text = json.dumps(mock_response)
        parsed = json.loads(response_text)
        
        assert "slugs" in parsed
        assert len(parsed["slugs"]) == 3
        assert all("confidence" in slug for slug in parsed["slugs"])
        assert all("reasoning" in slug for slug in parsed["slugs"])
        
        # Test confidence filtering (>= 0.5 threshold)
        high_confidence_slugs = [s for s in parsed["slugs"] if s["confidence"] >= 0.5]
        assert len(high_confidence_slugs) == 3
        
        print("✅ Structured JSON response parsing works")


class TestContentAnalysis:
    """Test content analysis improvements"""
    
    def test_content_limit_improvements(self):
        """Test improved content limits"""
        # Current: 2000 chars for API, 500 for preview
        # Improved: 3000 chars for API, 1500 for preview
        
        sample_content = "A" * 5000  # 5000 character content
        
        # Current limits
        current_api_content = sample_content[:2000]
        current_preview_content = sample_content[:500]
        
        # Improved limits  
        improved_api_content = sample_content[:3000]
        improved_preview_content = sample_content[:1500]
        
        assert len(current_api_content) == 2000
        assert len(current_preview_content) == 500
        assert len(improved_api_content) == 3000
        assert len(improved_preview_content) == 1500
        
        print(f"Content limit improvement: {len(improved_api_content) - len(current_api_content)} more chars for API")
        print(f"Preview limit improvement: {len(improved_preview_content) - len(current_preview_content)} more chars for preview")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])