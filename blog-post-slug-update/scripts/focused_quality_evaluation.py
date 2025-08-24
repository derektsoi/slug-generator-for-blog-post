#!/usr/bin/env python3
"""
Focused Quality Evaluation - Sample evaluation to fill critical gap
"""

import os
import sys
import json
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from evaluation.core.seo_evaluator import SEOEvaluator


def run_focused_evaluation():
    """Run focused evaluation on key test cases"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not set")
        return
    
    print("🎯 FOCUSED QUALITY EVALUATION")
    print("=" * 60)
    print("📊 Scoring representative slugs with v2_cultural_focused")
    print("🌏 Priority: Cultural authenticity + brand hierarchy")
    print("=" * 60)
    
    # Load A/B test results
    with open("focused_ab_test_20250824_174412.json", 'r', encoding='utf-8') as f:
        ab_results = json.load(f)
    
    # Initialize evaluator
    evaluator = SEOEvaluator(
        api_key=api_key,
        evaluation_prompt_version='v2_cultural_focused'
    )
    
    print("✅ Using v2_cultural_focused evaluation prompt")
    print()
    
    # Focus on key cases that represent different challenges
    key_cases = [
        0,  # Multi-brand complex
        1,  # Cultural subculture  
        4,  # Cultural complex brands
        6,  # Fashion subculture
        8   # Anime collectibles cultural
    ]
    
    versions = ['v8', 'v10', 'v11a', 'v11b']
    version_results = {v: [] for v in versions}
    
    for case_idx in key_cases:
        case_result = ab_results['detailed_results'][case_idx]
        case_info = case_result['case_info']
        generations = case_result['generations']
        
        print(f"📝 Case {case_idx + 1}: {case_info['category']}")
        print(f"    Title: {case_info['title'][:60]}...")
        
        case_scores = {}
        
        # Evaluate each version
        for version in versions:
            slug = generations.get(version)
            
            if slug is None:
                print(f"    ❌ {version}: Failed generation")
                continue
                
            print(f"    🔄 {version}: {slug[:50]}..." + ("" if len(slug) <= 50 else ""))
            
            try:
                result = evaluator.evaluate_slug(
                    slug=slug,
                    title=case_info['title'],
                    content=case_info['content']
                )
                
                scores = result.get('dimension_scores', {})
                overall = result.get('overall_score', 0)
                
                case_scores[version] = {
                    'overall_score': overall,
                    'cultural_authenticity': scores.get('cultural_authenticity', 0),
                    'brand_hierarchy': scores.get('brand_hierarchy', 0),
                    'competitive_differentiation': scores.get('competitive_differentiation', 0),
                    'click_through_potential': scores.get('click_through_potential', 0),
                    'user_intent_match': scores.get('user_intent_match', 0),
                    'technical_seo': scores.get('technical_seo', 0)
                }
                
                version_results[version].append(case_scores[version])
                
                print(f"         Overall: {overall:.3f} | Cultural: {scores.get('cultural_authenticity', 0):.3f} | "
                      f"Brand: {scores.get('brand_hierarchy', 0):.3f} | Competitive: {scores.get('competitive_differentiation', 0):.3f}")
                
            except Exception as e:
                print(f"         ❌ Evaluation error: {e}")
        
        print()
    
    # Calculate summary statistics
    print("📊 QUALITY ANALYSIS SUMMARY")
    print("=" * 50)
    
    summary_stats = {}
    
    for version in versions:
        results = version_results[version]
        if not results:
            print(f"{version:4s}: No successful evaluations")
            continue
            
        # Calculate averages
        avg_overall = sum(r['overall_score'] for r in results) / len(results)
        avg_cultural = sum(r['cultural_authenticity'] for r in results) / len(results)
        avg_brand = sum(r['brand_hierarchy'] for r in results) / len(results)
        avg_competitive = sum(r['competitive_differentiation'] for r in results) / len(results)
        avg_click = sum(r['click_through_potential'] for r in results) / len(results)
        
        summary_stats[version] = {
            'count': len(results),
            'avg_overall': avg_overall,
            'avg_cultural_authenticity': avg_cultural,
            'avg_brand_hierarchy': avg_brand,
            'avg_competitive_differentiation': avg_competitive,
            'avg_click_through_potential': avg_click
        }
        
        print(f"{version:4s}: {avg_overall:.3f} overall | {avg_cultural:.3f} cultural | {avg_brand:.3f} brand | {avg_competitive:.3f} competitive")
    
    # Key insights
    print(f"\n🔍 KEY QUALITY INSIGHTS")
    print("=" * 40)
    
    # Find best performers
    if summary_stats:
        best_overall = max(summary_stats.items(), key=lambda x: x[1]['avg_overall'])
        best_cultural = max(summary_stats.items(), key=lambda x: x[1]['avg_cultural_authenticity'])
        best_competitive = max(summary_stats.items(), key=lambda x: x[1]['avg_competitive_differentiation'])
        
        print(f"🏆 Best Overall Quality: {best_overall[0]} ({best_overall[1]['avg_overall']:.3f})")
        print(f"🌏 Best Cultural Auth: {best_cultural[0]} ({best_cultural[1]['avg_cultural_authenticity']:.3f})")  
        print(f"⚡ Best Competitive: {best_competitive[0]} ({best_competitive[1]['avg_competitive_differentiation']:.3f})")
        
        # V10 analysis
        if 'v10' in summary_stats:
            v10_stats = summary_stats['v10']
            print(f"\n⚠️  V10 Pattern Crisis Analysis:")
            print(f"    Overall Score: {v10_stats['avg_overall']:.3f}")
            print(f"    Competitive Score: {v10_stats['avg_competitive_differentiation']:.3f}")
            print(f"    Cultural Score: {v10_stats['avg_cultural_authenticity']:.3f}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"focused_quality_evaluation_{timestamp}.json"
    
    results_data = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'evaluation_prompt': 'v2_cultural_focused',
            'focus': 'cultural_authenticity_priority',
            'cases_evaluated': len(key_cases)
        },
        'summary_statistics': summary_stats,
        'detailed_results': version_results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Focused evaluation complete!")
    print(f"📁 Results saved: {output_file}")
    
    return results_data


if __name__ == "__main__":
    try:
        results = run_focused_evaluation()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)