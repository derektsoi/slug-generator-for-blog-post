#!/usr/bin/env python3
"""
Comprehensive prompt version performance testing
Consolidates all prompt testing functionality
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Add src directory to Python path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from slug_generator import SlugGenerator

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
    """Main testing function"""
    tester = PromptVersionTester()
    
    try:
        # Run comparison of current implementation
        results = tester.compare_versions(['current'])
        
        # Save results
        tester.save_results(results)
        
        print("\n✅ Prompt version testing completed successfully!")
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())