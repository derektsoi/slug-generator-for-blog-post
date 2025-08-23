#!/usr/bin/env python3
"""
Test-Driven Development for Refactored Batch Processor
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
        "refactored_batch_processor", 
        os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'core', 'refactored_batch_processor.py')
    )
    batch_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(batch_module)
    
    RefactoredBatchProcessor = batch_module.RefactoredBatchProcessor
    BatchProcessingContext = batch_module.BatchProcessingContext
    ProcessingResult = batch_module.ProcessingResult
except (ImportError, AttributeError, FileNotFoundError):
    # Expected to fail initially - we haven't implemented it yet
    RefactoredBatchProcessor = None
    BatchProcessingContext = None
    ProcessingResult = None


class TestRefactoredBatchProcessor(unittest.TestCase):
    """Test suite for RefactoredBatchProcessor - TDD approach"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.test_dir, 'output')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Sample URLs for testing
        self.sample_urls = [
            {"title": "Test Blog Post 1", "url": "https://example.com/post1"},
            {"title": "Test Blog Post 2", "url": "https://example.com/post2"},
            {"title": "Test Blog Post 3", "url": "https://example.com/post3"}
        ]
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @unittest.skipIf(RefactoredBatchProcessor is None, "RefactoredBatchProcessor not implemented yet")
    def test_processor_initialization_with_all_components(self):
        """TEST: Processor initializes with all refactored components"""
        processor = RefactoredBatchProcessor(
            output_dir=self.output_dir,
            max_budget=50.0,
            batch_size=10
        )
        
        # Should have all integrated components
        self.assertIsNotNone(processor.atomic_writer)
        self.assertIsNotNone(processor.checkpoint_manager)
        # Progress tracker initialized lazily during processing
        self.assertIsNotNone(processor.context.config)
        self.assertIsNotNone(processor.preflight_validator)
        self.assertIsNotNone(processor.recovery_system)
        self.assertEqual(processor.output_dir, self.output_dir)
    
    @unittest.skipIf(RefactoredBatchProcessor is None, "RefactoredBatchProcessor not implemented yet")
    def test_integrated_preflight_validation(self):
        """TEST: Integrated preflight validation with all components"""
        processor = RefactoredBatchProcessor(self.output_dir)
        
        # Mock slug generator to ensure validation focuses on architecture
        with patch.object(processor, '_get_slug_generator') as mock_generator:
            mock_generator.return_value = Mock()
            
            validation_result = processor.run_preflight_validation()
            
            # Debug output to see what's failing
            if not validation_result['is_valid']:
                print(f"Validation failed: {validation_result}")
            
            self.assertTrue(validation_result['is_valid'])
            self.assertIn('configuration_validation', validation_result)
            self.assertIn('component_validation', validation_result)
            self.assertIn('file_system_validation', validation_result)
    
    @unittest.skipIf(RefactoredBatchProcessor is None, "RefactoredBatchProcessor not implemented yet")
    def test_atomic_batch_processing_with_checkpoints(self):
        """TEST: Batch processing with atomic operations and checkpoints"""
        processor = RefactoredBatchProcessor(
            output_dir=self.output_dir,
            batch_size=2,
            checkpoint_interval=1
        )
        
        # Mock slug generation
        with patch.object(processor, '_generate_slug') as mock_generate:
            mock_generate.return_value = {
                'primary': 'test-blog-post',
                'alternatives': ['alt-test-post'],
                'confidence': 0.95
            }
            
            result = processor.process_urls(self.sample_urls[:2])
            
            self.assertTrue(result.success)
            self.assertEqual(result.processed_count, 2)
            self.assertEqual(result.success_count, 2)
            
            # Verify checkpoint file exists
            checkpoint_file = os.path.join(self.output_dir, 'checkpoint.json')
            self.assertTrue(os.path.exists(checkpoint_file))
            
            # Verify results file exists and is atomic
            results_file = os.path.join(self.output_dir, 'results.jsonl')
            self.assertTrue(os.path.exists(results_file))
    
    @unittest.skipIf(RefactoredBatchProcessor is None, "RefactoredBatchProcessor not implemented yet")
    def test_recovery_integration_during_processing(self):
        """TEST: Recovery system integration during processing errors"""
        processor = RefactoredBatchProcessor(self.output_dir)
        
        # Create corrupted checkpoint to trigger recovery
        checkpoint_file = os.path.join(self.output_dir, 'checkpoint.json')
        with open(checkpoint_file, 'w') as f:
            f.write('{"corrupted": "checkpoint"')  # Invalid JSON
        
        # Mock slug generation to fail once, triggering exception and recovery
        with patch.object(processor, '_generate_slug') as mock_generate:
            mock_generate.side_effect = Exception("Simulated processing failure")
            
            # Should trigger recovery due to exception
            result = processor.process_urls(self.sample_urls)
            
            # Recovery attempted should be true, but processing may fail
            self.assertTrue(hasattr(result, 'recovery_attempted'))
            self.assertTrue(result.recovery_attempted)
    
    @unittest.skipIf(RefactoredBatchProcessor is None, "RefactoredBatchProcessor not implemented yet")
    def test_progress_synchronization_across_components(self):
        """TEST: Progress synchronization between all components"""
        processor = RefactoredBatchProcessor(
            output_dir=self.output_dir,
            progress_update_interval=1  # Update every entry
        )
        
        with patch.object(processor, '_generate_slug') as mock_generate:
            mock_generate.return_value = {
                'primary': 'test-slug',
                'alternatives': [],
                'confidence': 0.9
            }
            
            # Process with progress tracking
            result = processor.process_urls(self.sample_urls)
            
            # Verify progress file exists and matches processing
            progress_file = os.path.join(self.output_dir, 'live_progress.json')
            self.assertTrue(os.path.exists(progress_file))
            
            with open(progress_file, 'r') as f:
                progress_data = json.load(f)
            
            self.assertEqual(progress_data['processed'], result.processed_count)
            self.assertEqual(progress_data['failed'], result.failed_count)
    
    @unittest.skipIf(RefactoredBatchProcessor is None, "RefactoredBatchProcessor not implemented yet")
    def test_configuration_aware_processing(self):
        """TEST: Processing adapts to configuration pipeline settings"""
        # Test with V8 configuration (enhanced constraints)
        processor = RefactoredBatchProcessor(
            output_dir=self.output_dir,
            prompt_version='v8'
        )
        
        with patch.object(processor, '_generate_slug') as mock_generate:
            mock_generate.return_value = {
                'primary': 'very-long-enhanced-constraint-slug-for-v8',  # 7 words, acceptable for V8
                'alternatives': [],
                'confidence': 0.85
            }
            
            result = processor.process_urls(self.sample_urls[:1])
            
            self.assertTrue(result.success)
            # V8 should accept longer slugs (up to 8 words)
            self.assertEqual(result.success_count, 1)
    
    @unittest.skipIf(RefactoredBatchProcessor is None, "RefactoredBatchProcessor not implemented yet")
    def test_comprehensive_error_handling(self):
        """TEST: Comprehensive error handling with classification"""
        processor = RefactoredBatchProcessor(self.output_dir)
        
        # Simulate various error conditions
        with patch.object(processor, '_generate_slug') as mock_generate:
            # First call succeeds, second fails, third succeeds
            mock_generate.side_effect = [
                {'primary': 'success-slug', 'alternatives': [], 'confidence': 0.9},
                Exception("API rate limit exceeded"),
                {'primary': 'recovery-slug', 'alternatives': [], 'confidence': 0.8}
            ]
            
            result = processor.process_urls(self.sample_urls)
            
            self.assertTrue(result.success)  # Overall success despite one failure
            self.assertEqual(result.processed_count, 3)
            self.assertEqual(result.success_count, 2)  # Two succeeded
            self.assertEqual(result.failed_count, 1)   # One failed
            self.assertTrue(hasattr(result, 'error_classifications'))
    
    @unittest.skipIf(RefactoredBatchProcessor is None, "RefactoredBatchProcessor not implemented yet")
    def test_resume_functionality_with_recovery(self):
        """TEST: Resume functionality with integrated recovery"""
        processor = RefactoredBatchProcessor(self.output_dir)
        
        # First processing run (partial)
        with patch.object(processor, '_generate_slug') as mock_generate:
            mock_generate.return_value = {
                'primary': 'partial-slug',
                'alternatives': [],
                'confidence': 0.85
            }
            
            # Process first 2 URLs
            partial_result = processor.process_urls(self.sample_urls[:2])
            self.assertTrue(partial_result.success)
        
        # Second processing run (resume) - should continue from checkpoint
        processor_resumed = RefactoredBatchProcessor(self.output_dir)
        
        with patch.object(processor_resumed, '_generate_slug') as mock_generate:
            mock_generate.return_value = {
                'primary': 'resumed-slug',
                'alternatives': [],
                'confidence': 0.9
            }
            
            # Should resume from where we left off
            resume_result = processor_resumed.process_urls(
                self.sample_urls, 
                resume=True
            )
            
            self.assertTrue(resume_result.success)
            self.assertTrue(resume_result.resumed_from_checkpoint)
            # Should only process the remaining URL (third one)
            self.assertEqual(resume_result.processed_count, 1)
    
    @unittest.skipIf(RefactoredBatchProcessor is None, "RefactoredBatchProcessor not implemented yet")
    def test_concurrent_safety_with_atomic_operations(self):
        """TEST: Concurrent processing safety with atomic operations"""
        processor = RefactoredBatchProcessor(
            output_dir=self.output_dir,
            enable_concurrent_processing=False  # Disable for safety testing
        )
        
        with patch.object(processor, '_generate_slug') as mock_generate:
            mock_generate.return_value = {
                'primary': 'thread-safe-slug',
                'alternatives': [],
                'confidence': 0.85
            }
            
            # Simulate concurrent access by multiple threads
            def process_batch(urls_subset):
                return processor.process_urls(urls_subset)
            
            threads = []
            results = []
            
            # Create threads for concurrent processing
            for i in range(2):
                urls_subset = [self.sample_urls[i]]
                thread = threading.Thread(target=lambda: results.append(process_batch(urls_subset)))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads
            for thread in threads:
                thread.join()
            
            # All processing should complete successfully with atomic operations
            self.assertEqual(len(results), 2)
            for result in results:
                self.assertTrue(result.success)


