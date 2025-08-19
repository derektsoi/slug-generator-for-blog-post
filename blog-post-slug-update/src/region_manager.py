from typing import List


class RegionManager:
    """Manage regions and their URL-friendly suffixes"""
    
    def __init__(self, regions: List[str] = None):
        # Default regions
        self.default_regions = [
            "Hong Kong", "Singapore", "Australia", "Malaysia", "Taiwan"
        ]
        self.regions = regions or self.default_regions.copy()
    
    def get_region_slug_suffix(self, region: str) -> str:
        """Convert region name to URL-friendly suffix"""
        mapping = {
            "Hong Kong": "hong-kong",
            "Singapore": "singapore", 
            "Australia": "australia",
            "Malaysia": "malaysia",
            "Taiwan": "taiwan"
        }
        
        # Use mapping if available, otherwise convert to lowercase with hyphens
        return mapping.get(region, region.lower().replace(' ', '-'))
    
    def add_region(self, region_name: str):
        """Dynamically add new regions"""
        if region_name not in self.regions:
            self.regions.append(region_name)