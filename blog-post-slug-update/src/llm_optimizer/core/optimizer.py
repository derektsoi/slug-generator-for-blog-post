"""
LLM Optimization Orchestrator

Main class that coordinates A/B testing, metrics collection, and comparison
of different LLM prompt versions to identify optimal configurations.
"""

import time
import json
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime

from .test_runner import TestRunner
from .metrics_calculator import MetricsCalculator
from .comparator import Comparator


class LLMOptimizer:
    """
    Main optimization coordinator for systematic LLM prompt improvement.
    
    Orchestrates the complete optimization workflow:
    1. Run A/B tests across multiple prompt versions
    2. Collect performance metrics for each version
    3. Compare results and identify best performing version
    4. Generate actionable insights and recommendations
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize optimizer with configuration.
        
        Args:
            config: Configuration dictionary containing:
                - test_function: Function to test with different prompt versions
                - metrics: List of metrics to collect
                - confidence_threshold: Minimum confidence for results
                - primary_metric: Main metric for ranking versions
        """
        self.config = config
        self.test_function = config.get('test_function')
        self.metrics = config.get('metrics', ['theme_coverage', 'success_rate', 'duration'])
        self.confidence_threshold = config.get('confidence_threshold', 0.8)
        self.primary_metric = config.get('primary_metric', 'theme_coverage')
        self.results = {}
        
        # Initialize components
        self.metrics_calculator = MetricsCalculator()
        self.test_runner = TestRunner([], self.metrics_calculator)
        self.comparator = Comparator()
        
    def run_comparison(self, prompt_versions: List[str], test_cases: List[Dict]) -> Dict[str, Dict]:
        """
        Run A/B testing comparison across multiple prompt versions.
        
        Args:
            prompt_versions: List of prompt version identifiers (e.g., ['v1', 'v2', 'v3'])
            test_cases: List of test cases to evaluate each version against
            
        Returns:
            Dictionary with results for each version:
            {
                'v1': {'coverage': 0.6, 'success_rate': 1.0, 'duration': 5.0},
                'v2': {'coverage': 0.75, 'success_rate': 1.0, 'duration': 4.5}
            }
        """
        print("🔬 RUNNING LLM OPTIMIZATION A/B TESTING")
        print("=" * 60)
        print(f"Testing {len(prompt_versions)} versions across {len(test_cases)} test cases")
        print()
        
        results = {}
        
        for version in prompt_versions:
            print(f"🧪 Testing Version: {version}")
            
            start_time = time.time()
            
            try:
                # Run test function with specific prompt version
                version_results = self.test_function(version, test_cases)
                
                # Store results with metadata
                results[version] = {
                    **version_results,
                    'version': version,
                    'test_time': datetime.now().isoformat(),
                    'total_test_cases': len(test_cases)
                }
                
                # Extract key metrics for summary
                key_metrics = {
                    metric: version_results.get(metric, 0) 
                    for metric in self.metrics 
                    if metric in version_results
                }
                
                print(f"   Results: {key_metrics}")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                results[version] = {
                    'error': str(e),
                    'version': version,
                    'test_time': datetime.now().isoformat()
                }
            
            print(f"   Duration: {time.time() - start_time:.2f}s")
            print()
        
        self.results = results
        return results
    
    def get_best_version(self, primary_metric: Optional[str] = None) -> str:
        """
        Identify the best performing prompt version based on primary metric.
        
        Args:
            primary_metric: Metric to use for ranking (defaults to config primary_metric)
            
        Returns:
            Version identifier of best performing prompt
        """
        if not self.results:
            raise ValueError("No results available. Run comparison first.")
        
        metric = primary_metric or self.primary_metric
        
        # Filter out versions with errors
        valid_results = {
            version: data for version, data in self.results.items()
            if 'error' not in data and metric in data
        }
        
        if not valid_results:
            raise ValueError(f"No valid results found for metric: {metric}")
        
        # Find version with highest metric value
        best_version = max(
            valid_results.keys(),
            key=lambda v: valid_results[v][metric]
        )
        
        return best_version
    
    def calculate_improvement(self, baseline_version: str, improved_version: str, metric: str) -> float:
        """
        Calculate improvement percentage between two versions.
        
        Args:
            baseline_version: Version to use as baseline
            improved_version: Version to compare against baseline
            metric: Metric to calculate improvement for
            
        Returns:
            Improvement as decimal (0.15 = 15% improvement)
        """
        if baseline_version not in self.results or improved_version not in self.results:
            raise ValueError("Specified versions not found in results")
        
        baseline_value = self.results[baseline_version].get(metric, 0)
        improved_value = self.results[improved_version].get(metric, 0)
        
        if baseline_value == 0:
            return 0.0
        
        improvement = improved_value - baseline_value
        return improvement
    
    def get_ranking(self, metric: Optional[str] = None) -> List[str]:
        """
        Get versions ranked by performance (best first).
        
        Args:
            metric: Metric to rank by (defaults to primary_metric)
            
        Returns:
            List of version identifiers in ranked order
        """
        return self.comparator.rank_versions(self.results, metric or self.primary_metric)
    
    def generate_insights(self) -> Dict[str, Any]:
        """
        Generate comprehensive optimization insights and recommendations.
        
        Returns:
            Dictionary containing insights, recommendations, and summary
        """
        if not self.results:
            raise ValueError("No results available. Run comparison first.")
        
        insights = self.comparator.generate_insights(self.results)
        
        # Add optimization-specific insights
        best_version = self.get_best_version()
        ranking = self.get_ranking()
        
        insights.update({
            'optimization_summary': {
                'best_version': best_version,
                'total_versions_tested': len(self.results),
                'primary_metric': self.primary_metric,
                'ranking': ranking
            },
            'deployment_recommendation': {
                'recommended_version': best_version,
                'confidence_level': 'high' if len(ranking) >= 3 else 'medium',
                'next_steps': self._generate_next_steps(best_version, ranking)
            }
        })
        
        return insights
    
    def _generate_next_steps(self, best_version: str, ranking: List[str]) -> List[str]:
        """Generate actionable next steps based on optimization results"""
        steps = []
        
        if len(ranking) >= 2:
            best_score = self.results[ranking[0]].get(self.primary_metric, 0)
            second_score = self.results[ranking[1]].get(self.primary_metric, 0)
            
            improvement = best_score - second_score
            
            if improvement > 0.1:  # Significant improvement
                steps.append(f"Deploy {best_version} to production (significant improvement)")
                steps.append("Monitor production performance for 1 week")
                steps.append("Consider A/B testing with real users")
            elif improvement > 0.05:  # Moderate improvement
                steps.append(f"Consider deploying {best_version} (moderate improvement)")
                steps.append("Run additional test cases to validate improvement")
            else:  # Minimal improvement
                steps.append("Investigate why improvements are minimal")
                steps.append("Consider testing more diverse prompt variations")
                steps.append("Analyze failed test cases for insights")
        else:
            steps.append("Run more prompt versions for better comparison")
            
        return steps
    
    def export_results(self, filepath: str) -> None:
        """
        Export optimization results to JSON file.
        
        Args:
            filepath: Path to save results file
        """
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'config': {
                'metrics': self.metrics,
                'primary_metric': self.primary_metric,
                'confidence_threshold': self.confidence_threshold
            },
            'results': self.results,
            'insights': self.generate_insights()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Results exported to: {filepath}")