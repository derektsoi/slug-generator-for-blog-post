#!/usr/bin/env python3
"""
Real LLM Optimization Test with Slug Generator

Tests the LLM optimization tool with actual blog URLs and OpenAI API calls
to validate that it works in production conditions.
"""

import sys
import os
import json
import time
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, 'src')

from llm_optimizer.core.optimizer import LLMOptimizer
from slug_generator import SlugGenerator


def create_real_slug_test_function():
    """
    Create a test function that integrates with our actual slug generator.
    
    This tests different prompt versions with real OpenAI API calls.
    """
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable required")
    
    def test_slug_generator_with_prompts(prompt_version, test_cases):
        """Test slug generator with specific prompt version using real API calls"""
        
        print(f"   🧪 Testing {prompt_version} with {len(test_cases)} URLs...")
        
        # Create generator
        generator = SlugGenerator(api_key=api_key, max_retries=2)
        
        # Override prompt loading for specific version
        original_load_prompt = generator._load_prompt
        
        def load_specific_prompt(prompt_name):
            if prompt_version == "current":
                # Use current production prompt (whatever is set as default)
                return original_load_prompt("slug_generation")
            elif prompt_version == "v1_original":
                # Use original v1 prompt
                prompt_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)), 
                    'config', 'prompts', 'slug_generation.txt'
                )
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            elif prompt_version == "v2_optimized":
                # Use optimized v2 prompt but fix JSON format issue
                prompt_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)), 
                    'config', 'prompts', 'slug_generation_v2.txt'
                )
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    # Fix JSON format requirement
                    if "Respond in JSON format:" not in content:
                        content += "\n\nRespond in JSON format with the structure shown above."
                    return content
            else:
                return original_load_prompt(prompt_name)
        
        generator._load_prompt = load_specific_prompt
        
        # Test each URL
        results = []
        total_duration = 0
        successful_tests = 0
        
        for i, test_case in enumerate(test_cases, 1):
            url = test_case['url']
            expected_themes = test_case['expected_themes']
            
            print(f"      {i}. Testing: {url[:60]}...")
            
            try:
                start_time = time.time()
                
                # Generate slug using real API
                result = generator.generate_slug(url, count=2)
                
                duration = time.time() - start_time
                total_duration += duration
                
                # Calculate theme coverage
                expected = set(expected_themes)
                all_slugs = [result['primary']] + result.get('alternatives', [])
                slug_text = ' '.join(all_slugs).lower()
                
                matched = set()
                for theme in expected:
                    if theme.lower() in slug_text:
                        matched.add(theme)
                
                coverage = len(matched) / len(expected) if expected else 1.0
                successful_tests += 1
                
                results.append({
                    'url': url,
                    'primary_slug': result['primary'],
                    'alternatives': result.get('alternatives', []),
                    'theme_coverage': coverage,
                    'matched_themes': list(matched),
                    'expected_themes': expected_themes,
                    'duration': duration,
                    'success': True
                })
                
                print(f"         ✅ {result['primary']} ({coverage:.1%} themes, {duration:.1f}s)")
                
            except Exception as e:
                print(f"         ❌ Error: {str(e)[:50]}...")
                results.append({
                    'url': url,
                    'error': str(e),
                    'theme_coverage': 0.0,
                    'duration': 0.0,
                    'success': False
                })
        
        # Calculate aggregated metrics
        if successful_tests > 0:
            avg_coverage = sum(r['theme_coverage'] for r in results if r['success']) / successful_tests
            success_rate = successful_tests / len(test_cases)
            avg_duration = total_duration / successful_tests
        else:
            avg_coverage = 0.0
            success_rate = 0.0
            avg_duration = 0.0
        
        print(f"      📊 Results: {avg_coverage:.1%} coverage, {success_rate:.0%} success, {avg_duration:.1f}s avg")
        
        return {
            'avg_theme_coverage': avg_coverage,
            'success_rate': success_rate,
            'avg_duration': avg_duration,
            'total_tests': len(test_cases),
            'successful_tests': successful_tests,
            'individual_results': results
        }
    
    return test_slug_generator_with_prompts


