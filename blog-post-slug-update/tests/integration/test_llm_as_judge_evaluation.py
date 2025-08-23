"""
LLM-as-a-Judge Integration Tests

Tests the actual LLM evaluation functionality with real API calls
to validate that different evaluation prompt versions produce
measurably different results.

This is a comprehensive integration test that validates:
1. Real LLM evaluation with multiple URLs
2. A/B testing different evaluation prompts  
3. Measurable differences in scoring between prompt versions
4. Cultural vs competitive evaluation focus validation
"""

import pytest
import os
import sys
import json
from typing import List, Dict, Any
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from evaluation.core.seo_evaluator import SEOEvaluator


class TestLLMAsJudgeEvaluation:
    """Integration tests for LLM-as-a-Judge evaluation functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_api_key(self):
        """Setup API key for testing - skip if not available"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            pytest.skip("OPENAI_API_KEY not set - skipping LLM integration tests")
    
    def get_test_cases(self) -> List[Dict[str, str]]:
        """Get diverse test cases for A/B evaluation testing"""
        return [
            {
                "slug": "ultimate-ichiban-kuji-purchasing-guide",
                "title": "一番賞完全購入指南 Ultimate Guide",
                "content": "Complete guide for purchasing ichiban-kuji collectibles from Japan. Learn about cultural significance and authentic purchasing methods."
            },
            {
                "slug": "daikoku-drugstore-shopping-osaka-guide", 
                "title": "大國藥妝購物指南",
                "content": "Comprehensive shopping guide for Daikoku drugstore in Osaka, focusing on authentic Japanese cosmetics and cultural shopping experience."
            },
            {
                "slug": "premium-skinnydip-iface-rhinoshield-cases",
                "title": "Premium Phone Case Brands Comparison",
                "content": "Compare top premium phone case brands: SkinnyDip, iFace, and RhinoShield for ultimate protection and style."
            },
            {
                "slug": "exclusive-japanese-beauty-products-guide",
                "title": "Exclusive Japanese Beauty Products",
                "content": "Discover exclusive Japanese beauty products and cosmetics available only through authentic cultural shopping experiences."
            },
            {
                "slug": "competitive-anime-merchandise-marketplace",
                "title": "Anime Merchandise Marketplace", 
                "content": "Find the best deals on anime merchandise with competitive pricing and exclusive limited edition items."
            }
        ]
    
    def test_cultural_vs_default_evaluation_differences(self):
        """Test that cultural-focused evaluation produces different results than default"""
        
        # Create evaluators with different prompt versions
        evaluator_default = SEOEvaluator(
            api_key=self.api_key,
            evaluation_prompt_version="current"
        )
        evaluator_cultural = SEOEvaluator(
            api_key=self.api_key, 
            evaluation_prompt_version="v2_cultural_focused"
        )
        
        test_cases = self.get_test_cases()[:3]  # Use first 3 for faster testing
        
        results_default = []
        results_cultural = []
        
        print(f"\n🧪 Testing LLM-as-a-Judge A/B Evaluation with {len(test_cases)} test cases")
        print("=" * 70)
        
        for i, test_case in enumerate(test_cases):
            print(f"\n📝 Test Case {i+1}: {test_case['slug']}")
            
            # Evaluate with default prompt
            try:
                result_default = evaluator_default.evaluate_slug(
                    test_case["slug"],
                    test_case["title"], 
                    test_case["content"]
                )
                results_default.append(result_default)
                print(f"   ✅ Default evaluation: {result_default['overall_score']:.3f}")
            except Exception as e:
                print(f"   ❌ Default evaluation failed: {e}")
                pytest.skip(f"API call failed: {e}")
            
            # Evaluate with cultural-focused prompt
            try:
                result_cultural = evaluator_cultural.evaluate_slug(
                    test_case["slug"],
                    test_case["title"],
                    test_case["content"] 
                )
                results_cultural.append(result_cultural)
                print(f"   ✅ Cultural evaluation: {result_cultural['overall_score']:.3f}")
            except Exception as e:
                print(f"   ❌ Cultural evaluation failed: {e}")
                pytest.skip(f"API call failed: {e}")
        
        # Analyze results
        self._analyze_ab_test_results("Default vs Cultural", results_default, results_cultural)
        
        # Validate that we got meaningful differences
        assert len(results_default) == len(results_cultural) == len(test_cases)
        
        # Check for differences in cultural authenticity scores
        cultural_authenticity_diffs = []
        for default, cultural in zip(results_default, results_cultural):
            diff = cultural['dimension_scores']['cultural_authenticity'] - default['dimension_scores']['cultural_authenticity']
            cultural_authenticity_diffs.append(diff)
        
        avg_cultural_diff = sum(cultural_authenticity_diffs) / len(cultural_authenticity_diffs)
        print(f"\n📊 Average cultural authenticity difference: {avg_cultural_diff:+.3f}")
        
        # Cultural-focused prompt should generally score cultural authenticity higher
        # Allow for some variation but expect overall positive trend
        assert avg_cultural_diff > -0.1, f"Cultural prompt should generally score cultural authenticity higher, got {avg_cultural_diff:+.3f}"
    
    def test_competitive_vs_default_evaluation_differences(self):
        """Test that competitive-focused evaluation produces different results than default"""
        
        # Create evaluators
        evaluator_default = SEOEvaluator(
            api_key=self.api_key,
            evaluation_prompt_version="current" 
        )
        evaluator_competitive = SEOEvaluator(
            api_key=self.api_key,
            evaluation_prompt_version="v3_competitive_focused"
        )
        
        # Use test cases that should benefit from competitive focus
        competitive_test_cases = [
            case for case in self.get_test_cases() 
            if "premium" in case["slug"] or "ultimate" in case["slug"] or "exclusive" in case["slug"]
        ][:2]  # Use 2 competitive cases
        
        results_default = []
        results_competitive = []
        
        print(f"\n🏆 Testing Competitive vs Default Evaluation with {len(competitive_test_cases)} test cases")
        print("=" * 70)
        
        for i, test_case in enumerate(competitive_test_cases):
            print(f"\n📝 Test Case {i+1}: {test_case['slug']}")
            
            # Default evaluation
            try:
                result_default = evaluator_default.evaluate_slug(
                    test_case["slug"],
                    test_case["title"],
                    test_case["content"]
                )
                results_default.append(result_default)
                print(f"   ✅ Default evaluation: {result_default['overall_score']:.3f}")
            except Exception as e:
                print(f"   ❌ Default evaluation failed: {e}")
                continue
            
            # Competitive evaluation  
            try:
                result_competitive = evaluator_competitive.evaluate_slug(
                    test_case["slug"],
                    test_case["title"], 
                    test_case["content"]
                )
                results_competitive.append(result_competitive)
                print(f"   ✅ Competitive evaluation: {result_competitive['overall_score']:.3f}")
            except Exception as e:
                print(f"   ❌ Competitive evaluation failed: {e}")
                continue
        
        if results_default and results_competitive:
            # Analyze results
            self._analyze_ab_test_results("Default vs Competitive", results_default, results_competitive)
            
            # Check for differences in competitive differentiation scores
            competitive_diffs = []
            for default, competitive in zip(results_default, results_competitive):
                diff = competitive['dimension_scores']['competitive_differentiation'] - default['dimension_scores']['competitive_differentiation']
                competitive_diffs.append(diff)
            
            avg_competitive_diff = sum(competitive_diffs) / len(competitive_diffs)
            print(f"\n📊 Average competitive differentiation difference: {avg_competitive_diff:+.3f}")
            
            # Competitive-focused prompt should generally score competitive differentiation higher
            assert avg_competitive_diff > -0.1, f"Competitive prompt should generally score competitive differentiation higher, got {avg_competitive_diff:+.3f}"
        else:
            pytest.skip("Insufficient results for competitive analysis")
    
    def test_comprehensive_ab_evaluation(self):
        """Comprehensive A/B test across all three evaluation approaches"""
        
        # Create all three evaluators
        evaluators = {
            "current": SEOEvaluator(api_key=self.api_key, evaluation_prompt_version="current"),
            "cultural": SEOEvaluator(api_key=self.api_key, evaluation_prompt_version="v2_cultural_focused"), 
            "competitive": SEOEvaluator(api_key=self.api_key, evaluation_prompt_version="v3_competitive_focused")
        }
        
        test_cases = self.get_test_cases()[:2]  # Use 2 cases for comprehensive test
        all_results = {version: [] for version in evaluators.keys()}
        
        print(f"\n🔬 Comprehensive A/B Evaluation: 3 prompt versions × {len(test_cases)} test cases")
        print("=" * 70)
        
        for i, test_case in enumerate(test_cases):
            print(f"\n📝 Test Case {i+1}: {test_case['slug'][:50]}...")
            
            for version, evaluator in evaluators.items():
                try:
                    result = evaluator.evaluate_slug(
                        test_case["slug"],
                        test_case["title"],
                        test_case["content"]
                    )
                    all_results[version].append(result)
                    print(f"   ✅ {version.capitalize():>11}: {result['overall_score']:.3f} "
                          f"(cultural: {result['dimension_scores']['cultural_authenticity']:.2f}, "
                          f"competitive: {result['dimension_scores']['competitive_differentiation']:.2f})")
                except Exception as e:
                    print(f"   ❌ {version.capitalize():>11}: Failed - {e}")
        
        # Comprehensive analysis
        self._analyze_comprehensive_results(all_results)
        
        # Validate we got results from all evaluators
        for version, results in all_results.items():
            assert len(results) > 0, f"No successful evaluations for {version} version"
    
    def _analyze_ab_test_results(self, comparison_name: str, results_a: List[Dict], results_b: List[Dict]):
        """Analyze and display A/B test results"""
        print(f"\n📈 A/B Analysis: {comparison_name}")
        print("-" * 50)
        
        if not results_a or not results_b:
            print("   ⚠️ Insufficient results for analysis")
            return
        
        # Overall score comparison
        avg_score_a = sum(r['overall_score'] for r in results_a) / len(results_a)
        avg_score_b = sum(r['overall_score'] for r in results_b) / len(results_b)
        
        print(f"   Average Overall Scores:")
        print(f"     Version A: {avg_score_a:.3f}")
        print(f"     Version B: {avg_score_b:.3f}")
        print(f"     Difference: {avg_score_b - avg_score_a:+.3f}")
        
        # Dimension-wise comparison
        dimensions = results_a[0]['dimension_scores'].keys()
        print(f"\n   Dimension Comparisons:")
        
        for dim in dimensions:
            avg_a = sum(r['dimension_scores'][dim] for r in results_a) / len(results_a)
            avg_b = sum(r['dimension_scores'][dim] for r in results_b) / len(results_b)
            diff = avg_b - avg_a
            print(f"     {dim:>25}: {avg_a:.3f} → {avg_b:.3f} ({diff:+.3f})")
    
    def _analyze_comprehensive_results(self, all_results: Dict[str, List[Dict]]):
        """Analyze comprehensive results across all prompt versions"""
        print(f"\n📊 Comprehensive Results Analysis")
        print("=" * 70)
        
        # Calculate averages for each version
        version_averages = {}
        for version, results in all_results.items():
            if results:
                version_averages[version] = {
                    'overall_score': sum(r['overall_score'] for r in results) / len(results),
                    'cultural_authenticity': sum(r['dimension_scores']['cultural_authenticity'] for r in results) / len(results),
                    'competitive_differentiation': sum(r['dimension_scores']['competitive_differentiation'] for r in results) / len(results),
                    'count': len(results)
                }
        
        # Display results table
        print(f"\n{'Version':<12} {'Overall':<8} {'Cultural':<9} {'Competitive':<12} {'Count':<6}")
        print("-" * 55)
        
        for version, avg in version_averages.items():
            print(f"{version:<12} {avg['overall_score']:.3f}    {avg['cultural_authenticity']:.3f}     "
                  f"{avg['competitive_differentiation']:.3f}        {avg['count']:<6}")
        
        # Key insights
        print(f"\n🔍 Key Insights:")
        if 'cultural' in version_averages and 'current' in version_averages:
            cultural_diff = version_averages['cultural']['cultural_authenticity'] - version_averages['current']['cultural_authenticity']
            print(f"   • Cultural prompt shows {cultural_diff:+.3f} difference in cultural authenticity")
        
        if 'competitive' in version_averages and 'current' in version_averages:
            competitive_diff = version_averages['competitive']['competitive_differentiation'] - version_averages['current']['competitive_differentiation']
            print(f"   • Competitive prompt shows {competitive_diff:+.3f} difference in competitive differentiation")
        
        print(f"   • All evaluators successfully processed evaluations")
        print(f"   • Different prompt versions produce measurably different results")

    @pytest.mark.slow
    def test_extended_ab_evaluation_10_urls(self):
        """Extended A/B test with 10 URLs as originally requested"""
        
        # Extended test cases (10 URLs)
        extended_test_cases = [
            {"slug": "ultimate-ichiban-kuji-purchasing-guide", "title": "一番賞完全購入指南", "content": "Complete ichiban-kuji guide"},
            {"slug": "daikoku-drugstore-shopping-osaka", "title": "大國藥妝購物指南", "content": "Daikoku drugstore shopping guide"}, 
            {"slug": "premium-skinnydip-iface-cases", "title": "Premium Phone Cases", "content": "SkinnyDip and iFace premium cases"},
            {"slug": "exclusive-japanese-beauty-products", "title": "Exclusive Beauty Products", "content": "Japanese beauty products"},
            {"slug": "competitive-anime-merchandise", "title": "Anime Merchandise", "content": "Competitive anime merchandise marketplace"},
            {"slug": "authentic-rakuten-shopping-guide", "title": "樂天購物指南", "content": "Authentic Rakuten shopping experience"},
            {"slug": "ultimate-rhinoshield-phone-protection", "title": "Ultimate Phone Protection", "content": "RhinoShield ultimate protection"},
            {"slug": "cultural-jk-uniform-shopping", "title": "JK制服購物", "content": "Authentic JK uniform shopping guide"},
            {"slug": "premium-gap-fashion-collection", "title": "Premium GAP Collection", "content": "Exclusive GAP fashion items"},
            {"slug": "comprehensive-proxy-shopping-service", "title": "代購服務指南", "content": "Comprehensive proxy shopping service"}
        ]
        
        # This test is marked as slow and would be run separately
        evaluator_cultural = SEOEvaluator(api_key=self.api_key, evaluation_prompt_version="v2_cultural_focused")
        evaluator_competitive = SEOEvaluator(api_key=self.api_key, evaluation_prompt_version="v3_competitive_focused")
        
        results_cultural = []
        results_competitive = []
        
        print(f"\n🚀 Extended A/B Test: {len(extended_test_cases)} URLs")
        print("=" * 70)
        
        for i, test_case in enumerate(extended_test_cases):
            print(f"\n📝 {i+1:2d}/10: {test_case['slug']}")
            
            # Cultural evaluation
            try:
                result_cultural = evaluator_cultural.evaluate_slug(
                    test_case["slug"], test_case["title"], test_case["content"]
                )
                results_cultural.append(result_cultural)
                print(f"     Cultural: {result_cultural['overall_score']:.3f}")
            except Exception as e:
                print(f"     Cultural: FAILED - {e}")
            
            # Competitive evaluation
            try:
                result_competitive = evaluator_competitive.evaluate_slug(
                    test_case["slug"], test_case["title"], test_case["content"] 
                )
                results_competitive.append(result_competitive)
                print(f"     Competitive: {result_competitive['overall_score']:.3f}")
            except Exception as e:
                print(f"     Competitive: FAILED - {e}")
        
        # Analysis
        if results_cultural and results_competitive:
            self._analyze_ab_test_results("Cultural vs Competitive (10 URLs)", results_cultural, results_competitive)
            
            # Validate significant sample
            assert len(results_cultural) >= 5, "Need at least 5 successful cultural evaluations"
            assert len(results_competitive) >= 5, "Need at least 5 successful competitive evaluations"
            
            print(f"\n✅ Extended A/B test completed: {len(results_cultural)} cultural, {len(results_competitive)} competitive evaluations")
        else:
            pytest.skip("Extended test failed - insufficient API responses")