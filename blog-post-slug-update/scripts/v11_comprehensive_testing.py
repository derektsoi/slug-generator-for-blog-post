#!/usr/bin/env python3
"""
V11 Comprehensive 4-Version A/B Testing Script
Real LLM API testing with production data analysis
"""

import json
import random
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def load_production_urls():
    """Load URLs from production batch data for random selection"""
    production_file = Path(__file__).parent.parent / 'docs/archive/batch-processing-data/batch_data/production/batch_8000/comprehensive_url_database.json'
    
    if not production_file.exists():
        print(f"❌ Production file not found: {production_file}")
        return []
    
    try:
        with open(production_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"📊 Loaded production database: {len(data)} total URLs")
        
        # Extract URLs with titles for testing
        urls_with_titles = []
        for item in data:
            if isinstance(item, dict) and 'title' in item and 'url' in item:
                urls_with_titles.append({
                    'title': item['title'],
                    'url': item['url'],
                    'content': item.get('content', item['title'])  # Use title as content if no content
                })
        
        print(f"✅ Found {len(urls_with_titles)} URLs with titles")
        return urls_with_titles
        
    except Exception as e:
        print(f"❌ Error loading production data: {e}")
        return []

def select_random_urls(all_urls, count=30):
    """Randomly select URLs from production dataset"""
    if len(all_urls) < count:
        print(f"⚠️ Only {len(all_urls)} URLs available, using all")
        return all_urls
    
    random.seed(42)  # Reproducible results
    selected = random.sample(all_urls, count)
    
    print(f"🎲 Randomly selected {len(selected)} URLs for testing")
    return selected

def hand_pick_problematic_urls():
    """Hand-pick 10 problematic URLs targeting specific failure categories"""
    problematic_cases = [
        # Multi-brand failures (3+ brands)
        {
            "title": "日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！",
            "url": "https://example.com/multi-brand-phone-cases",
            "content": "全面比較SKINNIYDIP、iface、犀牛盾等7個手機殼品牌的特色",
            "category": "multi_brand_failure",
            "v11_target": "v11b",
            "challenge": "3+ brands with complex product context"
        },
        
        # Cultural subculture terms (new V11 capability)
        {
            "title": "地雷系vs量產型風格完整對比！2025年最新潮流分析",
            "url": "https://example.com/jirai-kei-vs-ryousangata",
            "content": "深入分析地雷系和量產型兩種日系時尚風格的差異和搭配技巧",
            "category": "cultural_subculture", 
            "v11_target": "v11b",
            "challenge": "V10 lacks subculture intelligence - jirai-kei, ryousangata"
        },
        
        # Pattern repetition victims (currently using ultimate/premium)
        {
            "title": "【終極攻略】一番賞購買完整教學！日本動漫周邊收藏指南",
            "url": "https://example.com/ultimate-ichiban-kuji-guide", 
            "content": "一番賞購買完整攻略，從新手到專家的收藏教學",
            "category": "pattern_repetition_victim",
            "v11_target": "v11b", 
            "challenge": "Currently would use 'ultimate' - V11 must use alternatives"
        },
        
        # Complex service contexts (proxy + forwarding + official)
        {
            "title": "大國藥妝香港店vs日本代購vs官網直送完整比較分析",
            "url": "https://example.com/daikoku-multi-service-comparison",
            "content": "比較大國藥妝香港實體店、日本代購服務、官網直送的優缺點",
            "category": "complex_service_context",
            "v11_target": "v11b",
            "challenge": "Multi-service comparison with brand + geography + service types"
        },
        
        # Simple content over-enhancement (should be V11a)
        {
            "title": "Tory Burch減價優惠！英國網購低至3折",
            "url": "https://example.com/tory-burch-discount",
            "content": "Tory Burch英國官網減價活動，手袋鞋履3折優惠",
            "category": "simple_over_enhancement",
            "v11_target": "v11a", 
            "challenge": "V10 might over-enhance simple discount info"
        },
        
        # Brand hierarchy confusion (parent + sub-brand)
        {
            "title": "Uniqlo U系列vs一般Uniqlo產品線差異完整分析",
            "url": "https://example.com/uniqlo-u-vs-regular",
            "content": "深入比較Uniqlo U設計師系列與一般Uniqlo產品的差異",
            "category": "brand_hierarchy_confusion",
            "v11_target": "v11b",
            "challenge": "Parent brand (Uniqlo) vs sub-brand (Uniqlo U) distinction"
        },
        
        # Geographic complexity (multi-region)
        {
            "title": "樂天全球配送服務：日本→香港→台灣轉運完整教學",
            "url": "https://example.com/rakuten-multi-region-shipping", 
            "content": "樂天國際配送服務，涵蓋日本到香港再到台灣的轉運流程",
            "category": "geographic_complexity",
            "v11_target": "v11b",
            "challenge": "Multi-region shipping flow with service complexity"
        },
        
        # Character archetype content (new V11 terms)
        {
            "title": "病嬌角色完整分析：動漫文化中的心理特徵研究",
            "url": "https://example.com/yandere-character-analysis",
            "content": "深入分析病嬌角色在動漫文化中的心理特徵和表現手法",
            "category": "character_archetype",
            "v11_target": "v11b",
            "challenge": "V10 lacks yandere cultural archetype recognition"
        },
        
        # Fashion subculture (V11 new intelligence)
        {
            "title": "蘿莉塔時尚完整指南：從Classic到Gothic風格全解析",
            "url": "https://example.com/lolita-fashion-guide",
            "content": "蘿莉塔時尚的完整指南，包含Classic、Sweet、Gothic等各種風格",
            "category": "fashion_subculture", 
            "v11_target": "v11b",
            "challenge": "V10 lacks lolita-fashion subculture recognition"
        },
        
        # Cross-border service comparison
        {
            "title": "Amazon Japan官網 vs 日本代購 vs 集運服務完整比較",
            "url": "https://example.com/amazon-japan-service-comparison",
            "content": "比較Amazon Japan官網直送、代購服務、集運服務的優缺點",
            "category": "cross_border_service",
            "v11_target": "v11b", 
            "challenge": "Official vs proxy vs forwarding service comparison"
        }
    ]
    
    print(f"🎯 Hand-picked {len(problematic_cases)} problematic URLs:")
    for i, case in enumerate(problematic_cases, 1):
        print(f"{i:2d}. {case['category']:25s} -> {case['v11_target']}")
    
    return problematic_cases

