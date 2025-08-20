"""
Test Suite for SEO Evaluator - LLM-Powered Evaluation System

Tests the core SEO evaluation functionality using TDD approach.
These tests should FAIL initially to ensure they work properly.
"""

import pytest
import json
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from evaluation.core.seo_evaluator import SEOEvaluator
from evaluation.core.feedback_extractor import FeedbackExtractor
from evaluation.validation.ground_truth_validator import GroundTruthValidator


class TestSEOEvaluator:
    """Test the multi-dimensional SEO assessment system"""

    def setup_method(self):
        """Set up test fixtures"""
        self.evaluator = SEOEvaluator(api_key="test-key")
        
        # V8 breakthrough case that should score highest
        self.v8_breakthrough_case = {
            'title': '日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！',
            'content': '日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！詳細介紹各品牌特色',
            'v6_slug': None,  # V6 failed
            'v7_slug': None,  # V7 failed  
            'v8_slug': 'skinnydip-iface-rhinoshield-phone-cases-guide'
        }
        
        # V6 cultural success case
        self.v6_cultural_case = {
            'title': '【2025年最新】日本一番賞Online手把手教學！',
            'content': '日本一番賞Online購買教學，詳細步驟說明',
            'v5_slug': 'ichiban-kuji-anime-merchandise-japan-guide',  # generic
            'v6_slug': 'ichiban-kuji-anime-japan-guide',  # preserved cultural term
            'v8_slug': 'ichiban-kuji-anime-japan-guide'
        }

    def test_seo_evaluator_initialization(self):
        """Test SEO evaluator initializes with required components"""
        evaluator = SEOEvaluator(api_key="test-key")
        
        assert evaluator.api_key == "test-key"
        assert hasattr(evaluator, 'scoring_dimensions')
        assert hasattr(evaluator, 'cultural_terms')
        assert hasattr(evaluator, 'brand_patterns')
        
        # Verify required scoring dimensions exist
        expected_dimensions = [
            'user_intent_match',
            'brand_hierarchy', 
            'cultural_authenticity',
            'click_through_potential',
            'competitive_differentiation',
            'technical_seo'
        ]
        
        for dimension in expected_dimensions:
            assert dimension in evaluator.scoring_dimensions

    def test_evaluate_slug_returns_structured_score(self):
        """Test that slug evaluation returns properly structured multi-dimensional scores"""
        test_slug = "skinnydip-iface-rhinoshield-phone-cases-guide"
        test_content = self.v8_breakthrough_case['content']
        
        result = self.evaluator.evaluate_slug(
            slug=test_slug,
            title=self.v8_breakthrough_case['title'],
            content=test_content
        )
        
        # Should return structured scoring
        assert 'overall_score' in result
        assert 'dimension_scores' in result
        assert 'qualitative_feedback' in result
        assert 'confidence' in result
        
        # Verify all dimensions are scored
        for dimension in self.evaluator.scoring_dimensions:
            assert dimension in result['dimension_scores']
            assert 0.0 <= result['dimension_scores'][dimension] <= 1.0
        
        # Overall score should be aggregate of dimensions
        assert 0.0 <= result['overall_score'] <= 1.0
        assert isinstance(result['qualitative_feedback'], str)
        assert len(result['qualitative_feedback']) > 50  # Meaningful feedback

    def test_v8_breakthrough_scores_higher_than_failures(self):
        """Test that V8 breakthrough case scores higher than V6/V7 failures"""
        # This should demonstrate the evaluator can recognize breakthrough quality
        
        # V8 success case
        v8_result = self.evaluator.evaluate_slug(
            slug=self.v8_breakthrough_case['v8_slug'],
            title=self.v8_breakthrough_case['title'],
            content=self.v8_breakthrough_case['content']
        )
        
        # Simulate V6/V7 failure (no slug generated)
        failure_result = self.evaluator.evaluate_failure_case(
            title=self.v8_breakthrough_case['title'],
            content=self.v8_breakthrough_case['content'],
            failure_reason="exceeded_word_limit"
        )
        
        assert v8_result['overall_score'] > 0.8  # High quality
        assert failure_result['overall_score'] < 0.3  # Clear failure
        assert v8_result['overall_score'] > failure_result['overall_score']
        
        # V8 should excel in specific dimensions
        assert v8_result['dimension_scores']['brand_hierarchy'] > 0.8  # Multi-brand handling
        assert v8_result['dimension_scores']['user_intent_match'] > 0.7  # Product-focused

    def test_cultural_authenticity_detection(self):
        """Test cultural term preservation is properly scored"""
        
        # V6 cultural success
        v6_result = self.evaluator.evaluate_slug(
            slug=self.v6_cultural_case['v6_slug'],
            title=self.v6_cultural_case['title'],
            content=self.v6_cultural_case['content']
        )
        
        # V5 generic version (for comparison)
        v5_result = self.evaluator.evaluate_slug(
            slug=self.v6_cultural_case['v5_slug'],
            title=self.v6_cultural_case['title'],
            content=self.v6_cultural_case['content']
        )
        
        # V6 should score higher on cultural authenticity
        assert v6_result['dimension_scores']['cultural_authenticity'] > v5_result['dimension_scores']['cultural_authenticity']
        
        # Both should be identified in feedback
        assert 'ichiban-kuji' in v6_result['qualitative_feedback'].lower()
        assert 'cultural' in v6_result['qualitative_feedback'].lower() or 'authentic' in v6_result['qualitative_feedback'].lower()

    def test_brand_hierarchy_scoring(self):
        """Test proper brand positioning assessment"""
        
        # Multi-brand case (V8 breakthrough)
        multi_brand_result = self.evaluator.evaluate_slug(
            slug="skinnydip-iface-rhinoshield-phone-cases-guide",
            title="SKINNIYDIP/iface/犀牛盾 phone case brands",
            content="Multiple phone case brands comparison"
        )
        
        # Single brand case
        single_brand_result = self.evaluator.evaluate_slug(
            slug="apple-iphone-case-guide", 
            title="Apple iPhone cases",
            content="Apple iPhone case recommendations"
        )
        
        # Multi-brand should score higher on brand hierarchy (more complex)
        assert multi_brand_result['dimension_scores']['brand_hierarchy'] >= single_brand_result['dimension_scores']['brand_hierarchy']
        
        # Feedback should mention brand handling
        assert 'brand' in multi_brand_result['qualitative_feedback'].lower()

    def test_technical_seo_validation(self):
        """Test technical SEO factors (length, structure, readability)"""
        
        # Good technical SEO case
        good_slug = "skincare-korean-brands-hongkong-guide"
        good_result = self.evaluator.evaluate_slug(
            slug=good_slug,
            title="Korean skincare brands in Hong Kong",
            content="Guide to Korean skincare brands available in Hong Kong"
        )
        
        # Poor technical SEO case (too long, poor structure)
        bad_slug = "korean-skincare-beauty-products-brands-available-in-hongkong-shopping-guide-recommendations"
        bad_result = self.evaluator.evaluate_slug(
            slug=bad_slug,
            title="Korean skincare brands in Hong Kong", 
            content="Guide to Korean skincare brands available in Hong Kong"
        )
        
        # Good slug should score higher on technical SEO
        assert good_result['dimension_scores']['technical_seo'] > bad_result['dimension_scores']['technical_seo']
        assert good_result['overall_score'] > bad_result['overall_score']


