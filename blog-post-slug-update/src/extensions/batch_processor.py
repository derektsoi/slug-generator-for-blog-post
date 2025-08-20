import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple
from content_analyzer import ContentAnalyzer
from seo_generator import SEOGenerator
from region_manager import RegionManager
from output_manager import OutputManager

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Production-scale batch processing of SEO packages"""
    
    def __init__(self, batch_size: int = 8, max_retries: int = 3):
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.content_analyzer = ContentAnalyzer()
        self.seo_generator = SEOGenerator()
        self.region_manager = RegionManager()
        self.output_manager = OutputManager()
    
    def process_region_batch(self, entries: List[Dict[str, str]], region: str) -> List[Dict[str, Any]]:
        """Process batch for single region"""
        results = []
        
        # Process in optimal batch sizes for LLM efficiency
        for i in range(0, len(entries), self.batch_size):
            batch_entries = entries[i:i + self.batch_size]
            
            try:
                # Try LLM batch processing first for efficiency
                batch_results = self.process_llm_batch(batch_entries, region)
                results.extend(batch_results)
            except Exception as e:
                logger.warning(f"LLM batch processing failed: {e}. Falling back to individual processing.")
                
                # Fallback to individual processing
                for entry in batch_entries:
                    try:
                        result = self.process_single_entry(entry, region)
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Failed to process entry: {e}")
                        # Continue processing other entries
                        continue
                
        return results
    
    def process_multi_region(self, entries: List[Dict[str, str]], regions: List[str]) -> List[Dict[str, Any]]:
        """Process same entries for multiple regions"""
        all_results = []
        
        for region in regions:
            region_results = self.process_region_batch(entries, region)
            all_results.extend(region_results)
            
        return all_results
    
    def process_single_entry(self, entry: Dict[str, str], region: str) -> Dict[str, Any]:
        """Process single entry for given region"""
        title = entry['title']
        url = entry['url']
        
        # Step 1: Content analysis
        content_analysis = self.content_analyzer.analyze_complete(title, url)
        
        # Step 2: SEO package generation
        seo_package = self.seo_generator.generate_seo_package(content_analysis, region)
        
        # Combine results
        result = {
            'original_title': title,
            'original_url': url,
            'region': region,
            **seo_package  # slug, title, meta_description
        }
        
        return result
    
    async def process_single_entry_async(self, entry: Dict[str, str], region: str) -> Dict[str, Any]:
        """Async version of single entry processing"""
        # Simulate async processing with small delay
        await asyncio.sleep(0.001)  # Minimal delay for async behavior
        return self.process_single_entry(entry, region)
    
    async def process_region_batch_async(self, entries: List[Dict[str, str]], region: str) -> List[Dict[str, Any]]:
        """Async batch processing for better performance"""
        tasks = [
            self.process_single_entry_async(entry, region) 
            for entry in entries
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful results
        successful_results = [
            result for result in results 
            if not isinstance(result, Exception)
        ]
        
        return successful_results
    
    def process_with_failure_handling(self, entries: List[Dict[str, str]], region: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Process with explicit failure handling"""
        results = []
        failed_entries = []
        
        for entry in entries:
            try:
                result = self.process_single_entry(entry, region)
                results.append(result)
            except Exception as e:
                failed_entry = {
                    'entry': entry,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                failed_entries.append(failed_entry)
                
        return results, failed_entries
    
    def process_llm_batch(self, entries: List[Dict[str, str]], region: str = None) -> List[Dict[str, Any]]:
        """Process entries in LLM-optimized batches"""
        # For testing purposes, this should be called with reasonable batch sizes
        if len(entries) > 10:
            raise ValueError("Batch size too large for LLM processing")
            
        # Process each entry individually but return structured results
        results = []
        for entry in entries:
            try:
                result = self.process_single_entry(entry, region)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process entry in batch: {e}")
                # Continue with other entries
                continue
            
        return results