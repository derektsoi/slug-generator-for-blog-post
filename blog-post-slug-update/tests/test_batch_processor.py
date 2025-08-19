import unittest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import json
import tempfile
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# These imports will fail initially - that's expected!
try:
    from batch_processor import BatchProcessor
    from output_manager import OutputManager
    from region_manager import RegionManager
except ImportError:
    BatchProcessor = None
    OutputManager = None
    RegionManager = None


class TestBatchProcessor(unittest.TestCase):
    """Test cases for batch processing functionality - THESE WILL FAIL INITIALLY"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = BatchProcessor() if BatchProcessor else None
        
        # Sample dataset entries
        self.sample_entries = [
            {
                "title": "8大日牌輕珠寶品牌一次睇！Agete、nojess及Star Jewelry等日劇女主御用明星珠寶",
                "url": "https://www.buyandship.today/blog/2025/08/18/%e6%97%a5%e6%9c%ac%e8%bc%95%e7%8f%a0%e5%af%b6%e5%93%81%e7%89%8c%e5%90%88%e9%9b%86/"
            },
            {
                "title": "英國必買童裝 JoJo Maman Bébé官網 3 折起入手網購教學",
                "url": "https://www.buyandship.today/blog/2025/08/18/jojo-maman-bebe%e8%8b%b1%e5%9c%8b%e5%ae%98%e7%b6%b2%e6%8a%98%e6%89%a3%e5%8f%8a%e8%b3%bc%e8%b2%b7%e6%95%99%e5%ad%b8/"
            },
            {
                "title": "Kindle電子書閱讀器最強攻略：Paper White、Colorsoft等型號分別、價格比較及網購集運教學",
                "url": "https://www.buyandship.today/blog/2025/08/13/kindle%e7%b6%b2%e8%b3%bc%e6%94%bb%e7%95%a5/"
            }
        ]
        
        self.test_regions = ["Hong Kong", "Singapore", "Australia"]
    
    @unittest.skipIf(BatchProcessor is None, "BatchProcessor not implemented yet")
    def test_single_region_batch_processing(self):
        """Test processing batch for single region - WILL FAIL"""
        region = "Hong Kong"
        
        results = self.processor.process_region_batch(self.sample_entries, region)
        
        # Should return same number of results as input entries
        self.assertEqual(len(results), len(self.sample_entries))
        
        # Each result should have required fields
        required_fields = ['original_title', 'original_url', 'region', 'slug', 'title', 'meta_description']
        
        for result in results:
            for field in required_fields:
                self.assertIn(field, result, f"Missing field: {field}")
            
            # Region should be correctly set
            self.assertEqual(result['region'], region)
            
            # Original data should be preserved
            self.assertIn(result['original_title'], [e['title'] for e in self.sample_entries])
            self.assertIn(result['original_url'], [e['url'] for e in self.sample_entries])
    
    @unittest.skipIf(BatchProcessor is None, "BatchProcessor not implemented yet")
    def test_multi_region_processing(self):
        """Test processing same entries for multiple regions - WILL FAIL"""
        results = self.processor.process_multi_region(self.sample_entries, self.test_regions)
        
        # Should have results for all regions
        expected_total = len(self.sample_entries) * len(self.test_regions)
        self.assertEqual(len(results), expected_total)
        
        # Group results by region
        results_by_region = {}
        for result in results:
            region = result['region']
            if region not in results_by_region:
                results_by_region[region] = []
            results_by_region[region].append(result)
        
        # Each region should have same number of entries
        for region in self.test_regions:
            self.assertIn(region, results_by_region)
            self.assertEqual(len(results_by_region[region]), len(self.sample_entries))
        
        # Slugs should be different across regions for same entry
        first_entry_title = self.sample_entries[0]['title']
        slugs_for_first_entry = []
        
        for result in results:
            if result['original_title'] == first_entry_title:
                slugs_for_first_entry.append(result['slug'])
        
        # All slugs should be unique (different regions = different slugs)
        self.assertEqual(len(slugs_for_first_entry), len(set(slugs_for_first_entry)))
    
    @unittest.skipIf(BatchProcessor is None, "BatchProcessor not implemented yet")
    def test_batch_processing_with_failures(self):
        """Test batch processing handles individual failures gracefully - WILL FAIL"""
        # Mock some entries to fail during processing
        with patch.object(self.processor, 'process_single_entry') as mock_process:
            # First entry succeeds, second fails, third succeeds
            mock_process.side_effect = [
                {'slug': 'success-1', 'title': 'Success 1', 'meta_description': 'Meta 1'},
                Exception("API Error"),
                {'slug': 'success-3', 'title': 'Success 3', 'meta_description': 'Meta 3'}
            ]
            
            results, failed_entries = self.processor.process_with_failure_handling(
                self.sample_entries, "Hong Kong"
            )
            
            # Should have 2 successful results
            self.assertEqual(len(results), 2)
            
            # Should have 1 failed entry
            self.assertEqual(len(failed_entries), 1)
            
            # Failed entry should contain error information
            failed_entry = failed_entries[0]
            self.assertIn('entry', failed_entry)
            self.assertIn('error', failed_entry)
            self.assertIn('timestamp', failed_entry)
    
    @unittest.skipIf(BatchProcessor is None, "BatchProcessor not implemented yet")
    def test_batch_size_optimization(self):
        """Test batch processing uses optimal batch sizes - WILL FAIL"""
        # Create larger dataset
        large_dataset = self.sample_entries * 20  # 60 entries
        
        with patch.object(self.processor, 'process_llm_batch') as mock_llm_batch:
            mock_llm_batch.return_value = [{'slug': 'test', 'title': 'Test', 'meta_description': 'Test'}] * 8
            
            results = self.processor.process_region_batch(large_dataset, "Singapore")
            
            # Should have made multiple batch calls
            self.assertGreater(mock_llm_batch.call_count, 1)
            
            # Each batch should be reasonable size (not too big for LLM)
            for call in mock_llm_batch.call_args_list:
                batch_entries = call[0][0]  # First argument is batch entries
                self.assertLessEqual(len(batch_entries), 10, "Batch size too large for LLM")
                self.assertGreater(len(batch_entries), 0, "Empty batch")
    
    @unittest.skipIf(BatchProcessor is None, "BatchProcessor not implemented yet")
    async def test_async_processing_performance(self):
        """Test async processing is faster than sequential - WILL FAIL"""
        import time
        
        # Mock async processing
        async def mock_async_process(entry, region):
            await asyncio.sleep(0.1)  # Simulate API call
            return {
                'slug': 'test-slug',
                'title': 'Test Title', 
                'meta_description': 'Test meta'
            }
        
        with patch.object(self.processor, 'process_single_entry_async', side_effect=mock_async_process):
            start_time = time.time()
            
            results = await self.processor.process_region_batch_async(self.sample_entries, "Malaysia")
            
            processing_time = time.time() - start_time
            
            # Async processing should be faster than sequential
            # 3 entries × 0.1s each = 0.3s sequential, but async should be ~0.1s
            self.assertLess(processing_time, 0.25, "Async processing not fast enough")
            self.assertEqual(len(results), len(self.sample_entries))


class TestOutputManager(unittest.TestCase):
    """Test cases for output file management - THESE WILL FAIL INITIALLY"""
    
    def setUp(self):
        """Set up test fixtures with temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.output_manager = OutputManager(self.temp_dir) if OutputManager else None
        
        # Sample results
        self.sample_results = [
            {
                'original_title': 'Test Title 1',
                'original_url': 'https://example.com/1',
                'region': 'Hong Kong',
                'slug': 'test-slug-1-hong-kong',
                'title': 'Test Title 1 | Hong Kong',
                'meta_description': 'Test meta description for Hong Kong'
            },
            {
                'original_title': 'Test Title 2', 
                'original_url': 'https://example.com/2',
                'region': 'Hong Kong',
                'slug': 'test-slug-2-hong-kong',
                'title': 'Test Title 2 | Hong Kong',
                'meta_description': 'Another test meta description for Hong Kong'
            }
        ]
    
    def tearDown(self):
        """Clean up temporary directory"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @unittest.skipIf(OutputManager is None, "OutputManager not implemented yet")
    def test_save_region_results(self):
        """Test saving results for single region - WILL FAIL"""
        region = "Hong Kong"
        timestamp = "20250819_143022"
        
        filepath = self.output_manager.save_region_results(
            self.sample_results, region, timestamp
        )
        
        # File should be created
        self.assertTrue(os.path.exists(filepath))
        
        # File should have correct naming
        expected_filename = "seo_mapping_hong_kong_20250819_143022.json"
        self.assertTrue(filepath.endswith(expected_filename))
        
        # File should contain valid JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check structure
        self.assertIn('region', data)
        self.assertIn('generated_at', data)  
        self.assertIn('total_entries', data)
        self.assertIn('entries', data)
        
        # Check content
        self.assertEqual(data['region'], region)
        self.assertEqual(data['total_entries'], len(self.sample_results))
        self.assertEqual(len(data['entries']), len(self.sample_results))
    
    @unittest.skipIf(OutputManager is None, "OutputManager not implemented yet")
    def test_save_all_regions(self):
        """Test saving results for multiple regions - WILL FAIL"""
        region_results = {
            "Hong Kong": self.sample_results,
            "Singapore": self.sample_results,  # Reuse for test
            "Australia": self.sample_results   # Reuse for test
        }
        timestamp = "20250819_143022"
        
        saved_files = self.output_manager.save_all_regions(region_results, timestamp)
        
        # Should have saved files for all regions
        self.assertEqual(len(saved_files), 3)
        
        # All files should exist
        for region, filepath in saved_files.items():
            self.assertTrue(os.path.exists(filepath))
            
            # Load and verify content
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.assertEqual(data['region'], region)
            self.assertEqual(len(data['entries']), len(self.sample_results))


class TestRegionManager(unittest.TestCase):
    """Test cases for region management - THESE WILL FAIL INITIALLY"""
    
    @unittest.skipIf(RegionManager is None, "RegionManager not implemented yet")
    def test_default_regions_loaded(self):
        """Test default regions are loaded correctly - WILL FAIL"""
        manager = RegionManager()
        
        expected_regions = ["Hong Kong", "Singapore", "Australia", "Malaysia", "Taiwan"]
        
        for region in expected_regions:
            self.assertIn(region, manager.regions)
    
    @unittest.skipIf(RegionManager is None, "RegionManager not implemented yet")
    def test_region_slug_suffix_conversion(self):
        """Test region names convert to proper URL suffixes - WILL FAIL"""
        manager = RegionManager()
        
        test_cases = [
            ("Hong Kong", "hong-kong"),
            ("Singapore", "singapore"),
            ("Australia", "australia"),
            ("Malaysia", "malaysia"),
            ("Taiwan", "taiwan")
        ]
        
        for region_name, expected_suffix in test_cases:
            result = manager.get_region_slug_suffix(region_name)
            self.assertEqual(result, expected_suffix)
    
    @unittest.skipIf(RegionManager is None, "RegionManager not implemented yet")
    def test_dynamic_region_addition(self):
        """Test adding new regions dynamically - WILL FAIL"""
        manager = RegionManager()
        initial_count = len(manager.regions)
        
        new_region = "Philippines"
        manager.add_region(new_region)
        
        self.assertIn(new_region, manager.regions)
        self.assertEqual(len(manager.regions), initial_count + 1)
        
        # Should generate proper suffix for new region
        suffix = manager.get_region_slug_suffix(new_region)
        self.assertEqual(suffix, "philippines")


if __name__ == '__main__':
    unittest.main()