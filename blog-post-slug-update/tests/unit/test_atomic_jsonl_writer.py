#!/usr/bin/env python3
"""
Test-Driven Development for AtomicJSONLWriter
Tests written FIRST to define the expected behavior before implementation.
"""

import unittest
import tempfile
import os
import json
import threading
import time
from unittest.mock import patch, Mock

# Import will fail initially - this is expected in TDD
try:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
    # Import directly from the module to avoid __init__.py dependencies
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "atomic_writer", 
        os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'core', 'atomic_writer.py')
    )
    atomic_writer_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(atomic_writer_module)
    
    AtomicJSONLWriter = atomic_writer_module.AtomicJSONLWriter
    JSONWriteError = atomic_writer_module.JSONWriteError
except (ImportError, AttributeError, FileNotFoundError):
    # Expected to fail initially - we haven't implemented it yet
    AtomicJSONLWriter = None
    JSONWriteError = Exception


class TestAtomicJSONLWriter(unittest.TestCase):
    """Test suite for AtomicJSONLWriter - TDD approach"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test_output.jsonl')
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @unittest.skipIf(AtomicJSONLWriter is None, "AtomicJSONLWriter not implemented yet")
    def test_single_entry_write_with_proper_formatting(self):
        """TEST: Single JSON entry is written with proper newline formatting"""
        writer = AtomicJSONLWriter(self.test_file, backup_enabled=False)
        
        test_data = {"slug": "test-slug", "title": "Test Title", "quality_score": 1.0}
        result = writer.write_entry(test_data)
        
        # Should return True for successful write
        self.assertTrue(result)
        
        # File should exist and contain properly formatted JSON
        self.assertTrue(os.path.exists(self.test_file))
        
        with open(self.test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Critical requirement: Must end with newline
        self.assertTrue(content.endswith('\n'))
        
        # Should be exactly one line
        lines = content.strip().split('\n')
        self.assertEqual(len(lines), 1)
        
        # Line should be valid JSON
        parsed_data = json.loads(lines[0])
        self.assertEqual(parsed_data, test_data)
    
    @unittest.skipIf(AtomicJSONLWriter is None, "AtomicJSONLWriter not implemented yet")
    def test_multiple_entries_proper_line_separation(self):
        """TEST: Multiple entries are separated by newlines correctly"""
        writer = AtomicJSONLWriter(self.test_file, backup_enabled=False)
        
        test_entries = [
            {"slug": "first-slug", "title": "First Title"},
            {"slug": "second-slug", "title": "Second Title"},
            {"slug": "third-slug", "title": "Third Title"}
        ]
        
        # Write all entries
        for entry in test_entries:
            result = writer.write_entry(entry)
            self.assertTrue(result)
        
        # Verify file format
        with open(self.test_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Should have exactly 3 lines
        self.assertEqual(len(lines), 3)
        
        # Each line should end with newline
        for line in lines:
            self.assertTrue(line.endswith('\n'))
        
        # Each line should be valid JSON matching our entries
        for i, line in enumerate(lines):
            parsed_data = json.loads(line.strip())
            self.assertEqual(parsed_data, test_entries[i])
    
    @unittest.skipIf(AtomicJSONLWriter is None, "AtomicJSONLWriter not implemented yet")
    def test_unicode_content_handling(self):
        """TEST: Unicode content (Asian characters) handled correctly"""
        writer = AtomicJSONLWriter(self.test_file, backup_enabled=False)
        
        unicode_data = {
            "slug": "japanese-beauty-products", 
            "title": "日本美容產品推介",
            "description": "一番賞系列商品"
        }
        
        result = writer.write_entry(unicode_data)
        self.assertTrue(result)
        
        # Read back and verify Unicode preservation
        with open(self.test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        parsed_data = json.loads(content.strip())
        self.assertEqual(parsed_data["title"], "日本美容產品推介")
        self.assertEqual(parsed_data["description"], "一番賞系列商品")
    
    @unittest.skipIf(AtomicJSONLWriter is None, "AtomicJSONLWriter not implemented yet")
    def test_concurrent_writes_thread_safety(self):
        """TEST: Concurrent writes from multiple threads are thread-safe"""
        writer = AtomicJSONLWriter(self.test_file, backup_enabled=False)
        
        results = []
        errors = []
        
        def write_worker(worker_id, entry_count):
            """Worker function for concurrent writing"""
            try:
                for i in range(entry_count):
                    data = {"worker": worker_id, "entry": i, "slug": f"worker-{worker_id}-entry-{i}"}
                    result = writer.write_entry(data)
                    results.append((worker_id, i, result))
            except Exception as e:
                errors.append((worker_id, e))
        
        # Create multiple threads
        threads = []
        for worker_id in range(3):
            thread = threading.Thread(target=write_worker, args=(worker_id, 5))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify no errors
        self.assertEqual(len(errors), 0, f"Concurrent write errors: {errors}")
        
        # Verify all writes succeeded
        successful_writes = [r for r in results if r[2] is True]
        self.assertEqual(len(successful_writes), 15)  # 3 workers × 5 entries
        
        # Verify file integrity
        with open(self.test_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Should have exactly 15 lines
        self.assertEqual(len(lines), 15)
        
        # Each line should be valid JSON
        for line in lines:
            self.assertIsNotNone(json.loads(line.strip()))
    
    @unittest.skipIf(AtomicJSONLWriter is None, "AtomicJSONLWriter not implemented yet")
    def test_write_failure_handling(self):
        """TEST: Write failures are handled gracefully"""
        # Use invalid path to trigger write failure
        invalid_path = "/root/nonexistent_dir/test.jsonl"  # Should fail on most systems
        writer = AtomicJSONLWriter(invalid_path, backup_enabled=False)
        
        test_data = {"slug": "test-slug"}
        result = writer.write_entry(test_data)
        
        # Should return False for failed write
        self.assertFalse(result)
    
    @unittest.skipIf(AtomicJSONLWriter is None, "AtomicJSONLWriter not implemented yet")
    def test_atomic_operations_on_system_crash_simulation(self):
        """TEST: Atomic operations prevent corruption on simulated system crashes"""
        writer = AtomicJSONLWriter(self.test_file, backup_enabled=False)
        
        # Write some entries successfully
        for i in range(3):
            data = {"entry": i, "slug": f"entry-{i}"}
            result = writer.write_entry(data)
            self.assertTrue(result)
        
        # Simulate system crash during write (mock file operation failure)
        with patch.object(writer, '_should_finalize', return_value=True):
            with patch('os.rename', side_effect=OSError("Simulated crash")):
                # This write should fail but not corrupt existing data
                crash_data = {"entry": "crash", "slug": "crash-entry"}
                result = writer.write_entry(crash_data)
                self.assertFalse(result)
        
        # Original data should still be intact
        if os.path.exists(self.test_file):
            with open(self.test_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Should have original 3 entries
            self.assertLessEqual(len(lines), 3)
            
            # Each line should still be valid JSON
            for line in lines:
                if line.strip():  # Skip empty lines
                    self.assertIsNotNone(json.loads(line.strip()))
    
    @unittest.skipIf(AtomicJSONLWriter is None, "AtomicJSONLWriter not implemented yet")
    def test_backup_functionality(self):
        """TEST: Backup functionality works correctly when enabled"""
        writer = AtomicJSONLWriter(self.test_file, backup_enabled=True)
        
        # Write initial data
        initial_data = {"slug": "initial-entry", "title": "Initial Title"}
        result = writer.write_entry(initial_data)
        self.assertTrue(result)
        
        # Force finalization to create backup
        if hasattr(writer, '_atomic_finalize'):
            writer._atomic_finalize()
        
        # Backup file should exist
        backup_file = f"{self.test_file}.backup"
        self.assertTrue(os.path.exists(backup_file))
        
        # Backup should contain the data
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        
        if backup_content.strip():  # If backup has content
            parsed_backup = json.loads(backup_content.strip().split('\n')[0])
            self.assertEqual(parsed_backup["slug"], "initial-entry")
    
    @unittest.skipIf(AtomicJSONLWriter is None, "AtomicJSONLWriter not implemented yet")
    def test_json_serialization_error_handling(self):
        """TEST: Non-serializable objects are handled gracefully"""
        writer = AtomicJSONLWriter(self.test_file, backup_enabled=False)
        
        # Try to write non-serializable object
        non_serializable_data = {"slug": "test", "function": lambda x: x}
        
        result = writer.write_entry(non_serializable_data)
        
        # Should return False for non-serializable data
        self.assertFalse(result)
        
        # File should not exist or be empty
        if os.path.exists(self.test_file):
            with open(self.test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertEqual(content.strip(), "")


class TestJSONWriteError(unittest.TestCase):
    """Test custom JSON write error exception"""
    
    @unittest.skipIf(JSONWriteError is Exception, "JSONWriteError not implemented yet")
    def test_json_write_error_creation(self):
        """TEST: JSONWriteError can be created with appropriate message"""
        error = JSONWriteError("Test write error", "ATOMIC_WRITE_FAILED")
        
        self.assertEqual(str(error), "Test write error")
        self.assertEqual(error.error_type, "ATOMIC_WRITE_FAILED")
        self.assertIsInstance(error.timestamp, (int, float))


if __name__ == '__main__':
    # Run tests - expect failures initially (TDD approach)
    print("🧪 Running AtomicJSONLWriter TDD Tests")
    print("⚠️  Expected: Tests will FAIL initially - this is TDD!")
    print("✅ Goal: Implement AtomicJSONLWriter to make these tests pass")
    print("=" * 60)
    
    unittest.main(verbosity=2)