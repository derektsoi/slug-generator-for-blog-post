import urllib.parse
import re
from typing import List, Dict, Any


class ContentAnalyzer:
    """Content intelligence extraction and analysis for blog posts"""
    
    def __init__(self):
        # Brand patterns for extraction
        self.brand_patterns = {
            'jewelry': ['Agete', 'nojess', 'Star Jewelry', 'Tiffany', 'Pandora'],
            'fashion': ['JoJo Maman Bébé', 'H&M', 'Zara', 'Uniqlo', 'GAP', 'Old Navy', 'Banana Republic', 'Athleta'],
            'electronics': ['Kindle', 'Amazon', 'Apple', 'Sony', 'Nintendo', 'Samsung'],
            'beauty': ['Swarovski', 'YSL', 'Chanel'],
            'sports': ['Nike', 'Adidas', 'New Balance', 'Champion', 'BEAMS'],
            'home': ['3COINS'],
            'baby': ['Carter\'s']
        }
        
        # Category keywords mapping
        self.category_keywords = {
            'jewelry': ['珠寶', '首飾', 'jewelry', '飾品'],
            'baby-fashion': ['童裝', '嬰兒', '母嬰', 'baby', '育兒', 'bébé'],
            'electronics': ['電子', 'kindle', '閱讀器', '電腦', 'electronics', '手錶', 'watch'],
            'fashion': ['服飾', '服裝', '時尚', 'fashion', '衣服', '褲', '鞋'],
            'beauty': ['美妝', '護膚', '化妝', 'beauty', 'skincare'],
            'home': ['家居', '用品', 'home'],
            'sports': ['運動', 'sports', '戶外', 'outdoor']
        }
        
        # Promotional terms
        self.promo_patterns = [
            r'\d+折', r'\d+\s*折起', r'折扣', r'減價', r'特價', r'優惠',
            r'sale', r'discount', r'off', r'deal', r'promo'
        ]
    
    def decode_url_slug(self, url: str) -> str:
        """Decode URL slug from encoded Chinese characters"""
        try:
            # Extract the last part of the URL (the slug)
            url_parts = url.split('/')
            encoded_slug = url_parts[-1] if url_parts[-1] else url_parts[-2]
            
            # Remove trailing slash if present
            encoded_slug = encoded_slug.rstrip('/')
            
            # URL decode to get Chinese characters
            decoded = urllib.parse.unquote(encoded_slug, encoding='utf-8')
            
            return decoded
        except Exception:
            return url.split('/')[-1] if url else ''
    
    def extract_brands(self, title: str) -> List[str]:
        """Extract brand names from title text"""
        brands_found = []
        title_lower = title.lower()
        
        # Check all brand patterns
        for category, brands in self.brand_patterns.items():
            for brand in brands:
                # Case-insensitive search
                if brand.lower() in title_lower:
                    brands_found.append(brand)
                # Also check for variations without special characters
                brand_clean = re.sub(r'[^\w\s]', '', brand)
                if brand_clean.lower() in title_lower:
                    if brand not in brands_found:
                        brands_found.append(brand)
        
        # Special handling for common brand variations
        if 'jojo' in title_lower and 'maman' in title_lower:
            if 'JoJo Maman Bébé' not in brands_found:
                brands_found.append('JoJo Maman Bébé')
        
        # For electronics, check if Amazon is implied by Kindle
        if 'kindle' in title_lower and 'Amazon' not in brands_found:
            brands_found.append('Amazon')
            
        return sorted(list(set(brands_found)))  # Remove duplicates and sort
    
    def categorize_content(self, title: str) -> str:
        """Automatically detect content category"""
        title_lower = title.lower()
        
        # Score each category based on keyword matches
        category_scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in title_lower:
                    score += 1
            category_scores[category] = score
        
        # Find the category with highest score
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category
        
        # Default categorization based on common patterns
        if any(word in title_lower for word in ['珠寶', '首飾', 'jewelry']):
            return 'jewelry'
        elif any(word in title_lower for word in ['童裝', 'baby', 'bébé', '育兒']):
            return 'baby-fashion'
        elif any(word in title_lower for word in ['kindle', '電子', 'electronics']):
            return 'electronics'
        else:
            return 'fashion'  # Default fallback
    
    def extract_keywords(self, title: str, url: str) -> List[str]:
        """Extract evergreen keywords from title and URL context"""
        keywords = []
        title_lower = title.lower()
        decoded_url = self.decode_url_slug(url).lower()
        
        # Extract from title
        if 'japanese' in title_lower or '日牌' in title or '日本' in title:
            keywords.append('japanese')
        
        if 'jewelry' in title_lower or '珠寶' in title:
            keywords.append('jewelry')
            
        if 'brand' in title_lower or '品牌' in title:
            keywords.append('brands')
            
        if 'guide' in title_lower or '攻略' in title or '教學' in title or '一次睇' in title:
            keywords.append('guide')
            
        if 'uk' in title_lower or '英國' in title:
            keywords.append('uk')
            
        if 'baby' in title_lower or '童裝' in title or 'bébé' in title:
            keywords.append('baby')
            
        if 'clothes' in title_lower or '服飾' in title or '衣' in title or '童裝' in title:
            keywords.append('clothes')
            
        if 'shopping' in title_lower or '網購' in title or '購買' in title:
            keywords.append('shopping')
            
        if 'kindle' in title_lower:
            keywords.extend(['kindle', 'ereader', 'amazon'])
            
        if 'comparison' in title_lower or '比較' in title:
            keywords.append('comparison')
            
        # Extract from URL context
        if 'kindle' in decoded_url:
            keywords.extend(['kindle', 'ereader', 'amazon'])
            
        return sorted(list(set(keywords)))  # Remove duplicates and sort
    
    def detect_promotional_terms(self, title: str) -> Dict[str, Any]:
        """Detect promotional terms in title"""
        promo_terms = []
        
        for pattern in self.promo_patterns:
            matches = re.findall(pattern, title, re.IGNORECASE)
            promo_terms.extend(matches)
        
        # Clean up duplicates
        promo_terms = list(set(promo_terms))
        
        return {
            'has_promo': len(promo_terms) > 0,
            'promo_terms': promo_terms
        }
    
    def analyze_complete(self, title: str, url: str) -> Dict[str, Any]:
        """Complete analysis pipeline returning all required fields"""
        promo_result = self.detect_promotional_terms(title)
        
        return {
            'decoded_url_slug': self.decode_url_slug(url),
            'brands': self.extract_brands(title),
            'category': self.categorize_content(title),
            'content_type': self._determine_content_type(title),
            'evergreen_keywords': self.extract_keywords(title, url),
            'promo_terms': promo_result['promo_terms'],
            'has_promo': promo_result['has_promo']
        }
    
    def _determine_content_type(self, title: str) -> str:
        """Determine the type of content (guide, review, comparison, etc.)"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['攻略', 'guide', '教學']):
            return 'guide'
        elif any(word in title_lower for word in ['比較', 'comparison', 'vs']):
            return 'comparison'
        elif any(word in title_lower for word in ['review', '評測', '測試']):
            return 'review'
        elif any(word in title_lower for word in ['購買', 'shopping', '網購']):
            return 'shopping-guide'
        else:
            return 'guide'  # Default fallback