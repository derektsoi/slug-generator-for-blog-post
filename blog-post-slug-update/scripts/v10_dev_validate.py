#!/usr/bin/env python3
"""
V10 Development Validation CLI
Quick pre-flight validation for V10 development with enhanced checks
Prevents V9's 2+ hour debugging issues with comprehensive upfront validation
"""

import sys
import os
import argparse
import json
import time
from pathlib import Path

# Add src directory to path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.join(project_root, 'src'))

try:
    from core.pre_flight_validator import create_enhanced_validator
    from core.exceptions import ValidationError, ConfigurationError
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the project root and src/ directory exists")
    sys.exit(1)


class V10ValidationCLI:
    """Enhanced CLI for V10 development validation"""
    
    def __init__(self, dev_mode: bool = True):
        self.validator = create_enhanced_validator(dev_mode=dev_mode)
        self.dev_mode = dev_mode
    
    def quick_v10_check(self, version: str = None) -> bool:
        """Ultra-fast V10 development check (< 5 seconds)"""
        print("🚀 Quick V10 Development Check...")
        start_time = time.time()
        
        success = self.validator.rapid_validation(version)
        elapsed = time.time() - start_time
        
        if success:
            print(f"✅ Ready for V10 development! ({elapsed:.1f}s)")
        else:
            print(f"❌ Issues found. Run comprehensive check for details. ({elapsed:.1f}s)")
        
        return success
    
    def comprehensive_v10_validation(self, version: str = None) -> Dict[str, Any]:
        """Complete V10 validation with all enhanced checks"""
        print("🔬 Comprehensive V10 Validation...")
        print("Addressing V9 insights: JSON format, configuration consistency, runtime readiness")
        print()
        
        results = self.validator.comprehensive_validation(version)
        
        self._print_comprehensive_results(results)
        return results
    
    def json_format_focus(self, version: str = None) -> Dict[str, Any]:
        """Focus on JSON format validation (V9's main issue)"""
        print("📝 JSON Format Validation (Prevents 2+ Hour Debugging)...")
        
        results = self.validator.validate_json_compatibility(version)
        self._print_focused_results(results, "JSON Format Compatibility")
        
        return results
    
    def configuration_focus(self, version: str = None) -> Dict[str, Any]:
        """Focus on configuration consistency (V9's wrong files issue)"""
        print("⚙️  Configuration Consistency Validation...")
        
        results = self.validator.validate_configuration_consistency(version)
        self._print_focused_results(results, "Configuration Consistency")
        
        return results
    
    def runtime_focus(self, version: str = None) -> Dict[str, Any]:
        """Focus on runtime readiness validation"""
        print("🔗 Runtime Readiness Validation...")
        
        results = self.validator.validate_runtime_readiness(version)
        self._print_focused_results(results, "Runtime Readiness")
        
        return results
    
    def v10_setup_focus(self) -> Dict[str, Any]:
        """Focus on V10-specific development setup"""
        print("🎯 V10 Development Setup Validation...")
        
        results = self.validator.validate_v10_development_setup()
        self._print_focused_results(results, "V10 Development Setup")
        
        return results
    
    def interactive_validation(self):
        """Interactive validation with user guidance"""
        print("🚀 V10 Enhanced Pre-Flight Validation")
        print("=" * 60)
        print("Preventing V9's 2+ hour debugging with comprehensive checks")
        print()
        
        # Step 1: Quick check
        print("Step 1: Quick Development Readiness...")
        quick_success = self.quick_v10_check()
        
        if not quick_success:
            print("\n❌ Quick check failed. Running diagnostic...")
        
        print()
        
        # Step 2: Version selection
        version = input("Enter version to validate (default: current): ").strip() or None
        print()
        
        # Step 3: Comprehensive validation
        print("Step 2: Comprehensive Validation...")
        comprehensive_results = self.comprehensive_v10_validation(version)
        
        # Step 4: Summary and recommendations
        print("\n" + "=" * 60)
        print("🎯 VALIDATION SUMMARY")
        print("=" * 60)
        
        if comprehensive_results['overall_passed']:
            print("✅ All validations passed! Ready for V10 development.")
            print("\nRecommended next steps:")
            print("  1. Create V10 prompt file")
            print("  2. Implement dual-mode generation")
            print("  3. Start with V8 robustness foundation")
        else:
            print("❌ Some validations failed. Please address issues before development.")
            print("\nPriority fixes:")
            
            for check_name, check_result in comprehensive_results['checks'].items():
                if not check_result['passed']:
                    print(f"  • {check_name}: {len(check_result['errors'])} errors")
        
        print(f"\nValidation completed in {comprehensive_results['validation_time']}s")
        return comprehensive_results['overall_passed']
    
    def _print_comprehensive_results(self, results: Dict[str, Any]):
        """Print comprehensive validation results"""
        summary = results['summary']
        
        print(f"📊 Validation Summary:")
        print(f"  Total Checks: {summary['total_checks']}")
        print(f"  Passed: {summary['passed_checks']} ✅")
        print(f"  Failed: {summary['failed_checks']} ❌")
        print(f"  Warnings: {summary['warnings_count']} ⚠️")
        print(f"  Duration: {results['validation_time']}s")
        print()
        
        # Show detailed results for each check
        for check_name, check_result in results['checks'].items():
            self._print_check_result(check_name, check_result)
        
        # Overall result
        status = "✅ PASS" if results['overall_passed'] else "❌ FAIL"
        print(f"🎯 Overall Result: {status}")
        print()
    
    def _print_focused_results(self, results: Dict[str, Any], check_title: str):
        """Print focused validation results for single check"""
        print(f"📋 {check_title}:")
        print(f"  Version: {results['version']}")
        print(f"  Status: {'✅ PASS' if results['passed'] else '❌ FAIL'}")
        
        if results['errors']:
            print(f"  ❌ Errors ({len(results['errors'])}):")
            for error in results['errors']:
                print(f"    • {error}")
        
        if results['warnings']:
            print(f"  ⚠️  Warnings ({len(results['warnings'])}):")
            for warning in results['warnings']:
                print(f"    • {warning}")
        
        if results.get('details'):
            print(f"  📊 Details: {len(results['details'])} items")
            if self.dev_mode:
                for key, value in results['details'].items():
                    print(f"    {key}: {value}")
        
        print()
    
    def _print_check_result(self, check_name: str, check_result: Dict[str, Any]):
        """Print individual check result"""
        status = "✅" if check_result['passed'] else "❌"
        print(f"  {status} {check_name.replace('_', ' ').title()}")
        
        if check_result['errors']:
            for error in check_result['errors']:
                print(f"    ❌ {error}")
        
        if check_result['warnings']:
            for warning in check_result['warnings']:
                print(f"    ⚠️  {warning}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='V10 Enhanced Pre-Flight Validation - Prevents V9 debugging issues'
    )
    parser.add_argument(
        '--version', '-v',
        help='Version to validate (default: current)'
    )
    parser.add_argument(
        '--quick', '-q',
        action='store_true',
        help='Quick validation for rapid development (< 5s)'
    )
    parser.add_argument(
        '--comprehensive', '-c',
        action='store_true',  
        help='Comprehensive validation with all checks'
    )
    parser.add_argument(
        '--json-focus',
        action='store_true',
        help='Focus on JSON format validation (prevents 2+ hour debugging)'
    )
    parser.add_argument(
        '--config-focus',
        action='store_true',
        help='Focus on configuration consistency'
    )
    parser.add_argument(
        '--runtime-focus',
        action='store_true',
        help='Focus on runtime readiness'
    )
    parser.add_argument(
        '--v10-focus',
        action='store_true',
        help='Focus on V10 development setup'
    )
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Interactive validation with guidance'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    parser.add_argument(
        '--production',
        action='store_true',
        help='Production mode (less verbose output)'
    )
    
    args = parser.parse_args()
    
    # Determine mode
    dev_mode = not args.production
    cli = V10ValidationCLI(dev_mode=dev_mode)
    
    try:
        if args.interactive:
            success = cli.interactive_validation()
            sys.exit(0 if success else 1)
        
        elif args.quick:
            success = cli.quick_v10_check(args.version)
            sys.exit(0 if success else 1)
        
        elif args.json_focus:
            results = cli.json_format_focus(args.version)
            success = results['passed']
        
        elif args.config_focus:
            results = cli.configuration_focus(args.version)
            success = results['passed']
        
        elif args.runtime_focus:
            results = cli.runtime_focus(args.version)
            success = results['passed']
        
        elif args.v10_focus:
            results = cli.v10_setup_focus()
            success = results['passed']
        
        else:
            # Default: comprehensive validation
            results = cli.comprehensive_v10_validation(args.version)
            success = results['overall_passed']
            
            if args.json:
                print(json.dumps(results, indent=2))
        
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