"""
Integration Tests for Real API Evaluation

Tests the complete system with real OpenAI API calls.
Requires valid API key - marked with pytest.mark.requires_api_key
"""

import pytest
import os
import sys
import time
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from evaluation.core.seo_evaluator_clean import SEOEvaluator
from evaluation.core.evaluation_coordinator import EvaluationCoordinator
from evaluation.utils.exceptions import InvalidAPIKeyError, LLMUnavailableError
from evaluation.utils.retry_logic import RetryConfig


# Skip all tests if no API key available
def get_api_key():
    """Get API key from environment or .env file"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        try:
            # Try to load from .env file
            import dotenv
            dotenv.load_dotenv()
            api_key = os.getenv('OPENAI_API_KEY')
        except ImportError:
            pass
    return api_key


API_KEY = get_api_key()
requires_api_key = pytest.mark.skipif(
    not API_KEY or API_KEY == "test-key",
    reason="Requires valid OPENAI_API_KEY environment variable"
)


@requires_api_key
class TestRealLLMEvaluation:
    """Test LLM evaluation with real API calls"""
    
    def setup_method(self):
        """Set up test fixtures with real API key"""
        self.evaluator = SEOEvaluator(
            api_key=API_KEY,
            retry_config=RetryConfig(max_retries=2, base_delay=0.5)
        )
        
        # Real test cases from V6/V7/V8 development
        self.test_cases = {
            'v8_breakthrough': {
                'slug': 'skinnydip-iface-rhinoshield-phone-cases-guide',
                'title': '日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！',
                'content': '本文將介紹來自日韓台的7大手機殼品牌，包括SKINNIYDIP、iface、犀牛盾等知名品牌的iPhone16/Pro手機殼新品。'
            },
            'v6_cultural': {
                'slug': 'ichiban-kuji-anime-japan-guide',
                'title': '【2025年最新】日本一番賞Online手把手教學！',
                'content': '詳細教學如何在日本一番賞Online平台購買動漫周邊商品，包括註冊流程、購買步驟等完整指南。'
            },
            'brand_focus': {
                'slug': 'jojo-maman-bebe-maternity-clothes-guide',
                'title': 'JoJo Maman Bébé maternity clothes shopping guide',
                'content': 'Comprehensive guide to shopping for JoJo Maman Bébé maternity wear, including sizing, styles, and best deals.'
            }
        }

    def test_real_llm_evaluation_structure(self):
        """Test real LLM evaluation returns proper structure"""
        
        case = self.test_cases['v8_breakthrough']
        
        result = self.evaluator.evaluate_slug(
            case['slug'],
            case['title'], 
            case['content']
        )
        
        # Verify structure
        assert result['analysis_type'] == 'llm_qualitative'
        assert 'overall_score' in result
        assert 'dimension_scores' in result
        assert 'qualitative_feedback' in result
        assert 'confidence' in result
        
        # Verify all dimensions present
        expected_dimensions = [
            'user_intent_match', 'brand_hierarchy', 'cultural_authenticity',
            'click_through_potential', 'competitive_differentiation', 'technical_seo'
        ]
        for dim in expected_dimensions:
            assert dim in result['dimension_scores']
            assert 0.0 <= result['dimension_scores'][dim] <= 1.0
        
        # Verify qualitative feedback is substantial
        assert len(result['qualitative_feedback']) > 100
        assert isinstance(result['qualitative_feedback'], str)

    def test_v8_breakthrough_recognition(self):
        """Test real LLM recognizes V8 breakthrough quality"""
        
        case = self.test_cases['v8_breakthrough']
        
        result = self.evaluator.evaluate_slug(
            case['slug'],
            case['title'],
            case['content']
        )
        
        # Should score highly overall
        assert result['overall_score'] > 0.7
        
        # Should excel in brand hierarchy (multi-brand case)
        assert result['dimension_scores']['brand_hierarchy'] > 0.7
        
        # Should have good technical SEO
        assert result['dimension_scores']['technical_seo'] > 0.6
        
        # Qualitative feedback should mention brands
        feedback = result['qualitative_feedback'].lower()
        assert any(brand in feedback for brand in ['skinniydip', 'iface', 'rhinoshield', 'brand'])

    def test_cultural_authenticity_assessment(self):
        """Test real LLM assesses cultural authenticity"""
        
        case = self.test_cases['v6_cultural']
        
        result = self.evaluator.evaluate_slug(
            case['slug'],
            case['title'],
            case['content']
        )
        
        # Should score well on cultural authenticity
        assert result['dimension_scores']['cultural_authenticity'] > 0.7
        
        # Should recognize cultural term preservation
        feedback = result['qualitative_feedback'].lower()
        assert any(term in feedback for term in ['ichiban', 'cultural', 'authentic', 'japanese'])

    def test_brand_hierarchy_assessment(self):
        """Test real LLM assesses brand hierarchy properly"""
        
        case = self.test_cases['brand_focus']
        
        result = self.evaluator.evaluate_slug(
            case['slug'],
            case['title'],
            case['content']
        )
        
        # Should score well on brand hierarchy
        assert result['dimension_scores']['brand_hierarchy'] > 0.7
        
        # Feedback should mention brand
        feedback = result['qualitative_feedback'].lower()
        assert any(term in feedback for term in ['jojo', 'brand', 'hierarchy'])

    def test_comparative_assessment(self):
        """Test LLM can distinguish quality differences"""
        
        # Test high-quality vs poor-quality slugs
        good_case = self.test_cases['v8_breakthrough']
        
        good_result = self.evaluator.evaluate_slug(
            good_case['slug'],
            good_case['title'],
            good_case['content']
        )
        
        # Poor quality slug for same content
        poor_result = self.evaluator.evaluate_slug(
            'phone-case-guide',  # Generic, loses brand info
            good_case['title'],
            good_case['content']
        )
        
        # Good slug should score higher
        assert good_result['overall_score'] > poor_result['overall_score']
        assert good_result['dimension_scores']['brand_hierarchy'] > poor_result['dimension_scores']['brand_hierarchy']

    def test_failure_case_analysis(self):
        """Test real LLM analyzes failure cases"""
        
        failure_result = self.evaluator.evaluate_failure_case(
            title='日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！',
            content='Complex multi-brand comparison with special characters',
            failure_reason='exceeded_word_constraints'
        )
        
        # Should provide failure analysis
        assert failure_result['analysis_type'] == 'failure_analysis'
        assert 'failure_analysis' in failure_result
        assert len(failure_result['qualitative_feedback']) > 50

    def test_retry_behavior_with_rate_limiting(self):
        """Test retry behavior (may trigger rate limits intentionally)"""
        
        # Make rapid consecutive calls to potentially trigger rate limiting
        case = self.test_cases['brand_focus']
        
        results = []
        for i in range(3):  # Multiple rapid calls
            try:
                result = self.evaluator.evaluate_slug(
                    case['slug'],
                    case['title'],
                    case['content']
                )
                results.append(result)
                
                # Brief delay to be respectful
                time.sleep(0.1)
                
            except LLMUnavailableError as e:
                # Rate limiting or other API issues are acceptable
                pytest.skip(f"API unavailable during test: {e}")
        
        # At least one call should succeed
        assert len(results) >= 1
        
        # Results should be consistent in structure
        for result in results:
            assert result['analysis_type'] == 'llm_qualitative'
            assert 'overall_score' in result


@requires_api_key  
class TestRealEvaluationCoordinator:
    """Test evaluation coordinator with real LLM integration"""
    
    def setup_method(self):
        """Set up coordinator with real API key"""
        self.coordinator = EvaluationCoordinator(
            api_key=API_KEY,
            enable_llm=True,
            retry_config=RetryConfig(max_retries=2, base_delay=0.5)
        )

    def test_comprehensive_real_evaluation(self):
        """Test complete evaluation with both quantitative and qualitative analysis"""
        
        result = self.coordinator.evaluate_comprehensive(
            'skinnydip-iface-rhinoshield-phone-cases-guide',
            '日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！',
            'Multi-brand phone case comparison guide with detailed analysis'
        )
        
        # Should have both analyses
        assert 'quantitative_analysis' in result
        assert 'qualitative_insights' in result
        assert result['analysis_type'] == 'complete'
        assert result['llm_available'] is True
        
        # Should have combined analysis
        assert 'combined_recommendation' in result
        assert 'meta_analysis' in result
        
        # Quantitative analysis structure
        quant = result['quantitative_analysis']
        assert quant['analysis_type'] == 'quantitative_only'
        assert 'overall_score' in quant
        
        # Qualitative analysis structure  
        qual = result['qualitative_insights']
        assert qual['analysis_type'] == 'llm_qualitative'
        assert len(qual['qualitative_feedback']) > 100

    def test_meta_analysis_insights(self):
        """Test meta-analysis combines both approaches meaningfully"""
        
        result = self.coordinator.evaluate_comprehensive(
            'jojo-maman-bebe-maternity-guide',
            'JoJo Maman Bébé maternity clothes shopping guide',
            'Comprehensive guide to JoJo Maman Bébé maternity wear'
        )
        
        meta = result['meta_analysis']
        
        # Should have dimension comparison
        assert 'dimension_comparison' in meta
        assert 'overall_agreement' in meta
        
        # Should compare overlapping dimensions
        assert 'technical_seo' in meta['dimension_comparison']
        assert 'brand_hierarchy' in meta['dimension_comparison']
        
        # Each comparison should have agreement assessment
        for dim, comp in meta['dimension_comparison'].items():
            assert 'quantitative_score' in comp
            assert 'qualitative_score' in comp
            assert 'agreement' in comp
            assert isinstance(comp['agreement'], bool)

    def test_graceful_degradation_on_llm_failure(self):
        """Test graceful degradation when LLM temporarily fails"""
        
        # Create coordinator with invalid model to force LLM failure
        coordinator_with_bad_model = EvaluationCoordinator(
            api_key=API_KEY,
            model="non-existent-model",  # Will cause API error
            enable_llm=True
        )
        
        # Should still provide quantitative analysis
        result = coordinator_with_bad_model.evaluate_comprehensive(
            'test-slug',
            'Test title',
            'Test content'
        )
        
        # Should have quantitative analysis
        assert 'quantitative_analysis' in result
        assert result['quantitative_analysis']['analysis_type'] == 'quantitative_only'
        
        # Should indicate LLM unavailable
        assert result['llm_available'] is False
        assert result['analysis_type'] == 'quantitative_only'


@requires_api_key
class TestAPIErrorHandling:
    """Test real API error handling and classification"""
    
    def test_invalid_model_error_handling(self):
        """Test handling of invalid model specification"""
        
        evaluator = SEOEvaluator(
            api_key=API_KEY,
            model="non-existent-model"
        )
        
        with pytest.raises(LLMUnavailableError):
            evaluator.evaluate_slug(
                'test-slug',
                'Test title',
                'Test content'
            )

    def test_malformed_request_handling(self):
        """Test handling of various API error conditions"""
        
        evaluator = SEOEvaluator(api_key=API_KEY)
        
        # Extremely long input that might cause issues
        very_long_content = "A" * 10000
        
        try:
            result = evaluator.evaluate_slug(
                'test-slug',
                'Test title',
                very_long_content
            )
            # If it succeeds, verify structure
            assert 'analysis_type' in result
            
        except LLMUnavailableError:
            # API errors are acceptable for edge cases
            pytest.skip("API rejected extremely long input as expected")


if __name__ == "__main__":
    # Run with API key requirement
    if not API_KEY:
        print("⚠️  No OPENAI_API_KEY found - skipping integration tests")
        print("   Set OPENAI_API_KEY environment variable to run these tests")
    else:
        print(f"🔑 Running integration tests with API key: {API_KEY[:8]}...")
        pytest.main([__file__, "-v", "--tb=short", "-m", "requires_api_key"])