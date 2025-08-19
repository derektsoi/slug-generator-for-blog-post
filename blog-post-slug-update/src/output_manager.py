import json
import os
from pathlib import Path
from typing import List, Dict, Any


class OutputManager:
    """Manage output file operations for SEO packages"""
    
    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def save_region_results(self, results: List[Dict[str, Any]], region: str, timestamp: str) -> str:
        """Save results for single region"""
        # Convert region name to filename-friendly format
        region_filename = region.lower().replace(' ', '_')
        filename = f"seo_mapping_{region_filename}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        # Prepare output data
        output_data = {
            'region': region,
            'generated_at': timestamp,
            'total_entries': len(results),
            'entries': results
        }
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        return str(filepath)
    
    def save_all_regions(self, region_results: Dict[str, List[Dict[str, Any]]], timestamp: str) -> Dict[str, str]:
        """Save separate file for each region"""
        saved_files = {}
        
        for region, results in region_results.items():
            filepath = self.save_region_results(results, region, timestamp)
            saved_files[region] = filepath
            
        return saved_files