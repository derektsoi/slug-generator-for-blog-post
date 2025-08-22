#!/usr/bin/env python3
"""
RobustCheckpointManager - Schema-validated checkpoint operations with atomic saves and recovery
Implementation follows TDD approach - minimal code to satisfy test requirements.
"""

import json
import os
import time
import threading
from typing import Dict, Any, Optional


class CheckpointFormatError(Exception):
    """Custom exception for checkpoint format validation errors"""
    
    def __init__(self, message: str, validation_details: Dict[str, Any] = None):
        super().__init__(message)
        self.validation_details = validation_details or {}
        self.timestamp = time.time()


class CheckpointRecoveryError(Exception):
    """Custom exception for checkpoint recovery errors"""
    
    def __init__(self, message: str, recovery_attempts: int = 0, last_error: str = None):
        super().__init__(message)
        self.recovery_attempts = recovery_attempts
        self.last_error = last_error
        self.timestamp = time.time()


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
        
        # Ensure directory exists
        os.makedirs(output_dir, exist_ok=True)
    
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
        with self._lock:
            try:
                # Validate schema before saving
                self._validate_checkpoint_format(data)
                
                # Write to temp file first (atomic operation)
                with open(self.temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    f.flush()
                    os.fsync(f.fileno())
                
                # Create backup of existing checkpoint if it exists
                if os.path.exists(self.checkpoint_file):
                    with open(self.checkpoint_file, 'r', encoding='utf-8') as src:
                        with open(self.backup_file, 'w', encoding='utf-8') as dst:
                            dst.write(src.read())
                
                # Atomic move from temp to main
                os.rename(self.temp_file, self.checkpoint_file)
                
                return True
                
            except CheckpointFormatError:
                # Re-raise format errors for caller to handle
                raise
            except Exception:
                # File operation errors
                self._cleanup_temp_file()
                return False
    
    def load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """
        Load checkpoint with schema validation and backup recovery.
        
        Returns:
            dict: Loaded checkpoint data, or None if no valid checkpoint found
        """
        with self._lock:
            # Try loading main checkpoint first
            if os.path.exists(self.checkpoint_file):
                try:
                    with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Validate loaded data
                    self._validate_checkpoint_format(data)
                    return data
                    
                except (json.JSONDecodeError, CheckpointFormatError):
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