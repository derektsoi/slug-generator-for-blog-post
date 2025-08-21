#!/usr/bin/env python3
"""
Test V9 LLM-Guided Improvements

Tests V9 prompt against baseline cases to validate LLM-guided development approach.
"""

import os
import sys
import json
from typing import Dict, List, Any
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from evaluation.core.evaluation_coordinator import EvaluationCoordinator
from core.slug_generator import SlugGenerator


def test_v9_improvements(api_key: str) -> Dict[str, Any]:
    """Test V9 improvements against baseline cases"""
    
    print("🚀 Testing V9 LLM-Guided Improvements")
    print("=" * 50)
    
    # Initialize systems
    coordinator = EvaluationCoordinator(api_key=api_key, enable_llm=True)
    
    # Test cases from baseline evaluation
    test_cases = {
        'v8_breakthrough': {
            'title': '日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！',
            'expected_improvements': ['click_through_optimization', 'competitive_differentiation']
        },
        'v6_cultural': {
            'title': '【2025年最新】日本一番賞Online手把手教學！',
            'expected_improvements': ['click_through_optimization', 'brand_optimization']
        },
        'brand_compound': {
            'title': '大國藥妝香港開店定價無優勢！學識日本轉運平價入手化妝品、日用品等必買推介',
            'expected_improvements': ['brand_optimization', 'competitive_differentiation']
        }
    }
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'v9_performance': {},
        'v8_comparison': {},
        'improvement_validation': {},
        'llm_feedback_analysis': []
    }
    
    # Test V9 prompt
    print(f"\n📋 Testing V9 Prompt (LLM-Guided):")
    results['v9_performance'] = test_prompt_version('v9', test_cases, coordinator)
    
    # Test V8 for comparison
    print(f"\n📋 Testing V8 Prompt (Baseline):")
    results['v8_comparison'] = test_prompt_version('v8', test_cases, coordinator)
    
    # Analyze improvements
    print(f"\n🎯 Analyzing V9 Improvements:")
    results['improvement_validation'] = analyze_improvements(
        results['v9_performance'], 
        results['v8_comparison'],
        test_cases
    )
    
    # Generate LLM feedback analysis
    results['llm_feedback_analysis'] = analyze_llm_feedback(results)
    
    # Print summary
    print_improvement_summary(results)
    
    # Save results
    save_v9_results(results)
    
    return results


def test_prompt_version(version: str, test_cases: Dict, coordinator: EvaluationCoordinator) -> Dict[str, Any]:
    """Test specific prompt version on all cases"""
    
    version_results = {
        'version': version,
        'test_results': {},
        'performance_summary': {}
    }
    
    try:
        # Create slug generator for this version
        generator = SlugGenerator(prompt_version=version)
        
        for case_name, case_data in test_cases.items():
            print(f"  Testing {case_name}...")
            
            try:
                # Generate slug
                slug_result = generator.generate_slug_from_content(
                    case_data['title'],
                    case_data['title']
                )
                
                if slug_result and 'primary' in slug_result:
                    generated_slug = slug_result['primary']
                    
                    # Evaluate with LLM system
                    evaluation = coordinator.evaluate_comprehensive(
                        generated_slug,
                        case_data['title'],
                        case_data['title']
                    )
                    
                    case_result = {
                        'generated_slug': generated_slug,
                        'evaluation': evaluation,
                        'success': True
                    }
                    
                    # Extract key metrics
                    if evaluation['llm_available'] and evaluation['qualitative_insights']:
                        qual = evaluation['qualitative_insights']
                        case_result['key_metrics'] = {
                            'overall_score': qual['overall_score'],
                            'click_through_potential': qual['dimension_scores'].get('click_through_potential', 0),
                            'competitive_differentiation': qual['dimension_scores'].get('competitive_differentiation', 0),
                            'brand_hierarchy': qual['dimension_scores'].get('brand_hierarchy', 0),
                            'cultural_authenticity': qual['dimension_scores'].get('cultural_authenticity', 0)
                        }
                
                else:
                    case_result = {
                        'generated_slug': None,
                        'success': False,
                        'error': 'slug_generation_failed'
                    }
            
            except Exception as e:
                case_result = {
                    'generated_slug': None,
                    'success': False,
                    'error': str(e)
                }
            
            version_results['test_results'][case_name] = case_result
    
    except Exception as e:
        print(f"  ❌ Error testing {version}: {e}")
        version_results['error'] = str(e)
    
    # Calculate performance summary
    version_results['performance_summary'] = calculate_performance_summary(version_results['test_results'])
    
    return version_results


