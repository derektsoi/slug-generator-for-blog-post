"""
LLM Optimization Orchestrator

Main class that coordinates A/B testing, metrics collection, and comparison
of different LLM prompt versions to identify optimal configurations.
"""

import time
import json
import random
import os
from pathlib import Path
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime

from .test_runner import TestRunner
from .metrics_calculator import MetricsCalculator
from .comparator import Comparator


def load_sample_urls() -> List[Dict[str, Any]]:
    """
    Load sample URLs from the test fixtures dataset.
    
    Returns:
        List of URL dictionaries with 'title' and 'url' keys
    """
    # Find the sample dataset file
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    sample_urls_path = project_root / 'tests' / 'fixtures' / 'sample_blog_urls.json'
    
    if not sample_urls_path.exists():
        raise FileNotFoundError(f"Sample URLs dataset not found at: {sample_urls_path}")
    
    with open(sample_urls_path, 'r', encoding='utf-8') as f:
        urls = json.load(f)
    
    return urls


def generate_expected_themes(title: str) -> List[str]:
    """
    Generate expected themes from a blog post title.
    
    Args:
        title: Blog post title
        
    Returns:
        List of expected theme keywords
    """
    # Simple theme extraction logic
    themes = []
    title_lower = title.lower()
    
    # Brand detection patterns
    brand_patterns = {
        'agete': ['agete', 'nojess'],
        'jojo': ['jojo-maman-bebe', 'baby', 'uk'],
        'gap': ['gap', 'us', 'fashion'],
        'kindle': ['kindle', 'amazon', 'ereader'],
        'rakuten': ['rakuten', 'japan'],
        'verish': ['verish', 'lingerie'],
        'taylor': ['taylor-swift', 'music']
    }
    
    # Category patterns
    category_patterns = {
        '珠寶': ['jewelry', 'accessories'],
        '童裝': ['baby', 'clothes', 'kids'],
        '內衣': ['lingerie', 'underwear'],
        '時尚': ['fashion', 'style'],
        '電子': ['electronics', 'tech'],
        '書': ['books', 'reading'],
        '美妝': ['beauty', 'cosmetics'],
        '集運': ['shipping', 'logistics'],
        '代購': ['proxy-shopping', 'buying'],
        '網購': ['shopping', 'online']
    }
    
    # Geographic patterns
    geo_patterns = {
        '英國': ['uk', 'britain'],
        '美國': ['us', 'america'],
        '日本': ['japan', 'japanese'],
        '韓國': ['korea', 'korean'],
        '香港': ['hongkong', 'hk']
    }
    
    # Apply pattern matching
    for pattern, theme_list in {**brand_patterns, **category_patterns, **geo_patterns}.items():
        if pattern in title_lower:
            themes.extend(theme_list)
    
    # Add common themes
    if '教學' in title or 'guide' in title_lower:
        themes.append('guide')
    if '推介' in title or 'recommendation' in title_lower:
        themes.append('recommendation')
    if '比較' in title or 'comparison' in title_lower:
        themes.append('comparison')
    
    # Remove duplicates and return
    return list(set(themes))


