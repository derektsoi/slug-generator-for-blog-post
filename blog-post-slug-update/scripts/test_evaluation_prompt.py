#!/usr/bin/env python3
"""
Evaluation Prompt Testing CLI Script

Test individual evaluation prompt versions with sample data and detailed 
performance analysis to help developers iterate on evaluation prompts.

Usage:
    python scripts/test_evaluation_prompt.py v2_cultural_focused --sample-size 10
    python scripts/test_evaluation_prompt.py current --verbose --sample-size 5  
    python scripts/test_evaluation_prompt.py v3_competitive_focused --output results.json

Examples:
    # Test cultural-focused evaluation prompt with 10 samples
    python scripts/test_evaluation_prompt.py v2_cultural_focused --sample-size 10
    
    # Test current evaluation prompt with verbose output
    python scripts/test_evaluation_prompt.py current --verbose
    
    # Test competitive evaluation prompt and save results
    python scripts/test_evaluation_prompt.py v3_competitive_focused --output results.json
"""

import argparse
import json
import sys
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
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


class EvaluationPromptTester:
    """Test evaluation prompt versions with sample data and analysis"""
    
    def __init__(self, api_key: str, verbose: bool = False):
        """Initialize tester with API key"""
        self.api_key = api_key
        self.verbose = verbose
        self.prompt_manager = EvaluationPromptManager()
        
        # Sample test cases with diverse characteristics
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
            }
        ]

    def validate_prompt_version(self, version: str) -> bool:
        """Validate that evaluation prompt version exists"""
        try:
            available_versions = self.prompt_manager.list_available_versions()
            if version not in available_versions:
                print(f"Error: Evaluation prompt version '{version}' not found.")
                print(f"Available versions: {', '.join(sorted(available_versions))}")
                return False
            return True
        except Exception as e:
            print(f"Error: Failed to validate prompt version: {e}")
            return False

    def test_prompt_version(self, version: str, sample_size: int) -> Dict[str, Any]:
        """Test evaluation prompt version with sample data"""
        if not self.validate_prompt_version(version):
            return {}
        
        try:
            evaluator = SEOEvaluator(
                api_key=self.api_key,
                evaluation_prompt_version=version
            )
            
            if self.verbose:
                print(f"🧪 TESTING EVALUATION PROMPT: {version}")
                print("=" * 50)
                print(f"Sample Size: {sample_size}")
                
                # Show prompt metadata
                metadata = evaluator.prompt_metadata
                print(f"Description: {metadata.get('description', 'No description')}")
                print(f"Focus Areas: {', '.join(metadata.get('focus_areas', ['general']))}")
                print()
            
            # Test with sample_size number of test cases
            test_subset = self.test_cases[:sample_size] if sample_size <= len(self.test_cases) else self.test_cases
            
            results = []
            total_scores = {dim: 0.0 for dim in DEFAULT_SCORING_DIMENSIONS}
            overall_total = 0.0
            
            for i, test_case in enumerate(test_subset):
                if self.verbose:
                    print(f"Testing {i+1}/{len(test_subset)}: {test_case['slug']}")
                
                try:
                    result = evaluator.evaluate_slug(
                        test_case['slug'],
                        test_case['title'], 
                        test_case['content']
                    )
                    
                    results.append({
                        'test_case': test_case,
                        'evaluation': result
                    })
                    
                    # Accumulate scores
                    for dim in DEFAULT_SCORING_DIMENSIONS:
                        if dim in result.get('dimension_scores', {}):
                            total_scores[dim] += result['dimension_scores'][dim]
                    
                    overall_total += result.get('overall_score', 0.0)
                    
                except Exception as e:
                    print(f"Warning: Failed to evaluate test case {i+1}: {e}")
                    continue
            
            # Calculate averages
            count = len(results)
            if count == 0:
                print("Error: No test cases could be evaluated successfully.")
                return {}
            
            avg_scores = {dim: total_scores[dim] / count for dim in total_scores}
            avg_overall = overall_total / count
            
            return {
                'evaluation_prompt_version': version,
                'sample_size': count,
                'results': results,
                'summary': {
                    'avg_overall_score': avg_overall,
                    'avg_dimension_scores': avg_scores
                }
            }
            
        except Exception as e:
            print(f"Error: Failed to test evaluation prompt: {e}")
            return {}

    def analyze_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test results and generate insights"""
        if not results:
            return {}
        
        summary = results['summary']
        avg_scores = summary['avg_dimension_scores']
        
        # Find strengths and improvements
        sorted_dimensions = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)
        strengths = sorted_dimensions[:2]  # Top 2 dimensions
        improvements = sorted_dimensions[-2:]  # Bottom 2 dimensions
        
        # Generate specific insights
        insights = {
            'strengths': [],
            'improvements': []
        }
        
        for dim, score in strengths:
            if score >= 0.8:
                insights['strengths'].append(f"Excellent {dim.replace('_', ' ')} scoring ({score:.3f})")
            elif score >= 0.7:
                insights['strengths'].append(f"Strong {dim.replace('_', ' ')} evaluation ({score:.3f})")
        
        for dim, score in improvements:
            if score < 0.6:
                insights['improvements'].append(f"Low {dim.replace('_', ' ')} scoring ({score:.3f}) - consider prompt refinement")
            elif score < 0.7:
                insights['improvements'].append(f"Moderate {dim.replace('_', ' ')} performance ({score:.3f}) - room for improvement")
        
        # Overall assessment
        overall_score = summary['avg_overall_score']
        if overall_score >= 0.85:
            performance_assessment = "Excellent overall performance"
        elif overall_score >= 0.75:
            performance_assessment = "Good overall performance"
        elif overall_score >= 0.65:
            performance_assessment = "Moderate performance with improvement opportunities"
        else:
            performance_assessment = "Performance needs significant improvement"
        
        insights['overall_assessment'] = f"{performance_assessment} ({overall_score:.3f})"
        
        return insights

    def print_console_results(self, results: Dict[str, Any], insights: Dict[str, Any]) -> None:
        """Print human-readable results to console"""
        if not results:
            return
        
        print(f"🧪 TESTING EVALUATION PROMPT: {results['evaluation_prompt_version']}")
        print("=" * 50)
        print(f"Sample Size: {results['sample_size']}")
        print()
        
        print("Evaluation Results:")
        summary = results['summary']
        print(f"• Overall Score: {summary['avg_overall_score']:.3f}")
        
        # Show dimension scores
        for dim, score in summary['avg_dimension_scores'].items():
            print(f"• {dim.replace('_', ' ').title()}: {score:.3f}")
        print()
        
        # Show insights
        if insights.get('overall_assessment'):
            print(f"✨ {insights['overall_assessment']}")
            print()
        
        if insights.get('strengths'):
            print("✅ Strengths:")
            for strength in insights['strengths']:
                print(f"- {strength}")
            print()
        
        if insights.get('improvements'):
            print("⚠️ Areas for improvement:")
            for improvement in insights['improvements']:
                print(f"- {improvement}")
            print()

    def save_results(self, results: Dict[str, Any], insights: Dict[str, Any], output_file: str) -> bool:
        """Save results to JSON file"""
        try:
            output_data = {
                **results,
                'analysis': insights,
                'timestamp': datetime.now().isoformat(),
                'tool': 'test_evaluation_prompt.py'
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            if self.verbose:
                print(f"Results saved to: {output_file}")
            
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
    if sample_size > 20:
        print("Warning: Large sample sizes may take significant time and API credits.")
        response = input("Continue? (y/N): ").lower()
        if response != 'y':
            print("Cancelled.")
            return False
    return True


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Test evaluation prompt versions with sample data and analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test cultural-focused evaluation prompt with 10 samples
  python scripts/test_evaluation_prompt.py v2_cultural_focused --sample-size 10
  
  # Test current evaluation prompt with verbose output  
  python scripts/test_evaluation_prompt.py current --verbose
  
  # Test competitive evaluation prompt and save results
  python scripts/test_evaluation_prompt.py v3_competitive_focused --output results.json
        """
    )
    
    parser.add_argument(
        'evaluation_prompt_version',
        help='Evaluation prompt version to test (e.g., current, v2_cultural_focused)'
    )
    
    parser.add_argument(
        '--sample-size',
        type=int,
        default=5,
        help='Number of test cases to evaluate (default: 5)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output during testing'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Save results to JSON file'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    api_key = validate_api_key()
    
    if not validate_sample_size(args.sample_size):
        sys.exit(1)
    
    # Initialize tester
    tester = EvaluationPromptTester(api_key, verbose=args.verbose)
    
    # Run tests
    start_time = time.time()
    results = tester.test_prompt_version(args.evaluation_prompt_version, args.sample_size)
    
    if not results:
        sys.exit(1)
    
    # Analyze results
    insights = tester.analyze_results(results)
    
    # Output results
    if not args.verbose:  # Print summary if not verbose
        tester.print_console_results(results, insights)
    
    # Save to file if requested
    if args.output:
        if not tester.save_results(results, insights, args.output):
            sys.exit(1)
    
    elapsed = time.time() - start_time
    if args.verbose:
        print(f"Testing completed in {elapsed:.1f} seconds.")


if __name__ == '__main__':
    main()