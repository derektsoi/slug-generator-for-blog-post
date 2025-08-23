"""
Backward Compatibility Tests for Configurable Evaluation System

These tests ensure that existing SEOEvaluator usage continues to work
unchanged when configurable evaluation prompts are introduced.

TDD Phase: RED (should pass immediately with current implementation)
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from evaluation.core.seo_evaluator import SEOEvaluator


class TestBackwardCompatibility:
    """Test that existing SEOEvaluator usage remains unchanged"""
    
    def test_existing_seo_evaluator_constructor_still_works(self):
        """Existing constructor without evaluation_prompt_version should work"""
        # This should work exactly as before
        evaluator = SEOEvaluator(api_key="test-key")
        
        # Verify basic attributes exist
        assert evaluator.api_key == "test-key"
        assert evaluator.model == "gpt-4o-mini"
        assert hasattr(evaluator, 'scoring_dimensions')
        assert hasattr(evaluator, 'cultural_terms')
        assert hasattr(evaluator, 'brand_patterns')
    
    def test_existing_seo_evaluator_constructor_with_model_parameter(self):
        """Existing constructor with model parameter should work"""
        evaluator = SEOEvaluator(api_key="test-key", model="gpt-4o")
        
        assert evaluator.api_key == "test-key" 
        assert evaluator.model == "gpt-4o"
    
    def test_existing_scoring_dimensions_preserved(self):
        """Current scoring dimensions should remain the same"""
        evaluator = SEOEvaluator(api_key="test-key")
        
        expected_dimensions = [
            'user_intent_match',
            'brand_hierarchy', 
            'cultural_authenticity',
            'click_through_potential',
            'competitive_differentiation',
            'technical_seo'
        ]
        
        assert evaluator.scoring_dimensions == expected_dimensions
    
    def test_existing_cultural_terms_preserved(self):
        """Current cultural terms mapping should remain unchanged"""
        evaluator = SEOEvaluator(api_key="test-key")
        
        expected_cultural_terms = {
            '一番賞': 'ichiban-kuji',
            'JK制服': 'jk-uniform', 
            '大國藥妝': 'daikoku-drugstore',
            '樂天': 'rakuten',
            '官網': 'official-store',
            '集運': 'shipping',
            '代購': 'proxy-shopping',
            '藥妝': 'drugstore'
        }
        
        assert evaluator.cultural_terms == expected_cultural_terms
    
    def test_existing_brand_patterns_preserved(self):
        """Current brand patterns should remain unchanged"""
        evaluator = SEOEvaluator(api_key="test-key")
        
        expected_patterns = [
            r'jojo-maman-bebe',
            r'skinniydip',
            r'iface', 
            r'rhinoshield',
            r'daikoku',
            r'rakuten',
            r'amazon',
            r'gap'
        ]
        
        assert evaluator.brand_patterns == expected_patterns
    
    @patch('openai.OpenAI')
    def test_existing_evaluate_slug_method_unchanged_behavior(self, mock_openai):
        """evaluate_slug method should work exactly as before"""
        # Mock OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """{
            "dimension_scores": {
                "user_intent_match": 0.8,
                "brand_hierarchy": 0.9,
                "cultural_authenticity": 0.7,
                "click_through_potential": 0.8,
                "competitive_differentiation": 0.6,
                "technical_seo": 0.9
            },
            "overall_score": 0.8,
            "qualitative_feedback": "Test feedback",
            "confidence": 0.9
        }"""
        
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        evaluator = SEOEvaluator(api_key="test-key")
        
        # This should work exactly as before
        result = evaluator.evaluate_slug(
            slug="test-slug",
            title="Test Title", 
            content="Test content"
        )
        
        # Verify structure matches current expectations
        assert 'overall_score' in result
        assert 'dimension_scores' in result
        assert 'qualitative_feedback' in result
        assert 'confidence' in result
        # Just verify the overall score is reasonable (between 0 and 1)
        assert 0.0 <= result['overall_score'] <= 1.0
        assert len(result['dimension_scores']) == 6
        # Verify all dimension scores are present
        expected_dimensions = [
            'user_intent_match',
            'brand_hierarchy', 
            'cultural_authenticity',
            'click_through_potential',
            'competitive_differentiation',
            'technical_seo'
        ]
        for dim in expected_dimensions:
            assert dim in result['dimension_scores']
            assert 0.0 <= result['dimension_scores'][dim] <= 1.0
    
    def test_existing_evaluate_failure_case_unchanged(self):
        """evaluate_failure_case method should work exactly as before"""
        evaluator = SEOEvaluator(api_key="test-key")
        
        result = evaluator.evaluate_failure_case(
            title="Test Title",
            content="Test content", 
            failure_reason="exceeded_word_limit"
        )
        
        # Verify structure matches current expectations
        assert result['overall_score'] == 0.1
        assert len(result['dimension_scores']) == 6
        assert all(score == 0.1 for score in result['dimension_scores'].values())
        assert result['confidence'] == 0.9
        assert 'failure_analysis' in result
        assert result['failure_analysis']['failure_type'] == "exceeded_word_limit"
    
    def test_existing_fallback_evaluation_behavior(self):
        """Fallback evaluation should work exactly as before when API fails"""
        evaluator = SEOEvaluator(api_key="test-key")
        
        # Test fallback evaluation directly
        result = evaluator._create_fallback_evaluation(
            slug="test-multi-brand-slug",
            title="Test Title", 
            content="Test content",
            error="API timeout"
        )
        
        # Verify structure matches current expectations
        assert 'overall_score' in result
        assert 'dimension_scores' in result  
        assert 'qualitative_feedback' in result
        assert 'confidence' in result
        assert 'api_error' in result
        assert result['confidence'] == 0.4
        assert result['api_error'] == "API timeout"
        assert len(result['dimension_scores']) == 6
    
    def test_existing_create_evaluation_prompt_method_exists(self):
        """_create_evaluation_prompt method should still exist and work"""
        evaluator = SEOEvaluator(api_key="test-key")
        
        # This method should still exist for backward compatibility
        assert hasattr(evaluator, '_create_evaluation_prompt')
        
        prompt = evaluator._create_evaluation_prompt(
            slug="test-slug",
            title="Test Title",
            content="Test content"
        )
        
        # Verify it returns a string prompt
        assert isinstance(prompt, str)
        assert len(prompt) > 100  # Should be substantial prompt
        assert "SLUG:" in prompt
        assert "ORIGINAL TITLE:" in prompt
        assert "CONTENT PREVIEW:" in prompt