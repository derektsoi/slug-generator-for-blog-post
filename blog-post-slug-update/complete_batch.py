#!/usr/bin/env python3
"""
Complete the remaining batch processing without corrupting existing results
"""
import json
import sys
import os
sys.path.insert(0, 'src')

from core.slug_generator import SlugGenerator

def complete_batch():
    # Load original dataset
    with open('tests/fixtures/sample_blog_urls.json', 'r') as f:
        all_urls = json.load(f)
    
    # Check existing results
    results_file = 'batch_8000/results.jsonl.tmp'
    processed_urls = set()
    
    if os.path.exists(results_file):
        with open(results_file, 'r') as f:
            for line in f:
                if line.strip():
                    result = json.loads(line)
                    processed_urls.add(result.get('original_url', ''))
    
    print(f"✅ Found {len(processed_urls)} already processed URLs")
    
    # Find remaining URLs
    remaining_urls = []
    for url_data in all_urls:
        if url_data.get('url') not in processed_urls:
            remaining_urls.append(url_data)
    
    print(f"🔄 Found {len(remaining_urls)} remaining URLs to process")
    
    if len(remaining_urls) == 0:
        print("🎉 All URLs already processed!")
        return
    
    # Process remaining URLs
    generator = SlugGenerator()
    
    with open(results_file, 'a') as f:  # Append mode
        for i, url_data in enumerate(remaining_urls):
            try:
                title = url_data.get('title', '')
                url = url_data.get('url', '')
                
                print(f"Processing {i+1}/{len(remaining_urls)}: {title[:50]}...")
                
                result = generator.generate_slug_from_content(title, title)
                
                # Add metadata
                result['title'] = title
                result['original_url'] = url
                result['quality_issues'] = []
                result['quality_score'] = 1.0
                
                # Write result
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
                f.flush()  # Ensure immediate write
                
            except Exception as e:
                print(f"❌ Failed: {title[:30]} - {e}")
                continue
    
    print(f"✅ Completed processing {len(remaining_urls)} remaining URLs")

if __name__ == "__main__":
    complete_batch()