class TestFeedbackExtractor:
    """Test qualitative feedback extraction system"""
    
    def setup_method(self):
        self.extractor = FeedbackExtractor(api_key="test-key")
    
    def test_extract_improvement_suggestions(self):
        """Test extraction of actionable improvement suggestions"""
        
        comparison_data = {
            'slug_a': 'generic-product-guide',
            'slug_b': 'jojo-maman-bebe-maternity-clothes-guide',
            'title': 'JoJo Maman Bébé maternity clothes recommendations',
            'content': 'Detailed guide to JoJo Maman Bébé maternity wear',
            'winner': 'slug_b',
            'score_difference': 0.3
        }
        
        suggestions = self.extractor.extract_improvement_suggestions(comparison_data)
        
        assert 'strengths' in suggestions
        assert 'weaknesses' in suggestions  
        assert 'specific_improvements' in suggestions
        assert 'pattern_insights' in suggestions
        
        # Should identify brand importance
        feedback_text = str(suggestions).lower()
        assert 'brand' in feedback_text
        assert 'jojo' in feedback_text or 'specific' in feedback_text
        
        assert isinstance(suggestions['specific_improvements'], list)
        assert len(suggestions['specific_improvements']) >= 2

    def test_cultural_feedback_extraction(self):
        """Test cultural awareness feedback extraction"""
        
        cultural_comparison = {
            'slug_a': 'anime-merchandise-japan-guide',  # generic
            'slug_b': 'ichiban-kuji-anime-japan-guide',  # cultural
            'title': '日本一番賞Online手把手教學',
            'content': '一番賞購買教學詳細說明',
            'winner': 'slug_b',
            'cultural_terms': ['一番賞', 'ichiban-kuji']
        }
        
        feedback = self.extractor.extract_cultural_feedback(cultural_comparison)
        
        assert 'cultural_preservation' in feedback
        assert 'authenticity_score' in feedback
        assert 'cultural_insights' in feedback
        
        # Should recognize cultural term preservation
        assert feedback['cultural_preservation'] > 0.7
        feedback_text = str(feedback).lower()
        assert 'ichiban' in feedback_text or 'cultural' in feedback_text


