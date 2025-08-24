"""
Tests for GPT Authenticity Validation System

These tests ensure our anti-fake analysis system works correctly
and can detect simulated vs real GPT responses.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from validation.gpt_authenticity_validator import (
    GPTAuthenticityValidator,
    APICallTrace,
    GPTFingerprint,
    TrackedSlugGenerator
)


class TestGPTAuthenticityValidator:
    """Test the GPT authenticity validation system"""
    
    def test_authentic_response_detection(self):
        """Test detection of authentic GPT responses"""
        validator = GPTAuthenticityValidator()
        
        # Create a trace that looks like a real GPT response
        authentic_trace = APICallTrace(
            timestamp=datetime.now().isoformat(),
            request_hash="real123",
            response_hash="real456",
            model="gpt-4o-mini",
            prompt_snippet="Generate SEO slug for blog post...",
            response_snippet='{"analysis": {"detected_brands": ["brand"]}, "slugs": [{"slug": "brand-hongkong-shopping", "confidence": 0.85, "reasoning": "Brand detected with location context"}]}',
            response_time_ms=2500,  # Realistic timing
            token_count=150,  # Real API metadata
            confidence_scores=[0.85],
            reasoning_present=True,  # Has reasoning
            analysis_present=True   # Has analysis structure
        )
        
        response_content = '{"analysis": {"detected_brands": ["brand"]}, "slugs": [{"slug": "brand-hongkong-shopping", "confidence": 0.85, "reasoning": "Brand detected with location context"}]}'
        
        fingerprint = validator.validate_response_authenticity(response_content, authentic_trace)
        is_authentic, reason = validator.is_response_authentic(fingerprint)
        
        assert is_authentic, f"Should detect authentic response, but got: {reason}"
        assert fingerprint.has_reasoning
        assert fingerprint.has_analysis_structure
        assert fingerprint.temporal_consistency
        assert fingerprint.api_metadata_present
        assert fingerprint.content_coherence_score > 0.5
    
    def test_fake_response_detection(self):
        """Test detection of fake/simulated responses"""
        validator = GPTAuthenticityValidator()
        
        # Create a trace that looks fake
        fake_trace = APICallTrace(
            timestamp=datetime.now().isoformat(),
            request_hash="fake123",
            response_hash="fake456",
            model="gpt-4o-mini",
            prompt_snippet="Generate slug...",
            response_snippet='{"slugs": [{"slug": "hardcoded-test-slug", "confidence": 1.0}]}',
            response_time_ms=10,  # Suspiciously fast
            token_count=None,  # No API metadata
            confidence_scores=[1.0],  # Perfect confidence is suspicious
            reasoning_present=False,  # No reasoning
            analysis_present=False   # No analysis
        )
        
        response_content = '{"slugs": [{"slug": "hardcoded-test-slug", "confidence": 1.0}]}'
        
        fingerprint = validator.validate_response_authenticity(response_content, fake_trace)
        is_authentic, reason = validator.is_response_authentic(fingerprint)
        
        assert not is_authentic, "Should detect fake response as inauthentic"
        assert "reasoning or analysis structure" in reason.lower()
        assert not fingerprint.has_reasoning
        assert not fingerprint.has_analysis_structure
        assert not fingerprint.temporal_consistency
        assert not fingerprint.api_metadata_present
    
    def test_duplicate_response_detection(self):
        """Test detection of duplicate responses"""
        validator = GPTAuthenticityValidator()
        
        # First trace
        trace1 = APICallTrace(
            timestamp=datetime.now().isoformat(),
            request_hash="req1",
            response_hash="same_response",  # Same response hash
            model="gpt-4o-mini",
            prompt_snippet="First prompt...",
            response_snippet='{"slugs": [{"slug": "identical-response"}]}',
            response_time_ms=2000,
            token_count=100,
            confidence_scores=[0.8],
            reasoning_present=True,
            analysis_present=True
        )
        
        # Second trace with identical response
        trace2 = APICallTrace(
            timestamp=datetime.now().isoformat(),
            request_hash="req2",  # Different request
            response_hash="same_response",  # But same response - suspicious!
            model="gpt-4o-mini",
            prompt_snippet="Different prompt...",
            response_snippet='{"slugs": [{"slug": "identical-response"}]}',
            response_time_ms=2000,
            token_count=100,
            confidence_scores=[0.8],
            reasoning_present=True,
            analysis_present=True
        )
        
        # Process first trace
        validator.call_traces.append(trace1)
        validator.response_hashes.add(trace1.response_hash)
        
        # Process second trace - should detect as duplicate
        validator.call_traces.append(trace2)  # Add to traces first
        fingerprint2 = validator.validate_response_authenticity('{"slugs": [{"slug": "identical-response"}]}', trace2)
        
        # Response variability should be low due to duplicate
        assert fingerprint2.response_variability < 0.8, "Should detect low variability for duplicate response"
    
    def test_api_call_tracing(self):
        """Test that API calls are properly traced"""
        validator = GPTAuthenticityValidator()
        
        request_data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "user", "content": "Test prompt for tracing"}
            ],
            "max_tokens": 100,
            "temperature": 0.3
        }
        
        response_data = {
            "choices": [{
                "message": {
                    "content": '{"slugs": [{"slug": "traced-response", "confidence": 0.8, "reasoning": "Test reasoning"}]}'
                }
            }],
            "usage": {
                "total_tokens": 85
            }
        }
        
        start_time = 1234567890.0
        end_time = 1234567892.5  # 2.5 second response time
        
        trace = validator.trace_api_call(request_data, response_data, start_time, end_time)
        
        assert trace.model == "gpt-4o-mini"
        assert trace.response_time_ms == 2500
        assert trace.token_count == 85
        assert trace.reasoning_present == True
        assert trace.analysis_present == False  # No analysis structure in this example
        assert "Test prompt" in trace.prompt_snippet
        assert "traced-response" in trace.response_snippet
    
    def test_authenticity_report_generation(self):
        """Test generation of comprehensive authenticity reports"""
        validator = GPTAuthenticityValidator()
        
        # Add some sample traces
        authentic_trace = APICallTrace(
            timestamp=datetime.now().isoformat(),
            request_hash="auth1",
            response_hash="auth_resp1",
            model="gpt-4o-mini",
            prompt_snippet="Authentic prompt...",
            response_snippet='{"analysis": {}, "slugs": [{"slug": "authentic-slug", "reasoning": "Good reasoning"}]}',
            response_time_ms=2000,
            token_count=120,
            confidence_scores=[0.85],
            reasoning_present=True,
            analysis_present=True
        )
        
        suspicious_trace = APICallTrace(
            timestamp=datetime.now().isoformat(),
            request_hash="sus1",
            response_hash="sus_resp1",
            model="gpt-4o-mini",
            prompt_snippet="Suspicious prompt...",
            response_snippet='{"slugs": [{"slug": "fake-slug"}]}',
            response_time_ms=10,  # Too fast
            token_count=None,  # No metadata
            confidence_scores=[],
            reasoning_present=False,
            analysis_present=False
        )
        
        validator.call_traces = [authentic_trace, suspicious_trace]
        validator.response_hashes = {"auth_resp1", "sus_resp1"}
        
        report = validator.generate_authenticity_report()
        
        assert report["total_calls"] == 2
        assert report["authentic_calls"] == 1  # Only the first one should be authentic
        assert report["suspicious_calls"] == 1
        assert report["authenticity_rate"] == 0.5
        assert report["unique_responses"] == 2
        assert len(report["issues_summary"]) == 1  # One suspicious call should have issues
    
    @pytest.mark.integration
    @pytest.mark.skipif(not os.getenv('OPENAI_API_KEY'), reason="OPENAI_API_KEY not set")
    def test_tracked_slug_generator_integration(self):
        """Integration test with real SlugGenerator"""
        from core.slug_generator import SlugGenerator
        
        api_key = os.getenv('OPENAI_API_KEY')
        base_generator = SlugGenerator(api_key=api_key, prompt_version='v11a')
        validator = GPTAuthenticityValidator()
        
        tracked_generator = TrackedSlugGenerator(base_generator, validator)
        
        # Generate a real slug
        result = tracked_generator.generator.generate_slug_from_content(
            "Test Content",
            "Test content for authenticity validation"
        )
        
        # Check that result is valid
        assert 'primary' in result
        assert isinstance(result['primary'], str)
        assert len(result['primary']) > 0
        
        # Check that API call was traced
        assert len(validator.call_traces) == 1
        trace = validator.call_traces[0]
        
        assert trace.model == "gpt-4o-mini"
        assert trace.token_count is not None
        assert trace.response_time_ms > 500  # Should take reasonable time
        
        # Check authenticity
        fingerprint = validator.validate_response_authenticity("", trace)
        is_authentic, reason = validator.is_response_authentic(fingerprint)
        
        # Real API call should be authentic
        assert is_authentic or "rate limit" in reason.lower(), f"Real API call should be authentic: {reason}"


if __name__ == "__main__":
    pytest.main([__file__, '-v'])