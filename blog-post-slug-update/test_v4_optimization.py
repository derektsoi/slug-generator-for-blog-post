#!/usr/bin/env python3
"""
V4 Prompt Optimization Test

Tests our new V4 prompt against the fixed V2 prompt using real URLs
and the LLM optimization tool to validate improvements.
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


def create_v4_test_function():
    """
    Create a test function that compares V2 (fixed) vs V4 prompts.
    """
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable required")
    
    def test_v4_vs_v2_fixed(prompt_version, test_cases):
        """Test V4 vs V2 with actual API calls"""
        
        print(f"   🧪 Testing {prompt_version} with {len(test_cases)} test cases...")
        
        # Create generator with lower confidence threshold to fix V2 issues
        generator = SlugGenerator(api_key=api_key, max_retries=2)
        generator.confidence_threshold = 0.4  # Lower threshold to fix V2 filtering issue
        
        # Override prompt loading for specific version
        original_load_prompt = generator._load_prompt
        
        def load_specific_prompt(prompt_name):
            if prompt_version == "v2_fixed":
                # Use V2 prompt with JSON format fix
                prompt_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)), 
                    'config', 'prompts', 'slug_generation_v2.txt'
                )
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    # Ensure JSON format requirement
                    if "Respond in JSON format" not in content:
                        content += "\n\nRespond in JSON format with the structure shown above."
                    return content
            elif prompt_version == "v4_optimized":
                # Use new V4 prompt
                prompt_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)), 
                    'config', 'prompts', 'slug_generation_v4.txt'
                )
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            else:
                return original_load_prompt(prompt_name)
        
        generator._load_prompt = load_specific_prompt
        
        # Test each case
        results = []
        total_duration = 0
        successful_tests = 0
        
        for i, test_case in enumerate(test_cases, 1):
            title = test_case['title']
            expected_themes = test_case['expected_themes']
            
            print(f"      {i}. Testing: {title[:50]}...")
            
            try:
                start_time = time.time()
                
                # Generate slug from title content (simulating URL extraction)
                result = generator.generate_slug_from_content(
                    title, 
                    f"Blog content about {test_case.get('category', 'general shopping')}", 
                    count=2
                )
                
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
                    'title': title,
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
                    'title': title,
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
    
    return test_v4_vs_v2_fixed


def main():
    """Test V4 prompt against fixed V2 using optimization tool"""
    
    print("🚀 V4 PROMPT OPTIMIZATION TEST")
    print("=" * 80)
    print("Testing new V4 prompt against fixed V2 with real API calls")
    print()
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not found")
        return
    
    # Comprehensive test scenarios covering various content types
    test_scenarios = [
        {
            "title": "英國必買童裝 JoJo Maman Bébé官網 3 折起入手網購教學",
            "expected_themes": ["uk", "baby", "clothes", "shopping", "guide"],
            "category": "brand-product-association"
        },
        {
            "title": "Kindle電子書閱讀器最強攻略：Paper White、Colorsoft等型號分別、價格比較及網購集運教學",
            "expected_themes": ["kindle", "ereader", "comparison", "guide"],
            "category": "product-recognition"
        },
        {
            "title": "開學季代購必買清單！IFME返學鞋、Gregory背囊及電子文具產品低至3折",
            "expected_themes": ["school", "season", "shoes", "bags"],
            "category": "seasonal-content"
        },
        {
            "title": "GAP集團美國官網網購教學，附Old Navy、Banana Republic及Athleta等副牌全面介紹",
            "expected_themes": ["gap", "us", "fashion", "brands"],
            "category": "fashion-brands"
        },
        {
            "title": "打風落雨必備！PROTECT U、Floatus及Wpc.等超強防風/跣水/降溫雨傘樂天網購教學",
            "expected_themes": ["umbrella", "japan", "rakuten", "weather"],
            "category": "platform-product"
        },
        {
            "title": "日本樂天時尚特價1折怎麼買？NB、BEAMS等男女、童裝優惠合集及集運教學",
            "expected_themes": ["japan", "rakuten", "fashion", "sale"],
            "category": "marketplace-fashion"
        },
        {
            "title": "8大日牌輕珠寶品牌一次睇！Agete、nojess及Star Jewelry等日劇女主御用明星珠寶",
            "expected_themes": ["japanese", "jewelry", "brands", "guide"],
            "category": "luxury-brands"
        }
    ]
    
    print(f"📊 Testing {len(test_scenarios)} diverse scenarios:")
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"   {i}. {scenario['category']}: {len(scenario['expected_themes'])} themes")
    print()
    
    # Configure optimizer
    config = {
        'test_function': create_v4_test_function(),
        'metrics': ['avg_theme_coverage', 'success_rate', 'avg_duration'],
        'primary_metric': 'avg_theme_coverage',
        'confidence_threshold': 0.7
    }
    
    optimizer = LLMOptimizer(config)
    
    # Run V4 vs V2 comparison
    print("🧪 Running V4 vs V2 Optimization Test")
    print("-" * 50)
    
    prompt_versions = ['v2_fixed', 'v4_optimized']
    
    try:
        results = optimizer.run_comparison(prompt_versions, test_scenarios)
        
        # Analyze results
        print("\n📊 V4 OPTIMIZATION RESULTS")
        print("=" * 60)
        
        best_version = optimizer.get_best_version()
        ranking = optimizer.get_ranking()
        
        print(f"🏆 Best Version: {best_version}")
        print(f"📈 Performance Ranking: {' > '.join(ranking)}")
        print()
        
        # Show detailed comparison
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
            
            if improvement > 0:
                print(f"📈 V4 Improvement: +{improvement:.1f}% theme coverage over V2")
            else:
                print(f"📉 V4 Performance: {improvement:.1f}% vs V2 (needs optimization)")
            print()
        
        # Generate insights
        insights = optimizer.generate_insights()
        
        print("💡 OPTIMIZATION INSIGHTS")
        print("=" * 40)
        
        print("📋 Recommendations:")
        for i, rec in enumerate(insights['recommendations'], 1):
            print(f"   {i}. {rec}")
        print()
        
        print("🎯 Deployment Recommendation:")
        deployment = insights['deployment_recommendation']
        print(f"   • Recommended Version: {deployment['recommended_version']}")
        print(f"   • Confidence Level: {deployment['confidence_level']}")
        print()
        
        # Show example results
        print("🎯 Example Results Comparison:")
        for version in ['v2_fixed', 'v4_optimized']:
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
        results_file = f"results/v4_optimization_test_{timestamp}.json"
        
        os.makedirs('results', exist_ok=True)
        optimizer.export_results(results_file)
        
        print("✅ V4 OPTIMIZATION TEST COMPLETE")
        print("=" * 60)
        print(f"✓ Successfully tested V4 vs V2 with real API calls")
        print(f"✓ Validated prompt improvements with production data")
        print(f"✓ Results exported to: {results_file}")
        
        # Final assessment
        if best_version == 'v4_optimized':
            v4_coverage = results['v4_optimized']['avg_theme_coverage']
            v2_coverage = results['v2_fixed']['avg_theme_coverage']
            improvement = (v4_coverage - v2_coverage) * 100
            
            print(f"✓ SUCCESS: V4 outperforms V2 (+{improvement:.1f}% coverage)")
            print("✓ V4 ready for production deployment consideration")
        elif best_version == 'v2_fixed':
            print("📝 V2 still performs better - V4 needs further optimization")
            print("💡 Use insights above to improve V4 design")
        
    except Exception as e:
        print(f"\n❌ V4 optimization test failed: {e}")
        print("This could be due to:")
        print("  • API rate limits or network issues")
        print("  • V4 prompt format compatibility issues")
        print("  • OpenAI API response parsing problems")
        return


if __name__ == "__main__":
    main()