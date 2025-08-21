import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple

# Use actual available imports from the refactored codebase
from core.slug_generator import SlugGenerator
from core.content_extractor import ContentExtractor
from core.validators import SlugValidator
from utils.retry_logic import exponential_backoff

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Production-scale batch processing of SEO packages"""
    
    def __init__(self, batch_size: int = 8, max_retries: int = 3, prompt_version: str = "v10"):
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.prompt_version = prompt_version
        
        # Initialize core components
        self.slug_generator = SlugGenerator(prompt_version=prompt_version)
        self.content_extractor = ContentExtractor()
        self.validator = SlugValidator()
    
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
    
    def process_single_entry(self, entry: Dict[str, str], region: str = None) -> Dict[str, Any]:
        """Process single entry for given region"""
        title = entry.get('title', '')
        url = entry.get('url', '')
        
        try:
            # Step 1: Content extraction if URL provided
            if url:
                extracted_content = self.content_extractor.extract_content(url)
                content = extracted_content.get('content', title)
            else:
                content = title
            
            # Step 2: Generate slug using V10 prompt
            result = self.slug_generator.generate_slug_from_content(title, content)
            
            # Step 3: Validate result
            primary_slug = result.get('primary', '')
            if self.validator.is_valid_slug(primary_slug):
                # Add metadata
                result.update({
                    'original_title': title,
                    'original_url': url,
                    'region': region,
                    'processing_status': 'success'
                })
            else:
                result['processing_status'] = 'validation_failed'
                
            return result
            
        except Exception as e:
            logger.error(f"Failed to process entry {title}: {e}")
            return {
                'original_title': title,
                'original_url': url,
                'region': region,
                'processing_status': 'failed',
                'error': str(e)
            }
    
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
        """Process entries in LLM-optimized batches with proper error handling"""
        if len(entries) > 10:
            raise ValueError(f"Batch size {len(entries)} exceeds maximum of 10 for LLM processing")
            
        results = []
        successful_count = 0
        failed_count = 0
        
        for i, entry in enumerate(entries):
            try:
                result = self.process_single_entry(entry, region)
                results.append(result)
                
                if result.get('processing_status') == 'success':
                    successful_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to process entry {i+1}/{len(entries)} in batch: {e}")
                failed_result = {
                    'original_title': entry.get('title', ''),
                    'original_url': entry.get('url', ''),
                    'region': region,
                    'processing_status': 'error',
                    'error': str(e)
                }
                results.append(failed_result)
                failed_count += 1
                
        logger.info(f"Batch processing complete: {successful_count} successful, {failed_count} failed")
        return results