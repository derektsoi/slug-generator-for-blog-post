#!/usr/bin/env python3
"""
Comprehensive comparison of all prompt versions
"""

import sys
import os
import json
import time
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, 'src')

from slug_generator import SlugGenerator

def test_all_prompt_versions():
    """Test all prompt versions on expanded dataset"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OPENAI_API_KEY found")
        return
    
    # Expanded test cases covering various scenarios
    test_cases = [
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
        },
        {
            "title": "GAP集團美國官網網購教學，附Old Navy、Banana Republic及Athleta等副牌全面介紹",
            "expected_themes": ["gap", "us", "fashion", "brands"],
            "category": "fashion-brands"
        },
        {
            "title": "打風落雨必備！PROTECT U、Floatus及Wpc.等超強防風/跣水/降溫雨傘樂天網購教學",
            "expected_themes": ["umbrella", "japan", "rakuten", "weather"],
            "category": "platform-product"
        },
        {
            "title": "日本樂天時尚特價1折怎麼買？NB、BEAMS等男女、童裝優惠合集及集運教學",
            "expected_themes": ["japan", "rakuten", "fashion", "sale"],
            "category": "marketplace-fashion"
        },
        {
            "title": "8大日牌輕珠寶品牌一次睇！Agete、nojess及Star Jewelry等日劇女主御用明星珠寶",
            "expected_themes": ["japanese", "jewelry", "brands", "guide"],
            "category": "luxury-brands"
        }
    ]
    
    versions = ["v1", "v2", "v3"]
    results = {}
    
    print("🔬 COMPREHENSIVE PROMPT COMPARISON")
    print("="*80)
    print(f"Testing {len(test_cases)} cases across {len(versions)} prompt versions")
    print()
    
    for version in versions:
        print(f"🧪 Testing Prompt Version: {version}")
        
        # Create generator with specific prompt version
        generator = SlugGenerator(api_key=api_key, max_retries=2)
        
        if version == "v1":
            # Use original prompt
            def load_v1_prompt(prompt_name):
                with open("config/prompts/slug_generation.txt", 'r') as f:
                    return f.read().strip()
            generator._load_prompt = load_v1_prompt
        elif version == "v2":
            def load_v2_prompt(prompt_name):
                with open("config/prompts/slug_generation_v2.txt", 'r') as f:
                    return f.read().strip()
            generator._load_prompt = load_v2_prompt
        elif version == "v3":
            def load_v3_prompt(prompt_name):
                with open("config/prompts/slug_generation_v3.txt", 'r') as f:
                    return f.read().strip()
            generator._load_prompt = load_v3_prompt
        
        version_results = []
        total_coverage = 0
        successful = 0
        
        for i, case in enumerate(test_cases, 1):
            try:
                start_time = time.time()
                result = generator.generate_slug_from_content(
                    case['title'], 
                    f"Blog post about {case['category']}", 
                    count=2
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
                successful += 1
                
                version_results.append({
                    'case_id': i,
                    'category': case['category'],
                    'primary_slug': result['primary'],
                    'alternatives': result.get('alternatives', []),
                    'expected_themes': list(expected),
                    'matched_themes': list(matched),
                    'theme_coverage': coverage,
                    'duration': duration
                })
                
                print(f"   {i}. {case['category']}: {result['primary']} ({coverage:.1%})")
                
            except Exception as e:
                print(f"   {i}. {case['category']}: ❌ Error - {str(e)[:50]}...")
                version_results.append({
                    'case_id': i,
                    'category': case['category'],
                    'error': str(e),
                    'duration': 0
                })
        
        avg_coverage = total_coverage / len(test_cases) if test_cases else 0
        
        results[version] = {
            'avg_coverage': avg_coverage,
            'successful': successful,
            'total': len(test_cases),
            'results': version_results
        }
        
        print(f"   📊 Summary: {successful}/{len(test_cases)} success, {avg_coverage:.1%} avg coverage")
        print()
        time.sleep(1)  # Brief pause between versions
    
    # Generate comprehensive comparison
    print("="*80)
    print("📊 FINAL COMPARISON RESULTS")
    print("="*80)
    
    print("🏆 Performance Ranking:")
    sorted_versions = sorted(results.keys(), key=lambda v: results[v]['avg_coverage'], reverse=True)
    
    for i, version in enumerate(sorted_versions, 1):
        result = results[version]
        success_rate = result['successful'] / result['total']
        print(f"   {i}. {version}: {result['avg_coverage']:.1%} coverage, {success_rate:.0%} success")
    
    best_version = sorted_versions[0]
    baseline_version = "v1"
    
    if best_version != baseline_version:
        improvement = results[best_version]['avg_coverage'] - results[baseline_version]['avg_coverage']
        print(f"\n📈 Improvement: {best_version} vs {baseline_version}: +{improvement:.1%} coverage")
    
    # Category-wise analysis
    print(f"\n🎯 Category Performance (Best Version: {best_version}):")
    best_results = results[best_version]['results']
    
    for result in best_results:
        if 'error' not in result:
            print(f"   {result['category']}: {result['theme_coverage']:.1%} - {result['primary_slug']}")
            if result['theme_coverage'] < 1.0:
                missing = set(result['expected_themes']) - set(result['matched_themes'])
                print(f"      Missing: {', '.join(missing)}")
    
    # Save comprehensive results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"results/comprehensive_prompt_comparison_{timestamp}.json"
    
    os.makedirs('results', exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'test_cases': len(test_cases),
            'versions_tested': versions,
            'results': results,
            'best_version': best_version,
            'improvement_over_baseline': results[best_version]['avg_coverage'] - results[baseline_version]['avg_coverage']
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Detailed results saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    test_all_prompt_versions()