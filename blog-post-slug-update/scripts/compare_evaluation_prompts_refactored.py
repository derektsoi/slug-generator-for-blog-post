#!/usr/bin/env python3
"""
Evaluation Prompt Comparison CLI Script (Refactored)

Compare multiple evaluation prompt versions side-by-side with statistical analysis.
Conduct A/B testing with effect size analysis and performance insights.

Usage:
    python scripts/compare_evaluation_prompts_refactored.py v2_cultural_focused v3_competitive_focused --sample-size 10
    python scripts/compare_evaluation_prompts_refactored.py current v2_cultural_focused --verbose --sample-size 5
    python scripts/compare_evaluation_prompts_refactored.py v3_competitive_focused current --output comparison.json

Examples:
    # Compare cultural vs competitive evaluation approaches with 10 samples
    python scripts/compare_evaluation_prompts_refactored.py v2_cultural_focused v3_competitive_focused --sample-size 10
    
    # Compare current vs cultural with detailed output
    python scripts/compare_evaluation_prompts_refactored.py current v2_cultural_focused --verbose
    
    # Compare competitive vs current and save results
    python scripts/compare_evaluation_prompts_refactored.py v3_competitive_focused current --output results.json
"""

import argparse
import time
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from cli import BaseCLI, TestDataMixin, PromptValidationMixin, OutputFormattingMixin, setup_common_args, add_sample_size_arg
from cli.analysis import PerformanceAnalyzer, ResultsInsightGenerator


