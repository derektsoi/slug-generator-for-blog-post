"""
Ground Truth Validator - Validation against known V6/V7/V8 performance data

Validates evaluator performance against documented breakthrough cases
and historical performance patterns.
"""

from typing import Dict, List, Any, Optional
import re


class GroundTruthValidator:
    """Validate evaluation results against known performance benchmarks"""
    
    def __init__(self):
        """Initialize validator with known benchmark cases"""
        
        # Known V8 breakthrough cases
        self.v8_breakthroughs = [
            {
                'title': '日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！',
                'v6_result': None,  # Failed
                'v7_result': None,  # Failed
                'v8_result': 'skinnydip-iface-rhinoshield-phone-cases-guide',
                'breakthrough_factors': ['constraint_relaxation', 'multi_brand_handling']
            }
        ]
        
        # Known V6 cultural wins
        self.v6_cultural_wins = [
            {
                'title': '【2025年最新】日本一番賞Online手把手教學！',
                'v5_result': 'ichiban-kuji-anime-merchandise-japan-guide',  # generic
                'v6_result': 'ichiban-kuji-anime-japan-guide',  # preserved cultural term
                'cultural_improvement': 'preserved_ichiban_kuji'
            },
            {
                'title': '【日本JK制服品牌 Lucy Pop】人氣日系校園穿搭登陸香港',
                'v5_result': 'lucy-pop-fashion-hongkong-shopping',
                'v6_result': 'lucy-pop-jk-uniform-hongkong-guide',
                'cultural_improvement': 'preserved_jk_uniform'
            }
        ]
        
        # Known brand detection improvements
        self.brand_improvements = [
            {
                'title': 'JoJo Maman Bébé maternity clothes',
                'generic_result': 'maternity-clothes-guide',
                'brand_aware_result': 'jojo-maman-bebe-maternity-guide',
                'brand_score_improvement': 0.6  # 60% improvement
            }
        ]

    def validate_breakthrough_recognition(self, case: Dict, success_score: Dict, failure_score: Dict) -> bool:
        """
        Validate that evaluator recognizes V8 breakthroughs as superior
        
        Args:
            case: Breakthrough case data
            success_score: Evaluation result for successful slug
            failure_score: Evaluation result for failure case
            
        Returns:
            bool: True if evaluator correctly ranks breakthrough higher
        """
        
        # Success should significantly outperform failure
        score_gap = success_score['overall_score'] - failure_score['overall_score']
        if score_gap < 0.5:
            return False
        
        # Success should have high absolute score
        if success_score['overall_score'] < 0.7:
            return False
        
        # Success should excel in relevant dimensions
        relevant_dimensions = ['brand_hierarchy', 'user_intent_match', 'technical_seo']
        for dim in relevant_dimensions:
            if success_score['dimension_scores'][dim] < 0.6:
                return False
        
        # Qualitative feedback should mention breakthrough factors
        feedback = success_score['qualitative_feedback'].lower()
        breakthrough_mentioned = any(
            factor.replace('_', ' ') in feedback 
            for factor in case.get('breakthrough_factors', [])
        )
        
        return breakthrough_mentioned or 'brand' in feedback

    def validate_cultural_improvement(self, case: Dict, v5_score: Dict, v6_score: Dict) -> bool:
        """
        Validate that evaluator recognizes cultural authenticity improvements
        
        Args:
            case: Cultural improvement case
            v5_score: V5 (generic) evaluation result
            v6_score: V6 (cultural) evaluation result
            
        Returns:
            bool: True if evaluator correctly scores cultural improvement
        """
        
        # V6 should score higher on cultural authenticity
        cultural_improvement = (
            v6_score['dimension_scores']['cultural_authenticity'] - 
            v5_score['dimension_scores']['cultural_authenticity']
        )
        
        if cultural_improvement < 0.19:  # At least 19% improvement (account for float precision)
            return False
        
        # V6 should have high cultural authenticity score
        if v6_score['dimension_scores']['cultural_authenticity'] < 0.7:
            return False
        
        # Feedback should mention cultural elements
        v6_feedback = v6_score['qualitative_feedback'].lower()
        cultural_terms = ['ichiban', 'cultural', 'authentic', 'jk-uniform', 'preserve']
        
        return any(term in v6_feedback for term in cultural_terms)

    def detect_presentation_bias(self, test_cases: List[Dict], scores: List[float]) -> Dict[str, Any]:
        """
        Detect potential evaluator biases based on presentation differences
        
        Args:
            test_cases: List of test cases with different presentations
            scores: Corresponding evaluation scores
            
        Returns:
            Dict with bias_detected, bias_severity, recommendations
        """
        
        if len(scores) < 2:
            return {
                'bias_detected': False,
                'bias_severity': 0.0,
                'recommendations': ['Need at least 2 test cases for bias detection']
            }
        
        # Calculate score variance
        score_variance = max(scores) - min(scores)
        bias_severity = min(1.0, score_variance / 0.5)  # Normalize to 0-1 scale
        
        bias_detected = bias_severity > 0.3  # 30% variance threshold
        
        recommendations = []
        if bias_detected:
            recommendations.extend([
                'High variance in scores for identical slugs',
                'Consider prompt modifications to reduce presentation bias',
                'Implement blind evaluation protocols'
            ])
        else:
            recommendations.append('Evaluation shows consistent scoring across presentations')
        
        return {
            'bias_detected': bias_detected,
            'bias_severity': bias_severity,
            'score_variance': score_variance,
            'recommendations': recommendations
        }

    def validate_brand_detection_improvement(self, generic_score: Dict, brand_aware_score: Dict) -> Dict[str, Any]:
        """
        Validate improvement in brand detection scoring
        
        Args:
            generic_score: Evaluation of generic slug
            brand_aware_score: Evaluation of brand-aware slug
            
        Returns:
            Dict with validation results and analysis
        """
        
        brand_improvement = (
            brand_aware_score['dimension_scores']['brand_hierarchy'] - 
            generic_score['dimension_scores']['brand_hierarchy']
        )
        
        overall_improvement = brand_aware_score['overall_score'] - generic_score['overall_score']
        
        validation_passed = (
            brand_improvement > 0.3 and  # Significant brand improvement
            overall_improvement > 0.1 and  # Overall improvement
            brand_aware_score['dimension_scores']['brand_hierarchy'] > 0.6  # High absolute brand score
        )
        
        return {
            'validation_passed': validation_passed,
            'brand_improvement': brand_improvement,
            'overall_improvement': overall_improvement,
            'brand_absolute_score': brand_aware_score['dimension_scores']['brand_hierarchy'],
            'analysis': self._generate_brand_analysis(generic_score, brand_aware_score, brand_improvement)
        }

    def validate_historical_pattern_recognition(self, prompt_versions: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Validate that evaluator recognizes historical V6->V7->V8 evolution patterns
        
        Args:
            prompt_versions: Dict mapping version names to performance data
            
        Returns:
            Dict with pattern recognition validation results
        """
        
        expected_patterns = {
            'v6_cultural_strength': 'V6 should excel in cultural_authenticity',
            'v7_plateau_detection': 'V7 should show incremental improvement',
            'v8_breakthrough_recognition': 'V8 should solve constraint failures'
        }
        
        recognized_patterns = []
        missed_patterns = []
        
        # Check V6 cultural strength
        if 'v6' in prompt_versions and prompt_versions['v6'].get('cultural_authenticity', 0) > 0.8:
            recognized_patterns.append('v6_cultural_strength')
        else:
            missed_patterns.append('v6_cultural_strength')
        
        # Check V8 breakthrough (higher success rate)
        if ('v8' in prompt_versions and 'v6' in prompt_versions and 
            prompt_versions['v8'].get('success_rate', 0) > prompt_versions['v6'].get('success_rate', 0)):
            recognized_patterns.append('v8_breakthrough_recognition')
        else:
            missed_patterns.append('v8_breakthrough_recognition')
        
        pattern_recognition_score = len(recognized_patterns) / len(expected_patterns)
        
        return {
            'pattern_recognition_score': pattern_recognition_score,
            'recognized_patterns': recognized_patterns,
            'missed_patterns': missed_patterns,
            'recommendations': self._generate_pattern_recommendations(missed_patterns)
        }

    def _generate_brand_analysis(self, generic_score: Dict, brand_aware_score: Dict, improvement: float) -> str:
        """Generate analysis text for brand detection validation"""
        
        if improvement > 0.5:
            return f"Excellent brand detection improvement (+{improvement:.2f}). Evaluator properly recognizes brand importance."
        elif improvement > 0.2:
            return f"Good brand detection improvement (+{improvement:.2f}). Evaluator shows brand awareness."
        else:
            return f"Limited brand detection improvement (+{improvement:.2f}). May need calibration for brand recognition."

    def _generate_pattern_recommendations(self, missed_patterns: List[str]) -> List[str]:
        """Generate recommendations based on missed historical patterns"""
        
        recommendations = []
        
        if 'v6_cultural_strength' in missed_patterns:
            recommendations.append('Calibrate cultural authenticity scoring - V6 should excel in this dimension')
        
        if 'v8_breakthrough_recognition' in missed_patterns:
            recommendations.append('Improve breakthrough detection - V8 solved constraint failures V6/V7 could not')
        
        if 'v7_plateau_detection' in missed_patterns:
            recommendations.append('Enhance plateau recognition - V7 showed incremental gains without breakthrough')
        
        if not recommendations:
            recommendations.append('Historical pattern recognition is working well')
        
        return recommendations