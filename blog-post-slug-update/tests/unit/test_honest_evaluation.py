"""
Test Suite for Honest Evaluation Architecture

Tests the clean separation between quantitative and qualitative analysis.
Unit tests with comprehensive mocking - no real API calls.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from evaluation.core.rule_based_analyzer import RuleBasedAnalyzer
from evaluation.core.seo_evaluator_clean import SEOEvaluator
from evaluation.core.evaluation_coordinator import EvaluationCoordinator
from evaluation.utils.exceptions import (
    InvalidAPIKeyError, APIRateLimitError, TemporaryAPIError, 
    EvaluationParsingError, classify_api_error
)


class TestRuleBasedAnalyzer:
    """Test pure quantitative analysis - no API dependencies"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = RuleBasedAnalyzer()
        
        # V8 breakthrough case
        self.v8_case = {
            'slug': 'skinnydip-iface-rhinoshield-phone-cases-guide',
            'title': '日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！',
            'content': 'Multi-brand phone case comparison guide'
        }
        
        # V6 cultural case
        self.v6_case = {
            'slug': 'ichiban-kuji-anime-japan-guide',
            'title': '【2025年最新】日本一番賞Online手把手教學！',
            'content': 'Ichiban kuji purchasing guide'
        }

    def test_rule_based_analyzer_initialization(self):
        """Test analyzer initializes without API dependencies"""
        analyzer = RuleBasedAnalyzer()
        
        assert hasattr(analyzer, 'brand_patterns')
        assert hasattr(analyzer, 'cultural_terms')
        assert hasattr(analyzer, 'generic_terms')
        assert len(analyzer.brand_patterns) > 5  # Has reasonable patterns

    def test_pure_quantitative_analysis(self):
        """Test quantitative analysis returns structured data only"""
        result = self.analyzer.analyze_slug(
            self.v8_case['slug'], 
            self.v8_case['title'], 
            self.v8_case['content']
        )
        
        # Verify structure
        assert result['analysis_type'] == 'quantitative_only'
        assert 'overall_score' in result
        assert 'technical_seo' in result
        assert 'brand_hierarchy' in result
        assert 'cultural_preservation' in result
        
        # Verify no qualitative feedback
        assert 'qualitative_feedback' not in result
        assert 'qualitative_insights' not in result
        
        # Verify metadata
        assert 'metadata' in result
        assert result['metadata']['analyzer_version'] == '1.0'

    def test_v8_breakthrough_quantitative_scoring(self):
        """Test V8 breakthrough case gets high quantitative scores"""
        result = self.analyzer.analyze_slug(
            self.v8_case['slug'],
            self.v8_case['title'], 
            self.v8_case['content']
        )
        
        # Should score highly on multiple brands
        assert result['brand_hierarchy']['brands_count'] >= 2
        assert result['brand_hierarchy']['score'] > 0.8
        
        # Should score well on technical SEO
        assert result['technical_seo']['score'] > 0.7
        
        # Overall score should be good
        assert result['overall_score'] > 0.7

    def test_cultural_preservation_quantitative_detection(self):
        """Test cultural term preservation detection"""
        result = self.analyzer.analyze_slug(
            self.v6_case['slug'],
            self.v6_case['title'],
            self.v6_case['content']
        )
        
        # Should detect cultural term preservation
        cultural = result['cultural_preservation']
        assert len(cultural['preserved_terms']) > 0
        assert 'ichiban-kuji' in cultural['preserved_terms']
        assert cultural['preservation_rate'] > 0.8

    def test_technical_seo_scoring(self):
        """Test technical SEO quantitative metrics"""
        good_slug = "korean-skincare-hongkong-guide"
        bad_slug = "korean-skincare-beauty-products-available-in-hongkong-shopping-recommendations-detailed"
        
        good_result = self.analyzer.analyze_slug(good_slug, "Korean skincare guide", "Content")
        bad_result = self.analyzer.analyze_slug(bad_slug, "Korean skincare guide", "Content")
        
        # Good slug should score higher
        assert good_result['technical_seo']['score'] > bad_result['technical_seo']['score']
        assert good_result['overall_score'] > bad_result['overall_score']

    def test_no_api_dependencies(self):
        """Test analyzer works completely offline"""
        # This should work even with no network connection
        analyzer = RuleBasedAnalyzer()
        
        result = analyzer.analyze_slug(
            "test-slug-example",
            "Test title",
            "Test content"
        )
        
        assert result['analysis_type'] == 'quantitative_only'
        assert isinstance(result['overall_score'], float)


