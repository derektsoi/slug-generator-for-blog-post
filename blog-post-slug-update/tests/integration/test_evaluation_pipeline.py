"""
Integration Tests for LLM-Powered Evaluation Pipeline

Tests the end-to-end evaluation and improvement system.
These tests should FAIL initially to ensure TDD approach works.
"""

import pytest
import json
import tempfile
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from evaluation.improvement.prompt_optimizer import PromptOptimizer
from evaluation.improvement.weakness_analyzer import WeaknessAnalyzer  
from evaluation.improvement.iteration_pipeline import IterationPipeline
from evaluation.integration.ab_testing_bridge import ABTestingBridge


class TestPromptOptimizer:
    """Test LLM-driven prompt enhancement system"""
    
    def setup_method(self):
        self.optimizer = PromptOptimizer(api_key="test-key")
        
        # Mock evaluation results showing weaknesses
        self.mock_evaluation_results = {
            'current_prompt_performance': {
                'overall_score': 0.72,
                'weakness_areas': ['brand_hierarchy', 'cultural_authenticity'],
                'failure_cases': [
                    {
                        'title': '日韓台7大手機殼品牌推介',
                        'failure_reason': 'exceeded_constraints',
                        'suggested_fix': 'relax_word_limits'
                    }
                ]
            },
            'benchmark_comparisons': {
                'v6_vs_v7': {
                    'winner': 'v6',
                    'key_differences': ['cultural_preservation', 'constraint_handling']
                }
            }
        }
    
    def test_analyze_prompt_weaknesses(self):
        """Test identification of specific prompt improvement areas"""
        
        weaknesses = self.optimizer.analyze_weaknesses(self.mock_evaluation_results)
        
        assert 'priority_areas' in weaknesses
        assert 'specific_failures' in weaknesses
        assert 'improvement_suggestions' in weaknesses
        assert 'constraint_issues' in weaknesses
        
        # Should identify brand hierarchy and cultural authenticity as priorities
        priority_areas = weaknesses['priority_areas']
        assert 'brand_hierarchy' in priority_areas
        assert 'cultural_authenticity' in priority_areas
        
        # Should suggest constraint relaxation for failure case
        suggestions = weaknesses['improvement_suggestions']
        assert any('constraint' in str(suggestion).lower() for suggestion in suggestions)
        assert any('word' in str(suggestion).lower() or 'limit' in str(suggestion).lower() 
                  for suggestion in suggestions)

    def test_generate_prompt_improvements(self):
        """Test generation of specific prompt enhancement recommendations"""
        
        improvements = self.optimizer.generate_improvements(
            current_prompt="Generate SEO slug with 3-6 words, under 60 characters",
            weakness_analysis=self.mock_evaluation_results,
            target_version="v9"
        )
        
        assert 'enhanced_prompt' in improvements
        assert 'key_changes' in improvements
        assert 'rationale' in improvements
        assert 'expected_improvements' in improvements
        
        # Enhanced prompt should address constraint issues
        enhanced_prompt = improvements['enhanced_prompt']
        assert len(enhanced_prompt) > 100  # Should be detailed
        
        # Should mention relaxed constraints
        key_changes = improvements['key_changes']
        assert any('constraint' in change.lower() for change in key_changes)
        
        # Should target identified weaknesses  
        rationale = improvements['rationale']
        assert 'brand' in rationale.lower() or 'cultural' in rationale.lower()

    def test_validate_improvement_suggestions(self):
        """Test validation of proposed improvements against known cases"""
        
        proposed_improvements = {
            'enhanced_prompt': "Generate SEO slug with 3-8 words, under 70 characters, preserve cultural terms",
            'key_changes': ['relaxed_word_limit', 'relaxed_char_limit', 'cultural_emphasis'],
            'target_cases': [
                {
                    'title': '日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！',
                    'expected_improvement': 'should_now_succeed'
                }
            ]
        }
        
        validation = self.optimizer.validate_improvements(proposed_improvements)
        
        assert 'validation_score' in validation
        assert 'likely_successes' in validation
        assert 'potential_regressions' in validation
        assert 'confidence_level' in validation
        
        # Should predict success for V8 breakthrough case
        assert validation['validation_score'] > 0.7
        assert validation['confidence_level'] > 0.6


