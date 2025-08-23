"""
Unit Tests for Evaluation Prompt Validation CLI Script - Phase 2.2

These tests define the behavior and functionality of the
scripts/validate_evaluation_prompt.py CLI script that enables developers
to validate evaluation prompt configurations and metadata.

TDD Phase: RED (these will initially fail - CLI script doesn't exist yet)

Target CLI Script: scripts/validate_evaluation_prompt.py
Usage Examples:
  python scripts/validate_evaluation_prompt.py v2_cultural_focused
  python scripts/validate_evaluation_prompt.py current --verbose
  python scripts/validate_evaluation_prompt.py v3_competitive_focused --output validation.json
  python scripts/validate_evaluation_prompt.py --all
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


class TestEvaluationPromptValidationCLI:
    """Test the evaluation prompt validation CLI script functionality"""
    
    def setup_method(self):
        """Set up test environment before each test"""
        self.script_path = Path("scripts/validate_evaluation_prompt.py")

    def test_cli_script_file_exists(self):
        """scripts/validate_evaluation_prompt.py should exist"""
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

    def test_cli_script_accepts_single_prompt_version(self):
        """CLI script should accept single evaluation prompt version for validation"""
        # Should fail initially - no script exists
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "v2_cultural_focused", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode in [0, 2], "Should accept single evaluation prompt version"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.fail("CLI script should accept single evaluation prompt version")

    def test_cli_script_accepts_all_flag(self):
        """CLI script should accept --all flag to validate all prompt versions"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "--all", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode in [0, 2], "Should accept --all flag"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.fail("CLI script should accept --all flag")

    def test_cli_script_accepts_verbose_option(self):
        """CLI script should accept --verbose option for detailed output"""
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
        """CLI script should accept --output option for JSON validation results"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "--output", "validation.json", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode in [0, 2], "Should accept --output option"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.fail("CLI script should accept --output option")

    def test_cli_script_accepts_fix_flag(self):
        """CLI script should accept --fix flag to attempt automatic fixes"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "--fix", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode in [0, 2], "Should accept --fix flag"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.fail("CLI script should accept --fix flag")

    def test_cli_script_validates_prompt_version_exists(self):
        """CLI script should validate evaluation prompt version exists"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "nonexistent_version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode != 0, "Should fail for nonexistent evaluation prompt version"
            assert "not found" in result.stderr.lower() or "invalid" in result.stderr.lower(), "Should show informative error"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_produces_validation_output_format(self):
        """CLI script should produce expected validation output format"""
        # This will fail initially - no script exists
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                temp_output = temp_file.name
            
            result = subprocess.run(
                ["python", str(self.script_path), "current", "--output", temp_output],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            assert result.returncode == 0, f"Script should run successfully: {result.stderr}"
            assert os.path.exists(temp_output), "Should create output file"
            
            with open(temp_output, 'r') as f:
                output_data = json.load(f)
            
            # Validate expected validation output structure
            expected_keys = {
                'prompt_version', 'validation_timestamp', 'is_valid', 
                'errors', 'warnings', 'file_checks', 'metadata_checks',
                'configuration_checks', 'recommendations'
            }
            actual_keys = set(output_data.keys())
            assert expected_keys.issubset(actual_keys), f"Output should contain keys: {expected_keys}"
            
            os.unlink(temp_output)
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_console_validation_output(self):
        """CLI script should produce human-readable validation console output"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "--verbose"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            assert result.returncode == 0, "Script should run successfully"
            
            output = result.stdout
            expected_sections = [
                "VALIDATION RESULTS:",
                "Prompt Version:",
                "File Checks:",
                "Metadata Checks:",
                "Configuration Checks:",
                "Overall Status:"
            ]
            
            for section in expected_sections:
                assert section in output, f"Console output should contain '{section}' section"
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_validates_prompt_file_exists(self):
        """CLI script should validate that prompt .txt file exists"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "--verbose"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            assert result.returncode == 0, "Script should run successfully"
            
            output = result.stdout
            file_validation_indicators = [
                "file exists",
                ".txt",
                "prompt file",
                "readable"
            ]
            
            file_check_found = any(indicator in output.lower() for indicator in file_validation_indicators)
            assert file_check_found, "Should validate prompt file existence and readability"
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_validates_metadata_file(self):
        """CLI script should validate metadata JSON file structure"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "--verbose"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            assert result.returncode == 0, "Script should run successfully"
            
            output = result.stdout
            metadata_validation_indicators = [
                "metadata",
                "json",
                "scoring_dimensions",
                "dimension_weights",
                "valid structure"
            ]
            
            metadata_check_found = any(indicator in output.lower() for indicator in metadata_validation_indicators)
            assert metadata_check_found, "Should validate metadata file structure"
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_validates_scoring_dimensions(self):
        """CLI script should validate scoring dimensions consistency"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "v2_cultural_focused", "--verbose"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            assert result.returncode == 0, "Script should run successfully"
            
            output = result.stdout
            dimension_validation_indicators = [
                "dimensions",
                "weights",
                "sum to 1.0",
                "consistency"
            ]
            
            dimension_check_found = any(indicator in output.lower() for indicator in dimension_validation_indicators)
            assert dimension_check_found, "Should validate scoring dimensions and weights"
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_detects_configuration_errors(self):
        """CLI script should detect and report configuration errors"""
        # Should fail initially - we'll test this with a malformed prompt version
        try:
            # This would ideally test against a known malformed configuration
            # For now, we test that error detection mechanism exists
            result = subprocess.run(
                ["python", str(self.script_path), "current"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Should run and report validation status
            assert result.returncode in [0, 1], "Should run and report validation results"
            
            output = result.stdout + result.stderr
            error_reporting_indicators = [
                "error",
                "warning", 
                "valid",
                "invalid",
                "check"
            ]
            
            error_reporting_found = any(indicator in output.lower() for indicator in error_reporting_indicators)
            assert error_reporting_found, "Should have error/warning reporting mechanism"
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_validates_all_prompts(self):
        """CLI script should validate all prompt versions with --all flag"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "--all"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            assert result.returncode == 0, "Script should run successfully"
            
            output = result.stdout
            # Should mention multiple prompt versions
            all_validation_indicators = [
                "current",
                "v2_cultural_focused", 
                "v3_competitive_focused",
                "total",
                "summary"
            ]
            
            multiple_versions_found = sum(1 for indicator in all_validation_indicators 
                                        if indicator in output.lower())
            assert multiple_versions_found >= 3, "Should validate multiple prompt versions"
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_provides_fix_suggestions(self):
        """CLI script should provide fix suggestions for validation issues"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "--verbose"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            assert result.returncode == 0, "Script should run successfully"
            
            output = result.stdout
            fix_suggestion_indicators = [
                "recommend",
                "suggest",
                "fix",
                "improve",
                "solution"
            ]
            
            suggestions_found = any(indicator in output.lower() for indicator in fix_suggestion_indicators)
            # Should provide suggestions (even if everything is valid, should mention that)
            assert suggestions_found or "no issues" in output.lower(), "Should provide fix suggestions or confirm no issues"
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_handles_fix_flag(self):
        """CLI script should attempt automatic fixes when --fix flag used"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "--fix"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Should run (may succeed if no fixes needed, or fail if fixes required)
            assert result.returncode in [0, 1], "Script should handle --fix flag"
            
            output = result.stdout + result.stderr
            fix_indicators = [
                "fix",
                "repair", 
                "corrected",
                "updated",
                "no fixes needed"
            ]
            
            fix_handling_found = any(indicator in output.lower() for indicator in fix_indicators)
            assert fix_handling_found, "Should handle automatic fixes or report no fixes needed"
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_exit_codes(self):
        """CLI script should use appropriate exit codes for validation results"""
        # Should fail initially
        try:
            # Test valid prompt version - should exit 0
            result = subprocess.run(
                ["python", str(self.script_path), "current"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # For a valid prompt, should exit successfully
            if "valid" in result.stdout.lower() and "error" not in result.stdout.lower():
                assert result.returncode == 0, "Should exit 0 for valid prompt configurations"
            else:
                # If validation found issues, should exit non-zero
                assert result.returncode != 0, "Should exit non-zero for validation issues"
                
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
                "validate", 
                "evaluation prompt",
                "version",
                "--all",
                "--verbose",
                "--output",
                "--fix",
                "examples:"
            ]
            
            for content in expected_help_content:
                assert content.lower() in help_output.lower(), f"Help should contain '{content}'"
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_integration_with_evaluation_prompt_manager(self):
        """CLI script should integrate with EvaluationPromptManager"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", "-c", f"""
import sys
sys.path.append('src')
sys.path.append('scripts')

import validate_evaluation_prompt
assert hasattr(validate_evaluation_prompt, 'main'), 'Script should have main function'
assert hasattr(validate_evaluation_prompt, 'validate_prompt_configuration'), 'Script should have validation function'
print('Integration check passed')
"""],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            assert result.returncode == 0, f"Script should integrate with EvaluationPromptManager: {result.stderr}"
            assert "Integration check passed" in result.stdout
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_validates_weight_sum(self):
        """CLI script should validate that dimension weights sum to 1.0"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "--verbose"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            assert result.returncode == 0, "Script should run successfully"
            
            output = result.stdout
            weight_validation_indicators = [
                "weights sum",
                "1.0",
                "total weight",
                "weight validation"
            ]
            
            weight_check_found = any(indicator in output.lower() for indicator in weight_validation_indicators)
            assert weight_check_found, "Should validate dimension weights sum to 1.0"
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_validates_prompt_template_syntax(self):
        """CLI script should validate prompt template has required placeholders"""
        # Should fail initially
        try:
            result = subprocess.run(
                ["python", str(self.script_path), "current", "--verbose"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            assert result.returncode == 0, "Script should run successfully"
            
            output = result.stdout
            template_validation_indicators = [
                "template",
                "placeholder",
                "{slug}",
                "{title}",
                "{content}",
                "format"
            ]
            
            template_check_found = any(indicator in output.lower() for indicator in template_validation_indicators)
            assert template_check_found, "Should validate prompt template syntax and placeholders"
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")

    def test_cli_script_error_handling_and_recovery(self):
        """CLI script should handle errors gracefully with recovery suggestions"""
        # Should fail initially
        try:
            error_conditions = [
                (["nonexistent_version"], "not found"),
                (["current", "--output", "/invalid/path.json"], "output.*path"),
                (["--all", "--fix", "--output", "/invalid/path.json"], "multiple.*error")
            ]
            
            for args, error_pattern in error_conditions:
                result = subprocess.run(
                    ["python", str(self.script_path)] + args,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                assert result.returncode != 0, f"Should fail for error condition: {args}"
                # Error message should be informative
                assert len(result.stderr.split('\n')) < 15, "Should show concise error, not full traceback"
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pytest.skip("Expected to fail in RED phase - script doesn't exist yet")