"""
V11 OpenAI API Dependency Integration Tests - TDD RED Phase
Tests that V11 versions properly integrate with OpenAI API

This file focuses specifically on API integration testing
to ensure V11 can make real OpenAI API calls with proper error handling

🔴 RED: These tests SHOULD fail initially since V11 doesn't exist yet
🟢 GREEN: Implementation will make these pass
"""

import pytest
import sys
import os
import openai
from unittest.mock import patch, Mock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.slug_generator import SlugGenerator


class TestV11OpenAIDependency:
    """Test V11 OpenAI API integration and dependency management"""
    
    @pytest.mark.integration
    @pytest.mark.skipif(not os.getenv('OPENAI_API_KEY'), reason="OPENAI_API_KEY not set")
    def test_v11a_openai_api_success_response(self):
        """Test V11a handles successful OpenAI API responses"""
        # This SHOULD FAIL initially - V11a doesn't exist
        api_key = os.getenv('OPENAI_API_KEY')
        generator = SlugGenerator(api_key=api_key, prompt_version='v11a')
        
        # Test with real API call
        result = generator.generate_slug_from_content(
            title="大國藥妝香港購物教學", 
            content="大國藥妝香港購物教學 - 專業代購服務"
        )
        
        # Validate successful API response
        assert result is not None
        assert 'primary' in result
        assert isinstance(result['primary'], str)
        assert len(result['primary']) > 0
        
        # V11a should produce 3-5 word slugs
        word_count = len(result['primary'].split('-'))
        assert 3 <= word_count <= 5, f"V11a should generate 3-5 words, got {word_count}"
        
    @pytest.mark.integration
    @pytest.mark.skipif(not os.getenv('OPENAI_API_KEY'), reason="OPENAI_API_KEY not set")  
    def test_v11b_openai_api_success_response(self):
        """Test V11b handles successful OpenAI API responses"""
        # This SHOULD FAIL initially - V11b doesn't exist
        api_key = os.getenv('OPENAI_API_KEY')
        generator = SlugGenerator(api_key=api_key, prompt_version='v11b')
        
        # Test with complex multi-brand content
        result = generator.generate_slug_from_content(
            title="【2025年最新】日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！",
            content="日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！完整購買教學與評價比較"
        )
        
        # Validate successful API response  
        assert result is not None
        assert 'primary' in result
        assert isinstance(result['primary'], str)
        assert len(result['primary']) > 0
        
        # V11b should produce 8-12 word slugs
        word_count = len(result['primary'].split('-'))
        assert 8 <= word_count <= 12, f"V11b should generate 8-12 words, got {word_count}"
        
    def test_v11a_openai_api_authentication_error(self):
        """Test V11a handles OpenAI authentication errors properly"""
        # This SHOULD FAIL initially - V11a doesn't exist
        generator = SlugGenerator(api_key='invalid-key-12345', prompt_version='v11a')
        
        # Should raise authentication error, not crash silently
        with pytest.raises((openai.AuthenticationError, Exception)) as exc_info:
            generator.generate_slug_from_content("test", "test content")
            
        # Error should be related to authentication
        error_msg = str(exc_info.value).lower()
        assert any(word in error_msg for word in ['auth', 'key', 'invalid', 'unauthorized'])
        
    def test_v11b_openai_api_authentication_error(self):
        """Test V11b handles OpenAI authentication errors properly"""
        # This SHOULD FAIL initially - V11b doesn't exist
        generator = SlugGenerator(api_key='invalid-key-12345', prompt_version='v11b')
        
        # Should raise authentication error, not crash silently
        with pytest.raises((openai.AuthenticationError, Exception)) as exc_info:
            generator.generate_slug_from_content("test", "test content")
            
        # Error should be related to authentication
        error_msg = str(exc_info.value).lower() 
        assert any(word in error_msg for word in ['auth', 'key', 'invalid', 'unauthorized'])
        
    @pytest.mark.integration
    def test_v11_openai_rate_limiting_handling(self):
        """Test V11 versions handle rate limiting appropriately"""
        # This SHOULD FAIL initially - V11 versions don't exist
        api_key = os.getenv('OPENAI_API_KEY', 'test-key')
        
        # Mock rate limit error
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            # Simulate rate limit error
            mock_client.chat.completions.create.side_effect = openai.RateLimitError(
                "Rate limit exceeded", response=None, body=None
            )
            
            generator_a = SlugGenerator(api_key=api_key, prompt_version='v11a')
            generator_b = SlugGenerator(api_key=api_key, prompt_version='v11b')
            
            # Both should handle rate limiting gracefully
            with pytest.raises(openai.RateLimitError):
                generator_a.generate_slug_from_content("test", "test")
                
            with pytest.raises(openai.RateLimitError):
                generator_b.generate_slug_from_content("test", "test")
                
    @pytest.mark.integration
    def test_v11_openai_model_configuration(self):
        """Test V11 versions use correct OpenAI model configuration"""
        # This SHOULD FAIL initially - V11 versions don't exist
        api_key = os.getenv('OPENAI_API_KEY', 'test-key')
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            # Mock successful response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "test-slug-result"
            mock_client.chat.completions.create.return_value = mock_response
            
            generator_a = SlugGenerator(api_key=api_key, prompt_version='v11a')
            generator_b = SlugGenerator(api_key=api_key, prompt_version='v11b')
            
            # Generate slugs to trigger API calls
            generator_a.generate_slug_from_content("test", "test content")
            generator_b.generate_slug_from_content("test", "test content")
            
            # Verify API was called with correct model
            calls = mock_client.chat.completions.create.call_args_list
            assert len(calls) >= 2
            
            for call in calls:
                args, kwargs = call
                assert 'model' in kwargs
                # Should use the configured model from settings
                assert kwargs['model'] in ['gpt-4o-mini', 'gpt-4', 'gpt-4o']
                
    def test_v11_api_dependency_isolation(self):
        """Test V11 versions don't interfere with each other's API calls"""
        # This SHOULD FAIL initially - V11 versions don't exist
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set - cannot test API isolation")
            
        # Create both generators
        generator_a = SlugGenerator(api_key=api_key, prompt_version='v11a')
        generator_b = SlugGenerator(api_key=api_key, prompt_version='v11b')
        
        # Both should work independently
        result_a = generator_a.generate_slug_from_content("Test A", "Content A")
        result_b = generator_b.generate_slug_from_content("Test B", "Content B")
        
        # Both should succeed
        assert 'primary' in result_a
        assert 'primary' in result_b
        
        # Results should be independent (different slugs expected)
        assert result_a['primary'] != result_b['primary']
        
        # Each should follow its constraints
        words_a = len(result_a['primary'].split('-'))
        words_b = len(result_b['primary'].split('-'))
        
        assert 3 <= words_a <= 5, f"V11a constraint violation: {words_a} words"
        assert 8 <= words_b <= 12, f"V11b constraint violation: {words_b} words"


