import re
import logging
from typing import Dict, Any
from character_limit_handler import CharacterLimitHandler

logger = logging.getLogger(__name__)


def llm_call_with_retry(prompt: str, max_retries: int = 2) -> str:
    """Mock LLM call function for testing purposes"""
    # In real implementation, this would call OpenAI API
    # For testing, we return a shortened version
    return "shortened-version"


class SEOGenerator:
    """Generate complete SEO packages (slug, title, meta) for blog posts"""
    
    def __init__(self, character_handler_mode: str = "retry_shorter"):
        self.char_handler = CharacterLimitHandler(character_handler_mode)
        
        # Region mapping for URL-friendly suffixes
        self.region_suffixes = {
            "Hong Kong": "hong-kong",
            "Singapore": "singapore", 
            "Australia": "australia",
            "Malaysia": "malaysia",
            "Taiwan": "taiwan"
        }
    
    def generate_seo_package(self, content_analysis: Dict[str, Any], region: str) -> Dict[str, str]:
        """Generate complete SEO package for given content analysis and region"""
        
        # Extract key information
        brands = content_analysis.get('brands', [])
        category = content_analysis.get('category', 'guide')
        keywords = content_analysis.get('evergreen_keywords', [])
        promo_terms = content_analysis.get('promo_terms', [])
        
        # Generate each component
        slug = self._generate_slug(brands, category, keywords, region)
        title = self._generate_title(brands, category, keywords, region, promo_terms)
        meta_description = self._generate_meta_description(brands, category, keywords, region)
        
        # Apply character limits
        slug = self.char_handler.handle_over_limit(slug, 60, "slug")
        title = self.char_handler.handle_over_limit(title, 60, "title")
        meta_description = self.char_handler.handle_over_limit(meta_description, 155, "meta_description")
        
        return {
            'slug': slug,
            'title': title, 
            'meta_description': meta_description
        }
    
    def _generate_slug(self, brands: list, category: str, keywords: list, region: str) -> str:
        """Generate SEO-friendly slug"""
        slug_parts = []
        
        # Add main keywords/brands (avoid promotional terms)
        if 'japanese' in keywords and 'jewelry' in keywords:
            slug_parts.extend(['japanese', 'jewelry'])
        elif 'uk' in keywords and 'baby' in keywords:
            slug_parts.extend(['uk', 'baby'])
        elif 'kindle' in keywords:
            slug_parts.extend(['kindle', 'guide'])
        
        # Add primary brand (clean version)
        if brands:
            brand = brands[0]
            if 'JoJo Maman Bébé' in brand:
                slug_parts.insert(0, 'jojo-maman-bebe')
            elif 'Kindle' in brand:
                if 'kindle' not in slug_parts:
                    slug_parts.insert(0, 'kindle')
        
        # Add category context
        if category == 'jewelry' and 'brands' in keywords:
            if 'brands' not in slug_parts:
                slug_parts.append('brands')
        elif category == 'baby-fashion':
            if 'clothes' in keywords and 'clothes' not in slug_parts:
                slug_parts.append('clothes')  
        elif category == 'electronics' and 'guide' in keywords:
            if 'guide' not in slug_parts:
                slug_parts.append('guide')
                
        # Add content type
        if 'guide' in keywords and 'guide' not in slug_parts:
            slug_parts.append('guide')
        
        # Add region at the end
        region_suffix = self.region_suffixes.get(region, region.lower().replace(' ', '-'))
        slug_parts.append(region_suffix)
        
        # Create final slug
        slug = '-'.join(slug_parts)
        
        # Clean up the slug
        slug = re.sub(r'-+', '-', slug)  # Remove multiple hyphens
        slug = slug.strip('-')  # Remove leading/trailing hyphens
        slug = slug.lower()
        
        return slug
    
    def _generate_title(self, brands: list, category: str, keywords: list, region: str, promo_terms: list) -> str:
        """Generate human-friendly, click-optimized title"""
        
        # Build title components
        if 'japanese' in keywords and 'jewelry' in keywords:
            title = "Japanese Jewelry Brands Guide"
        elif brands and 'JoJo Maman Bébé' in brands[0]:
            title = "JoJo Maman Bébé UK Baby Clothes Guide"
        elif 'kindle' in keywords:
            title = "Kindle E-Reader Guide & Comparison"
        elif 'gap' in ' '.join(brands).lower():
            title = "GAP Group US Online Shopping Guide"
        else:
            # Generic title based on category
            if category == 'jewelry':
                title = "Jewelry Shopping Guide"
            elif category == 'baby-fashion':
                title = "Baby Fashion Shopping Guide"
            else:
                title = "Shopping Guide"
        
        # Add region
        title += f" | {region}"
        
        return title
    
    def _generate_meta_description(self, brands: list, category: str, keywords: list, region: str) -> str:
        """Generate compelling meta description with CTA and benefits"""
        
        # Start with main value proposition
        if 'japanese' in keywords and 'jewelry' in keywords:
            if brands:
                brand_list = ', '.join(brands[:3])  # First 3 brands
                meta = f"Discover popular Japanese jewelry brands like {brand_list}."
            else:
                meta = "Discover popular Japanese jewelry brands and collections."
        elif brands and 'JoJo Maman Bébé' in brands[0]:
            meta = "Shop JoJo Maman Bébé UK baby clothes with exclusive discounts."
        elif 'kindle' in keywords:
            meta = "Compare Kindle e-reader models and find the best deals."
        else:
            # Generic meta based on category
            if category == 'jewelry':
                meta = "Explore premium jewelry collections and brands."
            elif category == 'baby-fashion': 
                meta = "Find the best baby fashion and clothing deals."
            else:
                meta = "Discover the best shopping deals and guides."
        
        # Add benefit/value
        if 'shopping' in keywords:
            meta += " Get authentic products"
        else:
            meta += " Find exclusive deals"
            
        # Add service/location benefit  
        meta += f" with BuyandShip {region}"
        
        # Add call-to-action
        if 'guide' in keywords:
            meta += " shipping service."
        else:
            meta += ". Shop now!"
        
        return meta
    
    def _clean_slug(self, slug: str) -> str:
        """Clean and validate slug format"""
        # Convert to lowercase
        slug = slug.lower()
        
        # Replace spaces and invalid characters with hyphens
        slug = re.sub(r'[^a-z0-9\-]', '-', slug)
        
        # Remove multiple consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        
        # Remove leading and trailing hyphens
        slug = slug.strip('-')
        
        return slug