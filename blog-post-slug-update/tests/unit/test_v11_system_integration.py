"""
V11 System Integration Tests - TDD RED Phase
Tests V11a/V11b system configuration and integration

Following TDD Protocol:
🔴 RED: These tests are designed to FAIL initially
🟢 GREEN: Implementation will make tests pass
🔵 REFACTOR: Code quality improvements while preserving functionality

Anti-Fake Analysis Compliance:
- Tests real system configuration integration
- Validates actual SlugGenerator instantiation  
- Requires real OpenAI API connectivity
"""

import pytest
import sys
import os
from unittest.mock import patch, Mock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from config.settings import SlugGeneratorConfig
from core.slug_generator import SlugGenerator


class TestV11SystemConfiguration:
    """Test V11a/V11b system configuration integration"""
    
    def test_v11a_exists_in_version_settings(self):
        """Test that V11a is configured in VERSION_SETTINGS"""
        # This SHOULD FAIL initially - V11a not yet added to settings
        assert 'v11a' in SlugGeneratorConfig.VERSION_SETTINGS
        
    def test_v11b_exists_in_version_settings(self):
        """Test that V11b is configured in VERSION_SETTINGS"""
        # This SHOULD FAIL initially - V11b not yet added to settings
        assert 'v11b' in SlugGeneratorConfig.VERSION_SETTINGS
        
    def test_v11a_has_correct_constraints(self):
        """Test V11a has 3-5 word constraints"""
        # This SHOULD FAIL initially - V11a configuration doesn't exist
        v11a_config = SlugGeneratorConfig.VERSION_SETTINGS['v11a']
        assert v11a_config['MAX_WORDS'] <= 5
        assert v11a_config['MAX_WORDS'] >= 3
        assert v11a_config['MAX_CHARS'] <= 60  # Shorter constraint for simple slugs
        
    def test_v11b_has_correct_constraints(self):
        """Test V11b has 8-12 word constraints"""
        # This SHOULD FAIL initially - V11b configuration doesn't exist
        v11b_config = SlugGeneratorConfig.VERSION_SETTINGS['v11b']
        assert v11b_config['MAX_WORDS'] <= 12
        assert v11b_config['MAX_WORDS'] >= 8
        assert v11b_config['MAX_CHARS'] <= 90  # Expanded constraint for comprehensive slugs


class TestV11SlugGeneratorInstantiation:
    """Test SlugGenerator can instantiate V11 versions"""
    
    def test_v11a_slug_generator_instantiation(self):
        """Test SlugGenerator can be instantiated with v11a"""
        # This SHOULD FAIL initially - v11a prompt doesn't exist
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            generator = SlugGenerator(prompt_version='v11a')
            assert generator.prompt_version == 'v11a'
            
    def test_v11b_slug_generator_instantiation(self):
        """Test SlugGenerator can be instantiated with v11b"""
        # This SHOULD FAIL initially - v11b prompt doesn't exist
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            generator = SlugGenerator(prompt_version='v11b')
            assert generator.prompt_version == 'v11b'
            
    def test_v11a_prompt_loading(self):
        """Test V11a prompt file exists and loads correctly"""
        # Test that V11a prompt can be loaded
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            generator = SlugGenerator(prompt_version='v11a')
            # Use the internal method to test prompt loading
            prompt_content = generator._load_prompt('v11a')
            assert prompt_content is not None
            assert len(prompt_content) > 0
            assert 'V11a' in prompt_content or 'v11a' in prompt_content.lower()
            
    def test_v11b_prompt_loading(self):
        """Test V11b prompt file exists and loads correctly"""
        # Test that V11b prompt can be loaded
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            generator = SlugGenerator(prompt_version='v11b')
            # Use the internal method to test prompt loading
            prompt_content = generator._load_prompt('v11b')
            assert prompt_content is not None
            assert len(prompt_content) > 0
            assert 'V11b' in prompt_content or 'v11b' in prompt_content.lower()


class TestV11OpenAIIntegration:
    """Test V11 versions work with real OpenAI API"""
    
    @pytest.mark.integration
    def test_v11a_real_openai_connectivity(self):
        """Test V11a can make real OpenAI API calls"""
        # This SHOULD FAIL initially - v11a doesn't exist
        # Requires real OPENAI_API_KEY in environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set - cannot test real API integration")
            
        generator = SlugGenerator(api_key=api_key, prompt_version='v11a')
        
        # Simple test case
        result = generator.generate_slug_from_content(
            title="大國藥妝香港購物教學",
            content="大國藥妝香港購物教學"
        )
        
        # Validate response structure
        assert 'primary' in result
        assert isinstance(result['primary'], str)
        assert len(result['primary']) > 0
        
        # Validate V11a constraints (3-5 words)
        word_count = len(result['primary'].split('-'))
        assert 3 <= word_count <= 5, f"V11a should generate 3-5 words, got {word_count}"
        
    @pytest.mark.integration  
    def test_v11b_real_openai_connectivity(self):
        """Test V11b can make real OpenAI API calls"""
        # This SHOULD FAIL initially - v11b doesn't exist
        # Requires real OPENAI_API_KEY in environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set - cannot test real API integration")
            
        generator = SlugGenerator(api_key=api_key, prompt_version='v11b')
        
        # Complex test case for V11b
        result = generator.generate_slug_from_content(
            title="【2025年最新】日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！",
            content="日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！"
        )
        
        # Validate response structure
        assert 'primary' in result
        assert isinstance(result['primary'], str)
        assert len(result['primary']) > 0
        
        # Validate V11b constraints (8-12 words)
        word_count = len(result['primary'].split('-'))
        assert 8 <= word_count <= 12, f"V11b should generate 8-12 words, got {word_count}"
        
    @pytest.mark.integration
    def test_v11_api_error_handling(self):
        """Test V11 versions handle API errors gracefully"""
        # This SHOULD FAIL initially - V11 versions don't exist
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'invalid-key'}):
            generator_a = SlugGenerator(api_key='invalid-key', prompt_version='v11a')
            generator_b = SlugGenerator(api_key='invalid-key', prompt_version='v11b')
            
            # Both should handle API errors without crashing
            with pytest.raises(Exception):  # Should raise API authentication error
                generator_a.generate_slug_from_content("test", "test")
                
            with pytest.raises(Exception):  # Should raise API authentication error
                generator_b.generate_slug_from_content("test", "test")