def main():
    """Run real optimization test with actual blog URLs"""
    
    print("🔬 REAL LLM OPTIMIZATION TEST")
    print("=" * 80)
    print("Testing slug generator optimization with real URLs and OpenAI API")
    print()
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not found")
        print("Please set your OpenAI API key: export OPENAI_API_KEY=your-key-here")
        return
    
    # Load real test URLs from our dataset
    dataset_path = 'data/blog_urls_dataset.json'
    if not os.path.exists(dataset_path):
        print(f"❌ Error: Dataset not found at {dataset_path}")
        return
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    # Select 10 diverse URLs for testing
    test_cases = [
        {
            "url": "https://www.buyandship.today/blog/2025/08/18/%e6%97%a5%e6%9c%ac%e8%bc%95%e7%8f%a0%e5%af%b6%e5%93%81%e7%89%8c%e5%90%88%e9%9b%86/",
            "title": "8大日牌輕珠寶品牌一次睇！Agete、nojess及Star Jewelry等日劇女主御用明星珠寶",
            "expected_themes": ["japanese", "jewelry", "brands", "guide"]
        },
        {
            "url": "https://www.buyandship.today/blog/2025/08/18/jojo-maman-bebe%e8%8b%b1%e5%9c%8b%e5%ae%98%e7%b6%b2%e6%8a%98%e6%89%a3%e5%8f%8a%e8%b3%bc%e8%b2%b7%e6%95%99%e5%ad%b8/",
            "title": "英國必買童裝 JoJo Maman Bébé官網 3 折起入手網購教學",
            "expected_themes": ["uk", "baby", "clothes", "shopping", "guide"]
        },
        {
            "url": "https://www.buyandship.today/blog/2025/08/18/verish%e9%9f%93%e5%83%b9%e5%b7%ae%e5%a4%a7%e6%af%94%e6%8b%bc/",
            "title": "Verish內衣品牌港韓價差大比拼！人氣Cool-Fit無鋼圈、運動系列必買推介",
            "expected_themes": ["korean", "underwear", "comparison", "hong-kong"]
        },
        {
            "url": "https://www.buyandship.today/blog/2025/08/17/kindle-amazon%e9%9b%bb%e5%ad%90%e6%9b%b8%e5%85%a8%e6%94%bb%e7%95%a5/",
            "title": "Kindle電子書閱讀器最強攻略：Paper White、Colorsoft等型號分別、價格比較及網購集運教學",
            "expected_themes": ["kindle", "ereader", "amazon", "comparison", "guide"]
        },
        {
            "url": "https://www.buyandship.today/blog/2025/08/17/%e9%96%8b%e5%ad%b8%e5%ad%a3%e4%bb%a3%e8%b3%bc%e5%bf%85%e8%b2%b7%e6%b8%85%e5%96%ae/",
            "title": "開學季代購必買清單！IFME返學鞋、Gregory背囊及電子文具產品低至3折",
            "expected_themes": ["school", "season", "shoes", "bags", "sale"]
        }
    ]
    
    print(f"📊 Selected {len(test_cases)} URLs for optimization testing:")
    for i, case in enumerate(test_cases, 1):
        print(f"   {i}. {case['title'][:50]}... ({len(case['expected_themes'])} themes)")
    print()
    
    # Configure optimizer with real test function
    config = {
        'test_function': create_real_slug_test_function(),
        'metrics': ['avg_theme_coverage', 'success_rate', 'avg_duration'],
        'primary_metric': 'avg_theme_coverage',
        'confidence_threshold': 0.7
    }
    
    optimizer = LLMOptimizer(config)
    
    # Run optimization across prompt versions
    print("🧪 Running Real Optimization Test")
    print("-" * 50)
    
    # Test current production vs original baseline
    prompt_versions = ['current', 'v1_original']
    
    try:
        results = optimizer.run_comparison(prompt_versions, test_cases)
        
        # Analyze results
        print("\n📊 REAL OPTIMIZATION RESULTS")
        print("=" * 60)
        
        best_version = optimizer.get_best_version()
        ranking = optimizer.get_ranking()
        
        print(f"🏆 Best Version: {best_version}")
        print(f"📈 Performance Ranking: {' > '.join(ranking)}")
        print()
        
        # Show detailed metrics
        for version in ranking:
            if version in results and 'error' not in results[version]:
                metrics = results[version]
                print(f"   {version}: {metrics['avg_theme_coverage']:.1%} coverage, "
                      f"{metrics['success_rate']:.0%} success, "
                      f"{metrics['avg_duration']:.1f}s avg "
                      f"({metrics['successful_tests']}/{metrics['total_tests']} successful)")
            else:
                print(f"   {version}: ❌ Failed")
        print()
        
        # Calculate improvement
        if len(ranking) >= 2 and all(v in results for v in ranking[:2]):
            best_coverage = results[ranking[0]]['avg_theme_coverage']
            baseline_coverage = results[ranking[1]]['avg_theme_coverage']
            improvement = (best_coverage - baseline_coverage) * 100
            
            print(f"📈 Real Improvement: +{improvement:.1f}% theme coverage")
            print()
        
        # Generate insights
        insights = optimizer.generate_insights()
        
        print("💡 OPTIMIZATION INSIGHTS")
        print("=" * 40)
        
        print("📋 Recommendations:")
        for i, rec in enumerate(insights['recommendations'], 1):
            print(f"   {i}. {rec}")
        print()
        
        # Show some example results
        print("🎯 Example Results:")
        for version in ['v1', 'v2']:
            if version in results and 'individual_results' in results[version]:
                version_results = results[version]['individual_results']
                successful_results = [r for r in version_results if r['success']]
                
                if successful_results:
                    print(f"   {version} examples:")
                    for result in successful_results[:2]:  # Show first 2 examples
                        matched_pct = len(result['matched_themes']) / len(result['expected_themes']) * 100
                        print(f"      • {result['primary_slug']} ({matched_pct:.0f}% themes)")
                    print()
        
        # Export results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"results/real_optimization_test_{timestamp}.json"
        
        os.makedirs('results', exist_ok=True)
        optimizer.export_results(results_file)
        
        print("✅ REAL OPTIMIZATION TEST COMPLETE")
        print("=" * 60)
        print(f"✓ Successfully tested with real URLs and OpenAI API")
        print(f"✓ Validated optimization tool with production data")
        print(f"✓ Results exported to: {results_file}")
        
        # Validate against expected results
        if 'v2' in results and 'v1' in results:
            v2_coverage = results['v2']['avg_theme_coverage']
            v1_coverage = results['v1']['avg_theme_coverage']
            
            if v2_coverage > v1_coverage:
                print(f"✓ Confirmed: V2 outperforms V1 ({v2_coverage:.1%} vs {v1_coverage:.1%})")
            else:
                print(f"⚠️  Unexpected: V1 performed better than V2")
        
    except Exception as e:
        print(f"\n❌ Optimization test failed: {e}")
        print("This could be due to:")
        print("  • API rate limits or network issues")
        print("  • Invalid URLs in test dataset")  
        print("  • OpenAI API key issues")
        return


if __name__ == "__main__":
    main()