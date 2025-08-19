import unittest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# These imports will fail initially - that's expected!
try:
    from seo_generator import SEOGenerator
    from character_limit_handler import CharacterLimitHandler
except ImportError:
    SEOGenerator = None
    CharacterLimitHandler = None


class TestSEOGenerator(unittest.TestCase):
    """Test cases for SEO package generation - THESE WILL FAIL INITIALLY"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = SEOGenerator() if SEOGenerator else None
        
        # Sample content analysis data
        self.sample_analysis = {
            'decoded_url_slug': '日本輕珠寶品牌合集',
            'brands': ['Agete', 'nojess', 'Star Jewelry'],
            'category': 'jewelry',
            'content_type': 'guide',
            'evergreen_keywords': ['japanese', 'jewelry', 'brands', 'guide'],
            'promo_terms': [],
            'has_promo': False
        }
        
        self.sample_analysis_with_promo = {
            'decoded_url_slug': 'jojo-maman-bebe英國官網折扣及購買教學',
            'brands': ['JoJo Maman Bébé'],
            'category': 'baby-fashion', 
            'content_type': 'shopping-guide',
            'evergreen_keywords': ['uk', 'baby', 'clothes', 'shopping', 'guide'],
            'promo_terms': ['3 折起', '折扣'],
            'has_promo': True
        }
    
    @unittest.skipIf(SEOGenerator is None, "SEOGenerator not implemented yet")
    def test_slug_generation_requirements(self):
        """Test slug meets all requirements - WILL FAIL"""
        region = "Hong Kong"
        
        result = self.generator.generate_seo_package(self.sample_analysis, region)
        
        slug = result['slug']
        
        # Test all slug requirements
        self.assertLessEqual(len(slug), 60, f"Slug too long: {len(slug)} chars")
        self.assertTrue(slug.islower(), "Slug must be lowercase")
        self.assertRegex(slug, r'^[a-z0-9-]+$', "Slug contains invalid characters")
        self.assertNotIn('--', slug, "Slug contains double hyphens")
        self.assertFalse(slug.startswith('-'), "Slug starts with hyphen")
        self.assertFalse(slug.endswith('-'), "Slug ends with hyphen")
        
        # Must contain region
        self.assertIn('hong-kong', slug, "Slug must contain region")
        
        # Must contain at least one main keyword
        main_keywords = ['japanese', 'jewelry', 'brands']
        self.assertTrue(any(keyword in slug for keyword in main_keywords), 
                       "Slug must contain main keywords")
    
    @unittest.skipIf(SEOGenerator is None, "SEOGenerator not implemented yet")
    def test_title_requirements(self):
        """Test title meets all requirements - WILL FAIL"""
        region = "Singapore"
        
        result = self.generator.generate_seo_package(self.sample_analysis, region)
        
        title = result['title']
        
        # Character limit
        self.assertLessEqual(len(title), 60, f"Title too long: {len(title)} chars")
        
        # Must contain region
        self.assertIn('Singapore', title, "Title must contain region")
        
        # Must be human-friendly (not just keywords)
        self.assertRegex(title, r'^[A-Z]', "Title should start with capital letter")
        self.assertNotRegex(title, r'^[a-z-]+$', "Title shouldn't be just slug-like")
        
        # Should contain brand or main topic
        brands = self.sample_analysis['brands']
        keywords = self.sample_analysis['evergreen_keywords']
        
        title_lower = title.lower()
        has_brand_or_keyword = any(brand.lower() in title_lower for brand in brands) or \
                              any(keyword in title_lower for keyword in keywords)
        
        self.assertTrue(has_brand_or_keyword, "Title must contain brands or keywords")
    
    @unittest.skipIf(SEOGenerator is None, "SEOGenerator not implemented yet")
    def test_meta_description_requirements(self):
        """Test meta description meets all requirements - WILL FAIL"""
        region = "Australia"
        
        result = self.generator.generate_seo_package(self.sample_analysis, region)
        
        meta = result['meta_description']
        
        # Character limit
        self.assertLessEqual(len(meta), 155, f"Meta description too long: {len(meta)} chars")
        
        # Must contain region
        self.assertIn('Australia', meta, "Meta description must contain region")
        
        # Should contain a call-to-action
        cta_phrases = ['shop', 'buy', 'discover', 'get', 'find', 'explore', 'browse']
        meta_lower = meta.lower()
        has_cta = any(phrase in meta_lower for phrase in cta_phrases)
        self.assertTrue(has_cta, "Meta description must contain call-to-action")
        
        # Should be benefit-focused, not just description
        benefit_indicators = ['with', 'for', 'from', 'save', 'free', 'easy', 'best']
        has_benefit = any(indicator in meta_lower for indicator in benefit_indicators)
        self.assertTrue(has_benefit, "Meta description should highlight benefits")
    
    @unittest.skipIf(SEOGenerator is None, "SEOGenerator not implemented yet")
    def test_promo_handling_in_title_meta_not_slug(self):
        """Test promotional terms handled correctly - WILL FAIL"""
        region = "Hong Kong"
        
        result = self.generator.generate_seo_package(self.sample_analysis_with_promo, region)
        
        slug = result['slug']
        title = result['title']
        meta = result['meta_description']
        
        # Slug should NOT contain promo terms (evergreen requirement)
        promo_terms = ['discount', 'sale', 'off', '折', 'promo']
        slug_lower = slug.lower()
        has_promo_in_slug = any(term in slug_lower for term in promo_terms)
        self.assertFalse(has_promo_in_slug, "Slug must not contain promotional terms")
        
        # Title and meta CAN contain promo terms for click optimization
        # (This is acceptable behavior, not a requirement to test)
    
    @unittest.skipIf(SEOGenerator is None, "SEOGenerator not implemented yet")
    def test_region_variations_create_unique_content(self):
        """Test different regions create different content - WILL FAIL"""
        regions = ["Hong Kong", "Singapore", "Australia"]
        results = {}
        
        for region in regions:
            result = self.generator.generate_seo_package(self.sample_analysis, region)
            results[region] = result
        
        # All slugs should be different (contain different regions)
        slugs = [results[region]['slug'] for region in regions]
        self.assertEqual(len(slugs), len(set(slugs)), "All slugs should be unique")
        
        # Each should contain its respective region
        for region in regions:
            region_in_slug = region.lower().replace(' ', '-')
            self.assertIn(region_in_slug, results[region]['slug'])
            self.assertIn(region, results[region]['title'])
            self.assertIn(region, results[region]['meta_description'])
    
    @unittest.skipIf(SEOGenerator is None, "SEOGenerator not implemented yet")
    def test_complete_package_structure(self):
        """Test complete SEO package has all required fields - WILL FAIL"""
        region = "Malaysia"
        
        result = self.generator.generate_seo_package(self.sample_analysis, region)
        
        # Check all required fields are present
        required_fields = ['slug', 'title', 'meta_description']
        for field in required_fields:
            self.assertIn(field, result)
            self.assertIsInstance(result[field], str)
            self.assertGreater(len(result[field]), 0, f"{field} cannot be empty")
        
        # Optional fields that might be included
        optional_fields = ['confidence_score', 'keywords_used', 'character_counts']
        # These don't need to be present, but if they are, check their types
        for field in optional_fields:
            if field in result:
                self.assertIsNotNone(result[field])


class TestCharacterLimitHandler(unittest.TestCase):
    """Test character limit handling strategies - THESE WILL FAIL INITIALLY"""
    
    @unittest.skipIf(CharacterLimitHandler is None, "CharacterLimitHandler not implemented yet")
    def test_retry_shorter_mode(self):
        """Test retry with shorter target works - WILL FAIL"""
        handler = CharacterLimitHandler(mode="retry_shorter")
        
        # Mock LLM call for shortening
        with patch('seo_generator.llm_call_with_retry') as mock_llm:
            mock_llm.return_value = "shortened-version"
            
            over_limit_content = "a" * 70  # Over 60 char limit
            result = handler.handle_over_limit(over_limit_content, 60, "slug")
            
            self.assertEqual(result, "shortened-version")
            mock_llm.assert_called_once()
    
    @unittest.skipIf(CharacterLimitHandler is None, "CharacterLimitHandler not implemented yet")
    def test_truncate_mode(self):
        """Test truncation mode works - WILL FAIL"""
        handler = CharacterLimitHandler(mode="truncate")
        
        over_limit_content = "this-is-a-very-long-slug-that-exceeds-the-limit-by-quite-a-bit"
        result = handler.handle_over_limit(over_limit_content, 40, "slug")
        
        self.assertLessEqual(len(result), 40)
        self.assertFalse(result.endswith('-'), "Truncated slug shouldn't end with hyphen")
    
    @unittest.skipIf(CharacterLimitHandler is None, "CharacterLimitHandler not implemented yet")
    def test_hard_fail_mode(self):
        """Test hard fail mode raises exception - WILL FAIL"""
        handler = CharacterLimitHandler(mode="hard_fail")
        
        over_limit_content = "a" * 70
        
        with self.assertRaises(ValueError):
            handler.handle_over_limit(over_limit_content, 60, "slug")


if __name__ == '__main__':
    unittest.main()