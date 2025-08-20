#!/usr/bin/env python3
"""
Test script to run SEO generation on 20 sample entries and evaluate results
"""

import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from batch_processor import BatchProcessor
from performance_estimator import PerformanceEstimator

def load_sample_data(count=20):
    """Load sample entries from dataset"""
    dataset_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'blog_urls_dataset.json')
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    return dataset[:count]

def evaluate_seo_quality(results):
    """Evaluate the quality of generated SEO packages"""
    evaluation = {
        'total_entries': len(results),
        'successful_entries': 0,
        'quality_scores': {
            'slugs': {'valid': 0, 'length_ok': 0, 'contains_region': 0},
            'titles': {'valid': 0, 'length_ok': 0, 'contains_region': 0},
            'meta_descriptions': {'valid': 0, 'length_ok': 0, 'compelling': 0}
        },
        'issues': []
    }
    
    for result in results:
        if all(key in result for key in ['slug', 'title', 'meta_description']):
            evaluation['successful_entries'] += 1
            
            # Evaluate slug
            slug = result['slug']
            if slug and isinstance(slug, str):
                evaluation['quality_scores']['slugs']['valid'] += 1
                if len(slug) <= 60:
                    evaluation['quality_scores']['slugs']['length_ok'] += 1
                if result['region'].lower().replace(' ', '-') in slug:
                    evaluation['quality_scores']['slugs']['contains_region'] += 1
            
            # Evaluate title
            title = result['title']
            if title and isinstance(title, str):
                evaluation['quality_scores']['titles']['valid'] += 1
                if len(title) <= 60:
                    evaluation['quality_scores']['titles']['length_ok'] += 1
                if result['region'] in title:
                    evaluation['quality_scores']['titles']['contains_region'] += 1
            
            # Evaluate meta description
            meta = result['meta_description']
            if meta and isinstance(meta, str):
                evaluation['quality_scores']['meta_descriptions']['valid'] += 1
                if len(meta) <= 155:
                    evaluation['quality_scores']['meta_descriptions']['length_ok'] += 1
                if any(word in meta.lower() for word in ['discover', 'shop', 'find', 'get']):
                    evaluation['quality_scores']['meta_descriptions']['compelling'] += 1
        else:
            evaluation['issues'].append(f"Missing fields in result: {result}")
    
    return evaluation

def print_evaluation_report(evaluation, processing_time, cost_estimate):
    """Print detailed evaluation report"""
    total = evaluation['total_entries']
    
    print("\n" + "="*60)
    print("SEO GENERATION EVALUATION REPORT")
    print("="*60)
    
    print(f"\n📊 OVERALL RESULTS:")
    print(f"Total entries processed: {total}")
    print(f"Successful entries: {evaluation['successful_entries']}")
    print(f"Success rate: {evaluation['successful_entries']/total*100:.1f}%")
    print(f"Processing time: {processing_time:.2f} seconds")
    print(f"Estimated cost: ${cost_estimate:.4f}")
    
    print(f"\n🏷️  SLUG QUALITY:")
    slugs = evaluation['quality_scores']['slugs']
    print(f"Valid slugs: {slugs['valid']}/{total} ({slugs['valid']/total*100:.1f}%)")
    print(f"Length compliant: {slugs['length_ok']}/{total} ({slugs['length_ok']/total*100:.1f}%)")
    print(f"Contains region: {slugs['contains_region']}/{total} ({slugs['contains_region']/total*100:.1f}%)")
    
    print(f"\n📝 TITLE QUALITY:")
    titles = evaluation['quality_scores']['titles']
    print(f"Valid titles: {titles['valid']}/{total} ({titles['valid']/total*100:.1f}%)")
    print(f"Length compliant: {titles['length_ok']}/{total} ({titles['length_ok']/total*100:.1f}%)")
    print(f"Contains region: {titles['contains_region']}/{total} ({titles['contains_region']/total*100:.1f}%)")
    
    print(f"\n📄 META DESCRIPTION QUALITY:")
    meta = evaluation['quality_scores']['meta_descriptions']
    print(f"Valid meta descriptions: {meta['valid']}/{total} ({meta['valid']/total*100:.1f}%)")
    print(f"Length compliant: {meta['length_ok']}/{total} ({meta['length_ok']/total*100:.1f}%)")
    print(f"Compelling language: {meta['compelling']}/{total} ({meta['compelling']/total*100:.1f}%)")
    
    if evaluation['issues']:
        print(f"\n⚠️  ISSUES FOUND:")
        for issue in evaluation['issues'][:5]:  # Show first 5 issues
            print(f"- {issue}")

def main():
    """Main execution function"""
    print("Loading 20 sample entries from dataset...")
    sample_data = load_sample_data(20)
    
    print(f"Sample entries loaded: {len(sample_data)}")
    print("\nFirst 3 sample titles:")
    for i, entry in enumerate(sample_data[:3]):
        print(f"{i+1}. {entry['title']}")
    
    # Initialize components
    print("\nInitializing batch processor...")
    processor = BatchProcessor()
    estimator = PerformanceEstimator()
    
    # Test with Hong Kong region only for initial evaluation
    test_region = "Hong Kong"
    
    # Measure processing
    print(f"\nProcessing {len(sample_data)} entries for {test_region}...")
    import time
    start_time = time.time()
    
    try:
        results = processor.process_region_batch(sample_data, test_region)
        processing_time = time.time() - start_time
        
        print(f"Processing completed in {processing_time:.2f} seconds")
        print(f"Results generated: {len(results)}")
        
        # Estimate cost
        cost_estimate = estimator.estimate_processing_cost(len(sample_data), 1)
        
        # Show sample results
        print(f"\n📋 SAMPLE RESULTS (first 3 entries):")
        for i, result in enumerate(results[:3]):
            print(f"\n--- Entry {i+1} ---")
            print(f"Original: {result['original_title'][:80]}...")
            print(f"Slug: {result['slug']}")
            print(f"Title: {result['title']}")
            print(f"Meta: {result['meta_description']}")
        
        # Evaluate quality
        evaluation = evaluate_seo_quality(results)
        print_evaluation_report(evaluation, processing_time, cost_estimate)
        
        # Save results for inspection
        output_file = f"sample_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path = os.path.join('results', output_file)
        os.makedirs('results', exist_ok=True)
        
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'sample_size': len(sample_data),
            'region': test_region,
            'processing_time': processing_time,
            'estimated_cost': cost_estimate,
            'evaluation': evaluation,
            'results': results
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Results saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()