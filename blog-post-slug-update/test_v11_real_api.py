#!/usr/bin/env python3
"""
V11 REAL API TESTING - Fix the Simulation Problem
Test V11a and V11b against real LLM API calls with actual content
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.slug_generator import SlugGenerator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_sample_test_cases():
    """Load 10 diverse test cases from the V11 testing data"""
    test_cases_file = Path(__file__).parent / 'docs/evolution/results/v11/v11_test_cases.json'
    
    if test_cases_file.exists():
        with open(test_cases_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['test_cases'][:10]  # First 10 cases
    else:
        # Fallback test cases
        return [
            {
                "id": "test_01",
                "title": "人氣 Rhythm 風扇專業評測！Buyandship Facebook交流區會員真實用後感",
                "content": "人氣 Rhythm 風扇專業評測！Buyandship Facebook交流區會員真實用後感",
                "source": "production"
            },
            {
                "id": "test_02", 
                "title": "HK$38 買 Ralph Lauren Tee！",
                "content": "HK$38 買 Ralph Lauren Tee！",
                "source": "production"
            },
            {
                "id": "test_03",
                "title": "日本 Onspotz 靚帽網店特價低至七折",
                "content": "日本 Onspotz 靚帽網店特價低至七折",
                "source": "production"
            },
            {
                "id": "test_04",
                "title": "地雷系vs量產型風格完整對比！2025年最新潮流分析",
                "content": "深入分析地雷系和量產型兩種日系時尚風格的差異和搭配技巧",
                "source": "problematic"
            },
            {
                "id": "test_05",
                "title": "大國藥妝香港店vs日本代購vs官網直送完整比較分析",
                "content": "比較大國藥妝香港實體店、日本代購服務、官網直送的優缺點",
                "source": "problematic"
            }
        ]

def test_real_v11_api(test_cases):
    """Test V11 variants with real LLM API calls"""
    
    print("🧪 V11 REAL API TESTING")
    print("=" * 40)
    print(f"📊 Testing {len(test_cases)} cases with real LLM API calls")
    print()
    
    # Initialize generators for ACTUAL available versions
    # V11a and V11b don't exist in the system - the testing was completely fake!
    versions = {
        'v8': SlugGenerator(prompt_version='v8'),   # V8 Breakthrough (known working)
        'v9': SlugGenerator(prompt_version='v9'),   # V9 LLM-guided  
        'v10': SlugGenerator(prompt_version='v10')  # V10 Production current
    }
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🔍 Test Case {i}: {test_case['id']}")
        print(f"   Title: {test_case['title'][:60]}{'...' if len(test_case['title']) > 60 else ''}")
        
        case_results = {
            'test_case': test_case,
            'version_results': {}
        }
        
        # Test each version
        for version_name, generator in versions.items():
            print(f"   Testing {version_name}...", end=' ')
            
            try:
                result = generator.generate_slug_from_content(
                    test_case['title'],
                    test_case['content']
                )
                
                case_results['version_results'][version_name] = {
                    'slug': result['primary'],
                    'confidence': result.get('confidence', 0.0),
                    'success': True,
                    'word_count': len(result['primary'].split('-')),
                    'analysis': result.get('analysis', {})
                }
                
                print(f"✅ {result['primary']}")
                
            except Exception as e:
                case_results['version_results'][version_name] = {
                    'error': str(e),
                    'success': False
                }
                print(f"❌ Error: {str(e)[:50]}...")
        
        results.append(case_results)
        print()
    
    return results

def analyze_real_results(results):
    """Analyze real API results for brand intelligence and pattern issues"""
    
    print("📊 REAL V11 RESULTS ANALYSIS")
    print("=" * 35)
    
    # Extract all slugs by version
    version_slugs = {'v8': [], 'v9': [], 'v10': []}
    
    for result in results:
        for version, version_result in result['version_results'].items():
            if version_result.get('success'):
                version_slugs[version].append({
                    'slug': version_result['slug'],
                    'test_id': result['test_case']['id'],
                    'title': result['test_case']['title']
                })
    
    # 1. Brand Intelligence Analysis
    print("🏢 BRAND INTELLIGENCE ANALYSIS:")
    print("-" * 32)
    
    brands_mentioned = ['Ralph Lauren', 'Rhythm', 'Buyandship', 'Buy&Ship', 'Onspotz', 'Uniqlo', '大國藥妝', 'Daikoku']
    
    for version in ['v8', 'v9', 'v10']:
        print(f"\n{version.upper()} Brand Recognition:")
        brand_preserved = 0
        total_with_brands = 0
        
        for slug_data in version_slugs[version]:
            title = slug_data['title']
            slug = slug_data['slug']
            
            # Check if title contains brands
            title_brands = [brand for brand in brands_mentioned if brand.lower() in title.lower()]
            if title_brands:
                total_with_brands += 1
                
                # Check if slug preserves any brand
                slug_brands = [brand for brand in title_brands if brand.lower().replace(' ', '').replace('&', '') in slug.lower()]
                if slug_brands:
                    brand_preserved += 1
                    print(f"   ✅ {slug_data['test_id']}: {slug} (preserved: {', '.join(slug_brands)})")
                else:
                    print(f"   ❌ {slug_data['test_id']}: {slug} (lost: {', '.join(title_brands)})")
        
        if total_with_brands > 0:
            preservation_rate = (brand_preserved / total_with_brands) * 100
            print(f"   📊 Brand Preservation: {brand_preserved}/{total_with_brands} ({preservation_rate:.1f}%)")
        else:
            print("   📊 No brand test cases found")
    
    # 2. Pattern Repetition Analysis  
    print(f"\n🔄 PATTERN REPETITION ANALYSIS:")
    print("-" * 30)
    
    for version in ['v8', 'v9', 'v10']:
        slugs = [s['slug'] for s in version_slugs[version]]
        
        if not slugs:
            print(f"{version.upper()}: No successful results")
            continue
        
        # Check for problematic patterns
        ultimate_count = sum(1 for slug in slugs if 'ultimate' in slug)
        premium_count = sum(1 for slug in slugs if 'premium' in slug) 
        japan_guide_count = sum(1 for slug in slugs if slug == 'japan-shopping-guide')
        
        print(f"\n{version.upper()} Pattern Analysis ({len(slugs)} slugs):")
        print(f"   🚨 'ultimate': {ultimate_count} ({(ultimate_count/len(slugs)*100):.1f}%)")
        print(f"   🚨 'premium': {premium_count} ({(premium_count/len(slugs)*100):.1f}%)")  
        print(f"   ⚠️ Exact 'japan-shopping-guide': {japan_guide_count} ({(japan_guide_count/len(slugs)*100):.1f}%)")
        
        # Show unique slugs
        unique_slugs = list(set(slugs))
        print(f"   📊 Unique patterns: {len(unique_slugs)}/{len(slugs)} ({(len(unique_slugs)/len(slugs)*100):.1f}%)")
        
        if len(unique_slugs) < len(slugs):
            print("   🔍 Generated slugs:")
            for slug_data in version_slugs[version]:
                print(f"      {slug_data['test_id']}: {slug_data['slug']}")
    
    # 3. V11 Specific Assessment
    print(f"\n🎯 V11 SPECIFIC ASSESSMENT:")
    print("-" * 25)
    
    # Compare versions for pattern analysis
    print("📈 VERSION COMPARISON:")
    v8_slugs = [s['slug'] for s in version_slugs['v8']]
    v9_slugs = [s['slug'] for s in version_slugs['v9']]
    v10_slugs = [s['slug'] for s in version_slugs['v10']]
    
    all_versions = [('V8', v8_slugs), ('V9', v9_slugs), ('V10', v10_slugs)]
    for version_name, slugs in all_versions:
        if slugs:
            banned_count = sum(1 for slug in slugs if 'ultimate' in slug or 'premium' in slug)
            print(f"{version_name} banned word usage: {banned_count}/{len(slugs)} ({(banned_count/len(slugs)*100):.1f}%)")
    
    print("\n❌ CRITICAL: V11a and V11b prompts DO NOT EXIST in the system!")
    print("❌ CRITICAL: All previous V11 testing was SIMULATED with hardcoded responses!")
    
    return {
        'version_slugs': version_slugs,
        'total_tests': len(results),
        'analysis_complete': True
    }

def save_real_results(results, analysis):
    """Save real API testing results"""
    
    output_data = {
        'test_metadata': {
            'test_type': 'real_api_testing_corrected',
            'timestamp': datetime.now().isoformat(),
            'versions_tested': ['v8', 'v9', 'v10'],
            'critical_finding': 'V11a and V11b do not exist - previous testing was completely simulated',
            'total_cases': len(results)
        },
        'results': results,
        'analysis': analysis
    }
    
    output_file = Path(__file__).parent / 'docs/evolution/results/v11/v11_real_api_results.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Real API results saved to: {output_file}")
    return output_file

if __name__ == "__main__":
    print("🚨 CRITICAL: Fixing V11 Testing - Moving from Simulation to Real API")
    print("=" * 65)
    print()
    
    # Check if we have API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY not found in environment")
        print("Please set your API key in .env file")
        sys.exit(1)
    
    # Load test cases
    test_cases = load_sample_test_cases()
    print(f"📋 Loaded {len(test_cases)} test cases for real API testing")
    print()
    
    # Run real API testing
    results = test_real_v11_api(test_cases)
    
    # Analyze results
    analysis = analyze_real_results(results)
    
    # Save results
    output_file = save_real_results(results, analysis)
    
    print()
    print("🎯 NEXT STEPS:")
    print("1. Review brand intelligence results")
    print("2. Validate V11 pattern elimination claims")  
    print("3. Fix any identified issues with V11 prompts")
    print("4. Re-run comprehensive testing with corrected approach")