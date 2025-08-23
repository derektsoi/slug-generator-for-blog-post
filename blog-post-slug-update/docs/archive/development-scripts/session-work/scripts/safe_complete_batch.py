#!/usr/bin/env python3
"""
Safe completion script for remaining batch processing
- Uses clean deduplicated results as baseline
- Only processes truly remaining URLs
- Append-only operations (no file overwriting)
- Progress checkpoints every 10 URLs
- Cost tracking and budget limits
"""
import json
import sys
import os
import time
from typing import List, Dict, Set

sys.path.insert(0, 'src')
from core.slug_generator import SlugGenerator

class SafeBatchCompleter:
    def __init__(self, output_dir: str = "batch_8000", max_budget: float = 10.0):
        self.output_dir = output_dir
        self.max_budget = max_budget
        self.current_cost = 0.0
        
        # File paths
        self.clean_results_file = os.path.join(output_dir, "results_clean.jsonl")
        self.final_results_file = os.path.join(output_dir, "results_final.jsonl")
        self.progress_file = os.path.join(output_dir, "safe_progress.json")
        self.remaining_file = os.path.join(output_dir, "remaining_urls.json")
        
        # Initialize slug generator
        self.generator = SlugGenerator()
        
    def load_processed_urls(self) -> Set[str]:
        """Load URLs that have already been processed"""
        processed = set()
        
        if os.path.exists(self.clean_results_file):
            with open(self.clean_results_file, 'r') as f:
                for line in f:
                    if line.strip():
                        result = json.loads(line)
                        processed.add(result.get('original_url', ''))
        
        print(f"✅ Loaded {len(processed)} already processed URLs")
        return processed
    
    def find_remaining_urls(self) -> List[Dict]:
        """Find URLs that still need processing"""
        # Load full dataset
        with open('tests/fixtures/sample_blog_urls.json', 'r') as f:
            all_urls = json.load(f)
        
        processed_urls = self.load_processed_urls()
        
        # Find remaining URLs starting from index 7039
        remaining = []
        for i in range(7039, len(all_urls)):  # Start from our clean resume point
            url_data = all_urls[i]
            if url_data.get('url') not in processed_urls:
                remaining.append({
                    'index': i,
                    'title': url_data.get('title', ''),
                    'url': url_data.get('url', '')
                })
        
        print(f"🔄 Found {len(remaining)} URLs to process (starting from index 7039)")
        
        # Save remaining URLs for debugging
        with open(self.remaining_file, 'w') as f:
            json.dump(remaining, f, indent=2, ensure_ascii=False)
        
        return remaining
    
    def estimate_cost(self, url_count: int) -> float:
        """Estimate processing cost"""
        # Conservative estimate: $0.001 per URL
        return url_count * 0.001
    
    def save_progress(self, processed_count: int, failed_count: int, current_index: int):
        """Save progress checkpoint"""
        progress = {
            'processed_count': processed_count,
            'failed_count': failed_count,
            'current_index': current_index,
            'current_cost': self.current_cost,
            'timestamp': time.time()
        }
        
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
    
    def process_remaining_urls(self) -> Dict:
        """Process all remaining URLs safely"""
        remaining_urls = self.find_remaining_urls()
        
        if not remaining_urls:
            print("🎉 No URLs remaining to process!")
            return {'processed': 0, 'failed': 0, 'cost': 0.0}
        
        # Cost check
        estimated_cost = self.estimate_cost(len(remaining_urls))
        print(f"💰 Estimated cost: ${estimated_cost:.4f} (Budget: ${self.max_budget:.2f})")
        
        if estimated_cost > self.max_budget:
            raise ValueError(f"Estimated cost ${estimated_cost:.4f} exceeds budget ${self.max_budget:.2f}")
        
        # Copy clean results to final results file first
        if os.path.exists(self.clean_results_file) and not os.path.exists(self.final_results_file):
            print("📋 Copying clean results to final results file...")
            with open(self.clean_results_file, 'r') as src:
                with open(self.final_results_file, 'w') as dst:
                    dst.write(src.read())
        
        # Process remaining URLs
        processed_count = 0
        failed_count = 0
        failed_urls = []
        
        print(f"🚀 Starting processing of {len(remaining_urls)} URLs...")
        start_time = time.time()
        
        with open(self.final_results_file, 'a') as results_file:  # Append mode
            for i, url_data in enumerate(remaining_urls):
                try:
                    index = url_data['index']
                    title = url_data['title']
                    url = url_data['url']
                    
                    print(f"Processing {i+1}/{len(remaining_urls)} (Index {index}): {title[:50]}...")
                    
                    # Generate slug
                    result = self.generator.generate_slug_from_content(title, title)
                    
                    # Add metadata
                    result['title'] = title
                    result['original_url'] = url
                    result['quality_issues'] = []
                    result['quality_score'] = 1.0
                    
                    # Write result immediately (append mode)
                    results_file.write(json.dumps(result, ensure_ascii=False) + '\\n')
                    results_file.flush()  # Ensure immediate write
                    
                    processed_count += 1
                    self.current_cost += 0.001  # Update cost tracking
                    
                    # Progress checkpoint every 10 URLs
                    if processed_count % 10 == 0:
                        self.save_progress(processed_count, failed_count, index)
                        elapsed = time.time() - start_time
                        rate = processed_count / elapsed * 60  # per minute
                        eta_minutes = (len(remaining_urls) - processed_count) / (rate / 60)
                        print(f"  ✅ Progress: {processed_count}/{len(remaining_urls)} | Rate: {rate:.1f}/min | ETA: {eta_minutes:.1f}min | Cost: ${self.current_cost:.4f}")
                    
                    # Budget check
                    if self.current_cost > self.max_budget:
                        print(f"💰 Budget limit reached: ${self.current_cost:.4f}")
                        break
                        
                except Exception as e:
                    print(f"❌ Failed: {title[:30]} - {e}")
                    failed_count += 1
                    failed_urls.append({
                        'index': url_data['index'],
                        'url': url,
                        'title': title,
                        'error': str(e)
                    })
                    continue
        
        # Final progress save
        self.save_progress(processed_count, failed_count, 
                          remaining_urls[-1]['index'] if remaining_urls else 7039)
        
        elapsed_time = time.time() - start_time
        
        # Summary
        result = {
            'processed': processed_count,
            'failed': failed_count,
            'total_cost': self.current_cost,
            'elapsed_time': elapsed_time,
            'failed_urls': failed_urls
        }
        
        print(f"\\n🎉 COMPLETION SUMMARY:")
        print(f"✅ Processed: {processed_count} URLs")
        print(f"❌ Failed: {failed_count} URLs")
        print(f"💰 Total cost: ${self.current_cost:.4f}")
        print(f"⏱️  Time taken: {elapsed_time/60:.1f} minutes")
        print(f"📁 Results saved to: {self.final_results_file}")
        
        if failed_urls:
            print(f"\\n❌ Failed URLs:")
            for fail in failed_urls[:5]:  # Show first 5 failures
                print(f"  - Index {fail['index']}: {fail['title'][:50]}... ({fail['error']})")
        
        return result

def main():
    """Main execution function"""
    try:
        # Initialize completer
        completer = SafeBatchCompleter(output_dir="batch_8000", max_budget=10.0)
        
        # Process remaining URLs
        result = completer.process_remaining_urls()
        
        print(f"\\n✅ Safe completion finished successfully!")
        
    except Exception as e:
        print(f"❌ Error during safe completion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()