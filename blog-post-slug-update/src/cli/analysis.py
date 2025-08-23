"""
Statistical Analysis and Evaluation Logic for CLI Tools

Shared analytical functionality for comparing and analyzing evaluation results
across different prompt versions and configurations.
"""

import statistics
from typing import Dict, List, Any, Tuple, Optional
from functools import lru_cache
import time


class StatisticalAnalyzer:
    """Statistical analysis tools for evaluation comparisons"""
    
    @lru_cache(maxsize=128)
    def _calculate_stats_cached(self, values_tuple: tuple) -> Dict[str, float]:
        """Cached version of basic statistics calculation"""
        values = list(values_tuple)
        if not values:
            return {'count': 0, 'mean': 0, 'stdev': 0, 'min': 0, 'max': 0}
        
        return {
            'count': len(values),
            'mean': statistics.mean(values),
            'stdev': statistics.stdev(values) if len(values) > 1 else 0,
            'min': min(values),
            'max': max(values)
        }
    
    def calculate_basic_statistics(self, values: List[float]) -> Dict[str, float]:
        """Calculate basic statistical measures with caching"""
        return self._calculate_stats_cached(tuple(values))
    
    def calculate_effect_size(self, values_a: List[float], values_b: List[float]) -> Dict[str, Any]:
        """Calculate Cohen's d effect size and interpretation"""
        if not values_a or not values_b:
            return {'error': 'Insufficient data for effect size calculation'}
        
        try:
            mean_a = statistics.mean(values_a)
            mean_b = statistics.mean(values_b)
            stdev_a = statistics.stdev(values_a) if len(values_a) > 1 else 0
            stdev_b = statistics.stdev(values_b) if len(values_b) > 1 else 0
            
            mean_difference = abs(mean_a - mean_b)
            pooled_stdev = ((stdev_a ** 2 + stdev_b ** 2) / 2) ** 0.5
            
            effect_size = mean_difference / pooled_stdev if pooled_stdev > 0 else 0
            confidence_interval = 1.96 * pooled_stdev  # 95% CI approximation
            
            return {
                'mean_difference': mean_difference,
                'effect_size': effect_size,
                'confidence_interval': confidence_interval,
                'sample_size_a': len(values_a),
                'sample_size_b': len(values_b),
                'significance_note': self._interpret_effect_size(effect_size),
                'pooled_stdev': pooled_stdev
            }
        except Exception as e:
            return {'error': f'Statistical analysis failed: {str(e)}'}
    
    def _interpret_effect_size(self, effect_size: float) -> str:
        """Interpret Cohen's d effect size"""
        if effect_size < 0.2:
            return "No significant difference"
        elif effect_size < 0.5:
            return "Small effect size"
        elif effect_size < 0.8:
            return "Medium effect size"
        else:
            return "Large effect size"