class TestWeaknessAnalyzer:
    """Test systematic analysis of prompt failure patterns"""
    
    def setup_method(self):
        self.analyzer = WeaknessAnalyzer()
        
        # Mock historical performance data
        self.historical_data = {
            'v6_performance': {
                'success_rate': 1.0,
                'cultural_preservation': 1.0,
                'brand_detection': 0.66,
                'failure_cases': []
            },
            'v7_performance': {
                'success_rate': 0.9,
                'cultural_preservation': 0.95,
                'brand_detection': 0.7,
                'failure_cases': [
                    '日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！'
                ]
            },
            'v8_performance': {
                'success_rate': 1.0,
                'cultural_preservation': 1.0,
                'brand_detection': 0.8,
                'failure_cases': []
            }
        }
    
    def test_identify_performance_patterns(self):
        """Test identification of performance evolution patterns"""
        
        patterns = self.analyzer.identify_patterns(self.historical_data)
        
        assert 'evolution_trend' in patterns
        assert 'breakthrough_points' in patterns  
        assert 'plateau_periods' in patterns
        assert 'regression_risks' in patterns
        
        # Should identify V8 as breakthrough
        breakthroughs = patterns['breakthrough_points']
        assert any('v8' in str(breakthrough).lower() for breakthrough in breakthroughs)
        
        # Should identify V7 plateau
        plateaus = patterns['plateau_periods']
        assert any('v7' in str(plateau).lower() for plateau in plateaus)

    def test_analyze_failure_case_patterns(self):
        """Test analysis of specific failure case characteristics"""
        
        failure_analysis = self.analyzer.analyze_failure_cases([
            '日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！',
            'JoJo Maman Bébé premium maternity wear collection detailed buying guide',
            'Complex multi-brand electronics comparison with detailed specifications'
        ])
        
        assert 'common_characteristics' in failure_analysis
        assert 'failure_categories' in failure_analysis
        assert 'root_causes' in failure_analysis
        assert 'solution_patterns' in failure_analysis
        
        # Should identify length/complexity patterns
        characteristics = failure_analysis['common_characteristics']
        assert any('length' in char.lower() or 'complex' in char.lower() 
                  for char in characteristics)
        
        # Should suggest constraint solutions
        solutions = failure_analysis['solution_patterns']
        assert any('constraint' in str(solution).lower() for solution in solutions)

    def test_predict_improvement_impact(self):
        """Test prediction of improvement strategy effectiveness"""
        
        improvement_strategy = {
            'changes': ['relax_word_limits', 'relax_char_limits', 'enhance_cultural_awareness'],
            'target_failures': [
                '日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！'
            ]
        }
        
        impact_prediction = self.analyzer.predict_impact(
            improvement_strategy, 
            self.historical_data
        )
        
        assert 'success_probability' in impact_prediction
        assert 'expected_metrics' in impact_prediction
        assert 'risk_assessment' in impact_prediction
        assert 'similar_cases' in impact_prediction
        
        # Should predict high success for constraint relaxation
        assert impact_prediction['success_probability'] > 0.7
        
        # Should predict metric improvements
        expected_metrics = impact_prediction['expected_metrics']
        assert 'success_rate' in expected_metrics
        assert expected_metrics['success_rate'] >= 0.9


