#!/usr/bin/env python3
"""
Test-Driven Development for SynchronizedProgressTracker
Tests written FIRST to define expected behavior before implementation.
"""

import unittest
import tempfile
import os
import json
import time
import threading
from unittest.mock import patch, Mock

# Import will fail initially - this is expected in TDD
try:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
    # Import directly from the module to avoid __init__.py dependencies
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "synchronized_progress", 
        os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'core', 'synchronized_progress.py')
    )
    progress_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(progress_module)
    
    SynchronizedProgressTracker = progress_module.SynchronizedProgressTracker
    ProgressSyncError = progress_module.ProgressSyncError
except (ImportError, AttributeError, FileNotFoundError):
    # Expected to fail initially - we haven't implemented it yet
    SynchronizedProgressTracker = None
    ProgressSyncError = Exception


class TestSynchronizedProgressTracker(unittest.TestCase):
    """Test suite for SynchronizedProgressTracker - TDD approach"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.total_count = 1000
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @unittest.skipIf(SynchronizedProgressTracker is None, "SynchronizedProgressTracker not implemented yet")
    def test_progress_initialization(self):
        """TEST: Progress tracker initializes with correct state"""
        tracker = SynchronizedProgressTracker(self.total_count, self.test_dir)
        
        # Initial state should be zero
        self.assertEqual(tracker.total_count, self.total_count)
        self.assertEqual(tracker._memory_state['processed'], 0)
        self.assertEqual(tracker._memory_state['failed'], 0)
        self.assertEqual(tracker._memory_state['current_index'], 0)
        
        # Live progress file should be created
        live_progress_file = os.path.join(self.test_dir, 'live_progress.json')
        self.assertTrue(os.path.exists(live_progress_file))
    
    @unittest.skipIf(SynchronizedProgressTracker is None, "SynchronizedProgressTracker not implemented yet")
    def test_successful_progress_update(self):
        """TEST: Successful progress updates are tracked and persisted correctly"""
        tracker = SynchronizedProgressTracker(self.total_count, self.test_dir)
        
        # Update progress with success
        result = tracker.update_progress(success=True, current_index=50)
        
        # Memory state should be updated
        self.assertEqual(result['processed'], 1)
        self.assertEqual(result['failed'], 0)
        self.assertEqual(result['current_index'], 50)
        
        # File should be immediately updated
        live_progress_file = os.path.join(self.test_dir, 'live_progress.json')
        with open(live_progress_file, 'r') as f:
            file_data = json.load(f)
        
        self.assertEqual(file_data['processed'], 1)
        self.assertEqual(file_data['failed'], 0)
        self.assertEqual(file_data['current_index'], 50)
        self.assertIn('percent', file_data)
        self.assertIn('timestamp', file_data)
    
    @unittest.skipIf(SynchronizedProgressTracker is None, "SynchronizedProgressTracker not implemented yet")
    def test_failed_progress_update(self):
        """TEST: Failed progress updates are tracked correctly"""
        tracker = SynchronizedProgressTracker(self.total_count, self.test_dir)
        
        # Update progress with failure
        result = tracker.update_progress(success=False, current_index=25)
        
        # Should increment both processed and failed
        self.assertEqual(result['processed'], 1)
        self.assertEqual(result['failed'], 1)
        self.assertEqual(result['current_index'], 25)
        
        # File should reflect failure
        live_progress_file = os.path.join(self.test_dir, 'live_progress.json')
        with open(live_progress_file, 'r') as f:
            file_data = json.load(f)
        
        self.assertEqual(file_data['processed'], 1)
        self.assertEqual(file_data['failed'], 1)
    
    @unittest.skipIf(SynchronizedProgressTracker is None, "SynchronizedProgressTracker not implemented yet")
    def test_multiple_progress_updates(self):
        """TEST: Multiple progress updates accumulate correctly"""
        tracker = SynchronizedProgressTracker(self.total_count, self.test_dir)
        
        # Simulate multiple updates
        updates = [
            (True, 10),
            (True, 20),
            (False, 30),
            (True, 40),
            (False, 50)
        ]
        
        expected_processed = 0
        expected_failed = 0
        
        for i, (success, index) in enumerate(updates):
            result = tracker.update_progress(success, index)
            expected_processed += 1
            if not success:
                expected_failed += 1
            
            self.assertEqual(result['processed'], expected_processed)
            self.assertEqual(result['failed'], expected_failed)
            self.assertEqual(result['current_index'], index)
        
        # Final state verification
        self.assertEqual(result['processed'], 5)
        self.assertEqual(result['failed'], 2)
        self.assertEqual(result['current_index'], 50)
    
    @unittest.skipIf(SynchronizedProgressTracker is None, "SynchronizedProgressTracker not implemented yet")
    def test_percentage_calculation(self):
        """TEST: Percentage calculation is accurate"""
        tracker = SynchronizedProgressTracker(100, self.test_dir)  # Use 100 for easy percentage calculation
        
        # 25 successful updates
        for i in range(25):
            result = tracker.update_progress(True, i)
        
        # Should be 25%
        self.assertEqual(result['percent'], 25.0)
        
        # Verify in file as well
        live_progress_file = os.path.join(self.test_dir, 'live_progress.json')
        with open(live_progress_file, 'r') as f:
            file_data = json.load(f)
        
        self.assertEqual(file_data['percent'], 25.0)
    
    @unittest.skipIf(SynchronizedProgressTracker is None, "SynchronizedProgressTracker not implemented yet")
    def test_thread_safety_concurrent_updates(self):
        """TEST: Concurrent progress updates from multiple threads are handled safely"""
        tracker = SynchronizedProgressTracker(self.total_count, self.test_dir)
        
        results = []
        errors = []
        
        def progress_worker(worker_id, update_count):
            """Worker that makes progress updates concurrently"""
            try:
                for i in range(update_count):
                    success = (i % 3 != 0)  # 2/3 success rate
                    index = worker_id * 100 + i
                    result = tracker.update_progress(success, index)
                    results.append((worker_id, i, result['processed'], result['failed']))
            except Exception as e:
                errors.append((worker_id, e))
        
        # Create multiple threads
        threads = []
        workers = 5
        updates_per_worker = 10
        
        for worker_id in range(workers):
            thread = threading.Thread(target=progress_worker, args=(worker_id, updates_per_worker))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Should have no errors
        self.assertEqual(len(errors), 0, f"Concurrent update errors: {errors}")
        
        # Should have results from all workers
        self.assertEqual(len(results), workers * updates_per_worker)
        
        # Final state should be consistent
        final_state = tracker._memory_state
        self.assertEqual(final_state['processed'], workers * updates_per_worker)
        
        # File should match memory state
        live_progress_file = os.path.join(self.test_dir, 'live_progress.json')
        with open(live_progress_file, 'r') as f:
            file_data = json.load(f)
        
        self.assertEqual(file_data['processed'], final_state['processed'])
        self.assertEqual(file_data['failed'], final_state['failed'])
    
    @unittest.skipIf(SynchronizedProgressTracker is None, "SynchronizedProgressTracker not implemented yet")
    def test_file_persistence_immediate_sync(self):
        """TEST: File is updated immediately after each progress update"""
        tracker = SynchronizedProgressTracker(self.total_count, self.test_dir)
        
        live_progress_file = os.path.join(self.test_dir, 'live_progress.json')
        
        # Make several updates and check file after each
        for i in range(5):
            tracker.update_progress(True, i * 10)
            
            # File should be updated immediately
            self.assertTrue(os.path.exists(live_progress_file))
            
            with open(live_progress_file, 'r') as f:
                file_data = json.load(f)
            
            # File should match current state
            self.assertEqual(file_data['processed'], i + 1)
            self.assertEqual(file_data['current_index'], i * 10)
            
            # Timestamp should be recent
            self.assertGreater(file_data['timestamp'], time.time() - 5)
    
    @unittest.skipIf(SynchronizedProgressTracker is None, "SynchronizedProgressTracker not implemented yet")
    def test_progress_state_recovery(self):
        """TEST: Progress state can be recovered from file after restart"""
        # Create initial tracker and make some progress
        tracker1 = SynchronizedProgressTracker(self.total_count, self.test_dir)
        
        for i in range(10):
            tracker1.update_progress(i % 2 == 0, i * 5)  # 5 success, 5 failed
        
        # Create new tracker (simulating restart)
        tracker2 = SynchronizedProgressTracker(self.total_count, self.test_dir)
        
        # Should be able to recover state from file
        if hasattr(tracker2, 'recover_from_file'):
            recovered_state = tracker2.recover_from_file()
            
            self.assertEqual(recovered_state['processed'], 10)
            self.assertEqual(recovered_state['failed'], 5)
        
        # At minimum, file should still be readable
        live_progress_file = os.path.join(self.test_dir, 'live_progress.json')
        with open(live_progress_file, 'r') as f:
            file_data = json.load(f)
        
        self.assertEqual(file_data['processed'], 10)
        self.assertEqual(file_data['failed'], 5)
    
    @unittest.skipIf(SynchronizedProgressTracker is None, "SynchronizedProgressTracker not implemented yet")
    def test_file_write_failure_handling(self):
        """TEST: File write failures are handled gracefully without crashing"""
        tracker = SynchronizedProgressTracker(self.total_count, self.test_dir)
        
        # Simulate file write failure
        with patch('builtins.open', side_effect=OSError("Simulated write failure")):
            # Should not raise exception, should handle gracefully
            try:
                result = tracker.update_progress(True, 100)
                # Memory state should still be updated even if file write fails
                self.assertEqual(result['processed'], 1)
                self.assertEqual(result['current_index'], 100)
            except ProgressSyncError:
                # Acceptable to raise specific error, but should not crash
                pass
            except Exception as e:
                self.fail(f"Unexpected exception on file write failure: {e}")
    
    @unittest.skipIf(SynchronizedProgressTracker is None, "SynchronizedProgressTracker not implemented yet")
    def test_progress_data_completeness(self):
        """TEST: Progress data includes all expected fields"""
        tracker = SynchronizedProgressTracker(self.total_count, self.test_dir)
        
        result = tracker.update_progress(True, 500)
        
        # Required fields in memory state
        required_fields = ['processed', 'failed', 'current_index']
        for field in required_fields:
            self.assertIn(field, result)
        
        # File should have additional computed fields
        live_progress_file = os.path.join(self.test_dir, 'live_progress.json')
        with open(live_progress_file, 'r') as f:
            file_data = json.load(f)
        
        extended_fields = ['processed', 'failed', 'current_index', 'percent', 'timestamp']
        for field in extended_fields:
            self.assertIn(field, file_data)
        
        # Verify data types
        self.assertIsInstance(file_data['processed'], int)
        self.assertIsInstance(file_data['failed'], int)
        self.assertIsInstance(file_data['current_index'], int)
        self.assertIsInstance(file_data['percent'], (int, float))
        self.assertIsInstance(file_data['timestamp'], (int, float))
    
    @unittest.skipIf(SynchronizedProgressTracker is None, "SynchronizedProgressTracker not implemented yet")
    def test_zero_total_count_handling(self):
        """TEST: Zero total count is handled without division by zero errors"""
        tracker = SynchronizedProgressTracker(0, self.test_dir)
        
        # Should not crash on zero division
        result = tracker.update_progress(True, 0)
        
        # Percentage should be handled gracefully (could be 0 or 100, depending on implementation)
        live_progress_file = os.path.join(self.test_dir, 'live_progress.json')
        with open(live_progress_file, 'r') as f:
            file_data = json.load(f)
        
        # Should not crash and should have valid percentage
        self.assertIsInstance(file_data['percent'], (int, float))
        self.assertGreaterEqual(file_data['percent'], 0)
        self.assertLessEqual(file_data['percent'], 100)


class TestProgressSyncError(unittest.TestCase):
    """Test custom progress synchronization error exception"""
    
    @unittest.skipIf(ProgressSyncError is Exception, "ProgressSyncError not implemented yet")
    def test_progress_sync_error_creation(self):
        """TEST: ProgressSyncError can be created with sync details"""
        memory_state = {'processed': 10, 'failed': 2}
        file_state = {'processed': 8, 'failed': 1}
        
        error = ProgressSyncError("Memory and file state out of sync", memory_state, file_state)
        
        self.assertIn("out of sync", str(error))
        self.assertEqual(error.memory_state, memory_state)
        self.assertEqual(error.file_state, file_state)


if __name__ == '__main__':
    # Run tests - expect failures initially (TDD approach)
    print("🧪 Running SynchronizedProgressTracker TDD Tests")
    print("⚠️  Expected: Tests will FAIL initially - this is TDD!")
    print("✅ Goal: Implement SynchronizedProgressTracker to make these tests pass")
    print("=" * 60)
    
    unittest.main(verbosity=2)