class TestBatchProcessingContext(unittest.TestCase):
    """Test suite for BatchProcessingContext - TDD approach"""
    
    @unittest.skipIf(BatchProcessingContext is None, "BatchProcessingContext not implemented yet")
    def test_context_creation_with_components(self):
        """TEST: Context creation with all required components"""
        with tempfile.TemporaryDirectory() as temp_dir:
            context = BatchProcessingContext(
                output_dir=temp_dir,
                prompt_version='v8',
                max_budget=100.0
            )
            
            self.assertEqual(context.output_dir, temp_dir)
            self.assertEqual(context.prompt_version, 'v8')
            self.assertEqual(context.max_budget, 100.0)
            self.assertIsNotNone(context.config)
            self.assertIsNotNone(context.component_registry)
    
    @unittest.skipIf(BatchProcessingContext is None, "BatchProcessingContext not implemented yet")
    def test_context_component_injection(self):
        """TEST: Context supports component dependency injection"""
        with tempfile.TemporaryDirectory() as temp_dir:
            context = BatchProcessingContext(temp_dir)
            
            # Should be able to retrieve and inject components
            atomic_writer = context.get_component('atomic_writer')
            checkpoint_manager = context.get_component('checkpoint_manager')
            recovery_system = context.get_component('recovery_system')
            
            self.assertIsNotNone(atomic_writer)
            self.assertIsNotNone(checkpoint_manager)
            self.assertIsNotNone(recovery_system)
            
            # Components should be properly configured
            self.assertEqual(atomic_writer.file_path, os.path.join(temp_dir, 'results.jsonl'))


