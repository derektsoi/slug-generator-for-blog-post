#!/usr/bin/env python3
"""
Shared Error Handling Patterns - Common patterns extracted from error classification and recovery
Refactored from error_classification.py and recovery_system.py for DRY principles.
"""

import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass

# Use shared import utilities
try:
    from .import_utils import import_from_core
    BaseTimestampedException = import_from_core('file_operations', 'BaseTimestampedException')
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


@dataclass
class ErrorContext:
    """Standardized error context for enriched error information"""
    operation: str = None
    file_path: str = None
    line_number: int = None
    batch_id: str = None
    url_count: int = None
    current_index: int = None
    additional_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_data is None:
            self.additional_data = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error context to dictionary for serialization"""
        return {
            'operation': self.operation,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'batch_id': self.batch_id,
            'url_count': self.url_count,
            'current_index': self.current_index,
            'additional_data': self.additional_data
        }


class ErrorContextEnricher:
    """Utility class for enriching error contexts with diagnostic information"""
    
    @staticmethod
    def enrich_with_file_info(context: ErrorContext, file_path: str, line_number: int = None) -> ErrorContext:
        """Enrich context with file information"""
        context.file_path = file_path
        context.line_number = line_number
        return context
    
    @staticmethod
    def enrich_with_batch_info(context: ErrorContext, batch_id: str, url_count: int, current_index: int) -> ErrorContext:
        """Enrich context with batch processing information"""
        context.batch_id = batch_id
        context.url_count = url_count
        context.current_index = current_index
        return context
    
    @staticmethod
    def enrich_with_operation(context: ErrorContext, operation: str) -> ErrorContext:
        """Enrich context with operation information"""
        context.operation = operation
        return context


class DiagnosticInfoGenerator:
    """Standardized diagnostic information generation for different error types"""
    
    @staticmethod
    def generate_sync_diagnostic(memory_state: Dict[str, Any], file_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate diagnostic information for synchronization issues"""
        diagnostic = {}
        
        # Calculate sync lag
        memory_time = memory_state.get('timestamp', 0)
        file_time = file_state.get('timestamp', 0)
        diagnostic['sync_lag_seconds'] = abs(memory_time - file_time)
        
        # Calculate processing differences
        memory_processed = memory_state.get('processed', 0)
        file_processed = file_state.get('processed', 0)
        diagnostic['memory_ahead_by'] = memory_processed - file_processed
        
        # Calculate percentage differences
        if file_processed > 0:
            diagnostic['sync_percentage'] = (memory_processed / file_processed) * 100 - 100
        else:
            diagnostic['sync_percentage'] = 0
        
        return diagnostic
    
    @staticmethod
    def generate_file_diagnostic(file_path: str, expected_format: str = "jsonl") -> Dict[str, Any]:
        """Generate diagnostic information for file-related issues"""
        import os
        import json
        
        diagnostic = {
            'file_exists': os.path.exists(file_path),
            'file_size': 0,
            'line_count': 0,
            'valid_entries': 0,
            'invalid_entries': 0,
            'format_errors': []
        }
        
        if not diagnostic['file_exists']:
            return diagnostic
        
        diagnostic['file_size'] = os.path.getsize(file_path)
        
        if expected_format == "jsonl":
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        diagnostic['line_count'] += 1
                        if line.strip():
                            try:
                                json.loads(line.strip())
                                diagnostic['valid_entries'] += 1
                            except json.JSONDecodeError as e:
                                diagnostic['invalid_entries'] += 1
                                diagnostic['format_errors'].append(f"Line {line_num}: {str(e)}")
            except Exception as e:
                diagnostic['format_errors'].append(f"File read error: {str(e)}")
        
        return diagnostic


