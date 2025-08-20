#!/usr/bin/env python3
"""
V5 Brand-Focused Prompt Test

Test V5 with improved scoring that properly weights brand inclusion.
"""

import sys
import os
import json
import time
import re

sys.path.insert(0, 'src')

from slug_generator import SlugGenerator

def calculate_brand_weighted_score(expected_themes, slug_text, brand_list=None):
    """
    Calculate score with proper brand weighting.
    Brand inclusion gets 2x weight vs other themes.
    """
    if not expected_themes:
        return 1.0
    
    slug_lower = slug_text.lower()
    
    # Define common brand patterns
    common_brands = [
        'jojo-maman-bebe', 'jojo', 'maman', 'bebe',
        'kindle', 'amazon', 'gap', 'rakuten', 'uniqlo', 
        'lululemon', 'nike', 'adidas'
    ]
    
    # Brand detection heuristics
    detected_brands = []
    if brand_list:
        detected_brands.extend(brand_list)
    
    for brand in common_brands:
        if brand in slug_lower:
            detected_brands.append(brand)
    
    # Calculate weighted score
    total_weight = 0
    matched_weight = 0
    
    for theme in expected_themes:
        theme_lower = theme.lower()
        
        # Determine if this theme is brand-related
        is_brand = any(brand in theme_lower for brand in common_brands)
        weight = 2.0 if is_brand else 1.0  # 2x weight for brands
        
        total_weight += weight
        
        # Check for theme match
        if theme_lower in slug_lower:
            matched_weight += weight
        # Fuzzy brand matching
        elif is_brand and any(brand in slug_lower for brand in [theme_lower]):
            matched_weight += weight
    
    # Calculate brand inclusion bonus
    brand_bonus = 0
    if detected_brands and any('brand' in str(expected_themes).lower() or 
                             brand in ' '.join(expected_themes).lower() 
                             for brand in detected_brands):
        brand_bonus = 0.1  # 10% bonus for brand inclusion
    
    if total_weight == 0:
        return 1.0
    
    base_score = matched_weight / total_weight
    final_score = min(1.0, base_score + brand_bonus)
    
    return final_score

