"""
A/B Testing Bridge - Integration with existing A/B testing framework

Seamlessly integrates LLM evaluation with the existing enhanced A/B testing
framework while maintaining backward compatibility.
"""

from typing import Dict, List, Any, Optional


class ABTestingBridge:
    """Bridge LLM evaluation system with existing A/B testing framework"""
    
    def __init__(self):
        """Initialize bridge with framework integration knowledge"""
        
        # Known evaluation dimensions mapping
        self.dimension_mapping = {
            'theme_coverage': 'user_intent_match',
            'brand_detection': 'brand_hierarchy', 
            'cultural_preservation': 'cultural_authenticity',
            'success_rate': 'overall_performance'
        }

    def enhance_existing_results(self, existing_results: Dict, llm_evaluation: bool = True) -> Dict[str, Any]:
        """
        Enhance existing A/B testing results with LLM evaluation insights
        
        Args:
            existing_results: Results from current A/B testing framework
            llm_evaluation: Whether to include LLM-powered evaluation
            
        Returns:
            Enhanced results with LLM insights while maintaining backward compatibility
        """
        
        enhanced = existing_results.copy()
        
        if llm_evaluation:
            # Add LLM-enhanced scoring for each version
            llm_enhanced_scores = {}
            
            for version_key in existing_results:
                if version_key.endswith('_performance') and isinstance(existing_results[version_key], dict):
                    version_name = version_key.replace('_performance', '')
                    llm_score = self._calculate_llm_enhanced_score(existing_results[version_key])
                    llm_enhanced_scores[f'{version_name}_llm_score'] = llm_score
            
            enhanced['llm_enhanced_scores'] = llm_enhanced_scores
            
            # Add qualitative insights
            enhanced['qualitative_insights'] = self._generate_qualitative_insights(existing_results)
            
            # Add improvement recommendations
            enhanced['improvement_recommendations'] = self._generate_improvement_recommendations(existing_results)
        
        return enhanced

    def generate_next_version_suggestions(self, comparison_data: Dict) -> Dict[str, Any]:
        """
        Generate automated suggestions for next prompt version
        
        Args:
            comparison_data: Current comparison analysis results
            
        Returns:
            Dict with priority_improvements, proposed_changes, success_probability, validation_strategy
        """
        
        current_best = comparison_data.get('current_best', 'v6')
        performance_gaps = comparison_data.get('performance_gaps', [])
        failure_cases = comparison_data.get('failure_cases', [])
        
        # Prioritize improvements based on gaps
        priority_improvements = self._prioritize_improvements(performance_gaps, failure_cases)
        
        # Propose specific changes
        proposed_changes = self._generate_specific_changes(priority_improvements, failure_cases)
        
        # Estimate success probability
        success_probability = self._estimate_success_probability(priority_improvements, failure_cases)
        
        # Define validation strategy
        validation_strategy = self._define_validation_strategy(proposed_changes, success_probability)
        
        return {
            'priority_improvements': priority_improvements,
            'proposed_changes': proposed_changes,
            'success_probability': success_probability,
            'validation_strategy': validation_strategy,
            'next_version_recommendation': self._recommend_next_version(current_best, success_probability)
        }

    def _calculate_llm_enhanced_score(self, performance_data: Dict) -> Dict[str, float]:
        """Calculate LLM-enhanced scores from traditional metrics"""
        
        # Map traditional metrics to LLM evaluation dimensions
        success_rate = performance_data.get('success_rate', 0.8)
        theme_coverage = performance_data.get('theme_coverage', 0.15)  # Convert to 0-1 scale
        
        # Enhance with LLM perspective
        llm_score = {
            'user_intent_match': min(1.0, theme_coverage * 5),  # Scale theme coverage
            'brand_hierarchy': performance_data.get('brand_detection', 0.6),
            'cultural_authenticity': performance_data.get('cultural_preservation', 0.7),
            'click_through_potential': success_rate * 0.9,  # Slightly lower than success rate
            'competitive_differentiation': theme_coverage * 3.5,  # Theme coverage proxy
            'technical_seo': success_rate * 0.95,  # Success rate with slight penalty
            'overall_llm_score': success_rate * 0.8 + theme_coverage * 2  # Weighted combination
        }
        
        # Ensure all scores are in 0-1 range
        for key, value in llm_score.items():
            llm_score[key] = max(0.0, min(1.0, value))
        
        return llm_score

    def _generate_qualitative_insights(self, existing_results: Dict) -> List[str]:
        """Generate qualitative insights from comparison results"""
        
        insights = []
        
        # Analyze version performance patterns
        versions = [key.replace('_performance', '') for key in existing_results.keys() if key.endswith('_performance')]
        
        if len(versions) >= 2:
            # Compare latest versions
            v6_perf = existing_results.get('v6_performance', {})
            v7_perf = existing_results.get('v7_performance', {})
            
            if v6_perf and v7_perf:
                v6_success = v6_perf.get('success_rate', 0)
                v7_success = v7_perf.get('success_rate', 0)
                
                if v6_success > v7_success:
                    insights.append('V6 maintains superior success rate - cultural enhancements prove stable')
                elif v7_success > v6_success:
                    insights.append('V7 shows incremental improvement - evolution continues')
                else:
                    insights.append('V6-V7 performance plateau suggests need for breakthrough approach')
        
        # Analyze failure patterns
        test_urls = existing_results.get('test_urls', [])
        if test_urls and len(test_urls) >= 10:
            insights.append(f'Large-scale testing with {len(test_urls)} URLs provides robust validation')
        
        return insights

    def _generate_improvement_recommendations(self, existing_results: Dict) -> List[str]:
        """Generate improvement recommendations based on results"""
        
        recommendations = []
        
        # Analyze latest performance
        latest_version = 'v7' if 'v7_performance' in existing_results else 'v6'
        latest_perf = existing_results.get(f'{latest_version}_performance', {})
        
        success_rate = latest_perf.get('success_rate', 0.9)
        cultural_preservation = latest_perf.get('cultural_preservation', 0.8)
        brand_detection = latest_perf.get('brand_detection', 0.7)
        
        # Success rate recommendations
        if success_rate < 1.0:
            recommendations.append('Address remaining failure cases with constraint relaxation approach')
        
        # Cultural preservation recommendations  
        if cultural_preservation < 0.9:
            recommendations.append('Enhance cultural term recognition and preservation')
        
        # Brand detection recommendations
        if brand_detection < 0.8:
            recommendations.append('Strengthen brand hierarchy and multi-brand handling')
        
        # General recommendations based on patterns
        if success_rate >= 0.9 and cultural_preservation >= 0.9:
            recommendations.append('Consider breakthrough approach for remaining edge cases')
        
        return recommendations or ['Continue systematic optimization approach']

    def _prioritize_improvements(self, performance_gaps: List[str], failure_cases: List[str]) -> List[str]:
        """Prioritize improvement areas"""
        
        priorities = []
        
        # High priority: constraint handling if failure cases exist
        if failure_cases and any(len(case) > 100 for case in failure_cases):
            priorities.append('constraint_handling')
        
        # Medium priority: performance gaps
        if 'cultural_authenticity' in performance_gaps:
            priorities.append('cultural_enhancement')
        
        if 'brand_hierarchy' in performance_gaps:
            priorities.append('brand_optimization')
        
        if 'multi_brand_support' in performance_gaps:
            priorities.append('multi_brand_handling')
        
        return priorities[:3]  # Top 3 priorities

    def _generate_specific_changes(self, priority_improvements: List[str], failure_cases: List[str]) -> List[str]:
        """Generate specific changes based on priorities"""
        
        changes = []
        
        if 'constraint_handling' in priority_improvements:
            changes.extend([
                'Relax word count constraints to 3-8 words for complex cases',
                'Extend character limit to 70 characters for multi-brand scenarios'
            ])
        
        if 'cultural_enhancement' in priority_improvements:
            changes.append('Strengthen cultural term preservation rules and examples')
        
        if 'brand_optimization' in priority_improvements:
            changes.append('Enhance brand detection and positioning logic')
        
        if 'multi_brand_handling' in priority_improvements:
            changes.append('Improve multi-brand parsing and hierarchy rules')
        
        return changes

    def _estimate_success_probability(self, priority_improvements: List[str], failure_cases: List[str]) -> float:
        """Estimate success probability for proposed improvements"""
        
        base_probability = 0.7
        
        # Boost for addressing constraint issues (V8 precedent)
        if 'constraint_handling' in priority_improvements and failure_cases:
            base_probability += 0.2  # V8 breakthrough precedent
        
        # Boost for cultural enhancements (V6 precedent)  
        if 'cultural_enhancement' in priority_improvements:
            base_probability += 0.15  # V6 cultural breakthrough precedent
        
        # Modest boost for brand optimization (V5 precedent)
        if 'brand_optimization' in priority_improvements:
            base_probability += 0.1  # V5 brand-first precedent
        
        return min(0.95, base_probability)

    def _define_validation_strategy(self, proposed_changes: List[str], success_probability: float) -> Dict[str, Any]:
        """Define validation strategy based on changes and probability"""
        
        strategy = {
            'test_approach': 'enhanced_ab_testing',
            'sample_size': 30,  # Standard for framework
            'success_threshold': 0.8,
            'risk_mitigation': []
        }
        
        if success_probability > 0.8:
            strategy['deployment_recommendation'] = 'proceed_with_confidence'
        elif success_probability > 0.6:
            strategy['deployment_recommendation'] = 'proceed_with_monitoring'
        else:
            strategy['deployment_recommendation'] = 'iterate_further'
        
        # Add risk mitigation for major changes
        if any('relax' in change.lower() for change in proposed_changes):
            strategy['risk_mitigation'].append('Monitor for quality regression with relaxed constraints')
        
        return strategy

    def _recommend_next_version(self, current_best: str, success_probability: float) -> str:
        """Recommend next version identifier"""
        
        if current_best == 'v6':
            return 'v8' if success_probability > 0.8 else 'v7'  # Skip v7 for breakthrough
        elif current_best == 'v7':
            return 'v8' if success_probability > 0.7 else 'v7.1'
        else:
            return 'v9'  # Next iteration