#!/usr/bin/env python3
"""
Evaluation Prompt Validation CLI Script

Validate evaluation prompt configurations and metadata to ensure they meet
quality standards and are properly configured for use in the evaluation system.

Usage:
    python scripts/validate_evaluation_prompt.py v2_cultural_focused
    python scripts/validate_evaluation_prompt.py current --verbose
    python scripts/validate_evaluation_prompt.py v3_competitive_focused --output validation.json
    python scripts/validate_evaluation_prompt.py --all

Examples:
    # Validate a specific evaluation prompt
    python scripts/validate_evaluation_prompt.py v2_cultural_focused
    
    # Validate with detailed output
    python scripts/validate_evaluation_prompt.py current --verbose
    
    # Validate all prompts with summary
    python scripts/validate_evaluation_prompt.py --all
    
    # Validate and attempt fixes
    python scripts/validate_evaluation_prompt.py current --fix
"""

import argparse
import json
import sys
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    from config.evaluation_prompt_manager import EvaluationPromptManager
    from config.constants import DEFAULT_SCORING_DIMENSIONS
except ImportError as e:
    print(f"Error: Failed to import required modules: {e}")
    print("Please ensure you're running from the project root directory.")
    sys.exit(1)


class EvaluationPromptValidator:
    """Validate evaluation prompt configurations and metadata"""
    
    def __init__(self, verbose: bool = False):
        """Initialize validator"""
        self.verbose = verbose
        self.prompt_manager = EvaluationPromptManager()
        
        # Required template placeholders
        self.required_placeholders = ['{slug}', '{title}', '{content}']
        
        # Required metadata fields
        self.required_metadata_fields = [
            'prompt_version',
            'scoring_dimensions',
            'dimension_weights'
        ]

    def validate_prompt_configuration(self, version: str) -> Dict[str, Any]:
        """Validate a single evaluation prompt configuration"""
        validation_result = {
            'prompt_version': version,
            'validation_timestamp': datetime.now().isoformat(),
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'file_checks': {},
            'metadata_checks': {},
            'configuration_checks': {},
            'recommendations': []
        }
        
        try:
            # Check if prompt version exists
            available_versions = self.prompt_manager.list_available_versions()
            if version not in available_versions:
                validation_result['is_valid'] = False
                validation_result['errors'].append(f"Evaluation prompt version '{version}' not found")
                validation_result['recommendations'].append(f"Available versions: {', '.join(sorted(available_versions))}")
                return validation_result
            
            if self.verbose:
                print(f"✓ Prompt version '{version}' exists")
            
            # Validate prompt file
            file_validation = self._validate_prompt_file(version)
            validation_result['file_checks'] = file_validation
            if not file_validation['is_valid']:
                validation_result['is_valid'] = False
                validation_result['errors'].extend(file_validation['errors'])
            validation_result['warnings'].extend(file_validation.get('warnings', []))
            
            # Validate metadata file  
            metadata_validation = self._validate_metadata_file(version)
            validation_result['metadata_checks'] = metadata_validation
            if not metadata_validation['is_valid']:
                validation_result['is_valid'] = False
                validation_result['errors'].extend(metadata_validation['errors'])
            validation_result['warnings'].extend(metadata_validation.get('warnings', []))
            
            # Validate configuration consistency
            config_validation = self._validate_configuration_consistency(version)
            validation_result['configuration_checks'] = config_validation
            if not config_validation['is_valid']:
                validation_result['is_valid'] = False
                validation_result['errors'].extend(config_validation['errors'])
            validation_result['warnings'].extend(config_validation.get('warnings', []))
            
            # Generate recommendations
            validation_result['recommendations'].extend(
                self._generate_recommendations(validation_result)
            )
            
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Validation failed with exception: {str(e)}")
        
        return validation_result

    def _validate_prompt_file(self, version: str) -> Dict[str, Any]:
        """Validate prompt template file"""
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'file_exists': False,
            'file_readable': False,
            'template_valid': False,
            'placeholders_present': []
        }
        
        try:
            # Check if file exists and is readable
            prompt_content = self.prompt_manager.load_prompt_template(version)
            result['file_exists'] = True
            result['file_readable'] = True
            
            if self.verbose:
                print(f"✓ Prompt file exists and is readable")
            
            # Validate template placeholders
            missing_placeholders = []
            for placeholder in self.required_placeholders:
                if placeholder in prompt_content:
                    result['placeholders_present'].append(placeholder)
                else:
                    missing_placeholders.append(placeholder)
            
            if missing_placeholders:
                result['is_valid'] = False
                result['errors'].append(f"Missing required placeholders: {', '.join(missing_placeholders)}")
            else:
                result['template_valid'] = True
                if self.verbose:
                    print(f"✓ All required placeholders present: {', '.join(self.required_placeholders)}")
            
            # Check template length
            if len(prompt_content) < 100:
                result['warnings'].append("Prompt template appears unusually short")
            elif len(prompt_content) > 5000:
                result['warnings'].append("Prompt template appears unusually long - may impact performance")
            
            # Check for common formatting issues
            if '{' in prompt_content and '}' in prompt_content:
                # Check for unmatched braces
                open_braces = prompt_content.count('{')
                close_braces = prompt_content.count('}')
                if open_braces != close_braces:
                    result['warnings'].append("Unmatched braces detected - check template formatting")
            
        except FileNotFoundError:
            result['is_valid'] = False
            result['errors'].append(f"Prompt file not found for version '{version}'")
        except Exception as e:
            result['is_valid'] = False
            result['errors'].append(f"Failed to read prompt file: {str(e)}")
        
        return result

    def _validate_metadata_file(self, version: str) -> Dict[str, Any]:
        """Validate metadata JSON file"""
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'file_exists': False,
            'json_valid': False,
            'required_fields_present': [],
            'structure_valid': False
        }
        
        try:
            # Load and validate metadata
            metadata = self.prompt_manager.get_prompt_metadata(version)
            result['file_exists'] = True
            result['json_valid'] = True
            
            if self.verbose:
                print(f"✓ Metadata file exists and contains valid JSON")
            
            # Check required fields
            missing_fields = []
            for field in self.required_metadata_fields:
                if field in metadata:
                    result['required_fields_present'].append(field)
                else:
                    missing_fields.append(field)
            
            if missing_fields:
                result['is_valid'] = False
                result['errors'].append(f"Missing required metadata fields: {', '.join(missing_fields)}")
            else:
                if self.verbose:
                    print(f"✓ All required metadata fields present")
            
            # Validate scoring dimensions
            if 'scoring_dimensions' in metadata:
                dimensions = metadata['scoring_dimensions']
                if not isinstance(dimensions, list):
                    result['is_valid'] = False
                    result['errors'].append("scoring_dimensions must be a list")
                elif not dimensions:
                    result['is_valid'] = False
                    result['errors'].append("scoring_dimensions cannot be empty")
                else:
                    if self.verbose:
                        print(f"✓ Scoring dimensions: {len(dimensions)} dimensions defined")
            
            # Validate dimension weights
            if 'dimension_weights' in metadata:
                weights = metadata['dimension_weights']
                if not isinstance(weights, dict):
                    result['is_valid'] = False
                    result['errors'].append("dimension_weights must be a dictionary")
                else:
                    # Check weight sum
                    weight_sum = sum(weights.values())
                    if abs(weight_sum - 1.0) > 0.01:
                        result['warnings'].append(f"Dimension weights sum to {weight_sum:.3f}, not 1.0")
                    else:
                        if self.verbose:
                            print(f"✓ Dimension weights sum to {weight_sum:.3f}")
                    
                    # Check for negative weights
                    negative_weights = [k for k, v in weights.items() if v < 0]
                    if negative_weights:
                        result['is_valid'] = False
                        result['errors'].append(f"Negative weights not allowed: {', '.join(negative_weights)}")
            
            if not result['errors']:
                result['structure_valid'] = True
            
        except Exception as e:
            result['is_valid'] = False
            result['errors'].append(f"Failed to validate metadata: {str(e)}")
        
        return result

    def _validate_configuration_consistency(self, version: str) -> Dict[str, Any]:
        """Validate consistency between prompt and metadata"""
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'dimensions_consistent': False,
            'weights_consistent': False
        }
        
        try:
            metadata = self.prompt_manager.get_prompt_metadata(version)
            
            # Check dimensions and weights consistency
            if 'scoring_dimensions' in metadata and 'dimension_weights' in metadata:
                dimensions = set(metadata['scoring_dimensions'])
                weight_keys = set(metadata['dimension_weights'].keys())
                
                if dimensions == weight_keys:
                    result['dimensions_consistent'] = True
                    result['weights_consistent'] = True
                    if self.verbose:
                        print(f"✓ Dimensions and weights are consistent")
                else:
                    result['is_valid'] = False
                    missing_weights = dimensions - weight_keys
                    extra_weights = weight_keys - dimensions
                    
                    if missing_weights:
                        result['errors'].append(f"Missing weights for dimensions: {', '.join(missing_weights)}")
                    if extra_weights:
                        result['errors'].append(f"Extra weights for unknown dimensions: {', '.join(extra_weights)}")
            
            # Check against default dimensions
            if 'scoring_dimensions' in metadata:
                config_dimensions = set(metadata['scoring_dimensions'])
                default_dimensions = set(DEFAULT_SCORING_DIMENSIONS)
                
                if config_dimensions != default_dimensions:
                    missing_defaults = default_dimensions - config_dimensions
                    extra_dimensions = config_dimensions - default_dimensions
                    
                    if missing_defaults:
                        result['warnings'].append(f"Missing default dimensions: {', '.join(missing_defaults)}")
                    if extra_dimensions:
                        result['warnings'].append(f"Additional custom dimensions: {', '.join(extra_dimensions)}")
            
        except Exception as e:
            result['is_valid'] = False
            result['errors'].append(f"Failed to validate configuration consistency: {str(e)}")
        
        return result

    def _generate_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on validation"""
        recommendations = []
        
        if validation_result['is_valid']:
            recommendations.append("✓ Configuration is valid and ready for use")
        else:
            recommendations.append("⚠️ Configuration has issues that need to be resolved")
        
        # File-specific recommendations
        file_checks = validation_result.get('file_checks', {})
        if not file_checks.get('template_valid', False):
            recommendations.append("Fix template placeholder issues before using this prompt version")
        
        # Metadata-specific recommendations
        metadata_checks = validation_result.get('metadata_checks', {})
        if metadata_checks.get('warnings'):
            recommendations.append("Review metadata warnings for optimal configuration")
        
        # Performance recommendations
        if any('long' in warning for warning in validation_result.get('warnings', [])):
            recommendations.append("Consider optimizing prompt length for better API performance")
        
        return recommendations

    def validate_all_prompts(self) -> Dict[str, Any]:
        """Validate all available evaluation prompts"""
        try:
            available_versions = self.prompt_manager.list_available_versions()
            
            if self.verbose:
                print(f"Validating {len(available_versions)} evaluation prompt versions...")
                print()
            
            results = {}
            valid_count = 0
            total_errors = 0
            total_warnings = 0
            
            for version in sorted(available_versions):
                if self.verbose:
                    print(f"Validating {version}...")
                
                validation = self.validate_prompt_configuration(version)
                results[version] = validation
                
                if validation['is_valid']:
                    valid_count += 1
                    if self.verbose:
                        print(f"  ✓ Valid")
                else:
                    if self.verbose:
                        print(f"  ✗ Invalid ({len(validation['errors'])} errors)")
                
                total_errors += len(validation['errors'])
                total_warnings += len(validation['warnings'])
                
                if self.verbose:
                    print()
            
            summary = {
                'total_prompts': len(available_versions),
                'valid_prompts': valid_count,
                'invalid_prompts': len(available_versions) - valid_count,
                'total_errors': total_errors,
                'total_warnings': total_warnings,
                'validation_results': results,
                'overall_status': 'PASS' if valid_count == len(available_versions) else 'FAIL'
            }
            
            return summary
            
        except Exception as e:
            return {
                'error': f"Failed to validate all prompts: {str(e)}",
                'overall_status': 'ERROR'
            }

    def attempt_fixes(self, version: str) -> Dict[str, Any]:
        """Attempt to automatically fix common validation issues"""
        fix_result = {
            'fixes_attempted': [],
            'fixes_successful': [],
            'fixes_failed': [],
            'requires_manual_intervention': []
        }
        
        # This is a placeholder for automatic fixing functionality
        # In a real implementation, this would attempt to fix issues like:
        # - Normalizing dimension weights to sum to 1.0
        # - Adding missing metadata fields with defaults
        # - Fixing common template formatting issues
        
        fix_result['requires_manual_intervention'].append(
            "Automatic fixes not implemented - manual review required"
        )
        
        return fix_result

    def print_console_results(self, validation_result: Dict[str, Any]) -> None:
        """Print human-readable validation results to console"""
        version = validation_result['prompt_version']
        is_valid = validation_result['is_valid']
        
        print(f"📋 VALIDATION RESULTS: {version}")
        print("=" * 50)
        
        # Overall status
        status = "✅ VALID" if is_valid else "❌ INVALID"
        print(f"Overall Status: {status}")
        print()
        
        # File checks
        file_checks = validation_result.get('file_checks', {})
        print("File Checks:")
        print(f"  • File exists: {'✓' if file_checks.get('file_exists') else '✗'}")
        print(f"  • File readable: {'✓' if file_checks.get('file_readable') else '✗'}")
        print(f"  • Template valid: {'✓' if file_checks.get('template_valid') else '✗'}")
        print()
        
        # Metadata checks
        metadata_checks = validation_result.get('metadata_checks', {})
        print("Metadata Checks:")
        print(f"  • JSON valid: {'✓' if metadata_checks.get('json_valid') else '✗'}")
        print(f"  • Structure valid: {'✓' if metadata_checks.get('structure_valid') else '✗'}")
        print()
        
        # Configuration checks
        config_checks = validation_result.get('configuration_checks', {})
        print("Configuration Checks:")
        print(f"  • Dimensions consistent: {'✓' if config_checks.get('dimensions_consistent') else '✗'}")
        print(f"  • Weights consistent: {'✓' if config_checks.get('weights_consistent') else '✗'}")
        print()
        
        # Errors
        if validation_result.get('errors'):
            print("❌ Errors:")
            for error in validation_result['errors']:
                print(f"  • {error}")
            print()
        
        # Warnings
        if validation_result.get('warnings'):
            print("⚠️ Warnings:")
            for warning in validation_result['warnings']:
                print(f"  • {warning}")
            print()
        
        # Recommendations
        if validation_result.get('recommendations'):
            print("💡 Recommendations:")
            for rec in validation_result['recommendations']:
                print(f"  • {rec}")
            print()

    def print_summary_results(self, summary: Dict[str, Any]) -> None:
        """Print summary results for all prompt validation"""
        print("📋 VALIDATION SUMMARY")
        print("=" * 50)
        
        total = summary['total_prompts']
        valid = summary['valid_prompts']
        invalid = summary['invalid_prompts']
        
        print(f"Total prompts: {total}")
        print(f"Valid: {valid} ({'100.0' if total == 0 else f'{valid/total*100:.1f}'}%)")
        print(f"Invalid: {invalid}")
        print(f"Total errors: {summary['total_errors']}")
        print(f"Total warnings: {summary['total_warnings']}")
        print()
        
        status = summary['overall_status']
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"Overall Status: {status_symbol} {status}")
        print()
        
        # Show invalid prompts
        if invalid > 0:
            print("Invalid prompts:")
            for version, result in summary['validation_results'].items():
                if not result['is_valid']:
                    error_count = len(result['errors'])
                    print(f"  • {version} ({error_count} errors)")
            print()

    def save_results(self, results: Dict[str, Any], output_file: str) -> bool:
        """Save validation results to JSON file"""
        try:
            output_data = {
                **results,
                'tool': 'validate_evaluation_prompt.py'
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            if self.verbose:
                print(f"Validation results saved to: {output_file}")
            
            return True
        except Exception as e:
            print(f"Error: Failed to save results to {output_file}: {e}")
            return False


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Validate evaluation prompt configurations and metadata',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate a specific evaluation prompt
  python scripts/validate_evaluation_prompt.py v2_cultural_focused
  
  # Validate with detailed output
  python scripts/validate_evaluation_prompt.py current --verbose
  
  # Validate all prompts with summary
  python scripts/validate_evaluation_prompt.py --all
  
  # Validate and attempt fixes
  python scripts/validate_evaluation_prompt.py current --fix
        """
    )
    
    parser.add_argument(
        'prompt_version',
        nargs='?',
        help='Evaluation prompt version to validate'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Validate all available evaluation prompt versions'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed validation output'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Save validation results to JSON file'
    )
    
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Attempt to automatically fix common issues'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.all and not args.prompt_version:
        print("Error: Either specify a prompt version or use --all to validate all prompts")
        parser.print_help()
        sys.exit(1)
    
    # Initialize validator
    validator = EvaluationPromptValidator(verbose=args.verbose)
    
    try:
        if args.all:
            # Validate all prompts
            results = validator.validate_all_prompts()
            
            if 'error' in results:
                print(f"Error: {results['error']}")
                sys.exit(1)
            
            # Print results
            if not args.verbose:
                validator.print_summary_results(results)
            
            # Save results if requested
            if args.output:
                if not validator.save_results(results, args.output):
                    sys.exit(1)
            
            # Exit with appropriate code
            if results['overall_status'] == 'PASS':
                sys.exit(0)
            else:
                sys.exit(1)
        
        else:
            # Validate single prompt
            validation_result = validator.validate_prompt_configuration(args.prompt_version)
            
            # Attempt fixes if requested
            if args.fix:
                fix_result = validator.attempt_fixes(args.prompt_version)
                validation_result['fix_attempts'] = fix_result
            
            # Print results
            if not args.verbose:
                validator.print_console_results(validation_result)
            
            # Save results if requested
            if args.output:
                if not validator.save_results(validation_result, args.output):
                    sys.exit(1)
            
            # Exit with appropriate code
            if validation_result['is_valid']:
                sys.exit(0)
            else:
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\nValidation cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"Error: Validation failed with unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()