class EvaluationPromptComparatorRefactored(BaseCLI, TestDataMixin, PromptValidationMixin, OutputFormattingMixin):
    """Compare evaluation prompt versions with statistical analysis - Refactored Version"""
    
    def __init__(self):
        super().__init__(
            tool_name="compare_evaluation_prompts_refactored.py",
            description="Compare evaluation prompt versions with statistical analysis"
        )

    def setup_parser(self) -> argparse.ArgumentParser:
        """Setup argument parser"""
        parser = argparse.ArgumentParser(
            description=self.description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Compare cultural vs competitive evaluation approaches with 10 samples
  python scripts/compare_evaluation_prompts_refactored.py v2_cultural_focused v3_competitive_focused --sample-size 10
  
  # Compare current vs cultural with detailed output
  python scripts/compare_evaluation_prompts_refactored.py current v2_cultural_focused --verbose
  
  # Compare competitive vs current and save results
  python scripts/compare_evaluation_prompts_refactored.py v3_competitive_focused current --output results.json
            """
        )
        
        parser.add_argument(
            'version_a',
            help='First evaluation prompt version to compare'
        )
        
        parser.add_argument(
            'version_b', 
            help='Second evaluation prompt version to compare'
        )
        
        add_sample_size_arg(parser, default=5)
        setup_common_args(parser)
        
        return parser

    def test_single_version(self, version: str, sample_size: int) -> Dict[str, Any]:
        """Test a single evaluation prompt version"""
        evaluator = self.SEOEvaluator(
            api_key=self.api_key,
            evaluation_prompt_version=version
        )
        
        if self.verbose:
            print(f"Testing {version}...")
            metadata = evaluator.prompt_metadata
            print(f"  Description: {metadata.get('description', 'No description')}")
            print(f"  Focus Areas: {', '.join(metadata.get('focus_areas', ['general']))}")
        
        test_cases = self.get_test_subset(sample_size)
        results = []
        
        for i, test_case in enumerate(test_cases):
            if self.verbose:
                print(f"  {i+1}/{len(test_cases)}: {test_case['slug']}")
            
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
                
            except Exception as e:
                print(f"    Warning: Failed to evaluate test case {i+1}: {e}")
                continue
        
        if not results:
            raise ValueError(f"No test cases could be evaluated for version {version}")
        
        return results

    def run_comparison(self, version_a: str, version_b: str, sample_size: int) -> Dict[str, Any]:
        """Run A/B comparison between two evaluation prompt versions"""
        # Validate sample size
        self.validate_sample_size(sample_size)
        
        # Validate prompt versions
        prompt_manager = self.EvaluationPromptManager()
        self.validate_prompt_versions(version_a, version_b, prompt_manager)
        
        if self.verbose:
            self.print_section_header(f"COMPARING EVALUATION PROMPTS")
            print(f"Version A: {version_a}")
            print(f"Version B: {version_b}")
            print(f"Sample Size: {sample_size}")
            print()
        
        # Test both versions
        results_a = self.test_single_version(version_a, sample_size)
        results_b = self.test_single_version(version_b, sample_size)
        
        # Analyze comparison
        insight_generator = ResultsInsightGenerator(self.DEFAULT_SCORING_DIMENSIONS)
        comparison_analysis = insight_generator.compare_results(
            results_a, results_b, version_a, version_b
        )
        
        return {
            'version_a': version_a,
            'version_b': version_b,
            'sample_size': sample_size,
            'results_a': results_a,
            'results_b': results_b,
            'comparison_analysis': comparison_analysis
        }

    def print_comparison_results(self, results: Dict[str, Any]) -> None:
        """Print comprehensive comparison results to console"""
        version_a = results['version_a']
        version_b = results['version_b']
        analysis = results['comparison_analysis']
        
        self.print_section_header(f"EVALUATION PROMPT COMPARISON RESULTS")
        print(f"Version A: {version_a}")
        print(f"Version B: {version_b}")
        print(f"Sample Size: {results['sample_size']}")
        print()
        
        # Performance Summary
        self.print_subsection_header("Performance Summary")
        summary = analysis['results_summary']
        perf_a = summary[f'{version_a}_performance']
        perf_b = summary[f'{version_b}_performance']
        
        self.print_score_line(f"{version_a} Overall Score", perf_a['avg_overall_score'])
        self.print_score_line(f"{version_b} Overall Score", perf_b['avg_overall_score'])
        print()
        
        # Winner Analysis
        winner_info = analysis['comparative_analysis']
        winner_symbol = "🏆" if winner_info['improvement_percentage'] > 5 else "📊"
        print(f"{winner_symbol} Winner: {winner_info['winner']} ({self.format_score_display(winner_info['winner_score'])})")
        print(f"   Runner-up: {winner_info['runner_up']} ({self.format_score_display(winner_info['runner_up_score'])})")
        print(f"   Improvement: {winner_info['improvement_percentage']:.1f}%")
        print()
        
        # Statistical Analysis
        stats = analysis.get('statistical_analysis', {})
        if 'error' not in stats:
            self.print_subsection_header("Statistical Analysis")
            self.print_score_line("Effect Size", stats.get('effect_size', 0))
            print(f"• Significance: {stats.get('significance_note', 'Unknown')}")
            print(f"• Mean Difference: {self.format_score_display(stats.get('mean_difference', 0))}")
            print()
        
        # Dimension Comparison
        self.print_subsection_header("Dimension Breakdown")
        dim_comparison = analysis['dimension_comparison']
        for dim, comparison in dim_comparison.items():
            dim_name = self.format_dimension_name(dim)
            winner_symbol = "✓" if comparison['difference'] > 0.05 else "≈"
            print(f"{winner_symbol} {dim_name}: {comparison['winner']}")
            print(f"   {version_a}: {self.format_score_display(comparison[f'{version_a}_score'])}")
            print(f"   {version_b}: {self.format_score_display(comparison[f'{version_b}_score'])}")
        print()
        
        # Recommendations
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            self.print_subsection_header("Recommendations")
            self.print_bullet_list(recommendations, "•")
            print()

    def run_command(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Execute the main comparison logic"""
        start_time = time.time()
        
        # Run comparison
        results = self.run_comparison(args.version_a, args.version_b, args.sample_size)
        
        # Output results if not in verbose mode
        if not self.verbose:
            self.print_comparison_results(results)
        
        elapsed = time.time() - start_time
        if self.verbose:
            print(f"Comparison completed in {elapsed:.1f} seconds.")
        
        return results


def main():
    """Main CLI entry point"""
    comparator = EvaluationPromptComparatorRefactored()
    comparator.run()


if __name__ == '__main__':
    main()