class TestV11OpenAIResponseProcessing:
    """Test V11 versions properly process OpenAI API responses"""
    
    def test_v11a_response_parsing(self):
        """Test V11a properly parses OpenAI responses"""
        # This SHOULD FAIL initially - V11a doesn't exist
        api_key = os.getenv('OPENAI_API_KEY', 'test-key')
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            # Mock response with typical slug format
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "daigoku-hongkong-shopping"
            mock_client.chat.completions.create.return_value = mock_response
            
            generator = SlugGenerator(api_key=api_key, prompt_version='v11a')
            result = generator.generate_slug_from_content("大國藥妝", "大國藥妝購物")
            
            # Should properly parse the response
            assert 'primary' in result
            assert result['primary'] == "daigoku-hongkong-shopping"
            
    def test_v11b_response_parsing(self):
        """Test V11b properly parses OpenAI responses"""
        # This SHOULD FAIL initially - V11b doesn't exist
        api_key = os.getenv('OPENAI_API_KEY', 'test-key')
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            # Mock response with longer comprehensive slug
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "comprehensive-skinniydip-iface-rhinoshield-phone-case-comparison-guide"
            mock_client.chat.completions.create.return_value = mock_response
            
            generator = SlugGenerator(api_key=api_key, prompt_version='v11b')
            result = generator.generate_slug_from_content("手機殼品牌", "SKINNIYDIP/iface/犀牛盾手機殼比較")
            
            # Should properly parse the comprehensive response
            assert 'primary' in result
            assert result['primary'] == "comprehensive-skinniydip-iface-rhinoshield-phone-case-comparison-guide"
            
            # Should meet V11b word count expectations
            word_count = len(result['primary'].split('-'))
            assert 8 <= word_count <= 12


if __name__ == "__main__":
    print("🔴 TDD RED Phase: Running V11 OpenAI API dependency tests...")
    print("These tests SHOULD fail initially - V11 API integration not implemented yet")
    
    # Run with integration marker
    pytest.main([__file__, '-v', '-m', 'integration', '--tb=short'])