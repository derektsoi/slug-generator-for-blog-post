#!/usr/bin/env python3
"""
Evaluation Prompt Comparison CLI Script

Compare different evaluation prompt versions to understand their relative
performance and identify the best prompt for specific use cases.

Usage:
    python scripts/compare_evaluation_prompts.py current v2_cultural_focused --urls 20
    python scripts/compare_evaluation_prompts.py v2_cultural_focused v3_competitive_focused --sample-size 15 --verbose
    python scripts/compare_evaluation_prompts.py current v2_cultural_focused --output comparison.json --statistical

Examples:
    # Compare current vs cultural-focused with 20 test cases
    python scripts/compare_evaluation_prompts.py current v2_cultural_focused --urls 20
    
    # Detailed comparison with statistical analysis
    python scripts/compare_evaluation_prompts.py v2_cultural_focused v3_competitive_focused --statistical --verbose
    
    # Compare and save detailed results
    python scripts/compare_evaluation_prompts.py current v3_competitive_focused --output comparison.json
"""

import argparse
import json
import sys
import os
import time
import statistics
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    from evaluation.core.seo_evaluator import SEOEvaluator
    from config.evaluation_prompt_manager import EvaluationPromptManager
    from config.constants import DEFAULT_SCORING_DIMENSIONS
except ImportError as e:
    print(f"Error: Failed to import required modules: {e}")
    print("Please ensure you're running from the project root directory.")
    sys.exit(1)


