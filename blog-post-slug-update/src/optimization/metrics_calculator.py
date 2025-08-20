"""
Performance Metrics Calculator

Handles calculation of various performance metrics for LLM optimization,
including theme coverage, duration measurement, and quality scoring.
"""

import time
import re
import statistics
from typing import List, Dict, Any, Optional
from contextlib import contextmanager


class DurationTimer:
    """Context manager for measuring execution duration"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.duration = 0.0
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time


class MetricsCalculator:
    """
    Calculates performance metrics for LLM optimization.
    
    Provides methods for measuring theme coverage, execution duration,
    and other quality metrics relevant to prompt optimization.
    """
    
    def __init__(self):
        self.metric_history = []
        
    def calculate_theme_coverage(self, expected_themes: List[str], output_text: str) -> float:
        """
        Calculate how many expected themes are present in the output.
        
        Args:
            expected_themes: List of themes that should be present
            output_text: Generated text to analyze
            
        Returns:
            Coverage percentage as float (0.0 to 1.0)
        """
        if not expected_themes:
            return 1.0
            
        output_lower = output_text.lower()
        matched_themes = []
        
        for theme in expected_themes:
            theme_lower = theme.lower()
            
            # Check for exact word match or substring match
            if (theme_lower in output_lower or 
                self._fuzzy_theme_match(theme_lower, output_lower)):
                matched_themes.append(theme)
        
        coverage = len(matched_themes) / len(expected_themes)
        
        # Store for analysis
        self.metric_history.append({
            'type': 'theme_coverage',
            'expected': expected_themes,
            'matched': matched_themes,
            'coverage': coverage,
            'output': output_text
        })
        
        return coverage
    
    def _fuzzy_theme_match(self, theme: str, text: str) -> bool:
        """
        Perform fuzzy matching for theme detection.
        
        Args:
            theme: Theme to match
            text: Text to search in
            
        Returns:
            True if theme likely present
        """
        # Handle common variations
        variations = {
            'uk': ['britain', 'england', 'british'],
            'us': ['usa', 'america', 'american', 'united-states'],
            'clothes': ['clothing', 'fashion', 'apparel'],
            'baby': ['infant', 'toddler', 'kids', 'children'],
            'shopping': ['buying', 'purchase', 'buy'],
            'guide': ['tutorial', 'how-to', 'tips'],
            'japan': ['japanese', 'jp'],
            'comparison': ['compare', 'vs', 'versus']
        }
        
        # Check if theme or its variations are present
        theme_variants = variations.get(theme, []) + [theme]
        
        for variant in theme_variants:
            if variant in text:
                return True
                
        return False
    
    @contextmanager
    def measure_duration(self):
        """
        Context manager for measuring execution duration.
        
        Usage:
            with calculator.measure_duration() as timer:
                # code to time
                pass
            print(timer.duration)
        """
        timer = DurationTimer()
        try:
            yield timer.__enter__()
        finally:
            timer.__exit__(None, None, None)
    
    def calculate_seo_compliance(self, text: str) -> Dict[str, Any]:
        """
        Calculate SEO compliance metrics for slug generation.
        
        Args:
            text: Generated slug or text to analyze
            
        Returns:
            Dictionary with SEO compliance metrics
        """
        # Remove any URL encoding
        clean_text = text.replace('%', '').replace('-', ' ')
        words = clean_text.split()
        
        return {
            'word_count': len(words),
            'character_count': len(text),
            'has_hyphens': '-' in text,
            'no_spaces': ' ' not in text,
            'lowercase': text.islower(),
            'no_special_chars': bool(re.match(r'^[a-z0-9-]+$', text)),
            'seo_compliant': (
                3 <= len(words) <= 6 and 
                len(text) <= 60 and
                '-' in text and
                ' ' not in text and
                text.islower()
            )
        }
    
    def calculate_confidence_metrics(self, confidence_scores: List[float]) -> Dict[str, float]:
        """
        Calculate aggregate confidence metrics.
        
        Args:
            confidence_scores: List of confidence scores from results
            
        Returns:
            Dictionary with confidence statistics
        """
        if not confidence_scores:
            return {'avg_confidence': 0.0, 'min_confidence': 0.0, 'max_confidence': 0.0}
        
        return {
            'avg_confidence': statistics.mean(confidence_scores),
            'min_confidence': min(confidence_scores),
            'max_confidence': max(confidence_scores),
            'confidence_stdev': statistics.stdev(confidence_scores) if len(confidence_scores) > 1 else 0.0,
            'high_confidence_ratio': len([s for s in confidence_scores if s >= 0.8]) / len(confidence_scores)
        }
    
    def analyze_failure_patterns(self, failed_results: List[Dict]) -> Dict[str, Any]:
        """
        Analyze patterns in failed test cases.
        
        Args:
            failed_results: List of failed test result dictionaries
            
        Returns:
            Analysis of failure patterns
        """
        if not failed_results:
            return {'failure_rate': 0.0, 'common_errors': []}
        
        error_messages = [r.get('error', 'Unknown error') for r in failed_results]
        error_counts = {}
        
        for error in error_messages:
            # Group similar errors
            error_type = self._classify_error(error)
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        common_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'total_failures': len(failed_results),
            'failure_rate': len(failed_results),  # Will be calculated by caller
            'common_errors': common_errors,
            'error_distribution': error_counts,
            'recommendations': self._generate_failure_recommendations(common_errors)
        }
    
    def _classify_error(self, error_message: str) -> str:
        """Classify error message into category"""
        error_lower = error_message.lower()
        
        if 'timeout' in error_lower or 'time' in error_lower:
            return 'timeout'
        elif 'rate limit' in error_lower:
            return 'rate_limit'
        elif 'json' in error_lower or 'parse' in error_lower:
            return 'parsing_error'
        elif 'api' in error_lower or 'openai' in error_lower:
            return 'api_error'
        elif 'connection' in error_lower or 'network' in error_lower:
            return 'connection_error'
        else:
            return 'other'
    
    def _generate_failure_recommendations(self, common_errors: List[tuple]) -> List[str]:
        """Generate recommendations based on failure patterns"""
        recommendations = []
        
        for error_type, count in common_errors[:3]:  # Top 3 errors
            if error_type == 'timeout':
                recommendations.append("Consider increasing timeout values or optimizing prompt length")
            elif error_type == 'rate_limit':
                recommendations.append("Add rate limiting delays or reduce concurrent requests")
            elif error_type == 'parsing_error':
                recommendations.append("Review JSON response format requirements in prompts")
            elif error_type == 'api_error':
                recommendations.append("Check API key validity and service status")
            elif error_type == 'connection_error':
                recommendations.append("Verify network connectivity and API endpoint availability")
        
        return recommendations
    
    def get_metric_trends(self) -> Dict[str, Any]:
        """
        Analyze trends in metrics over time.
        
        Returns:
            Dictionary with trend analysis
        """
        if len(self.metric_history) < 2:
            return {'insufficient_data': True}
        
        theme_coverages = [m['coverage'] for m in self.metric_history if m['type'] == 'theme_coverage']
        
        if len(theme_coverages) < 2:
            return {'insufficient_theme_data': True}
        
        # Simple trend calculation
        recent_avg = statistics.mean(theme_coverages[-5:]) if len(theme_coverages) >= 5 else statistics.mean(theme_coverages)
        overall_avg = statistics.mean(theme_coverages)
        
        return {
            'theme_coverage_trend': 'improving' if recent_avg > overall_avg else 'declining',
            'recent_avg_coverage': recent_avg,
            'overall_avg_coverage': overall_avg,
            'total_measurements': len(theme_coverages),
            'coverage_variance': statistics.variance(theme_coverages) if len(theme_coverages) > 1 else 0
        }