class PerformanceAnalyzer:
    """Performance analysis tools for evaluation results"""
    
    def __init__(self, scoring_dimensions: List[str]):
        self.scoring_dimensions = scoring_dimensions
    
    def calculate_averages(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate average scores across multiple evaluation results"""
        if not results:
            return {}
        
        total_scores = {dim: 0.0 for dim in self.scoring_dimensions}
        overall_total = 0.0
        count = len(results)
        
        for result in results:
            eval_data = result.get('evaluation', {})
            
            # Accumulate dimension scores
            dimension_scores = eval_data.get('dimension_scores', {})
            for dim in self.scoring_dimensions:
                if dim in dimension_scores:
                    total_scores[dim] += dimension_scores[dim]
            
            # Accumulate overall score
            overall_total += eval_data.get('overall_score', 0.0)
        
        avg_scores = {dim: total_scores[dim] / count for dim in total_scores}
        avg_overall = overall_total / count
        
        return {
            'avg_overall_score': avg_overall,
            'avg_dimension_scores': avg_scores,
            'count': count
        }
    
    def find_performance_winner(self, results_a: Dict[str, Any], results_b: Dict[str, Any], 
                               version_a: str, version_b: str) -> Dict[str, Any]:
        """Determine performance winner between two result sets"""
        score_a = results_a.get('avg_overall_score', 0)
        score_b = results_b.get('avg_overall_score', 0)
        
        if score_a > score_b:
            winner = version_a
            winner_score = score_a
            runner_up = version_b
            runner_up_score = score_b
        else:
            winner = version_b
            winner_score = score_b
            runner_up = version_a
            runner_up_score = score_a
        
        score_difference = winner_score - runner_up_score
        improvement_percentage = (score_difference / runner_up_score) * 100 if runner_up_score > 0 else 0
        
        return {
            'winner': winner,
            'winner_score': winner_score,
            'runner_up': runner_up,
            'runner_up_score': runner_up_score,
            'score_difference': score_difference,
            'improvement_percentage': improvement_percentage
        }
    
    def analyze_dimension_comparison(self, results_a: Dict[str, Any], results_b: Dict[str, Any],
                                   version_a: str, version_b: str) -> Dict[str, Any]:
        """Compare performance across individual dimensions"""
        scores_a = results_a.get('avg_dimension_scores', {})
        scores_b = results_b.get('avg_dimension_scores', {})
        
        dimension_comparison = {}
        
        for dim in self.scoring_dimensions:
            score_a = scores_a.get(dim, 0)
            score_b = scores_b.get(dim, 0)
            
            if score_a > score_b:
                dim_winner = version_a
                difference = score_a - score_b
            else:
                dim_winner = version_b
                difference = score_b - score_a
            
            dimension_comparison[dim] = {
                f'{version_a}_score': score_a,
                f'{version_b}_score': score_b,
                'winner': dim_winner,
                'difference': difference
            }
        
        return dimension_comparison
    
    def generate_insights(self, dimension_comparison: Dict[str, Any], score_difference: float,
                         version_a: str, version_b: str) -> List[str]:
        """Generate actionable insights based on performance analysis"""
        insights = []
        
        # Overall performance insight
        if score_difference < 0.05:
            insights.append("Performance difference is minimal - either version is suitable")
        elif score_difference < 0.10:
            insights.append("Small performance difference - consider other factors like consistency")
        else:
            insights.append(f"Significant performance difference ({score_difference:.3f}) - prefer the winning version")
        
        # Dimension-specific insights
        strong_dimensions_a = []
        strong_dimensions_b = []
        
        for dim, comparison in dimension_comparison.items():
            if comparison['winner'] == version_a and comparison['difference'] > 0.05:
                strong_dimensions_a.append(dim.replace('_', ' '))
            elif comparison['winner'] == version_b and comparison['difference'] > 0.05:
                strong_dimensions_b.append(dim.replace('_', ' '))
        
        if strong_dimensions_a:
            insights.append(f"{version_a} excels in: {', '.join(strong_dimensions_a)}")
        
        if strong_dimensions_b:
            insights.append(f"{version_b} excels in: {', '.join(strong_dimensions_b)}")
        
        return insights


class PerformanceMonitor:
    """Monitor and optimize performance of analysis operations"""
    
    def __init__(self):
        self.timers = {}
        self.call_counts = {}
    
    def time_operation(self, operation_name: str):
        """Decorator to time operations"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                
                if operation_name not in self.timers:
                    self.timers[operation_name] = []
                self.timers[operation_name].append(elapsed)
                
                self.call_counts[operation_name] = self.call_counts.get(operation_name, 0) + 1
                return result
            return wrapper
        return decorator
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = {}
        for operation, times in self.timers.items():
            stats[operation] = {
                'total_calls': self.call_counts[operation],
                'total_time': sum(times),
                'average_time': sum(times) / len(times),
                'min_time': min(times),
                'max_time': max(times)
            }
        return stats
    
    def optimize_batch_size(self, operation_times: List[float], target_time: float = 5.0) -> int:
        """Suggest optimal batch size based on timing data"""
        if not operation_times:
            return 10
        
        avg_time = sum(operation_times) / len(operation_times)
        optimal_batch = max(1, int(target_time / avg_time))
        return min(optimal_batch, 50)  # Cap at reasonable maximum


class BatchProcessor:
    """Efficient batch processing for analysis operations"""
    
    def __init__(self, batch_size: int = 10):
        self.batch_size = batch_size
        self.monitor = PerformanceMonitor()
    
    def process_in_batches(self, items: List[Any], processor_func, progress_callback=None) -> List[Any]:
        """Process items in batches for better performance"""
        results = []
        total_batches = (len(items) + self.batch_size - 1) // self.batch_size
        
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_number = i // self.batch_size + 1
            
            if progress_callback:
                progress_callback(batch_number, total_batches, f"Processing batch {batch_number}/{total_batches}")
            
            batch_results = processor_func(batch)
            results.extend(batch_results)
        
        return results
    
    def adaptive_batch_size(self, items: List[Any], processor_func, target_time: float = 5.0) -> int:
        """Determine optimal batch size by testing small samples"""
        if len(items) < 10:
            return len(items)
        
        # Test with small sample to estimate timing
        sample_size = min(5, len(items))
        sample_items = items[:sample_size]
        
        start_time = time.time()
        processor_func(sample_items)
        elapsed = time.time() - start_time
        
        if elapsed == 0:
            return min(50, len(items))
        
        time_per_item = elapsed / sample_size
        optimal_batch = max(1, int(target_time / time_per_item))
        return min(optimal_batch, 50)


class ResultsInsightGenerator:
    """Generate insights and recommendations from evaluation results"""
    
    def __init__(self, scoring_dimensions: List[str]):
        self.scoring_dimensions = scoring_dimensions
    
    def analyze_single_result(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single evaluation result and generate insights"""
        summary = results.get('summary', {})
        avg_scores = summary.get('avg_dimension_scores', {})
        
        if not avg_scores:
            return {'insights': [], 'overall_assessment': 'Unable to analyze - no scores available'}
        
        # Find strengths and improvements
        sorted_dimensions = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)
        strengths = [item for item in sorted_dimensions[:2] if item[1] >= 0.7]  # Top performing dimensions
        improvements = [item for item in sorted_dimensions[-2:] if item[1] < 0.7]  # Low performing dimensions
        
        # Generate insights
        insights = {
            'strengths': [],
            'improvements': [],
            'overall_assessment': self._assess_overall_performance(summary.get('avg_overall_score', 0))
        }
        
        # Strength insights
        for dim, score in strengths:
            if score >= 0.8:
                insights['strengths'].append(f"Excellent {self._format_dimension_name(dim)} scoring ({score:.3f})")
            else:
                insights['strengths'].append(f"Strong {self._format_dimension_name(dim)} evaluation ({score:.3f})")
        
        # Improvement insights
        for dim, score in improvements:
            if score < 0.6:
                insights['improvements'].append(f"Low {self._format_dimension_name(dim)} scoring ({score:.3f}) - consider prompt refinement")
            else:
                insights['improvements'].append(f"Moderate {self._format_dimension_name(dim)} performance ({score:.3f}) - room for improvement")
        
        return insights
    
    def _format_dimension_name(self, dimension: str) -> str:
        """Format dimension name for display"""
        return dimension.replace('_', ' ').title()
    
    def _assess_overall_performance(self, overall_score: float) -> str:
        """Assess overall performance level"""
        if overall_score >= 0.85:
            return f"Excellent overall performance ({overall_score:.3f})"
        elif overall_score >= 0.75:
            return f"Good overall performance ({overall_score:.3f})"
        elif overall_score >= 0.65:
            return f"Moderate performance with improvement opportunities ({overall_score:.3f})"
        else:
            return f"Performance needs significant improvement ({overall_score:.3f})"
    
    def compare_results(self, results_a: List[Dict], results_b: List[Dict], 
                       version_a: str, version_b: str) -> Dict[str, Any]:
        """Compare two sets of evaluation results and generate insights"""
        analyzer = PerformanceAnalyzer(self.scoring_dimensions)
        statistical_analyzer = StatisticalAnalyzer()
        
        # Calculate averages
        averages_a = analyzer.calculate_averages(results_a)
        averages_b = analyzer.calculate_averages(results_b)
        
        # Determine winner
        winner_analysis = analyzer.find_performance_winner(
            averages_a, averages_b, version_a, version_b
        )
        
        # Dimension comparison
        dimension_comparison = analyzer.analyze_dimension_comparison(
            averages_a, averages_b, version_a, version_b
        )
        
        # Statistical analysis
        scores_a = [r['evaluation']['overall_score'] for r in results_a if 'evaluation' in r]
        scores_b = [r['evaluation']['overall_score'] for r in results_b if 'evaluation' in r]
        statistical_analysis = statistical_analyzer.calculate_effect_size(scores_a, scores_b)
        
        # Generate insights
        insights = analyzer.generate_insights(
            dimension_comparison, 
            winner_analysis['score_difference'],
            version_a, version_b
        )
        
        return {
            'results_summary': {
                f'{version_a}_performance': averages_a,
                f'{version_b}_performance': averages_b
            },
            'comparative_analysis': winner_analysis,
            'dimension_comparison': dimension_comparison,
            'statistical_analysis': statistical_analysis,
            'recommendations': insights
        }