class EvaluationPromptComparator:
    """Compare evaluation prompt versions with statistical analysis"""
    
    def __init__(self, api_key: str, verbose: bool = False):
        """Initialize comparator with API key"""
        self.api_key = api_key
        self.verbose = verbose
        self.prompt_manager = EvaluationPromptManager()
        
        # Sample test cases for comparison
        self.test_cases = [
            {
                "slug": "ultimate-ichiban-kuji-guide", 
                "title": "一番賞完全購入指南",
                "content": "Complete guide to ichiban-kuji purchasing and collecting rare anime merchandise"
            },
            {
                "slug": "skinniydip-iface-rhinoshield-comparison",
                "title": "日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！",
                "content": "Comprehensive comparison of top phone case brands including SKINNIYDIP, iface, and RhinoShield"
            },
            {
                "slug": "daikoku-drugstore-shopping-guide", 
                "title": "大國藥妝購物完全攻略",
                "content": "Complete Daikoku drugstore shopping guide for tourists and locals"
            },
            {
                "slug": "rakuten-official-store-benefits",
                "title": "樂天官網購物教學與優惠攻略",
                "content": "Guide to Rakuten official store shopping benefits and discount strategies"
            },
            {
                "slug": "gap-jojo-maman-bebe-kids-fashion", 
                "title": "GAP vs JoJo Maman Bébé童裝比較",
                "content": "Detailed comparison of GAP and JoJo Maman Bébé children's fashion collections"
            },
            {
                "slug": "jk-uniform-authentic-shopping-guide",
                "title": "正版JK制服購買指南與假貨辨別",
                "content": "Authentic JK uniform shopping guide with counterfeit identification tips"
            },
            {
                "slug": "asian-beauty-skincare-routine",
                "title": "亞洲美妝護膚步驟完整教學",
                "content": "Complete Asian beauty skincare routine guide with product recommendations"
            },
            {
                "slug": "cross-border-shipping-consolidation-guide",
                "title": "跨境購物集運教學與費用比較",
                "content": "Cross-border shopping consolidation service guide and cost comparison"
            }
        ]

    def validate_prompt_versions(self, version_a: str, version_b: str) -> bool:
        """Validate both evaluation prompt versions exist"""
        try:
            available_versions = self.prompt_manager.list_available_versions()
            
            missing_versions = []
            if version_a not in available_versions:
                missing_versions.append(version_a)
            if version_b not in available_versions:
                missing_versions.append(version_b)
            
            if missing_versions:
                print(f"Error: Evaluation prompt version(s) not found: {', '.join(missing_versions)}")
                print(f"Available versions: {', '.join(sorted(available_versions))}")
                return False
            
            # Check for identical versions
            if version_a == version_b:
                print("Warning: Comparing identical evaluation prompt versions.")
                print("Results will show no differences between versions.")
                
            return True
        except Exception as e:
            print(f"Error: Failed to validate prompt versions: {e}")
            return False

    def compare_prompt_versions(self, version_a: str, version_b: str, sample_size: int) -> Dict[str, Any]:
        """Compare two evaluation prompt versions"""
        if not self.validate_prompt_versions(version_a, version_b):
            return {}
        
        try:
            # Initialize evaluators
            evaluator_a = SEOEvaluator(
                api_key=self.api_key,
                evaluation_prompt_version=version_a
            )
            evaluator_b = SEOEvaluator(
                api_key=self.api_key,
                evaluation_prompt_version=version_b
            )
            
            if self.verbose:
                print(f"🔬 COMPARISON: {version_a} vs {version_b}")
                print("=" * 60)
                print(f"Sample Size: {sample_size}")
                print()
            
            # Prepare test cases
            test_subset = self.test_cases[:sample_size] if sample_size <= len(self.test_cases) else self.test_cases
            
            results_a = []
            results_b = []
            
            # Run evaluations
            for i, test_case in enumerate(test_subset):
                if self.verbose:
                    print(f"Testing {i+1}/{len(test_subset)}: {test_case['slug']}")
                
                try:
                    # Evaluate with version A
                    result_a = evaluator_a.evaluate_slug(
                        test_case['slug'],
                        test_case['title'], 
                        test_case['content']
                    )
                    
                    # Evaluate with version B
                    result_b = evaluator_b.evaluate_slug(
                        test_case['slug'],
                        test_case['title'], 
                        test_case['content']
                    )
                    
                    results_a.append({
                        'test_case': test_case,
                        'evaluation': result_a
                    })
                    
                    results_b.append({
                        'test_case': test_case,
                        'evaluation': result_b
                    })
                    
                except Exception as e:
                    print(f"Warning: Failed to evaluate test case {i+1}: {e}")
                    continue
            
            if len(results_a) == 0 or len(results_b) == 0:
                print("Error: No test cases could be evaluated successfully.")
                return {}
            
            return {
                'comparison_versions': [version_a, version_b],
                'sample_size': len(results_a),
                'version_a_results': results_a,
                'version_b_results': results_b,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error: Failed to compare evaluation prompts: {e}")
            return {}

    def calculate_statistics(self, results: Dict[str, Any], statistical_analysis: bool = False) -> Dict[str, Any]:
        """Calculate comparison statistics"""
        if not results:
            return {}
        
        results_a = results['version_a_results']
        results_b = results['version_b_results']
        version_a, version_b = results['comparison_versions']
        
        # Calculate averages for each version
        def calculate_averages(result_set):
            if not result_set:
                return {}
            
            total_scores = {dim: 0.0 for dim in DEFAULT_SCORING_DIMENSIONS}
            overall_total = 0.0
            count = len(result_set)
            
            for result in result_set:
                eval_data = result['evaluation']
                for dim in DEFAULT_SCORING_DIMENSIONS:
                    if dim in eval_data.get('dimension_scores', {}):
                        total_scores[dim] += eval_data['dimension_scores'][dim]
                overall_total += eval_data.get('overall_score', 0.0)
            
            avg_scores = {dim: total_scores[dim] / count for dim in total_scores}
            avg_overall = overall_total / count
            
            return {
                'avg_overall_score': avg_overall,
                'avg_dimension_scores': avg_scores,
                'count': count
            }
        
        averages_a = calculate_averages(results_a)
        averages_b = calculate_averages(results_b)
        
        # Determine winner
        if averages_a['avg_overall_score'] > averages_b['avg_overall_score']:
            winner = version_a
            winner_score = averages_a['avg_overall_score']
            runner_up = version_b
            runner_up_score = averages_b['avg_overall_score']
        else:
            winner = version_b
            winner_score = averages_b['avg_overall_score']
            runner_up = version_a
            runner_up_score = averages_a['avg_overall_score']
        
        score_difference = winner_score - runner_up_score
        
        # Dimension-by-dimension comparison
        dimension_comparison = {}
        for dim in DEFAULT_SCORING_DIMENSIONS:
            score_a = averages_a['avg_dimension_scores'][dim]
            score_b = averages_b['avg_dimension_scores'][dim]
            
            if score_a > score_b:
                dim_winner = version_a
                difference = score_a - score_b
            else:
                dim_winner = version_b
                difference = score_b - score_a
            
            dimension_comparison[dim] = {
                f'{version_a}_score': score_a,
                f'{version_b}_score': score_b,
                'winner': dim_winner,
                'difference': difference
            }
        
        analysis = {
            'results_summary': {
                f'{version_a}_performance': averages_a,
                f'{version_b}_performance': averages_b
            },
            'comparative_analysis': {
                'winner': winner,
                'winner_score': winner_score,
                'runner_up': runner_up,
                'runner_up_score': runner_up_score,
                'score_difference': score_difference,
                'improvement_percentage': (score_difference / runner_up_score) * 100
            },
            'dimension_comparison': dimension_comparison
        }
        
        # Add statistical analysis if requested
        if statistical_analysis:
            analysis['statistical_analysis'] = self._calculate_statistical_significance(results_a, results_b)
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(
            version_a, version_b, dimension_comparison, score_difference
        )
        
        return analysis

    def _calculate_statistical_significance(self, results_a: List[Dict], results_b: List[Dict]) -> Dict[str, Any]:
        """Calculate statistical significance metrics"""
        try:
            # Extract overall scores
            scores_a = [r['evaluation']['overall_score'] for r in results_a]
            scores_b = [r['evaluation']['overall_score'] for r in results_b]
            
            # Calculate basic statistics
            mean_a = statistics.mean(scores_a)
            mean_b = statistics.mean(scores_b)
            stdev_a = statistics.stdev(scores_a) if len(scores_a) > 1 else 0
            stdev_b = statistics.stdev(scores_b) if len(scores_b) > 1 else 0
            
            mean_difference = abs(mean_a - mean_b)
            pooled_stdev = ((stdev_a ** 2 + stdev_b ** 2) / 2) ** 0.5
            
            # Effect size (Cohen's d approximation)
            effect_size = mean_difference / pooled_stdev if pooled_stdev > 0 else 0
            
            # Confidence interval (rough approximation)
            confidence_interval = 1.96 * pooled_stdev  # 95% CI approximation
            
            return {
                'mean_difference': mean_difference,
                'effect_size': effect_size,
                'confidence_interval': confidence_interval,
                'sample_size': len(scores_a),
                'significance_note': self._interpret_effect_size(effect_size)
            }
        except Exception:
            return {
                'error': 'Statistical analysis failed due to insufficient data'
            }

    def _interpret_effect_size(self, effect_size: float) -> str:
        """Interpret Cohen's d effect size"""
        if effect_size < 0.2:
            return "No significant difference"
        elif effect_size < 0.5:
            return "Small effect size"
        elif effect_size < 0.8:
            return "Medium effect size"
        else:
            return "Large effect size"

    def _generate_recommendations(self, version_a: str, version_b: str, 
                                dimension_comparison: Dict, score_difference: float) -> List[str]:
        """Generate actionable recommendations based on comparison"""
        recommendations = []
        
        if score_difference < 0.05:
            recommendations.append("Performance difference is minimal - either version is suitable")
        elif score_difference < 0.10:
            recommendations.append("Small performance difference - consider other factors like consistency")
        else:
            recommendations.append(f"Significant performance difference ({score_difference:.3f}) - prefer the winning version")
        
        # Analyze dimension strengths
        strong_dimensions_a = []
        strong_dimensions_b = []
        
        for dim, comparison in dimension_comparison.items():
            if comparison['winner'] == version_a and comparison['difference'] > 0.05:
                strong_dimensions_a.append(dim.replace('_', ' '))
            elif comparison['winner'] == version_b and comparison['difference'] > 0.05:
                strong_dimensions_b.append(dim.replace('_', ' '))
        
        if strong_dimensions_a:
            recommendations.append(f"{version_a} excels in: {', '.join(strong_dimensions_a)}")
        
        if strong_dimensions_b:
            recommendations.append(f"{version_b} excels in: {', '.join(strong_dimensions_b)}")
        
        return recommendations

    def print_console_results(self, results: Dict[str, Any], analysis: Dict[str, Any]) -> None:
        """Print human-readable comparison results to console"""
        if not results or not analysis:
            return
        
        version_a, version_b = results['comparison_versions']
        
        print(f"🔬 COMPARISON: {version_a} vs {version_b}")
        print("=" * 60)
        print(f"Sample Size: {results['sample_size']}")
        print()
        
        # Performance Summary
        print("Performance Summary:")
        summary = analysis['results_summary']
        comp_analysis = analysis['comparative_analysis']
        
        score_a = summary[f'{version_a}_performance']['avg_overall_score']
        score_b = summary[f'{version_b}_performance']['avg_overall_score']
        
        print(f"• {version_a}: {score_a:.3f}")
        print(f"• {version_b}: {score_b:.3f}")
        print()
        
        # Winner
        print(f"🏆 Winner: {comp_analysis['winner']} ({comp_analysis['winner_score']:.3f})")
        print(f"Improvement: {comp_analysis['improvement_percentage']:.1f}% over {comp_analysis['runner_up']}")
        print()
        
        # Key Differences
        print("Key Differences:")
        dimension_comp = analysis['dimension_comparison']
        for dim, comp in dimension_comp.items():
            if comp['difference'] > 0.05:  # Only show significant differences
                print(f"• {dim.replace('_', ' ').title()}: {comp['winner']} leads by {comp['difference']:.3f}")
        print()
        
        # Recommendations
        if analysis.get('recommendations'):
            print("Recommendations:")
            for rec in analysis['recommendations']:
                print(f"• {rec}")
            print()
        
        # Statistical analysis if available
        if 'statistical_analysis' in analysis:
            stats = analysis['statistical_analysis']
            if 'error' not in stats:
                print("Statistical Analysis:")
                print(f"• Effect size: {stats.get('significance_note', 'Unknown')}")
                print(f"• Mean difference: {stats.get('mean_difference', 0):.3f}")
                print()

    def save_results(self, results: Dict[str, Any], analysis: Dict[str, Any], output_file: str) -> bool:
        """Save comparison results to JSON file"""
        try:
            output_data = {
                **results,
                **analysis,
                'tool': 'compare_evaluation_prompts.py'
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            if self.verbose:
                print(f"Comparison results saved to: {output_file}")
            
            return True
        except Exception as e:
            print(f"Error: Failed to save results to {output_file}: {e}")
            return False


def validate_api_key() -> str:
    """Validate and get API key from environment"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is required.")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    return api_key


def validate_sample_size(sample_size: int) -> bool:
    """Validate sample size parameter"""
    if sample_size <= 0:
        print("Error: Sample size must be greater than 0.")
        return False
    if sample_size > 30:
        print("Warning: Large sample sizes may take significant time and API credits.")
        response = input("Continue? (y/N): ").lower()
        if response != 'y':
            print("Cancelled.")
            return False
    return True


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Compare evaluation prompt versions with statistical analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare current vs cultural-focused with 20 test cases
  python scripts/compare_evaluation_prompts.py current v2_cultural_focused --urls 20
  
  # Detailed comparison with statistical analysis
  python scripts/compare_evaluation_prompts.py v2_cultural_focused v3_competitive_focused --statistical --verbose
  
  # Compare and save detailed results
  python scripts/compare_evaluation_prompts.py current v3_competitive_focused --output comparison.json
        """
    )
    
    parser.add_argument(
        'version1',
        help='First evaluation prompt version to compare'
    )
    
    parser.add_argument(
        'version2', 
        help='Second evaluation prompt version to compare'
    )
    
    parser.add_argument(
        '--urls',
        type=int,
        default=10,
        help='Number of test URLs to compare (default: 10)'
    )
    
    parser.add_argument(
        '--sample-size',
        type=int,
        dest='urls',  # Map to same parameter
        help='Alias for --urls'
    )
    
    parser.add_argument(
        '--statistical',
        action='store_true',
        help='Include statistical significance analysis'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed progress during comparison'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Save comparison results to JSON file'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    api_key = validate_api_key()
    
    if not validate_sample_size(args.urls):
        sys.exit(1)
    
    # Check for single version error
    if len(sys.argv) < 3:
        print("Error: Two evaluation prompt versions are required for comparison.")
        print("Usage: python scripts/compare_evaluation_prompts.py version1 version2 [options]")
        sys.exit(1)
    
    # Initialize comparator
    comparator = EvaluationPromptComparator(api_key, verbose=args.verbose)
    
    # Run comparison
    start_time = time.time()
    results = comparator.compare_prompt_versions(args.version1, args.version2, args.urls)
    
    if not results:
        sys.exit(1)
    
    # Calculate statistics
    analysis = comparator.calculate_statistics(results, args.statistical)
    
    # Output results
    if not args.verbose:  # Print summary if not verbose
        comparator.print_console_results(results, analysis)
    
    # Save to file if requested
    if args.output:
        if not comparator.save_results(results, analysis, args.output):
            sys.exit(1)
    
    elapsed = time.time() - start_time
    if args.verbose:
        print(f"Comparison completed in {elapsed:.1f} seconds.")


if __name__ == '__main__':
    main()