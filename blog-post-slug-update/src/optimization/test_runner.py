"""
Test Execution Engine

Handles execution of test cases, collection of results, and aggregation
of performance metrics for LLM optimization.
"""

import time
import statistics
from typing import Dict, List, Callable, Any
from contextlib import contextmanager

from .metrics_calculator import MetricsCalculator


class TestRunner:
    """
    Executes test cases and collects performance metrics.
    
    Responsible for running individual test cases, measuring performance,
    and aggregating results across multiple tests.
    """
    
    def __init__(self, test_cases: List[Dict], metrics_calculator: MetricsCalculator):
        """
        Initialize test runner.
        
        Args:
            test_cases: List of test case dictionaries
            metrics_calculator: Calculator for performance metrics
        """
        self.test_cases = test_cases
        self.metrics_calculator = metrics_calculator
        self.results = []
        
    def execute_single_test(self, test_function: Callable, test_case: Dict) -> Dict[str, Any]:
        """
        Execute a single test case and collect metrics.
        
        Args:
            test_function: Function to test (takes test input, returns result)
            test_case: Test case dictionary with 'input' and 'expected' keys
            
        Returns:
            Dictionary with test results and metrics
        """
        test_input = test_case['input']
        expected_outcomes = test_case.get('expected', [])
        
        # Measure execution time
        with self.metrics_calculator.measure_duration() as timer:
            try:
                # Execute the test function
                result = test_function(test_input)
                success = True
                error = None
                
            except Exception as e:
                result = None
                success = False
                error = str(e)
        
        # Calculate metrics if test succeeded
        metrics = {}
        if success and result:
            # Calculate theme coverage if expected themes provided
            if expected_outcomes:
                output_text = self._extract_output_text(result)
                metrics['theme_coverage'] = self.metrics_calculator.calculate_theme_coverage(
                    expected_outcomes, output_text
                )
                
            # Add other metrics
            metrics.update({
                'confidence': result.get('confidence', 0.0) if isinstance(result, dict) else 0.0,
                'output_length': len(str(result)),
            })
        
        return {
            'test_input': test_input,
            'result': result,
            'success': success,
            'error': error,
            'duration': timer.duration,
            'expected': expected_outcomes,
            **metrics
        }
    
    def execute_all_tests(self, test_function: Callable) -> Dict[str, Any]:
        """
        Execute all test cases and return aggregated results.
        
        Args:
            test_function: Function to test across all cases
            
        Returns:
            Aggregated results dictionary with summary metrics
        """
        individual_results = []
        
        for test_case in self.test_cases:
            result = self.execute_single_test(test_function, test_case)
            individual_results.append(result)
        
        # Aggregate metrics
        successful_tests = [r for r in individual_results if r['success']]
        total_tests = len(individual_results)
        
        if not successful_tests:
            return {
                'success_rate': 0.0,
                'total_tests': total_tests,
                'successful_tests': 0,
                'individual_results': individual_results
            }
        
        # Calculate aggregate metrics
        theme_coverages = [r.get('theme_coverage', 0) for r in successful_tests if 'theme_coverage' in r]
        durations = [r['duration'] for r in successful_tests]
        confidences = [r.get('confidence', 0) for r in successful_tests]
        
        # Create detailed individual results with enhanced metadata
        detailed_individual_results = []
        for i, result in enumerate(individual_results):
            test_case = self.test_cases[i] if i < len(self.test_cases) else {}
            
            detailed_result = {
                'url_index': test_case.get('url_index', i),
                'original_title': test_case.get('input', {}).get('title', 'Unknown Title'),
                'category': test_case.get('category', 'unknown'),
                'generated_slug': self._extract_primary_slug(result.get('result')),
                'theme_coverage': result.get('theme_coverage', 0),
                'duration': result['duration'],
                'success': result['success'],
                'confidence': result.get('confidence', 0),
                'expected_themes': result.get('expected', []),
                'error': result.get('error')
            }
            detailed_individual_results.append(detailed_result)
        
        aggregated = {
            'success_rate': len(successful_tests) / total_tests,
            'total_tests': total_tests,
            'successful_tests': len(successful_tests),
            'avg_duration': statistics.mean(durations) if durations else 0,
            'total_duration': sum(durations),
            'min_duration': min(durations) if durations else 0,
            'max_duration': max(durations) if durations else 0,
            'individual_results': individual_results,
            'detailed_individual_results': detailed_individual_results  # NEW: Enhanced detailed results
        }
        
        # Add theme coverage metrics if available
        if theme_coverages:
            aggregated.update({
                'avg_theme_coverage': statistics.mean(theme_coverages),
                'min_theme_coverage': min(theme_coverages),
                'max_theme_coverage': max(theme_coverages),
                'theme_coverage_stdev': statistics.stdev(theme_coverages) if len(theme_coverages) > 1 else 0
            })
        
        # Add confidence metrics if available
        if confidences:
            aggregated.update({
                'avg_confidence': statistics.mean(confidences),
                'min_confidence': min(confidences),
                'max_confidence': max(confidences)
            })
        
        return aggregated
    
    def _extract_output_text(self, result: Any) -> str:
        """
        Extract text from test function result for analysis.
        
        Args:
            result: Result from test function
            
        Returns:
            Text string for analysis
        """
        if isinstance(result, dict):
            # Handle structured results (e.g., {'primary': 'slug', 'alternatives': [...]})
            if 'primary' in result:
                text = result['primary']
                if 'alternatives' in result and result['alternatives']:
                    text += ' ' + ' '.join(result['alternatives'])
                return text
            elif 'output' in result:
                return str(result['output'])
            else:
                # Concatenate all string values
                return ' '.join(str(v) for v in result.values() if isinstance(v, str))
        elif isinstance(result, str):
            return result
        else:
            return str(result)
    
    def _extract_primary_slug(self, result: Any) -> str:
        """
        Extract primary slug from test function result.
        
        Args:
            result: Result from test function
            
        Returns:
            Primary slug string for display
        """
        if isinstance(result, dict):
            # Handle SlugGenerator structured results
            if 'primary' in result:
                return result['primary']
            elif 'slug' in result:
                return result['slug']
            elif 'output' in result:
                return str(result['output'])
            else:
                # Return first string value found
                for value in result.values():
                    if isinstance(value, str) and value:
                        return value
                return 'unknown-slug'
        elif isinstance(result, str):
            return result
        else:
            return str(result) if result else 'unknown-slug'
    
    def get_failed_tests(self) -> List[Dict]:
        """
        Get list of failed test cases for analysis.
        
        Returns:
            List of failed test result dictionaries
        """
        return [r for r in self.results if not r['success']]
    
    def get_low_performing_tests(self, threshold: float = 0.5) -> List[Dict]:
        """
        Get tests that performed below threshold.
        
        Args:
            threshold: Performance threshold (0.0 to 1.0)
            
        Returns:
            List of low-performing test results
        """
        return [
            r for r in self.results 
            if r['success'] and r.get('theme_coverage', 0) < threshold
        ]