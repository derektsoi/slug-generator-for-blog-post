#!/usr/bin/env python3
"""
TDD tests for improved LLM implementation
Tests all the improvements we implemented
"""

import sys
import os
import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from slug_generator import SlugGenerator


class TestKeywordFallbackElimination:
    """Test removal of keyword-based fallback mechanisms"""
    
    def test_no_fallback_method_exists(self):
        """_generate_fallback_slug should not exist"""
        generator = SlugGenerator(api_key="test-key")
        assert not hasattr(generator, '_generate_fallback_slug')
    
    def test_has_generate_from_content_method(self):
        """Should have generate_slug_from_content for testing"""
        generator = SlugGenerator(api_key="test-key")
        assert hasattr(generator, 'generate_slug_from_content')


class TestRetryLogic:
    """Test intelligent retry behavior for LLM failures"""
    
    def test_retry_configuration(self):
        """Should allow configurable retry attempts"""
        generator = SlugGenerator(api_key="test-key", max_retries=3, retry_delay=1.0)
        assert generator.max_retries == 3
        assert generator.retry_delay == 1.0
    
    @patch('time.sleep')
    @patch('openai.OpenAI')
    def test_retry_on_api_failure(self, mock_openai, mock_sleep):
        """Should retry LLM calls on API failures"""
        # First 2 calls fail, 3rd succeeds
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = [
            Exception("API Error"),
            Exception("API Error"),
            Mock(choices=[Mock(message=Mock(content='{"slugs": [{"slug": "test-slug-generator", "confidence": 0.9, "reasoning": "test"}]}'))])
        ]
        
        generator = SlugGenerator(api_key="test-key", max_retries=3)
        result = generator.generate_slug_from_content("Test Title", "Test content")
        
        # Should succeed after retries
        assert result['primary'] == "test-slug-generator"
        # Should have made 3 attempts
        assert mock_client.chat.completions.create.call_count == 3
    
    @patch('time.sleep')
    @patch('openai.OpenAI')
    def test_exponential_backoff(self, mock_openai, mock_sleep):
        """Should implement exponential backoff between retries"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = [
            Exception("API Error"),
            Exception("API Error"),
            Mock(choices=[Mock(message=Mock(content='{"slugs": [{"slug": "test-slug-generator", "confidence": 0.9, "reasoning": "test"}]}'))])
        ]
        
        generator = SlugGenerator(api_key="test-key", max_retries=3, retry_delay=1.0)
        generator.generate_slug_from_content("Test Title", "Test content")
        
        # Should sleep with exponential backoff: 1s, 2s
        expected_sleeps = [1.0, 2.0]
        actual_sleeps = [call[0][0] for call in mock_sleep.call_args_list]
        assert actual_sleeps == expected_sleeps
    
    @patch('openai.OpenAI')
    def test_final_failure_after_max_retries(self, mock_openai):
        """Should fail clearly after exhausting retries"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("Persistent API Error")
        
        generator = SlugGenerator(api_key="test-key", max_retries=2)
        
        with pytest.raises(Exception, match="Failed to generate slug after 2 retry attempts"):
            generator.generate_slug_from_content("Test Title", "Test content")
        
        # Should have made exactly max_retries + 1 attempts
        assert mock_client.chat.completions.create.call_count == 3


class TestEnhancedContentLimits:
    """Test improved content limits for better LLM analysis"""
    
    def test_increased_api_content_limit(self):
        """API should receive 3000 chars instead of 2000"""
        generator = SlugGenerator(api_key="test-key")
        assert generator.api_content_limit == 3000
    
    def test_increased_prompt_preview_limit(self):
        """Prompt should include 1500 chars preview instead of 500"""
        generator = SlugGenerator(api_key="test-key")
        assert generator.prompt_preview_limit == 1500
    
    @patch('openai.OpenAI')
    def test_content_limit_usage(self, mock_openai):
        """Should use new content limits in practice"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content='{"slugs": [{"slug": "test-slug-generator", "confidence": 0.9, "reasoning": "test"}]}'))]
        )
        
        long_content = "A" * 5000
        generator = SlugGenerator(api_key="test-key")
        generator.generate_slug_from_content("Test Title", long_content)
        
        # Check the prompt that was sent
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        user_message = messages[1]['content']
        
        # Should include more content than old 500 char limit
        assert len(user_message) > 1000  # Much more than old limit
        assert "A" * 1000 in user_message  # Substantial content included


class TestStructuredPromptPattern:
    """Test adoption of content-analyzer's structured approach"""
    
    def test_external_prompt_template_loading(self):
        """Should load prompt from external file"""
        generator = SlugGenerator(api_key="test-key")
        
        # Should have method to load external prompts
        assert hasattr(generator, '_load_prompt')
        
        # Should load from config/prompts/ directory
        prompt = generator._load_prompt('slug_generation')
        assert len(prompt) > 100  # Substantial prompt content
        assert "STEP" in prompt
    
    def test_prompt_has_step_by_step_analysis(self):
        """Prompt should include systematic analysis steps"""
        generator = SlugGenerator(api_key="test-key")
        prompt = generator._create_slug_prompt("Test Title", "Test content", 3)
        
        required_steps = [
            "STEP 1:",
            "STEP 2:", 
            "STEP 3:",
            "STEP 4:",
            "STEP 5:"
        ]
        
        for step in required_steps:
            assert step in prompt
    
    def test_prompt_includes_ecommerce_context(self):
        """Prompt should mention cross-border ecommerce specialization"""
        generator = SlugGenerator(api_key="test-key")
        prompt = generator._create_slug_prompt("UK shopping guide", "content", 1)
        
        context_keywords = [
            "cross-border",
            "e-commerce",
            "geographic", 
            "brands"
        ]
        
        # At least some ecommerce context should be present
        assert any(keyword in prompt.lower() for keyword in context_keywords)
    
    def test_prompt_requests_json_format(self):
        """Prompt should explicitly request JSON response format"""
        generator = SlugGenerator(api_key="test-key")
        prompt = generator._create_slug_prompt("Test", "content", 3)
        
        assert "JSON format" in prompt
        assert "{" in prompt and "}" in prompt  # JSON example
        assert "confidence" in prompt
        assert "reasoning" in prompt