def analyze_improvements(v9_results: Dict, v8_results: Dict, test_cases: Dict) -> Dict[str, Any]:
    """Analyze V9 improvements compared to V8 baseline"""
    
    improvements = {
        'overall_comparison': {},
        'dimensional_improvements': {},
        'case_by_case_analysis': {},
        'improvement_validation': {}
    }
    
    # Overall performance comparison
    v9_perf = v9_results.get('performance_summary', {})
    v8_perf = v8_results.get('performance_summary', {})
    
    improvements['overall_comparison'] = {
        'success_rate_change': v9_perf.get('success_rate', 0) - v8_perf.get('success_rate', 0),
        'avg_score_change': v9_perf.get('avg_overall_score', 0) - v8_perf.get('avg_overall_score', 0),
        'v9_success_rate': v9_perf.get('success_rate', 0),
        'v8_success_rate': v8_perf.get('success_rate', 0)
    }
    
    # Dimensional improvements analysis
    dimensions = ['click_through_potential', 'competitive_differentiation', 'brand_hierarchy', 'cultural_authenticity']
    
    for dimension in dimensions:
        v9_scores = []
        v8_scores = []
        
        # Collect scores for this dimension
        for case_name in test_cases.keys():
            v9_case = v9_results.get('test_results', {}).get(case_name, {})
            v8_case = v8_results.get('test_results', {}).get(case_name, {})
            
            if v9_case.get('success') and 'key_metrics' in v9_case:
                v9_scores.append(v9_case['key_metrics'].get(dimension, 0))
            
            if v8_case.get('success') and 'key_metrics' in v8_case:
                v8_scores.append(v8_case['key_metrics'].get(dimension, 0))
        
        if v9_scores and v8_scores:
            v9_avg = sum(v9_scores) / len(v9_scores)
            v8_avg = sum(v8_scores) / len(v8_scores)
            
            improvements['dimensional_improvements'][dimension] = {
                'v9_average': v9_avg,
                'v8_average': v8_avg,
                'improvement': v9_avg - v8_avg,
                'improvement_percentage': ((v9_avg - v8_avg) / v8_avg * 100) if v8_avg > 0 else 0
            }
    
    # Case-by-case analysis
    for case_name, case_data in test_cases.items():
        v9_case = v9_results.get('test_results', {}).get(case_name, {})
        v8_case = v8_results.get('test_results', {}).get(case_name, {})
        
        case_analysis = {
            'v9_slug': v9_case.get('generated_slug'),
            'v8_slug': v8_case.get('generated_slug'),
            'expected_improvements': case_data.get('expected_improvements', []),
            'actual_improvements': []
        }
        
        # Check if expected improvements materialized
        if (v9_case.get('success') and v8_case.get('success') and 
            'key_metrics' in v9_case and 'key_metrics' in v8_case):
            
            v9_metrics = v9_case['key_metrics']
            v8_metrics = v8_case['key_metrics']
            
            for expected_improvement in case_data.get('expected_improvements', []):
                if expected_improvement == 'click_through_optimization':
                    dimension = 'click_through_potential'
                elif expected_improvement == 'competitive_differentiation':
                    dimension = 'competitive_differentiation'
                elif expected_improvement == 'brand_optimization':
                    dimension = 'brand_hierarchy'
                else:
                    dimension = expected_improvement
                
                v9_score = v9_metrics.get(dimension, 0)
                v8_score = v8_metrics.get(dimension, 0)
                
                if v9_score > v8_score:
                    case_analysis['actual_improvements'].append({
                        'area': expected_improvement,
                        'improvement': v9_score - v8_score,
                        'v9_score': v9_score,
                        'v8_score': v8_score
                    })
        
        improvements['case_by_case_analysis'][case_name] = case_analysis
    
    return improvements


