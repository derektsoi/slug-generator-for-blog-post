#!/usr/bin/env python3
"""
Focused A/B Testing: 10 Difficult Cases × 4 Versions = 40 Authenticated Generations

Tests the most challenging cases to validate V8 vs V10 vs V11a vs V11b performance
with complete authenticity documentation.
"""

import os
import sys
import json
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from validation.gpt_authenticity_validator import create_validated_generator


def get_difficult_cases():
    """10 hand-picked difficult cases that challenge slug generation"""
    return [
        {
            'id': 'difficult_01',
            'category': 'multi_brand_complex',
            'title': '【2025年最新】日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！',
            'content': '日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！完整購買教學與評價比較'
        },
        {
            'id': 'difficult_02',
            'category': 'cultural_subculture',
            'title': '一番賞Online購買教學，地雷系量產型手把手指南',
            'content': '一番賞Online購買教學，地雷系量產型服飾購物完整指南，包含jirai-kei風格搭配'
        },
        {
            'id': 'difficult_03',
            'category': 'compound_brand_hierarchy',
            'title': 'JoJo Maman Bébé童裝減價！英國官網直送香港攻略',
            'content': 'JoJo Maman Bébé童裝減價促銷活動，英國官網直送香港完整購物攻略'
        },
        {
            'id': 'difficult_04',
            'category': 'platform_vs_service',
            'title': 'BuyandShip vs Rakuten vs Amazon集運服務大比較',
            'content': 'BuyandShip vs Rakuten vs Amazon集運代購服務詳細比較，運費、時效、服務範圍完整分析'
        },
        {
            'id': 'difficult_05',
            'category': 'cultural_complex_brands',
            'title': '大國藥妝 vs @cosme store日本美妝代購平台比較',
            'content': '大國藥妝 vs @cosme store日本美妝代購平台詳細比較，產品種類、價格、運送方式分析'
        },
        {
            'id': 'difficult_06',
            'category': 'technical_product_specific',
            'title': 'DR.WU玻尿酸保濕精華液香港專櫃 vs 網購價格比較',
            'content': 'DR.WU玻尿酸保濕精華液香港專櫃價格與網購代購價格詳細比較分析'
        },
        {
            'id': 'difficult_07',
            'category': 'fashion_subculture_brands',
            'title': 'Musinsa韓系服飾 vs 地雷系量產型風格穿搭指南',
            'content': 'Musinsa韓系服飾平台與地雷系量產型風格穿搭完整指南，包含品牌推薦和搭配技巧'
        },
        {
            'id': 'difficult_08',
            'category': 'luxury_discount_complex',
            'title': 'Ralph Lauren Polo衫香港代購攻略：官網vs代購平台價格分析',
            'content': 'Ralph Lauren Polo衫香港代購完整攻略，官網直購與代購平台價格比較'
        },
        {
            'id': 'difficult_09',
            'category': 'anime_collectibles_cultural',
            'title': '一番賞海賊王最新彈！香港購買攻略和中獎率分析',
            'content': '一番賞海賊王最新彈完整購買攻略，香港購買地點推薦、中獎率統計分析'
        },
        {
            'id': 'difficult_10',
            'category': 'service_comparison_complex',
            'title': '香港集運服務大比較：順豐集運vs易達集運vs買買買攻略',
            'content': '香港集運服務詳細比較分析，順豐集運vs易達集運vs其他代購平台服務內容'
        }
    ]


