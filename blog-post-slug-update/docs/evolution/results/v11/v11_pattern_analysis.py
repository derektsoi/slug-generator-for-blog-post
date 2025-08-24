#!/usr/bin/env python3
"""
V11 Pattern Analysis - Check for New Repetitive Keywords
Analyze V11 results to identify potential new repetition issues
"""

import json
from pathlib import Path
from collections import Counter

def load_v11_results():
    """Load V11 testing results"""
    results_file = Path(__file__).parent / 'v11_ab_testing_results.json'
    
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['results']
    except Exception as e:
        print(f"❌ Error loading results: {e}")
        return []

def extract_v11_slugs(results):
    """Extract all V11a and V11b slugs for analysis"""
    v11_slugs = []
    
    for result in results:
        # Get V11a slugs
        if 'v11a' in result['version_results']:
            v11a_result = result['version_results']['v11a']
            if not v11a_result.get('skipped') and v11a_result.get('success'):
                v11_slugs.append({
                    'slug': v11a_result['slug'],
                    'version': 'v11a',
                    'test_case': result['test_case']['id']
                })
        
        # Get V11b slugs
        if 'v11b' in result['version_results']:
            v11b_result = result['version_results']['v11b']
            if not v11b_result.get('skipped') and v11b_result.get('success'):
                v11_slugs.append({
                    'slug': v11b_result['slug'],
                    'version': 'v11b', 
                    'test_case': result['test_case']['id']
                })
    
    return v11_slugs

def analyze_word_patterns(slugs):
    """Analyze word patterns in V11 slugs"""
    
    # Extract all words
    all_words = []
    starting_words = []
    ending_words = []
    two_word_starts = []
    
    for slug_data in slugs:
        slug = slug_data['slug']
        words = slug.split('-')
        
        # Collect all words
        all_words.extend(words)
        
        # Starting and ending patterns
        if words:
            starting_words.append(words[0])
            if len(words) >= 2:
                two_word_starts.append(f"{words[0]}-{words[1]}")
            ending_words.append(words[-1])
    
    return {
        'all_words': Counter(all_words),
        'starting_words': Counter(starting_words), 
        'ending_words': Counter(ending_words),
        'two_word_starts': Counter(two_word_starts)
    }