class TestSEOEvaluatorClean:
    """Test LLM-only evaluator with comprehensive mocking"""
    
    def setup_method(self):
        """Set up test fixtures with mocking"""
        self.mock_client = Mock()
        
    def test_invalid_api_key_raises_error(self):
        """Test that invalid API key raises clear error"""
        
        with pytest.raises(InvalidAPIKeyError):
            SEOEvaluator(api_key="")
        
        with pytest.raises(InvalidAPIKeyError):
            SEOEvaluator(api_key="test-key")

    @patch('evaluation.core.seo_evaluator_clean.OpenAI')
    def test_successful_llm_evaluation(self, mock_openai_class):
        """Test successful LLM evaluation with mocked response"""
        
        # Setup mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "dimension_scores": {
                "user_intent_match": 0.8,
                "brand_hierarchy": 0.9,
                "cultural_authenticity": 0.85,
                "click_through_potential": 0.8,
                "competitive_differentiation": 0.7,
                "technical_seo": 0.9
            },
            "overall_score": 0.84,
            "qualitative_feedback": "This slug demonstrates excellent multi-brand handling with clear brand hierarchy. The combination of skinniydip, iface, and rhinoshield creates a comprehensive product comparison while maintaining readability. Cultural awareness is maintained through proper brand representation.",
            "confidence": 0.9,
            "key_strengths": ["multi-brand clarity", "technical optimization"],
            "improvement_areas": ["could be more concise"]
        })
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        # Test evaluation
        evaluator = SEOEvaluator(api_key="valid-key")
        result = evaluator.evaluate_slug(
            "skinnydip-iface-rhinoshield-phone-cases-guide",
            "Multi-brand phone case guide",
            "Detailed comparison of brands"
        )
        
        # Verify result structure
        assert result['analysis_type'] == 'llm_qualitative'
        assert result['overall_score'] == 0.84
        assert len(result['qualitative_feedback']) > 100
        assert 'dimension_scores' in result
        assert len(result['dimension_scores']) == 6

    @patch('evaluation.core.seo_evaluator_clean.OpenAI')
    def test_api_error_classification(self, mock_openai_class):
        """Test proper API error classification and retry behavior"""
        
        mock_client = Mock()
        
        # Test invalid API key error
        mock_client.chat.completions.create.side_effect = Exception("Incorrect API key provided")
        mock_openai_class.return_value = mock_client
        
        evaluator = SEOEvaluator(api_key="valid-key")
        
        with pytest.raises(InvalidAPIKeyError):
            evaluator.evaluate_slug("test-slug", "Test title", "Test content")

    @patch('evaluation.core.seo_evaluator_clean.OpenAI')
    def test_parsing_error_handling(self, mock_openai_class):
        """Test handling of unparseable LLM responses"""
        
        # Setup mock response with invalid JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is not valid JSON"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        evaluator = SEOEvaluator(api_key="valid-key")
        
        with pytest.raises(EvaluationParsingError):
            evaluator.evaluate_slug("test-slug", "Test title", "Test content")

    @patch('evaluation.core.seo_evaluator_clean.OpenAI')
    def test_insufficient_feedback_error(self, mock_openai_class):
        """Test error when LLM provides insufficient qualitative feedback"""
        
        # Setup mock response with minimal feedback
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "dimension_scores": {
                "user_intent_match": 0.8,
                "brand_hierarchy": 0.9,
                "cultural_authenticity": 0.85,
                "click_through_potential": 0.8,
                "competitive_differentiation": 0.7,
                "technical_seo": 0.9
            },
            "overall_score": 0.84,
            "qualitative_feedback": "Good.",  # Too short
            "confidence": 0.9
        })
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        evaluator = SEOEvaluator(api_key="valid-key")
        
        with pytest.raises(EvaluationParsingError, match="Insufficient qualitative feedback"):
            evaluator.evaluate_slug("test-slug", "Test title", "Test content")


