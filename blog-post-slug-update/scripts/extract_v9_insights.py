#!/usr/bin/env python3
"""
Extract V9 Development Insights from Baseline Evaluation

Analyzes the LLM evaluation results to identify specific areas for V9 improvement.
"""

import json
import sys
from typing import Dict, List, Any


def analyze_baseline_results(results_file: str) -> Dict[str, Any]:
    """Analyze baseline evaluation results and extract V9 development insights"""
    
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    print("🔍 V9 Development Insights Analysis")
    print("=" * 50)
    
    # Extract LLM qualitative insights
    llm_insights = extract_llm_insights(results)
    print_llm_insights(llm_insights)
    
    # Analyze performance gaps
    performance_gaps = analyze_performance_gaps(results)
    print_performance_gaps(performance_gaps)
    
    # Generate V9 improvement strategy
    v9_strategy = generate_v9_strategy(llm_insights, performance_gaps)
    print_v9_strategy(v9_strategy)
    
    return {
        'llm_insights': llm_insights,
        'performance_gaps': performance_gaps,
        'v9_strategy': v9_strategy
    }


def extract_llm_insights(results: Dict) -> Dict[str, Any]:
    """Extract genuine LLM qualitative insights from evaluation results"""
    
    insights = {
        'successful_evaluations': [],
        'identified_weaknesses': [],
        'strength_patterns': [],
        'improvement_themes': []
    }
    
    for version, version_data in results['prompt_evaluations'].items():
        for case_name, case_result in version_data['test_case_results'].items():
            
            if case_result['success'] and 'key_insights' in case_result:
                case_insights = case_result['key_insights']
                
                evaluation = {
                    'version': version,
                    'case': case_name,
                    'slug': case_result['generated_slug'],
                    'overall_score': case_insights['overall_score'],
                    'strengths': case_insights.get('strengths', []),
                    'improvements': case_insights.get('improvements', []),
                    'cultural_insights': case_insights.get('cultural_insights', ''),
                    'competitive_analysis': case_insights.get('competitive_analysis', '')
                }
                
                insights['successful_evaluations'].append(evaluation)
                
                # Collect weaknesses and themes
                for improvement in case_insights.get('improvements', []):
                    insights['identified_weaknesses'].append({
                        'weakness': improvement,
                        'context': f"{version}:{case_name}",
                        'current_score': case_insights['overall_score']
                    })
                
                for strength in case_insights.get('strengths', []):
                    insights['strength_patterns'].append({
                        'strength': strength,
                        'context': f"{version}:{case_name}",
                        'score': case_insights['overall_score']
                    })
    
    # Analyze themes
    weakness_themes = {}
    for weakness in insights['identified_weaknesses']:
        theme = categorize_weakness(weakness['weakness'])
        if theme not in weakness_themes:
            weakness_themes[theme] = []
        weakness_themes[theme].append(weakness)
    
    insights['improvement_themes'] = weakness_themes
    
    return insights


def categorize_weakness(weakness_text: str) -> str:
    """Categorize weakness into themes for V9 development"""
    
    weakness_lower = weakness_text.lower()
    
    if any(term in weakness_lower for term in ['clarity', 'concise', 'length', 'verbose']):
        return 'clarity_and_conciseness'
    elif any(term in weakness_lower for term in ['appeal', 'click', 'engagement', 'attractive']):
        return 'click_through_optimization'
    elif any(term in weakness_lower for term in ['brand', 'prominence', 'hierarchy']):
        return 'brand_optimization'
    elif any(term in weakness_lower for term in ['cultural', 'authentic', 'preservation']):
        return 'cultural_enhancement'
    elif any(term in weakness_lower for term in ['compete', 'differentiat', 'unique']):
        return 'competitive_differentiation'
    elif any(term in weakness_lower for term in ['intent', 'user', 'search', 'match']):
        return 'user_intent_alignment'
    else:
        return 'other'


def analyze_performance_gaps(results: Dict) -> Dict[str, Any]:
    """Analyze performance gaps between V8 and V6"""
    
    gaps = {
        'v8_vs_v6': {},
        'dimension_analysis': {},
        'failure_patterns': []
    }
    
    v8_data = results['prompt_evaluations'].get('v8', {})
    v6_data = results['prompt_evaluations'].get('v6', {})
    
    if v8_data and v6_data:
        v8_perf = v8_data['overall_performance']
        v6_perf = v6_data['overall_performance']
        
        gaps['v8_vs_v6'] = {
            'success_rate_gap': v8_perf['success_rate'] - v6_perf['success_rate'],
            'score_gap': v8_perf['average_score'] - v6_perf['average_score'],
            'v8_successful_cases': v8_perf['successful_cases'],
            'v6_successful_cases': v6_perf['successful_cases']
        }
    
    # Analyze dimensional performance
    for version, version_data in results['prompt_evaluations'].items():
        for case_name, case_result in version_data['test_case_results'].items():
            if case_result['success'] and 'evaluation' in case_result:
                eval_data = case_result['evaluation']
                
                if 'qualitative_insights' in eval_data:
                    qual_scores = eval_data['qualitative_insights']['dimension_scores']
                    
                    for dimension, score in qual_scores.items():
                        if dimension not in gaps['dimension_analysis']:
                            gaps['dimension_analysis'][dimension] = []
                        
                        gaps['dimension_analysis'][dimension].append({
                            'version': version,
                            'case': case_name,
                            'score': score
                        })
    
    return gaps


