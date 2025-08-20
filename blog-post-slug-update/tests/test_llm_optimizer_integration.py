#!/usr/bin/env python3
"""
Integration Test for LLM Optimization Tool with Slug Generator

This test demonstrates how the LLM optimization tool should integrate with
the existing slug generator to provide systematic prompt optimization.
"""

import pytest
import sys
import os
import json
from unittest.mock import Mock, patch

# Add src directory to Python path
sys.path.insert(0, 'src')

class TestSlugGeneratorOptimization:
    """Integration test for optimizing the slug generator using the LLM optimization tool"""
    
    def test_slug_generator_optimization_workflow(self):
        """Complete workflow: analyze baseline, run A/B tests, deploy best prompt"""
        
        # This is how the optimization tool should work with our slug generator
        from llm_optimizer.core.optimizer import LLMOptimizer
        from llm_optimizer.utils.prompt_loader import PromptLoader
        from llm_optimizer.utils.results_reporter import ResultsReporter
        
        # Step 1: Define test scenarios specific to slug generation
        test_scenarios = [
            {
                "title": "英國必買童裝 JoJo Maman Bébé官網 3 折起入手網購教學",
                "expected_themes": ["uk", "baby", "clothes", "shopping", "guide"],
                "category": "brand-product-association"
            },
            {
                "title": "Kindle電子書閱讀器最強攻略：Paper White、Colorsoft等型號分別、價格比較及網購集運教學",
                "expected_themes": ["kindle", "ereader", "comparison", "guide"],
                "category": "product-recognition"
            }
        ]
        
        # Step 2: Define the test function that evaluates a slug generator with a specific prompt
        def evaluate_slug_generator(prompt_version, test_cases):
            """Function that tests slug generator performance with a specific prompt"""
            from slug_generator import SlugGenerator
            
            # Create generator with specific prompt version
            generator = SlugGenerator(api_key="test-key")
            
            # Override prompt loading to use specified version
            def load_specific_prompt(prompt_name):
                return PromptLoader.load_prompt(f"slug_generation_{prompt_version}.txt")
            
            generator._load_prompt = load_specific_prompt
            
            # Run tests and collect metrics
            results = []
            for test_case in test_cases:
                # This would be mocked in actual test
                result = generator.generate_slug_from_content(
                    test_case['title'], 
                    f"Blog content about {test_case['category']}"
                )
                
                # Calculate theme coverage
                expected = set(test_case['expected_themes'])
                slug_text = result['primary'].lower()
                matched = set(theme for theme in expected if theme in slug_text)
                coverage = len(matched) / len(expected)
                
                results.append({
                    'coverage': coverage,
                    'success': True,
                    'duration': 5.0  # Mocked
                })
            
            # Return aggregated metrics
            return {
                'avg_theme_coverage': sum(r['coverage'] for r in results) / len(results),
                'success_rate': sum(1 for r in results if r['success']) / len(results),
                'avg_duration': sum(r['duration'] for r in results) / len(results),
                'individual_results': results
            }
        
        # Step 3: Configure the optimizer
        optimizer = LLMOptimizer({
            'test_function': evaluate_slug_generator,
            'metrics': ['avg_theme_coverage', 'success_rate', 'avg_duration'],
            'primary_metric': 'avg_theme_coverage'
        })
        
        # Step 4: Run comparison across prompt versions
        prompt_versions = ['v1', 'v2', 'v3']
        results = optimizer.run_comparison(prompt_versions, test_scenarios)
        
        # Step 5: Analyze results and get recommendations
        best_version = optimizer.get_best_version()
        improvement = optimizer.calculate_improvement('v1', best_version, 'avg_theme_coverage')
        
        # Step 6: Generate comprehensive report
        reporter = ResultsReporter()
        report = reporter.generate_comparison_report(results, best_version, improvement)
        
        # Assertions for integration test
        assert len(results) == 3  # Results for all versions
        assert best_version in prompt_versions
        assert improvement >= 0  # Should show improvement or no regression
        assert 'recommendations' in report
        assert 'best_version' in report
        
        # The test should fail initially since modules don't exist
        with pytest.raises((ImportError, ModuleNotFoundError)):
            # This will fail until we implement the tool
            pass
    
    def test_optimization_config_for_slug_generator(self):
        """Test configuration specific to slug generator optimization"""
        
        from llm_optimizer.config.optimization_config import SlugGeneratorConfig
        
        # Configuration should be tailored for slug generation
        config = SlugGeneratorConfig()
        
        # Should have slug-specific test scenarios
        assert len(config.test_scenarios) > 0
        assert 'brand-product-association' in [s['category'] for s in config.test_scenarios]
        assert 'product-recognition' in [s['category'] for s in config.test_scenarios]
        
        # Should have slug-specific metrics
        assert 'theme_coverage' in config.metrics
        assert 'seo_compliance' in config.metrics
        assert 'slug_length' in config.metrics
        
        # Should have prompt directory configured
        assert config.prompt_directory == 'config/prompts/'
        assert config.prompt_pattern == 'slug_generation_{version}.txt'
        
        # This will fail initially
        with pytest.raises((ImportError, ModuleNotFoundError)):
            pass
    
    def test_cli_usage_for_slug_optimization(self):
        """Test CLI interface for slug generator optimization"""
        
        from llm_optimizer.cli.optimizer_cli import OptimizationCLI
        
        # Should be able to run optimization from command line
        # Example: python -m llm_optimizer optimize --config slug_generator --versions v1,v2,v3
        
        cli_args = Mock()
        cli_args.config = 'slug_generator'
        cli_args.versions = ['v1', 'v2', 'v3']
        cli_args.output_dir = 'results/'
        cli_args.primary_metric = 'theme_coverage'
        
        cli = OptimizationCLI(cli_args)
        
        # Should load slug generator configuration
        assert cli.config.name == 'slug_generator'
        
        # Should be able to run optimization
        results = cli.run_optimization()
        
        assert 'comparison_results' in results
        assert 'best_version' in results
        assert 'recommendations' in results
        
        # This will fail initially
        with pytest.raises((ImportError, ModuleNotFoundError)):
            pass

    def test_automated_deployment_workflow(self):
        """Test automated deployment of best prompt to production"""
        
        from llm_optimizer.core.optimizer import LLMOptimizer
        from llm_optimizer.utils.deployment import PromptDeployer
        
        # After optimization, should be able to automatically deploy best prompt
        optimizer_results = {
            'v1': {'avg_theme_coverage': 0.586, 'success_rate': 1.0},
            'v2': {'avg_theme_coverage': 0.729, 'success_rate': 1.0},  # Best
            'v3': {'avg_theme_coverage': 0.607, 'success_rate': 0.86}
        }
        
        deployer = PromptDeployer('config/prompts/')
        
        # Should identify best version
        best_version = 'v2'
        
        # Should be able to deploy automatically
        deployment_result = deployer.deploy_prompt(
            best_version, 
            target_file='slug_generation.txt',  # Production prompt file
            backup=True
        )
        
        assert deployment_result['success'] == True
        assert deployment_result['backup_created'] == True
        assert deployment_result['deployed_version'] == 'v2'
        
        # Should update slug generator to use new prompt
        from slug_generator import SlugGenerator
        generator = SlugGenerator(api_key="test")
        
        # Should now load the optimized prompt by default
        prompt_content = generator._load_prompt('slug_generation')
        assert 'Few-shot examples' in prompt_content  # V2 characteristic
        
        # This will fail initially
        with pytest.raises((ImportError, ModuleNotFoundError)):
            pass

    def test_continuous_optimization_monitoring(self):
        """Test continuous monitoring and optimization capabilities"""
        
        from llm_optimizer.monitoring.performance_tracker import PerformanceTracker
        
        # Should be able to monitor performance over time
        tracker = PerformanceTracker('results/')
        
        # Should track metrics from production usage
        production_metrics = {
            'daily_avg_coverage': 0.72,
            'daily_success_rate': 0.98,
            'daily_avg_duration': 4.5,
            'sample_count': 150
        }
        
        tracker.record_daily_metrics(production_metrics)
        
        # Should detect performance degradation
        degradation = tracker.detect_performance_degradation(
            baseline_coverage=0.729,
            threshold=0.05  # 5% degradation threshold
        )
        
        if degradation['detected']:
            # Should trigger re-optimization
            re_optimization_needed = True
            assert degradation['recommended_action'] == 'retrain_prompts'
        
        # This will fail initially
        with pytest.raises((ImportError, ModuleNotFoundError)):
            pass


if __name__ == "__main__":
    # Run the integration tests to see them fail initially
    pytest.main([__file__, "-v"])