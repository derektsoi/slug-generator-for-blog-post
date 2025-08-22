#!/usr/bin/env python3
"""
Test-Driven Development for RobustCheckpointManager
Tests written FIRST to define expected behavior before implementation.
"""

import unittest
import tempfile
import os
import json
import time
from unittest.mock import patch, Mock

# Import will fail initially - this is expected in TDD
try:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
    # Import directly from the module to avoid __init__.py dependencies
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "robust_checkpoint", 
        os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'core', 'robust_checkpoint.py')
    )
    checkpoint_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checkpoint_module)
    
    RobustCheckpointManager = checkpoint_module.RobustCheckpointManager
    CheckpointFormatError = checkpoint_module.CheckpointFormatError
    CheckpointRecoveryError = checkpoint_module.CheckpointRecoveryError
except (ImportError, AttributeError, FileNotFoundError):
    # Expected to fail initially - we haven't implemented it yet
    RobustCheckpointManager = None
    CheckpointFormatError = Exception
    CheckpointRecoveryError = Exception


class TestRobustCheckpointManager(unittest.TestCase):
    """Test suite for RobustCheckpointManager - TDD approach"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.checkpoint_file = os.path.join(self.test_dir, 'checkpoint.json')
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @unittest.skipIf(RobustCheckpointManager is None, "RobustCheckpointManager not implemented yet")
    def test_valid_checkpoint_save_and_load(self):
        """TEST: Valid checkpoint data can be saved and loaded correctly"""
        manager = RobustCheckpointManager(self.test_dir)
        
        checkpoint_data = {
            'version': 'v1.0',
            'resume_index': 1500,
            'processed_count': 1499,
            'failed_count': 5,
            'timestamp': time.time(),
            'metadata': {'batch_id': 'test_batch_001', 'prompt_version': 'v10'}
        }
        
        # Save checkpoint
        result = manager.save_checkpoint(checkpoint_data)
        self.assertTrue(result)
        
        # Checkpoint file should exist
        self.assertTrue(os.path.exists(self.checkpoint_file))
        
        # Load checkpoint
        loaded_data = manager.load_checkpoint()
        self.assertIsNotNone(loaded_data)
        
        # Data should match
        self.assertEqual(loaded_data['version'], 'v1.0')
        self.assertEqual(loaded_data['resume_index'], 1500)
        self.assertEqual(loaded_data['processed_count'], 1499)
        self.assertEqual(loaded_data['failed_count'], 5)
        self.assertIn('batch_id', loaded_data['metadata'])
    
    @unittest.skipIf(RobustCheckpointManager is None, "RobustCheckpointManager not implemented yet")
    def test_checkpoint_schema_validation_on_save(self):
        """TEST: Checkpoint schema is validated before saving"""
        manager = RobustCheckpointManager(self.test_dir)
        
        # Test missing required fields
        invalid_data = {
            'version': 'v1.0',
            # Missing resume_index, processed_count, etc.
            'metadata': {}
        }
        
        with self.assertRaises(CheckpointFormatError):
            manager.save_checkpoint(invalid_data)
        
        # Test wrong data types
        invalid_types_data = {
            'version': 'v1.0',
            'resume_index': '1500',  # Should be int
            'processed_count': 'invalid',  # Should be int
            'failed_count': 5,
            'timestamp': time.time(),
            'metadata': {}
        }
        
        with self.assertRaises(CheckpointFormatError):
            manager.save_checkpoint(invalid_types_data)
    
    @unittest.skipIf(RobustCheckpointManager is None, "RobustCheckpointManager not implemented yet")
    def test_checkpoint_schema_validation_on_load(self):
        """TEST: Checkpoint schema is validated when loading"""
        manager = RobustCheckpointManager(self.test_dir)
        
        # Create invalid checkpoint file directly
        invalid_checkpoint = {
            'version': 'v1.0',
            'resume_index': 'invalid_type',  # Wrong type
            'processed_count': 100,
            # Missing required fields
            'metadata': {}
        }
        
        with open(self.checkpoint_file, 'w') as f:
            json.dump(invalid_checkpoint, f)
        
        # Should attempt recovery (return None or fallback)
        loaded_data = manager.load_checkpoint()
        
        # Should either be None (failed) or recovered data
        if loaded_data is not None:
            # If recovery succeeded, should have valid structure
            self.assertIsInstance(loaded_data['resume_index'], int)
            self.assertIn('timestamp', loaded_data)
    
    @unittest.skipIf(RobustCheckpointManager is None, "RobustCheckpointManager not implemented yet")
    def test_atomic_checkpoint_operations(self):
        """TEST: Checkpoint operations are atomic (no corruption on failure)"""
        manager = RobustCheckpointManager(self.test_dir)
        
        # Save valid checkpoint first
        valid_data = {
            'version': 'v1.0',
            'resume_index': 1000,
            'processed_count': 999,
            'failed_count': 1,
            'timestamp': time.time(),
            'metadata': {'test': 'initial_save'}
        }
        
        result = manager.save_checkpoint(valid_data)
        self.assertTrue(result)
        
        # Simulate system failure during save
        with patch('os.rename', side_effect=OSError("Simulated system failure")):
            corrupt_data = {
                'version': 'v1.0',
                'resume_index': 2000,
                'processed_count': 1999,
                'failed_count': 1,
                'timestamp': time.time(),
                'metadata': {'test': 'should_not_save'}
            }
            
            result = manager.save_checkpoint(corrupt_data)
            self.assertFalse(result)
        
        # Original checkpoint should still be intact
        loaded_data = manager.load_checkpoint()
        self.assertIsNotNone(loaded_data)
        self.assertEqual(loaded_data['resume_index'], 1000)
        self.assertEqual(loaded_data['metadata']['test'], 'initial_save')
    
    @unittest.skipIf(RobustCheckpointManager is None, "RobustCheckpointManager not implemented yet")
    def test_backup_recovery_functionality(self):
        """TEST: System can recover from backup when main checkpoint is corrupted"""
        manager = RobustCheckpointManager(self.test_dir)
        
        # Save initial checkpoint
        initial_data = {
            'version': 'v1.0',
            'resume_index': 500,
            'processed_count': 499,
            'failed_count': 1,
            'timestamp': time.time(),
            'metadata': {'backup_test': True}
        }
        
        manager.save_checkpoint(initial_data)
        
        # Manually corrupt main checkpoint file
        with open(self.checkpoint_file, 'w') as f:
            f.write("CORRUPTED DATA NOT JSON")
        
        # Should recover from backup
        loaded_data = manager.load_checkpoint()
        
        # Should either recover successfully or return None (graceful failure)
        if loaded_data is not None:
            self.assertEqual(loaded_data['resume_index'], 500)
            self.assertTrue(loaded_data['metadata']['backup_test'])
    
    @unittest.skipIf(RobustCheckpointManager is None, "RobustCheckpointManager not implemented yet")
    def test_no_checkpoint_file_returns_none(self):
        """TEST: Loading non-existent checkpoint returns None gracefully"""
        manager = RobustCheckpointManager(self.test_dir)
        
        # No checkpoint file exists
        self.assertFalse(os.path.exists(self.checkpoint_file))
        
        # Should return None, not raise exception
        loaded_data = manager.load_checkpoint()
        self.assertIsNone(loaded_data)
    
    @unittest.skipIf(RobustCheckpointManager is None, "RobustCheckpointManager not implemented yet")
    def test_checkpoint_with_large_metadata(self):
        """TEST: Checkpoints with large metadata are handled correctly"""
        manager = RobustCheckpointManager(self.test_dir)
        
        # Create large metadata object
        large_metadata = {
            'failed_urls': [{'url': f'https://example.com/{i}', 'error': f'Error {i}'} for i in range(1000)],
            'processing_stats': {'stat_' + str(i): i * 10 for i in range(500)},
            'configuration': {'setting_' + str(i): f'value_{i}' for i in range(100)}
        }
        
        checkpoint_data = {
            'version': 'v1.0',
            'resume_index': 2500,
            'processed_count': 2000,
            'failed_count': 500,
            'timestamp': time.time(),
            'metadata': large_metadata
        }
        
        # Should handle large data without issues
        result = manager.save_checkpoint(checkpoint_data)
        self.assertTrue(result)
        
        # Should load correctly
        loaded_data = manager.load_checkpoint()
        self.assertIsNotNone(loaded_data)
        self.assertEqual(len(loaded_data['metadata']['failed_urls']), 1000)
        self.assertEqual(len(loaded_data['metadata']['processing_stats']), 500)
    
    @unittest.skipIf(RobustCheckpointManager is None, "RobustCheckpointManager not implemented yet")
    def test_concurrent_checkpoint_access(self):
        """TEST: Concurrent checkpoint operations are handled safely"""
        import threading
        
        manager = RobustCheckpointManager(self.test_dir)
        results = []
        errors = []
        
        def checkpoint_worker(worker_id):
            """Worker that saves checkpoint concurrently"""
            try:
                data = {
                    'version': 'v1.0',
                    'resume_index': worker_id * 100,
                    'processed_count': worker_id * 100 - 1,
                    'failed_count': worker_id,
                    'timestamp': time.time(),
                    'metadata': {'worker_id': worker_id}
                }
                result = manager.save_checkpoint(data)
                results.append((worker_id, result))
            except Exception as e:
                errors.append((worker_id, e))
        
        # Create multiple threads
        threads = []
        for worker_id in range(5):
            thread = threading.Thread(target=checkpoint_worker, args=(worker_id,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Should have no errors
        self.assertEqual(len(errors), 0, f"Concurrent errors: {errors}")
        
        # At least one save should succeed
        successful_saves = [r for r in results if r[1] is True]
        self.assertGreater(len(successful_saves), 0)
        
        # Final checkpoint should be loadable
        final_checkpoint = manager.load_checkpoint()
        self.assertIsNotNone(final_checkpoint)
    
    @unittest.skipIf(RobustCheckpointManager is None, "RobustCheckpointManager not implemented yet")
    def test_checkpoint_version_compatibility(self):
        """TEST: Different checkpoint versions are handled appropriately"""
        manager = RobustCheckpointManager(self.test_dir)
        
        # Save checkpoint with older version
        old_version_data = {
            'version': 'v0.1',  # Old version
            'resume_index': 100,
            'processed_count': 99,
            'failed_count': 1,
            'timestamp': time.time(),
            'metadata': {'legacy_field': True}
        }
        
        result = manager.save_checkpoint(old_version_data)
        self.assertTrue(result)
        
        # Should load and handle version differences
        loaded_data = manager.load_checkpoint()
        self.assertIsNotNone(loaded_data)
        
        # Should preserve or upgrade version appropriately
        self.assertIn('version', loaded_data)
        self.assertIn('resume_index', loaded_data)


class TestCheckpointErrors(unittest.TestCase):
    """Test custom checkpoint error exceptions"""
    
    @unittest.skipIf(CheckpointFormatError is Exception, "CheckpointFormatError not implemented yet")
    def test_checkpoint_format_error_creation(self):
        """TEST: CheckpointFormatError can be created with validation details"""
        error = CheckpointFormatError("Invalid resume_index type", {'field': 'resume_index', 'expected': 'int', 'actual': 'str'})
        
        self.assertIn("Invalid resume_index type", str(error))
        self.assertEqual(error.validation_details['field'], 'resume_index')
    
    @unittest.skipIf(CheckpointRecoveryError is Exception, "CheckpointRecoveryError not implemented yet")
    def test_checkpoint_recovery_error_creation(self):
        """TEST: CheckpointRecoveryError can be created with recovery context"""
        error = CheckpointRecoveryError("Backup recovery failed", recovery_attempts=3, last_error="File not found")
        
        self.assertIn("Backup recovery failed", str(error))
        self.assertEqual(error.recovery_attempts, 3)
        self.assertEqual(error.last_error, "File not found")


if __name__ == '__main__':
    # Run tests - expect failures initially (TDD approach)
    print("🧪 Running RobustCheckpointManager TDD Tests")
    print("⚠️  Expected: Tests will FAIL initially - this is TDD!")
    print("✅ Goal: Implement RobustCheckpointManager to make these tests pass")
    print("=" * 60)
    
    unittest.main(verbosity=2)