class TestV11ABTestingFramework:
    """Test A/B testing framework for V11a vs V11b comparison"""
    
    def test_parallel_v11_generation(self):
        """Test both V11a and V11b can generate slugs for same content"""
        # This SHOULD FAIL initially - V11 versions don't exist
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set - cannot test parallel generation")
            
        # Test content
        title = "Ralph Lauren香港網購教學"
        content = "Ralph Lauren香港網購教學"
        
        # Generate with both versions
        generator_a = SlugGenerator(api_key=api_key, prompt_version='v11a')
        generator_b = SlugGenerator(api_key=api_key, prompt_version='v11b')
        
        result_a = generator_a.generate_slug_from_content(title, content)
        result_b = generator_b.generate_slug_from_content(title, content)
        
        # Both should succeed
        assert 'primary' in result_a
        assert 'primary' in result_b
        
        # Results should be different (different approaches)
        assert result_a['primary'] != result_b['primary']
        
        # Validate constraints
        words_a = len(result_a['primary'].split('-'))
        words_b = len(result_b['primary'].split('-'))
        
        assert 3 <= words_a <= 5, f"V11a: expected 3-5 words, got {words_a}"
        assert 8 <= words_b <= 12, f"V11b: expected 8-12 words, got {words_b}"
        
    def test_v11_vs_baseline_comparison_structure(self):
        """Test framework for comparing V11 vs V8/V10 baselines"""
        # This SHOULD FAIL initially - V11 versions don't exist
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set - cannot test comparison framework")
            
        test_content = {
            'title': '一番賞Online購物教學',
            'content': '一番賞Online購物教學'
        }
        
        # All versions should be instantiable
        generators = {
            'v8': SlugGenerator(api_key=api_key, prompt_version='v8'),
            'v10': SlugGenerator(api_key=api_key, prompt_version='v10'), 
            'v11a': SlugGenerator(api_key=api_key, prompt_version='v11a'),
            'v11b': SlugGenerator(api_key=api_key, prompt_version='v11b')
        }
        
        # All should generate results
        results = {}
        for version, generator in generators.items():
            results[version] = generator.generate_slug_from_content(
                test_content['title'], 
                test_content['content']
            )
            
        # All results should have primary slug
        for version, result in results.items():
            assert 'primary' in result, f"Version {version} missing primary slug"
            assert len(result['primary']) > 0, f"Version {version} empty primary slug"


class TestV11AntiFakeAnalysisValidation:
    """Anti-fake analysis validation tests"""
    
    def test_v11_configuration_exists_before_testing(self):
        """Validate V11 configuration exists before any analysis"""
        # This SHOULD FAIL initially - enforces anti-fake analysis protocol
        
        # Check system configuration
        assert 'v11a' in SlugGeneratorConfig.VERSION_SETTINGS, "V11a not in VERSION_SETTINGS - FAKE ANALYSIS RISK"
        assert 'v11b' in SlugGeneratorConfig.VERSION_SETTINGS, "V11b not in VERSION_SETTINGS - FAKE ANALYSIS RISK"
        
        # Check prompt files exist
        v11a_prompt_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'src', 'config', 'prompts', 'v11a_prompt.txt'
        )
        v11b_prompt_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'src', 'config', 'prompts', 'v11b_prompt.txt'
        )
        
        assert os.path.exists(v11a_prompt_path), "V11a prompt file missing - FAKE ANALYSIS RISK"
        assert os.path.exists(v11b_prompt_path), "V11b prompt file missing - FAKE ANALYSIS RISK"
        
    def test_no_simulation_mode_allowed(self):
        """Ensure no simulation/mock mode for V11 analysis"""
        # This test validates real API integration requirement
        api_key = os.getenv('OPENAI_API_KEY')
        
        # Real API key required - no simulation tolerance
        assert api_key is not None, "Real OPENAI_API_KEY required - no simulation allowed"
        assert api_key.startswith('sk-'), "Invalid API key format - must be real OpenAI key"
        assert len(api_key) > 20, "API key too short - likely fake/test key"


if __name__ == "__main__":
    print("🔴 TDD RED Phase: Running V11 failing tests...")
    print("These tests SHOULD fail initially - V11 not implemented yet")
    
    # Run with verbose output
    pytest.main([__file__, '-v', '--tb=short'])