#!/usr/bin/env python3
"""
Production batch processing script for blog post slug generation.
Processes URLs from sample_blog_urls.json with checkpointing and resume capability.
"""

import os
import sys
import json
import argparse
import subprocess
import threading
import time
from datetime import datetime
from typing import List, Dict

# Add src to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(script_dir), 'src')
sys.path.insert(0, src_dir)

from extensions.production_batch_processor import ProductionBatchProcessor


def monitor_progress(output_dir: str, total_urls: int, verbose: bool = False, stop_event=None):
    """Monitor processing progress in real-time."""
    results_file = os.path.join(output_dir, 'results.jsonl')
    progress_file = os.path.join(output_dir, 'batch_progress.json')
    
    last_count = 0
    start_time = time.time()
    
    print(f"\n📊 LIVE PROGRESS MONITORING (Press Ctrl+C to stop)")
    print("=" * 50)
    
    while not (stop_event and stop_event.is_set()):
        try:
            # Read real-time progress from live progress file
            current_count = 0
            failed_count = 0
            current_cost = 0.0
            
            # Try reading from live progress file first (real-time data)
            live_progress_file = os.path.join(output_dir, 'live_progress.json')
            if os.path.exists(live_progress_file):
                try:
                    with open(live_progress_file, 'r') as f:
                        live_progress = json.load(f)
                        current_count = live_progress.get('processed', 0)
                        failed_count = live_progress.get('failed', 0)
                except:
                    pass
            
            # Read cost from batch progress file
            if os.path.exists(progress_file):
                try:
                    with open(progress_file, 'r') as f:
                        progress = json.load(f)
                        current_cost = progress.get('current_cost', 0.0)
                except:
                    pass
            
            # Fallback: count results file if no live progress
            if current_count == 0 and os.path.exists(results_file):
                with open(results_file, 'r') as f:
                    current_count = sum(1 for _ in f)
            
            if current_count != last_count or current_count == 0:
                elapsed = time.time() - start_time
                rate = current_count / elapsed if elapsed > 0 else 0
                eta_seconds = (total_urls - current_count) / rate if rate > 0 else 0
                eta_hours = eta_seconds / 3600
                
                # Progress bar
                progress_pct = (current_count / total_urls) * 100 if total_urls > 0 else 0
                bar_length = 30
                filled_length = int(bar_length * current_count / total_urls) if total_urls > 0 else 0
                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                
                print(f"\r🔄 Progress: [{bar}] {current_count}/{total_urls} ({progress_pct:.1f}%)", end="")
                
                if verbose or current_count != last_count:
                    print(f"\n   ⏱️  Elapsed: {elapsed/60:.1f}min | Rate: {rate:.2f}/min | ETA: {eta_hours:.1f}h")
                    print(f"   💰 Cost: ${current_cost:.4f} | ❌ Failed: {failed_count}")
                    if not verbose:
                        print("", end="", flush=True)  # Return to progress line
                
                last_count = current_count
            
            time.sleep(5)  # Update every 5 seconds
            
        except KeyboardInterrupt:
            print(f"\n⏸️  Progress monitoring stopped by user")
            break
        except Exception as e:
            if verbose:
                print(f"\n⚠️  Progress monitoring error: {e}")
            time.sleep(10)  # Wait longer on error


def run_with_caffeinate(command_args: List[str], prevent_sleep: bool = True) -> int:
    """Run command with caffeinate to prevent sleep."""
    if prevent_sleep and sys.platform == 'darwin':  # macOS only
        print("🌙 Preventing Mac from sleeping during processing...")
        caffeinate_cmd = ['caffeinate', '-s'] + command_args
        return subprocess.run(caffeinate_cmd).returncode
    else:
        return subprocess.run(command_args).returncode