class TestIterationPipeline:
    """Test automated improvement cycle orchestration"""
    
    def setup_method(self):
        self.pipeline = IterationPipeline(api_key="test-key")
        
    def test_full_iteration_cycle(self):
        """Test complete iteration from evaluation to improvement to validation"""
        
        # Mock current state
        current_state = {
            'prompt_version': 'v7',
            'performance_metrics': {
                'success_rate': 0.9,
                'cultural_preservation': 0.95,
                'brand_detection': 0.7
            },
            'known_failures': [
                '日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！'
            ]
        }
        
        # Run iteration cycle
        iteration_result = self.pipeline.run_iteration_cycle(
            current_state=current_state,
            target_version='v9',
            iteration_goals=['solve_constraint_failures', 'maintain_cultural_awareness']
        )
        
        assert 'analysis_phase' in iteration_result
        assert 'improvement_phase' in iteration_result
        assert 'validation_phase' in iteration_result
        assert 'recommendation' in iteration_result
        
        # Analysis should identify constraint issues
        analysis = iteration_result['analysis_phase']
        assert 'weakness_areas' in analysis
        assert any('constraint' in str(weakness).lower() 
                  for weakness in analysis['weakness_areas'])
        
        # Improvement should propose enhancements
        improvement = iteration_result['improvement_phase']
        assert 'proposed_changes' in improvement
        assert 'enhanced_prompt' in improvement
        
        # Validation should assess viability  
        validation = iteration_result['validation_phase']
        assert 'success_prediction' in validation
        assert 'risk_assessment' in validation
        
        # Should recommend deployment or further iteration
        recommendation = iteration_result['recommendation']
        assert 'action' in recommendation  # 'deploy' or 'iterate'
        assert 'confidence' in recommendation

    def test_breakthrough_detection(self):
        """Test detection of potential breakthrough improvements"""
        
        # Test with V8-like breakthrough scenario
        breakthrough_scenario = {
            'current_performance': {
                'success_rate': 0.9,
                'persistent_failures': 3
            },
            'proposed_improvements': {
                'constraint_relaxation': True,
                'predicted_success_rate': 1.0,
                'predicted_failure_resolution': 3
            }
        }
        
        breakthrough_analysis = self.pipeline.detect_breakthrough_potential(breakthrough_scenario)
        
        assert 'breakthrough_probability' in breakthrough_analysis
        assert 'breakthrough_indicators' in breakthrough_analysis
        assert 'historical_precedent' in breakthrough_analysis
        
        # Should recognize high breakthrough potential
        assert breakthrough_analysis['breakthrough_probability'] > 0.8
        
        # Should identify failure resolution as key indicator
        indicators = breakthrough_analysis['breakthrough_indicators']
        assert any('failure' in str(indicator).lower() 
                  for indicator in indicators)

    def test_regression_prevention(self):
        """Test prevention of performance regressions during improvement"""
        
        improvement_proposal = {
            'changes': ['major_prompt_rewrite', 'new_scoring_system'],
            'predicted_impact': {
                'success_rate': 0.95,
                'cultural_preservation': 0.8,  # Potential regression
                'brand_detection': 0.85
            }
        }
        
        regression_analysis = self.pipeline.assess_regression_risk(improvement_proposal)
        
        assert 'regression_risk' in regression_analysis
        assert 'risk_factors' in regression_analysis
        assert 'mitigation_strategies' in regression_analysis
        
        # Should detect cultural preservation regression risk
        risk_factors = regression_analysis['risk_factors']
        assert any('cultural' in str(factor).lower() 
                  for factor in risk_factors)
        
        # Should suggest mitigation
        mitigations = regression_analysis['mitigation_strategies']
        assert len(mitigations) > 0


class TestABTestingBridge:
    """Test integration with existing A/B testing framework"""
    
    def setup_method(self):
        self.bridge = ABTestingBridge()
    
    def test_integration_with_existing_framework(self):
        """Test seamless integration with current A/B testing system"""
        
        # Mock existing framework results
        existing_results = {
            'v6_performance': {'success_rate': 1.0, 'theme_coverage': 0.18},
            'v7_performance': {'success_rate': 0.9, 'theme_coverage': 0.16},
            'test_urls': ['url1', 'url2', 'url3']
        }
        
        # Enhance with LLM evaluation
        enhanced_results = self.bridge.enhance_existing_results(
            existing_results,
            llm_evaluation=True
        )
        
        assert 'llm_enhanced_scores' in enhanced_results
        assert 'qualitative_insights' in enhanced_results
        assert 'improvement_recommendations' in enhanced_results
        
        # Should maintain backward compatibility
        assert enhanced_results['v6_performance']['success_rate'] == 1.0
        assert enhanced_results['v7_performance']['success_rate'] == 0.9
        
        # Should add LLM insights
        llm_scores = enhanced_results['llm_enhanced_scores']
        assert 'v6_llm_score' in llm_scores
        assert 'v7_llm_score' in llm_scores

    def test_automated_improvement_suggestions(self):
        """Test generation of automated improvement suggestions for next prompt version"""
        
        comparison_data = {
            'current_best': 'v6',
            'performance_gaps': ['constraint_handling', 'multi_brand_support'],
            'failure_cases': [
                '日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！'
            ]
        }
        
        suggestions = self.bridge.generate_next_version_suggestions(comparison_data)
        
        assert 'priority_improvements' in suggestions
        assert 'proposed_changes' in suggestions
        assert 'success_probability' in suggestions
        assert 'validation_strategy' in suggestions
        
        # Should prioritize constraint handling
        priorities = suggestions['priority_improvements']
        assert any('constraint' in str(priority).lower() 
                  for priority in priorities)
        
        # Should propose specific changes
        changes = suggestions['proposed_changes']
        assert len(changes) >= 2
        
        # Should predict success probability
        assert 0.5 <= suggestions['success_probability'] <= 1.0


if __name__ == "__main__":
    # Run tests to verify they fail initially  
    pytest.main([__file__, "-v", "--tb=short"])