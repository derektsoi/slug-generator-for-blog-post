#!/usr/bin/env python3
"""
Shared file operation utilities for atomic and thread-safe operations.
Extracted from Phase 1 components to eliminate code duplication.
"""

import json
import os
import threading
import time
from typing import Dict, Any, Optional


class BaseTimestampedException(Exception):
    """Base exception class with automatic timestamp for all core components"""
    
    def __init__(self, message: str):
        super().__init__(message)
        self.timestamp = time.time()


class AtomicFileOperations:
    """
    Utility class for atomic file operations shared across components.
    Provides consistent temp file + rename pattern used by all Phase 1 components.
    """
    
    @staticmethod
    def ensure_directory(file_path: str) -> bool:
        """
        Ensure directory exists for given file path.
        
        Args:
            file_path: Full path to file
            
        Returns:
            bool: True if directory exists or was created successfully
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            return True
        except (OSError, PermissionError):
            return False
    
    @staticmethod
    def atomic_write_json(file_path: str, data: Dict[str, Any], lock: threading.Lock = None) -> bool:
        """
        Atomically write JSON data to file using temp file + rename pattern.
        
        Args:
            file_path: Target file path
            data: Data to write as JSON
            lock: Optional thread lock for synchronization
            
        Returns:
            bool: True if write successful, False otherwise
        """
        temp_path = f"{file_path}.tmp"
        
        def _do_write():
            try:
                # Write to temp file first
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    f.flush()
                    os.fsync(f.fileno())
                
                # Atomic rename
                os.rename(temp_path, file_path)
                return True
                
            except Exception:
                # Cleanup temp file on failure
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except:
                    pass
                return False
        
        if lock:
            with lock:
                return _do_write()
        else:
            return _do_write()
    
    @staticmethod
    def safe_read_json(file_path: str, lock: threading.Lock = None) -> Optional[Dict[str, Any]]:
        """
        Safely read JSON data from file with error handling.
        
        Args:
            file_path: File path to read
            lock: Optional thread lock for synchronization
            
        Returns:
            dict: Loaded JSON data, or None if read failed
        """
        def _do_read():
            try:
                if not os.path.exists(file_path):
                    return None
                    
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
                    
            except (json.JSONDecodeError, OSError):
                return None
        
        if lock:
            with lock:
                return _do_read()
        else:
            return _do_read()
    
    @staticmethod
    def atomic_backup_and_write(file_path: str, data: Dict[str, Any], 
                               backup_enabled: bool = True, lock: threading.Lock = None) -> bool:
        """
        Atomically write with automatic backup of existing file.
        
        Args:
            file_path: Target file path
            data: Data to write
            backup_enabled: Whether to create backup
            lock: Optional thread lock
            
        Returns:
            bool: True if successful, False otherwise
        """
        backup_path = f"{file_path}.backup"
        temp_path = f"{file_path}.tmp"
        
        def _do_backup_write():
            try:
                # Create backup if enabled and file exists
                if backup_enabled and os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as src:
                        with open(backup_path, 'w', encoding='utf-8') as dst:
                            dst.write(src.read())
                
                # Write to temp file
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    f.flush()
                    os.fsync(f.fileno())
                
                # Atomic rename
                os.rename(temp_path, file_path)
                return True
                
            except Exception:
                # Cleanup on failure
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except:
                    pass
                return False
        
        if lock:
            with lock:
                return _do_backup_write()
        else:
            return _do_backup_write()


class JSONLOperations:
    """
    Specialized operations for JSONL (JSON Lines) format.
    Handles the specific newline requirements for proper JSONL formatting.
    """
    
    @staticmethod
    def append_jsonl_entry(file_path: str, data: Dict[str, Any], lock: threading.Lock = None) -> bool:
        """
        Append single JSON entry to JSONL file with guaranteed newline formatting.
        
        Args:
            file_path: Target JSONL file
            data: Data to append as JSON line
            lock: Optional thread lock
            
        Returns:
            bool: True if successful, False otherwise
        """
        def _do_append():
            try:
                # Validate JSON serialization first
                json_str = json.dumps(data, ensure_ascii=False)
                
                # Append with guaranteed newline
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(json_str + '\n')  # CRITICAL: Always add newline
                    f.flush()
                    os.fsync(f.fileno())
                
                return True
                
            except (TypeError, ValueError, OSError):
                return False
        
        if lock:
            with lock:
                return _do_append()
        else:
            return _do_append()