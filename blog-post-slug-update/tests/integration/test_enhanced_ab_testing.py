#!/usr/bin/env python3
"""
Test-Driven Development for Enhanced A/B Testing

Tests for enhanced A/B testing functionality that shows detailed per-URL results
for each prompt version being compared, not just aggregated metrics.

Uses dynamic prompt version discovery and realistic test scenarios.
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from optimization.optimizer import LLMOptimizer
from optimization.test_runner import TestRunner
from optimization.metrics_calculator import MetricsCalculator


class TestEnhancedABTesting:
    """Test cases for enhanced A/B testing with detailed per-URL results"""
    
    def setup_method(self):
        """Setup test environment"""
        self.sample_test_cases = [
            {
                'input': {'title': '8大日牌輕珠寶品牌一次睇！Agete、nojess及Star Jewelry等日劇女主御用明星珠寶', 'content': 'Agete jewelry content'},
                'expected': ['agete', 'nojess', 'japanese', 'jewelry', 'brands'],
                'url_index': 0,
                'category': 'jewelry-brands'
            },
            {
                'input': {'title': '英國必買童裝 JoJo Maman Bébé官網 3 折起入手網購教學', 'content': 'JoJo Maman Bebe UK shopping'},
                'expected': ['uk', 'jojo-maman-bebe', 'baby', 'clothes', 'shopping', 'guide'],
                'url_index': 1,
                'category': 'brand-product-association'
            },
            {
                'input': {'title': 'GAP集團美國官網網購教學，附Old Navy、Banana Republic及Athleta等副牌全面介紹', 'content': 'GAP group brands'},
                'expected': ['gap', 'us', 'fashion', 'brands', 'guide'],
                'url_index': 2,
                'category': 'fashion-brands'
            }
        ]
    
    def discover_available_prompt_versions(self):
        """Discover available prompt versions from config directory"""
        project_root = Path(__file__).parent.parent.parent
        prompt_dir = project_root / 'src' / 'config' / 'prompts'
        
        available_versions = []
        
        # Check for current production prompt
        if (prompt_dir / 'current.txt').exists():
            available_versions.append('current')
            
        # Check for archived versions
        archive_dir = prompt_dir / 'archive'
        if archive_dir.exists():
            for prompt_file in archive_dir.glob('*.txt'):
                version_name = prompt_file.stem
                available_versions.append(version_name)
        
        return available_versions
    
    def create_realistic_test_function(self):
        """Create test function that simulates realistic prompt version differences"""
        def mock_test_function(version, test_cases):
            # Realistic performance characteristics based on actual V5/V6 evolution
            version_performance = {
                'current': {'avg_coverage': 0.90, 'brand_detection': 0.75, 'cultural_preservation': 0.85},
                'v6_cultural_enhanced': {'avg_coverage': 0.95, 'brand_detection': 0.85, 'cultural_preservation': 1.0},
                'v5_brand_focused': {'avg_coverage': 0.75, 'brand_detection': 0.80, 'cultural_preservation': 0.60},
                'v2_few_shot': {'avg_coverage': 0.73, 'brand_detection': 0.50, 'cultural_preservation': 0.40},
                'v1_baseline': {'avg_coverage': 0.59, 'brand_detection': 0.40, 'cultural_preservation': 0.30}
            }
            
            # Default performance for unknown versions
            default_perf = {'avg_coverage': 0.65, 'brand_detection': 0.45, 'cultural_preservation': 0.35}
            perf = version_performance.get(version, default_perf)
            
            # Generate realistic per-URL results
            detailed_results = []
            for i, test_case in enumerate(test_cases):
                title = test_case['input']['title']
                category = test_case['category']
                
                # Simulate version-specific slug generation patterns
                if version == 'v6_cultural_enhanced':
                    if 'agete' in title.lower():
                        generated_slug = 'agete-nojess-star-jewelry-japan-guide'
                        coverage = 1.0  # Perfect cultural preservation
                    elif 'jojo' in title.lower():
                        generated_slug = 'jojo-maman-bebe-baby-clothes-uk-guide'
                        coverage = 0.83
                    else:
                        generated_slug = f'{version}-enhanced-{category.replace("_", "-")}-guide'
                        coverage = 0.90
                        
                elif version == 'v5_brand_focused':
                    if 'agete' in title.lower():
                        generated_slug = 'agete-nojess-jewelry-brands-guide'  # Less cultural awareness
                        coverage = 0.75
                    elif 'jojo' in title.lower():
                        generated_slug = 'jojo-maman-bebe-uk-shopping-guide'
                        coverage = 0.80
                    else:
                        generated_slug = f'{version}-brand-focused-{category.replace("_", "-")}'
                        coverage = 0.70
                        
                else:
                    # Generic version behavior
                    generated_slug = f'{version}-generic-{category.replace("_", "-")}'
                    coverage = perf['avg_coverage'] + (i * 0.05)  # Slight variation
                
                detailed_results.append({
                    'url_index': test_case['url_index'],
                    'title': title,
                    'generated_slug': generated_slug,
                    'expected_themes': test_case['expected'],
                    'coverage': min(coverage, 1.0),
                    'duration': 4.0 + (i * 0.3),  # Realistic timing variation
                    'success': True,
                    'category': category,
                    'confidence': 0.8 + (coverage * 0.2)  # Higher confidence with better coverage
                })
            
            return {
                'avg_theme_coverage': perf['avg_coverage'],
                'success_rate': 1.0,
                'avg_duration': 4.2,
                'brand_detection_rate': perf['brand_detection'],
                'cultural_preservation_rate': perf['cultural_preservation'],
                # NEW: This is what we want to add
                'detailed_url_results': detailed_results
            }
        
        return mock_test_function
    
    def test_enhanced_optimizer_with_real_prompt_versions(self):
        """Test that optimizer results include detailed per-URL results using real prompt versions"""
        
        available_versions = self.discover_available_prompt_versions()
        assert len(available_versions) >= 1, "Need at least 1 prompt version for testing"
        
        # Use first 2 versions if available, otherwise duplicate for testing
        test_versions = available_versions[:2] if len(available_versions) >= 2 else [available_versions[0]] * 2
        
        config = {
            'test_function': self.create_realistic_test_function(),
            'primary_metric': 'avg_theme_coverage',
            'include_detailed_results': True  # NEW: Flag for detailed results
        }
        optimizer = LLMOptimizer(config)
        
        # Run comparison with discovered versions
        results = optimizer.run_comparison(test_versions, self.sample_test_cases)
        
        # ASSERTIONS: What we expect but don't have yet
        
        # 1. Each tested version should have detailed_url_results
        for version in test_versions:
            assert version in results
            assert 'detailed_url_results' in results[version]
        
        # 2. Should have results for each URL
        first_version = test_versions[0]
        version_details = results[first_version]['detailed_url_results']
        
        assert len(version_details) == 3  # All 3 test URLs
        
        # 3. Each URL result should have required fields
        for url_result in version_details:
            assert 'url_index' in url_result
            assert 'title' in url_result
            assert 'generated_slug' in url_result
            assert 'expected_themes' in url_result
            assert 'coverage' in url_result
            assert 'duration' in url_result
            assert 'success' in url_result
            assert 'category' in url_result
            assert 'confidence' in url_result
        
        # 4. Results should show version-specific differences if multiple versions
        if len(test_versions) >= 2:
            v1_details = results[test_versions[0]]['detailed_url_results']
            v2_details = results[test_versions[1]]['detailed_url_results']
            
            # Should have different generated slugs for different versions
            assert v1_details[0]['generated_slug'] != v2_details[0]['generated_slug']
        
        # 5. Original aggregated metrics should still exist
        assert 'avg_theme_coverage' in results[first_version]
        assert 'success_rate' in results[first_version]
        assert 'avg_duration' in results[first_version]
    
    def test_enhanced_test_runner_preserves_individual_results(self):
        """Test that TestRunner preserves detailed individual test results"""
        
        metrics_calc = MetricsCalculator()
        test_runner = TestRunner(self.sample_test_cases, metrics_calc)
        
        # Mock test function that simulates SlugGenerator behavior
        def mock_slug_generator(test_input):
            title = test_input['title']
            if 'agete' in title.lower():
                return {
                    'primary': 'agete-nojess-star-jewelry-japan-guide',
                    'alternatives': ['japanese-jewelry-brands-guide'],
                    'confidence': 0.9
                }
            elif 'jojo' in title.lower():
                return {
                    'primary': 'jojo-maman-bebe-baby-clothes-uk-guide',
                    'alternatives': ['uk-baby-fashion-guide'],
                    'confidence': 0.85
                }
            else:
                clean_title = title.replace(' ', '-').lower()[:30]
                return {
                    'primary': f"generated-slug-for-{clean_title}",
                    'alternatives': [],
                    'confidence': 0.8
                }
        
        # Execute tests
        results = test_runner.execute_all_tests(mock_slug_generator)
        
        # ASSERTIONS: What we want to add
        
        # 1. Should preserve individual results with enhanced metadata
        assert 'detailed_individual_results' in results  # NEW: Enhanced field
        individual_results = results['detailed_individual_results']
        
        # 2. Should have result for each test case
        assert len(individual_results) == 3
        
        # 3. Each individual result should include URL metadata
        for i, result in enumerate(individual_results):
            assert 'url_index' in result  # NEW: Track URL position
            assert 'original_title' in result  # NEW: Preserve original title
            assert 'category' in result  # NEW: Preserve category
            assert 'generated_slug' in result  # NEW: Extract primary slug
            assert result['url_index'] == self.sample_test_cases[i]['url_index']
            assert result['category'] == self.sample_test_cases[i]['category']
        
        # 4. Should maintain existing structure
        assert 'success_rate' in results
        assert 'avg_theme_coverage' in results
    
    def test_enhanced_json_export_includes_per_url_breakdown(self):
        """Test that JSON export includes detailed per-URL breakdown"""
        
        available_versions = self.discover_available_prompt_versions()
        test_versions = available_versions[:2] if len(available_versions) >= 2 else ['current', 'test_version']
        
        config = {
            'test_function': self.create_realistic_test_function(),
            'include_detailed_results': True
        }
        optimizer = LLMOptimizer(config)
        
        results = optimizer.run_comparison(test_versions, self.sample_test_cases)
        
        # Export to JSON (this should be enhanced)
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        optimizer.export_results(temp_path)
        
        # Read and verify JSON structure
        with open(temp_path, 'r') as f:
            exported_data = json.load(f)
        
        # ASSERTIONS: Enhanced JSON structure
        
        # 1. Should have detailed results section
        assert 'results' in exported_data
        results_section = exported_data['results']
        
        # 2. Each version should have detailed breakdown
        for version in test_versions:
            if version in results:  # Only check versions that were actually tested
                version_data = results_section[version]
                
                # 3. Should have both summary and detailed results
                assert 'avg_theme_coverage' in version_data  # Existing
                assert 'detailed_url_results' in version_data  # NEW
                
                # 4. Detailed results should have all URLs
                detailed = version_data['detailed_url_results']
                assert len(detailed) == 3
                
                # 5. Each URL should have complete information
                for url_result in detailed:
                    assert 'url_index' in url_result
                    assert 'title' in url_result
                    assert 'generated_slug' in url_result
                    assert 'expected_themes' in url_result
                    assert 'coverage' in url_result
                    assert 'category' in url_result
        
        # 6. Should include metadata about test run
        assert 'timestamp' in exported_data
        assert 'config' in exported_data
        
        # Clean up
        os.unlink(temp_path)
    
    def test_url_randomization_consistency(self):
        """Test that same randomized URLs are used across all prompt versions"""
        
        def mock_test_function_with_url_tracking(version, test_cases):
            # Verify same test cases provided to each version
            return {
                'avg_theme_coverage': 0.8,
                'test_case_titles': [tc['input']['title'] for tc in test_cases],
                'test_case_count': len(test_cases),
                'url_indices': [tc['url_index'] for tc in test_cases]
            }
        
        config = {
            'test_function': mock_test_function_with_url_tracking,
            'randomize_urls': True,  # NEW: Enable URL randomization
            'url_count': 10,  # NEW: Number of URLs to randomly select
            'random_seed': 42  # NEW: For reproducible randomization
        }
        optimizer = LLMOptimizer(config)
        
        available_versions = self.discover_available_prompt_versions()
        test_versions = available_versions[:2] if len(available_versions) >= 2 else ['current', 'test_version']
        
        # Mock URL dataset loading
        with patch('optimization.optimizer.load_sample_urls') as mock_load:
            mock_load.return_value = [
                {
                    'title': f'日本手信零食 Sample URL {i}',
                    'url': f'https://www.buyandship.today/blog/2025/08/{i}/',
                    'category': 'food' if i % 2 == 0 else 'fashion'
                }
                for i in range(20)  # 20 URLs to choose from
            ]
            
            results = optimizer.run_comparison(test_versions, self.sample_test_cases)
        
        # ASSERTIONS: URL consistency
        
        # 1. Same number of test cases for each version
        first_version = test_versions[0]
        if len(test_versions) >= 2:
            second_version = test_versions[1]
            assert results[first_version]['test_case_count'] == results[second_version]['test_case_count']
            
            # 2. Exact same URLs used for both versions
            first_titles = results[first_version]['test_case_titles']
            second_titles = results[second_version]['test_case_titles']
            assert first_titles == second_titles
            
            # 3. Same URL indices (order consistency)
            first_indices = results[first_version]['url_indices']
            second_indices = results[second_version]['url_indices']
            assert first_indices == second_indices
        
        # 4. Should use specified number of URLs (when URL randomization is enabled)
        expected_count = 10  # As configured
        actual_count = results[first_version]['test_case_count']
        assert actual_count == expected_count
    
    def test_enhanced_console_output_display(self):
        """Test enhanced console output with per-URL results display"""
        
        available_versions = self.discover_available_prompt_versions()
        test_versions = available_versions[:1] if available_versions else ['current']
        
        config = {
            'test_function': self.create_realistic_test_function(),
            'verbose_output': True  # NEW: Enable detailed console output
        }
        optimizer = LLMOptimizer(config)
        
        # Capture console output
        import io
        from contextlib import redirect_stdout
        
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            optimizer.run_comparison(test_versions, self.sample_test_cases)
        
        console_output = captured_output.getvalue()
        
        # ASSERTIONS: Enhanced console format
        
        # 1. Should show per-URL results
        assert 'URL 0:' in console_output or 'agete' in console_output.lower()
        assert 'URL 1:' in console_output or 'jojo' in console_output.lower()
        
        # 2. Should show generated slugs
        assert 'generated' in console_output.lower() or 'slug' in console_output.lower()
        
        # 3. Should show coverage percentages
        assert '%' in console_output  # Coverage percentages
        
        # 4. Should show success indicators
        assert '✅' in console_output or 'success' in console_output.lower()
        
        # 5. Should maintain summary statistics
        assert 'coverage' in console_output.lower() or 'average' in console_output.lower()
    
    def test_backward_compatibility_maintained(self):
        """Test that all existing functionality still works without detailed results"""
        
        # Use existing test function format (no detailed results)
        def existing_test_function(version, test_cases):
            return {
                'avg_theme_coverage': 0.7,
                'success_rate': 1.0,
                'avg_duration': 5.0
            }
        
        config = {'test_function': existing_test_function}
        optimizer = LLMOptimizer(config)
        
        results = optimizer.run_comparison(['current'], self.sample_test_cases)
        
        # ASSERTIONS: Backward compatibility
        
        # 1. Should work with existing function format
        assert 'current' in results
        assert 'avg_theme_coverage' in results['current']
        assert 'success_rate' in results['current']
        
        # 2. Should not break existing methods
        best_version = optimizer.get_best_version()
        assert best_version == 'current'
        
        ranking = optimizer.get_ranking()
        assert ranking == ['current']
        
        insights = optimizer.generate_insights()
        assert 'optimization_summary' in insights
        
        # 3. Should not require detailed_url_results field
        assert results['current'].get('detailed_url_results') is None


class TestURLRandomization:
    """Test cases for URL randomization functionality"""
    
    def test_load_sample_urls_from_dataset(self):
        """Test loading URLs from sample dataset"""
        
        # This function should be added to optimizer
        from optimization.optimizer import load_sample_urls  # This will fail - not implemented yet
        
        urls = load_sample_urls()
        
        # Should load from tests/fixtures/sample_blog_urls.json
        assert len(urls) >= 10  # Should have substantial dataset
        assert all('title' in url for url in urls)
        assert all('url' in url for url in urls)
        
        # Should have real cross-border e-commerce content
        titles = [url['title'] for url in urls]
        assert any('agete' in title.lower() for title in titles)
        assert any('jojo' in title.lower() for title in titles)
        assert any('gap' in title.lower() for title in titles)
    
    def test_create_randomized_test_cases(self):
        """Test creating randomized test cases from URL dataset"""
        
        sample_urls = [
            {
                'title': '8大日牌輕珠寶品牌一次睇！Agete、nojess及Star Jewelry等日劇女主御用明星珠寶',
                'url': 'https://www.buyandship.today/blog/2025/08/18/agete/'
            },
            {
                'title': '英國必買童裝 JoJo Maman Bébé官網 3 折起入手網購教學',
                'url': 'https://www.buyandship.today/blog/2025/08/18/jojo/'
            }
        ] * 10  # Duplicate to have 20 URLs for selection
        
        # This function should be added
        from optimization.optimizer import create_randomized_test_cases  # Will fail - not implemented
        
        test_cases = create_randomized_test_cases(
            sample_urls, 
            count=10, 
            random_seed=42,
            expected_themes_generator=lambda title: ['theme1', 'theme2']  # Mock theme generation
        )
        
        assert len(test_cases) == 10
        assert all('input' in tc for tc in test_cases)
        assert all('expected' in tc for tc in test_cases)
        assert all('url_index' in tc for tc in test_cases)
        assert all('category' in tc for tc in test_cases)
        
        # Should preserve original URL metadata
        assert all('title' in tc['input'] for tc in test_cases)
        
        # Should generate appropriate expected themes
        assert all(len(tc['expected']) > 0 for tc in test_cases)
    
    def test_expected_themes_generation(self):
        """Test automatic generation of expected themes from blog titles"""
        
        from optimization.optimizer import generate_expected_themes  # Will fail - not implemented
        
        test_cases = [
            {
                'title': '8大日牌輕珠寶品牌一次睇！Agete、nojess及Star Jewelry等日劇女主御用明星珠寶',
                'expected_themes': ['agete', 'nojess', 'japanese', 'jewelry', 'brands']
            },
            {
                'title': '英國必買童裝 JoJo Maman Bébé官網 3 折起入手網購教學',
                'expected_themes': ['uk', 'jojo-maman-bebe', 'baby', 'clothes', 'shopping', 'guide']
            },
            {
                'title': 'GAP集團美國官網網購教學，附Old Navy、Banana Republic及Athleta等副牌全面介紹',
                'expected_themes': ['gap', 'us', 'fashion', 'brands', 'guide']
            }
        ]
        
        for test_case in test_cases:
            generated_themes = generate_expected_themes(test_case['title'])
            expected_themes = test_case['expected_themes']
            
            # Should capture major themes
            overlap = set(generated_themes) & set(expected_themes)
            assert len(overlap) >= 2, f"Generated themes {generated_themes} should overlap with expected {expected_themes}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])