class RecoveryStrategyPatterns:
    """Common patterns for recovery strategy implementation"""
    
    @staticmethod
    def execute_with_fallback(strategies: List[Callable], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute recovery strategies with fallback pattern"""
        last_error = None
        attempted_strategies = []
        
        for strategy in strategies:
            try:
                strategy_name = getattr(strategy, '__name__', 'unknown_strategy')
                attempted_strategies.append(strategy_name)
                result = strategy(context)
                
                if result.get('success', False):
                    result['attempted_strategies'] = attempted_strategies
                    return result
                else:
                    last_error = result.get('error', 'Strategy failed without details')
                    
            except Exception as e:
                last_error = str(e)
        
        return {
            'success': False,
            'error': f'All strategies failed. Last error: {last_error}',
            'attempted_strategies': attempted_strategies
        }
    
    @staticmethod
    def validate_recovery_result(result: Dict[str, Any], required_fields: List[str] = None) -> bool:
        """Validate recovery result has required fields"""
        if required_fields is None:
            required_fields = ['success']
        
        return all(field in result for field in required_fields)
    
    @staticmethod
    def create_success_result(strategy_name: str, **kwargs) -> Dict[str, Any]:
        """Create standardized success result"""
        result = {
            'success': True,
            'strategy_used': strategy_name,
            'timestamp': time.time()
        }
        result.update(kwargs)
        return result
    
    @staticmethod
    def create_failure_result(strategy_name: str, error_message: str, **kwargs) -> Dict[str, Any]:
        """Create standardized failure result"""
        result = {
            'success': False,
            'strategy_used': strategy_name,
            'error': error_message,
            'timestamp': time.time()
        }
        result.update(kwargs)
        return result


class ErrorSeverityCalculator:
    """Calculate error severity based on various factors"""
    
    SEVERITY_LEVELS = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    
    @staticmethod
    def calculate_sync_severity(memory_state: Dict[str, Any], file_state: Dict[str, Any]) -> str:
        """Calculate severity for synchronization errors (backward compatible with original logic)"""
        diagnostic = DiagnosticInfoGenerator.generate_sync_diagnostic(memory_state, file_state)
        
        # Use processed count difference as primary factor (matching original algorithm)
        memory_processed = memory_state.get('processed', 0)
        file_processed = file_state.get('processed', 0)
        processed_diff = abs(memory_processed - file_processed)
        
        # Original algorithm logic for backward compatibility
        if processed_diff <= 5:
            return 'LOW'
        elif processed_diff <= 20:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    @staticmethod
    def calculate_file_severity(file_diagnostic: Dict[str, Any]) -> str:
        """Calculate severity for file-related errors"""
        if not file_diagnostic.get('file_exists', False):
            return 'CRITICAL'
        
        invalid_entries = file_diagnostic.get('invalid_entries', 0)
        total_entries = file_diagnostic.get('valid_entries', 0) + invalid_entries
        
        if total_entries == 0:
            return 'HIGH'
        
        corruption_rate = invalid_entries / total_entries
        
        if corruption_rate > 0.5:
            return 'CRITICAL'
        elif corruption_rate > 0.2:
            return 'HIGH'
        elif corruption_rate > 0.1:
            return 'MEDIUM'
        else:
            return 'LOW'


class CommonRecoveryInstructions:
    """Standardized recovery instructions for common scenarios"""
    
    @staticmethod
    def get_file_corruption_instructions(file_path: str) -> Dict[str, List[str]]:
        """Get recovery instructions for file corruption"""
        return {
            'immediate_actions': [
                f"1. Stop all processes writing to {file_path}",
                "2. Create backup of current file state",
                "3. Analyze corruption extent with diagnostic tools"
            ],
            'validation_commands': [
                f"python -m json.tool {file_path} > /dev/null",  # Validate JSON
                f"wc -l {file_path}",  # Count lines
                f"head -n 5 {file_path}",  # Inspect format
                f"tail -n 5 {file_path}"   # Check end of file
            ],
            'recovery_options': [
                "Option 1: Restore from backup if available",
                "Option 2: Rebuild from alternative data source", 
                "Option 3: Manual repair of corrupted sections",
                "Option 4: Safe restart with data reconstruction"
            ],
            'verification_steps': [
                "Verify file format matches expected schema",
                "Test processing with small sample",
                "Confirm data integrity with checksums"
            ]
        }
    
    @staticmethod
    def get_sync_recovery_instructions(sync_severity: str) -> Dict[str, List[str]]:
        """Get recovery instructions for synchronization issues"""
        base_instructions = {
            'immediate_actions': [
                "1. Pause all concurrent processing",
                "2. Analyze sync lag and processing differences",
                "3. Identify authoritative data source"
            ],
            'diagnostic_commands': [
                "Compare memory vs file timestamps",
                "Check processing counts and indices",
                "Analyze sync patterns over time"
            ]
        }
        
        if sync_severity in ['HIGH', 'CRITICAL']:
            base_instructions['immediate_actions'].extend([
                "4. URGENT: Stop all processing immediately",
                "5. Backup current state before recovery"
            ])
            base_instructions['recovery_options'] = [
                "Priority 1: Force synchronization from authoritative source",
                "Priority 2: Rollback to last known good state",
                "Priority 3: Manual state reconstruction"
            ]
        else:
            base_instructions['recovery_options'] = [
                "Option 1: Wait for natural convergence", 
                "Option 2: Trigger manual synchronization",
                "Option 3: Restart processing from checkpoint"
            ]
        
        return base_instructions