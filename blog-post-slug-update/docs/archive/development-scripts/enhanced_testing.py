#!/usr/bin/env python3
"""
Convenience script for enhanced A/B testing
Provides easy access to the integrated enhanced testing framework
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tests', 'performance'))

from test_prompt_versions import PromptVersionTester


def main():
    """
    Enhanced A/B Testing Convenience Script
    
    Examples:
        python scripts/enhanced_testing.py                           # Test current version with 6 URLs
        python scripts/enhanced_testing.py v6 v7 --urls 10          # Compare V6 vs V7 with 10 URLs
        python scripts/enhanced_testing.py --help                   # Show all options
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced A/B Testing for Prompt Versions')
    parser.add_argument('versions', nargs='*', default=['current'],
                       help='Prompt versions to test (default: current)')
    parser.add_argument('--urls', type=int, default=6,
                       help='Number of URLs to test (default: 6)')
    parser.add_argument('--no-randomize', action='store_true',
                       help='Use predefined test cases instead of randomized URLs')
    parser.add_argument('--quiet', action='store_true',
                       help='Reduce console output verbosity')
    
    args = parser.parse_args()
    
    print("🚀 ENHANCED A/B TESTING CONVENIENCE SCRIPT")
    print("=" * 50)
    print(f"Testing versions: {', '.join(args.versions)}")
    print(f"URLs: {args.urls} {'(predefined)' if args.no_randomize else '(randomized)'}")
    print()
    
    try:
        tester = PromptVersionTester()
        
        results = tester.enhanced_ab_testing(
            versions=args.versions,
            use_randomized_urls=not args.no_randomize,
            url_count=args.urls,
            verbose=not args.quiet
        )
        
        # Quick summary if testing multiple versions
        if len(args.versions) > 1:
            print("\n📊 QUICK COMPARISON:")
            for version in args.versions:
                if version in results:
                    metrics = results[version]
                    coverage = metrics.get('avg_theme_coverage', 0)
                    success = metrics.get('success_rate', 0)
                    duration = metrics.get('avg_duration', 0)
                    print(f"  {version:15} | Coverage: {coverage:.1%} | Success: {success:.1%} | Duration: {duration:.1f}s")
        
        print(f"\n🎉 Enhanced testing complete!")
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())