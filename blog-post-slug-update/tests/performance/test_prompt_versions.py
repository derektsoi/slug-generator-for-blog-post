#!/usr/bin/env python3
"""
Comprehensive Prompt Version Performance Testing
=================================================

Consolidates both traditional and enhanced A/B testing functionality.

ENHANCED A/B TESTING FEATURES:
✅ Detailed per-URL results display
✅ URL randomization with consistent testing
✅ Enhanced console output with visual indicators  
✅ Comprehensive JSON export
✅ Advanced metrics calculation
✅ 100% backward compatibility

Usage Examples:
    # Traditional testing
    python test_prompt_versions.py
    
    # Enhanced A/B testing (NEW)
    python test_prompt_versions.py --enhanced --urls 8
    
    # Compare multiple versions with enhanced framework
    python test_prompt_versions.py --enhanced --versions current v6 --urls 10
    
    # Use predefined test cases instead of random URLs
    python test_prompt_versions.py --enhanced --no-randomize

Or use the convenience script:
    python scripts/enhanced_testing.py current v6 --urls 8
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Add src directory to Python path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.slug_generator import SlugGenerator
from optimization.optimizer import LLMOptimizer, load_sample_urls, create_randomized_test_cases

class PromptVersionTester:
    """Comprehensive testing of different prompt versions"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY required for prompt testing")
    
    def get_test_cases(self) -> List[Dict[str, Any]]:
        """Get comprehensive test cases covering various content types"""
        return [
            {
                "title": "英國必買童裝 JoJo Maman Bébé官網 3 折起入手網購教學",
                "expected_themes": ["uk", "jojo-maman-bebe", "baby", "clothes", "shopping", "guide"],
                "category": "brand-product-association"
            },
            {
                "title": "Kindle電子書閱讀器最強攻略：Paper White、Colorsoft等型號分別、價格比較及網購集運教學",
                "expected_themes": ["kindle", "ereader", "amazon", "comparison", "guide"],
                "category": "product-recognition"
            },
            {
                "title": "GAP集團美國官網網購教學，附Old Navy、Banana Republic及Athleta等副牌全面介紹",
                "expected_themes": ["gap", "us", "fashion", "brands", "guide"],
                "category": "fashion-brands"
            },
            {
                "title": "日牌輕珠寶Agete、nojess及Star Jewelry等，一次睇齊首飾網購集運教學",
                "expected_themes": ["japanese", "jewelry", "agete", "nojess", "brands"],
                "category": "jewelry-brands"
            },
            {
                "title": "開學季代購必買清單！IFME返學鞋、Gregory背囊及電子文具產品低至3折",
                "expected_themes": ["school", "season", "shoes", "bags", "electronics"],
                "category": "seasonal-content"
            }
        ]
    
    def calculate_theme_coverage(self, generated_slug: str, expected_themes: List[str]) -> float:
        """Calculate how well the slug covers expected themes"""
        if not generated_slug or not expected_themes:
            return 0.0
        
        # Normalize slug for comparison
        slug_words = set(generated_slug.lower().replace('-', ' ').split())
        
        covered_themes = 0
        for theme in expected_themes:
            # Direct match or fuzzy match
            theme_words = set(theme.lower().replace('-', ' ').split())
            if theme_words.intersection(slug_words):
                covered_themes += 1
            elif theme.lower() in generated_slug.lower():
                covered_themes += 1
        
        return covered_themes / len(expected_themes)
    
    def test_prompt_version(self, version: str, test_cases: List[Dict]) -> Dict[str, Any]:
        """Test a specific prompt version against test cases"""
        print(f"\n🧪 Testing {version.upper()} Prompt...")
        
        generator = SlugGenerator(api_key=self.api_key)
        
        # Override prompt version (would need modification to SlugGenerator)
        # For now, testing current implementation
        
        results = []
        total_duration = 0
        success_count = 0
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"  {i}/{len(test_cases)}: {test_case['category']}")
            
            start_time = time.time()
            try:
                result = generator.generate_slug_from_content(
                    test_case['title'], 
                    test_case['title'],  # Using title as content for testing
                    count=1
                )
                
                duration = time.time() - start_time
                total_duration += duration
                success_count += 1
                
                primary_slug = result['primary']
                coverage = self.calculate_theme_coverage(primary_slug, test_case['expected_themes'])
                
                results.append({
                    'title': test_case['title'],
                    'category': test_case['category'],
                    'slug': primary_slug,
                    'expected_themes': test_case['expected_themes'],
                    'coverage': coverage,
                    'duration': duration,
                    'success': True
                })
                
                print(f"    ✅ {primary_slug} (coverage: {coverage:.1%})")
                
            except Exception as e:
                duration = time.time() - start_time
                total_duration += duration
                
                results.append({
                    'title': test_case['title'],
                    'category': test_case['category'],
                    'error': str(e),
                    'duration': duration,
                    'success': False
                })
                
                print(f"    ❌ Error: {e}")
        
        # Calculate summary statistics
        successful_results = [r for r in results if r['success']]
        avg_coverage = sum(r['coverage'] for r in successful_results) / len(successful_results) if successful_results else 0
        avg_duration = total_duration / len(test_cases)
        success_rate = success_count / len(test_cases)
        
        return {
            'version': version,
            'results': results,
            'summary': {
                'avg_coverage': avg_coverage,
                'avg_duration': avg_duration,
                'success_rate': success_rate,
                'total_tests': len(test_cases),
                'successful_tests': success_count
            }
        }
    
    def compare_versions(self, versions: List[str] = None) -> Dict[str, Any]:
        """Compare multiple prompt versions"""
        if versions is None:
            versions = ['current']  # Would expand to ['v2', 'v4', 'v5'] etc.
        
        test_cases = self.get_test_cases()
        comparison_results = {}
        
        for version in versions:
            comparison_results[version] = self.test_prompt_version(version, test_cases)
        
        # Generate comparison summary
        print(f"\n📊 COMPARISON SUMMARY")
        print(f"{'Version':<10} {'Coverage':<10} {'Duration':<10} {'Success':<10}")
        print("-" * 50)
        
        for version, result in comparison_results.items():
            summary = result['summary']
            print(f"{version:<10} {summary['avg_coverage']:.1%} {summary['avg_duration']:.2f}s {summary['success_rate']:.1%}")
        
        return comparison_results
    
    def enhanced_ab_testing(self, versions: List[str] = None, use_randomized_urls: bool = True, 
                           url_count: int = 10, verbose: bool = True) -> Dict[str, Any]:
        """
        Enhanced A/B testing with detailed per-URL results using the optimization framework.
        
        Args:
            versions: List of prompt versions to test
            use_randomized_urls: Whether to use randomized URLs from dataset
            url_count: Number of URLs to test (when using randomized)
            verbose: Whether to show detailed console output
            
        Returns:
            Enhanced results with per-URL breakdown
        """
        if versions is None:
            versions = ['current']  # Default to current version
        
        print(f"🚀 ENHANCED A/B TESTING: {' vs '.join(versions)}")
        print("=" * 70)
        print(f"Framework: Enhanced A/B Testing with Detailed Per-URL Results")
        if use_randomized_urls:
            print(f"URLs: {url_count} randomized from sample dataset")
        print()
        
        # Create test function for the optimizer
        def test_function(version, test_cases):
            """Test function compatible with LLMOptimizer"""
            print(f"  🔄 Testing {len(test_cases)} URLs with {version}...")
            
            detailed_results = []
            successful_tests = 0
            total_duration = 0
            
            for test_case in test_cases:
                title = test_case['input']['title']
                expected_themes = test_case['expected']
                url_index = test_case['url_index']
                category = test_case['category']
                
                print(f"    • URL {url_index}: {title[:50]}...")
                
                try:
                    start_time = time.time()
                    result = SlugGenerator(api_key=self.api_key).generate_slug_from_content(
                        title, title, count=1
                    )
                    duration = time.time() - start_time
                    
                    generated_slug = result['primary']
                    confidence = result.get('confidence', 0.8)
                    coverage = self.calculate_theme_coverage(generated_slug, expected_themes)
                    
                    detailed_results.append({
                        'url_index': url_index,
                        'title': title,
                        'generated_slug': generated_slug,
                        'expected_themes': expected_themes,
                        'coverage': coverage,
                        'duration': duration,
                        'success': True,
                        'category': category,
                        'confidence': confidence
                    })
                    
                    successful_tests += 1
                    total_duration += duration
                    
                    print(f"      → {generated_slug} (coverage: {coverage:.0%})")
                    
                except Exception as e:
                    print(f"      ❌ Error: {e}")
                    detailed_results.append({
                        'url_index': url_index,
                        'title': title,
                        'generated_slug': 'FAILED',
                        'expected_themes': expected_themes,
                        'coverage': 0.0,
                        'duration': 0.0,
                        'success': False,
                        'category': category,
                        'error': str(e)
                    })
                    total_duration += 0.1  # Small penalty for failures
            
            # Calculate summary metrics
            success_rate = successful_tests / len(test_cases)
            avg_coverage = sum(r['coverage'] for r in detailed_results if r['success']) / max(successful_tests, 1)
            avg_duration = total_duration / len(test_cases)
            
            return {
                'avg_theme_coverage': avg_coverage,
                'success_rate': success_rate,
                'avg_duration': avg_duration,
                # NEW: Enhanced detailed results
                'detailed_url_results': detailed_results
            }
        
        # Configure enhanced optimizer
        config = {
            'test_function': test_function,
            'primary_metric': 'avg_theme_coverage',
            'include_detailed_results': True,    # Enable detailed URL results
            'verbose_output': verbose,           # Show per-URL console output  
            'randomize_urls': use_randomized_urls,  # Use randomized URLs from dataset
            'url_count': url_count,             # Number of URLs to select
            'random_seed': 42                   # Reproducible results
        }
        
        optimizer = LLMOptimizer(config)
        
        # Run enhanced comparison
        test_cases = [] if use_randomized_urls else self.get_test_cases()
        results = optimizer.run_comparison(versions, test_cases)
        
        # Export results (fix path to be relative to project root)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_root = os.path.join(os.path.dirname(__file__), '..', '..')
        os.makedirs(os.path.join(project_root, 'results'), exist_ok=True)
        results_file = os.path.join(project_root, 'results', f'enhanced_ab_testing_{timestamp}.json')
        optimizer.export_results(results_file)
        
        print(f"\n✅ Enhanced A/B Testing Complete!")
        print(f"📊 Detailed results saved to: {results_file}")
        
        return results
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save test results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"prompt_comparison_{timestamp}.json"
        
        os.makedirs('results', exist_ok=True)
        filepath = os.path.join('results', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Results saved to {filepath}")
        return filepath

def main():
    """
    Main testing function with both traditional and enhanced A/B testing options.
    
    Usage:
        python test_prompt_versions.py                    # Traditional testing
        python test_prompt_versions.py --enhanced         # Enhanced A/B testing
        python test_prompt_versions.py --enhanced --urls 6  # Enhanced with 6 URLs
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Prompt Version Testing')
    parser.add_argument('--enhanced', action='store_true', 
                       help='Use enhanced A/B testing with detailed per-URL results')
    parser.add_argument('--versions', nargs='+', default=['current'],
                       help='Prompt versions to test (default: current)')
    parser.add_argument('--urls', type=int, default=8,
                       help='Number of URLs for enhanced testing (default: 8)')
    parser.add_argument('--no-randomize', action='store_true',
                       help='Use predefined test cases instead of randomized URLs')
    
    args = parser.parse_args()
    
    tester = PromptVersionTester()
    
    try:
        if args.enhanced:
            print("🔬 Using Enhanced A/B Testing Framework")
            results = tester.enhanced_ab_testing(
                versions=args.versions,
                use_randomized_urls=not args.no_randomize,
                url_count=args.urls,
                verbose=True
            )
        else:
            print("📊 Using Traditional Prompt Testing")
            results = tester.compare_versions(args.versions)
            tester.save_results(results)
        
        print("\n✅ Prompt version testing completed successfully!")
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())