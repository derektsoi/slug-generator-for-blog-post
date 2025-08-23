#!/usr/bin/env python3
"""
Evaluation Prompt Validation CLI Script (Refactored)

Validate evaluation prompt configuration, metadata, and functionality.
Test runtime configuration features and automated fixing capabilities.

Usage:
    python scripts/validate_evaluation_prompt_refactored.py v2_cultural_focused --comprehensive
    python scripts/validate_evaluation_prompt_refactored.py current --verbose --test-config
    python scripts/validate_evaluation_prompt_refactored.py v3_competitive_focused --output validation.json

Examples:
    # Comprehensive validation of cultural-focused evaluation prompt
    python scripts/validate_evaluation_prompt_refactored.py v2_cultural_focused --comprehensive
    
    # Validate current evaluation prompt with configuration testing
    python scripts/validate_evaluation_prompt_refactored.py current --verbose --test-config
    
    # Validate competitive evaluation prompt and save results
    python scripts/validate_evaluation_prompt_refactored.py v3_competitive_focused --output results.json
"""

import argparse
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple
import sys

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from cli import BaseCLI, TestDataMixin, PromptValidationMixin, OutputFormattingMixin, setup_common_args


class EvaluationPromptValidatorRefactored(BaseCLI, TestDataMixin, PromptValidationMixin, OutputFormattingMixin):
    """Validate evaluation prompt configuration and functionality - Refactored Version"""
    
    def __init__(self):
        super().__init__(
            tool_name="validate_evaluation_prompt_refactored.py",
            description="Validate evaluation prompt configuration and functionality"
        )

    def setup_parser(self) -> argparse.ArgumentParser:
        """Setup argument parser"""
        parser = argparse.ArgumentParser(
            description=self.description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Comprehensive validation of cultural-focused evaluation prompt
  python scripts/validate_evaluation_prompt_refactored.py v2_cultural_focused --comprehensive
  
  # Validate current evaluation prompt with configuration testing
  python scripts/validate_evaluation_prompt_refactored.py current --verbose --test-config
  
  # Validate competitive evaluation prompt and save results
  python scripts/validate_evaluation_prompt_refactored.py v3_competitive_focused --output results.json
            """
        )
        
        parser.add_argument(
            'evaluation_prompt_version',
            help='Evaluation prompt version to validate'
        )
        
        parser.add_argument(
            '--comprehensive',
            action='store_true',
            help='Run comprehensive validation including performance tests'
        )
        
        parser.add_argument(
            '--test-config',
            action='store_true', 
            help='Test runtime configuration features'
        )
        
        parser.add_argument(
            '--auto-fix',
            action='store_true',
            help='Automatically fix detected issues where possible'
        )
        
        setup_common_args(parser)
        
        return parser

    def validate_prompt_structure(self, version: str) -> Dict[str, Any]:
        """Validate prompt structure and metadata"""
        validation_results = {
            'prompt_file_exists': False,
            'metadata_file_exists': False,
            'prompt_content_valid': False,
            'metadata_structure_valid': False,
            'focus_areas_valid': False,
            'issues': [],
            'warnings': []
        }
        
        try:
            prompt_manager = self.EvaluationPromptManager()
            
            # Check if version exists
            available_versions = prompt_manager.list_available_versions()
            if version not in available_versions:
                validation_results['issues'].append(f"Version '{version}' not found in available versions")
                return validation_results
            
            # Test prompt loading
            try:
                prompt_content = prompt_manager.get_prompt(version)
                validation_results['prompt_file_exists'] = True
                validation_results['prompt_content_valid'] = len(prompt_content.strip()) > 100  # Reasonable minimum
                
                if not validation_results['prompt_content_valid']:
                    validation_results['issues'].append("Prompt content appears too short")
                    
            except Exception as e:
                validation_results['issues'].append(f"Failed to load prompt: {e}")
            
            # Test metadata loading
            try:
                metadata = prompt_manager.get_metadata(version)
                validation_results['metadata_file_exists'] = True
                
                # Validate metadata structure
                required_fields = ['description', 'focus_areas', 'version', 'created']
                missing_fields = [field for field in required_fields if field not in metadata]
                
                if not missing_fields:
                    validation_results['metadata_structure_valid'] = True
                else:
                    validation_results['issues'].append(f"Missing metadata fields: {missing_fields}")
                
                # Validate focus areas
                if 'focus_areas' in metadata and isinstance(metadata['focus_areas'], list):
                    validation_results['focus_areas_valid'] = len(metadata['focus_areas']) > 0
                    if not validation_results['focus_areas_valid']:
                        validation_results['warnings'].append("No focus areas specified in metadata")
                else:
                    validation_results['issues'].append("Invalid focus_areas format in metadata")
                    
            except Exception as e:
                validation_results['issues'].append(f"Failed to load metadata: {e}")
        
        except Exception as e:
            validation_results['issues'].append(f"Prompt manager initialization failed: {e}")
        
        return validation_results

    def test_basic_functionality(self, version: str) -> Dict[str, Any]:
        """Test basic evaluation functionality"""
        functionality_results = {
            'evaluator_initialization': False,
            'basic_evaluation': False,
            'dimension_scoring': False,
            'overall_scoring': False,
            'issues': [],
            'sample_result': None
        }
        
        try:
            # Initialize evaluator
            evaluator = self.SEOEvaluator(
                api_key=self.api_key,
                evaluation_prompt_version=version
            )
            functionality_results['evaluator_initialization'] = True
            
            # Test basic evaluation with a simple test case
            test_case = self.standard_test_cases[0]
            
            try:
                result = evaluator.evaluate_slug(
                    test_case['slug'],
                    test_case['title'],
                    test_case['content']
                )
                
                functionality_results['basic_evaluation'] = True
                functionality_results['sample_result'] = result
                
                # Check result structure
                if 'dimension_scores' in result:
                    dimension_scores = result['dimension_scores']
                    if isinstance(dimension_scores, dict) and len(dimension_scores) > 0:
                        functionality_results['dimension_scoring'] = True
                    else:
                        functionality_results['issues'].append("Invalid dimension scores structure")
                else:
                    functionality_results['issues'].append("No dimension scores in result")
                
                if 'overall_score' in result and isinstance(result['overall_score'], (int, float)):
                    functionality_results['overall_scoring'] = True
                else:
                    functionality_results['issues'].append("Invalid overall score in result")
                    
            except Exception as e:
                functionality_results['issues'].append(f"Evaluation failed: {e}")
                
        except Exception as e:
            functionality_results['issues'].append(f"Evaluator initialization failed: {e}")
        
        return functionality_results

    def test_configuration_features(self, version: str) -> Dict[str, Any]:
        """Test runtime configuration capabilities"""
        config_results = {
            'configure_context_available': False,
            'focus_areas_modification': False,
            'quality_thresholds_modification': False,
            'evaluation_style_modification': False,
            'issues': [],
            'test_results': []
        }
        
        try:
            evaluator = self.SEOEvaluator(
                api_key=self.api_key,
                evaluation_prompt_version=version
            )
            
            # Check if configure_context method exists
            if hasattr(evaluator, 'configure_context'):
                config_results['configure_context_available'] = True
                
                # Test focus areas modification
                try:
                    evaluator.configure_context({
                        'focus_areas': ['cultural_authenticity', 'brand_hierarchy']
                    })
                    config_results['focus_areas_modification'] = True
                    config_results['test_results'].append("Focus areas configuration: SUCCESS")
                except Exception as e:
                    config_results['issues'].append(f"Focus areas modification failed: {e}")
                
                # Test quality thresholds modification
                try:
                    evaluator.configure_context({
                        'quality_thresholds': {'minimum_score': 0.8, 'excellence_score': 0.9}
                    })
                    config_results['quality_thresholds_modification'] = True
                    config_results['test_results'].append("Quality thresholds configuration: SUCCESS")
                except Exception as e:
                    config_results['issues'].append(f"Quality thresholds modification failed: {e}")
                
                # Test evaluation style modification
                try:
                    evaluator.configure_context({
                        'evaluation_style': 'strict'
                    })
                    config_results['evaluation_style_modification'] = True
                    config_results['test_results'].append("Evaluation style configuration: SUCCESS")
                except Exception as e:
                    config_results['issues'].append(f"Evaluation style modification failed: {e}")
            else:
                config_results['issues'].append("configure_context method not available")
        
        except Exception as e:
            config_results['issues'].append(f"Configuration testing failed: {e}")
        
        return config_results

    def run_performance_test(self, version: str) -> Dict[str, Any]:
        """Run basic performance test"""
        performance_results = {
            'test_completed': False,
            'average_score': 0.0,
            'score_distribution': {},
            'issues': []
        }
        
        try:
            evaluator = self.SEOEvaluator(
                api_key=self.api_key,
                evaluation_prompt_version=version
            )
            
            # Test with a small subset
            test_cases = self.get_test_subset(3)  # Small sample for validation
            results = []
            
            for test_case in test_cases:
                try:
                    result = evaluator.evaluate_slug(
                        test_case['slug'],
                        test_case['title'],
                        test_case['content']
                    )
                    results.append(result['overall_score'])
                except Exception as e:
                    performance_results['issues'].append(f"Performance test case failed: {e}")
            
            if results:
                performance_results['test_completed'] = True
                performance_results['average_score'] = sum(results) / len(results)
                
                # Score distribution
                score_ranges = {
                    'excellent (≥0.8)': sum(1 for s in results if s >= 0.8),
                    'good (0.6-0.8)': sum(1 for s in results if 0.6 <= s < 0.8),
                    'needs_improvement (<0.6)': sum(1 for s in results if s < 0.6)
                }
                performance_results['score_distribution'] = score_ranges
            else:
                performance_results['issues'].append("No performance test results obtained")
        
        except Exception as e:
            performance_results['issues'].append(f"Performance testing failed: {e}")
        
        return performance_results

    def print_validation_results(self, version: str, structure_results: Dict[str, Any],
                                functionality_results: Dict[str, Any], 
                                config_results: Dict[str, Any] = None,
                                performance_results: Dict[str, Any] = None) -> None:
        """Print comprehensive validation results"""
        self.print_section_header(f"EVALUATION PROMPT VALIDATION: {version}")
        
        # Structure Validation
        self.print_subsection_header("Structure Validation")
        self.print_status_line("Prompt file exists", structure_results['prompt_file_exists'])
        self.print_status_line("Metadata file exists", structure_results['metadata_file_exists'])
        self.print_status_line("Prompt content valid", structure_results['prompt_content_valid'])
        self.print_status_line("Metadata structure valid", structure_results['metadata_structure_valid'])
        self.print_status_line("Focus areas valid", structure_results['focus_areas_valid'])
        
        # Functionality Validation
        self.print_subsection_header("Functionality Validation")
        self.print_status_line("Evaluator initialization", functionality_results['evaluator_initialization'])
        self.print_status_line("Basic evaluation", functionality_results['basic_evaluation'])
        self.print_status_line("Dimension scoring", functionality_results['dimension_scoring'])
        self.print_status_line("Overall scoring", functionality_results['overall_scoring'])
        
        # Configuration Testing
        if config_results:
            self.print_subsection_header("Configuration Testing")
            self.print_status_line("configure_context available", config_results['configure_context_available'])
            self.print_status_line("Focus areas modification", config_results['focus_areas_modification'])
            self.print_status_line("Quality thresholds modification", config_results['quality_thresholds_modification'])
            self.print_status_line("Evaluation style modification", config_results['evaluation_style_modification'])
            
            if config_results['test_results']:
                print("\nConfiguration Test Results:")
                self.print_bullet_list(config_results['test_results'], "•")
        
        # Performance Testing
        if performance_results:
            self.print_subsection_header("Performance Testing")
            self.print_status_line("Performance test completed", performance_results['test_completed'])
            
            if performance_results['test_completed']:
                self.print_score_line("Average score", performance_results['average_score'])
                
                print("\nScore Distribution:")
                for range_name, count in performance_results['score_distribution'].items():
                    print(f"  • {range_name}: {count} cases")
        
        # Issues and Warnings
        all_issues = structure_results['issues'] + functionality_results['issues']
        if config_results:
            all_issues.extend(config_results['issues'])
        if performance_results:
            all_issues.extend(performance_results['issues'])
        
        if all_issues:
            self.print_subsection_header("Issues Found")
            self.print_bullet_list(all_issues, "⚠️")
        
        if structure_results.get('warnings'):
            self.print_subsection_header("Warnings")
            self.print_bullet_list(structure_results['warnings'], "⚡")
        
        # Overall Status
        all_core_checks = [
            structure_results['prompt_file_exists'],
            structure_results['metadata_file_exists'], 
            structure_results['prompt_content_valid'],
            functionality_results['evaluator_initialization'],
            functionality_results['basic_evaluation']
        ]
        
        overall_status = all(all_core_checks) and not all_issues
        status_symbol = "✅" if overall_status else "❌"
        status_text = "VALIDATION PASSED" if overall_status else "VALIDATION FAILED"
        
        print(f"\n{status_symbol} {status_text}")

    def run_command(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Execute the main validation logic"""
        version = args.evaluation_prompt_version
        
        # Validate prompt version exists
        prompt_manager = self.EvaluationPromptManager()
        self.validate_prompt_version(version, prompt_manager)
        
        if self.verbose:
            self.print_section_header(f"VALIDATING EVALUATION PROMPT: {version}")
            metadata = prompt_manager.get_metadata(version)
            print(f"Description: {metadata.get('description', 'No description')}")
            print(f"Focus Areas: {', '.join(metadata.get('focus_areas', ['general']))}")
            print()
        
        start_time = time.time()
        
        # Run validations
        structure_results = self.validate_prompt_structure(version)
        functionality_results = self.test_basic_functionality(version)
        
        config_results = None
        if args.test_config:
            config_results = self.test_configuration_features(version)
        
        performance_results = None
        if args.comprehensive:
            performance_results = self.run_performance_test(version)
        
        # Prepare results
        results = {
            'evaluation_prompt_version': version,
            'validation_type': 'comprehensive' if args.comprehensive else 'standard',
            'structure_validation': structure_results,
            'functionality_validation': functionality_results
        }
        
        if config_results:
            results['configuration_validation'] = config_results
        
        if performance_results:
            results['performance_validation'] = performance_results
        
        # Output results if not in verbose mode
        if not self.verbose:
            self.print_validation_results(
                version, structure_results, functionality_results, 
                config_results, performance_results
            )
        
        elapsed = time.time() - start_time
        if self.verbose:
            print(f"Validation completed in {elapsed:.1f} seconds.")
        
        return results


def main():
    """Main CLI entry point"""
    validator = EvaluationPromptValidatorRefactored()
    validator.run()


if __name__ == '__main__':
    main()