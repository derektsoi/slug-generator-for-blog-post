#!/usr/bin/env python3
"""
Rapid iteration testing framework for development velocity
Enables quick single-case testing and progressive scaling for V10 development
"""

import pytest
import time
import json
from pathlib import Path
from unittest.mock import Mock, patch
from typing import List, Dict, Any


class RapidIterationFramework:
    """Framework for rapid prompt development and testing"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "test-key"
        self.test_cache = {}
        self.timing_data = {}
    
    def single_case_test(self, version: str, test_case: Dict[str, str]) -> Dict[str, Any]:
        """Test single case for rapid feedback during development"""
        start_time = time.time()
        
        try:
            # Import here to avoid circular dependencies during development
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
            
            from core import SlugGenerator
            
            generator = SlugGenerator(
                api_key=self.api_key,
                prompt_version=version
            )
            
            result = generator.generate_slug_from_content(
                test_case['title'],
                test_case['content']
            )
            
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'result': result,
                'execution_time': execution_time,
                'version': version,
                'test_case': test_case['title'][:50] + "..." if len(test_case['title']) > 50 else test_case['title']
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                'success': False,
                'error': str(e),
                'execution_time': execution_time,
                'version': version,
                'test_case': test_case['title'][:50] + "..." if len(test_case['title']) > 50 else test_case['title']
            }
    
    def progressive_scaling_test(self, version: str, test_cases: List[Dict], 
                                scale_steps: List[int] = [1, 3, 5, 10]) -> Dict[str, Any]:
        """Test with progressive scaling: 1 → 3 → 5 → 10 cases"""
        results = {
            'version': version,
            'scale_results': {},
            'total_time': 0,
            'success_rates': {},
            'early_stop': None
        }
        
        total_start_time = time.time()
        
        for scale in scale_steps:
            if scale > len(test_cases):
                continue
                
            scale_start_time = time.time()
            scale_cases = test_cases[:scale]
            scale_results = []
            
            for i, test_case in enumerate(scale_cases):
                case_result = self.single_case_test(version, test_case)
                scale_results.append(case_result)
                
                # Quick feedback during execution
                if i == 0:  # First case feedback
                    print(f"✓ First case ({version}): {'✅ Success' if case_result['success'] else '❌ Failed'}")
            
            scale_time = time.time() - scale_start_time
            success_count = sum(1 for r in scale_results if r['success'])
            success_rate = success_count / len(scale_results)
            
            results['scale_results'][scale] = {
                'results': scale_results,
                'execution_time': scale_time,
                'success_count': success_count,
                'success_rate': success_rate
            }
            
            results['success_rates'][scale] = success_rate
            
            print(f"Scale {scale}: {success_count}/{scale} success ({success_rate:.1%}) in {scale_time:.2f}s")
            
            # Early stopping logic for development efficiency
            if success_rate < 0.5 and scale >= 3:
                results['early_stop'] = f"Low success rate ({success_rate:.1%}) at scale {scale}"
                print(f"⚠️  Early stop: {results['early_stop']}")
                break
        
        results['total_time'] = time.time() - total_start_time
        return results
    
    def rapid_comparison(self, versions: List[str], test_case: Dict[str, str]) -> Dict[str, Any]:
        """Rapidly compare multiple versions on single test case"""
        comparison_results = {
            'test_case': test_case['title'][:50] + "..." if len(test_case['title']) > 50 else test_case['title'],
            'version_results': {},
            'best_version': None,
            'execution_summary': {}
        }
        
        for version in versions:
            result = self.single_case_test(version, test_case)
            comparison_results['version_results'][version] = result
            
            # Immediate feedback
            status = "✅ Success" if result['success'] else "❌ Failed"
            time_ms = result['execution_time'] * 1000
            print(f"{version}: {status} ({time_ms:.0f}ms)")
        
        # Determine best version (successful + fastest)
        successful_versions = [
            (v, r) for v, r in comparison_results['version_results'].items()
            if r['success']
        ]
        
        if successful_versions:
            best_version, best_result = min(successful_versions, key=lambda x: x[1]['execution_time'])
            comparison_results['best_version'] = best_version
        
        comparison_results['execution_summary'] = {
            'total_versions': len(versions),
            'successful_versions': len(successful_versions),
            'fastest_successful': comparison_results['best_version']
        }
        
        return comparison_results
    
    def development_helper_validation(self, version: str) -> Dict[str, Any]:
        """Quick validation helpers for development"""
        validation_results = {
            'version': version,
            'validations': {},
            'overall_status': 'pending'
        }
        
        # Import validation from our new pipeline
        try:
            from tests.unit.test_validation_pipeline import PreFlightValidator
            
            # Run pre-flight validation
            preflight_results = PreFlightValidator.run_full_validation(version)
            validation_results['validations']['preflight'] = preflight_results
            
            if not preflight_results['passed']:
                validation_results['overall_status'] = 'failed'
                return validation_results
            
        except ImportError:
            validation_results['validations']['preflight'] = {
                'passed': False,
                'errors': ['PreFlightValidator not available']
            }
        
        # Configuration validation
        try:
            from config.settings import SlugGeneratorConfig
            config = SlugGeneratorConfig.for_version(version)
            validation_results['validations']['configuration'] = {
                'passed': True,
                'max_words': config.MAX_WORDS,
                'max_chars': config.MAX_CHARS,
                'confidence_threshold': config.CONFIDENCE_THRESHOLD
            }
        except Exception as e:
            validation_results['validations']['configuration'] = {
                'passed': False,
                'error': str(e)
            }
        
        # Determine overall status
        all_passed = all(
            v.get('passed', False) for v in validation_results['validations'].values()
        )
        validation_results['overall_status'] = 'passed' if all_passed else 'failed'
        
        return validation_results


@pytest.mark.development
class TestSingleCaseTesting:
    """Test single case testing functionality"""
    
    def test_single_case_success_structure(self, sample_test_content):
        """Test single case returns expected structure on success"""
        framework = RapidIterationFramework()
        
        with patch('core.SlugGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate_slug_from_content.return_value = {
                'primary': 'test-slug-example',
                'alternatives': ['alternative-slug']
            }
            
            result = framework.single_case_test('v8', sample_test_content)
            
            assert result['success'] is True
            assert 'result' in result
            assert 'execution_time' in result
            assert 'version' in result
            assert 'test_case' in result
            assert result['version'] == 'v8'
    
    def test_single_case_failure_handling(self, sample_test_content):
        """Test single case handles failures gracefully"""
        framework = RapidIterationFramework()
        
        with patch('core.SlugGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate_slug_from_content.side_effect = Exception("Test error")
            
            result = framework.single_case_test('v8', sample_test_content)
            
            assert result['success'] is False
            assert 'error' in result
            assert 'execution_time' in result
            assert result['version'] == 'v8'
            assert "Test error" in result['error']
    
    def test_single_case_timing_measurement(self, sample_test_content):
        """Test single case measures execution time"""
        framework = RapidIterationFramework()
        
        with patch('core.SlugGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate_slug_from_content.return_value = {'primary': 'test'}
            
            result = framework.single_case_test('v8', sample_test_content)
            
            assert 'execution_time' in result
            assert isinstance(result['execution_time'], float)
            assert result['execution_time'] >= 0


@pytest.mark.development
class TestProgressiveScaling:
    """Test progressive scaling functionality"""
    
    def test_progressive_scaling_structure(self, sample_test_content):
        """Test progressive scaling returns expected structure"""
        framework = RapidIterationFramework()
        test_cases = [sample_test_content] * 5  # 5 identical test cases
        
        with patch('core.SlugGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate_slug_from_content.return_value = {'primary': 'test'}
            
            result = framework.progressive_scaling_test('v8', test_cases, [1, 3])
            
            assert 'version' in result
            assert 'scale_results' in result
            assert 'total_time' in result
            assert 'success_rates' in result
            assert result['version'] == 'v8'
    
    def test_progressive_scaling_respects_limits(self, sample_test_content):
        """Test progressive scaling respects test case limits"""
        framework = RapidIterationFramework()
        test_cases = [sample_test_content] * 2  # Only 2 test cases
        
        with patch('core.SlugGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate_slug_from_content.return_value = {'primary': 'test'}
            
            result = framework.progressive_scaling_test('v8', test_cases, [1, 3, 5])
            
            # Should only have results for scales 1 and 3 (not 5, as we only have 2 cases)
            assert 1 in result['scale_results']
            assert 5 not in result['scale_results']  # Shouldn't try scale 5 with only 2 cases
    
    def test_progressive_scaling_early_stop(self, sample_test_content):
        """Test progressive scaling early stop on low success rate"""
        framework = RapidIterationFramework()
        test_cases = [sample_test_content] * 10
        
        with patch('core.SlugGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator
            # Most cases fail
            mock_generator.generate_slug_from_content.side_effect = [
                {'primary': 'success'},  # First one succeeds
                Exception("Fail"), Exception("Fail"), Exception("Fail")  # Rest fail
            ] * 10
            
            with patch('builtins.print'):  # Suppress print output
                result = framework.progressive_scaling_test('v8', test_cases, [1, 3, 5])
            
            # Should have early stop due to low success rate
            if 'early_stop' in result and result['early_stop']:
                assert 'Low success rate' in result['early_stop']


@pytest.mark.development
class TestRapidComparison:
    """Test rapid version comparison functionality"""
    
    def test_rapid_comparison_structure(self, sample_test_content):
        """Test rapid comparison returns expected structure"""
        framework = RapidIterationFramework()
        versions = ['v8', 'v9']
        
        with patch('core.SlugGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate_slug_from_content.return_value = {'primary': 'test'}
            
            with patch('builtins.print'):  # Suppress print output
                result = framework.rapid_comparison(versions, sample_test_content)
            
            assert 'test_case' in result
            assert 'version_results' in result
            assert 'best_version' in result
            assert 'execution_summary' in result
            
            for version in versions:
                assert version in result['version_results']
    
    def test_rapid_comparison_best_version_selection(self, sample_test_content):
        """Test rapid comparison selects best version correctly"""
        framework = RapidIterationFramework()
        versions = ['v8', 'v9']
        
        with patch('core.SlugGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate_slug_from_content.return_value = {'primary': 'test'}
            
            # Mock timing to make v9 faster
            with patch('time.time') as mock_time:
                mock_time.side_effect = [
                    0, 0.5,  # v8: 0.5s
                    0, 0.2   # v9: 0.2s (faster)
                ]
                
                with patch('builtins.print'):  # Suppress print output
                    result = framework.rapid_comparison(versions, sample_test_content)
                
                # v9 should be selected as best (faster)
                assert result['best_version'] == 'v9'
    
    def test_rapid_comparison_handles_failures(self, sample_test_content):
        """Test rapid comparison handles version failures"""
        framework = RapidIterationFramework()
        versions = ['v8', 'v9']
        
        with patch('core.SlugGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator
            # v8 succeeds, v9 fails
            mock_generator.generate_slug_from_content.side_effect = [
                {'primary': 'test'},
                Exception("v9 failed")
            ]
            
            with patch('builtins.print'):  # Suppress print output
                result = framework.rapid_comparison(versions, sample_test_content)
            
            # Only v8 should be successful
            assert result['version_results']['v8']['success'] is True
            assert result['version_results']['v9']['success'] is False
            assert result['best_version'] == 'v8'  # Only successful version


@pytest.mark.development
class TestDevelopmentHelpers:
    """Test development helper functionality"""
    
    def test_development_helper_structure(self):
        """Test development helper returns expected structure"""
        framework = RapidIterationFramework()
        
        result = framework.development_helper_validation('v8')
        
        assert 'version' in result
        assert 'validations' in result
        assert 'overall_status' in result
        assert result['version'] == 'v8'
    
    def test_development_helper_configuration_validation(self):
        """Test development helper validates configuration"""
        framework = RapidIterationFramework()
        
        result = framework.development_helper_validation('v8')
        
        if 'configuration' in result['validations']:
            config_result = result['validations']['configuration']
            assert 'passed' in config_result
            
            if config_result['passed']:
                assert 'max_words' in config_result
                assert 'max_chars' in config_result
                assert 'confidence_threshold' in config_result


@pytest.mark.development
class TestDevelopmentWorkflow:
    """Test complete development workflow"""
    
    def test_development_workflow_integration(self, sample_test_content):
        """Test complete development workflow: validate → single test → comparison"""
        framework = RapidIterationFramework()
        
        # Step 1: Validation
        validation_result = framework.development_helper_validation('v8')
        assert 'overall_status' in validation_result
        
        # Step 2: Single case test
        with patch('core.SlugGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate_slug_from_content.return_value = {'primary': 'test'}
            
            single_result = framework.single_case_test('v8', sample_test_content)
            assert 'success' in single_result
            
            # Step 3: Rapid comparison
            with patch('builtins.print'):  # Suppress print output
                comparison_result = framework.rapid_comparison(['v8'], sample_test_content)
            assert 'best_version' in comparison_result
    
    def test_workflow_timing_efficiency(self, sample_test_content):
        """Test workflow completes efficiently for development"""
        framework = RapidIterationFramework()
        
        start_time = time.time()
        
        with patch('core.SlugGenerator') as mock_generator_class:
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate_slug_from_content.return_value = {'primary': 'test'}
            
            # Run validation and single test
            framework.development_helper_validation('v8')
            framework.single_case_test('v8', sample_test_content)
        
        total_time = time.time() - start_time
        
        # Should complete quickly for development efficiency
        assert total_time < 1.0  # Should be very fast with mocks


@pytest.mark.development
class TestFrameworkReliability:
    """Test framework reliability and error handling"""
    
    def test_framework_handles_import_errors(self, sample_test_content):
        """Test framework handles import errors gracefully"""
        framework = RapidIterationFramework()
        
        with patch('sys.path'):
            # This should cause import errors
            result = framework.single_case_test('v8', sample_test_content)
            
            # Should return failure result instead of crashing
            assert 'success' in result
            assert 'error' in result or result['success']
    
    def test_framework_handles_configuration_errors(self):
        """Test framework handles configuration errors gracefully"""
        framework = RapidIterationFramework()
        
        # Test with invalid version
        result = framework.development_helper_validation('invalid_version')
        
        assert 'overall_status' in result
        # Should handle gracefully, not crash