#!/usr/bin/env python3
"""
Smart Recovery System - Intelligent recovery strategies for batch processing failures
Implementation follows TDD approach - minimal code to satisfy test requirements.
"""

import os
import json
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass

# Use shared import utilities
try:
    from .import_utils import import_from_core
    BaseTimestampedException = import_from_core('file_operations', 'BaseTimestampedException')
    AtomicFileOperations = import_from_core('file_operations', 'AtomicFileOperations')
    # Import shared error patterns
    from .error_patterns import (
        ErrorContext, DiagnosticInfoGenerator, RecoveryStrategyPatterns,
        CommonRecoveryInstructions
    )
except ImportError:
    # Fallback for direct module loading
    import importlib.util
    import os
    spec = importlib.util.spec_from_file_location(
        "file_operations", 
        os.path.join(os.path.dirname(__file__), "file_operations.py")
    )
    file_ops_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(file_ops_module)
    BaseTimestampedException = file_ops_module.BaseTimestampedException
    AtomicFileOperations = file_ops_module.AtomicFileOperations
    
    # Import error patterns with fallback
    spec = importlib.util.spec_from_file_location(
        "error_patterns", 
        os.path.join(os.path.dirname(__file__), "error_patterns.py")
    )
    error_patterns_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(error_patterns_module)
    ErrorContext = error_patterns_module.ErrorContext
    DiagnosticInfoGenerator = error_patterns_module.DiagnosticInfoGenerator
    RecoveryStrategyPatterns = error_patterns_module.RecoveryStrategyPatterns
    CommonRecoveryInstructions = error_patterns_module.CommonRecoveryInstructions


class RecoveryError(BaseTimestampedException):
    """Custom exception for recovery operation failures"""
    
    def __init__(self, message: str, strategy_name: str = None, original_error: str = None, recovery_attempts: int = 0):
        super().__init__(message)
        self.strategy_name = strategy_name
        self.original_error = original_error
        self.recovery_attempts = recovery_attempts


@dataclass
class RecoveryResult:
    """Result of a recovery operation"""
    success: bool
    strategy_used: str = None
    recovered_count: int = 0
    new_checkpoint: Dict[str, Any] = None
    error_message: str = None
    attempted_strategies: List[str] = None
    failure_reasons: Dict[str, str] = None
    
    def __post_init__(self):
        if self.attempted_strategies is None:
            self.attempted_strategies = []
        if self.failure_reasons is None:
            self.failure_reasons = {}


