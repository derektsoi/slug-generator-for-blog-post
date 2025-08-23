#!/usr/bin/env python3
"""
Centralized Error Classification - Structured error hierarchy with recovery suggestions
Implementation follows TDD approach - minimal code to satisfy test requirements.
"""

import json
import time
from typing import Dict, Any, List, Optional

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


class BatchProcessingError(BaseTimestampedException):
    """Base class for batch processing errors with recovery support"""
    
    def __init__(self, message: str, error_type: str, recovery_suggestion: str = None,
                 severity: str = "MEDIUM", context: Dict[str, Any] = None, cause: Exception = None):
        super().__init__(message)
        self.error_type = error_type
        self.recovery_suggestion = recovery_suggestion
        self.severity = severity
        self.context = context or {}
        self.cause = cause
    
    def get_error_summary(self) -> str:
        """Get formatted error summary"""
        return f"[{self.error_type}] {str(self)} (Severity: {self.severity})"
    
    def get_recovery_instructions(self) -> str:
        """Get recovery instructions"""
        if self.recovery_suggestion:
            return f"Recovery: {self.recovery_suggestion}"
        return "No specific recovery instructions available"
    
    def get_full_traceback(self) -> str:
        """Get full traceback including chained errors"""
        traceback_info = f"{self.__class__.__name__}: {str(self)}"
        if self.cause:
            traceback_info += f"\nCaused by: {self.cause.__class__.__name__}: {str(self.cause)}"
        return traceback_info
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize error for logging and debugging"""
        return {
            "error_type": self.error_type,
            "message": str(self),
            "severity": self.severity,
            "timestamp": self.timestamp,
            "recovery_suggestion": self.recovery_suggestion,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None
        }
    
    @classmethod
    def create_from_exception(cls, exception: Exception, context: Dict[str, Any] = None) -> 'BatchProcessingError':
        """Factory method to create appropriate error type from exception"""
        error_type = "UNKNOWN_ERROR"
        recovery_suggestion = "Contact support with error details"
        
        # Simple heuristics to detect error types
        if context and "resume" in context.get("operation", "").lower():
            error_type = "RESUME_LOGIC"
            recovery_suggestion = "Check checkpoint format and file integrity"
        elif isinstance(exception, (json.JSONDecodeError, ValueError)) and "json" in str(exception).lower():
            error_type = "JSON_FORMAT"
            recovery_suggestion = "Validate and repair JSON format"
        
        return cls(str(exception), error_type, recovery_suggestion, context=context, cause=exception)


class ResumeLogicError(BatchProcessingError):
    """Resume logic specific errors with checkpoint context"""
    
    def __init__(self, message: str, checkpoint_data: Dict[str, Any] = None, corruption_type: str = None):
        super().__init__(
            message, 
            "RESUME_LOGIC", 
            recovery_suggestion="Check checkpoint format and file integrity"
        )
        self.checkpoint_data = checkpoint_data or {}
        self.corruption_type = corruption_type
    
    def get_recovery_strategies(self) -> List[str]:
        """Get specific recovery strategies for resume errors"""
        return [
            "rebuild_from_results",
            "manual_checkpoint_repair", 
            "safe_restart"
        ]


class ProgressSyncError(BatchProcessingError):
    """Progress synchronization errors with state comparison"""
    
    def __init__(self, message: str, memory_state: Dict[str, Any], file_state: Dict[str, Any]):
        super().__init__(
            message,
            "PROGRESS_SYNC",
            recovery_suggestion="Verify file write permissions and progress file format"
        )
        self.memory_state = memory_state
        self.file_state = file_state
    
    def get_sync_diff(self) -> Dict[str, Any]:
        """Calculate differences between memory and file state"""
        diff = {}
        for key in self.memory_state.keys():
            if key in self.file_state:
                if isinstance(self.memory_state[key], (int, float)):
                    diff[key] = self.memory_state[key] - self.file_state[key]
                else:
                    diff[key] = self.memory_state[key] != self.file_state[key]
        return diff
    
    def get_diagnostic_info(self) -> Dict[str, Any]:
        """Get diagnostic information for troubleshooting"""
        diagnostic = {}
        
        # Calculate sync lag
        memory_time = self.memory_state.get('timestamp', 0)
        file_time = self.file_state.get('timestamp', 0)
        diagnostic['sync_lag_seconds'] = abs(memory_time - file_time)
        
        # Calculate how far ahead memory is
        memory_processed = self.memory_state.get('processed', 0)
        file_processed = self.file_state.get('processed', 0)
        diagnostic['memory_ahead_by'] = memory_processed - file_processed
        
        return diagnostic
    
    def get_recovery_priority(self) -> str:
        """Determine recovery priority based on sync difference"""
        diff = self.get_sync_diff()
        processed_diff = abs(diff.get('processed', 0))
        
        if processed_diff <= 5:
            return "LOW"
        elif processed_diff <= 20:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def to_dict(self) -> Dict[str, Any]:
        """Extended serialization including state data"""
        base_dict = super().to_dict()
        base_dict.update({
            'memory_state': self.memory_state,
            'file_state': self.file_state,
            'sync_diff': self.get_sync_diff(),
            'recovery_priority': self.get_recovery_priority()
        })
        return base_dict


class JSONFormatError(BatchProcessingError):
    """JSON format errors with repair suggestions"""
    
    def __init__(self, message: str, line_number: int = None, char_position: int = None,
                 invalid_content: str = None, repair_hint: str = None):
        super().__init__(
            message,
            "JSON_FORMAT", 
            recovery_suggestion="Validate and repair JSON format"
        )
        self.line_number = line_number
        self.char_position = char_position
        self.invalid_content = invalid_content
        self.repair_hint = repair_hint
    
    def get_repair_suggestions(self) -> List[str]:
        """Get specific repair suggestions based on hint"""
        suggestions = []
        
        if self.repair_hint == "MISSING_QUOTE":
            suggestions.append("Add closing quote to unterminated string")
        elif self.repair_hint == "MISSING_BRACKET":
            suggestions.append("Add closing bracket or brace")
        elif self.repair_hint == "INVALID_ESCAPE":
            suggestions.append("Fix invalid escape sequence")
        else:
            suggestions.append("Validate JSON format using online validator")
            suggestions.append("Check for missing quotes, brackets, or commas")
        
        return suggestions
    
    def __str__(self) -> str:
        """Enhanced string representation with line info"""
        base_str = super().__str__()
        if self.line_number is not None:
            base_str += f" at line {self.line_number}"
        if self.char_position is not None:
            base_str += f", position {self.char_position}"
        return base_str


class DependencyError(BatchProcessingError):
    """Dependency and version conflict errors"""
    
    def __init__(self, message: str, missing_dependencies: List[str] = None,
                 version_conflicts: Dict[str, Dict[str, str]] = None):
        super().__init__(
            message,
            "DEPENDENCY_ERROR",
            recovery_suggestion="Install or upgrade required dependencies"
        )
        self.missing_dependencies = missing_dependencies or []
        self.version_conflicts = version_conflicts or {}
    
    def get_installation_commands(self) -> str:
        """Get pip installation commands for missing dependencies"""
        if not self.missing_dependencies:
            return "No missing dependencies"
        
        deps_str = " ".join(self.missing_dependencies)
        return f"pip install {deps_str}"
    
    def get_resolution_steps(self) -> List[str]:
        """Get steps to resolve dependency issues"""
        steps = []
        
        if self.missing_dependencies:
            steps.append(f"Install missing dependencies: {self.get_installation_commands()}")
        
        if self.version_conflicts:
            for package, versions in self.version_conflicts.items():
                current = versions.get("current", "unknown")
                required = versions.get("required", "unknown")
                steps.append(f"Upgrade {package} from {current} to {required}")
        
        return steps