def load_urls_from_json(file_path: str, limit: int = None) -> List[Dict]:
    """Load URLs from JSON file with optional limit."""
    print(f"Loading URLs from: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        urls = json.load(f)
    
    if limit:
        urls = urls[:limit]
        print(f"Limited to first {limit} URLs")
    
    print(f"Total URLs to process: {len(urls)}")
    return urls


def estimate_costs_and_time(url_count: int):
    """Estimate processing costs and time."""
    # Based on gpt-4o-mini pricing: ~$0.15 per 1K input tokens, ~$0.60 per 1K output tokens
    # Estimated ~500 input tokens + ~50 output tokens per request
    cost_per_request = 0.0008  # Conservative estimate
    total_cost = url_count * cost_per_request
    
    # Estimated 5 seconds per request average
    total_time_seconds = url_count * 5
    total_time_minutes = total_time_seconds / 60
    total_time_hours = total_time_minutes / 60
    
    print(f"\n=== COST & TIME ESTIMATES ===")
    print(f"URLs to process: {url_count:,}")
    print(f"Estimated cost: ${total_cost:.2f}")
    print(f"Estimated time: {total_time_hours:.1f} hours ({total_time_minutes:.0f} minutes)")
    print(f"Processing rate: ~5 seconds per URL")
    print("=" * 30)
    
    return total_cost, total_time_hours


def main():
    parser = argparse.ArgumentParser(description="Production batch processing for blog post slugs")
    parser.add_argument('--count', type=int, default=100, 
                       help='Number of URLs to process (default: 100)')
    parser.add_argument('--resume', action='store_true', 
                       help='Resume from previous checkpoint')
    parser.add_argument('--budget', type=float, default=50.0, 
                       help='Maximum budget in USD (default: $50)')
    parser.add_argument('--batch-size', type=int, default=50, 
                       help='Batch size for processing (default: 50)')
    parser.add_argument('--checkpoint-interval', type=int, default=100, 
                       help='Save checkpoint every N URLs (default: 100)')
    parser.add_argument('--output-dir', type=str, default='./batch_results', 
                       help='Output directory for results (default: ./batch_results)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show estimates without processing')
    parser.add_argument('--prevent-sleep', action='store_true', default=True,
                       help='Prevent Mac from sleeping during processing (default: True)')
    parser.add_argument('--verbose', action='store_true',
                       help='Show detailed progress information')
    
    args = parser.parse_args()
    
    # File paths
    fixtures_dir = os.path.join(os.path.dirname(script_dir), 'tests', 'fixtures')
    urls_file = os.path.join(fixtures_dir, 'sample_blog_urls.json')
    
    if not os.path.exists(urls_file):
        print(f"Error: URLs file not found at {urls_file}")
        return 1
    
    # Load URLs
    try:
        urls = load_urls_from_json(urls_file, args.count)
    except Exception as e:
        print(f"Error loading URLs: {e}")
        return 1
    
    # Show estimates
    estimated_cost, estimated_hours = estimate_costs_and_time(len(urls))
    
    if estimated_cost > args.budget:
        print(f"\n⚠️  WARNING: Estimated cost (${estimated_cost:.2f}) exceeds budget (${args.budget:.2f})")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return 0
    
    if args.dry_run:
        print("\n🔍 DRY RUN - No actual processing performed")
        return 0
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize processor
    print(f"\n🚀 Starting production batch processing...")
    print(f"Output directory: {args.output_dir}")
    print(f"Resume mode: {'ON' if args.resume else 'OFF'}")
    if args.prevent_sleep:
        print(f"🌙 Sleep prevention: ON")
    
    processor = ProductionBatchProcessor(
        batch_size=args.batch_size,
        max_budget=args.budget,
        checkpoint_interval=args.checkpoint_interval,
        output_dir=args.output_dir
    )
    
    try:
        # Start progress monitoring in background thread
        stop_event = threading.Event()
        progress_thread = threading.Thread(
            target=monitor_progress, 
            args=(args.output_dir, len(urls), args.verbose, stop_event),
            daemon=True
        )
        progress_thread.start()
        
        # Small delay to let progress monitoring start
        time.sleep(2)
        
        # Run processing
        start_time = datetime.now()
        result = processor.process_urls_production(urls, resume=args.resume)
        end_time = datetime.now()
        
        # Stop progress monitoring
        stop_event.set()
        
        # Print results
        print(f"\n✅ PROCESSING COMPLETE")
        print(f"Time taken: {end_time - start_time}")
        print(f"URLs processed: {result['processing_stats']['processed']}")
        print(f"Success count: {len(result['successful_results'])}")
        print(f"Failed count: {result['processing_stats']['failed']}")
        
        total_processed = result['processing_stats']['processed']
        success_count = len(result['successful_results'])
        if total_processed > 0:
            success_rate = success_count / total_processed
            print(f"Success rate: {success_rate:.1%}")
        
        print(f"Total cost: ${result['total_cost']:.4f}")
        
        if result['processing_stats']['failed'] > 0:
            print(f"⚠️  Failed: {result['processing_stats']['failed']} URLs")
            if result['failed_urls']:
                print("Failed URLs:")
                for failed in result['failed_urls'][:3]:  # Show first 3
                    print(f"  - {failed.get('error', 'Unknown error')}")
                if len(result['failed_urls']) > 3:
                    print(f"  ... and {len(result['failed_urls']) - 3} more")
        
        print(f"\nResults saved to: {args.output_dir}")
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n⏸️  Processing interrupted by user")
        print(f"Checkpoint saved. Use --resume to continue from where you left off.")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        print(f"Check checkpoint files in {args.output_dir} for resume capability")
        return 1


if __name__ == "__main__":
    # Check if we should run with caffeinate
    if len(sys.argv) > 1 and '--prevent-sleep' in sys.argv and '--dry-run' not in sys.argv:
        # Run with caffeinate
        try:
            script_path = os.path.abspath(__file__)
            python_path = sys.executable
            
            # Rebuild args without prevent-sleep (avoid recursion)
            filtered_args = [arg for arg in sys.argv[1:] if arg != '--prevent-sleep']
            
            cmd = [python_path, script_path] + filtered_args
            print("🌙 Running with caffeinate to prevent Mac sleep...")
            result = subprocess.run(['caffeinate', '-s'] + cmd)
            exit(result.returncode)
            
        except KeyboardInterrupt:
            print(f"\n⏸️  Processing interrupted by user")
            exit(0)
        except Exception as e:
            print(f"❌ Error with caffeinate: {e}")
            print("🔄 Falling back to normal execution...")
    
    exit(main())