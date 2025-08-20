#!/usr/bin/env python3
"""
Quick test of v3 prompt to see if it improves theme coverage
"""

import sys
import os
import json
import time

# Add src directory to Python path
sys.path.insert(0, 'src')

from slug_generator import SlugGenerator

def test_v3_prompt():
    """Test the new v3 prompt on key samples"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OPENAI_API_KEY found")
        return
    
    # Critical test cases that missed themes before
    test_cases = [
        {
            "title": "英國必買童裝 JoJo Maman Bébé官網 3 折起入手網購教學",
            "expected_themes": ["uk", "baby", "clothes", "shopping", "guide"],
            "focus": "Should include ALL: uk + baby + clothes + shopping + guide"
        },
        {
            "title": "Kindle電子書閱讀器最強攻略：Paper White、Colorsoft等型號分別、價格比較及網購集運教學",
            "expected_themes": ["kindle", "ereader", "comparison", "guide"],
            "focus": "Should include: kindle + ereader + comparison + guide"
        },
        {
            "title": "開學季代購必買清單！IFME返學鞋、Gregory背囊及電子文具產品低至3折",
            "expected_themes": ["school", "season", "shoes", "bags"],
            "focus": "Should include: school + season + shoes + bags"
        }
    ]
    
    # Create generator with v3 prompt
    generator = SlugGenerator(api_key=api_key)
    
    # Override prompt loading for v3
    def load_v3_prompt(prompt_name):
        with open("config/prompts/slug_generation_v3.txt", 'r') as f:
            return f.read().strip()
    
    generator._load_prompt = load_v3_prompt
    
    print("🧪 Testing Enhanced V3 Prompt")
    print("="*60)
    
    total_coverage = 0
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['focus']}")
        print(f"   Title: {case['title'][:60]}...")
        
        try:
            start_time = time.time()
            result = generator.generate_slug_from_content(
                case['title'], 
                f"Blog post content about {case['focus']}", 
                count=3
            )
            duration = time.time() - start_time
            
            # Calculate coverage
            expected = set(case['expected_themes'])
            all_slugs = [result['primary']] + result.get('alternatives', [])
            slug_text = ' '.join(all_slugs).lower()
            
            matched = set()
            for theme in expected:
                if theme.lower() in slug_text:
                    matched.add(theme)
            
            coverage = len(matched) / len(expected)
            total_coverage += coverage
            
            print(f"   ✅ Primary: {result['primary']}")
            if result.get('alternatives'):
                print(f"   🔄 Alternatives: {result['alternatives']}")
            print(f"   📊 Theme Coverage: {coverage:.1%} ({len(matched)}/{len(expected)})")
            print(f"   ✓ Matched: {', '.join(sorted(matched))}")
            if expected - matched:
                print(f"   ❌ Missing: {', '.join(sorted(expected - matched))}")
            print(f"   ⏱️  Duration: {duration:.2f}s")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            
    avg_coverage = total_coverage / len(test_cases)
    
    print(f"\n" + "="*60)
    print(f"📊 V3 PROMPT RESULTS:")
    print(f"   Average Coverage: {avg_coverage:.1%}")
    print(f"   Target: >80% (improved from 63.5% baseline)")
    
    if avg_coverage > 0.8:
        print("   🎉 SUCCESS: V3 prompt shows significant improvement!")
    elif avg_coverage > 0.63:
        print("   📈 IMPROVEMENT: Better than baseline, continue optimizing")
    else:
        print("   ⚠️  NEEDS WORK: No improvement, try different approach")
    
    print("="*60)

if __name__ == "__main__":
    test_v3_prompt()