#!/usr/bin/env python3
"""
Simple V4 vs Current Prompt Test

Direct comparison without complex optimization framework first.
"""

import sys
import os
import json
import time

sys.path.insert(0, 'src')

from slug_generator import SlugGenerator

def test_prompt_version(prompt_file, test_cases):
    """Test a specific prompt version"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    generator = SlugGenerator(api_key=api_key)
    generator.confidence_threshold = 0.3  # Lower threshold for reliability
    
    # Override prompt loading
    def load_custom_prompt(prompt_name):
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            # Ensure JSON format requirement
            if "JSON format" not in content:
                content += "\n\nRespond in JSON format with the structure shown above."
            return content
    
    generator._load_prompt = load_custom_prompt
    
    results = []
    successful = 0
    total_coverage = 0
    
    for i, case in enumerate(test_cases, 1):
        title = case['title']
        expected_themes = case['expected_themes']
        
        print(f"   {i}. Testing: {title[:50]}...")
        
        try:
            result = generator.generate_slug_from_content(
                title, 
                f"Blog content about {case.get('category', 'shopping')}", 
                count=2
            )
            
            # Calculate theme coverage
            expected = set(expected_themes)
            all_slugs = [result['primary']] + result.get('alternatives', [])
            slug_text = ' '.join(all_slugs).lower()
            
            matched = set()
            for theme in expected:
                if theme.lower() in slug_text:
                    matched.add(theme)
            
            coverage = len(matched) / len(expected) if expected else 1.0
            total_coverage += coverage
            successful += 1
            
            results.append({
                'primary': result['primary'],
                'coverage': coverage,
                'matched': list(matched),
                'success': True
            })
            
            print(f"      ✅ {result['primary']} ({coverage:.1%} themes)")
            
        except Exception as e:
            print(f"      ❌ Error: {str(e)[:50]}...")
            results.append({
                'error': str(e),
                'coverage': 0.0,
                'success': False
            })
    
    avg_coverage = total_coverage / len(test_cases) if test_cases else 0
    success_rate = successful / len(test_cases) if test_cases else 0
    
    return {
        'avg_coverage': avg_coverage,
        'success_rate': success_rate,
        'results': results
    }

def main():
    """Simple V4 vs Current test"""
    
    print("🚀 SIMPLE V4 PROMPT TEST")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "title": "英國必買童裝 JoJo Maman Bébé官網購買教學",
            "expected_themes": ["uk", "baby", "clothes", "shopping", "guide"],
            "category": "brand-product"
        },
        {
            "title": "Kindle電子書閱讀器攻略：型號比較及購買教學",
            "expected_themes": ["kindle", "ereader", "comparison", "guide"],
            "category": "product-guide"
        },
        {
            "title": "開學季必買清單！鞋子背囊及文具產品",
            "expected_themes": ["school", "season", "shoes", "bags"],
            "category": "seasonal"
        }
    ]
    
    print(f"Testing {len(test_cases)} cases:")
    for i, case in enumerate(test_cases, 1):
        print(f"   {i}. {case['category']}: {len(case['expected_themes'])} themes")
    print()
    
    # Test current prompt (V2 production)
    print("🧪 Testing Current Production Prompt")
    current_results = test_prompt_version('config/prompts/slug_generation_v2.txt', test_cases)
    
    print(f"📊 Current: {current_results['avg_coverage']:.1%} coverage, {current_results['success_rate']:.0%} success")
    print()
    
    # Test V4 prompt
    print("🧪 Testing V4 Optimized Prompt")
    v4_results = test_prompt_version('config/prompts/slug_generation_v4.txt', test_cases)
    
    print(f"📊 V4: {v4_results['avg_coverage']:.1%} coverage, {v4_results['success_rate']:.0%} success")
    print()
    
    # Compare results
    print("📈 COMPARISON RESULTS")
    print("=" * 30)
    
    if v4_results['avg_coverage'] > current_results['avg_coverage']:
        improvement = (v4_results['avg_coverage'] - current_results['avg_coverage']) * 100
        print(f"✅ V4 WINS: +{improvement:.1f}% improvement in theme coverage")
    elif current_results['avg_coverage'] > v4_results['avg_coverage']:
        decline = (current_results['avg_coverage'] - v4_results['avg_coverage']) * 100
        print(f"📝 Current wins: V4 needs work (-{decline:.1f}% coverage)")
    else:
        print("🤝 Tie: Both versions perform equally")
    
    # Show example outputs
    print("\n🎯 Example Outputs:")
    for i, case in enumerate(test_cases):
        print(f"   {i+1}. {case['title'][:40]}...")
        
        current_result = current_results['results'][i]
        v4_result = v4_results['results'][i]
        
        if current_result['success']:
            print(f"      Current: {current_result['primary']} ({current_result['coverage']:.1%})")
        else:
            print(f"      Current: ❌ Failed")
            
        if v4_result['success']:
            print(f"      V4:      {v4_result['primary']} ({v4_result['coverage']:.1%})")
        else:
            print(f"      V4:      ❌ Failed")
        print()

if __name__ == "__main__":
    main()