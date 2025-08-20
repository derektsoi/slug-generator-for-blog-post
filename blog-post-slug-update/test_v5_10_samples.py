#!/usr/bin/env python3
"""
V5 Brand-Focused Test with 10 Random Samples

Quick validation with diverse samples from the blog dataset.
"""

import sys
import os
import json
import time
import random

sys.path.insert(0, 'src')

from slug_generator import SlugGenerator

def extract_expected_themes(title):
    """Extract expected themes focusing on brands, products, geography"""
    title_lower = title.lower()
    themes = []
    
    # Brand detection (most important)
    brands = {
        'jojo-maman-bebe': ['jojo', 'maman', 'bébé'],
        'amazon': ['amazon'],
        'gap': ['gap'], 
        'rakuten': ['rakuten', '樂天'],
        'kindle': ['kindle'],
        'verish': ['verish'],
        'agete': ['agete'],
        'sanrio': ['sanrio'],
        'ifme': ['ifme'],
        'gregory': ['gregory'],
        'taylor-swift': ['taylor swift']
    }
    
    for brand, patterns in brands.items():
        if any(p in title_lower for p in patterns):
            themes.append(brand)
            break
    
    # Geography
    if any(x in title_lower for x in ['日本', '日牌']):
        themes.append('japan')
    elif any(x in title_lower for x in ['英國', 'uk']):
        themes.append('uk') 
    elif any(x in title_lower for x in ['美國', 'usa']):
        themes.append('us')
    elif any(x in title_lower for x in ['韓國', 'korean']):
        themes.append('korea')
    
    # Product categories
    if any(x in title_lower for x in ['珠寶', 'jewelry']):
        themes.append('jewelry')
    elif any(x in title_lower for x in ['童裝', 'baby', '童']):
        themes.append('kids')
    elif any(x in title_lower for x in ['內衣', 'lingerie']):
        themes.append('lingerie')
    elif any(x in title_lower for x in ['電子書', 'ereader']):
        themes.append('ereader')
    elif any(x in title_lower for x in ['時尚', 'fashion']):
        themes.append('fashion')
    elif any(x in title_lower for x in ['零食', 'snacks']):
        themes.append('snacks')
    
    # Content type
    if any(x in title_lower for x in ['教學', 'guide']):
        themes.append('guide')
    elif any(x in title_lower for x in ['比較', 'comparison']):
        themes.append('comparison')
    
    return themes[:4]  # Max 4 themes

def calculate_brand_score(expected_themes, slug_text):
    """Calculate score with heavy brand weighting"""
    if not expected_themes:
        return 1.0
    
    slug_lower = slug_text.lower()
    brand_themes = ['jojo-maman-bebe', 'amazon', 'gap', 'rakuten', 'kindle', 'verish', 'agete', 'sanrio', 'ifme', 'gregory', 'taylor-swift']
    
    total_weight = 0
    matched_weight = 0
    
    for theme in expected_themes:
        # Brand themes get 3x weight
        weight = 3.0 if theme in brand_themes else 1.0
        total_weight += weight
        
        # Check match
        if theme.lower() in slug_lower or any(part in slug_lower for part in theme.split('-')):
            matched_weight += weight
    
    return matched_weight / total_weight if total_weight > 0 else 1.0