def classify_content_complexity(title, content):
    """Classify content as simple (V11a) or complex (V11b)"""
    
    # Simple content indicators
    simple_indicators = [
        '減價', '優惠', '折扣', 'discount', '免運', 'free shipping', 
        '價格', 'price', '費用', 'cost', '運送', 'shipping'
    ]
    
    # Complex content indicators  
    complex_indicators = [
        '完整', '詳細', '深入', '全面', '比較', '分析', '教學', '攻略',
        'vs', '對比', '指南', 'guide', '系列', 'collection', '風格', 'style'
    ]
    
    # Multi-brand detection
    brand_count = 0
    brands = ['Uniqlo', 'SKINNIYDIP', 'iface', '犀牛盾', 'Tory Burch', 
              'Amazon', '大國藥妝', '樂天', 'Daikoku']
    for brand in brands:
        if brand.lower() in title.lower() or brand.lower() in content.lower():
            brand_count += 1
    
    # Cultural complexity
    cultural_complex = any(term in title + content for term in [
        '地雷系', '量產型', '病嬌', '蘿莉塔', '一番賞', 'jirai', 'ryousa', 'yandere'
    ])
    
    # Decision logic
    if brand_count >= 2 or cultural_complex or any(ind in title + content for ind in complex_indicators):
        return "v11b", "complex"
    elif any(ind in title + content for ind in simple_indicators):
        return "v11a", "simple"  
    else:
        return "v11a", "simple"  # Default to simple

def setup_testing_framework():
    """Setup the 4-version testing framework"""
    
    # Load production URLs
    all_urls = load_production_urls()
    if not all_urls:
        print("❌ No production URLs loaded, cannot proceed")
        return None, None
        
    # Select random 30 URLs
    random_urls = select_random_urls(all_urls, 30)
    
    # Hand-pick 10 problematic URLs
    problematic_urls = hand_pick_problematic_urls()
    
    # Classify all URLs for V11a/V11b routing
    test_cases = []
    
    print(f"\n📊 CLASSIFYING URLS FOR V11 ROUTING:")
    print("=" * 50)
    
    # Process random URLs
    for i, url_data in enumerate(random_urls, 1):
        v11_variant, complexity = classify_content_complexity(
            url_data['title'], url_data['content']
        )
        test_cases.append({
            'id': f"random_{i:02d}",
            'title': url_data['title'],
            'content': url_data['content'], 
            'url': url_data['url'],
            'source': 'random',
            'complexity': complexity,
            'v11_target': v11_variant
        })
    
    # Process problematic URLs
    for i, url_data in enumerate(problematic_urls, 1):
        test_cases.append({
            'id': f"problem_{i:02d}",
            'title': url_data['title'],
            'content': url_data['content'],
            'url': url_data['url'], 
            'source': 'problematic',
            'category': url_data['category'],
            'complexity': 'complex' if url_data['v11_target'] == 'v11b' else 'simple',
            'v11_target': url_data['v11_target'],
            'challenge': url_data['challenge']
        })
    
    # Print classification summary
    v11a_count = len([t for t in test_cases if t['v11_target'] == 'v11a'])
    v11b_count = len([t for t in test_cases if t['v11_target'] == 'v11b'])
    
    print(f"V11a (Simple): {v11a_count} cases")
    print(f"V11b (Complex): {v11b_count} cases") 
    print(f"Total: {len(test_cases)} test cases")
    
    return test_cases, {
        'versions': ['v6', 'v10', 'v11a', 'v11b'],
        'random_count': len(random_urls),
        'problematic_count': len(problematic_urls),
        'v11a_cases': v11a_count,
        'v11b_cases': v11b_count
    }

if __name__ == "__main__":
    print("🧪 V11 COMPREHENSIVE 4-VERSION TESTING FRAMEWORK")
    print("=" * 55)
    
    test_cases, framework_info = setup_testing_framework()
    
    if test_cases:
        print(f"\n✅ TESTING FRAMEWORK READY:")
        print(f"📋 Test cases: {len(test_cases)}")
        print(f"🎲 Random URLs: {framework_info['random_count']}")
        print(f"🎯 Problematic URLs: {framework_info['problematic_count']}")
        print(f"🔧 V11a (Simple): {framework_info['v11a_cases']}")
        print(f"🚀 V11b (Complex): {framework_info['v11b_cases']}")
        print(f"📊 Versions to test: {', '.join(framework_info['versions'])}")
        
        # Save test cases for actual execution
        output_file = Path(__file__).parent / 'v11_test_cases.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'test_cases': test_cases,
                'framework_info': framework_info
            }, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Test cases saved to: {output_file}")
        print(f"\n🚀 READY FOR A/B TESTING EXECUTION!")
    else:
        print("❌ Failed to setup testing framework")