def generate_v9_strategy(llm_insights: Dict, performance_gaps: Dict) -> Dict[str, Any]:
    """Generate specific V9 development strategy based on insights"""
    
    strategy = {
        'priority_improvements': [],
        'specific_changes': [],
        'expected_benefits': [],
        'implementation_approach': [],
        'validation_criteria': []
    }
    
    # Analyze improvement themes
    improvement_themes = llm_insights['improvement_themes']
    
    # Priority 1: Most frequent improvement themes
    theme_frequency = {theme: len(weaknesses) for theme, weaknesses in improvement_themes.items()}
    top_themes = sorted(theme_frequency.items(), key=lambda x: x[1], reverse=True)[:3]
    
    for theme, count in top_themes:
        strategy['priority_improvements'].append({
            'theme': theme,
            'frequency': count,
            'examples': [w['weakness'] for w in improvement_themes[theme][:2]]
        })
    
    # Generate specific changes based on top themes
    for theme, _ in top_themes:
        if theme == 'clarity_and_conciseness':
            strategy['specific_changes'].extend([
                'Enhance prompt instructions for conciseness',
                'Add explicit guidance on avoiding redundancy',
                'Emphasize clear, direct language'
            ])
        elif theme == 'click_through_optimization':
            strategy['specific_changes'].extend([
                'Add user psychology considerations',
                'Include click-through appeal guidelines',
                'Enhance emotional engagement factors'
            ])
        elif theme == 'brand_optimization':
            strategy['specific_changes'].extend([
                'Strengthen brand hierarchy rules',
                'Improve multi-brand handling instructions',
                'Add brand prominence guidelines'
            ])
        elif theme == 'cultural_enhancement':
            strategy['specific_changes'].extend([
                'Expand cultural awareness instructions',
                'Add more cultural term examples',
                'Enhance cross-cultural sensitivity'
            ])
    
    # Expected benefits
    strategy['expected_benefits'] = [
        'Improved clarity and user engagement',
        'Better brand recognition and hierarchy',
        'Enhanced cultural authenticity',
        'Higher click-through potential',
        'Better competitive differentiation'
    ]
    
    # Implementation approach
    strategy['implementation_approach'] = [
        'Iterative prompt refinement based on LLM feedback',
        'Test each improvement individually before combining',
        'Validate against V8 breakthrough cases',
        'Ensure V6 cultural preservation is maintained',
        'Use real LLM evaluation throughout development'
    ]
    
    # Validation criteria
    strategy['validation_criteria'] = [
        'Maintains V8 breakthrough capabilities',
        'Improves on identified weakness areas',
        'Shows measurable improvement in LLM evaluation scores',
        'Preserves cultural awareness from V6',
        'Demonstrates novel capabilities beyond V8'
    ]
    
    return strategy


def print_llm_insights(insights: Dict):
    """Print LLM insights analysis"""
    
    print(f"\n🧠 LLM Qualitative Insights Analysis:")
    print(f"   Successful Evaluations: {len(insights['successful_evaluations'])}")
    print(f"   Identified Weaknesses: {len(insights['identified_weaknesses'])}")
    print(f"   Strength Patterns: {len(insights['strength_patterns'])}")
    
    print(f"\n🎯 Top Improvement Themes:")
    for theme, weaknesses in insights['improvement_themes'].items():
        if weaknesses:  # Only show themes with actual examples
            print(f"   {theme}: {len(weaknesses)} instances")
            for weakness in weaknesses[:2]:  # Show top 2 examples
                print(f"     • {weakness['weakness']} ({weakness['context']})")
    
    print(f"\n💪 Common Strengths:")
    strength_counts = {}
    for strength in insights['strength_patterns']:
        text = strength['strength']
        strength_counts[text] = strength_counts.get(text, 0) + 1
    
    top_strengths = sorted(strength_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    for strength, count in top_strengths:
        print(f"   • {strength} (mentioned {count} times)")


def print_performance_gaps(gaps: Dict):
    """Print performance gap analysis"""
    
    print(f"\n📊 Performance Gap Analysis:")
    
    if 'v8_vs_v6' in gaps and gaps['v8_vs_v6']:
        v8_v6 = gaps['v8_vs_v6']
        print(f"   V8 vs V6 Success Rate: {v8_v6['success_rate_gap']:+.1%}")
        print(f"   V8 vs V6 Average Score: {v8_v6['score_gap']:+.3f}")
        print(f"   V8 Successful Cases: {v8_v6['v8_successful_cases']}")
        print(f"   V6 Successful Cases: {v8_v6['v6_successful_cases']}")
    
    print(f"\n📈 Dimensional Performance:")
    if gaps['dimension_analysis']:
        for dimension, scores in gaps['dimension_analysis'].items():
            if scores:
                avg_score = sum(s['score'] for s in scores) / len(scores)
                print(f"   {dimension}: {avg_score:.3f} average")


def print_v9_strategy(strategy: Dict):
    """Print V9 development strategy"""
    
    print(f"\n🚀 V9 Development Strategy:")
    
    print(f"\n   Priority Improvements:")
    for improvement in strategy['priority_improvements']:
        print(f"   • {improvement['theme']} ({improvement['frequency']} instances)")
        for example in improvement['examples']:
            print(f"     - {example}")
    
    print(f"\n   Specific Changes for V9:")
    for change in strategy['specific_changes'][:5]:  # Top 5
        print(f"   • {change}")
    
    print(f"\n   Expected Benefits:")
    for benefit in strategy['expected_benefits']:
        print(f"   • {benefit}")


def main():
    """Main execution"""
    
    if len(sys.argv) != 2:
        print("Usage: python extract_v9_insights.py <results_file>")
        return 1
    
    results_file = sys.argv[1]
    
    try:
        analysis = analyze_baseline_results(results_file)
        
        print(f"\n✅ V9 insights analysis complete!")
        print(f"   Ready to proceed with V9 prompt development.")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error analyzing results: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())