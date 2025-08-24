#!/usr/bin/env python3
"""
Analyze repetitive words in 8000+ generated slugs to identify patterns
that should be flagged in the evaluation prompt.
"""

import json
from collections import Counter, defaultdict
from pathlib import Path
import sys

def load_slugs(file_path):
    """Load slugs from JSONL file."""
    slugs = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line.strip())
                    if 'primary' in data:
                        slugs.append(data['primary'])
                except json.JSONDecodeError as e:
                    print(f"Skipping line {line_num}: {e}")
                    continue
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    
    return slugs

def analyze_word_frequency(slugs):
    """Analyze word frequency across all slugs."""
    all_words = []
    first_words = []
    
    for slug in slugs:
        words = slug.split('-')
        all_words.extend(words)
        if words:
            first_words.append(words[0])
    
    total_slugs = len(slugs)
    word_counts = Counter(all_words)
    first_word_counts = Counter(first_words)
    
    return {
        'total_slugs': total_slugs,
        'total_words': len(all_words),
        'unique_words': len(word_counts),
        'word_frequency': word_counts,
        'first_word_frequency': first_word_counts
    }

def analyze_patterns(slugs):
    """Analyze common starting patterns and repetitive structures."""
    pattern_analysis = {
        'starting_patterns': defaultdict(int),
        'ending_patterns': defaultdict(int),
        'common_sequences': defaultdict(int)
    }
    
    for slug in slugs:
        words = slug.split('-')
        
        # Starting patterns (first 2-3 words)
        if len(words) >= 2:
            pattern_analysis['starting_patterns'][f"{words[0]}-{words[1]}"] += 1
        if len(words) >= 3:
            pattern_analysis['starting_patterns'][f"{words[0]}-{words[1]}-{words[2]}"] += 1
            
        # Ending patterns (last 2 words)
        if len(words) >= 2:
            pattern_analysis['ending_patterns'][f"{words[-2]}-{words[-1]}"] += 1
            
        # Common sequences (any 3-word sequence)
        for i in range(len(words) - 2):
            sequence = f"{words[i]}-{words[i+1]}-{words[i+2]}"
            pattern_analysis['common_sequences'][sequence] += 1
    
    return pattern_analysis

def identify_problematic_patterns(analysis, patterns, min_threshold=50):
    """Identify patterns that appear too frequently."""
    problematic = {
        'overused_words': [],
        'repetitive_starters': [],
        'repetitive_endings': [],
        'repetitive_sequences': []
    }
    
    total_slugs = analysis['total_slugs']
    
    # Overused words (appearing in >10% of slugs)
    word_threshold = total_slugs * 0.1
    for word, count in analysis['word_frequency'].most_common(20):
        if count > word_threshold:
            percentage = (count / total_slugs) * 100
            problematic['overused_words'].append({
                'word': word,
                'count': count,
                'percentage': round(percentage, 1)
            })
    
    # Repetitive starters (>5% of slugs)
    starter_threshold = total_slugs * 0.05
    for pattern, count in patterns['starting_patterns'].items():
        if count > starter_threshold:
            percentage = (count / total_slugs) * 100
            problematic['repetitive_starters'].append({
                'pattern': pattern,
                'count': count,
                'percentage': round(percentage, 1)
            })
    
    # Repetitive endings (>3% of slugs)
    ending_threshold = total_slugs * 0.03
    for pattern, count in patterns['ending_patterns'].items():
        if count > ending_threshold:
            percentage = (count / total_slugs) * 100
            problematic['repetitive_endings'].append({
                'pattern': pattern,
                'count': count,
                'percentage': round(percentage, 1)
            })
    
    # Repetitive sequences (>2% of slugs)
    sequence_threshold = total_slugs * 0.02
    for sequence, count in patterns['common_sequences'].items():
        if count > sequence_threshold:
            percentage = (count / total_slugs) * 100
            problematic['repetitive_sequences'].append({
                'sequence': sequence,
                'count': count,
                'percentage': round(percentage, 1)
            })
    
    return problematic

