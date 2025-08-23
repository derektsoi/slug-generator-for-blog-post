"""
Unit Tests for Enhanced SEOEvaluator Configuration API - Phase 2

These tests define the enhanced configuration functionality for SEOEvaluator
that enables developers to dynamically adjust evaluation behavior through
the configure_context() method.

TDD Phase: RED (these will initially fail - enhanced functionality doesn't exist yet)

Phase 2 Features Being Tested:
- configure_context() method for runtime configuration updates
- Dynamic focus area adjustments  
- Quality threshold updates
- Evaluation style configuration (detailed vs concise)
- Context-aware evaluation prompt modifications
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from evaluation.core.seo_evaluator import SEOEvaluator


class TestEnhancedSEOEvaluatorConfiguration:
    """Test enhanced configuration API for SEOEvaluator"""
    
    def setup_method(self):
        """Set up test environment before each test"""
        self.test_api_key = "test-api-key-12345"
        
    def test_configure_context_method_exists(self):
        """configure_context() method should exist on SEOEvaluator"""
        evaluator = SEOEvaluator(api_key=self.test_api_key)
        
        # This should fail initially - method doesn't exist yet
        assert hasattr(evaluator, 'configure_context'), "configure_context method should exist"
        assert callable(getattr(evaluator, 'configure_context', None)), "configure_context should be callable"
    
    def test_configure_context_accepts_focus_areas(self):
        """configure_context should accept focus_areas parameter"""
        evaluator = SEOEvaluator(api_key=self.test_api_key)
        
        # This should fail initially - method doesn't exist
        try:
            evaluator.configure_context({
                'focus_areas': ['cultural_authenticity', 'brand_hierarchy']
            })
            # Should not raise exception
            assert True
        except AttributeError:
            pytest.fail("configure_context method should accept focus_areas parameter")
    
    def test_configure_context_updates_focus_areas(self):
        """configure_context should update evaluation focus areas dynamically"""
        evaluator = SEOEvaluator(api_key=self.test_api_key)
        
        # Configure to focus on cultural aspects
        evaluator.configure_context({
            'focus_areas': ['cultural_authenticity', 'brand_hierarchy']
        })
        
        # Should have focus areas stored/accessible
        # This will fail initially - no focus area tracking exists
        assert hasattr(evaluator, '_current_focus_areas'), "Evaluator should track current focus areas"
        assert 'cultural_authenticity' in evaluator._current_focus_areas
        assert 'brand_hierarchy' in evaluator._current_focus_areas
    
    def test_configure_context_accepts_quality_thresholds(self):
        """configure_context should accept quality_thresholds parameter"""
        evaluator = SEOEvaluator(api_key=self.test_api_key)
        
        # This should fail initially
        try:
            evaluator.configure_context({
                'quality_thresholds': {
                    'minimum_confidence': 0.8,
                    'cultural_preservation_threshold': 0.9
                }
            })
            assert True
        except AttributeError:
            pytest.fail("configure_context should accept quality_thresholds parameter")
    
    def test_configure_context_updates_quality_thresholds(self):
        """configure_context should update minimum confidence thresholds"""
        evaluator = SEOEvaluator(api_key=self.test_api_key)
        
        # Update quality thresholds
        evaluator.configure_context({
            'quality_thresholds': {
                'minimum_confidence': 0.85,
                'cultural_preservation_threshold': 0.9
            }
        })
        
        # Should have thresholds stored/accessible
        # This will fail initially - no threshold tracking exists
        assert hasattr(evaluator, '_current_quality_thresholds'), "Evaluator should track quality thresholds"
        assert evaluator._current_quality_thresholds['minimum_confidence'] == 0.85
        assert evaluator._current_quality_thresholds['cultural_preservation_threshold'] == 0.9
    
    def test_configure_context_accepts_evaluation_style(self):
        """configure_context should accept evaluation_style parameter"""
        evaluator = SEOEvaluator(api_key=self.test_api_key)
        
        # This should fail initially
        try:
            evaluator.configure_context({
                'evaluation_style': 'detailed'
            })
            assert True
        except AttributeError:
            pytest.fail("configure_context should accept evaluation_style parameter")
    
    def test_configure_context_updates_evaluation_style(self):
        """configure_context should support 'detailed' vs 'concise' evaluation styles"""
        evaluator = SEOEvaluator(api_key=self.test_api_key)
        
        # Set detailed evaluation style
        evaluator.configure_context({
            'evaluation_style': 'detailed'
        })
        
        # Should have style stored/accessible
        # This will fail initially - no style tracking exists
        assert hasattr(evaluator, '_current_evaluation_style'), "Evaluator should track evaluation style"
        assert evaluator._current_evaluation_style == 'detailed'
        
        # Test concise style
        evaluator.configure_context({
            'evaluation_style': 'concise'
        })
        assert evaluator._current_evaluation_style == 'concise'
    
    def test_configure_context_validates_input_parameters(self):
        """configure_context should validate input parameters"""
        evaluator = SEOEvaluator(api_key=self.test_api_key)
        
        # Invalid focus areas should raise ValueError
        with pytest.raises(ValueError, match="Invalid focus area"):
            evaluator.configure_context({
                'focus_areas': ['invalid_focus_area', 'another_invalid']
            })
        
        # Invalid evaluation style should raise ValueError  
        with pytest.raises(ValueError, match="Invalid evaluation style"):
            evaluator.configure_context({
                'evaluation_style': 'invalid_style'
            })
        
        # Invalid threshold values should raise ValueError
        with pytest.raises(ValueError, match="Threshold.*out of range"):
            evaluator.configure_context({
                'quality_thresholds': {
                    'minimum_confidence': 1.5  # > 1.0
                }
            })
    
    def test_configure_context_affects_evaluation_prompt_generation(self):
        """configure_context should affect generated evaluation prompts"""
        evaluator = SEOEvaluator(api_key=self.test_api_key)
        
        # Generate baseline prompt
        baseline_prompt = evaluator._create_evaluation_prompt(
            slug="test-slug",
            title="Test Title", 
            content="Test content"
        )
        
        # Configure for cultural focus
        evaluator.configure_context({
            'focus_areas': ['cultural_authenticity'],
            'evaluation_style': 'detailed'
        })
        
        # Generate configured prompt
        configured_prompt = evaluator._create_evaluation_prompt(
            slug="test-slug",
            title="Test Title",
            content="Test content"  
        )
        
        # Prompts should be different after configuration
        # This will fail initially - no dynamic prompt modification exists
        assert baseline_prompt != configured_prompt, "Configuration should affect prompt generation"
        assert 'cultural' in configured_prompt.lower(), "Cultural focus should be emphasized in prompt"
        assert 'detailed' in configured_prompt.lower() or 'comprehensive' in configured_prompt.lower(), "Detailed style should be reflected"
    
    @patch('evaluation.core.seo_evaluator.OpenAI')
    def test_configure_context_affects_evaluation_behavior(self, mock_openai):
        """configure_context should affect actual evaluation behavior"""
        # Mock OpenAI response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """{
            "dimension_scores": {
                "user_intent_match": 0.8,
                "brand_hierarchy": 0.9,
                "cultural_authenticity": 0.95,
                "click_through_potential": 0.8,
                "competitive_differentiation": 0.6,
                "technical_seo": 0.9
            },
            "overall_score": 0.85,
            "qualitative_feedback": "Excellent cultural preservation with detailed analysis",
            "confidence": 0.9
        }"""
        
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        evaluator = SEOEvaluator(api_key=self.test_api_key)
        
        # Configure for detailed cultural evaluation
        evaluator.configure_context({
            'focus_areas': ['cultural_authenticity', 'brand_hierarchy'],
            'evaluation_style': 'detailed',
            'quality_thresholds': {'minimum_confidence': 0.8}
        })
        
        result = evaluator.evaluate_slug(
            slug="ultimate-ichiban-kuji-guide",
            title="一番賞完全購入指南", 
            content="Complete guide to ichiban-kuji purchasing"
        )
        
        # Should have called OpenAI with modified prompt reflecting configuration
        # This will fail initially - no configuration-aware evaluation exists
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        user_message_content = call_args[1]['messages'][1]['content']
        
        assert 'cultural' in user_message_content.lower(), "Cultural focus should be in evaluation prompt"
        assert 'detailed' in user_message_content.lower() or 'comprehensive' in user_message_content.lower(), "Detailed style should be in prompt"
    
    def test_configure_context_multiple_calls_override_previous(self):
        """Multiple configure_context calls should override previous settings"""
        evaluator = SEOEvaluator(api_key=self.test_api_key)
        
        # First configuration
        evaluator.configure_context({
            'focus_areas': ['cultural_authenticity'],
            'evaluation_style': 'concise'
        })
        
        # Second configuration should override
        evaluator.configure_context({
            'focus_areas': ['competitive_differentiation', 'brand_hierarchy'], 
            'evaluation_style': 'detailed'
        })
        
        # Should have latest configuration
        # This will fail initially - no configuration tracking exists
        assert 'competitive_differentiation' in evaluator._current_focus_areas
        assert 'brand_hierarchy' in evaluator._current_focus_areas  
        assert 'cultural_authenticity' not in evaluator._current_focus_areas  # Should be overridden
        assert evaluator._current_evaluation_style == 'detailed'
    
    def test_configure_context_partial_updates_preserve_other_settings(self):
        """Partial configure_context updates should preserve other settings"""
        evaluator = SEOEvaluator(api_key=self.test_api_key)
        
        # Initial full configuration
        evaluator.configure_context({
            'focus_areas': ['cultural_authenticity'],
            'evaluation_style': 'detailed',
            'quality_thresholds': {'minimum_confidence': 0.8}
        })
        
        # Partial update - only change evaluation style
        evaluator.configure_context({
            'evaluation_style': 'concise'
        })
        
        # Should preserve focus areas and thresholds, update style
        # This will fail initially - no selective update logic exists
        assert 'cultural_authenticity' in evaluator._current_focus_areas  # Preserved
        assert evaluator._current_quality_thresholds['minimum_confidence'] == 0.8  # Preserved
        assert evaluator._current_evaluation_style == 'concise'  # Updated
    
    def test_configure_context_reset_functionality(self):
        """configure_context should support resetting to defaults"""
        evaluator = SEOEvaluator(api_key=self.test_api_key)
        
        # Configure with custom settings
        evaluator.configure_context({
            'focus_areas': ['cultural_authenticity'],
            'evaluation_style': 'detailed',
            'quality_thresholds': {'minimum_confidence': 0.9}
        })
        
        # Reset to defaults
        evaluator.configure_context({'reset': True})
        
        # Should have default settings
        # This will fail initially - no reset functionality exists
        assert not hasattr(evaluator, '_current_focus_areas') or evaluator._current_focus_areas == []
        assert not hasattr(evaluator, '_current_evaluation_style') or evaluator._current_evaluation_style == 'balanced'
        assert not hasattr(evaluator, '_current_quality_thresholds') or evaluator._current_quality_thresholds == {}
    
    def test_configure_context_works_with_different_prompt_versions(self):
        """configure_context should work with different evaluation_prompt_version settings"""
        # Test with different prompt versions
        for prompt_version in ['current', 'v2_cultural_focused', 'v3_competitive_focused']:
            evaluator = SEOEvaluator(
                api_key=self.test_api_key,
                evaluation_prompt_version=prompt_version
            )
            
            # Should be able to configure context regardless of prompt version
            evaluator.configure_context({
                'focus_areas': ['brand_hierarchy'],
                'evaluation_style': 'detailed'
            })
            
            # Configuration should be applied
            # This will fail initially - no cross-version configuration exists
            assert hasattr(evaluator, '_current_focus_areas'), f"Context config should work with {prompt_version}"
            assert 'brand_hierarchy' in evaluator._current_focus_areas