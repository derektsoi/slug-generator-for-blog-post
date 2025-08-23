#!/usr/bin/env python3
"""
Evaluation Prompt Testing CLI Script (Refactored)

Test individual evaluation prompt versions with sample data and detailed 
performance analysis to help developers iterate on evaluation prompts.

Usage:
    python scripts/test_evaluation_prompt_refactored.py v2_cultural_focused --sample-size 10
    python scripts/test_evaluation_prompt_refactored.py current --verbose --sample-size 5  
    python scripts/test_evaluation_prompt_refactored.py v3_competitive_focused --output results.json

Examples:
    # Test cultural-focused evaluation prompt with 10 samples
    python scripts/test_evaluation_prompt_refactored.py v2_cultural_focused --sample-size 10
    
    # Test current evaluation prompt with verbose output
    python scripts/test_evaluation_prompt_refactored.py current --verbose
    
    # Test competitive evaluation prompt and save results
    python scripts/test_evaluation_prompt_refactored.py v3_competitive_focused --output results.json
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


class EvaluationPromptTesterRefactored(BaseCLI, TestDataMixin, PromptValidationMixin, OutputFormattingMixin):
    """Test evaluation prompt versions with sample data and analysis - Refactored Version"""
    
    def __init__(self):
        super().__init__(
            tool_name="test_evaluation_prompt_refactored.py",
            description="Test evaluation prompt versions with sample data and analysis"
        )

    def setup_parser(self) -> argparse.ArgumentParser:
        """Setup argument parser"""
        parser = argparse.ArgumentParser(
            description=self.description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Test cultural-focused evaluation prompt with 10 samples
  python scripts/test_evaluation_prompt_refactored.py v2_cultural_focused --sample-size 10
  
  # Test current evaluation prompt with verbose output  
  python scripts/test_evaluation_prompt_refactored.py current --verbose
  
  # Test competitive evaluation prompt and save results
  python scripts/test_evaluation_prompt_refactored.py v3_competitive_focused --output results.json
            """
        )
        
        parser.add_argument(
            'evaluation_prompt_version',
            help='Evaluation prompt version to test (e.g., current, v2_cultural_focused)'
        )
        
        add_sample_size_arg(parser, default=5)
        setup_common_args(parser)
        
        return parser

    def test_prompt_version(self, version: str, sample_size: int) -> Dict[str, Any]:
        """Test evaluation prompt version with sample data"""
        # Validate prompt version
        prompt_manager = self.EvaluationPromptManager()
        self.validate_prompt_version(version, prompt_manager)
        
        # Initialize evaluator
        evaluator = self.SEOEvaluator(
            api_key=self.api_key,
            evaluation_prompt_version=version
        )
        
        if self.verbose:
            self.print_section_header(f"TESTING EVALUATION PROMPT: {version}")
            print(f"Sample Size: {sample_size}")
            
            # Show prompt metadata
            metadata = evaluator.prompt_metadata
            print(f"Description: {metadata.get('description', 'No description')}")
            print(f"Focus Areas: {', '.join(metadata.get('focus_areas', ['general']))}")
            print()
        
        # Get test cases
        test_cases = self.get_test_subset(sample_size)
        
        results = []
        total_scores = {dim: 0.0 for dim in self.DEFAULT_SCORING_DIMENSIONS}
        overall_total = 0.0
        
        for i, test_case in enumerate(test_cases):
            if self.verbose:
                print(f"Testing {i+1}/{len(test_cases)}: {test_case['slug']}")
            
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
                for dim in self.DEFAULT_SCORING_DIMENSIONS:
                    if dim in result.get('dimension_scores', {}):
                        total_scores[dim] += result['dimension_scores'][dim]
                
                overall_total += result.get('overall_score', 0.0)
                
            except Exception as e:
                print(f"Warning: Failed to evaluate test case {i+1}: {e}")
                continue
        
        # Calculate averages
        count = len(results)
        if count == 0:
            raise ValueError("No test cases could be evaluated successfully.")
        
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

    def analyze_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test results and generate insights"""
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
                insights['strengths'].append(f"Excellent {self.format_dimension_name(dim)} scoring ({self.format_score_display(score)})")
            elif score >= 0.7:
                insights['strengths'].append(f"Strong {self.format_dimension_name(dim)} evaluation ({self.format_score_display(score)})")
        
        for dim, score in improvements:
            if score < 0.6:
                insights['improvements'].append(f"Low {self.format_dimension_name(dim)} scoring ({self.format_score_display(score)}) - consider prompt refinement")
            elif score < 0.7:
                insights['improvements'].append(f"Moderate {self.format_dimension_name(dim)} performance ({self.format_score_display(score)}) - room for improvement")
        
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
        
        insights['overall_assessment'] = f"{performance_assessment} ({self.format_score_display(overall_score)})"
        
        return insights

    def print_console_results(self, results: Dict[str, Any], insights: Dict[str, Any]) -> None:
        """Print human-readable results to console"""
        self.print_section_header(f"TESTING EVALUATION PROMPT: {results['evaluation_prompt_version']}")
        print(f"Sample Size: {results['sample_size']}")
        print()
        
        print("Evaluation Results:")
        summary = results['summary']
        self.print_score_line("Overall Score", summary['avg_overall_score'])
        
        # Show dimension scores
        for dim, score in summary['avg_dimension_scores'].items():
            self.print_score_line(self.format_dimension_name(dim), score)
        print()
        
        # Show insights
        if insights.get('overall_assessment'):
            print(f"✨ {insights['overall_assessment']}")
            print()
        
        if insights.get('strengths'):
            print("✅ Strengths:")
            self.print_bullet_list(insights['strengths'], "-")
            print()
        
        if insights.get('improvements'):
            print("⚠️ Areas for improvement:")
            self.print_bullet_list(insights['improvements'], "-")
            print()

    def run_command(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Execute the main testing logic"""
        # Validate sample size
        self.validate_sample_size(args.sample_size)
        
        # Run tests
        start_time = time.time()
        results = self.test_prompt_version(args.evaluation_prompt_version, args.sample_size)
        
        # Analyze results
        insights = self.analyze_results(results)
        
        # Add insights to results for JSON export
        results['analysis'] = insights
        
        # Output results if not in verbose mode
        if not self.verbose:
            self.print_console_results(results, insights)
        
        elapsed = time.time() - start_time
        if self.verbose:
            print(f"Testing completed in {elapsed:.1f} seconds.")
        
        return results


def main():
    """Main CLI entry point"""
    tester = EvaluationPromptTesterRefactored()
    tester.run()


if __name__ == '__main__':
    main()