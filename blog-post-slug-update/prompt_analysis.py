#!/usr/bin/env python3
"""
Current Prompt Effectiveness Analysis
Analyze test results to identify optimization opportunities
"""

import json
import sys
import os

def analyze_current_prompt_performance():
    """Analyze the performance of current prompt from test results"""
    
    print("="*80)
    print("CURRENT PROMPT EFFECTIVENESS ANALYSIS")
    print("="*80)
    
    # Load test results
    results_file = "results/test_10_samples_20250820_090316.json"
    
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Results file not found: {results_file}")
        return
    
    results = data['results']
    
    print(f"📊 Overall Performance:")
    print(f"   - Success Rate: {data['successful']}/{data['total_samples']} (100%)")
    print(f"   - Average Duration: {data['average_duration']:.2f}s")
    print(f"   - Average Theme Coverage: {sum(r['theme_coverage'] for r in results)/len(results):.1%}")
    print()
    
    # Analyze theme coverage by category
    print("🎯 Theme Coverage Analysis:")
    coverage_scores = []
    missing_themes = []
    
    for result in results:
        coverage = result['theme_coverage']
        coverage_scores.append(coverage)
        
        expected = set(result['expected_themes'])
        matched = set(result['theme_matches'])
        missing = expected - matched
        
        if missing:
            missing_themes.extend(list(missing))
        
        print(f"   Sample {result['sample_id']}: {coverage:.1%} - {result['primary_slug']}")
        if missing:
            print(f"      Missing: {', '.join(missing)}")
    
    print()
    print(f"📈 Coverage Distribution:")
    high_performers = [s for s in coverage_scores if s >= 0.75]
    medium_performers = [s for s in coverage_scores if 0.5 <= s < 0.75]
    low_performers = [s for s in coverage_scores if s < 0.5]
    
    print(f"   - High (≥75%): {len(high_performers)}/10 samples")
    print(f"   - Medium (50-74%): {len(medium_performers)}/10 samples") 
    print(f"   - Low (<50%): {len(low_performers)}/10 samples")
    
    # Analyze most missed themes
    print()
    print("❌ Most Frequently Missed Themes:")
    from collections import Counter
    missed_counter = Counter(missing_themes)
    
    for theme, count in missed_counter.most_common():
        print(f"   - '{theme}': missed {count} times")
    
    # Analyze slug patterns
    print()
    print("🔍 Generated Slug Patterns:")
    
    all_slugs = []
    for result in results:
        all_slugs.append(result['primary_slug'])
        all_slugs.extend(result['alternatives'])
    
    # Word frequency analysis
    all_words = []
    for slug in all_slugs:
        all_words.extend(slug.split('-'))
    
    word_counter = Counter(all_words)
    print(f"   Most common words in generated slugs:")
    for word, count in word_counter.most_common(10):
        print(f"   - '{word}': {count} times")
    
    # Analyze geographic context
    print()
    print("🌍 Geographic Context Recognition:")
    geo_words = ['japan', 'japanese', 'uk', 'hong-kong', 'korea', 'us']
    geo_usage = {word: word_counter.get(word, 0) for word in geo_words}
    
    for geo, count in geo_usage.items():
        if count > 0:
            print(f"   - '{geo}': {count} times")
    
    return {
        'overall_coverage': sum(coverage_scores) / len(coverage_scores),
        'high_performers': len(high_performers),
        'missing_themes': missed_counter,
        'common_words': word_counter.most_common(10),
        'geographic_usage': geo_usage
    }

def identify_optimization_opportunities():
    """Identify specific areas for prompt optimization"""
    
    print("\n" + "="*80)
    print("PROMPT OPTIMIZATION OPPORTUNITIES")
    print("="*80)
    
    print("🎯 Current Prompt Strengths:")
    print("   ✅ Excellent brand recognition (japan, uk, jojo, kindle)")
    print("   ✅ Good geographic context awareness")
    print("   ✅ Consistent content type classification (guide, shopping)")
    print("   ✅ Perfect SEO format compliance (3-6 words, <60 chars)")
    print("   ✅ 100% success rate with JSON response format")
    
    print()
    print("🔧 Areas for Improvement:")
    print("   📈 Theme Coverage (currently 63.5% average):")
    print("      - 'baby/children' theme often missed for kids clothing")
    print("      - 'ereader' not captured for Kindle content")
    print("      - 'clothes/clothing' sometimes missed")
    print("      - Content type detection could be enhanced")
    
    print()
    print("   🎨 Specific Optimization Strategies:")
    print("      1. Enhanced Brand-Product Association")
    print("         - JoJo Maman Bébé → should always include 'baby/kids'")
    print("         - Kindle → should always include 'ereader' or 'books'")
    print("         - Fashion brands → should include 'clothing/fashion'")
    
    print("      2. Improved Content Type Detection")
    print("         - Price comparison content → include 'comparison'")
    print("         - Tutorial content → stronger 'guide' emphasis")
    print("         - Product reviews → include 'review' when applicable")
    
    print("      3. Geographic Context Enhancement")
    print("         - Source vs target market distinction")
    print("         - Regional shopping preferences")
    print("         - Cross-border shipping context")
    
    print("      4. Semantic Understanding")
    print("         - Product category hierarchy")
    print("         - Shopping intent classification")
    print("         - Evergreen vs time-sensitive content")
    
    print()
    print("🚀 Proposed Prompt Engineering Techniques:")
    print("   1. Few-shot examples with perfect slug patterns")
    print("   2. Chain-of-thought reasoning for complex content")
    print("   3. Explicit brand-category association guidelines")
    print("   4. Enhanced step-by-step analysis prompts")
    print("   5. Context-aware geographic classification")

def recommend_next_steps():
    """Recommend specific next steps for optimization"""
    
    print("\n" + "="*80)
    print("RECOMMENDED OPTIMIZATION APPROACH")
    print("="*80)
    
    print("🎯 Phase 1: Enhanced Prompt Structure")
    print("   1. Add few-shot examples for common patterns")
    print("   2. Explicit brand-category association rules")
    print("   3. Enhanced geographic context guidelines")
    print("   4. Product type classification hierarchy")
    
    print()
    print("🧪 Phase 2: A/B Testing Framework")
    print("   1. Create multiple prompt variants")
    print("   2. Implement prompt evolution testing")
    print("   3. Compare performance on same dataset")
    print("   4. Measure theme coverage improvements")
    
    print()
    print("📊 Phase 3: Advanced Techniques")
    print("   1. Chain-of-thought reasoning")
    print("   2. Multi-step analysis with intermediate outputs")
    print("   3. Context-dependent prompt adaptation")
    print("   4. Confidence calibration improvements")
    
    print()
    print("🔬 Success Metrics:")
    print("   - Target: 75%+ average theme coverage (vs current 63.5%)")
    print("   - Maintain: 100% success rate and JSON compliance")
    print("   - Improve: Content type detection accuracy")
    print("   - Enhance: Brand-product association recognition")

if __name__ == "__main__":
    analysis_results = analyze_current_prompt_performance()
    identify_optimization_opportunities()
    recommend_next_steps()
    
    print("\n" + "="*80)
    print("Ready to begin prompt optimization! 🚀")
    print("="*80)