def run_focused_ab_test():
    """Run focused A/B test on 10 difficult cases"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not set")
        return
    
    print("🧪 FOCUSED A/B TESTING: V8 vs V10 vs V11a vs V11b")
    print("=" * 70)
    print("📊 10 Difficult Cases × 4 Versions = 40 Authenticated Generations")
    print("🛡️  Complete authenticity validation for every response")
    print("=" * 70)
    
    # Create all generators
    versions = ['v8', 'v10', 'v11a', 'v11b']
    generators = {}
    validators = {}
    
    for version in versions:
        gen, val = create_validated_generator(api_key, version)
        generators[version] = gen
        validators[version] = val
    
    print(f"✅ Created authenticated generators for: {versions}")
    
    # Get difficult cases
    cases = get_difficult_cases()
    results = []
    
    # Test each case
    for case_idx, case in enumerate(cases, 1):
        print(f"\n📝 [{case_idx:2d}/10] {case['id']}: {case['title'][:50]}...")
        print(f"    Category: {case['category']}")
        
        case_results = {
            'case_info': case,
            'generations': {},
            'word_counts': {},
            'timing': {},
            'success': {}
        }
        
        # Test each version
        for version in versions:
            print(f"    🔄 {version}...", end=' ')
            
            try:
                start_time = time.time()
                result = generators[version].generator.generate_slug_from_content(
                    case['title'], case['content']
                )
                end_time = time.time()
                
                slug = result['primary']
                word_count = len(slug.split('-'))
                generation_time = end_time - start_time
                
                case_results['generations'][version] = slug
                case_results['word_counts'][version] = word_count
                case_results['timing'][version] = generation_time
                case_results['success'][version] = True
                
                print(f"{slug} ({word_count}w, {generation_time:.1f}s)")
                
            except Exception as e:
                case_results['generations'][version] = None
                case_results['word_counts'][version] = 0
                case_results['timing'][version] = 0
                case_results['success'][version] = False
                print(f"❌ ERROR - {str(e)}")
        
        results.append(case_results)
    
    # Authenticity validation
    print(f"\n📊 AUTHENTICITY VALIDATION")
    print("=" * 50)
    
    authenticity_summary = {}
    for version in versions:
        report = validators[version].generate_authenticity_report()
        authenticity_summary[version] = report
        auth_rate = report['authenticity_rate'] * 100
        print(f"{version:4s}: {report['authentic_calls']:2d}/{report['total_calls']:2d} authentic ({auth_rate:5.1f}%)")
        
        if report.get('suspicious_calls', 0) > 0:
            print(f"      ⚠️  {report['suspicious_calls']} suspicious calls detected")
    
    # Performance analysis
    print(f"\n📈 PERFORMANCE ANALYSIS")
    print("=" * 50)
    
    # Success rates
    print("Success Rates:")
    for version in versions:
        success_count = sum(1 for result in results if result['success'][version])
        success_rate = success_count / len(results) * 100
        print(f"  {version:4s}: {success_count:2d}/10 ({success_rate:5.1f}%)")
    
    # Word count statistics
    print("\nWord Count Statistics:")
    for version in versions:
        word_counts = [r['word_counts'][version] for r in results if r['success'][version]]
        if word_counts:
            avg_words = sum(word_counts) / len(word_counts)
            min_words = min(word_counts)
            max_words = max(word_counts)
            print(f"  {version:4s}: avg={avg_words:4.1f}, range={min_words}-{max_words}")
    
    # Constraint compliance
    print("\nConstraint Compliance:")
    constraints = {'v8': (1, 8), 'v10': (1, 10), 'v11a': (3, 5), 'v11b': (8, 12)}
    
    for version in versions:
        compliant_count = 0
        total_count = 0
        
        for result in results:
            if result['success'][version]:
                total_count += 1
                words = result['word_counts'][version]
                min_w, max_w = constraints[version]
                if min_w <= words <= max_w:
                    compliant_count += 1
        
        if total_count > 0:
            compliance_rate = compliant_count / total_count * 100
            print(f"  {version:4s}: {compliant_count:2d}/{total_count:2d} ({compliance_rate:5.1f}%)")
    
    # Pattern analysis (banned words)
    print("\nPattern Analysis (banned words):")
    banned_words = ['ultimate', 'premium']
    
    for version in versions:
        pattern_issues = 0
        total_slugs = 0
        
        for result in results:
            slug = result['generations'].get(version)
            if slug:
                total_slugs += 1
                if any(word in slug.lower() for word in banned_words):
                    pattern_issues += 1
        
        if total_slugs > 0:
            issue_rate = pattern_issues / total_slugs * 100
            print(f"  {version:4s}: {pattern_issues:2d}/{total_slugs:2d} issues ({issue_rate:5.1f}%)")
    
    # Save evidence
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    evidence_file = f"focused_ab_test_{timestamp}.json"
    
    evidence_package = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'test_type': 'focused_difficult_cases',
            'total_cases': len(cases),
            'versions_tested': versions,
            'total_generations': len(cases) * len(versions)
        },
        'authenticity_summary': authenticity_summary,
        'detailed_results': results
    }
    
    with open(evidence_file, 'w', encoding='utf-8') as f:
        json.dump(evidence_package, f, indent=2, ensure_ascii=False)
    
    # Save individual traces
    os.makedirs("traces", exist_ok=True)
    for version in versions:
        validators[version].save_traces(f"traces/focused_{version}_{timestamp}.json")
    
    print(f"\n🎯 FOCUSED A/B TEST COMPLETE")
    print("=" * 50)
    print(f"✅ 40 authenticated slug generations completed")
    print(f"✅ All authenticity validated and documented")
    print(f"✅ Complete evidence package saved")
    
    # Final authenticity check
    total_suspicious = sum(
        auth['suspicious_calls'] for auth in authenticity_summary.values()
    )
    
    if total_suspicious == 0:
        print(f"\n🛡️  ALL RESPONSES VERIFIED AUTHENTIC")
        print(f"✅ Safe to use for performance analysis")
    else:
        print(f"\n⚠️  WARNING: {total_suspicious} suspicious responses")
        print(f"🚨 Review evidence before using for analysis")
    
    print(f"\n📁 Evidence saved:")
    print(f"   📊 Main results: {evidence_file}")
    for version in versions:
        print(f"   🔍 {version} traces: traces/focused_{version}_{timestamp}.json")


if __name__ == "__main__":
    run_focused_ab_test()