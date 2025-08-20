#!/usr/bin/env python3
"""
Test the improved slug generator with 10 sample URLs from the dataset
"""

import sys
import os
import json
import time
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, 'src')

from slug_generator import SlugGenerator

# Sample URLs from the dataset
TEST_SAMPLES = [
    {
        "title": "8大日牌輕珠寶品牌一次睇！Agete、nojess及Star Jewelry等日劇女主御用明星珠寶",
        "url": "https://www.buyandship.today/blog/2025/08/18/%e6%97%a5%e6%9c%ac%e8%bc%95%e7%8f%a0%e5%af%b6%e5%93%81%e7%89%8c%e5%90%88%e9%9b%86/",
        "expected_themes": ["japanese", "jewelry", "brands", "guide"]
    },
    {
        "title": "英國必買童裝 JoJo Maman Bébé官網 3 折起入手網購教學",
        "url": "https://www.buyandship.today/blog/2025/08/18/jojo-maman-bebe%e8%8b%b1%e5%9c%8b%e5%ae%98%e7%b6%b2%e6%8a%98%e6%89%a3%e5%8f%8a%e8%b3%bc%e8%b2%b7%e6%95%99%e5%ad%b8/",
        "expected_themes": ["uk", "baby", "clothes", "shopping", "guide"]
    },
    {
        "title": "Kindle電子書閱讀器最強攻略：Paper White、Colorsoft等型號分別、價格比較及網購集運教學",
        "url": "https://www.buyandship.today/blog/2025/08/13/kindle%e7%b6%b2%e8%b3%bc%e6%94%bb%e7%95%a5/",
        "expected_themes": ["kindle", "ereader", "comparison", "guide"]
    },
    {
        "title": "日本樂天時尚特價1折怎麼買？NB、BEAMS等男女、童裝優惠合集及集運教學",
        "url": "https://www.buyandship.today/blog/2025/08/14/rakuten-fashion-clearance-must-buy-brands/",
        "expected_themes": ["japan", "rakuten", "fashion", "sale"]
    },
    {
        "title": "GAP集團美國官網網購教學，附Old Navy、Banana Republic及Athleta等副牌全面介紹",
        "url": "https://www.buyandship.today/blog/2025/08/13/gap%e9%9b%86%e5%9c%98%e7%be%8e%e5%9c%8b%e5%ae%98%e7%b6%b2%e6%95%99%e5%ad%b8/",
        "expected_themes": ["gap", "us", "fashion", "brands"]
    },
    {
        "title": "如何代購 3COINS 日本限定及網絡限定商品？Pokemon周邊、相機及扭蛋收納神器推薦",
        "url": "https://www.buyandship.today/blog/2025/08/15/3coins%e6%97%a5%e6%9c%ac%e9%99%90%e5%ae%9a%e4%bb%a3%e8%b3%bc/",
        "expected_themes": ["3coins", "japan", "pokemon", "guide"]
    },
    {
        "title": "Verish內衣品牌港韓價差大比拼！人氣Cool-Fit無鋼圈、運動系列必買推介",
        "url": "https://www.buyandship.today/blog/2025/08/18/verish%e9%9f%93%e5%83%b9%e5%b7%ae%e5%a4%a7%e6%af%94%e6%8b%bc/",
        "expected_themes": ["verish", "korea", "comparison", "sports"]
    },
    {
        "title": "打風落雨必備！PROTECT U、Floatus及Wpc.等超強防風/跣水/降溫雨傘樂天網購教學",
        "url": "https://www.buyandship.today/blog/2025/08/13/%e6%97%a5%e6%9c%ac%e6%a8%82%e5%a4%a9%e9%9b%a8%e5%82%98%e7%b6%b2%e8%b3%bc%e6%95%99%e5%ad%b8/",
        "expected_themes": ["umbrella", "japan", "rakuten", "weather"]
    },
    {
        "title": "開學季代購必買清單！IFME返學鞋、Gregory背囊及電子文具產品低至3折",
        "url": "https://www.buyandship.today/blog/2025/08/12/%e9%96%8b%e5%ad%b8%e5%ad%a3%e4%bb%a3%e8%b3%bc%e5%bf%85%e8%b2%b7%e6%b8%85%e5%96%ae/",
        "expected_themes": ["school", "season", "shoes", "bags"]
    },
    {
        "title": "2025年12大必買日本手信零食，唔使出國親身排隊都輕鬆買到！",
        "url": "https://www.buyandship.today/blog/2025/08/12/%e5%bf%85%e8%b2%b7%e6%97%a5%e6%9c%ac%e6%89%8b%e4%bf%a1/",
        "expected_themes": ["japan", "snacks", "souvenirs", "2025"]
    }
]