class TestEvaluationCoordinator:
    """Test orchestration of quantitative + qualitative analysis"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.coordinator_quantitative_only = EvaluationCoordinator(
            api_key=None,  # No LLM
            enable_llm=False
        )

    def test_quantitative_only_mode(self):
        """Test coordinator works with quantitative analysis only"""
        
        result = self.coordinator_quantitative_only.evaluate_comprehensive(
            "test-slug-example",
            "Test title",
            "Test content"
        )
        
        # Should have quantitative analysis
        assert 'quantitative_analysis' in result
        assert result['quantitative_analysis']['analysis_type'] == 'quantitative_only'
        
        # Should not have qualitative analysis
        assert result['qualitative_insights'] is None
        assert result['analysis_type'] == 'quantitative_only'
        assert result['llm_available'] is False

    @patch('evaluation.core.evaluation_coordinator.SEOEvaluator')
    def test_combined_analysis_mode(self, mock_seo_evaluator_class):
        """Test coordinator combines both analyses when LLM available"""
        
        # Mock LLM evaluator
        mock_evaluator = Mock()
        mock_evaluator.evaluate_slug.return_value = {
            'analysis_type': 'llm_qualitative',
            'overall_score': 0.8,
            'dimension_scores': {
                'user_intent_match': 0.8,
                'brand_hierarchy': 0.9,
                'cultural_authenticity': 0.85,
                'click_through_potential': 0.8,
                'competitive_differentiation': 0.7,
                'technical_seo': 0.9
            },
            'qualitative_feedback': 'Excellent multi-brand handling with good technical structure.',
            'confidence': 0.9,
            'key_strengths': ['multi-brand clarity'],
            'improvement_areas': ['conciseness']
        }
        mock_seo_evaluator_class.return_value = mock_evaluator
        
        # Create coordinator with LLM
        coordinator = EvaluationCoordinator(api_key="valid-key", enable_llm=True)
        
        result = coordinator.evaluate_comprehensive(
            "test-slug-example",
            "Test title", 
            "Test content"
        )
        
        # Should have both analyses
        assert 'quantitative_analysis' in result
        assert 'qualitative_insights' in result
        assert result['analysis_type'] == 'complete'
        assert result['llm_available'] is True
        
        # Should have combined recommendation
        assert 'combined_recommendation' in result
        assert 'meta_analysis' in result

    def test_capabilities_reporting(self):
        """Test accurate reporting of analysis capabilities"""
        
        # Quantitative only
        capabilities = self.coordinator_quantitative_only.get_analysis_capabilities()
        
        assert capabilities['quantitative_analysis'] is True
        assert capabilities['qualitative_analysis'] is False
        assert len(capabilities['analysis_dimensions']['quantitative']) > 0
        assert len(capabilities['analysis_dimensions']['qualitative']) == 0


class TestErrorClassification:
    """Test API error classification system"""
    
    def test_classify_invalid_api_key(self):
        """Test classification of API key errors"""
        
        error = Exception("Incorrect API key provided: test-key")
        classified = classify_api_error(error)
        
        assert isinstance(classified, InvalidAPIKeyError)

    def test_classify_rate_limit_error(self):
        """Test classification of rate limit errors"""
        
        error = Exception("Rate limit exceeded")
        classified = classify_api_error(error)
        
        assert isinstance(classified, APIRateLimitError)

    def test_classify_temporary_error(self):
        """Test classification of temporary errors"""
        
        error = Exception("Connection timeout")
        classified = classify_api_error(error)
        
        assert isinstance(classified, TemporaryAPIError)
        assert classified.original_error == error

    def test_unknown_error_defaults_to_temporary(self):
        """Test unknown errors default to temporary"""
        
        error = Exception("Some unknown error")
        classified = classify_api_error(error)
        
        assert isinstance(classified, TemporaryAPIError)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])