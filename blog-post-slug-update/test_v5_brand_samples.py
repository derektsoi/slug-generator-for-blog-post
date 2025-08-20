#!/usr/bin/env python3
"""
V5 Brand-Focused Test with Brand-Heavy Samples

Target samples with known brands to test brand detection properly.
"""

import sys
import os
import json
import time

sys.path.insert(0, 'src')

from slug_generator import SlugGenerator

def find_brand_samples():
    """Find samples containing major brands from dataset"""
    
    with open('data/blog_urls_dataset.json', 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    brand_samples = []
    
    # Target brands to look for
    target_brands = [
        ('jojo-maman-bebe', ['jojo', 'maman', 'bébé'], ['uk', 'baby', 'clothes', 'guide']),
        ('amazon', ['amazon'], ['us', 'shopping', 'guide']),
        ('gap', ['gap'], ['us', 'fashion', 'brands']),
        ('rakuten', ['rakuten', '樂天'], ['japan', 'fashion', 'shopping']),
        ('kindle', ['kindle'], ['ereader', 'comparison', 'guide']),
        ('verish', ['verish'], ['korea', 'lingerie']),
        ('agete', ['agete'], ['japan', 'jewelry']),
        ('sanrio', ['sanrio'], ['japan', 'toys']),
        ('taylor-swift', ['taylor swift'], ['us', 'music']),
    ]
    
    for item in dataset:
        title_lower = item['title'].lower()
        
        for brand_slug, patterns, other_themes in target_brands:
            if any(pattern in title_lower for pattern in patterns):
                brand_samples.append({
                    'title': item['title'],
                    'expected_themes': [brand_slug] + other_themes,
                    'url': item.get('url', ''),
                    'primary_brand': brand_slug
                })
                break  # Only add once per title
        
        if len(brand_samples) >= 15:  # Limit to manageable number
            break
    
    return brand_samples

def calculate_brand_score(expected_themes, slug_text):
    """Calculate score with heavy brand emphasis"""
    if not expected_themes:
        return 1.0
    
    slug_lower = slug_text.lower()
    
    # Define brand themes (get 3x weight)
    brand_themes = [
        'jojo-maman-bebe', 'amazon', 'gap', 'rakuten', 'kindle', 
        'verish', 'agete', 'sanrio', 'taylor-swift'
    ]
    
    total_weight = 0
    matched_weight = 0
    
    for theme in expected_themes:
        # Brand themes get 3x weight, others get 1x
        is_brand = theme in brand_themes
        weight = 3.0 if is_brand else 1.0
        total_weight += weight
        
        # Check for match (exact or fuzzy)
        theme_parts = theme.split('-')
        if any(part in slug_lower for part in theme_parts) or theme.lower() in slug_lower:
            matched_weight += weight
            if is_brand:
                print(f"      🎯 Brand '{theme}' detected in slug!")
    
    return matched_weight / total_weight if total_weight > 0 else 1.0

def test_version_brands(prompt_file, test_cases, version_name):
    """Test version focusing on brand detection"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    generator = SlugGenerator(api_key=api_key)
    generator.confidence_threshold = 0.2
    
    def load_custom_prompt(prompt_name):
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if "JSON format" not in content:
                content += "\n\nRespond in JSON format."
            return content
    
    generator._load_prompt = load_custom_prompt
    
    results = []
    total_score = 0
    successful = 0
    brand_hits = 0
    
    print(f"🧪 {version_name}")
    print("-" * 50)
    
    for i, case in enumerate(test_cases, 1):
        title = case['title']
        expected_themes = case['expected_themes']
        primary_brand = case.get('primary_brand', 'unknown')
        
        print(f"   {i:2d}. {title[:50]}...")
        print(f"       Expected brand: {primary_brand}")
        
        try:
            result = generator.generate_slug_from_content(title, f"Cross-border shopping guide: {title}", count=1)
            
            primary_slug = result['primary']
            score = calculate_brand_score(expected_themes, primary_slug)
            total_score += score
            successful += 1
            
            # Check if brand detected
            brand_detected = primary_brand.lower() in primary_slug.lower() or any(part in primary_slug.lower() for part in primary_brand.split('-'))
            if brand_detected:
                brand_hits += 1
                print(f"       ✅ {primary_slug} ({score:.0%}) 🏷️ BRAND FOUND")
            else:
                print(f"       ⚠️  {primary_slug} ({score:.0%}) ⚪ No brand")
            
            results.append({
                'slug': primary_slug,
                'score': score, 
                'brand_detected': brand_detected,
                'primary_brand': primary_brand
            })
            
        except Exception as e:
            print(f"       ❌ Failed: {str(e)[:40]}...")
            results.append({
                'slug': None,
                'score': 0.0,
                'brand_detected': False,
                'primary_brand': primary_brand
            })
        
        print()
    
    avg_score = total_score / len(test_cases) if test_cases else 0
    success_rate = successful / len(test_cases) if test_cases else 0
    brand_rate = brand_hits / len(test_cases) if test_cases else 0
    
    print(f"📊 {version_name} Summary:")
    print(f"   Brand-Weighted Score: {avg_score:.1%}")
    print(f"   Success Rate: {success_rate:.0%}")
    print(f"   Brand Detection Rate: {brand_rate:.0%} ({brand_hits}/{len(test_cases)})")
    print()
    
    return {
        'avg_score': avg_score,
        'success_rate': success_rate,
        'brand_detection_rate': brand_rate,
        'brand_hits': brand_hits,
        'results': results
    }

def main():
    """Test V5 vs V2 vs V4 with brand-heavy samples"""
    
    print("🏷️ V5 BRAND-FOCUSED TEST - BRAND-HEAVY SAMPLES")
    print("=" * 60)
    print("Testing with samples containing known brands")
    print()
    
    # Find brand samples
    brand_samples = find_brand_samples()
    
    if len(brand_samples) < 5:
        print("⚠️ Not enough brand samples found in dataset")
        return
    
    # Limit to first 8 for manageable testing
    test_cases = brand_samples[:8]
    
    print(f"📋 Found {len(brand_samples)} brand samples, testing first {len(test_cases)}:")
    for i, case in enumerate(test_cases, 1):
        print(f"   {i}. {case['primary_brand']}: {case['title'][:50]}...")
    print()
    
    # Test all versions
    v2_results = test_version_brands('config/prompts/slug_generation_v2.txt', test_cases, 'V2 Production')
    v4_results = test_version_brands('config/prompts/slug_generation_v4.txt', test_cases, 'V4 Previous')
    v5_results = test_version_brands('config/prompts/slug_generation_v5.txt', test_cases, 'V5 Brand-Focused')
    
    # Final comparison
    print("🏆 BRAND-FOCUSED COMPARISON")
    print("=" * 40)
    
    versions = [
        ("V2 Production", v2_results),
        ("V4 Previous", v4_results),
        ("V5 Brand-Focused", v5_results)
    ]
    
    # Sort by brand detection rate, then by score
    versions.sort(key=lambda x: (x[1]['brand_detection_rate'], x[1]['avg_score']), reverse=True)
    
    print("📊 Rankings (Brand Detection Priority):")
    for i, (name, results) in enumerate(versions, 1):
        print(f"   {i}. {name}:")
        print(f"      Brand Detection: {results['brand_detection_rate']:.0%} ({results['brand_hits']}/{len(test_cases)})")
        print(f"      Weighted Score: {results['avg_score']:.1%}")
        print(f"      Success Rate: {results['success_rate']:.0%}")
        print()
    
    # Key insights
    best_brand_detector = versions[0]
    print("🔍 Brand Detection Analysis:")
    
    if v5_results['brand_detection_rate'] > max(v2_results['brand_detection_rate'], v4_results['brand_detection_rate']):
        print("   ✅ V5 shows superior brand detection")
    elif v2_results['brand_detection_rate'] > v5_results['brand_detection_rate']:
        print("   📝 V2 still leads in brand detection") 
    else:
        print("   🤝 Mixed results - need further analysis")
    
    # Score analysis
    if v5_results['avg_score'] > max(v2_results['avg_score'], v4_results['avg_score']):
        print("   ✅ V5 achieves highest weighted score")
    
    print(f"\n🎯 Best Brand Detector: {best_brand_detector[0][0]}")
    print(f"   Detected {best_brand_detector[1]['brand_hits']}/{len(test_cases)} brands ({best_brand_detector[1]['brand_detection_rate']:.0%})")
    
    # Show specific brand detection examples
    print("\n🏷️ Brand Detection Examples:")
    for i, case in enumerate(test_cases[:3]):
        print(f"   {i+1}. Brand: {case['primary_brand']}")
        print(f"      V2: {v2_results['results'][i].get('slug', 'FAILED')} {'🏷️' if v2_results['results'][i].get('brand_detected') else '⚪'}")
        print(f"      V4: {v4_results['results'][i].get('slug', 'FAILED')} {'🏷️' if v4_results['results'][i].get('brand_detected') else '⚪'}")
        print(f"      V5: {v5_results['results'][i].get('slug', 'FAILED')} {'🏷️' if v5_results['results'][i].get('brand_detected') else '⚪'}")
        print()

if __name__ == "__main__":
    main()