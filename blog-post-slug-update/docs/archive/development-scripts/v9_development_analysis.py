#!/usr/bin/env python3
"""
V9 Development Analysis - LLM-Guided Prompt Evolution

Uses honest LLM evaluation system to analyze current prompt performance
and identify specific improvement opportunities for V9 development.
"""

import os
import sys
import json
from typing import Dict, List, Any
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from evaluation.core.evaluation_coordinator import EvaluationCoordinator
from evaluation.core.seo_evaluator_clean import SEOEvaluator
from evaluation.utils.exceptions import LLMUnavailableError
from core.slug_generator import SlugGenerator


class V9DevelopmentAnalyzer:
    """Analyze current prompts and guide V9 development using LLM evaluation"""
    
    def __init__(self, api_key: str):
        """Initialize with real API key for honest evaluation"""
        if not api_key or api_key == "test-key":
            raise ValueError("Valid OpenAI API key required for V9 development")
        
        self.coordinator = EvaluationCoordinator(api_key=api_key, enable_llm=True)
        self.llm_evaluator = SEOEvaluator(api_key=api_key)
        
        # Test cases representing known challenges and breakthroughs
        self.test_cases = {
            'v8_breakthrough': {
                'title': '日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！',
                'description': 'V8 breakthrough case - multi-brand complexity',
                'v8_expected': 'skinnydip-iface-rhinoshield-phone-cases-guide'
            },
            'v6_cultural': {
                'title': '【2025年最新】日本一番賞Online手把手教學！',
                'description': 'V6 cultural preservation case',
                'v6_expected': 'ichiban-kuji-anime-japan-guide'
            },
            'brand_compound': {
                'title': '大國藥妝香港開店定價無優勢！學識日本轉運平價入手化妝品、日用品等必買推介',
                'description': 'Compound brand case',
                'v6_expected': 'daikoku-drugstore-hongkong-proxy-guide'
            },
            'long_descriptive': {
                'title': 'JoJo Maman Bébé premium maternity wear collection detailed buying guide and size recommendations',
                'description': 'Long descriptive title challenge',
                'expected_challenge': 'length_constraints'
            },
            'mixed_language': {
                'title': '【Kindle Paperwhite評測】2024最新電子書閱讀器推薦！Amazon Kindle功能完整分析',
                'description': 'Mixed language with brands',
                'expected_challenge': 'language_complexity'
            }
        }

    def run_baseline_evaluation(self) -> Dict[str, Any]:
        """
        Run comprehensive baseline evaluation of current prompts
        
        Returns:
            Dict with evaluation results and improvement opportunities
        """
        
        print("🔍 Starting V9 Development Baseline Evaluation")
        print("=" * 60)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'prompt_evaluations': {},
            'improvement_opportunities': [],
            'meta_analysis': {},
            'v9_development_insights': []
        }
        
        # Test V8 and V6 prompts on all cases
        for prompt_version in ['v8', 'v6']:
            print(f"\n📋 Evaluating {prompt_version.upper()} Prompt Performance:")
            results['prompt_evaluations'][prompt_version] = self._evaluate_prompt_version(prompt_version)
        
        # Analyze improvement opportunities
        print(f"\n🎯 Analyzing Improvement Opportunities:")
        results['improvement_opportunities'] = self._extract_improvement_opportunities(
            results['prompt_evaluations']
        )
        
        # Generate V9 development insights
        print(f"\n🚀 Generating V9 Development Insights:")
        results['v9_development_insights'] = self._generate_v9_insights(results)
        
        # Save detailed results
        self._save_results(results)
        
        return results

    def _evaluate_prompt_version(self, version: str) -> Dict[str, Any]:
        """Evaluate specific prompt version on all test cases"""
        
        version_results = {
            'version': version,
            'test_case_results': {},
            'overall_performance': {},
            'qualitative_insights': [],
            'quantitative_summary': {}
        }
        
        generator = SlugGenerator(prompt_version=version)
        
        for case_name, case_data in self.test_cases.items():
            print(f"  Testing {case_name}...")
            
            try:
                # Generate slug with current prompt
                slug_result = generator.generate_slug_from_content(
                    case_data['title'], 
                    case_data['title']
                )
                
                if slug_result and 'primary' in slug_result:
                    generated_slug = slug_result['primary']
                    
                    # Evaluate with honest LLM system
                    evaluation = self.coordinator.evaluate_comprehensive(
                        generated_slug,
                        case_data['title'],
                        case_data['title']
                    )
                    
                    case_result = {
                        'generated_slug': generated_slug,
                        'evaluation': evaluation,
                        'case_description': case_data['description'],
                        'success': True
                    }
                    
                    # Extract key insights
                    if evaluation['llm_available']:
                        qualitative = evaluation['qualitative_insights']
                        case_result['key_insights'] = {
                            'overall_score': qualitative['overall_score'],
                            'strengths': qualitative.get('key_strengths', []),
                            'improvements': qualitative.get('improvement_areas', []),
                            'cultural_insights': qualitative.get('cultural_insights', ''),
                            'competitive_analysis': qualitative.get('competitive_analysis', '')
                        }
                        
                        # Collect insights for analysis
                        version_results['qualitative_insights'].extend([
                            f"Case {case_name}: {insight}" 
                            for insight in qualitative.get('improvement_areas', [])
                        ])
                
                else:
                    # Generation failed
                    case_result = {
                        'generated_slug': None,
                        'success': False,
                        'failure_reason': 'slug_generation_failed'
                    }
                    
                    # Analyze failure with LLM
                    failure_analysis = self.llm_evaluator.evaluate_failure_case(
                        case_data['title'],
                        case_data['title'],
                        'generation_failure'
                    )
                    case_result['failure_analysis'] = failure_analysis
                
            except Exception as e:
                case_result = {
                    'generated_slug': None,
                    'success': False,
                    'error': str(e)
                }
            
            version_results['test_case_results'][case_name] = case_result
        
        # Calculate overall performance
        version_results['overall_performance'] = self._calculate_version_performance(version_results)
        
        return version_results

    def _extract_improvement_opportunities(self, prompt_evaluations: Dict) -> List[Dict[str, Any]]:
        """Extract specific improvement opportunities from LLM evaluations"""
        
        opportunities = []
        
        # Analyze across all prompt versions and test cases
        for version, version_data in prompt_evaluations.items():
            for case_name, case_result in version_data['test_case_results'].items():
                
                if case_result['success'] and 'key_insights' in case_result:
                    insights = case_result['key_insights']
                    
                    # Extract specific improvement areas
                    for improvement in insights.get('improvements', []):
                        opportunities.append({
                            'source_version': version,
                            'source_case': case_name,
                            'improvement_area': improvement,
                            'current_score': insights['overall_score'],
                            'context': case_result['case_description']
                        })
                
                elif not case_result['success']:
                    # Failure cases are improvement opportunities
                    opportunities.append({
                        'source_version': version,
                        'source_case': case_name,
                        'improvement_area': 'generation_failure',
                        'failure_reason': case_result.get('failure_reason', 'unknown'),
                        'context': case_result.get('case_description', 'failure case')
                    })
        
        # Deduplicate and prioritize opportunities
        opportunities = self._prioritize_opportunities(opportunities)
        
        return opportunities

    def _prioritize_opportunities(self, opportunities: List[Dict]) -> List[Dict]:
        """Prioritize improvement opportunities by impact and frequency"""
        
        # Count frequency of improvement areas
        area_frequency = {}
        for opp in opportunities:
            area = opp['improvement_area']
            area_frequency[area] = area_frequency.get(area, 0) + 1
        
        # Score opportunities
        for opp in opportunities:
            area = opp['improvement_area']
            
            # Base priority score
            priority_score = area_frequency[area]  # Frequency bonus
            
            # Boost for critical areas
            if 'generation_failure' in area:
                priority_score += 10  # Critical: must fix
            elif any(keyword in area.lower() for keyword in ['constraint', 'length', 'complex']):
                priority_score += 5   # High: architectural issues
            elif any(keyword in area.lower() for keyword in ['cultural', 'brand', 'authenticity']):
                priority_score += 3   # Medium: quality improvements
            
            opp['priority_score'] = priority_score
        
        # Sort by priority
        return sorted(opportunities, key=lambda x: x['priority_score'], reverse=True)

    def _generate_v9_insights(self, results: Dict) -> List[str]:
        """Generate specific insights for V9 development"""
        
        insights = []
        
        # Analyze performance patterns
        prompt_evaluations = results['prompt_evaluations']
        opportunities = results['improvement_opportunities']
        
        # High-level performance comparison
        if 'v8' in prompt_evaluations and 'v6' in prompt_evaluations:
            v8_perf = prompt_evaluations['v8']['overall_performance']
            v6_perf = prompt_evaluations['v6']['overall_performance']
            
            insights.append(f"V8 vs V6 Performance: V8 success rate {v8_perf.get('success_rate', 0):.1%} vs V6 {v6_perf.get('success_rate', 0):.1%}")
        
        # Top improvement opportunities
        top_opportunities = opportunities[:3]
        for i, opp in enumerate(top_opportunities, 1):
            insights.append(
                f"Priority {i}: {opp['improvement_area']} "
                f"(affects {opp.get('source_case', 'multiple cases')})"
            )
        
        # Specific V9 development strategies
        if any('constraint' in opp['improvement_area'].lower() for opp in opportunities):
            insights.append("V9 Strategy: Consider constraint architecture improvements")
        
        if any('cultural' in opp['improvement_area'].lower() for opp in opportunities):
            insights.append("V9 Strategy: Enhance cultural awareness beyond V6 levels")
        
        if any('brand' in opp['improvement_area'].lower() for opp in opportunities):
            insights.append("V9 Strategy: Improve multi-brand handling beyond V8 breakthroughs")
        
        # LLM-specific insights
        qualitative_insights = []
        for version_data in prompt_evaluations.values():
            qualitative_insights.extend(version_data.get('qualitative_insights', []))
        
        if qualitative_insights:
            insights.append(f"LLM identified {len(qualitative_insights)} specific improvement areas")
        
        return insights

    def _calculate_version_performance(self, version_results: Dict) -> Dict[str, Any]:
        """Calculate overall performance metrics for a prompt version"""
        
        test_results = version_results['test_case_results']
        
        # Success rate
        total_cases = len(test_results)
        successful_cases = sum(1 for result in test_results.values() if result['success'])
        success_rate = successful_cases / total_cases if total_cases > 0 else 0
        
        # Average scores for successful cases
        scores = []
        for result in test_results.values():
            if result['success'] and 'key_insights' in result:
                scores.append(result['key_insights']['overall_score'])
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return {
            'success_rate': success_rate,
            'successful_cases': successful_cases,
            'total_cases': total_cases,
            'average_score': avg_score,
            'score_distribution': scores
        }

    def _save_results(self, results: Dict):
        """Save detailed results for analysis"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"v9_development_analysis_{timestamp}.json"
        filepath = os.path.join('results', filename)
        
        # Ensure results directory exists
        os.makedirs('results', exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {filepath}")

    def print_summary(self, results: Dict):
        """Print comprehensive summary of baseline evaluation"""
        
        print(f"\n📊 V9 Development Analysis Summary")
        print("=" * 50)
        
        # Prompt performance overview
        for version, version_data in results['prompt_evaluations'].items():
            perf = version_data['overall_performance']
            print(f"{version.upper()} Performance: {perf['success_rate']:.1%} success, {perf['average_score']:.3f} avg score")
        
        # Top improvement opportunities
        print(f"\n🎯 Top Improvement Opportunities:")
        for i, opp in enumerate(results['improvement_opportunities'][:5], 1):
            print(f"{i}. {opp['improvement_area']} (Priority: {opp['priority_score']})")
        
        # V9 development insights
        print(f"\n🚀 V9 Development Insights:")
        for insight in results['v9_development_insights']:
            print(f"• {insight}")
        
        print(f"\n✅ Baseline evaluation complete - ready for V9 development!")


def main():
    """Main execution function"""
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv('OPENAI_API_KEY')
        except ImportError:
            pass
    
    if not api_key or api_key == "test-key":
        print("❌ Valid OPENAI_API_KEY required for V9 development")
        print("   Set OPENAI_API_KEY environment variable with real API key")
        return 1
    
    print(f"🔑 Using API key: {api_key[:8]}...")
    
    try:
        # Run baseline evaluation
        analyzer = V9DevelopmentAnalyzer(api_key)
        results = analyzer.run_baseline_evaluation()
        analyzer.print_summary(results)
        
        return 0
        
    except LLMUnavailableError as e:
        print(f"❌ LLM evaluation unavailable: {e}")
        print("   Check API key and network connection")
        return 1
    except Exception as e:
        print(f"❌ Error during V9 development analysis: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())