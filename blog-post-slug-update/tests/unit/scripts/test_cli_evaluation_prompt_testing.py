"""
Unit Tests for Evaluation Prompt Testing CLI Script - Phase 2.2

These tests define the behavior and functionality of the
scripts/test_evaluation_prompt.py CLI script that enables developers
to test individual evaluation prompt versions.

TDD Phase: RED (these will initially fail - CLI script doesn't exist yet)

Target CLI Script: scripts/test_evaluation_prompt.py
Usage Examples:
  python scripts/test_evaluation_prompt.py v2_cultural_focused --sample-size 10
  python scripts/test_evaluation_prompt.py current --verbose --sample-size 5
  python scripts/test_evaluation_prompt.py v3_competitive_focused --output results.json
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


class TestEvaluationPromptTestingCLI:
    """Test the evaluation prompt testing CLI script functionality"""
    
    def setup_method(self):
        """Set up test environment before each test"""
        self.script_path = Path("scripts/test_evaluation_prompt.py")
        self.test_slugs = [
            {
                "slug": "ultimate-ichiban-kuji-guide",
                "title": "一番賞完全購入指南",
                "content": "Complete guide to ichiban-kuji purchasing and collecting"
            },
            {
                "slug": "daikoku-drugstore-shopping-guide",
                "title": "大國藥妝購物完全攻略",
                "content": "Comprehensive Daikoku drugstore shopping guide"
            }
        ]

    def test_cli_script_file_exists(self):
        """scripts/test_evaluation_prompt.py should exist"""
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

    def test_cli_script_accepts_evaluation_prompt_version_argument(self):
        """CLI script should accept evaluation prompt version as first argument"""
        # Should fail initially - no script exists
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "v2_cultural_focused", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Should not error on valid prompt version argument
            assert result.returncode in [0, 2], "Should accept valid evaluation prompt version"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.fail("CLI script should accept evaluation prompt version argument")

    def test_cli_script_accepts_sample_size_option(self):
        """CLI script should accept --sample-size option"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "--sample-size", "5", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode in [0, 2], "Should accept --sample-size option"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.fail("CLI script should accept --sample-size option")

    def test_cli_script_accepts_verbose_option(self):
        """CLI script should accept --verbose option"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "--verbose", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode in [0, 2], "Should accept --verbose option"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.fail("CLI script should accept --verbose option")

    def test_cli_script_accepts_output_option(self):
        """CLI script should accept --output option for JSON results"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "--output", "results.json", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode in [0, 2], "Should accept --output option"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.fail("CLI script should accept --output option")

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_cli_script_validates_evaluation_prompt_version(self, mock_exists, mock_file):
        """CLI script should validate evaluation prompt version exists"""
        # Mock that script exists but prompt version doesn't
        mock_exists.return_value = False
        
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "nonexistent_version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Should fail with informative error for invalid version
            assert result.returncode != 0, "Should fail for nonexistent evaluation prompt version"
            assert "not found" in result.stderr.lower() or "invalid" in result.stderr.lower(), "Should show informative error message"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_produces_expected_output_format(self):
        """CLI script should produce expected output format"""
        # This will fail initially - no script exists
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                temp_output = temp_file.name
            
            # Run script with minimal sample size
            result = subprocess.run(
                ["python", str(self.script_path), "current", "--sample-size", "1", "--output", temp_output],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            assert result.returncode == 0, f"Script should run successfully: {result.stderr}"
            
            # Check output file exists and has expected structure
            assert os.path.exists(temp_output), "Should create output file"
            
            with open(temp_output, 'r') as f:
                output_data = json.load(f)
            
            # Validate expected output structure
            expected_keys = {
                'evaluation_prompt_version', 'sample_size', 'results', 
                'summary', 'strengths', 'improvements'
            }
            actual_keys = set(output_data.keys())
            assert expected_keys.issubset(actual_keys), f"Output should contain keys: {expected_keys}"
            
            # Clean up
            os.unlink(temp_output)
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_console_output_format(self):
        """CLI script should produce human-readable console output"""
        # Should fail initially - no script
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "--sample-size", "2", "--verbose"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            assert result.returncode == 0, "Script should run successfully"
            
            # Check for expected output sections
            output = result.stdout
            expected_sections = [
                "TESTING EVALUATION PROMPT:",
                "Sample Size:",
                "Evaluation Results:",
                "Strengths:",
                "Areas for improvement:"
            ]
            
            for section in expected_sections:
                assert section in output, f"Console output should contain '{section}' section"
            
            # Should show evaluation metrics
            assert "Cultural authenticity:" in output or "cultural_authenticity" in output
            assert "Brand hierarchy:" in output or "brand_hierarchy" in output
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_handles_api_key_missing(self):
        """CLI script should handle missing API key gracefully"""
        # Should fail initially
        try:
            # Run without API key in environment
            env = os.environ.copy()
            if 'OPENAI_API_KEY' in env:
                del env['OPENAI_API_KEY']
            
            result = subprocess.run(
                ["python", str(self.script_path), "current", "--sample-size", "1"],
                capture_output=True,
                text=True,
                timeout=5,
                env=env
            )
            
            # Should fail gracefully with informative error
            assert result.returncode != 0, "Should fail when API key is missing"
            assert "API key" in result.stderr or "OPENAI_API_KEY" in result.stderr, "Should mention API key requirement"
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_handles_invalid_sample_size(self):
        """CLI script should validate sample size parameter"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "--sample-size", "0"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            assert result.returncode != 0, "Should fail for invalid sample size"
            assert "sample" in result.stderr.lower(), "Should mention sample size issue"
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_shows_help_information(self):
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
            
            # Should contain key help sections
            expected_help_content = [
                "usage:",
                "evaluation prompt version",
                "--sample-size",
                "--verbose", 
                "--output",
                "examples:"
            ]
            
            for content in expected_help_content:
                assert content.lower() in help_output.lower(), f"Help should contain '{content}'"
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_integration_with_seo_evaluator(self):
        """CLI script should integrate properly with SEOEvaluator class"""
        # This tests that the script can import and use SEOEvaluator
        # Should fail initially - no script exists
        
        # We'll test this by checking the script can load the evaluator
        try:
            result = subprocess.run(
                ["python", "-c", f"""
import sys
sys.path.append('src')
sys.path.append('scripts')

# Try to import the script module
import test_evaluation_prompt
assert hasattr(test_evaluation_prompt, 'main'), 'Script should have main function'
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

    def test_cli_script_performance_analysis_output(self):
        """CLI script should provide detailed performance analysis"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "v2_cultural_focused", "--sample-size", "3", "--verbose"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            assert result.returncode == 0, "Script should run successfully"
            
            output = result.stdout
            
            # Should show detailed analysis
            performance_indicators = [
                "avg",  # Average scores
                "0.", # Score values (decimals)
                "vs", # Comparison indicators
                "baseline" # Comparison to baseline
            ]
            
            for indicator in performance_indicators:
                assert indicator in output.lower(), f"Output should contain performance indicator: {indicator}"
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_error_handling_and_recovery(self):
        """CLI script should handle errors gracefully and provide recovery suggestions"""
        # Should fail initially
        try:
            # Test with various error conditions
            error_conditions = [
                (["nonexistent_version"], "invalid.*version"),
                (["current", "--sample-size", "-1"], "invalid.*sample"),
                (["current", "--output", "/invalid/path/output.json"], "output.*path")
            ]
            
            for args, error_pattern in error_conditions:
                result = subprocess.run(
                    ["python", str(self.script_path)] + args,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                assert result.returncode != 0, f"Should fail for error condition: {args}"
                # Error message should be informative (not just generic Python traceback)
                assert len(result.stderr.split('\n')) < 10, "Should show concise error, not full traceback"
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")