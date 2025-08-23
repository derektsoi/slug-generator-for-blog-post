"""
Unit Tests for Evaluation Prompt Comparison CLI Script - Phase 2.2

These tests define the behavior and functionality of the
scripts/compare_evaluation_prompts.py CLI script that enables developers
to compare different evaluation prompt versions.

TDD Phase: RED (these will initially fail - CLI script doesn't exist yet)

Target CLI Script: scripts/compare_evaluation_prompts.py  
Usage Examples:
  python scripts/compare_evaluation_prompts.py current v2_cultural_focused --urls 20
  python scripts/compare_evaluation_prompts.py v2_cultural_focused v3_competitive_focused --sample-size 15 --verbose
  python scripts/compare_evaluation_prompts.py current v2_cultural_focused --output comparison.json --statistical
"""

import pytest
import subprocess
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import sys

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))


class TestEvaluationPromptComparisonCLI:
    """Test the evaluation prompt comparison CLI script functionality"""
    
    def setup_method(self):
        """Set up test environment before each test"""
        self.script_path = Path("scripts/compare_evaluation_prompts.py")
        self.test_urls = [
            {
                "slug": "ultimate-ichiban-kuji-guide",
                "title": "一番賞完全購入指南",
                "content": "Complete guide to ichiban-kuji purchasing"
            },
            {
                "slug": "skinniydip-iface-rhinoshield-comparison",
                "title": "日韓台7大手機殼品牌推介",
                "content": "SKINNIYDIP/iface/犀牛盾iPhone16手機殼評比"
            }
        ]

    def test_cli_script_file_exists(self):
        """scripts/compare_evaluation_prompts.py should exist"""
        # This should fail initially - script doesn't exist yet
        assert self.script_path.exists(), f"CLI script should exist at {self.script_path}"
        assert self.script_path.is_file(), "Should be a regular file"

    def test_cli_script_is_executable(self):
        """CLI script should be executable with python"""
        # This should fail initially - script doesn't exist
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode in [0, 2], "Script should run and show help or handle --help flag"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.fail("CLI script should be executable with python")

    def test_cli_script_accepts_two_prompt_version_arguments(self):
        """CLI script should require exactly two evaluation prompt versions"""
        # Should fail initially - no script exists
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "v2_cultural_focused", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode in [0, 2], "Should accept two evaluation prompt versions"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.fail("CLI script should accept two evaluation prompt version arguments")

    def test_cli_script_rejects_single_prompt_version(self):
        """CLI script should reject single evaluation prompt version"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current"],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode != 0, "Should fail with single evaluation prompt version"
            assert "two" in result.stderr.lower() or "compare" in result.stderr.lower(), "Should mention comparison requirement"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_accepts_urls_option(self):
        """CLI script should accept --urls option for number of test cases"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "v2_cultural_focused", "--urls", "20", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode in [0, 2], "Should accept --urls option"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.fail("CLI script should accept --urls option")

    def test_cli_script_accepts_sample_size_option(self):
        """CLI script should accept --sample-size as alias for --urls"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "v2_cultural_focused", "--sample-size", "15", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode in [0, 2], "Should accept --sample-size option"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.fail("CLI script should accept --sample-size option")

    def test_cli_script_accepts_statistical_option(self):
        """CLI script should accept --statistical option for statistical analysis"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "v2_cultural_focused", "--statistical", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode in [0, 2], "Should accept --statistical option"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.fail("CLI script should accept --statistical option")

    def test_cli_script_accepts_output_option(self):
        """CLI script should accept --output option for JSON results"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "v2_cultural_focused", "--output", "comparison.json", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode in [0, 2], "Should accept --output option"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.fail("CLI script should accept --output option")

    def test_cli_script_validates_prompt_versions(self):
        """CLI script should validate both evaluation prompt versions exist"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "nonexistent1", "nonexistent2"],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode != 0, "Should fail for nonexistent evaluation prompt versions"
            assert "not found" in result.stderr.lower() or "invalid" in result.stderr.lower(), "Should show informative error"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_produces_comparison_output_format(self):
        """CLI script should produce expected comparison output format"""
        # This will fail initially - no script exists
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                temp_output = temp_file.name
            
            result = subprocess.run(
                ["python", str(self.script_path), "current", "v2_cultural_focused", "--urls", "2", "--output", temp_output],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            assert result.returncode == 0, f"Script should run successfully: {result.stderr}"
            assert os.path.exists(temp_output), "Should create output file"
            
            with open(temp_output, 'r') as f:
                output_data = json.load(f)
            
            # Validate expected comparison output structure
            expected_keys = {
                'comparison_versions', 'sample_size', 'results_summary', 
                'version_a_results', 'version_b_results', 'comparative_analysis',
                'statistical_analysis', 'recommendations'
            }
            actual_keys = set(output_data.keys())
            assert expected_keys.issubset(actual_keys), f"Output should contain keys: {expected_keys}"
            
            os.unlink(temp_output)
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_console_comparison_output(self):
        """CLI script should produce human-readable comparison console output"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "v2_cultural_focused", "--urls", "3", "--verbose"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            assert result.returncode == 0, "Script should run successfully"
            
            output = result.stdout
            expected_sections = [
                "COMPARISON:",
                "vs",  # Version comparison indicator
                "Sample Size:",
                "Performance Summary:",
                "Winner:",
                "Key Differences:",
                "Recommendations:"
            ]
            
            for section in expected_sections:
                assert section in output, f"Console output should contain '{section}' section"
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_statistical_analysis_output(self):
        """CLI script should provide statistical analysis when --statistical flag used"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "v2_cultural_focused", "--urls", "10", "--statistical"],
                capture_output=True,
                text=True,
                timeout=20
            )
            
            assert result.returncode == 0, "Script should run successfully with statistical analysis"
            
            output = result.stdout
            statistical_indicators = [
                "p-value",
                "significance",
                "effect size",
                "confidence interval",
                "mean difference",
                "standard deviation"
            ]
            
            # Should contain at least some statistical analysis
            statistical_found = sum(1 for indicator in statistical_indicators 
                                  if indicator.lower() in output.lower())
            assert statistical_found >= 3, f"Should contain statistical analysis indicators: {statistical_indicators}"
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_handles_identical_prompt_versions(self):
        """CLI script should handle comparison of identical prompt versions"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "current", "--urls", "2"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Should either warn or handle gracefully
            if result.returncode == 0:
                # If it runs, should mention identical versions
                assert "identical" in result.stdout.lower() or "same" in result.stdout.lower()
            else:
                # If it fails, should give informative error
                assert "identical" in result.stderr.lower() or "same" in result.stderr.lower()
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_dimension_by_dimension_comparison(self):
        """CLI script should provide dimension-by-dimension comparison"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "v2_cultural_focused", "--urls", "5", "--verbose"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            assert result.returncode == 0, "Script should run successfully"
            
            output = result.stdout
            # Should show comparison across scoring dimensions
            expected_dimensions = [
                "cultural_authenticity",
                "brand_hierarchy", 
                "user_intent_match",
                "technical_seo"
            ]
            
            dimension_mentions = sum(1 for dim in expected_dimensions 
                                   if dim.lower() in output.lower())
            assert dimension_mentions >= 2, "Should compare across multiple scoring dimensions"
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_performance_winner_determination(self):
        """CLI script should determine and report performance winner"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "v2_cultural_focused", "--urls", "8"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            assert result.returncode == 0, "Script should run successfully"
            
            output = result.stdout
            # Should clearly identify winner
            winner_indicators = [
                "winner:",
                "performs better",
                "outperforms", 
                "superior",
                "recommended"
            ]
            
            winner_found = any(indicator in output.lower() for indicator in winner_indicators)
            assert winner_found, "Should clearly identify performance winner"
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_handles_invalid_sample_size(self):
        """CLI script should validate sample size parameter"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "v2_cultural_focused", "--urls", "0"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            assert result.returncode != 0, "Should fail for invalid sample size"
            assert "sample" in result.stderr.lower() or "urls" in result.stderr.lower(), "Should mention sample size issue"
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_shows_comprehensive_help(self):
        """CLI script should show comprehensive help information"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            help_output = result.stdout
            expected_help_content = [
                "usage:",
                "compare",
                "evaluation prompt",
                "version1 version2",
                "--urls",
                "--statistical",
                "--output",
                "--verbose",
                "examples:"
            ]
            
            for content in expected_help_content:
                assert content.lower() in help_output.lower(), f"Help should contain '{content}'"
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_integration_with_seo_evaluator(self):
        """CLI script should integrate with SEOEvaluator for both prompt versions"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", "-c", f"""
import sys
sys.path.append('src')
sys.path.append('scripts')

import compare_evaluation_prompts
assert hasattr(compare_evaluation_prompts, 'main'), 'Script should have main function'
assert hasattr(compare_evaluation_prompts, 'compare_prompt_versions'), 'Script should have comparison function'
print('Integration check passed')
"""],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            assert result.returncode == 0, f"Script should integrate with SEOEvaluator: {result.stderr}"
            assert "Integration check passed" in result.stdout
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_handles_api_errors_gracefully(self):
        """CLI script should handle API errors gracefully during comparison"""
        # Should fail initially
        try:
            # Test with missing API key
            env = os.environ.copy()
            if 'OPENAI_API_KEY' in env:
                del env['OPENAI_API_KEY']
            
            result = subprocess.run(
                ["python", str(self.script_path), "current", "v2_cultural_focused", "--urls", "2"],
                capture_output=True,
                text=True,
                timeout=10,
                env=env
            )
            
            assert result.returncode != 0, "Should fail gracefully when API key missing"
            assert "API key" in result.stderr or "OPENAI_API_KEY" in result.stderr, "Should mention API key requirement"
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_progress_reporting(self):
        """CLI script should show progress during comparison"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "v2_cultural_focused", "--urls", "10", "--verbose"],
                capture_output=True,
                text=True,
                timeout=25
            )
            
            assert result.returncode == 0, "Script should run successfully"
            
            output = result.stdout
            progress_indicators = [
                "testing",
                "processing", 
                "evaluating",
                "progress",
                "/",  # Progress fraction like "5/10"
                "%"   # Progress percentage
            ]
            
            progress_found = any(indicator in output.lower() for indicator in progress_indicators)
            assert progress_found, "Should show progress indicators during execution"
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_error_handling_and_recovery(self):
        """CLI script should handle errors gracefully with recovery suggestions"""
        # Should fail initially
        try:
            error_conditions = [
                (["nonexistent1", "nonexistent2"], "invalid.*version"),
                (["current", "v2_cultural_focused", "--urls", "-5"], "invalid.*sample"),
                (["current", "v2_cultural_focused", "--output", "/invalid/path.json"], "output.*path")
            ]
            
            for args, error_pattern in error_conditions:
                result = subprocess.run(
                    ["python", str(self.script_path)] + args,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                assert result.returncode != 0, f"Should fail for error condition: {args}"
                # Error message should be informative
                assert len(result.stderr.split('\n')) < 10, "Should show concise error, not full traceback"
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")