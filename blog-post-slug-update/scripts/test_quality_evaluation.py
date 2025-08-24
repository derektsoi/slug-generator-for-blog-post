#!/usr/bin/env python3
"""
Test Quality Evaluation - Quick validation of evaluation system
"""

import os
import sys
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from evaluation.core.seo_evaluator import SEOEvaluator


def test_evaluation():
    """Test evaluation on a few sample slugs"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not set")
        return
    
    print("🧪 TESTING QUALITY EVALUATION SYSTEM")
    print("=" * 50)
    
    # Initialize evaluator
    evaluator = SEOEvaluator(
        api_key=api_key,
        evaluation_prompt_version='v2_cultural_focused'
    )
    
    print("✅ Evaluator initialized with v2_cultural_focused")
    print()
    
    # Test cases from A/B results
    test_cases = [
        {
            'title': '【2025年最新】日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！',
            'content': '日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！完整購買教學與評價比較',
            'slugs': {
                'v8': 'skinnydip-iface-rhinoshield-phone-cases-guide',
                'v10': 'ultimate-skinnydip-iface-rhinoshield-phone-cases-guide'
            }
        },
        {
            'title': '一番賞Online購買教學，地雷系量產型手把手指南',
            'content': '一番賞Online購買教學，地雷系量產型服飾購物完整指南，包含jirai-kei風格搭配',
            'slugs': {
                'v8': 'ichiban-kuji-jirai-kei-fashion-online-guide',
                'v10': 'ultimate-ichiban-kuji-jirai-kei-fashion-guide'
            }
        }
    ]
    
    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        print(f"📝 Test Case {i}: {test_case['title'][:50]}...")
        
        for version, slug in test_case['slugs'].items():
            print(f"  🔄 {version}: {slug}")
            
            try:
                result = evaluator.evaluate_slug(
                    slug=slug,
                    title=test_case['title'],
                    content=test_case['content']
                )
                
                overall = result.get('overall_score', 0)
                cultural = result.get('dimension_scores', {}).get('cultural_authenticity', 0)
                competitive = result.get('dimension_scores', {}).get('competitive_differentiation', 0)
                
                print(f"     → Overall: {overall:.3f}, Cultural: {cultural:.3f}, Competitive: {competitive:.3f}")
                
            except Exception as e:
                print(f"     → ERROR: {e}")
        
        print()
    
    print("✅ Test evaluation complete!")


if __name__ == "__main__":
    test_evaluation()