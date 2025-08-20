"""
Iteration Pipeline - Automated improvement cycle orchestration

Orchestrates complete iteration cycles from evaluation to improvement
to validation with breakthrough detection.
"""

from typing import Dict, List, Any, Optional
from .prompt_optimizer import PromptOptimizer
from .weakness_analyzer import WeaknessAnalyzer


class IterationPipeline:
    """Orchestrate automated improvement cycles with breakthrough detection"""
    
    def __init__(self, api_key: str):
        """Initialize pipeline with optimizer and analyzer"""
        self.optimizer = PromptOptimizer(api_key)
        self.analyzer = WeaknessAnalyzer()
        self.api_key = api_key

    def run_iteration_cycle(self, current_state: Dict, target_version: str, iteration_goals: List[str]) -> Dict[str, Any]:
        """
        Run complete iteration cycle from analysis to recommendation
        
        Args:
            current_state: Current prompt performance state
            target_version: Target version identifier (e.g., 'v9')
            iteration_goals: List of goals (e.g., ['solve_constraint_failures'])
            
        Returns:
            Dict with analysis_phase, improvement_phase, validation_phase, recommendation
        """
        
        # Phase 1: Analysis
        analysis_phase = self._run_analysis_phase(current_state)
        
        # Phase 2: Improvement Generation
        improvement_phase = self._run_improvement_phase(analysis_phase, target_version)
        
        # Phase 3: Validation
        validation_phase = self._run_validation_phase(improvement_phase, current_state)
        
        # Generate final recommendation
        recommendation = self._generate_recommendation(analysis_phase, improvement_phase, validation_phase, iteration_goals)
        
        return {
            'analysis_phase': analysis_phase,
            'improvement_phase': improvement_phase,
            'validation_phase': validation_phase,
            'recommendation': recommendation,
            'iteration_metadata': {
                'target_version': target_version,
                'goals': iteration_goals,
                'cycle_complete': True
            }
        }

    def detect_breakthrough_potential(self, breakthrough_scenario: Dict) -> Dict[str, Any]:
        """
        Detect potential breakthrough improvements
        
        Args:
            breakthrough_scenario: Scenario data with current and proposed performance
            
        Returns:
            Dict with breakthrough_probability, breakthrough_indicators, historical_precedent
        """
        
        current_perf = breakthrough_scenario.get('current_performance', {})
        proposed_perf = breakthrough_scenario.get('proposed_improvements', {})
        
        # Calculate breakthrough indicators
        breakthrough_indicators = []
        
        # Success rate improvement
        current_success = current_perf.get('success_rate', 0)
        proposed_success = proposed_perf.get('predicted_success_rate', 0)
        if proposed_success - current_success > 0.15:  # >15% improvement
            breakthrough_indicators.append('significant_success_rate_improvement')
        
        # Failure resolution
        current_failures = current_perf.get('persistent_failures', 0)
        predicted_resolution = proposed_perf.get('predicted_failure_resolution', 0)
        if predicted_resolution >= current_failures * 0.5:  # Resolves 50%+ of failures
            breakthrough_indicators.append('substantial_failure_resolution')
        
        # Constraint breakthrough
        if proposed_perf.get('constraint_relaxation', False):
            breakthrough_indicators.append('constraint_breakthrough')
        
        # Calculate breakthrough probability
        breakthrough_probability = len(breakthrough_indicators) / 4.0  # Max 4 indicators
        
        # Add bonus for complete failure resolution
        if predicted_resolution >= current_failures:
            breakthrough_probability += 0.2
        
        breakthrough_probability = min(1.0, breakthrough_probability)
        
        # Find historical precedent
        historical_precedent = self._find_breakthrough_precedent(breakthrough_indicators)
        
        return {
            'breakthrough_probability': breakthrough_probability,
            'breakthrough_indicators': breakthrough_indicators,
            'historical_precedent': historical_precedent,
            'improvement_magnitude': proposed_success - current_success,
            'failure_resolution_rate': predicted_resolution / max(1, current_failures)
        }

    def assess_regression_risk(self, improvement_proposal: Dict) -> Dict[str, Any]:
        """
        Assess regression risk in improvement proposals
        
        Args:
            improvement_proposal: Proposed changes and predicted impact
            
        Returns:
            Dict with regression_risk, risk_factors, mitigation_strategies
        """
        
        changes = improvement_proposal.get('changes', [])
        predicted_impact = improvement_proposal.get('predicted_impact', {})
        
        risk_factors = []
        regression_risk = 'low'
        
        # Check for performance regressions in predictions
        for metric, value in predicted_impact.items():
            if isinstance(value, (int, float)) and value < 0.8:  # <80% performance
                risk_factors.append(f'{metric}_regression_risk')
                if value < 0.7:  # <70% is high risk
                    regression_risk = 'high'
                elif regression_risk == 'low':
                    regression_risk = 'medium'
        
        # Check for risky change types
        if any('major' in str(change).lower() or 'rewrite' in str(change).lower() for change in changes):
            risk_factors.append('major_change_risk')
            regression_risk = 'high' if regression_risk != 'high' else regression_risk
        
        # Check for multiple simultaneous changes
        if len(changes) > 3:
            risk_factors.append('multiple_change_complexity')
            if regression_risk == 'low':
                regression_risk = 'medium'
        
        # Generate mitigation strategies
        mitigation_strategies = self._generate_mitigation_strategies(risk_factors, regression_risk)
        
        return {
            'regression_risk': regression_risk,
            'risk_factors': risk_factors,
            'mitigation_strategies': mitigation_strategies,
            'risk_score': self._calculate_risk_score(risk_factors, regression_risk)
        }

    def _run_analysis_phase(self, current_state: Dict) -> Dict[str, Any]:
        """Run comprehensive analysis phase"""
        
        performance_metrics = current_state.get('performance_metrics', {})
        known_failures = current_state.get('known_failures', [])
        
        # Analyze weaknesses using mock evaluation results
        weakness_areas = []
        if performance_metrics.get('success_rate', 1.0) < 1.0:
            weakness_areas.extend(['brand_hierarchy', 'cultural_authenticity'])
        
        # Add constraint issues if there are known failures
        if known_failures:
            weakness_areas.extend(['constraint_handling', 'multi_brand_support'])
        
        mock_evaluation_results = {
            'current_prompt_performance': {
                'overall_score': performance_metrics.get('success_rate', 0.9),
                'weakness_areas': weakness_areas,
                'failure_cases': [{'title': failure, 'failure_reason': 'exceeded_constraints', 'suggested_fix': 'relax_word_limits'} 
                                for failure in known_failures]
            }
        }
        
        weakness_analysis = self.optimizer.analyze_weaknesses(mock_evaluation_results)
        
        # Analyze failure patterns
        failure_analysis = self.analyzer.analyze_failure_cases(known_failures)
        
        return {
            'weakness_areas': weakness_analysis['priority_areas'],
            'failure_patterns': failure_analysis,
            'improvement_opportunities': weakness_analysis['improvement_suggestions'],
            'constraint_issues': weakness_analysis['constraint_issues']
        }

    def _run_improvement_phase(self, analysis_phase: Dict, target_version: str) -> Dict[str, Any]:
        """Run improvement generation phase"""
        
        # Create mock current prompt for demonstration
        current_prompt = "Generate SEO slug with 3-6 words, under 60 characters"
        
        # Create weakness analysis structure
        weakness_analysis = {
            'priority_areas': analysis_phase.get('weakness_areas', []),
            'specific_failures': [{'title': 'Sample failure case'}],
            'improvement_suggestions': analysis_phase.get('improvement_opportunities', []),
            'constraint_issues': analysis_phase.get('constraint_issues', [])
        }
        
        improvements = self.optimizer.generate_improvements(current_prompt, weakness_analysis, target_version)
        
        return {
            'proposed_changes': improvements['key_changes'],
            'enhanced_prompt': improvements['enhanced_prompt'],
            'rationale': improvements['rationale'],
            'expected_benefits': improvements['expected_improvements']
        }

    def _run_validation_phase(self, improvement_phase: Dict, current_state: Dict) -> Dict[str, Any]:
        """Run validation phase"""
        
        # Validate improvements
        proposed_improvements = {
            'enhanced_prompt': improvement_phase.get('enhanced_prompt', ''),
            'key_changes': improvement_phase.get('proposed_changes', []),
            'target_cases': [{'title': failure, 'expected_improvement': 'should_now_succeed'} 
                           for failure in current_state.get('known_failures', [])]
        }
        
        validation_result = self.optimizer.validate_improvements(proposed_improvements)
        
        # Assess risk
        risk_assessment = self.assess_regression_risk({
            'changes': improvement_phase.get('proposed_changes', []),
            'predicted_impact': current_state.get('performance_metrics', {})
        })
        
        return {
            'success_prediction': validation_result['validation_score'],
            'likely_improvements': validation_result['likely_successes'],
            'risk_assessment': risk_assessment,
            'confidence': validation_result['confidence_level']
        }

    def _generate_recommendation(self, analysis: Dict, improvement: Dict, validation: Dict, goals: List[str]) -> Dict[str, Any]:
        """Generate final recommendation"""
        
        success_prediction = validation.get('success_prediction', 0)
        confidence = validation.get('confidence', 0)
        risk_level = validation.get('risk_assessment', {}).get('regression_risk', 'medium')
        
        # Decision logic
        if success_prediction > 0.8 and confidence > 0.7 and risk_level in ['low', 'medium']:
            action = 'deploy'
            rationale = 'High success probability with acceptable risk'
        elif success_prediction > 0.6 and confidence > 0.6:
            action = 'test_further'
            rationale = 'Promising but needs additional validation'
        else:
            action = 'iterate'
            rationale = 'Needs more development before deployment'
        
        return {
            'action': action,
            'rationale': rationale,
            'confidence': confidence,
            'success_factors': improvement.get('expected_benefits', []),
            'risk_mitigation': validation.get('risk_assessment', {}).get('mitigation_strategies', [])
        }

    def _find_breakthrough_precedent(self, indicators: List[str]) -> List[str]:
        """Find historical precedent for breakthrough indicators"""
        
        precedents = []
        
        if 'significant_success_rate_improvement' in indicators:
            precedents.append('V6 cultural enhancement breakthrough (+20% success rate)')
        
        if 'substantial_failure_resolution' in indicators:
            precedents.append('V8 constraint relaxation (solved persistent multi-brand failures)')
        
        if 'constraint_breakthrough' in indicators:
            precedents.append('V8 Enhanced Constraints historic breakthrough')
        
        return precedents or ['No direct historical precedent - novel breakthrough potential']

    def _generate_mitigation_strategies(self, risk_factors: List[str], risk_level: str) -> List[str]:
        """Generate risk mitigation strategies"""
        
        strategies = []
        
        if risk_level == 'high':
            strategies.extend([
                'Implement gradual rollout with A/B testing',
                'Maintain rollback capability to current version',
                'Monitor key metrics closely during deployment'
            ])
        
        if 'major_change_risk' in risk_factors:
            strategies.append('Consider phased implementation of major changes')
        
        if 'multiple_change_complexity' in risk_factors:
            strategies.append('Test individual changes separately before combining')
        
        return strategies or ['Standard validation and monitoring procedures']

    def _calculate_risk_score(self, risk_factors: List[str], risk_level: str) -> float:
        """Calculate numerical risk score"""
        
        base_scores = {'low': 0.2, 'medium': 0.5, 'high': 0.8}
        risk_score = base_scores.get(risk_level, 0.5)
        
        # Add factor penalties
        risk_score += len(risk_factors) * 0.1
        
        return min(1.0, risk_score)