def create_randomized_test_cases(sample_urls: List[Dict], count: int = 10, 
                                random_seed: Optional[int] = None,
                                expected_themes_generator: Optional[Callable] = None) -> List[Dict]:
    """
    Create randomized test cases from URL dataset.
    
    Args:
        sample_urls: List of URL dictionaries
        count: Number of test cases to generate
        random_seed: Seed for reproducible randomization
        expected_themes_generator: Function to generate expected themes
        
    Returns:
        List of test case dictionaries
    """
    if random_seed is not None:
        random.seed(random_seed)
    
    # Select random URLs
    selected_urls = random.sample(sample_urls, min(count, len(sample_urls)))
    
    test_cases = []
    for i, url_data in enumerate(selected_urls):
        title = url_data['title']
        
        # Generate expected themes
        if expected_themes_generator:
            expected_themes = expected_themes_generator(title)
        else:
            expected_themes = generate_expected_themes(title)
        
        # Determine category from title content
        category = 'unknown'
        if any(brand in title.lower() for brand in ['agete', 'nojess', 'jewelry']):
            category = 'jewelry-brands'
        elif any(brand in title.lower() for brand in ['jojo', 'baby', 'children']):
            category = 'brand-product-association'
        elif any(word in title.lower() for word in ['gap', 'fashion', 'clothes']):
            category = 'fashion-brands'
        elif any(word in title.lower() for word in ['kindle', 'electronics', 'tech']):
            category = 'technology'
        elif any(word in title.lower() for word in ['food', 'snack', '零食']):
            category = 'food'
        
        test_case = {
            'input': {
                'title': title,
                'content': title  # Use title as content for testing
            },
            'expected': expected_themes,
            'url_index': i,
            'category': category,
            'original_url': url_data.get('url', '')
        }
        test_cases.append(test_case)
    
    return test_cases


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
        self.primary_metric = config.get('primary_metric', 'avg_theme_coverage')
        
        # NEW: Enhanced A/B testing configuration
        self.include_detailed_results = config.get('include_detailed_results', False)
        self.verbose_output = config.get('verbose_output', False)
        self.randomize_urls = config.get('randomize_urls', False)
        self.url_count = config.get('url_count', 10)
        self.random_seed = config.get('random_seed', None)
        
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
        # NEW: Handle URL randomization if enabled
        if self.randomize_urls:
            try:
                sample_urls = load_sample_urls()
                test_cases = create_randomized_test_cases(
                    sample_urls, 
                    count=self.url_count, 
                    random_seed=self.random_seed
                )
                print(f"🎲 Using {len(test_cases)} randomized URLs from dataset")
            except Exception as e:
                print(f"⚠️  URL randomization failed: {e}")
                print("Proceeding with provided test cases...")
        
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
                
                # NEW: Enhanced console output with per-URL details
                if self.verbose_output and 'detailed_url_results' in version_results:
                    self._display_detailed_url_results(version, version_results['detailed_url_results'])
                
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
    
    def _display_detailed_url_results(self, version: str, detailed_results: List[Dict]) -> None:
        """
        Display detailed per-URL results in console.
        
        Args:
            version: Version identifier
            detailed_results: List of detailed URL results
        """
        print(f"\n   🔍 DETAILED URL RESULTS FOR {version.upper()}:")
        print(f"   {'='*(len(version)+28)}")
        
        for i, url_result in enumerate(detailed_results):
            title = url_result.get('title', 'Unknown Title')
            generated_slug = url_result.get('generated_slug', 'no-slug')
            coverage = url_result.get('coverage', 0)
            duration = url_result.get('duration', 0)
            success = url_result.get('success', False)
            expected_themes = url_result.get('expected_themes', [])
            
            # Truncate title for display
            display_title = title[:60] + '...' if len(title) > 60 else title
            
            # Status indicator
            status_icon = '✅' if success else '❌'
            
            print(f"   URL {i}: \"{display_title}\"")
            print(f"     Generated: {generated_slug}")
            print(f"     Expected: {expected_themes}")
            print(f"     Coverage: {coverage:.0%} {status_icon} ({duration:.1f}s)")
            print()
        
        # Summary
        if detailed_results:
            avg_coverage = sum(r.get('coverage', 0) for r in detailed_results) / len(detailed_results)
            success_count = sum(1 for r in detailed_results if r.get('success', False))
            success_rate = success_count / len(detailed_results)
            avg_duration = sum(r.get('duration', 0) for r in detailed_results) / len(detailed_results)
            
            print(f"   📊 SUMMARY: {avg_coverage:.0%} avg coverage, {success_rate:.0%} success rate, {avg_duration:.1f}s avg duration")
    
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
                'confidence_threshold': self.confidence_threshold,
                # NEW: Enhanced configuration
                'include_detailed_results': self.include_detailed_results,
                'verbose_output': self.verbose_output,
                'randomize_urls': self.randomize_urls,
                'url_count': self.url_count,
                'random_seed': self.random_seed
            },
            'results': self.results,
            'insights': self.generate_insights()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Results exported to: {filepath}")