def test_with_real_api():
    """Test with real OpenAI API"""
    print("="*80)
    print("TESTING IMPROVED SLUG GENERATOR WITH 10 REAL SAMPLES")
    print("="*80)
    
    # Check if API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OPENAI_API_KEY found in environment")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # Initialize generator with improved settings
    generator = SlugGenerator(
        api_key=api_key,
        max_retries=2,
        retry_delay=1.0
    )
    
    print(f"✅ Generator initialized with:")
    print(f"   - Model: gpt-4o-mini")
    print(f"   - Content limit: {generator.api_content_limit} chars")
    print(f"   - Preview limit: {generator.prompt_preview_limit} chars")
    print(f"   - Confidence threshold: {generator.confidence_threshold}")
    print(f"   - Max retries: {generator.max_retries}")
    print()
    
    results = []
    total_start_time = time.time()
    
    for i, sample in enumerate(TEST_SAMPLES, 1):
        print(f"🔄 Testing {i}/10: {sample['title'][:50]}...")
        
        try:
            start_time = time.time()
            
            # Generate slug with improved implementation
            result = generator.generate_slug(sample['url'], count=3)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Analyze the result
            primary_slug = result['primary']
            alternatives = result.get('alternatives', [])
            
            # Check if expected themes are present
            all_slugs = [primary_slug] + alternatives
            slug_text = ' '.join(all_slugs)
            
            theme_matches = []
            for theme in sample['expected_themes']:
                if any(theme.lower() in slug.lower() for slug in all_slugs):
                    theme_matches.append(theme)
            
            theme_coverage = len(theme_matches) / len(sample['expected_themes'])
            
            result_data = {
                'sample_id': i,
                'title': sample['title'],
                'url': sample['url'],
                'primary_slug': primary_slug,
                'alternatives': alternatives,
                'expected_themes': sample['expected_themes'],
                'theme_matches': theme_matches,
                'theme_coverage': theme_coverage,
                'duration': duration,
                'success': True
            }
            
            results.append(result_data)
            
            print(f"   ✅ Primary: {primary_slug}")
            if alternatives:
                print(f"   🔄 Alternatives: {', '.join(alternatives)}")
            print(f"   📊 Theme coverage: {theme_coverage:.1%} ({len(theme_matches)}/{len(sample['expected_themes'])})")
            print(f"   ⏱️  Duration: {duration:.2f}s")
            print()
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            result_data = {
                'sample_id': i,
                'title': sample['title'],
                'url': sample['url'],
                'error': str(e),
                'success': False,
                'duration': time.time() - start_time
            }
            results.append(result_data)
            print()
    
    total_duration = time.time() - total_start_time
    
    # Generate summary
    print("="*80)
    print("SUMMARY RESULTS")
    print("="*80)
    
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    print(f"✅ Successful: {len(successful_tests)}/10")
    print(f"❌ Failed: {len(failed_tests)}/10")
    print(f"⏱️  Total time: {total_duration:.2f}s")
    print(f"⏱️  Average time: {total_duration/10:.2f}s per request")
    
    if successful_tests:
        avg_coverage = sum(r['theme_coverage'] for r in successful_tests) / len(successful_tests)
        print(f"📊 Average theme coverage: {avg_coverage:.1%}")
        
        print(f"\n🏆 Best performing slugs:")
        best_results = sorted(successful_tests, key=lambda x: x['theme_coverage'], reverse=True)[:3]
        for result in best_results:
            print(f"   • {result['primary_slug']} (coverage: {result['theme_coverage']:.1%})")
    
    if failed_tests:
        print(f"\n❌ Failed tests:")
        for result in failed_tests:
            print(f"   • Sample {result['sample_id']}: {result['error']}")
    
    # Save detailed results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"results/test_10_samples_{timestamp}.json"
    
    os.makedirs('results', exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'total_samples': len(TEST_SAMPLES),
            'successful': len(successful_tests),
            'failed': len(failed_tests),
            'total_duration': total_duration,
            'average_duration': total_duration / len(TEST_SAMPLES),
            'generator_config': {
                'api_content_limit': generator.api_content_limit,
                'prompt_preview_limit': generator.prompt_preview_limit,
                'confidence_threshold': generator.confidence_threshold,
                'max_retries': generator.max_retries
            },
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Detailed results saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    test_with_real_api()