def test_version_quick(prompt_file, test_cases, version_name):
    """Quick test with focus on speed and brand detection"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    generator = SlugGenerator(api_key=api_key)
    generator.confidence_threshold = 0.2  # Lower for speed
    
    def load_custom_prompt(prompt_name):
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    generator._load_prompt = load_custom_prompt
    
    results = []
    total_score = 0
    successful = 0
    brands_found = 0
    
    print(f"🧪 {version_name}")
    
    for i, case in enumerate(test_cases, 1):
        title = case['title']
        expected_themes = case['expected_themes']
        
        print(f"   {i:2d}. {title[:45]}...")
        
        try:
            result = generator.generate_slug_from_content(title, f"Content: {title}", count=1)
            
            primary_slug = result['primary']
            score = calculate_brand_score(expected_themes, primary_slug)
            total_score += score
            successful += 1
            
            # Check for brand
            has_brand = any(brand in primary_slug.lower() for brand in ['jojo', 'amazon', 'gap', 'rakuten', 'kindle', 'verish', 'agete', 'sanrio'])
            if has_brand:
                brands_found += 1
            
            brand_icon = "🏷️" if has_brand else "⚪"
            print(f"      ✅ {primary_slug} ({score:.0%}) {brand_icon}")
            
            results.append({'slug': primary_slug, 'score': score, 'has_brand': has_brand})
            
        except Exception as e:
            print(f"      ❌ Failed: {str(e)[:30]}...")
            results.append({'slug': None, 'score': 0.0, 'has_brand': False})
    
    avg_score = total_score / len(test_cases) if test_cases else 0
    success_rate = successful / len(test_cases) if test_cases else 0
    brand_rate = brands_found / len(test_cases) if test_cases else 0
    
    print(f"   📊 {avg_score:.1%} score, {success_rate:.0%} success, {brand_rate:.0%} brands\n")
    
    return {
        'avg_score': avg_score,
        'success_rate': success_rate, 
        'brand_rate': brand_rate,
        'results': results
    }

def main():
    """Quick V5 validation test"""
    
    print("🎯 V5 BRAND-FOCUSED VALIDATION - 10 SAMPLES")
    print("=" * 55)
    
    # Load random samples
    with open('data/blog_urls_dataset.json', 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    random.seed(42)
    samples = random.sample(dataset, 10)
    
    test_cases = []
    for item in samples:
        themes = extract_expected_themes(item['title'])
        test_cases.append({
            'title': item['title'],
            'expected_themes': themes
        })
    
    # Count brand samples
    brand_samples = sum(1 for case in test_cases if any(t in ['jojo-maman-bebe', 'amazon', 'gap', 'rakuten', 'kindle'] for t in case['expected_themes']))
    print(f"📋 Testing 10 samples ({brand_samples} with brands)\n")
    
    # Test versions
    v2_results = test_version_quick('config/prompts/slug_generation_v2.txt', test_cases, 'V2 Production')
    v4_results = test_version_quick('config/prompts/slug_generation_v4.txt', test_cases, 'V4 Previous')
    v5_results = test_version_quick('config/prompts/slug_generation_v5.txt', test_cases, 'V5 Brand-Focused')
    
    # Results
    print("🏆 QUICK VALIDATION RESULTS")
    print("=" * 35)
    
    versions = [
        ("V2", v2_results['avg_score'], v2_results['brand_rate']),
        ("V4", v4_results['avg_score'], v4_results['brand_rate']),
        ("V5", v5_results['avg_score'], v5_results['brand_rate'])
    ]
    
    versions.sort(key=lambda x: x[1], reverse=True)
    
    for i, (name, score, brands) in enumerate(versions, 1):
        print(f"   {i}. {name}: {score:.1%} score, {brands:.0%} brands")
    
    print()
    
    # Key findings
    if v5_results['avg_score'] > v2_results['avg_score']:
        improvement = (v5_results['avg_score'] - v2_results['avg_score']) * 100
        print(f"✅ V5 improves over V2: +{improvement:.1f}%")
    else:
        gap = (v2_results['avg_score'] - v5_results['avg_score']) * 100
        print(f"📝 V2 still ahead: +{gap:.1f}%")
    
    if v5_results['brand_rate'] >= max(v2_results['brand_rate'], v4_results['brand_rate']):
        print("🏷️ V5 matches/exceeds brand detection")
    else:
        print("⚠️ V5 brand detection needs improvement")
    
    print(f"\n🎯 Winner: {versions[0][0]} with {versions[0][1]:.1%} brand-weighted score")

if __name__ == "__main__":
    main()