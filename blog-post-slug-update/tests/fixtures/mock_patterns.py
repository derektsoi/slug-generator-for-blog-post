#!/usr/bin/env python3
"""
Mock patterns and fixtures for testing OpenAI integration
Use these patterns during implementation for consistent mocking
"""

from unittest.mock import MagicMock, patch

# Mock OpenAI API responses for different scenarios
MOCK_OPENAI_RESPONSES = {
    'success_jojo': {
        'choices': [{
            'message': {
                'content': 'jojo-maman-bebe-uk-childrens-clothing-guide'
            }
        }]
    },
    'success_doll_clothing': {
        'choices': [{
            'message': {
                'content': 'japanese-doll-clothing-shopping-guide'
            }
        }]
    },
    'success_kindle': {
        'choices': [{
            'message': {
                'content': 'kindle-ereader-buying-guide-comparison'
            }
        }]
    },
    'rate_limit_error': Exception("Rate limit exceeded. Please try again later."),
    'api_error': Exception("OpenAI API request failed"),
    'invalid_response': {
        'choices': [{
            'message': {
                'content': 'invalid response with spaces and CAPS!'
            }
        }]
    }
}

# Mock patterns for different test scenarios
class OpenAIMockPatterns:
    """Reusable mock patterns for OpenAI testing"""
    
    @staticmethod
    def successful_response(slug_content):
        """Create a successful OpenAI API response mock"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = slug_content
        return mock_response
    
    @staticmethod
    def rate_limit_error():
        """Create a rate limit error mock"""
        return Exception("Rate limit exceeded. Please try again later.")
    
    @staticmethod
    def api_error():
        """Create a general API error mock"""
        return Exception("OpenAI API request failed")
    
    @staticmethod
    def mock_openai_client(response_or_exception):
        """Create a complete mock OpenAI client"""
        mock_client = MagicMock()
        
        if isinstance(response_or_exception, Exception):
            mock_client.chat.completions.create.side_effect = response_or_exception
        else:
            mock_client.chat.completions.create.return_value = response_or_exception
        
        return mock_client

# Example usage patterns for implementation:
"""
# Pattern 1: Mock successful API call
@patch('src.slug_generator.openai.OpenAI')
def test_successful_generation(self, mock_openai_class):
    mock_response = OpenAIMockPatterns.successful_response("test-blog-post-slug")
    mock_client = OpenAIMockPatterns.mock_openai_client(mock_response)
    mock_openai_class.return_value = mock_client
    
    generator = SlugGenerator()
    result = generator.generate_slug("https://example.com/test")
    
    self.assertEqual(result['primary'], "test-blog-post-slug")

# Pattern 2: Mock rate limit error
@patch('src.slug_generator.openai.OpenAI')
def test_rate_limit_handling(self, mock_openai_class):
    error = OpenAIMockPatterns.rate_limit_error()
    mock_client = OpenAIMockPatterns.mock_openai_client(error)
    mock_openai_class.return_value = mock_client
    
    generator = SlugGenerator()
    
    with self.assertRaises(Exception) as context:
        generator.generate_slug("https://example.com/test")
    
    self.assertIn("rate limit", str(context.exception).lower())

# Pattern 3: Verify prompt structure
@patch('src.slug_generator.openai.OpenAI')
def test_prompt_structure(self, mock_openai_class):
    mock_response = OpenAIMockPatterns.successful_response("test-slug")
    mock_client = OpenAIMockPatterns.mock_openai_client(mock_response)
    mock_openai_class.return_value = mock_client
    
    generator = SlugGenerator()
    generator.generate_slug("https://example.com/test", title="Test Title", content="Test content")
    
    # Verify the prompt was called with correct structure
    call_args = mock_client.chat.completions.create.call_args
    messages = call_args[1]['messages']
    prompt_content = messages[0]['content']
    
    self.assertIn("SEO-friendly slug", prompt_content)
    self.assertIn("Test Title", prompt_content)
    self.assertIn("Test content", prompt_content)
"""