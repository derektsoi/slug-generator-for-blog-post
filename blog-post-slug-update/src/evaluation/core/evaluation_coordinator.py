"""
Evaluation Coordinator - Orchestrates Quantitative + Qualitative Analysis

Combines rule-based quantitative analysis with LLM qualitative evaluation.
Provides graceful degradation when LLM unavailable.
"""

from typing import Dict, List, Any, Optional
from .rule_based_analyzer import RuleBasedAnalyzer
from .seo_evaluator_clean import SEOEvaluator
from ..utils.exceptions import LLMUnavailableError, InvalidAPIKeyError
from ..utils.retry_logic import RetryConfig


class EvaluationCoordinator:
    """Orchestrate both quantitative and qualitative analysis"""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        retry_config: Optional[RetryConfig] = None,
        enable_llm: bool = True
    ):
        """
        Initialize evaluation coordinator
        
        Args:
            api_key: OpenAI API key (optional - quantitative analysis always available)
            model: OpenAI model for qualitative analysis
            retry_config: Retry configuration for LLM calls
            enable_llm: Whether to attempt LLM evaluation
        """
        
        # Rule-based analyzer (always available)
        self.quantitative_analyzer = RuleBasedAnalyzer()
        
        # LLM evaluator (optional)
        self.qualitative_evaluator = None
        self.llm_available = False
        
        if enable_llm and api_key and api_key != "test-key":
            try:
                self.qualitative_evaluator = SEOEvaluator(
                    api_key=api_key,
                    model=model,
                    retry_config=retry_config
                )
                self.llm_available = True
            except InvalidAPIKeyError:
                self.llm_available = False

    def evaluate_comprehensive(self, slug: str, title: str, content: str) -> Dict[str, Any]:
        """
        Perform comprehensive evaluation using both quantitative and qualitative analysis
        
        Args:
            slug: The slug to evaluate
            title: Original title
            content: Original content
            
        Returns:
            Dict with quantitative analysis (always) and qualitative insights (when available)
        """
        
        # Always perform quantitative analysis
        quantitative_result = self.quantitative_analyzer.analyze_slug(slug, title, content)
        
        # Attempt qualitative analysis if LLM available
        qualitative_result = None
        llm_error = None
        
        if self.llm_available and self.qualitative_evaluator:
            try:
                qualitative_result = self.qualitative_evaluator.evaluate_slug(slug, title, content)
            except LLMUnavailableError as e:
                llm_error = str(e)
                # Don't fail - continue with quantitative only
        
        # Combine results
        return self._combine_analyses(quantitative_result, qualitative_result, llm_error)

    def evaluate_failure_case(self, title: str, content: str, failure_reason: str) -> Dict[str, Any]:
        """
        Evaluate failure cases using available analysis methods
        
        Args:
            title: Original title that failed
            content: Original content
            failure_reason: Reason for failure
            
        Returns:
            Dict with failure analysis
        """
        
        # Basic quantitative analysis of failure factors
        failure_analysis = {
            'analysis_type': 'failure_case',
            'title_length': len(title),
            'title_word_count': len(title.split()),
            'content_length': len(content),
            'failure_reason': failure_reason,
            'complexity_indicators': self._analyze_complexity(title, content)
        }
        
        # Attempt LLM failure analysis if available
        if self.llm_available and self.qualitative_evaluator:
            try:
                llm_failure_analysis = self.qualitative_evaluator.evaluate_failure_case(
                    title, content, failure_reason
                )
                failure_analysis.update(llm_failure_analysis)
            except LLMUnavailableError as e:
                failure_analysis['llm_error'] = str(e)
        
        return failure_analysis

    def get_analysis_capabilities(self) -> Dict[str, Any]:
        """
        Get information about available analysis capabilities
        
        Returns:
            Dict describing what analysis types are available
        """
        
        return {
            'quantitative_analysis': True,  # Always available
            'qualitative_analysis': self.llm_available,
            'llm_model': self.qualitative_evaluator.model if self.qualitative_evaluator else None,
            'analysis_dimensions': {
                'quantitative': [
                    'technical_seo',
                    'brand_hierarchy', 
                    'cultural_preservation',
                    'structure_analysis',
                    'seo_compliance'
                ],
                'qualitative': [
                    'user_intent_match',
                    'brand_hierarchy',
                    'cultural_authenticity', 
                    'click_through_potential',
                    'competitive_differentiation',
                    'technical_seo'
                ] if self.llm_available else []
            }
        }

    def _combine_analyses(
        self, 
        quantitative: Dict[str, Any], 
        qualitative: Optional[Dict[str, Any]], 
        llm_error: Optional[str]
    ) -> Dict[str, Any]:
        """Combine quantitative and qualitative analyses"""
        
        # Base result with quantitative analysis
        combined_result = {
            'quantitative_analysis': quantitative,
            'qualitative_insights': qualitative,
            'analysis_type': 'complete' if qualitative else 'quantitative_only',
            'llm_available': qualitative is not None,
            'capabilities': self.get_analysis_capabilities()
        }
        
        # Add error information if LLM failed
        if llm_error:
            combined_result['llm_error'] = llm_error
        
        # Generate combined recommendation when both analyses available
        if quantitative and qualitative:
            combined_result['combined_recommendation'] = self._generate_combined_recommendation(
                quantitative, qualitative
            )
            
            # Calculate meta-score combining both approaches
            combined_result['meta_analysis'] = self._calculate_meta_analysis(
                quantitative, qualitative
            )
        
        return combined_result

    def _generate_combined_recommendation(
        self, 
        quantitative: Dict[str, Any], 
        qualitative: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate recommendation combining both analysis types"""
        
        quant_score = quantitative['overall_score']
        qual_score = qualitative['overall_score']
        
        # Weighted combination (favor qualitative insights slightly)
        combined_score = (quant_score * 0.4) + (qual_score * 0.6)
        
        # Identify convergent insights
        convergent_insights = []
        
        # Technical SEO convergence
        quant_technical = quantitative['technical_seo']['score']
        qual_technical = qualitative['dimension_scores']['technical_seo']
        if abs(quant_technical - qual_technical) < 0.2:
            convergent_insights.append('Technical SEO assessment converges between analyses')
        
        # Brand hierarchy convergence
        quant_brand = quantitative['brand_hierarchy']['score']
        qual_brand = qualitative['dimension_scores']['brand_hierarchy']
        if abs(quant_brand - qual_brand) < 0.2:
            convergent_insights.append('Brand hierarchy assessment shows strong agreement')
        
        # Generate overall recommendation
        if combined_score > 0.8:
            recommendation = 'Excellent slug - both quantitative metrics and qualitative insights positive'
        elif combined_score > 0.6:
            recommendation = 'Good slug with room for targeted improvements'
        else:
            recommendation = 'Significant improvements needed across multiple dimensions'
        
        return {
            'combined_score': combined_score,
            'recommendation': recommendation,
            'convergent_insights': convergent_insights,
            'analysis_agreement': abs(quant_score - qual_score) < 0.2,
            'primary_strengths': qualitative.get('key_strengths', []),
            'priority_improvements': qualitative.get('improvement_areas', [])
        }

    def _calculate_meta_analysis(
        self,
        quantitative: Dict[str, Any],
        qualitative: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate meta-analysis combining both approaches"""
        
        # Dimension-by-dimension comparison
        dimension_comparison = {}
        
        # Map overlapping dimensions
        dimension_mapping = {
            'technical_seo': 'technical_seo',
            'brand_hierarchy': 'brand_hierarchy',
            'cultural_preservation': 'cultural_authenticity'
        }
        
        for quant_dim, qual_dim in dimension_mapping.items():
            quant_score = quantitative[quant_dim]['score']
            qual_score = qualitative['dimension_scores'][qual_dim]
            
            dimension_comparison[quant_dim] = {
                'quantitative_score': quant_score,
                'qualitative_score': qual_score,
                'agreement': abs(quant_score - qual_score) < 0.2,
                'difference': abs(quant_score - qual_score)
            }
        
        # Overall meta-insights
        avg_agreement = sum(1 for comp in dimension_comparison.values() if comp['agreement']) / len(dimension_comparison)
        
        return {
            'dimension_comparison': dimension_comparison,
            'overall_agreement': avg_agreement,
            'analysis_confidence': (quantitative['metadata']['analyzer_version'], qualitative['confidence']),
            'meta_insights': self._generate_meta_insights(dimension_comparison, avg_agreement)
        }

    def _generate_meta_insights(self, dimension_comparison: Dict, avg_agreement: float) -> List[str]:
        """Generate insights from meta-analysis"""
        
        insights = []
        
        if avg_agreement > 0.8:
            insights.append('High agreement between quantitative and qualitative analyses')
        elif avg_agreement < 0.4:
            insights.append('Significant disagreement between analysis methods - manual review recommended')
        
        # Identify dimensions with large disagreements
        for dim, comp in dimension_comparison.items():
            if comp['difference'] > 0.3:
                insights.append(f'Large disagreement in {dim} assessment - qualitative analysis may reveal nuances')
        
        return insights

    def _analyze_complexity(self, title: str, content: str) -> List[str]:
        """Analyze complexity factors that might cause generation failures"""
        
        complexity_factors = []
        
        if len(title) > 100:
            complexity_factors.append('very_long_title')
        
        if len(title.split()) > 20:
            complexity_factors.append('high_word_count')
        
        # Multi-language content
        import re
        if re.search(r'[一-龯]', title) and re.search(r'[a-zA-Z]', title):
            complexity_factors.append('mixed_language_content')
        
        # Special characters
        if re.search(r'[！？、。／＆]', title):
            complexity_factors.append('special_punctuation')
        
        # Multiple brands/entities
        if '/' in title or '&' in title or '、' in title:
            complexity_factors.append('multiple_entities')
        
        return complexity_factors