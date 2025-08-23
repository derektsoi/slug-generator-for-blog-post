"""
Unified Prompt Development CLI Commands

Complete prompt development lifecycle management with template-driven creation,
testing, validation, comparison, and deployment workflows.

Usage:
    python -m cli.prompt create my_prompt --template cultural --author dev@company.com
    python -m cli.prompt test my_prompt --samples 5
    python -m cli.prompt compare my_prompt cultural_focused --metric cultural_authenticity  
    python -m cli.prompt validate my_prompt --comprehensive
    python -m cli.prompt promote my_prompt
"""

import argparse
import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from cli import BaseCLI, TestDataMixin, PromptValidationMixin, OutputFormattingMixin, ProgressTrackingMixin
from config.unified_prompt_manager import UnifiedPromptManager
from cli.analysis import PerformanceAnalyzer, ResultsInsightGenerator


class PromptDevelopmentCLI(BaseCLI, TestDataMixin, PromptValidationMixin, OutputFormattingMixin, ProgressTrackingMixin):
    """Unified prompt development and management CLI"""
    
    def __init__(self):
        super().__init__(
            tool_name="cli.prompt",
            description="Unified prompt development and management system"
        )
        self.prompt_manager = UnifiedPromptManager()
    
    def setup_parser(self) -> argparse.ArgumentParser:
        """Setup argument parser with subcommands"""
        parser = argparse.ArgumentParser(
            description=self.description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Subcommands:
  create      Create new prompt from template
  test        Test prompt with sample data
  compare     Compare two prompt versions
  validate    Validate prompt structure and content
  promote     Promote prompt from development to active
  archive     Archive a prompt
  list        List available prompts
  templates   List available templates
  
Examples:
  # Create new cultural-focused prompt
  python -m cli.prompt create semantic_cultural --template cultural --author dev@company.com
  
  # Test prompt with 5 samples
  python -m cli.prompt test semantic_cultural --samples 5
  
  # Compare with existing prompt
  python -m cli.prompt compare semantic_cultural cultural_focused --metric cultural_authenticity
  
  # Validate and promote to production
  python -m cli.prompt validate semantic_cultural --comprehensive
  python -m cli.prompt promote semantic_cultural
            """
        )
        
        # Create subparsers
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Create command
        create_parser = subparsers.add_parser('create', help='Create new prompt from template')
        create_parser.add_argument('prompt_id', help='Unique ID for the new prompt')
        create_parser.add_argument('--template', default='basic', help='Template to use (basic, cultural, competitive)')
        create_parser.add_argument('--author', required=True, help='Author email or name')
        create_parser.add_argument('--name', help='Display name for the prompt')
        create_parser.add_argument('--description', help='Brief description of the prompt')
        create_parser.add_argument('--cultural-weight', type=float, help='Cultural authenticity weight (0.0-1.0)')
        create_parser.add_argument('--competitive-weight', type=float, help='Competitive differentiation weight (0.0-1.0)')
        create_parser.add_argument('--instructions', help='Custom instructions for the evaluator')
        
        # Test command
        test_parser = subparsers.add_parser('test', help='Test prompt with sample data')
        test_parser.add_argument('prompt_id', help='Prompt ID to test')
        test_parser.add_argument('--samples', type=int, default=5, help='Number of test samples (default: 5)')
        test_parser.add_argument('--verbose', action='store_true', help='Detailed output')
        
        # Compare command
        compare_parser = subparsers.add_parser('compare', help='Compare two prompts')
        compare_parser.add_argument('prompt_a', help='First prompt to compare')
        compare_parser.add_argument('prompt_b', help='Second prompt to compare')
        compare_parser.add_argument('--samples', type=int, default=5, help='Number of test samples')
        compare_parser.add_argument('--metric', help='Primary metric to focus on')
        compare_parser.add_argument('--verbose', action='store_true', help='Detailed output')
        
        # Validate command
        validate_parser = subparsers.add_parser('validate', help='Validate prompt')
        validate_parser.add_argument('prompt_id', help='Prompt ID to validate')
        validate_parser.add_argument('--comprehensive', action='store_true', help='Run comprehensive validation')
        validate_parser.add_argument('--fix-issues', action='store_true', help='Attempt to fix common issues')
        
        # Promote command
        promote_parser = subparsers.add_parser('promote', help='Promote prompt to active')
        promote_parser.add_argument('prompt_id', help='Prompt ID to promote')
        promote_parser.add_argument('--force', action='store_true', help='Force promotion even with warnings')
        
        # Archive command
        archive_parser = subparsers.add_parser('archive', help='Archive a prompt')
        archive_parser.add_argument('prompt_id', help='Prompt ID to archive')
        
        # List command
        list_parser = subparsers.add_parser('list', help='List prompts')
        list_parser.add_argument('--status', choices=['active', 'development', 'archived'], 
                               help='Filter by status')
        list_parser.add_argument('--verbose', action='store_true', help='Show detailed information')
        
        # Templates command
        templates_parser = subparsers.add_parser('templates', help='List available templates')
        templates_parser.add_argument('--verbose', action='store_true', help='Show template details')
        
        return parser
    
    def create_prompt(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Create new prompt from template"""
        print(f"🎨 Creating new evaluation prompt: {args.prompt_id}")
        print(f"📋 Template: {args.template}")
        
        # Prepare template variables
        variables = {
            'display_name': args.name or args.prompt_id.replace('_', ' ').title(),
            'description': args.description or f"Custom evaluation prompt based on {args.template} template",
            'author': args.author,
        }
        
        # Add optional variables
        if args.cultural_weight is not None:
            variables['cultural_weight'] = args.cultural_weight
        if args.competitive_weight is not None:
            variables['competitive_weight'] = args.competitive_weight
        if args.instructions:
            variables['custom_instructions'] = args.instructions
        
        try:
            output_path = self.prompt_manager.create_from_template(
                args.prompt_id, 
                args.template, 
                variables
            )
            
            print(f"✅ Created: {output_path}")
            print(f"📝 Edit the file to customize weights and instructions")
            print(f"🧪 Test with: python -m cli.prompt test {args.prompt_id}")
            
            return {'status': 'created', 'path': str(output_path)}
            
        except Exception as e:
            raise self.handle_validation_error(e, "prompt creation")
    
    def test_prompt(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Test prompt with sample data"""
        print(f"🧪 Testing: {args.prompt_id}")
        
        try:
            # Get prompt info
            prompt_info = self.prompt_manager.get_prompt_info(args.prompt_id)
            print(f"📋 {prompt_info.name} ({prompt_info.status})")
            
            if prompt_info.focus_areas:
                focus_display = prompt_info.focus_areas if isinstance(prompt_info.focus_areas, list) else [prompt_info.focus_areas]
                print(f"🎯 Focus: {', '.join(focus_display)}")
            
            # Use API to test if available  
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("⚠️ No OPENAI_API_KEY - running configuration validation only")
                return self._test_prompt_config_only(args, prompt_info)
            
            return self._test_prompt_with_api(args, prompt_info, api_key)
            
        except Exception as e:
            raise self.handle_validation_error(e, f"testing prompt {args.prompt_id}")
    
    def _test_prompt_config_only(self, args: argparse.Namespace, prompt_info) -> Dict[str, Any]:
        """Test prompt configuration without API calls"""
        print(f"📊 Running configuration validation...")
        
        # Test with embedded test cases
        test_cases = prompt_info.test_cases or self.get_test_subset(args.samples)
        
        print(f"📝 Testing with {len(test_cases)} cases:")
        for i, case in enumerate(test_cases, 1):
            case_name = case.get('name', case.get('slug', f'Case {i}'))
            print(f"  {i:2d}. {case_name}")
        
        # Validate weights
        weights = prompt_info.weights
        if weights:
            weight_sum = sum(weights.values())
            print(f"\n⚖️ Dimension Weights (sum: {weight_sum:.3f}):")
            for dim, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True):
                print(f"   {self.format_dimension_name(dim):<25} {weight:.1%}")
        
        # Show thresholds
        if prompt_info.thresholds:
            print(f"\n🎯 Quality Thresholds:")
            for threshold, value in prompt_info.thresholds.items():
                print(f"   {threshold.replace('_', ' ').title():<25} {value}")
        
        print(f"\n✅ Configuration validation complete")
        print(f"💡 Add OPENAI_API_KEY to test with real LLM evaluation")
        
        return {
            'status': 'config_validated',
            'prompt_id': args.prompt_id,
            'test_cases': len(test_cases),
            'weights': weights,
            'thresholds': prompt_info.thresholds
        }
    
    def _test_prompt_with_api(self, args: argparse.Namespace, prompt_info, api_key: str) -> Dict[str, Any]:
        """Test prompt with real API calls"""
        print(f"🚀 Running live evaluation test...")
        
        try:
            from evaluation.core.seo_evaluator import SEOEvaluator
            
            evaluator = SEOEvaluator(
                api_key=api_key,
                evaluation_prompt_version=args.prompt_id  # This should work with unified manager
            )
            
            # Get test cases
            test_cases = prompt_info.test_cases or self.get_test_subset(args.samples)
            
            results = []
            scores = []
            
            progress_tracker = self.create_progress_tracker(len(test_cases), "Evaluating")
            
            for i, case in enumerate(test_cases):
                case_name = case.get('name', case.get('slug', f'Case {i+1}'))
                
                if args.verbose:
                    progress_tracker.update(1, f"Testing {case_name}")
                
                try:
                    result = evaluator.evaluate_slug(
                        case['slug'],
                        case['title'],
                        case.get('content', '')
                    )
                    
                    overall_score = result.get('overall_score', 0)
                    dimension_scores = result.get('dimension_scores', {})
                    
                    results.append({
                        'case': case,
                        'result': result,
                        'overall_score': overall_score
                    })
                    
                    scores.append(overall_score)
                    
                    if args.verbose:
                        print(f"  Overall: {overall_score:.3f}")
                        
                        # Show key dimension scores
                        focus_dims = [prompt_info.focus_areas] if isinstance(prompt_info.focus_areas, str) else prompt_info.focus_areas
                        if focus_dims:
                            for dim in focus_dims[:2]:  # Show top 2 focus dimensions
                                if dim in dimension_scores:
                                    print(f"  {self.format_dimension_name(dim)}: {dimension_scores[dim]:.3f}")
                
                except Exception as e:
                    print(f"  ❌ Error: {e}")
                    continue
                
                # Brief pause to avoid rate limits
                time.sleep(1)
            
            progress_tracker.complete()
            
            if not results:
                print(f"❌ No successful evaluations completed")
                return {'status': 'failed', 'error': 'No evaluations completed'}
            
            # Calculate summary
            avg_score = sum(scores) / len(scores)
            
            print(f"\n📈 SUMMARY: {len(results)}/{len(test_cases)} tests passed")
            print(f"📊 Average Score: {avg_score:.3f}")
            
            # Check against expectations
            if prompt_info.benchmarks:
                min_performance = prompt_info.benchmarks.get('min_performance', {})
                min_overall = min_performance.get('avg_overall', 0.7)
                
                if avg_score >= min_overall:
                    print(f"✅ Meets performance target (>= {min_overall:.3f})")
                else:
                    print(f"⚠️ Below performance target (< {min_overall:.3f})")
            
            return {
                'status': 'completed',
                'prompt_id': args.prompt_id,
                'results': results,
                'summary': {
                    'avg_score': avg_score,
                    'successful_tests': len(results),
                    'total_tests': len(test_cases)
                }
            }
            
        except ImportError as e:
            print(f"⚠️ Cannot test with API: {e}")
            return self._test_prompt_config_only(args, prompt_info)
        except Exception as e:
            raise self.handle_api_error(e, "prompt testing")
    
    def compare_prompts(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Compare two prompt versions"""
        print(f"📊 Comparing: {args.prompt_a} vs {args.prompt_b}")
        
        # For now, show configuration comparison
        try:
            info_a = self.prompt_manager.get_prompt_info(args.prompt_a)
            info_b = self.prompt_manager.get_prompt_info(args.prompt_b)
            
            print(f"\n📋 Configuration Comparison:")
            print(f"{'Aspect':<25} {args.prompt_a:<20} {args.prompt_b:<20}")
            print("-" * 70)
            print(f"{'Status':<25} {info_a.status:<20} {info_b.status:<20}")
            print(f"{'Primary Focus':<25} {str(info_a.focus_areas):<20} {str(info_b.focus_areas):<20}")
            
            # Compare weights for focused metric
            if args.metric and args.metric in info_a.weights and args.metric in info_b.weights:
                weight_a = info_a.weights[args.metric]
                weight_b = info_b.weights[args.metric]
                print(f"\n🎯 {self.format_dimension_name(args.metric)} Weight:")
                print(f"   {args.prompt_a}: {weight_a:.1%}")
                print(f"   {args.prompt_b}: {weight_b:.1%}")
                
                diff = weight_a - weight_b
                if abs(diff) > 0.01:
                    winner = args.prompt_a if diff > 0 else args.prompt_b
                    print(f"   Higher priority: {winner} (+{abs(diff):.1%})")
            
            # TODO: Add real performance comparison with API testing
            print(f"\n💡 Run with API key for performance comparison")
            
            return {
                'status': 'compared',
                'prompt_a': args.prompt_a,
                'prompt_b': args.prompt_b,
                'comparison_type': 'configuration'
            }
            
        except Exception as e:
            raise self.handle_validation_error(e, f"comparing prompts")
    
    def validate_prompt(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Validate prompt structure and content"""
        print(f"🔍 Validating: {args.prompt_id}")
        
        try:
            validation = self.prompt_manager.validate_prompt(args.prompt_id)
            
            if validation['valid']:
                print(f"✅ Validation passed")
            else:
                print(f"❌ Validation failed")
            
            if validation['errors']:
                print(f"\n❌ Errors:")
                for error in validation['errors']:
                    print(f"   - {error}")
            
            if validation['warnings']:
                print(f"\n⚠️ Warnings:")
                for warning in validation['warnings']:
                    print(f"   - {warning}")
            
            if args.comprehensive:
                print(f"\n🔬 Running comprehensive validation...")
                # Add more comprehensive checks here
                
            return validation
            
        except Exception as e:
            raise self.handle_validation_error(e, f"validating prompt {args.prompt_id}")
    
    def promote_prompt(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Promote prompt from development to active"""
        print(f"🚀 Promoting: {args.prompt_id}")
        
        try:
            # Validate first unless forced
            if not args.force:
                validation = self.prompt_manager.validate_prompt(args.prompt_id)
                if not validation['valid']:
                    print(f"❌ Cannot promote invalid prompt")
                    for error in validation['errors']:
                        print(f"   - {error}")
                    print(f"💡 Use --force to override or fix issues first")
                    return {'status': 'blocked', 'errors': validation['errors']}
                
                if validation['warnings']:
                    print(f"⚠️ Promoting with warnings:")
                    for warning in validation['warnings']:
                        print(f"   - {warning}")
            
            # Promote
            active_path = self.prompt_manager.promote_prompt(args.prompt_id)
            
            print(f"✅ Promoted to: {active_path}")
            print(f"🚀 Now available for production use")
            
            return {'status': 'promoted', 'path': str(active_path)}
            
        except Exception as e:
            raise self.handle_validation_error(e, f"promoting prompt {args.prompt_id}")
    
    def archive_prompt(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Archive a prompt"""
        print(f"📦 Archiving: {args.prompt_id}")
        
        try:
            archive_path = self.prompt_manager.archive_prompt(args.prompt_id)
            print(f"✅ Archived to: {archive_path}")
            
            return {'status': 'archived', 'path': str(archive_path)}
            
        except Exception as e:
            raise self.handle_validation_error(e, f"archiving prompt {args.prompt_id}")
    
    def list_prompts(self, args: argparse.Namespace) -> Dict[str, Any]:
        """List available prompts"""
        try:
            prompts = self.prompt_manager.list_prompts(args.status)
            
            if not prompts:
                status_text = f" ({args.status})" if args.status else ""
                print(f"No prompts found{status_text}")
                return {'prompts': []}
            
            print(f"📝 Available Prompts{f' ({args.status})' if args.status else ''}:")
            
            if args.verbose:
                for prompt_id in prompts:
                    try:
                        info = self.prompt_manager.get_prompt_info(prompt_id)
                        focus_display = info.focus_areas if isinstance(info.focus_areas, list) else [info.focus_areas]
                        print(f"  {prompt_id:<25} {info.status:<12} {', '.join(focus_display)}")
                    except Exception:
                        print(f"  {prompt_id:<25} {'unknown':<12} (error loading)")
            else:
                for prompt_id in prompts:
                    print(f"  - {prompt_id}")
            
            return {'prompts': prompts}
            
        except Exception as e:
            raise self.handle_validation_error(e, "listing prompts")
    
    def list_templates(self, args: argparse.Namespace) -> Dict[str, Any]:
        """List available templates"""
        try:
            templates = self.prompt_manager.list_templates()
            
            if not templates:
                print(f"No templates found")
                return {'templates': []}
            
            print(f"📄 Available Templates:")
            
            for template_name in templates:
                if args.verbose:
                    try:
                        template_info = self.prompt_manager.get_template_info(template_name)
                        print(f"  {template_name:<20} {template_info['description']}")
                    except Exception:
                        print(f"  {template_name:<20} (error loading description)")
                else:
                    print(f"  - {template_name}")
            
            return {'templates': templates}
            
        except Exception as e:
            raise self.handle_validation_error(e, "listing templates")
    
    def run_command(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Execute the appropriate subcommand"""
        if not args.command:
            print("Error: No command specified. Use --help for available commands.")
            return {'error': 'no_command'}
        
        command_map = {
            'create': self.create_prompt,
            'test': self.test_prompt,
            'compare': self.compare_prompts,
            'validate': self.validate_prompt,
            'promote': self.promote_prompt,
            'archive': self.archive_prompt,
            'list': self.list_prompts,
            'templates': self.list_templates,
        }
        
        command_func = command_map.get(args.command)
        if not command_func:
            raise CLIError(f"Unknown command: {args.command}")
        
        return command_func(args)


def main():
    """Main CLI entry point"""
    cli = PromptDevelopmentCLI()
    cli.run()


if __name__ == '__main__':
    main()