#!/usr/bin/env python3
"""
Pre-flight validation CLI for the slug generator
Prevents the 2+ hour debugging issues by validating setup upfront
"""

import sys
import os
import argparse
import json
from pathlib import Path
from typing import Dict, Any

# Add src and tests directories to path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, project_root)

try:
    from config.settings import SlugGeneratorConfig
    from tests.unit.test_validation_pipeline import PreFlightValidator
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the project root and src/ directory exists")
    sys.exit(1)


class ValidationCLI:
    """CLI interface for pre-flight validation"""
    
    def __init__(self):
        self.validator = PreFlightValidator()
    
    def validate_environment(self) -> Dict[str, Any]:
        """Validate development environment setup"""
        results = {
            'environment': {
                'python_version': sys.version,
                'working_directory': os.getcwd(),
                'src_path_accessible': os.path.exists('src'),
                'venv_active': hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
            },
            'passed': True,
            'errors': [],
            'warnings': []
        }
        
        if not results['environment']['src_path_accessible']:
            results['errors'].append("src/ directory not found - run from project root")
            results['passed'] = False
        
        if not results['environment']['venv_active']:
            results['warnings'].append("Virtual environment not detected - consider activating venv")
        
        return results
    
    def validate_version_setup(self, version: str = None) -> Dict[str, Any]:
        """Validate specific version setup"""
        return self.validator.run_full_validation(version)
    
    def validate_all_versions(self) -> Dict[str, Any]:
        """Validate all available versions"""
        results = {
            'all_versions': {},
            'summary': {
                'total_versions': 0,
                'passing_versions': 0,
                'failing_versions': 0
            }
        }
        
        # Test known versions
        versions_to_test = ['current', 'v6', 'v7', 'v8', 'v9']
        
        for version in versions_to_test:
            try:
                version_result = self.validator.run_full_validation(version)
                results['all_versions'][version] = version_result
                results['summary']['total_versions'] += 1
                
                if version_result['passed']:
                    results['summary']['passing_versions'] += 1
                else:
                    results['summary']['failing_versions'] += 1
                    
            except Exception as e:
                results['all_versions'][version] = {
                    'passed': False,
                    'errors': [f"Validation failed: {e}"],
                    'version': version
                }
                results['summary']['total_versions'] += 1
                results['summary']['failing_versions'] += 1
        
        return results
    
    def quick_validation(self, version: str = None) -> bool:
        """Quick validation for development - returns True if ready to proceed"""
        try:
            env_result = self.validate_environment()
            version_result = self.validate_version_setup(version)
            
            return env_result['passed'] and version_result['passed']
        except Exception:
            return False
    
    def print_validation_results(self, results: Dict[str, Any], verbose: bool = False):
        """Print validation results in a readable format"""
        if 'environment' in results:
            print("🔧 Environment Validation:")
            env = results['environment']
            print(f"  Python: {env['python_version'][:20]}...")
            print(f"  Working Dir: {env['working_directory']}")
            print(f"  Src Accessible: {'✅' if env['src_path_accessible'] else '❌'}")
            print(f"  Venv Active: {'✅' if env['venv_active'] else '⚠️'}")
            print()
        
        if 'version' in results:
            version = results['version']
            status = '✅ PASS' if results['passed'] else '❌ FAIL'
            print(f"🎯 Version {version} Validation: {status}")
            
            if results['errors']:
                print("  ❌ Errors:")
                for error in results['errors']:
                    print(f"    • {error}")
            
            if results['warnings']:
                print("  ⚠️  Warnings:")
                for warning in results['warnings']:
                    print(f"    • {warning}")
            print()
        
        if 'all_versions' in results:
            print("📊 All Versions Summary:")
            summary = results['summary']
            print(f"  Total: {summary['total_versions']}, Passing: {summary['passing_versions']}, Failing: {summary['failing_versions']}")
            
            for version, result in results['all_versions'].items():
                status = '✅' if result['passed'] else '❌'
                print(f"  {version}: {status}")
                
                if verbose and not result['passed']:
                    for error in result.get('errors', []):
                        print(f"    • {error}")
            print()
    
    def run_interactive_validation(self):
        """Run interactive validation with user prompts"""
        print("🚀 Slug Generator Pre-Flight Validation")
        print("=" * 50)
        
        # Environment check
        print("Step 1: Environment validation...")
        env_result = self.validate_environment()
        self.print_validation_results(env_result)
        
        if not env_result['passed']:
            print("❌ Environment validation failed. Please fix issues before continuing.")
            return False
        
        # Version selection
        print("Step 2: Version validation...")
        version = input("Enter version to validate (default: current): ").strip() or None
        
        version_result = self.validate_version_setup(version)
        self.print_validation_results(version_result)
        
        if version_result['passed']:
            print("✅ Ready for development!")
            return True
        else:
            print("❌ Version validation failed. Please fix issues before development.")
            return False


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Pre-flight validation for slug generator development'
    )
    parser.add_argument(
        '--version', '-v',
        help='Specific version to validate (default: current)'
    )
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Validate all available versions'
    )
    parser.add_argument(
        '--quick', '-q',
        action='store_true',
        help='Quick validation (exit code only)'
    )
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Interactive validation with prompts'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output with detailed error information'
    )
    
    args = parser.parse_args()
    
    cli = ValidationCLI()
    
    try:
        if args.interactive:
            success = cli.run_interactive_validation()
            sys.exit(0 if success else 1)
        
        elif args.quick:
            success = cli.quick_validation(args.version)
            if not args.json:
                print('✅ Ready' if success else '❌ Issues found')
            sys.exit(0 if success else 1)
        
        elif args.all:
            results = cli.validate_all_versions()
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                cli.print_validation_results(results, args.verbose)
            
            success = results['summary']['failing_versions'] == 0
            sys.exit(0 if success else 1)
        
        else:
            # Single version validation
            env_result = cli.validate_environment()
            version_result = cli.validate_version_setup(args.version)
            
            if args.json:
                combined_result = {
                    'environment': env_result,
                    'version_validation': version_result,
                    'overall_passed': env_result['passed'] and version_result['passed']
                }
                print(json.dumps(combined_result, indent=2))
            else:
                cli.print_validation_results(env_result, args.verbose)
                cli.print_validation_results(version_result, args.verbose)
                
                if env_result['passed'] and version_result['passed']:
                    print("🎉 All validations passed! Ready for development.")
                else:
                    print("❌ Validation failed. Please fix issues before proceeding.")
            
            success = env_result['passed'] and version_result['passed']
            sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print("\n⚠️  Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        if args.json:
            error_result = {
                'error': str(e),
                'passed': False
            }
            print(json.dumps(error_result, indent=2))
        else:
            print(f"❌ Validation error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()