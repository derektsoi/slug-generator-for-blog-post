"""
A/B Testing Comparison Logic

Handles comparison of different prompt versions, statistical analysis,
and generation of insights and recommendations.
"""

import statistics
import math
from typing import Dict, List, Any, Optional


class Comparator:
    """
    Compares results from different prompt versions and generates insights.
    
    Provides statistical analysis, ranking, and recommendation generation
    for LLM optimization results.
    """
    
    def __init__(self):
        self.comparison_history = []
        
    def rank_versions(self, results: Dict[str, Dict], primary_metric: str) -> List[str]:
        """
        Rank prompt versions by performance.
        
        Args:
            results: Dictionary with results for each version
            primary_metric: Metric to rank by
            
        Returns:
            List of version identifiers ranked by performance (best first)
        """
        # Filter out versions with errors
        valid_results = {
            version: data for version, data in results.items()
            if 'error' not in data and primary_metric in data
        }
        
        if not valid_results:
            return []
        
        # Sort by primary metric (descending - higher is better)
        ranked = sorted(
            valid_results.keys(),
            key=lambda v: valid_results[v][primary_metric],
            reverse=True
        )
        
        return ranked
    
    def is_statistically_significant(self, baseline_scores: List[float], 
                                   improved_scores: List[float], 
                                   confidence_level: float = 0.95) -> bool:
        """
        Determine if improvement is statistically significant.
        
        Args:
            baseline_scores: List of baseline performance scores
            improved_scores: List of improved performance scores
            confidence_level: Statistical confidence level (default 0.95)
            
        Returns:
            True if improvement is statistically significant
        """
        if len(baseline_scores) < 2 or len(improved_scores) < 2:
            # Need at least 2 samples for statistical test
            return False
        
        try:
            # Simple statistical comparison without scipy
            baseline_mean = statistics.mean(baseline_scores)
            improved_mean = statistics.mean(improved_scores)
            
            baseline_std = statistics.stdev(baseline_scores) if len(baseline_scores) > 1 else 0
            improved_std = statistics.stdev(improved_scores) if len(improved_scores) > 1 else 0
            
            # Calculate effect size (Cohen's d)
            pooled_std = math.sqrt(((len(baseline_scores) - 1) * baseline_std**2 + 
                                  (len(improved_scores) - 1) * improved_std**2) / 
                                 (len(baseline_scores) + len(improved_scores) - 2))
            
            if pooled_std > 0:
                effect_size = (improved_mean - baseline_mean) / pooled_std
                # Consider significant if effect size > 0.5 (medium effect) and improvement > 0
                return effect_size > 0.5 and improved_mean > baseline_mean
            else:
                return improved_mean > baseline_mean
            
        except Exception:
            # Fallback to simple comparison
            baseline_mean = statistics.mean(baseline_scores)
            improved_mean = statistics.mean(improved_scores)
            return improved_mean > baseline_mean
    
    def generate_insights(self, results: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Generate comprehensive insights and recommendations.
        
        Args:
            results: Dictionary with results for each version
            
        Returns:
            Dictionary with insights, recommendations, and analysis
        """
        insights = {
            'summary': self._generate_summary(results),
            'performance_analysis': self._analyze_performance(results),
            'recommendations': self._generate_recommendations(results),
            'statistical_analysis': self._perform_statistical_analysis(results)
        }
        
        # Store for trend analysis
        self.comparison_history.append({
            'results': results,
            'insights': insights,
            'timestamp': None  # Would be set by caller
        })
        
        return insights
    
    def _generate_summary(self, results: Dict[str, Dict]) -> Dict[str, Any]:
        """Generate high-level summary of results"""
        valid_results = {v: d for v, d in results.items() if 'error' not in d}
        failed_results = {v: d for v, d in results.items() if 'error' in d}
        
        if not valid_results:
            return {
                'status': 'failed',
                'message': 'All versions failed',
                'total_versions': len(results),
                'failed_versions': len(failed_results)
            }
        
        # Find best and worst performers
        metric_keys = [k for k in list(valid_results.values())[0].keys() 
                      if isinstance(list(valid_results.values())[0][k], (int, float))]
        
        summary = {
            'status': 'success',
            'total_versions': len(results),
            'successful_versions': len(valid_results),
            'failed_versions': len(failed_results),
            'metrics_available': metric_keys
        }
        
        # Add best/worst for key metrics
        for metric in ['avg_theme_coverage', 'theme_coverage', 'success_rate']:
            if metric in metric_keys:
                best_version = max(valid_results.keys(), 
                                 key=lambda v: valid_results[v].get(metric, 0))
                worst_version = min(valid_results.keys(), 
                                  key=lambda v: valid_results[v].get(metric, 0))
                
                summary[f'best_{metric}'] = {
                    'version': best_version,
                    'value': valid_results[best_version][metric]
                }
                summary[f'worst_{metric}'] = {
                    'version': worst_version,
                    'value': valid_results[worst_version][metric]
                }
                break
        
        return summary
    
    def _analyze_performance(self, results: Dict[str, Dict]) -> Dict[str, Any]:
        """Analyze performance patterns across versions"""
        valid_results = {v: d for v, d in results.items() if 'error' not in d}
        
        if len(valid_results) < 2:
            return {'insufficient_data': True}
        
        analysis = {}
        
        # Analyze each metric
        for metric in ['avg_theme_coverage', 'theme_coverage', 'success_rate', 'avg_duration']:
            if metric in list(valid_results.values())[0]:
                values = [d[metric] for d in valid_results.values()]
                
                analysis[metric] = {
                    'mean': statistics.mean(values),
                    'min': min(values),
                    'max': max(values),
                    'range': max(values) - min(values),
                    'std_dev': statistics.stdev(values) if len(values) > 1 else 0,
                    'coefficient_of_variation': (statistics.stdev(values) / statistics.mean(values)) 
                                              if len(values) > 1 and statistics.mean(values) > 0 else 0
                }
        
        # Performance distribution
        if 'avg_theme_coverage' in analysis or 'theme_coverage' in analysis:
            coverage_metric = 'avg_theme_coverage' if 'avg_theme_coverage' in analysis else 'theme_coverage'
            coverage_values = [d[coverage_metric] for d in valid_results.values()]
            
            analysis['performance_distribution'] = {
                'high_performers': len([v for v in coverage_values if v >= 0.8]),
                'medium_performers': len([v for v in coverage_values if 0.5 <= v < 0.8]),
                'low_performers': len([v for v in coverage_values if v < 0.5]),
                'performance_consistency': 'high' if analysis[coverage_metric]['coefficient_of_variation'] < 0.1 else 
                                         'medium' if analysis[coverage_metric]['coefficient_of_variation'] < 0.3 else 'low'
            }
        
        return analysis
    
    def _generate_recommendations(self, results: Dict[str, Dict]) -> List[str]:
        """Generate actionable recommendations based on results"""
        recommendations = []
        valid_results = {v: d for v, d in results.items() if 'error' not in d}
        
        if not valid_results:
            recommendations.append("❌ All versions failed - review error messages and fix implementation issues")
            return recommendations
        
        # Performance-based recommendations
        coverage_metric = 'avg_theme_coverage' if 'avg_theme_coverage' in list(valid_results.values())[0] else 'theme_coverage'
        
        if coverage_metric in list(valid_results.values())[0]:
            coverage_values = [d[coverage_metric] for d in valid_results.values()]
            max_coverage = max(coverage_values)
            min_coverage = min(coverage_values)
            
            if max_coverage >= 0.8:
                best_version = max(valid_results.keys(), key=lambda v: valid_results[v][coverage_metric])
                recommendations.append(f"✅ Deploy version {best_version} - excellent performance ({max_coverage:.1%} coverage)")
            elif max_coverage >= 0.6:
                recommendations.append(f"⚠️ Best version achieves {max_coverage:.1%} coverage - consider further optimization")
            else:
                recommendations.append(f"🔄 All versions below 60% coverage - fundamental prompt redesign needed")
            
            if max_coverage - min_coverage > 0.2:
                recommendations.append("📊 High performance variance - analyze what makes top versions effective")
            
        # Success rate recommendations
        if 'success_rate' in list(valid_results.values())[0]:
            success_rates = [d['success_rate'] for d in valid_results.values()]
            min_success = min(success_rates)
            
            if min_success < 0.9:
                recommendations.append("⚠️ Some versions have reliability issues - prioritize error handling")
        
        # Duration recommendations  
        if 'avg_duration' in list(valid_results.values())[0]:
            durations = [d['avg_duration'] for d in valid_results.values()]
            max_duration = max(durations)
            min_duration = min(durations)
            
            if max_duration > 10.0:
                recommendations.append("⏱️ Some versions are slow - optimize prompt length or model choice")
            
            if max_duration - min_duration > 5.0:
                recommendations.append("🔧 Large performance variance - investigate optimization opportunities")
        
        # General recommendations
        if len(valid_results) < 3:
            recommendations.append("🧪 Test more prompt versions for better optimization insights")
        
        return recommendations
    
    def _perform_statistical_analysis(self, results: Dict[str, Dict]) -> Dict[str, Any]:
        """Perform statistical analysis of results"""
        valid_results = {v: d for v, d in results.items() if 'error' not in d}
        
        if len(valid_results) < 2:
            return {'insufficient_data': True}
        
        analysis = {}
        
        # Find best and baseline versions
        coverage_metric = 'avg_theme_coverage' if 'avg_theme_coverage' in list(valid_results.values())[0] else 'theme_coverage'
        
        if coverage_metric in list(valid_results.values())[0]:
            ranked_versions = sorted(valid_results.keys(), 
                                   key=lambda v: valid_results[v][coverage_metric], 
                                   reverse=True)
            
            best_version = ranked_versions[0]
            baseline_version = ranked_versions[-1]  # Worst performing as baseline
            
            best_score = valid_results[best_version][coverage_metric]
            baseline_score = valid_results[baseline_version][coverage_metric]
            
            analysis['best_vs_baseline'] = {
                'best_version': best_version,
                'baseline_version': baseline_version,
                'improvement': best_score - baseline_score,
                'improvement_percentage': ((best_score - baseline_score) / baseline_score * 100) 
                                        if baseline_score > 0 else 0,
                'relative_improvement': best_score / baseline_score if baseline_score > 0 else float('inf')
            }
            
            # Effect size (Cohen's d) if we have individual measurements
            # For now, using simplified analysis
            analysis['effect_size'] = 'large' if (best_score - baseline_score) > 0.2 else \
                                    'medium' if (best_score - baseline_score) > 0.1 else 'small'
        
        return analysis