class TestGroundTruthValidator:
    """Test validation against known V6/V7/V8 performance data"""
    
    def setup_method(self):
        self.validator = GroundTruthValidator()
        
        # Load known breakthrough cases
        self.known_cases = {
            'v8_breakthroughs': [
                {
                    'title': '日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！',
                    'v6_result': 'failure',
                    'v7_result': 'failure', 
                    'v8_result': 'skinnydip-iface-rhinoshield-phone-cases-guide',
                    'expected_evaluator_ranking': 'v8_highest'
                }
            ],
            'v6_cultural_wins': [
                {
                    'title': '【2025年最新】日本一番賞Online手把手教學！',
                    'v5_result': 'ichiban-kuji-anime-merchandise-japan-guide',
                    'v6_result': 'ichiban-kuji-anime-japan-guide',
                    'expected_evaluator_ranking': 'v6_higher_cultural'
                }
            ]
        }
    
    def test_evaluator_recognizes_v8_breakthroughs(self):
        """Test evaluator properly ranks V8 breakthroughs as superior"""
        
        evaluator = SEOEvaluator(api_key="test-key")
        
        for case in self.known_cases['v8_breakthroughs']:
            # Evaluate V8 success
            v8_score = evaluator.evaluate_slug(
                slug=case['v8_result'],
                title=case['title'],
                content=case['title']  # Use title as content for test
            )
            
            # Evaluate failure case
            failure_score = evaluator.evaluate_failure_case(
                title=case['title'],
                content=case['title'],
                failure_reason="constraint_violation"
            )
            
            # V8 should significantly outperform failures
            assert v8_score['overall_score'] > failure_score['overall_score']
            assert v8_score['overall_score'] > 0.7  # High absolute score
            
            # Validation should pass
            is_valid = self.validator.validate_breakthrough_recognition(
                case, v8_score, failure_score
            )
            assert is_valid

    def test_evaluator_recognizes_cultural_improvements(self):
        """Test evaluator properly scores cultural authenticity improvements"""
        
        evaluator = SEOEvaluator(api_key="test-key")
        
        for case in self.known_cases['v6_cultural_wins']:
            v5_score = evaluator.evaluate_slug(
                slug=case['v5_result'],
                title=case['title'],
                content=case['title']
            )
            
            v6_score = evaluator.evaluate_slug(
                slug=case['v6_result'], 
                title=case['title'],
                content=case['title']
            )
            
            # V6 should score higher on cultural authenticity
            assert v6_score['dimension_scores']['cultural_authenticity'] > v5_score['dimension_scores']['cultural_authenticity']
            
            # Validation should confirm cultural improvement
            is_valid = self.validator.validate_cultural_improvement(
                case, v5_score, v6_score
            )
            assert is_valid

    def test_bias_detection_cross_validation(self):
        """Test detection of potential evaluator biases"""
        
        evaluator = SEOEvaluator(api_key="test-key")
        
        # Test same content with different presentation
        test_cases = [
            {
                'slug': 'jojo-maman-bebe-maternity-guide',
                'presentation': 'standard'
            },
            {
                'slug': 'jojo-maman-bebe-maternity-guide',  # Same slug
                'presentation': 'with_context'  # Additional context provided
            }
        ]
        
        scores = []
        for case in test_cases:
            score = evaluator.evaluate_slug(
                slug=case['slug'],
                title="JoJo Maman Bébé maternity clothes",
                content="JoJo Maman Bébé maternity wear guide" if case['presentation'] == 'standard' 
                       else "Detailed comprehensive guide to JoJo Maman Bébé premium maternity wear collection"
            )
            scores.append(score['overall_score'])
        
        # Scores should be reasonably consistent (bias detection)
        score_difference = abs(scores[0] - scores[1])
        assert score_difference < 0.2  # Should not vary drastically
        
        bias_check = self.validator.detect_presentation_bias(test_cases, scores)
        assert bias_check['bias_detected'] == False or bias_check['bias_severity'] < 0.3


if __name__ == "__main__":
    # Run tests to verify they fail initially
    pytest.main([__file__, "-v", "--tb=short"])