class TestStructuredResponse:
    """Test JSON response parsing and validation"""
    
    @patch('openai.OpenAI')
    def test_parses_valid_json_response(self, mock_openai):
        """Should correctly parse structured JSON from LLM"""
        valid_response = {
            "slugs": [
                {"slug": "uk-fashion-guide", "confidence": 0.95, "reasoning": "Clear topic"},
                {"slug": "british-style-shopping", "confidence": 0.88, "reasoning": "Alternative angle"},
                {"slug": "uk-brands-tutorial", "confidence": 0.82, "reasoning": "Tutorial focus"}
            ]
        }
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content=json.dumps(valid_response)))]
        )
        
        generator = SlugGenerator(api_key="test-key")
        result = generator.generate_slug_from_content("Test Title", "Test content", count=3)
        
        assert result['primary'] == "uk-fashion-guide"
        assert len(result['alternatives']) == 2
        assert "british-style-shopping" in result['alternatives']
    
    @patch('openai.OpenAI')
    def test_confidence_threshold_filtering(self, mock_openai):
        """Should filter out low confidence suggestions"""
        mixed_confidence_response = {
            "slugs": [
                {"slug": "high-confidence-slug-test", "confidence": 0.9, "reasoning": "Good"},
                {"slug": "medium-confidence-slug-test", "confidence": 0.7, "reasoning": "OK"},
                {"slug": "low-confidence-slug-test", "confidence": 0.3, "reasoning": "Poor"}  # Below threshold
            ]
        }
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content=json.dumps(mixed_confidence_response)))]
        )
        
        generator = SlugGenerator(api_key="test-key")
        result = generator.generate_slug_from_content("Test Title", "Test content", count=3)
        
        # Should only include high and medium confidence
        all_slugs = [result['primary']] + result['alternatives']
        assert "high-confidence-slug-test" in all_slugs
        assert "medium-confidence-slug-test" in all_slugs  
        assert "low-confidence-slug-test" not in all_slugs
    
    @patch('openai.OpenAI')
    def test_model_upgrade_to_gpt4o_mini(self, mock_openai):
        """Should use gpt-4o-mini instead of gpt-3.5-turbo"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content='{"slugs": [{"slug": "test-slug-generator", "confidence": 0.9, "reasoning": "test"}]}'))]
        )
        
        generator = SlugGenerator(api_key="test-key")
        generator.generate_slug_from_content("Test Title", "Test content")
        
        # Check model used
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['model'] == 'gpt-4o-mini'
        assert call_kwargs['response_format'] == {"type": "json_object"}


class TestLLMFirstErrorHandling:
    """Test proper error handling without fallbacks"""
    
    @patch('openai.OpenAI')
    def test_malformed_json_handling(self, mock_openai):
        """Malformed JSON should raise clear error"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="This is not JSON at all"))]
        )
        
        generator = SlugGenerator(api_key="test-key")
        
        with pytest.raises(Exception, match="JSON"):
            generator.generate_slug_from_content("Test Title", "Test content")
    
    @patch('openai.OpenAI')
    def test_missing_slugs_key_in_response(self, mock_openai):
        """Response without 'slugs' key should fail clearly"""
        invalid_response = {"error": "No slugs generated"}
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content=json.dumps(invalid_response)))]
        )
        
        generator = SlugGenerator(api_key="test-key")
        with pytest.raises(Exception, match="slugs"):
            generator.generate_slug_from_content("Test Title", "Test content")
    
    @patch('openai.OpenAI')
    def test_empty_slugs_array(self, mock_openai):
        """Empty slugs array should raise exception"""
        empty_response = {"slugs": []}
        
        mock_client = Mock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content=json.dumps(empty_response)))]
        )
        
        generator = SlugGenerator(api_key="test-key")
        with pytest.raises(Exception, match="No slugs in response"):
            generator.generate_slug_from_content("Test Title", "Test content")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])