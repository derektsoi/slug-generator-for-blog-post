#!/usr/bin/env python3
"""
PreFlightValidator - Comprehensive pre-flight validation system
Implementation follows TDD approach - minimal code to satisfy test requirements.
"""

import os
import time
import tempfile
import importlib.util
from typing import Dict, Any, Callable

# Handle both relative and absolute imports for test compatibility
try:
    from .file_operations import BaseTimestampedException
    from .configuration_pipeline import ConfigurationPipeline
except ImportError:
    # Fallback for direct module loading (used by tests)
    import importlib.util
    import os
    spec = importlib.util.spec_from_file_location(
        "file_operations", 
        os.path.join(os.path.dirname(__file__), "file_operations.py")
    )
    file_ops_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(file_ops_module)
    BaseTimestampedException = file_ops_module.BaseTimestampedException
    
    # Load configuration pipeline
    config_spec = importlib.util.spec_from_file_location(
        "configuration_pipeline", 
        os.path.join(os.path.dirname(__file__), "configuration_pipeline.py")
    )
    config_module = importlib.util.module_from_spec(config_spec)
    config_spec.loader.exec_module(config_module)
    ConfigurationPipeline = config_module.ConfigurationPipeline


class ValidationFailureError(BaseTimestampedException):
    """Custom exception for validation failures"""
    
    def __init__(self, message: str, failed_checks: list = None, total_checks: int = 0):
        super().__init__(message)
        self.failed_checks = failed_checks or []
        self.total_checks = total_checks
        self.failure_count = len(self.failed_checks)


class PreFlightValidator:
    """Comprehensive pre-flight validation system"""
    
    def __init__(self, prompt_version: str, output_dir: str):
        """
        Initialize pre-flight validator.
        
        Args:
            prompt_version: Version of prompt to validate
            output_dir: Output directory for batch processing
        """
        self.prompt_version = prompt_version
        self.output_dir = output_dir
        self._custom_validations = {}
    
    def run_full_validation(self) -> Dict[str, Any]:
        """Run complete pre-flight validation suite"""
        results = {
            'prompt_config': self.validate_prompt_config(),
            'file_permissions': self.validate_file_permissions(),
            'dependencies': self.validate_dependencies(),
            'configuration_consistency': self.validate_configuration_consistency(),
            'resume_capability': self.validate_resume_capability()
        }
        
        # Add custom validations
        for name, validation_func in self._custom_validations.items():
            results[name] = validation_func()
        
        # Aggregate results
        all_passed = all(result.get('passed', False) for result in results.values())
        
        return {
            'overall_passed': all_passed,
            'results': results,
            'recommendation': 'PROCEED' if all_passed else 'FIX_ISSUES'
        }
    
    def validate_prompt_config(self) -> Dict[str, Any]:
        """Validate prompt file exists and has correct name format"""
        expected_file = f"src/config/prompts/{self.prompt_version}_prompt.txt"
        exists = os.path.exists(expected_file)
        
        return {
            'passed': exists,
            'message': f"Prompt file {'found' if exists else 'missing'}: {expected_file}",
            'fix': f"Ensure prompt file named exactly: {self.prompt_version}_prompt.txt" if not exists else None
        }
    
    def validate_file_permissions(self) -> Dict[str, Any]:
        """Validate file permissions for output directory"""
        try:
            # Test write permissions by creating a temporary file
            test_file = os.path.join(self.output_dir, 'test_write_permission.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            
            # Clean up test file
            os.remove(test_file)
            
            return {
                'passed': True,
                'message': f"Write permissions confirmed for: {self.output_dir}"
            }
            
        except (OSError, PermissionError) as e:
            return {
                'passed': False,
                'message': f"Permission denied for directory: {self.output_dir}. Error: {str(e)}",
                'fix': f"Ensure write permissions for directory: {self.output_dir}"
            }
    
    def validate_dependencies(self) -> Dict[str, Any]:
        """Validate required dependencies are available"""
        required_modules = ['json', 'os', 'time', 'threading']
        optional_modules = ['openai', 'requests', 'beautifulsoup4']
        
        missing_required = []
        missing_optional = []
        
        # Check required modules
        for module_name in required_modules:
            try:
                __import__(module_name)
            except ImportError:
                missing_required.append(module_name)
        
        # Check optional modules
        for module_name in optional_modules:
            try:
                __import__(module_name)
            except ImportError:
                missing_optional.append(module_name)
        
        passed = len(missing_required) == 0
        
        if passed:
            message = "All required dependencies available"
            if missing_optional:
                message += f". Optional missing: {', '.join(missing_optional)}"
        else:
            message = f"Missing required dependencies: {', '.join(missing_required)}"
        
        return {
            'passed': passed,
            'message': message,
            'dependencies': {
                'missing_required': missing_required,
                'missing_optional': missing_optional
            }
        }
    
    def validate_configuration_consistency(self) -> Dict[str, Any]:
        """Validate configuration consistency across components"""
        try:
            result = ConfigurationPipeline.validate_configuration_consistency(self.prompt_version)
            
            return {
                'passed': result['passed'],
                'message': f"Configuration consistency {'validated' if result['passed'] else 'failed'} for {self.prompt_version}",
                'issues': result.get('issues', []),
                'fix_suggestions': [
                    "Ensure validation functions use version-specific configuration",
                    "Check SlugGeneratorConfig.for_version() implementation",
                    "Verify constraint consistency across components"
                ] if not result['passed'] else []
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f"Configuration validation error: {str(e)}",
                'issues': [str(e)]
            }
    
    def validate_resume_capability(self) -> Dict[str, Any]:
        """Validate resume capability with checkpoint functionality"""
        try:
            # Test checkpoint creation and loading
            test_checkpoint_data = {
                'version': self.prompt_version,
                'resume_index': 100,
                'processed_count': 99,
                'failed_count': 1,
                'timestamp': time.time(),
                'metadata': {'test': True}
            }
            
            # Try to create checkpoint file
            checkpoint_file = os.path.join(self.output_dir, 'test_checkpoint.json')
            
            import json
            with open(checkpoint_file, 'w') as f:
                json.dump(test_checkpoint_data, f)
            
            # Try to read it back
            with open(checkpoint_file, 'r') as f:
                loaded_data = json.load(f)
            
            # Clean up
            os.remove(checkpoint_file)
            
            # Validate data integrity
            passed = loaded_data['resume_index'] == test_checkpoint_data['resume_index']
            
            return {
                'passed': passed,
                'message': f"Checkpoint functionality {'verified' if passed else 'failed'}",
                'fix': "Check checkpoint file format and permissions" if not passed else None
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f"Checkpoint validation failed: {str(e)}",
                'fix': f"Ensure write permissions and valid JSON format for checkpoint files"
            }
    
    def add_custom_validation(self, name: str, validation_func: Callable[[], Dict[str, Any]]):
        """Add custom validation function"""
        self._custom_validations[name] = validation_func