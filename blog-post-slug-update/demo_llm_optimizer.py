#!/usr/bin/env python3
"""
Demonstration of LLM Optimization Tool

Shows how to use the LLM optimization tool to systematically improve
prompt performance using our slug generator as an example.
"""

import sys
import os
import json
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, 'src')

from llm_optimizer.core.optimizer import LLMOptimizer
from llm_optimizer.core.metrics_calculator import MetricsCalculator
from llm_optimizer.core.comparator import Comparator


def create_mock_slug_test_function():
    """
    Create a mock test function that simulates testing different prompt versions.
    
    In real usage, this would integrate with your actual LLM application.
    """
    def test_slug_generator(prompt_version, test_cases):
        """Mock function that simulates slug generation with different prompts"""
        
        # Mock results that simulate different prompt performance
        mock_results = {
            'v1': {
                # Baseline performance (like our original prompt)
                'avg_theme_coverage': 0.586,
                'success_rate': 1.0,
                'avg_duration': 5.2,
                'individual_results': [
                    {'theme_coverage': 0.6, 'success': True, 'duration': 5.1},
                    {'theme_coverage': 0.5, 'success': True, 'duration': 5.3},
                    {'theme_coverage': 0.65, 'success': True, 'duration': 5.2}
                ]
            },
            'v2': {
                # Improved performance (like our optimized V2 prompt)
                'avg_theme_coverage': 0.729,
                'success_rate': 1.0,
                'avg_duration': 4.8,
                'individual_results': [
                    {'theme_coverage': 0.75, 'success': True, 'duration': 4.9},
                    {'theme_coverage': 0.7, 'success': True, 'duration': 4.7},
                    {'theme_coverage': 0.73, 'success': True, 'duration': 4.8}
                ]
            },
            'v3': {
                # Over-engineered version (like our V3 attempt)
                'avg_theme_coverage': 0.607,
                'success_rate': 0.86,  # Less reliable
                'avg_duration': 6.1,   # Slower
                'individual_results': [
                    {'theme_coverage': 0.9, 'success': True, 'duration': 5.8},
                    {'theme_coverage': 0.0, 'success': False, 'duration': 0.0, 'error': 'JSON parsing error'},
                    {'theme_coverage': 0.65, 'success': True, 'duration': 6.4}
                ]
            }
        }
        
        return mock_results.get(prompt_version, {
            'avg_theme_coverage': 0.0,
            'success_rate': 0.0,
            'avg_duration': 0.0,
            'error': f'Unknown prompt version: {prompt_version}'
        })
    
    return test_slug_generator


def main():
    """Demonstrate the LLM optimization tool"""
    
    print("🔬 LLM OPTIMIZATION TOOL DEMONSTRATION")
    print("=" * 80)
    print("Simulating systematic prompt optimization for blog slug generation")
    print()
    
    # Step 1: Define test scenarios
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
        },
        {
            "title": "開學季代購必買清單！IFME返學鞋、Gregory背囊及電子文具產品低至3折",
            "expected_themes": ["school", "season", "shoes", "bags"],
            "category": "seasonal-content"
        }
    ]
    
    print(f"📊 Test Scenarios: {len(test_scenarios)} diverse content types")
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"   {i}. {scenario['category']}: {len(scenario['expected_themes'])} themes")
    print()
    
    # Step 2: Configure optimizer
    config = {
        'test_function': create_mock_slug_test_function(),
        'metrics': ['avg_theme_coverage', 'success_rate', 'avg_duration'],
        'primary_metric': 'avg_theme_coverage',
        'confidence_threshold': 0.8
    }
    
    optimizer = LLMOptimizer(config)
    
    # Step 3: Run A/B testing across prompt versions
    print("🧪 Running A/B Testing Across Prompt Versions")
    print("-" * 50)
    
    prompt_versions = ['v1', 'v2', 'v3']
    results = optimizer.run_comparison(prompt_versions, test_scenarios)
    
    # Step 4: Analyze results and get best version
    print("\n📊 OPTIMIZATION RESULTS")
    print("=" * 50)
    
    best_version = optimizer.get_best_version()
    ranking = optimizer.get_ranking()
    
    print(f"🏆 Best Version: {best_version}")
    print(f"📈 Performance Ranking: {' > '.join(ranking)}")
    print()
    
    # Show detailed metrics
    for version in ranking:
        if version in results and 'error' not in results[version]:
            metrics = results[version]
            print(f"   {version}: {metrics['avg_theme_coverage']:.1%} coverage, "
                  f"{metrics['success_rate']:.0%} success, {metrics['avg_duration']:.1f}s avg")
        else:
            print(f"   {version}: ❌ Failed")
    print()
    
    # Step 5: Calculate improvement
    if len(ranking) >= 2:
        baseline_version = ranking[-1]  # Worst performer
        improvement = optimizer.calculate_improvement(baseline_version, best_version, 'avg_theme_coverage')
        improvement_percent = improvement * 100
        
        print(f"📈 Improvement: +{improvement_percent:.1f}% over {baseline_version}")
        print()
    
    # Step 6: Generate insights and recommendations
    insights = optimizer.generate_insights()
    
    print("💡 OPTIMIZATION INSIGHTS")
    print("=" * 50)
    
    print("📋 Recommendations:")
    for i, rec in enumerate(insights['recommendations'], 1):
        print(f"   {i}. {rec}")
    print()
    
    print("🎯 Deployment Recommendation:")
    deployment = insights['deployment_recommendation']
    print(f"   • Recommended Version: {deployment['recommended_version']}")
    print(f"   • Confidence Level: {deployment['confidence_level']}")
    print()
    
    print("📝 Next Steps:")
    for i, step in enumerate(deployment['next_steps'], 1):
        print(f"   {i}. {step}")
    print()
    
    # Step 7: Export results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"results/llm_optimization_demo_{timestamp}.json"
    
    os.makedirs('results', exist_ok=True)
    optimizer.export_results(results_file)
    
    print("✅ OPTIMIZATION COMPLETE")
    print("=" * 50)
    print(f"This demonstrates how the LLM optimization tool systematically")
    print(f"identifies the best performing prompt version through data-driven")
    print(f"A/B testing, just like we did manually for the slug generator.")
    print()
    print(f"The tool can be integrated with any LLM application to provide")
    print(f"automated prompt optimization with statistical analysis.")


if __name__ == "__main__":
    main()