@dataclass
class RecoveryStrategy:
    """Recovery strategy definition"""
    name: str
    priority: str
    description: str = ""
    applicable_errors: List[str] = None
    recovery_function: Callable = None
    
    def __post_init__(self):
        if self.applicable_errors is None:
            self.applicable_errors = []
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the recovery strategy"""
        if self.recovery_function:
            return self.recovery_function(context)
        else:
            return {"success": False, "error": "No recovery function defined"}


class BatchProcessingRecovery:
    """Intelligent recovery system for batch processing failures"""
    
    def __init__(self, output_dir: str):
        """
        Initialize recovery system.
        
        Args:
            output_dir: Directory containing batch processing files
        """
        self.output_dir = output_dir
        self.results_file = os.path.join(output_dir, 'results.jsonl')
        self.checkpoint_file = os.path.join(output_dir, 'checkpoint.json')
        self.backup_results_file = os.path.join(output_dir, 'results.jsonl.backup')
        
        # Initialize recovery strategies
        self.strategies = self._initialize_strategies()
    
    def _initialize_strategies(self) -> List[RecoveryStrategy]:
        """Initialize available recovery strategies"""
        return [
            RecoveryStrategy(
                name="rebuild_from_results",
                priority="HIGH",
                description="Rebuild checkpoint by analyzing results file",
                applicable_errors=["RESUME_LOGIC", "CHECKPOINT_CORRUPTION"],
                recovery_function=self._rebuild_from_results
            ),
            RecoveryStrategy(
                name="backup_recovery", 
                priority="MEDIUM",
                description="Recover from backup files",
                applicable_errors=["RESUME_LOGIC", "DATA_CORRUPTION"],
                recovery_function=self._backup_recovery
            ),
            RecoveryStrategy(
                name="safe_completion",
                priority="LOW", 
                description="Safe completion mode",
                applicable_errors=["CRITICAL_FAILURE", "RESUME_LOGIC"],
                recovery_function=self._safe_completion
            ),
            RecoveryStrategy(
                name="manual_mode",
                priority="LOWEST",
                description="Manual recovery guidance",
                applicable_errors=["COMPLEX_CORRUPTION", "RESUME_LOGIC"],
                recovery_function=self._manual_mode
            )
        ]
    
    def attempt_resume_recovery(self, error) -> Dict[str, Any]:
        """Attempt to recover from resume logic failures"""
        # Try rebuild from results first for resume errors
        try:
            new_checkpoint = self.rebuild_checkpoint_from_results()
            
            # Save the rebuilt checkpoint
            checkpoint_data = {
                'version': 'recovered',
                'resume_index': new_checkpoint['resume_index'],
                'processed_count': new_checkpoint['processed_count'],
                'failed_count': new_checkpoint.get('failed_count', 0),
                'timestamp': time.time(),
                'metadata': {'recovery_reason': getattr(error, 'error_type', 'RESUME_LOGIC')}
            }
            
            # Save using atomic operations
            AtomicFileOperations.atomic_write_json(self.checkpoint_file, checkpoint_data)
            
            return RecoveryStrategyPatterns.create_success_result(
                'rebuild_from_results',
                new_checkpoint=checkpoint_data,
                recovered_count=new_checkpoint['processed_count']
            )
            
        except Exception as e:
            return RecoveryStrategyPatterns.create_failure_result(
                'rebuild_from_results',
                f'Recovery failed: {str(e)}'
            )
    
    def rebuild_checkpoint_from_results(self) -> Dict[str, Any]:
        """Rebuild checkpoint by analyzing results file"""
        if not os.path.exists(self.results_file):
            raise FileNotFoundError("Results file not found for recovery")
        
        processed_count = 0
        failed_count = 0
        last_index = 0
        
        try:
            with open(self.results_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        try:
                            entry = json.loads(line.strip())
                            processed_count += 1
                            
                            # Count failures (empty slug or error field)
                            if not entry.get('slug') or entry.get('error'):
                                failed_count += 1
                                
                            # Track highest index (if available)
                            if 'index' in entry:
                                last_index = max(last_index, entry['index'])
                            else:
                                last_index = line_num  # Use line number as fallback
                                
                        except json.JSONDecodeError:
                            failed_count += 1  # Count malformed JSON as failure
                            
        except Exception as e:
            raise Exception(f"Failed to analyze results file: {str(e)}")
        
        return {
            'processed_count': processed_count,
            'failed_count': failed_count,
            'resume_index': last_index + 1,
            'version': 'recovered'
        }
    
    def attempt_safe_completion(self, error) -> Dict[str, Any]:
        """Safe completion when recovery strategies fail"""
        # Create a completion checkpoint
        completion_checkpoint = {
            'version': 'safe_completion',
            'resume_index': 0,  # Start from beginning
            'processed_count': 0,
            'failed_count': 0,
            'timestamp': time.time(),
            'metadata': {
                'original_error': getattr(error, 'error_type', 'UNKNOWN'),
                'completion_mode': True
            }
        }
        
        return {
            'success': True,
            'strategy': 'safe_completion',
            'completion_checkpoint': completion_checkpoint
        }
    
    def generate_manual_recovery_instructions(self, error_type: str, available_files: List[str]) -> Dict[str, Any]:
        """Generate manual recovery instructions"""
        instructions = {
            'manual_steps': [
                "1. Backup all existing files before attempting recovery",
                "2. Verify file integrity and format of available data files",
                "3. Manually inspect checkpoint and results files for corruption",
                "4. Create new checkpoint based on analysis",
                "5. Test recovery with small subset before full processing"
            ],
            'data_validation_commands': [
                f"python -m json.tool {self.results_file}",  # Validate JSON
                f"wc -l {self.results_file}",  # Count entries
                f"head -n 10 {self.results_file}",  # Inspect format
            ],
            'recovery_verification': [
                "Verify checkpoint format matches expected schema",
                "Confirm resume index is within valid range", 
                "Test batch processing with small sample"
            ]
        }
        
        return instructions
    
    def get_recovery_strategies_for_error(self, error_type: str) -> List[RecoveryStrategy]:
        """Get recovery strategies applicable to error type"""
        applicable_strategies = []
        
        for strategy in self.strategies:
            if not strategy.applicable_errors or error_type in strategy.applicable_errors:
                applicable_strategies.append(strategy)
        
        # Sort by priority
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "LOWEST": 3}
        applicable_strategies.sort(key=lambda s: priority_order.get(s.priority, 999))
        
        return applicable_strategies
    
    def attempt_backup_recovery(self) -> Dict[str, Any]:
        """Attempt recovery from backup files"""
        if not os.path.exists(self.backup_results_file):
            return {'success': False, 'error': 'No backup file available'}
        
        try:
            # Count entries in backup
            recovered_count = 0
            with open(self.backup_results_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        recovered_count += 1
            
            return {
                'success': True,
                'recovered_count': recovered_count,
                'source_file': 'backup'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def validate_recovery_data(self) -> Dict[str, Any]:
        """Validate recovery data for consistency"""
        if not os.path.exists(self.results_file):
            return {'is_valid': False, 'error': 'Results file not found'}
        
        valid_entries = 0
        invalid_entries = 0
        format_errors = []
        
        try:
            with open(self.results_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        try:
                            entry = json.loads(line.strip())
                            # Business logic validation - should have 'slug' field
                            if 'slug' in entry:
                                valid_entries += 1
                            else:
                                invalid_entries += 1
                                format_errors.append(f"Line {line_num}: Missing 'slug' field")
                        except json.JSONDecodeError as e:
                            invalid_entries += 1
                            format_errors.append(f"Line {line_num}: Invalid JSON - {str(e)}")
        
        except Exception as e:
            return {'is_valid': False, 'error': str(e)}
        
        is_valid = invalid_entries == 0
        
        return {
            'is_valid': is_valid,
            'valid_entries': valid_entries,
            'invalid_entries': invalid_entries,
            'format_errors': format_errors
        }
    
    def attempt_recovery_with_rollback(self) -> Dict[str, Any]:
        """Attempt recovery with rollback capability"""
        # Save original state first
        original_checkpoint = None
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    original_checkpoint = json.load(f)
            except:
                pass
        
        try:
            # Attempt recovery
            recovery_result = self.rebuild_checkpoint_from_results()
            return {'rollback_successful': False, 'recovery_succeeded': True}
            
        except Exception as e:
            # Recovery failed, attempt rollback
            if original_checkpoint:
                try:
                    AtomicFileOperations.atomic_write_json(self.checkpoint_file, original_checkpoint)
                    return {
                        'rollback_successful': True, 
                        'original_state_restored': True,
                        'recovery_error': str(e)
                    }
                except:
                    pass
            
            return {'rollback_successful': False, 'recovery_error': str(e)}
    
    def _rebuild_from_results(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy implementation for rebuilding from results"""
        try:
            checkpoint = self.rebuild_checkpoint_from_results()
            return {"success": True, "checkpoint": checkpoint}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _backup_recovery(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy implementation for backup recovery"""
        return self.attempt_backup_recovery()
    
    def _safe_completion(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy implementation for safe completion"""
        return self.attempt_safe_completion(context.get('error'))
    
    def _manual_mode(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy implementation for manual mode"""
        instructions = self.generate_manual_recovery_instructions(
            context.get('error_type', 'UNKNOWN'),
            context.get('available_files', [])
        )
        return {"success": True, "instructions": instructions}