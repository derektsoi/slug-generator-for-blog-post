#!/usr/bin/env python3
"""
RobustCheckpointManager - Schema-validated checkpoint operations with atomic saves and recovery
Implementation follows TDD approach - minimal code to satisfy test requirements.
Refactored to use shared file operation utilities.
"""

import json
import os
import time
import threading
from typing import Dict, Any, Optional

# Handle both relative and absolute imports for test compatibility
try:
    from .file_operations import BaseTimestampedException, AtomicFileOperations
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
    AtomicFileOperations = file_ops_module.AtomicFileOperations


class CheckpointFormatError(BaseTimestampedException):
    """Custom exception for checkpoint format validation errors"""
    
    def __init__(self, message: str, validation_details: Dict[str, Any] = None):
        super().__init__(message)
        self.validation_details = validation_details or {}


class CheckpointRecoveryError(BaseTimestampedException):
    """Custom exception for checkpoint recovery errors"""
    
    def __init__(self, message: str, recovery_attempts: int = 0, last_error: str = None):
        super().__init__(message)
        self.recovery_attempts = recovery_attempts
        self.last_error = last_error


class RobustCheckpointManager:
    """
    Schema-validated checkpoint manager with atomic operations and backup recovery.
    
    Addresses critical resume logic failures where batch processing restarts from 0
    instead of proper checkpoints, causing wasted API calls and duplicate processing.
    """
    
    # Required checkpoint schema
    CHECKPOINT_SCHEMA = {
        'version': str,
        'resume_index': int,
        'processed_count': int,
        'failed_count': int,
        'timestamp': (int, float),
        'metadata': dict
    }
    
    def __init__(self, output_dir: str, checkpoint_interval: int = 100):
        """
        Initialize robust checkpoint manager.
        
        Args:
            output_dir: Directory for checkpoint files
            checkpoint_interval: Interval between checkpoint saves (not used in minimal implementation)
        """
        self.output_dir = output_dir
        self.checkpoint_file = os.path.join(output_dir, 'checkpoint.json')
        self.backup_file = f"{self.checkpoint_file}.backup"
        self.temp_file = f"{self.checkpoint_file}.tmp"
        self._lock = threading.Lock()
        
        # Ensure directory exists using shared utility
        AtomicFileOperations.ensure_directory(self.checkpoint_file)
    
    def save_checkpoint(self, data: Dict[str, Any]) -> bool:
        """
        Save checkpoint with schema validation and atomic operations.
        
        Args:
            data: Checkpoint data dictionary
            
        Returns:
            bool: True if save successful, False otherwise
            
        Raises:
            CheckpointFormatError: If data doesn't match required schema
        """
        try:
            # Validate schema before saving
            self._validate_checkpoint_format(data)
            
            # Use shared atomic backup and write operation
            return AtomicFileOperations.atomic_backup_and_write(
                self.checkpoint_file, data, backup_enabled=True, lock=self._lock
            )
            
        except CheckpointFormatError:
            # Re-raise format errors for caller to handle
            raise
    
    def load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """
        Load checkpoint with schema validation and backup recovery.
        
        Returns:
            dict: Loaded checkpoint data, or None if no valid checkpoint found
        """
        # Try loading main checkpoint first using shared utility
        data = AtomicFileOperations.safe_read_json(self.checkpoint_file, self._lock)
        
        if data is not None:
            try:
                # Validate loaded data
                self._validate_checkpoint_format(data)
                return data
            except CheckpointFormatError:
                # Main checkpoint corrupted, try backup recovery
                return self._attempt_backup_recovery()
        
        # No checkpoint file exists
        return None
    
    def _validate_checkpoint_format(self, data: Dict[str, Any]) -> None:
        """
        Validate checkpoint data against required schema.
        
        Args:
            data: Checkpoint data to validate
            
        Raises:
            CheckpointFormatError: If validation fails
        """
        for field, expected_type in self.CHECKPOINT_SCHEMA.items():
            if field not in data:
                raise CheckpointFormatError(
                    f"Missing required field: {field}",
                    {'field': field, 'expected': expected_type.__name__ if hasattr(expected_type, '__name__') else str(expected_type)}
                )
            
            value = data[field]
            
            # Handle multiple acceptable types (like int, float for timestamp)
            if isinstance(expected_type, tuple):
                if not any(isinstance(value, t) for t in expected_type):
                    raise CheckpointFormatError(
                        f"Invalid type for field {field}",
                        {'field': field, 'expected': [t.__name__ for t in expected_type], 'actual': type(value).__name__}
                    )
            else:
                if not isinstance(value, expected_type):
                    raise CheckpointFormatError(
                        f"Invalid type for field {field}",
                        {'field': field, 'expected': expected_type.__name__, 'actual': type(value).__name__}
                    )
    
    def _attempt_backup_recovery(self) -> Optional[Dict[str, Any]]:
        """
        Attempt to recover checkpoint from backup file.
        
        Returns:
            dict: Recovered checkpoint data, or None if recovery failed
        """
        if not os.path.exists(self.backup_file):
            return None
        
        try:
            with open(self.backup_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate backup data
            self._validate_checkpoint_format(data)
            
            # Recovery successful - restore main checkpoint from backup
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return data
            
        except (json.JSONDecodeError, CheckpointFormatError, OSError):
            # Backup recovery failed
            return None
    
    def _cleanup_temp_file(self):
        """Clean up temporary file if it exists"""
        try:
            if os.path.exists(self.temp_file):
                os.remove(self.temp_file)
        except:
            pass