def test_prompt_version(prompt_file, test_cases, scoring_method='brand_weighted'):
    """Test prompt with improved brand-weighted scoring"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    generator = SlugGenerator(api_key=api_key)
    generator.confidence_threshold = 0.3
    
    # Override prompt loading
    def load_custom_prompt(prompt_name):
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if "JSON format" not in content:
                content += "\n\nRespond in JSON format with the structure shown above."
            return content
    
    generator._load_prompt = load_custom_prompt
    
    results = []
    successful = 0
    total_score = 0
    
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
            
            # Calculate score based on method
            primary_slug = result['primary']
            all_slugs = [primary_slug] + result.get('alternatives', [])
            slug_text = ' '.join(all_slugs)
            
            if scoring_method == 'brand_weighted':
                score = calculate_brand_weighted_score(expected_themes, slug_text)
            else:
                # Original theme coverage
                expected = set(expected_themes)
                matched = set()
                for theme in expected:
                    if theme.lower() in slug_text.lower():
                        matched.add(theme)
                score = len(matched) / len(expected) if expected else 1.0
            
            total_score += score
            successful += 1
            
            # Brand detection for analysis
            detected_brands = []
            for brand in ['jojo-maman-bebe', 'jojo', 'kindle', 'gap', 'rakuten']:
                if brand in slug_text.lower():
                    detected_brands.append(brand)
            
            results.append({
                'primary': primary_slug,
                'score': score,
                'detected_brands': detected_brands,
                'success': True
            })
            
            brand_indicator = "🏷️" if detected_brands else "⚪"
            print(f"      ✅ {primary_slug} ({score:.1%}) {brand_indicator}")
            
        except Exception as e:
            print(f"      ❌ Error: {str(e)[:50]}...")
            results.append({
                'error': str(e),
                'score': 0.0,
                'success': False
            })
    
    avg_score = total_score / len(test_cases) if test_cases else 0
    success_rate = successful / len(test_cases) if test_cases else 0
    
    return {
        'avg_score': avg_score,
        'success_rate': success_rate,
        'results': results
    }

def main():
    """Test V5 brand-focused prompt vs previous versions"""
    
    print("🏷️ V5 BRAND-FOCUSED PROMPT TEST")
    print("=" * 50)
    print("Testing with improved brand-weighted scoring")
    print()
    
    # Test cases emphasizing brand importance
    test_cases = [
        {
            "title": "英國必買童裝 JoJo Maman Bébé官網購買教學",
            "expected_themes": ["jojo-maman-bebe", "uk", "baby", "clothes", "guide"],
            "category": "brand-product"
        },
        {
            "title": "Amazon美國官網購物完整教學及運送方式",
            "expected_themes": ["amazon", "us", "shopping", "guide"],
            "category": "marketplace-guide"
        },
        {
            "title": "GAP集團美國官網網購教學及副牌介紹",
            "expected_themes": ["gap", "us", "fashion", "brands"],
            "category": "fashion-brands"
        },
        {
            "title": "日本樂天時尚特價購買及集運教學",
            "expected_themes": ["rakuten", "japan", "fashion", "shopping"],
            "category": "marketplace-fashion"
        }
    ]
    
    print(f"🎯 Testing {len(test_cases)} brand-focused scenarios:")
    for i, case in enumerate(test_cases, 1):
        brands_in_themes = [t for t in case['expected_themes'] if any(b in t for b in ['jojo', 'amazon', 'gap', 'rakuten'])]
        print(f"   {i}. {case['category']}: {len(brands_in_themes)} brand themes")
    print()
    
    # Test V2 with new scoring
    print("🧪 V2 Production (Brand-Weighted Scoring)")
    v2_results = test_prompt_version('config/prompts/slug_generation_v2.txt', test_cases, 'brand_weighted')
    print(f"📊 V2: {v2_results['avg_score']:.1%} brand-weighted score, {v2_results['success_rate']:.0%} success")
    print()
    
    # Test V4 with new scoring  
    print("🧪 V4 Previous (Brand-Weighted Scoring)")
    v4_results = test_prompt_version('config/prompts/slug_generation_v4.txt', test_cases, 'brand_weighted')
    print(f"📊 V4: {v4_results['avg_score']:.1%} brand-weighted score, {v4_results['success_rate']:.0%} success")
    print()
    
    # Test V5 brand-focused
    print("🧪 V5 Brand-Focused")
    v5_results = test_prompt_version('config/prompts/slug_generation_v5.txt', test_cases, 'brand_weighted')
    print(f"📊 V5: {v5_results['avg_score']:.1%} brand-weighted score, {v5_results['success_rate']:.0%} success")
    print()
    
    # Compare results
    print("📈 BRAND-WEIGHTED COMPARISON")
    print("=" * 40)
    
    scores = [
        ("V2 Production", v2_results['avg_score']),
        ("V4 Previous", v4_results['avg_score']), 
        ("V5 Brand-Focused", v5_results['avg_score'])
    ]
    
    scores.sort(key=lambda x: x[1], reverse=True)
    
    print("🏆 Brand-Weighted Rankings:")
    for i, (version, score) in enumerate(scores, 1):
        print(f"   {i}. {version}: {score:.1%}")
    print()
    
    # Show brand detection analysis
    print("🏷️ Brand Detection Analysis:")
    for i, case in enumerate(test_cases):
        print(f"   {i+1}. {case['title'][:40]}...")
        
        v2_brands = v2_results['results'][i].get('detected_brands', [])
        v4_brands = v4_results['results'][i].get('detected_brands', [])
        v5_brands = v5_results['results'][i].get('detected_brands', [])
        
        print(f"      V2: {v2_brands or 'No brands'}")
        print(f"      V4: {v4_brands or 'No brands'}")  
        print(f"      V5: {v5_brands or 'No brands'}")
        print()
    
    # Recommendation
    best_version = scores[0][0]
    best_score = scores[0][1]
    
    print(f"🎯 RECOMMENDATION: {best_version}")
    print(f"✓ Achieved {best_score:.1%} brand-weighted performance")
    print("✓ Brand inclusion is critical for cross-border e-commerce SEO")

if __name__ == "__main__":
    main()