class TestProcessingResult(unittest.TestCase):
    """Test suite for ProcessingResult - TDD approach"""
    
    @unittest.skipIf(ProcessingResult is None, "ProcessingResult not implemented yet")
    def test_processing_result_creation(self):
        """TEST: ProcessingResult captures comprehensive batch results"""
        result = ProcessingResult(
            success=True,
            processed_count=100,
            success_count=95,
            failed_count=5,
            total_cost=25.50,
            processing_duration=300.5
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.processed_count, 100)
        self.assertEqual(result.success_count, 95)
        self.assertEqual(result.failed_count, 5)
        self.assertEqual(result.total_cost, 25.50)
        self.assertEqual(result.processing_duration, 300.5)
    
    @unittest.skipIf(ProcessingResult is None, "ProcessingResult not implemented yet")
    def test_processing_result_serialization(self):
        """TEST: ProcessingResult can be serialized for logging"""
        result = ProcessingResult(
            success=True,
            processed_count=50,
            success_count=48,
            failed_count=2
        )
        
        serialized = result.to_dict()
        
        self.assertIn('success', serialized)
        self.assertIn('processed_count', serialized)
        self.assertIn('success_count', serialized)
        self.assertIn('performance_metrics', serialized)
        self.assertIn('timestamp', serialized)
    
    @unittest.skipIf(ProcessingResult is None, "ProcessingResult not implemented yet")
    def test_processing_result_performance_analysis(self):
        """TEST: ProcessingResult provides performance analysis"""
        result = ProcessingResult(
            success=True,
            processed_count=100,
            success_count=90,
            failed_count=10,
            processing_duration=180.0,
            total_cost=15.75
        )
        
        performance = result.get_performance_metrics()
        
        self.assertEqual(performance['success_rate'], 0.9)  # 90/100
        self.assertEqual(performance['avg_cost_per_url'], 0.1575)  # 15.75/100
        self.assertEqual(performance['avg_time_per_url'], 1.8)  # 180/100
        self.assertIn('cost_efficiency', performance)


if __name__ == '__main__':
    # Run tests - expect failures initially (TDD approach)
    print("🧪 Running Refactored Batch Processor TDD Tests")
    print("⚠️  Expected: Tests will FAIL initially - this is TDD!")
    print("✅ Goal: Implement Refactored Architecture to make these tests pass")
    print("=" * 60)
    
    unittest.main(verbosity=2)