def calculate_performance_summary(test_results: Dict) -> Dict[str, Any]:
    """Calculate performance summary for a set of test results"""
    
    successful_cases = [case for case in test_results.values() if case.get('success', False)]
    total_cases = len(test_results)
    
    success_rate = len(successful_cases) / total_cases if total_cases > 0 else 0
    
    # Calculate average scores
    overall_scores = []
    dimension_scores = {}
    
    for case in successful_cases:
        if 'key_metrics' in case:
            metrics = case['key_metrics']
            overall_scores.append(metrics.get('overall_score', 0))
            
            for dimension, score in metrics.items():
                if dimension != 'overall_score':
                    if dimension not in dimension_scores:
                        dimension_scores[dimension] = []
                    dimension_scores[dimension].append(score)
    
    avg_overall_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0
    
    avg_dimension_scores = {}
    for dimension, scores in dimension_scores.items():
        avg_dimension_scores[dimension] = sum(scores) / len(scores) if scores else 0
    
    return {
        'success_rate': success_rate,
        'successful_cases': len(successful_cases),
        'total_cases': total_cases,
        'avg_overall_score': avg_overall_score,
        'avg_dimension_scores': avg_dimension_scores
    }


def analyze_llm_feedback(results: Dict) -> List[str]:
    """Analyze LLM feedback to validate the guided development approach"""
    
    feedback_analysis = []
    
    # Check if LLM-guided improvements worked
    improvement_validation = results.get('improvement_validation', {})
    dimensional_improvements = improvement_validation.get('dimensional_improvements', {})
    
    # Analyze priority improvements from LLM insights
    priority_dimensions = ['click_through_potential', 'competitive_differentiation', 'brand_hierarchy']
    
    for dimension in priority_dimensions:
        if dimension in dimensional_improvements:
            improvement_data = dimensional_improvements[dimension]
            improvement = improvement_data.get('improvement', 0)
            improvement_pct = improvement_data.get('improvement_percentage', 0)
            
            if improvement > 0.1:  # Significant improvement
                feedback_analysis.append(
                    f"✅ LLM-guided improvement in {dimension}: +{improvement:.3f} ({improvement_pct:+.1f}%)"
                )
            elif improvement > 0:
                feedback_analysis.append(
                    f"⚠️ Minor improvement in {dimension}: +{improvement:.3f} ({improvement_pct:+.1f}%)"
                )
            else:
                feedback_analysis.append(
                    f"❌ No improvement in {dimension}: {improvement:+.3f} ({improvement_pct:+.1f}%)"
                )
    
    return feedback_analysis


def print_improvement_summary(results: Dict):
    """Print comprehensive improvement summary"""
    
    print(f"\n📊 V9 vs V8 Improvement Summary")
    print("=" * 40)
    
    overall = results.get('improvement_validation', {}).get('overall_comparison', {})
    print(f"Success Rate: {overall.get('v9_success_rate', 0):.1%} vs {overall.get('v8_success_rate', 0):.1%} (Δ{overall.get('success_rate_change', 0):+.1%})")
    print(f"Avg Score: {overall.get('v9_success_rate', 0):.3f} vs {overall.get('v8_success_rate', 0):.3f} (Δ{overall.get('avg_score_change', 0):+.3f})")
    
    print(f"\n🎯 Dimensional Improvements:")
    dimensional = results.get('improvement_validation', {}).get('dimensional_improvements', {})
    for dimension, data in dimensional.items():
        improvement = data.get('improvement', 0)
        improvement_pct = data.get('improvement_percentage', 0)
        print(f"{dimension}: {improvement:+.3f} ({improvement_pct:+.1f}%)")
    
    print(f"\n🔍 LLM Feedback Validation:")
    for feedback in results.get('llm_feedback_analysis', []):
        print(f"  {feedback}")


def save_v9_results(results: Dict):
    """Save V9 test results"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"v9_improvement_test_{timestamp}.json"
    filepath = os.path.join('results', filename)
    
    os.makedirs('results', exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 V9 test results saved to: {filepath}")


def main():
    """Main execution"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv('OPENAI_API_KEY')
        except ImportError:
            pass
    
    if not api_key or api_key == "test-key":
        print("❌ Valid OPENAI_API_KEY required for V9 testing")
        return 1
    
    try:
        results = test_v9_improvements(api_key)
        print(f"\n✅ V9 improvement testing complete!")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error testing V9 improvements: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())