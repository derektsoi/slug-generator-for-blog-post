"""
Rule-Based Analyzer - Pure Quantitative SEO Analysis

Provides reliable quantitative metrics without any API dependencies.
NO qualitative feedback - only structured data and numerical scores.
"""

import re
from typing import Dict, List, Any, Optional


class RuleBasedAnalyzer:
    """Pure quantitative analysis with no API dependencies"""
    
    def __init__(self):
        """Initialize analyzer with quantitative rules and patterns"""
        
        # Brand recognition patterns (quantitative detection)
        self.brand_patterns = [
            r'jojo-maman-bebe',
            r'skinniydip', 
            r'iface',
            r'rhinoshield',
            r'daikoku',
            r'rakuten',
            r'amazon',
            r'gap',
            r'kindle',
            r'sanrio',
            r'agete',
            r'verish'
        ]
        
        # Cultural term mappings for preservation detection
        self.cultural_terms = {
            '一番賞': 'ichiban-kuji',
            'JK制服': 'jk-uniform',
            '大國藥妝': 'daikoku-drugstore', 
            '樂天': 'rakuten',
            '官網': 'official-store',
            '集運': 'shipping',
            '代購': 'proxy-shopping',
            '藥妝': 'drugstore'
        }
        
        # Generic terms that dilute cultural authenticity
        self.generic_terms = [
            'merchandise', 'products', 'items', 'goods', 'stuff',
            'things', 'collection', 'selection'
        ]

    def analyze_slug(self, slug: str, title: str, content: str) -> Dict[str, Any]:
        """
        Perform pure quantitative analysis of slug quality
        
        Args:
            slug: The slug to analyze
            title: Original title for context
            content: Original content for context
            
        Returns:
            Dict with quantitative metrics only - NO qualitative feedback
        """
        
        # Technical SEO metrics
        technical_metrics = self._analyze_technical_seo(slug)
        
        # Brand detection metrics
        brand_metrics = self._analyze_brand_hierarchy(slug, title)
        
        # Cultural preservation metrics
        cultural_metrics = self._analyze_cultural_preservation(slug, title)
        
        # Length and structure metrics
        structure_metrics = self._analyze_structure(slug)
        
        # SEO compliance metrics
        compliance_metrics = self._analyze_seo_compliance(slug)
        
        # Overall quantitative score
        overall_score = self._calculate_overall_score([
            technical_metrics['score'],
            brand_metrics['score'], 
            cultural_metrics['score'],
            structure_metrics['score'],
            compliance_metrics['score']
        ])
        
        return {
            'analysis_type': 'quantitative_only',
            'overall_score': overall_score,
            'technical_seo': technical_metrics,
            'brand_hierarchy': brand_metrics,
            'cultural_preservation': cultural_metrics,
            'structure_analysis': structure_metrics,
            'seo_compliance': compliance_metrics,
            'metadata': {
                'analyzer_version': '1.0',
                'slug_length': len(slug),
                'word_count': len(slug.split('-')),
                'analysis_timestamp': self._get_timestamp()
            }
        }

    def _analyze_technical_seo(self, slug: str) -> Dict[str, Any]:
        """Analyze technical SEO factors with quantitative scoring"""
        
        word_count = len(slug.split('-'))
        char_count = len(slug)
        
        # Optimal scoring around 4-6 words, 30-60 characters
        word_score = max(0.0, 1.0 - abs(word_count - 5) * 0.1)
        char_score = max(0.0, 1.0 - max(0, char_count - 50) * 0.02)
        
        # Structure quality
        has_numbers = bool(re.search(r'\d', slug))
        has_special_chars = bool(re.search(r'[^a-z0-9\-]', slug))
        proper_format = slug.islower() and not slug.startswith('-') and not slug.endswith('-')
        
        structure_score = 1.0
        if has_numbers:
            structure_score -= 0.1  # Numbers slightly reduce readability
        if has_special_chars:
            structure_score -= 0.3  # Special chars hurt SEO
        if not proper_format:
            structure_score -= 0.2  # Poor formatting
            
        structure_score = max(0.0, structure_score)
        
        overall_technical_score = (word_score + char_score + structure_score) / 3
        
        return {
            'score': overall_technical_score,
            'word_count': word_count,
            'char_count': char_count,
            'word_score': word_score,
            'char_score': char_score,
            'structure_score': structure_score,
            'has_numbers': has_numbers,
            'has_special_chars': has_special_chars,
            'proper_format': proper_format
        }

    def _analyze_brand_hierarchy(self, slug: str, title: str) -> Dict[str, Any]:
        """Analyze brand detection and positioning"""
        
        # Count detected brands in slug
        detected_brands = []
        for pattern in self.brand_patterns:
            if re.search(pattern, slug, re.IGNORECASE):
                detected_brands.append(pattern)
        
        brands_count = len(detected_brands)
        
        # Score based on brand detection
        if brands_count >= 3:
            score = 0.95  # Excellent multi-brand handling
        elif brands_count >= 2:
            score = 0.85  # Good multi-brand
        elif brands_count >= 1:
            score = 0.7   # Single brand detected
        else:
            score = 0.3   # No brands detected
        
        # Brand positioning analysis
        brand_positions = []
        for brand in detected_brands:
            match = re.search(brand, slug, re.IGNORECASE)
            if match:
                position = match.start() / len(slug)  # Relative position (0-1)
                brand_positions.append(position)
        
        avg_brand_position = sum(brand_positions) / len(brand_positions) if brand_positions else 0
        
        return {
            'score': score,
            'detected_brands': detected_brands,
            'brands_count': brands_count,
            'brand_positions': brand_positions,
            'avg_brand_position': avg_brand_position,
            'multi_brand_handling': brands_count >= 2
        }

    def _analyze_cultural_preservation(self, slug: str, title: str) -> Dict[str, Any]:
        """Analyze cultural term preservation quantitatively"""
        
        # Find cultural terms in original title
        original_cultural_terms = []
        for original_term, english_term in self.cultural_terms.items():
            if original_term in title:
                original_cultural_terms.append((original_term, english_term))
        
        # Find preserved terms in slug
        preserved_terms = []
        for original_term, english_term in original_cultural_terms:
            if english_term.lower() in slug.lower():
                preserved_terms.append(english_term)
        
        # Calculate preservation rate
        if original_cultural_terms:
            preservation_rate = len(preserved_terms) / len(original_cultural_terms)
        else:
            preservation_rate = 1.0  # No cultural terms to preserve
        
        # Check for generic dilution
        generic_dilution = any(term in slug.lower() for term in self.generic_terms)
        
        # Calculate cultural authenticity score
        base_score = preservation_rate
        if generic_dilution and preserved_terms:
            base_score *= 0.8  # 20% penalty for generic dilution
        
        return {
            'score': base_score,
            'preservation_rate': preservation_rate,
            'original_cultural_terms': [term[0] for term in original_cultural_terms],
            'preserved_terms': preserved_terms,
            'generic_dilution': generic_dilution,
            'cultural_terms_count': len(original_cultural_terms)
        }

    def _analyze_structure(self, slug: str) -> Dict[str, Any]:
        """Analyze slug structure and readability"""
        
        words = slug.split('-')
        word_count = len(words)
        
        # Word length distribution
        word_lengths = [len(word) for word in words]
        avg_word_length = sum(word_lengths) / len(word_lengths)
        
        # Readability metrics
        very_long_words = sum(1 for length in word_lengths if length > 8)
        very_short_words = sum(1 for length in word_lengths if length < 3)
        
        # Structure quality scoring
        readability_score = 1.0
        if very_long_words > word_count * 0.3:  # >30% very long words
            readability_score -= 0.2
        if very_short_words > word_count * 0.3:  # >30% very short words  
            readability_score -= 0.1
        if avg_word_length > 7:  # Average word too long
            readability_score -= 0.1
        
        readability_score = max(0.0, readability_score)
        
        return {
            'score': readability_score,
            'word_count': word_count,
            'word_lengths': word_lengths,
            'avg_word_length': avg_word_length,
            'very_long_words': very_long_words,
            'very_short_words': very_short_words,
            'readability_score': readability_score
        }

    def _analyze_seo_compliance(self, slug: str) -> Dict[str, Any]:
        """Analyze SEO best practices compliance"""
        
        compliance_checks = {
            'uses_hyphens': '-' in slug and '_' not in slug,
            'lowercase_only': slug.islower(),
            'no_special_chars': not bool(re.search(r'[^a-z0-9\-]', slug)),
            'reasonable_length': 10 <= len(slug) <= 60,
            'starts_with_letter': slug and slug[0].isalpha(),
            'ends_with_alphanumeric': slug and slug[-1].isalnum(),
            'no_consecutive_hyphens': '--' not in slug,
            'no_leading_trailing_hyphens': not slug.startswith('-') and not slug.endswith('-')
        }
        
        # Calculate compliance score
        passed_checks = sum(1 for passed in compliance_checks.values() if passed)
        compliance_score = passed_checks / len(compliance_checks)
        
        return {
            'score': compliance_score,
            'compliance_checks': compliance_checks,
            'passed_checks': passed_checks,
            'total_checks': len(compliance_checks),
            'compliance_percentage': compliance_score * 100
        }

    def _calculate_overall_score(self, scores: List[float]) -> float:
        """Calculate weighted overall score from component scores"""
        
        # Equal weighting for quantitative analysis
        return sum(scores) / len(scores) if scores else 0.0

    def _get_timestamp(self) -> str:
        """Get current timestamp for metadata"""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_analysis_summary(self, analysis_result: Dict) -> str:
        """
        Generate structured summary of quantitative analysis
        
        NOTE: This is NOT qualitative feedback - just structured data summary
        """
        
        overall = analysis_result['overall_score']
        technical = analysis_result['technical_seo']['score']
        brands = analysis_result['brand_hierarchy']['score']
        cultural = analysis_result['cultural_preservation']['score']
        
        summary_parts = [
            f"Quantitative Analysis Summary (Score: {overall:.2f})",
            f"Technical SEO: {technical:.2f}",
            f"Brand Detection: {brands:.2f}", 
            f"Cultural Preservation: {cultural:.2f}",
            f"Word Count: {analysis_result['metadata']['word_count']}",
            f"Character Length: {analysis_result['metadata']['slug_length']}"
        ]
        
        return " | ".join(summary_parts)