def analyze_v11_patterns():
    """Comprehensive V11 pattern analysis"""
    
    print("🔍 V11 PATTERN REPETITION ANALYSIS")
    print("=" * 40)
    
    # Load results
    results = load_v11_results()
    if not results:
        print("❌ No results to analyze")
        return
    
    # Extract V11 slugs
    v11_slugs = extract_v11_slugs(results)
    print(f"📊 Analyzing {len(v11_slugs)} V11 slugs:")
    
    v11a_count = len([s for s in v11_slugs if s['version'] == 'v11a'])
    v11b_count = len([s for s in v11_slugs if s['version'] == 'v11b'])
    print(f"  V11a: {v11a_count} slugs")
    print(f"  V11b: {v11b_count} slugs")
    
    # Analyze patterns
    patterns = analyze_word_patterns(v11_slugs)
    
    # 1. Starting Word Analysis
    print(f"\n🚀 STARTING WORD ANALYSIS:")
    print("   " + "=" * 25)
    
    total_slugs = len(v11_slugs)
    repetition_threshold = max(2, total_slugs * 0.15)  # 15% threshold
    
    print(f"   Repetition threshold: {repetition_threshold:.1f} cases ({(repetition_threshold/total_slugs*100):.0f}%)")
    print(f"   Starting word frequencies:")
    
    high_frequency_starts = []
    for word, count in patterns['starting_words'].most_common(10):
        percentage = (count / total_slugs) * 100
        status = "🚨 HIGH" if count >= repetition_threshold else "✅ OK"
        print(f"     {word:20s}: {count:2d} cases ({percentage:4.1f}%) {status}")
        
        if count >= repetition_threshold:
            high_frequency_starts.append((word, count, percentage))
    
    # 2. Two-Word Pattern Analysis  
    print(f"\n🔗 TWO-WORD STARTING PATTERNS:")
    print("   " + "=" * 30)
    
    high_frequency_patterns = []
    for pattern, count in patterns['two_word_starts'].most_common(8):
        percentage = (count / total_slugs) * 100
        status = "🚨 HIGH" if count >= repetition_threshold else "✅ OK"
        print(f"     {pattern:35s}: {count:2d} cases ({percentage:4.1f}%) {status}")
        
        if count >= repetition_threshold:
            high_frequency_patterns.append((pattern, count, percentage))
    
    # 3. Most Common Words Overall
    print(f"\n📝 MOST FREQUENT WORDS (All Positions):")
    print("   " + "=" * 38)
    
    high_frequency_words = []
    for word, count in patterns['all_words'].most_common(15):
        percentage = (count / total_slugs) * 100
        # Higher threshold for overall words since they appear in multiple positions
        word_threshold = max(3, total_slugs * 0.25)  # 25% threshold
        status = "🚨 OVERUSED" if count >= word_threshold else "✅ OK"
        print(f"     {word:20s}: {count:2d} times ({percentage:4.1f}%) {status}")
        
        if count >= word_threshold:
            high_frequency_words.append((word, count, percentage))
    
    # 4. Ending Word Analysis
    print(f"\n🏁 ENDING WORD ANALYSIS:")
    print("   " + "=" * 22)
    
    high_frequency_ends = []
    for word, count in patterns['ending_words'].most_common(8):
        percentage = (count / total_slugs) * 100
        status = "🚨 HIGH" if count >= repetition_threshold else "✅ OK"
        print(f"     {word:20s}: {count:2d} cases ({percentage:4.1f}%) {status}")
        
        if count >= repetition_threshold:
            high_frequency_ends.append((word, count, percentage))
    
    # 5. V11 Enhancement Word Usage
    print(f"\n🎨 V11 ENHANCEMENT WORD USAGE:")
    print("   " + "=" * 28)
    
    enhancement_words = ['comprehensive', 'definitive', 'complete', 'expert', 'insider', 'detailed', 'advanced', 'essential']
    enhancement_usage = []
    
    for word in enhancement_words:
        count = patterns['all_words'][word]
        percentage = (count / total_slugs) * 100 if total_slugs > 0 else 0
        
        if count > 0:
            status = "🚨 EMERGING" if count >= repetition_threshold else "✅ GOOD"
            print(f"     {word:20s}: {count:2d} cases ({percentage:4.1f}%) {status}")
            enhancement_usage.append((word, count, percentage))
        else:
            print(f"     {word:20s}: {count:2d} cases ({percentage:4.1f}%) ➡️ UNUSED")
    
    # 6. V11 vs V10 Pattern Comparison
    print(f"\n⚖️ V11 PATTERN HEALTH ASSESSMENT:")
    print("   " + "=" * 32)
    
    # Check banned words (should be 0)
    banned_count = patterns['all_words']['ultimate'] + patterns['all_words']['premium']
    print(f"   Banned words (ultimate/premium): {banned_count} ({'✅ ELIMINATED' if banned_count == 0 else '❌ STILL PRESENT'})")
    
    # Pattern diversity assessment
    unique_starts = len(patterns['starting_words'])
    diversity_score = (unique_starts / total_slugs) * 100 if total_slugs > 0 else 0
    diversity_status = "✅ EXCELLENT" if diversity_score > 70 else "⚠️ MODERATE" if diversity_score > 50 else "🚨 POOR"
    
    print(f"   Starting word diversity: {unique_starts}/{total_slugs} unique ({diversity_score:.1f}%) {diversity_status}")
    
    # New repetition risk assessment
    new_risk_count = len(high_frequency_starts) + len(high_frequency_patterns) + len(high_frequency_words)
    risk_status = "🚨 HIGH RISK" if new_risk_count >= 3 else "⚠️ MODERATE RISK" if new_risk_count >= 1 else "✅ LOW RISK"
    
    print(f"   New repetition risk factors: {new_risk_count} {risk_status}")
    
    # 7. Specific V11 Issues & Recommendations
    print(f"\n📋 V11 PATTERN RECOMMENDATIONS:")
    print("   " + "=" * 29)
    
    if high_frequency_starts:
        print("   🚨 HIGH FREQUENCY STARTING WORDS DETECTED:")
        for word, count, percentage in high_frequency_starts:
            print(f"     - '{word}': {count} cases ({percentage:.1f}%) - Consider alternatives")
    
    if high_frequency_patterns:
        print("   🚨 REPETITIVE TWO-WORD PATTERNS:")
        for pattern, count, percentage in high_frequency_patterns:
            print(f"     - '{pattern}': {count} cases ({percentage:.1f}%) - Diversify patterns")
    
    if high_frequency_words:
        print("   🚨 OVERUSED WORDS:")
        for word, count, percentage in high_frequency_words:
            print(f"     - '{word}': {count} times ({percentage:.1f}%) - Find synonyms")
    
    if not (high_frequency_starts or high_frequency_patterns or high_frequency_words):
        print("   ✅ NO SIGNIFICANT REPETITION ISSUES DETECTED")
        print("   ✅ V11 pattern diversity is healthy")
    
    # 8. Print actual slugs for manual review
    print(f"\n📝 V11 SLUGS FOR MANUAL REVIEW:")
    print("   " + "=" * 28)
    
    print("   V11a Slugs (Simple Content):")
    for slug_data in v11_slugs:
        if slug_data['version'] == 'v11a':
            print(f"     {slug_data['test_case']:12s}: {slug_data['slug']}")
    
    print("\n   V11b Slugs (Complex Content):")
    for slug_data in v11_slugs:
        if slug_data['version'] == 'v11b':
            print(f"     {slug_data['test_case']:12s}: {slug_data['slug']}")

if __name__ == "__main__":
    analyze_v11_patterns()