#!/usr/bin/env python3
"""
Blog Post Slug Generator CLI
Command-line interface for generating SEO-friendly blog post slugs
"""

import argparse
import sys
import os
import time

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core import SlugGenerator, is_url


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description='Generate SEO-friendly slugs for blog posts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://blog.example.com/my-post
  %(prog)s --count 3 https://blog.example.com/my-post
  %(prog)s --verbose https://blog.example.com/my-post
        """
    )
    
    parser.add_argument(
        'url',
        help='Blog post URL to analyze'
    )
    
    parser.add_argument(
        '--count', '-c',
        type=int,
        default=1,
        help='Number of slug suggestions to generate (default: 1)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output and processing steps'
    )
    
    parser.add_argument(
        '--api-key',
        help='OpenAI API key (overrides environment variable)'
    )
    
    args = parser.parse_args()
    
    # Validate URL
    if not is_url(args.url):
        print(f"Error: Invalid URL format: {args.url}", file=sys.stderr)
        print("Please provide a valid HTTP/HTTPS URL.", file=sys.stderr)
        sys.exit(1)
    
    try:
        if args.verbose:
            print(f"Analyzing URL: {args.url}")
            print("Fetching content...")
        
        # Initialize slug generator
        generator = SlugGenerator(api_key=args.api_key)
        
        if args.verbose:
            print("Generating slug suggestions...")
        
        # Generate slugs
        start_time = time.time()
        result = generator.generate_slug(args.url, count=args.count)
        end_time = time.time()
        
        # Display results
        print("\n" + "="*60)
        print("BLOG POST SLUG SUGGESTIONS")
        print("="*60)
        
        if result.get('title'):
            print(f"Original Title: {result['title']}")
        print(f"URL: {result['url']}")
        print()
        
        print(f"✅ Primary Suggestion: {result['primary']}")
        
        if result.get('alternatives'):
            print("\n🔄 Alternative Suggestions:")
            for i, alt in enumerate(result['alternatives'], 1):
                print(f"   {i}. {alt}")
        
        # Show validation info if verbose
        if args.verbose:
            print(f"\n⚡ Generated in {end_time - start_time:.2f} seconds")
            
            validation = generator.get_slug_validation(result['primary'])
            print(f"\n📊 Validation Details:")
            print(f"   ✅ Valid: {validation['is_valid']}")
            print(f"   📏 Length: {validation['character_count']} characters")
            print(f"   📝 Words: {validation['word_count']} words")
            
            if not validation['is_valid']:
                print(f"   ⚠️  Issues: {', '.join(validation['reasons'])}")
        
        print("\n" + "="*60)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
        
    except Exception as e:
        error_msg = str(e)
        
        if "Invalid URL format" in error_msg:
            print(f"Error: {error_msg}", file=sys.stderr)
            sys.exit(1)
        elif "OpenAI API key" in error_msg:
            print("Error: OpenAI API key is required.", file=sys.stderr)
            print("Set the OPENAI_API_KEY environment variable or use --api-key option.", file=sys.stderr)
            sys.exit(1)
        elif "rate limit" in error_msg.lower():
            print("Error: OpenAI rate limit exceeded. Please try again later.", file=sys.stderr)
            sys.exit(1)
        else:
            if args.verbose:
                import traceback
                traceback.print_exc()
            else:
                print(f"Error: {error_msg}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()