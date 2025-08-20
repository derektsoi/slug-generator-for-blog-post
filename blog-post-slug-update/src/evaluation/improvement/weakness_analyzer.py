"""
Weakness Analyzer - Systematic analysis of prompt failure patterns

Identifies performance patterns and predicts improvement impacts
based on historical data.
"""

from typing import Dict, List, Any, Optional
import statistics


class WeaknessAnalyzer:
    """Analyze failure patterns and predict improvement impacts"""
    
    def __init__(self):
        """Initialize analyzer with historical pattern knowledge"""
        
        # Known improvement patterns from V1-V8 evolution
        self.improvement_patterns = {
            'constraint_relaxation': {
                'success_indicators': ['multi_brand_titles', 'long_descriptions', 'special_characters'],
                'historical_impact': 0.33,  # V8 breakthrough solved 33% of persistent failures
                'risk_level': 0.2
            },
            'cultural_enhancement': {
                'success_indicators': ['asian_terms', 'brand_compounds', 'cultural_context'],
                'historical_impact': 0.42,  # V6 cultural breakthrough (+42% preservation)
                'risk_level': 0.1
            },
            'brand_prioritization': {
                'success_indicators': ['brand_names', 'compound_brands', 'multi_brand'],
                'historical_impact': 0.25,  # V5 brand-first (+25% brand detection)
                'risk_level': 0.15
            }
        }

    def identify_patterns(self, historical_data: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Identify performance evolution patterns from historical data
        
        Args:
            historical_data: Dict mapping versions to performance metrics
            
        Returns:
            Dict with evolution_trend, breakthrough_points, plateau_periods, regression_risks
        """
        
        versions = sorted(historical_data.keys())
        success_rates = [historical_data[v].get('success_rate', 0) for v in versions]
        
        # Identify evolution trend
        if len(success_rates) >= 2:
            trend_slope = (success_rates[-1] - success_rates[0]) / max(1, len(success_rates) - 1)
            if trend_slope > 0.1:
                evolution_trend = 'improving'
            elif trend_slope < -0.05:
                evolution_trend = 'declining'
            else:
                evolution_trend = 'stable'
        else:
            evolution_trend = 'insufficient_data'
        
        # Identify breakthrough points (large improvements)
        breakthrough_points = []
        for i in range(1, len(versions)):
            prev_rate = success_rates[i-1]
            curr_rate = success_rates[i]
            if curr_rate - prev_rate > 0.15:  # 15%+ improvement
                breakthrough_points.append({
                    'version': versions[i],
                    'improvement': curr_rate - prev_rate,
                    'previous_version': versions[i-1]
                })
        
        # Identify plateau periods (minimal change)
        plateau_periods = []
        for i in range(1, len(versions)):
            prev_rate = success_rates[i-1]
            curr_rate = success_rates[i]
            if abs(curr_rate - prev_rate) < 0.05:  # <5% change
                plateau_periods.append({
                    'versions': [versions[i-1], versions[i]],
                    'performance_range': [min(prev_rate, curr_rate), max(prev_rate, curr_rate)]
                })
        
        # Assess regression risks
        regression_risks = []
        if len(success_rates) >= 3:
            recent_trend = success_rates[-1] - success_rates[-2]
            if recent_trend < -0.05:
                regression_risks.append('Recent performance decline detected')
        
        return {
            'evolution_trend': evolution_trend,
            'breakthrough_points': breakthrough_points,
            'plateau_periods': plateau_periods,
            'regression_risks': regression_risks,
            'performance_trajectory': list(zip(versions, success_rates))
        }

    def analyze_failure_cases(self, failure_cases: List[str]) -> Dict[str, Any]:
        """
        Analyze specific failure case characteristics
        
        Args:
            failure_cases: List of titles that failed to generate slugs
            
        Returns:
            Dict with common_characteristics, failure_categories, root_causes, solution_patterns
        """
        
        if not failure_cases:
            return {
                'common_characteristics': [],
                'failure_categories': [],
                'root_causes': [],
                'solution_patterns': []
            }
        
        # Analyze common characteristics
        characteristics = []
        
        # Length analysis
        lengths = [len(case) for case in failure_cases]
        avg_length = statistics.mean(lengths) if lengths else 0
        if avg_length > 100:
            characteristics.append('long_titles')
        
        word_counts = [len(case.split()) for case in failure_cases]
        avg_words = statistics.mean(word_counts) if word_counts else 0
        if avg_words > 15:
            characteristics.append('high_word_count')
        
        # Special character analysis
        special_char_count = sum(1 for case in failure_cases if any(char in case for char in ['/', '&', '！', '？']))
        if special_char_count > len(failure_cases) * 0.5:
            characteristics.append('frequent_special_characters')
        
        # Multi-brand analysis  
        multi_brand_count = sum(1 for case in failure_cases if '/' in case or '&' in case)
        if multi_brand_count > 0:
            characteristics.append('multi_brand_complexity')
        
        # Categorize failure types
        failure_categories = self._categorize_failures(failure_cases)
        
        # Identify root causes
        root_causes = self._identify_root_causes(characteristics, failure_categories)
        
        # Suggest solution patterns
        solution_patterns = self._suggest_solution_patterns(root_causes, characteristics)
        
        return {
            'common_characteristics': characteristics,
            'failure_categories': failure_categories,
            'root_causes': root_causes,
            'solution_patterns': solution_patterns,
            'failure_count': len(failure_cases),
            'avg_title_length': avg_length,
            'avg_word_count': avg_words
        }

    def predict_impact(self, improvement_strategy: Dict, historical_data: Dict) -> Dict[str, Any]:
        """
        Predict impact of improvement strategy based on historical patterns
        
        Args:
            improvement_strategy: Dict with changes and target_failures
            historical_data: Historical performance data
            
        Returns:
            Dict with success_probability, expected_metrics, risk_assessment, similar_cases
        """
        
        changes = improvement_strategy.get('changes', [])
        target_failures = improvement_strategy.get('target_failures', [])
        
        # Calculate success probability based on historical patterns
        success_probability = self._calculate_success_probability(changes, target_failures)
        
        # Predict expected metrics
        current_metrics = self._extract_current_metrics(historical_data)
        expected_metrics = self._predict_metrics(current_metrics, changes)
        
        # Assess risks
        risk_assessment = self._assess_improvement_risks(changes, historical_data)
        
        # Find similar cases
        similar_cases = self._find_similar_cases(changes, historical_data)
        
        return {
            'success_probability': success_probability,
            'expected_metrics': expected_metrics,
            'risk_assessment': risk_assessment,
            'similar_cases': similar_cases,
            'confidence_level': self._calculate_prediction_confidence(changes, historical_data)
        }

    def _categorize_failures(self, failure_cases: List[str]) -> List[str]:
        """Categorize failure cases by type"""
        
        categories = []
        
        constraint_failures = sum(1 for case in failure_cases if len(case) > 100 or len(case.split()) > 20)
        if constraint_failures > 0:
            categories.append('constraint_violations')
        
        complexity_failures = sum(1 for case in failure_cases if '/' in case or '&' in case)
        if complexity_failures > 0:
            categories.append('complexity_overload')
        
        multi_language_failures = sum(1 for case in failure_cases 
                                    if any('\u4e00' <= char <= '\u9fff' for char in case) and
                                       any('a' <= char.lower() <= 'z' for char in case))
        if multi_language_failures > 0:
            categories.append('multi_language_complexity')
        
        return categories

    def _identify_root_causes(self, characteristics: List[str], categories: List[str]) -> List[str]:
        """Identify root causes from characteristics and categories"""
        
        causes = []
        
        if 'long_titles' in characteristics and 'constraint_violations' in categories:
            causes.append('word_count_constraints_too_strict')
        
        if 'frequent_special_characters' in characteristics:
            causes.append('special_character_handling_insufficient')
        
        if 'multi_brand_complexity' in characteristics:
            causes.append('multi_brand_parsing_limitations')
        
        if 'multi_language_complexity' in categories:
            causes.append('cross_language_processing_gaps')
        
        return causes or ['general_complexity_handling']

    def _suggest_solution_patterns(self, root_causes: List[str], characteristics: List[str]) -> List[str]:
        """Suggest solution patterns based on analysis"""
        
        solutions = []
        
        if 'word_count_constraints_too_strict' in root_causes:
            solutions.append('relax_word_count_constraints')
        
        if 'multi_brand_parsing_limitations' in root_causes:
            solutions.append('enhance_multi_brand_handling')
        
        if 'special_character_handling_insufficient' in root_causes:
            solutions.append('improve_special_character_normalization')
        
        if 'cross_language_processing_gaps' in root_causes:
            solutions.append('strengthen_cultural_awareness')
        
        return solutions or ['general_robustness_improvements']

    def _calculate_success_probability(self, changes: List[str], target_failures: List[str]) -> float:
        """Calculate success probability based on changes and historical patterns"""
        
        base_probability = 0.6  # Conservative baseline
        
        for change in changes:
            for pattern_name, pattern_data in self.improvement_patterns.items():
                if pattern_name.replace('_', ' ') in change.lower().replace('_', ' '):
                    base_probability += pattern_data['historical_impact'] * 0.5
        
        # Adjust based on target failure complexity
        if target_failures:
            avg_failure_length = sum(len(f) for f in target_failures) / len(target_failures)
            if avg_failure_length > 100:  # Complex cases
                base_probability *= 0.8  # Reduce confidence for complex cases
        
        return min(0.95, base_probability)

    def _extract_current_metrics(self, historical_data: Dict) -> Dict[str, float]:
        """Extract current performance metrics"""
        
        if not historical_data:
            return {'success_rate': 0.8, 'cultural_preservation': 0.7, 'brand_detection': 0.6}
        
        latest_version = max(historical_data.keys()) if historical_data else 'v6'
        latest_data = historical_data.get(latest_version, {})
        
        return {
            'success_rate': latest_data.get('success_rate', 0.8),
            'cultural_preservation': latest_data.get('cultural_preservation', 0.7),
            'brand_detection': latest_data.get('brand_detection', 0.6)
        }

    def _predict_metrics(self, current_metrics: Dict, changes: List[str]) -> Dict[str, float]:
        """Predict expected metrics after improvements"""
        
        predicted = current_metrics.copy()
        
        for change in changes:
            if 'constraint' in change.lower():
                predicted['success_rate'] = min(1.0, predicted['success_rate'] + 0.1)
            if 'cultural' in change.lower():
                predicted['cultural_preservation'] = min(1.0, predicted['cultural_preservation'] + 0.15)
            if 'brand' in change.lower():
                predicted['brand_detection'] = min(1.0, predicted['brand_detection'] + 0.1)
        
        return predicted

    def _assess_improvement_risks(self, changes: List[str], historical_data: Dict) -> Dict[str, Any]:
        """Assess risks of proposed improvements"""
        
        risk_level = 'low'
        risk_factors = []
        
        if any('rewrite' in change.lower() for change in changes):
            risk_level = 'high'
            risk_factors.append('Major prompt rewrite carries regression risk')
        
        if len(changes) > 4:
            risk_level = 'medium' if risk_level == 'low' else risk_level
            risk_factors.append('Multiple simultaneous changes increase unpredictability')
        
        return {
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'mitigation_recommendations': self._generate_risk_mitigations(risk_factors)
        }

    def _find_similar_cases(self, changes: List[str], historical_data: Dict) -> List[str]:
        """Find similar improvement cases from history"""
        
        similar_cases = []
        
        if 'constraint' in ' '.join(changes).lower():
            similar_cases.append('V8 constraint relaxation breakthrough')
        
        if 'cultural' in ' '.join(changes).lower():
            similar_cases.append('V6 cultural awareness enhancement')
        
        if 'brand' in ' '.join(changes).lower():
            similar_cases.append('V5 brand-first optimization')
        
        return similar_cases

    def _calculate_prediction_confidence(self, changes: List[str], historical_data: Dict) -> float:
        """Calculate confidence level in predictions"""
        
        base_confidence = 0.7
        
        # Higher confidence if we have historical precedent
        if len(historical_data) >= 3:
            base_confidence += 0.1
        
        # Lower confidence for novel approaches
        if any('novel' in change.lower() or 'experimental' in change.lower() for change in changes):
            base_confidence -= 0.2
        
        return max(0.3, min(0.95, base_confidence))

    def _generate_risk_mitigations(self, risk_factors: List[str]) -> List[str]:
        """Generate risk mitigation recommendations"""
        
        mitigations = []
        
        if any('rewrite' in factor.lower() for factor in risk_factors):
            mitigations.append('Implement gradual rollout with A/B testing')
        
        if any('multiple' in factor.lower() for factor in risk_factors):
            mitigations.append('Consider phased implementation of changes')
        
        return mitigations or ['Standard testing and validation procedures']