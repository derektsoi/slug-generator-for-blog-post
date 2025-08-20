#!/usr/bin/env python3
"""
Prompt Evolution Testing Framework
Compare multiple prompt versions on the same dataset
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List

# Add src directory to Python path
sys.path.insert(0, 'src')

from slug_generator import SlugGenerator

class PromptEvolutionTester:
    """Test multiple prompt versions and compare performance"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
        # Test samples for consistent comparison
        self.test_samples = [
            {
                "title": "英國必買童裝 JoJo Maman Bébé官網 3 折起入手網購教學",
                "url": "https://www.buyandship.today/blog/2025/08/18/jojo-maman-bebe%e8%8b%b1%e5%9c%8b%e5%ae%98%e7%b6%b2%e6%8a%98%e6%89%a3%e5%8f%8a%e8%b3%bc%e8%b2%b7%e6%95%99%e5%ad%b8/",
                "expected_themes": ["uk", "baby", "clothes", "shopping", "guide"],
                "focus": "Brand-product association (JoJo Maman Bébé = baby clothes)"
            },
            {
                "title": "Kindle電子書閱讀器最強攻略：Paper White、Colorsoft等型號分別、價格比較及網購集運教學",
                "url": "https://www.buyandship.today/blog/2025/08/13/kindle%e7%b6%b2%e8%b3%bc%e6%94%bb%e7%95%a5/",
                "expected_themes": ["kindle", "ereader", "comparison", "guide"],
                "focus": "Product category recognition (Kindle = ereader)"
            },
            {
                "title": "開學季代購必買清單！IFME返學鞋、Gregory背囊及電子文具產品低至3折",
                "url": "https://www.buyandship.today/blog/2025/08/12/%e9%96%8b%e5%ad%b8%e5%ad%a3%e4%bb%a3%e8%b3%bc%e5%bf%85%e8%b2%b7%e6%b8%85%e5%96%ae/",
                "expected_themes": ["school", "season", "shoes", "bags"],
                "focus": "Seasonal content and multiple products"
            },
            {
                "title": "GAP集團美國官網網購教學，附Old Navy、Banana Republic及Athleta等副牌全面介紹",
                "url": "https://www.buyandship.today/blog/2025/08/13/gap%e9%9b%86%e5%9c%98%e7%be%8e%e5%9c%8b%e5%ae%98%e7%b6%b2%e6%95%99%e5%ad%b8/",
                "expected_themes": ["gap", "us", "fashion", "brands"],
                "focus": "Fashion brand group recognition"
            },
            {
                "title": "打風落雨必備！PROTECT U、Floatus及Wpc.等超強防風/跣水/降溫雨傘樂天網購教學",
                "url": "https://www.buyandship.today/blog/2025/08/13/%e6%97%a5%e6%9c%ac%e6%a8%82%e5%a4%a9%e9%9b%a8%e5%82%98%e7%b6%b2%e8%b3%bc%e6%95%99%e5%ad%b8/",
                "expected_themes": ["umbrella", "japan", "rakuten", "weather"],
                "focus": "Product + platform + weather context"
            }
        ]
    
    def create_test_generator(self, prompt_version: str) -> SlugGenerator:
        """Create generator with specific prompt version"""
        generator = SlugGenerator(api_key=self.api_key, max_retries=2)
        
        # Override the prompt loading method for testing
        def load_test_prompt(prompt_name):
            prompt_file = f"config/prompts/slug_generation_{prompt_version}.txt"
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            except FileNotFoundError:
                if prompt_version == "v1":
                    # Use original prompt
                    return open("config/prompts/slug_generation.txt", 'r').read().strip()
                else:
                    raise FileNotFoundError(f"Prompt version {prompt_version} not found")
        
        generator._load_prompt = load_test_prompt
        return generator
    
    def test_prompt_version(self, version: str, samples: List[Dict]) -> Dict:
        """Test a specific prompt version"""
        print(f"🧪 Testing Prompt Version: {version}")
        
        try:
            generator = self.create_test_generator(version)
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            return {"error": str(e)}
        
        results = []
        total_start_time = time.time()
        
        for i, sample in enumerate(samples, 1):
            print(f"   Testing {i}/{len(samples)}: {sample['focus']}")
            
            try:
                start_time = time.time()
                result = generator.generate_slug_from_content(
                    sample['title'], 
                    f"Blog post about {sample['focus']}", 
                    count=3
                )
                duration = time.time() - start_time
                
                # Calculate theme coverage
                expected_themes = set(sample['expected_themes'])
                all_slugs = [result['primary']] + result.get('alternatives', [])
                slug_text = ' '.join(all_slugs).lower()
                
                matched_themes = set()
                for theme in expected_themes:
                    if theme.lower() in slug_text:
                        matched_themes.add(theme)
                
                theme_coverage = len(matched_themes) / len(expected_themes)
                
                sample_result = {
                    'sample_id': i,
                    'title': sample['title'],
                    'focus': sample['focus'],
                    'primary_slug': result['primary'],
                    'alternatives': result.get('alternatives', []),
                    'expected_themes': list(expected_themes),
                    'matched_themes': list(matched_themes),
                    'theme_coverage': theme_coverage,
                    'duration': duration,
                    'success': True
                }
                
                results.append(sample_result)
                print(f"      ✅ {result['primary']} (coverage: {theme_coverage:.1%})")
                
            except Exception as e:
                print(f"      ❌ Error: {str(e)}")
                results.append({
                    'sample_id': i,
                    'error': str(e),
                    'success': False,
                    'duration': time.time() - start_time
                })
        
        total_duration = time.time() - total_start_time
        
        # Calculate metrics
        successful_results = [r for r in results if r.get('success', False)]
        
        if successful_results:
            avg_coverage = sum(r['theme_coverage'] for r in successful_results) / len(successful_results)
            avg_duration = sum(r['duration'] for r in successful_results) / len(successful_results)
        else:
            avg_coverage = 0
            avg_duration = 0
        
        summary = {
            'version': version,
            'total_samples': len(samples),
            'successful': len(successful_results),
            'failed': len(results) - len(successful_results),
            'avg_theme_coverage': avg_coverage,
            'avg_duration': avg_duration,
            'total_duration': total_duration,
            'results': results
        }
        
        print(f"   📊 Results: {len(successful_results)}/{len(samples)} success, "
              f"{avg_coverage:.1%} avg coverage, {avg_duration:.2f}s avg time")
        
        return summary
    
    def compare_prompt_versions(self, versions: List[str]) -> Dict:
        """Compare multiple prompt versions"""
        print("="*80)
        print("PROMPT EVOLUTION TESTING")
        print("="*80)
        
        all_results = {}
        
        for version in versions:
            print()
            result = self.test_prompt_version(version, self.test_samples)
            all_results[version] = result
            time.sleep(2)  # Brief pause between tests
        
        # Generate comparison
        print("\n" + "="*80)
        print("COMPARISON RESULTS")
        print("="*80)
        
        print("📊 Performance Summary:")
        for version, result in all_results.items():
            if 'error' not in result:
                success_rate = result['successful'] / result['total_samples']
                print(f"   {version:>10}: {success_rate:.0%} success, "
                      f"{result['avg_theme_coverage']:.1%} coverage, "
                      f"{result['avg_duration']:.2f}s avg")
            else:
                print(f"   {version:>10}: ❌ {result['error']}")
        
        # Find best performer
        valid_results = {k: v for k, v in all_results.items() if 'error' not in v}
        if valid_results:
            best_version = max(valid_results.keys(), 
                             key=lambda k: valid_results[k]['avg_theme_coverage'])
            
            print(f"\n🏆 Best Performer: {best_version}")
            best_result = valid_results[best_version]
            print(f"   Theme Coverage: {best_result['avg_theme_coverage']:.1%}")
            print(f"   Success Rate: {best_result['successful']}/{best_result['total_samples']}")
            
            # Show specific improvements
            if len(valid_results) > 1:
                print(f"\n📈 Improvements over other versions:")
                for version, result in valid_results.items():
                    if version != best_version:
                        coverage_diff = best_result['avg_theme_coverage'] - result['avg_theme_coverage']
                        print(f"   vs {version}: +{coverage_diff:.1%} theme coverage")
        
        # Save detailed results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"results/prompt_evolution_{timestamp}.json"
        
        os.makedirs('results', exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'test_samples': len(self.test_samples),
                'versions_tested': versions,
                'results': all_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed results saved to: {output_file}")
        
        return all_results

def main():
    """Run prompt evolution testing"""
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OPENAI_API_KEY found in environment")
        return
    
    tester = PromptEvolutionTester(api_key)
    
    # Test available prompt versions
    versions_to_test = ["v1", "v2"]  # v1 = original, v2 = enhanced
    
    print("🎯 Testing Focus Areas:")
    for sample in tester.test_samples:
        print(f"   - {sample['focus']}")
    print()
    
    results = tester.compare_prompt_versions(versions_to_test)
    
    print("\n" + "="*80)
    print("✅ Prompt evolution testing complete!")
    print("="*80)
    
    return results

if __name__ == "__main__":
    main()