def generate_evaluation_recommendations(problematic):
    """Generate recommendations for evaluation prompt enhancement."""
    recommendations = []
    
    if problematic['overused_words']:
        top_overused = [item['word'] for item in problematic['overused_words'][:5]]
        recommendations.append({
            'issue': 'Overused Words',
            'description': f"Words appearing in >10% of slugs: {', '.join(top_overused)}",
            'evaluation_criteria': 'Flag slugs using these high-frequency terms without clear justification'
        })
    
    if problematic['repetitive_starters']:
        top_starters = [item['pattern'] for item in problematic['repetitive_starters'][:3]]
        recommendations.append({
            'issue': 'Repetitive Starting Patterns',
            'description': f"Common starters: {', '.join(top_starters)}",
            'evaluation_criteria': 'Reduce score for slugs using overused starting patterns'
        })
    
    return recommendations

def main():
    # Path to the results file
    results_file = Path(__file__).parent.parent / "docs/archive/batch-processing-data/batch_data/production/batch_8000/results_clean.jsonl"
    
    print("🔍 Analyzing 8000+ Slugs for Repetitive Patterns...")
    print(f"Loading slugs from: {results_file}")
    
    # Load slugs
    slugs = load_slugs(results_file)
    if not slugs:
        print("❌ No slugs loaded. Check file path.")
        return
    
    print(f"✅ Loaded {len(slugs)} slugs")
    
    # Analyze word frequency
    print("\n📊 Analyzing word frequency...")
    analysis = analyze_word_frequency(slugs)
    
    # Analyze patterns
    print("📊 Analyzing common patterns...")
    patterns = analyze_patterns(slugs)
    
    # Identify problems
    print("🚨 Identifying problematic patterns...")
    problematic = identify_problematic_patterns(analysis, patterns)
    
    # Print results
    print(f"\n" + "="*60)
    print(f"📈 SLUG ANALYSIS RESULTS")
    print(f"="*60)
    print(f"Total Slugs Analyzed: {analysis['total_slugs']:,}")
    print(f"Total Words: {analysis['total_words']:,}")
    print(f"Unique Words: {analysis['unique_words']:,}")
    
    print(f"\n🔴 OVERUSED WORDS (>10% of slugs):")
    for item in problematic['overused_words'][:10]:
        print(f"  • {item['word']}: {item['count']:,} times ({item['percentage']}%)")
    
    print(f"\n🔴 REPETITIVE STARTING PATTERNS (>5% of slugs):")
    for item in sorted(problematic['repetitive_starters'], key=lambda x: x['percentage'], reverse=True)[:10]:
        print(f"  • {item['pattern']}: {item['count']:,} times ({item['percentage']}%)")
    
    print(f"\n🔴 REPETITIVE ENDING PATTERNS (>3% of slugs):")
    for item in sorted(problematic['repetitive_endings'], key=lambda x: x['percentage'], reverse=True)[:10]:
        print(f"  • {item['pattern']}: {item['count']:,} times ({item['percentage']}%)")
    
    print(f"\n🔴 REPETITIVE SEQUENCES (>2% of slugs):")
    for item in sorted(problematic['repetitive_sequences'], key=lambda x: x['percentage'], reverse=True)[:10]:
        print(f"  • {item['sequence']}: {item['count']:,} times ({item['percentage']}%)")
    
    # Generate recommendations
    recommendations = generate_evaluation_recommendations(problematic)
    
    print(f"\n" + "="*60)
    print(f"💡 EVALUATION PROMPT RECOMMENDATIONS")
    print(f"="*60)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['issue']}")
        print(f"   Problem: {rec['description']}")
        print(f"   Solution: {rec['evaluation_criteria']}")
    
    # Save detailed analysis
    output_file = Path(__file__).parent.parent / "docs/analysis/slug_repetition_analysis.json"
    output_file.parent.mkdir(exist_ok=True)
    
    detailed_results = {
        'summary': {
            'total_slugs': analysis['total_slugs'],
            'total_words': analysis['total_words'],
            'unique_words': analysis['unique_words']
        },
        'problematic_patterns': problematic,
        'top_words': dict(analysis['word_frequency'].most_common(50)),
        'top_starting_patterns': dict(Counter(patterns['starting_patterns']).most_common(20)),
        'recommendations': recommendations
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(detailed_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Detailed analysis saved to: {output_file}")
    
if __name__ == "__main__":
    main()