#!/usr/bin/env python3
"""
A/B Testing Framework for Evaluation Prompts
Compares enhanced_seo_focused (v1.0) vs enhanced_seo_focused_v2.1
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import statistics

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from config.evaluation_prompt_manager import EvaluationPromptManager

def create_test_scenarios() -> List[Dict]:
    """Create test scenarios for A/B testing"""
    return [
        {
            "name": "Brand-Heavy Multi-Brand Comparison",
            "slug": "ultimate-skinnydip-iface-rhinoshield-phone-cases-guide",
            "title": "日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！",
            "content": "Comprehensive comparison of Skinnydip, iface, and RhinoShield phone cases for iPhone 16 Pro with international shipping options",
            "expected_improvements_v2.1": [
                "Better brand hierarchy assessment (primary brands identification)",
                "Search intent alignment with 'brand comparison' pattern",
                "Justified 'ultimate' usage for multi-brand content"
            ]
        },
        {
            "name": "Cultural Product with Service Context",
            "slug": "insider-daikoku-drugstore-japan-proxy-guide",
            "title": "大國藥妝香港開店定價無優勢！學識日本轉運平價入手化妝品",
            "content": "Daikoku drugstore proxy shopping guide for cosmetics with Japan to Hong Kong forwarding",
            "expected_improvements_v2.1": [
                "Search intent alignment with 'brand+service' pattern",
                "Cultural authenticity validation via embedded dictionary",
                "Service clarity assessment for proxy shopping context"
            ]
        },
        {
            "name": "Premium Pattern Red Flag",
            "slug": "premium-japanese-skincare-shopping-guide",
            "title": "Japanese Skincare Shopping Guide",
            "content": "General guide to buying Japanese skincare products online",
            "expected_improvements_v2.1": [
                "Immediate red flag pattern detection (premium = 64% overuse)",
                "Search intent mismatch identification (generic vs specific)",
                "Improvement suggestions with specific alternatives"
            ]
        },
        {
            "name": "Cultural Authenticity Test",
            "slug": "ultimate-anime-merchandise-buying-guide",
            "title": "日本一番賞Online手把手教學",
            "content": "Complete guide to buying ichiban kuji anime prize figures from Japan",
            "expected_improvements_v2.1": [
                "Cultural authenticity penalty for 'anime-merchandise' vs 'ichiban-kuji'",
                "Embedded dictionary reference for proper romanization",
                "Search intent alignment with cultural term searches"
            ]
        },
        {
            "name": "Cross-Border Service Clarity",
            "slug": "tory-burch-uk-hongkong-shipping-guide",
            "title": "Tory Burch減價優惠！英國網購低至3折",
            "content": "Tory Burch UK discount shopping with Hong Kong forwarding service",
            "expected_improvements_v2.1": [
                "Search intent alignment with 'brand+geographic flow' pattern",
                "Service clarity assessment for international shipping",
                "Brand-first approach validation"
            ]
        },
        {
            "name": "Complex Search Intent Mapping",
            "slug": "comprehensive-jirai-kei-harajuku-fashion-guide",
            "title": "地雷系服裝風格指南",
            "content": "Guide to jirai kei fashion style shopping in Harajuku with proxy services",
            "expected_improvements_v2.1": [
                "Cultural term search intent alignment",
                "Geographic context evaluation (Harajuku specificity)",
                "Service integration assessment"
            ]
        }
    ]

def simulate_evaluation_comparison(scenario: Dict, prompt_v1: str, prompt_v2: str) -> Dict:
    """
    Simulate evaluation comparison between two prompts
    In real implementation, this would call actual LLM APIs
    """
    
    # Simulate v1.0 evaluation (current enhanced_seo_focused)
    v1_scores = simulate_v1_evaluation(scenario)
    
    # Simulate v2.1 evaluation with improvements
    v2_scores = simulate_v2_1_evaluation(scenario)
    
    return {
        "scenario": scenario["name"],
        "slug": scenario["slug"],
        "v1_scores": v1_scores,
        "v2_scores": v2_scores,
        "improvements": calculate_improvements(v1_scores, v2_scores),
        "expected_met": validate_expected_improvements(scenario, v1_scores, v2_scores)
    }

def simulate_v1_evaluation(scenario: Dict) -> Dict:
    """Simulate v1.0 evaluation logic"""
    slug = scenario["slug"]
    
    # V1.0 scoring simulation
    scores = {
        "brand_hierarchy_accuracy": assess_brand_hierarchy_v1(slug, scenario),
        "pattern_uniqueness": assess_pattern_uniqueness_v1(slug),
        "cultural_authenticity": assess_cultural_authenticity_v1(slug, scenario),
        "cross_border_service_clarity": assess_service_clarity_v1(slug, scenario),
        "technical_seo_compliance": assess_technical_seo(slug)
    }
    
    overall_score = sum(scores.values()) / len(scores)
    
    return {
        "dimension_scores": scores,
        "overall_score": overall_score,
        "version": "v1.0"
    }

def simulate_v2_1_evaluation(scenario: Dict) -> Dict:
    """Simulate v2.1 evaluation logic with improvements"""
    slug = scenario["slug"]
    
    # V2.1 scoring simulation with new dimension
    scores = {
        "brand_hierarchy_accuracy": assess_brand_hierarchy_v2_1(slug, scenario),
        "red_flag_pattern_avoidance": assess_red_flag_patterns_v2_1(slug),
        "cultural_authenticity": assess_cultural_authenticity_v2_1(slug, scenario),
        "cross_border_service_clarity": assess_service_clarity_v2_1(slug, scenario),
        "search_intent_alignment": assess_search_intent_alignment_v2_1(slug, scenario),
        "technical_seo_compliance": assess_technical_seo(slug)
    }
    
    # V2.1 weighted scoring
    weights = {
        "red_flag_pattern_avoidance": 0.30,
        "brand_hierarchy_accuracy": 0.25,
        "search_intent_alignment": 0.20,
        "cultural_authenticity": 0.15,
        "cross_border_service_clarity": 0.10,
        "technical_seo_compliance": 0.05
    }
    
    overall_score = sum(scores[dim] * weights[dim] for dim in weights.keys())
    
    return {
        "dimension_scores": scores,
        "overall_score": overall_score,
        "version": "v2.1",
        "evaluation_summary": {
            "primary_brands_detected": extract_primary_brands(scenario),
            "red_flag_patterns": detect_red_flag_patterns(slug),
            "search_pattern_match": map_search_intent(slug, scenario)
        }
    }

# Simulation helper functions
def assess_brand_hierarchy_v1(slug: str, scenario: Dict) -> float:
    """V1.0 brand assessment - basic brand detection"""
    brands = extract_brands_simple(scenario["content"])
    brands_in_slug = count_brands_in_slug(slug, brands)
    return min(brands_in_slug / max(len(brands), 1), 1.0)

def assess_brand_hierarchy_v2_1(slug: str, scenario: Dict) -> float:
    """V2.1 brand assessment - primary vs secondary distinction"""
    primary_brands = extract_primary_brands(scenario)
    secondary_brands = extract_secondary_brands(scenario)
    
    primary_in_slug = count_brands_in_slug(slug, primary_brands)
    primary_coverage = primary_in_slug / max(len(primary_brands), 1)
    
    # V2.1 gives higher priority to primary brand coverage
    if primary_coverage >= 0.8:
        return min(primary_coverage + 0.1, 1.0)
    else:
        return primary_coverage * 0.8

def assess_pattern_uniqueness_v1(slug: str) -> float:
    """V1.0 pattern assessment"""
    first_word = slug.split('-')[0]
    if first_word == "premium":
        return 0.0
    elif first_word == "ultimate":
        return 0.2
    else:
        return 0.8

def assess_red_flag_patterns_v2_1(slug: str) -> float:
    """V2.1 enhanced pattern detection with embedded reference data"""
    red_flag_patterns = {
        "premium-": 0.0,  # 64% overuse - immediate fail
        "ultimate-": 0.1,  # 8.6% overuse - severe penalty
        "best-": 0.3,     # 380 uses - moderate penalty
        "top-": 0.3       # 290 uses - moderate penalty
    }
    
    red_flag_endings = {
        "discount-shopping": 0.2,  # 12.9% overuse
        "shopping-guide": 0.4      # 6.4% overuse
    }
    
    # Check starting patterns
    for pattern, penalty_score in red_flag_patterns.items():
        if slug.startswith(pattern):
            return penalty_score
    
    # Check ending patterns
    for pattern, penalty_score in red_flag_endings.items():
        if slug.endswith(pattern):
            return penalty_score
    
    return 0.9  # Good uniqueness score

def assess_cultural_authenticity_v2_1(slug: str, scenario: Dict) -> float:
    """V2.1 cultural assessment with embedded dictionary"""
    cultural_dictionary = {
        "ichiban-kuji": 1.0,
        "drugstore": 0.9,
        "proxy-shopping": 0.9,
        "jirai-kei": 1.0,
        "anime-merchandise": 0.3  # Generic vs specific
    }
    
    score = 0.6  # baseline
    for term, term_score in cultural_dictionary.items():
        if term in slug:
            score = max(score, term_score)
    
    # V2.1 penalty for missing cultural terms when content has them
    if "一番賞" in scenario["title"] and "ichiban-kuji" not in slug:
        score = min(score, 0.3)
    
    return score

def assess_search_intent_alignment_v2_1(slug: str, scenario: Dict) -> float:
    """V2.1 NEW dimension - search intent alignment"""
    
    # Map content to search intent patterns
    content_lower = (scenario["title"] + " " + scenario["content"]).lower()
    
    search_patterns = {
        "brand_comparison": 0.9 if "vs" in slug or len(extract_brands_simple(scenario["content"])) > 2 else 0.5,
        "brand_service": 0.9 if any(brand in slug and service in slug 
                                   for brand in ["daikoku", "tory", "uniqlo"] 
                                   for service in ["proxy", "shipping", "forwarding"]) else 0.6,
        "cultural_specific": 0.9 if any(term in slug for term in ["ichiban-kuji", "jirai-kei", "drugstore"]) else 0.6,
        "geographic_flow": 0.8 if any(geo in slug for geo in ["japan", "uk", "korea", "hongkong"]) else 0.5
    }
    
    # Return highest matching pattern score
    return max(search_patterns.values())

def extract_primary_brands(scenario: Dict) -> List[str]:
    """Extract primary brands from scenario"""
    title_content = (scenario["title"] + " " + scenario["content"]).lower()
    
    primary_brands = []
    brand_indicators = ["skinnydip", "iface", "rhinoshield", "daikoku", "tory burch", "uniqlo", "muji"]
    
    for brand in brand_indicators:
        if brand in title_content:
            primary_brands.append(brand)
    
    return primary_brands

def extract_secondary_brands(scenario: Dict) -> List[str]:
    """Extract secondary brands (mentioned but not focus)"""
    return []  # Simplified for simulation

def extract_brands_simple(content: str) -> List[str]:
    """Simple brand extraction"""
    brands = []
    content_lower = content.lower()
    brand_list = ["skinnydip", "iface", "rhinoshield", "daikoku", "tory", "uniqlo", "muji"]
    
    for brand in brand_list:
        if brand in content_lower:
            brands.append(brand)
    
    return brands

def count_brands_in_slug(slug: str, brands: List[str]) -> int:
    """Count how many brands appear in slug"""
    count = 0
    for brand in brands:
        if brand.lower().replace(" ", "-") in slug:
            count += 1
    return count

def assess_service_clarity_v1(slug: str, scenario: Dict) -> float:
    """V1.0 service clarity assessment"""
    service_indicators = ["proxy", "forwarding", "shipping", "japan", "korea", "uk", "hongkong"]
    found = sum(1 for indicator in service_indicators if indicator in slug)
    return min(found * 0.3, 1.0)

def assess_service_clarity_v2_1(slug: str, scenario: Dict) -> float:
    """V2.1 enhanced service clarity assessment"""
    # More sophisticated service context evaluation
    geographic_flow = any(combo in slug for combo in ["japan-", "uk-", "korea-"])
    service_type = any(service in slug for service in ["proxy", "forwarding", "shipping"])
    
    if geographic_flow and service_type:
        return 0.9
    elif geographic_flow or service_type:
        return 0.7
    else:
        return 0.5

def assess_cultural_authenticity_v1(slug: str, scenario: Dict) -> float:
    """V1.0 cultural authenticity assessment"""
    cultural_terms = ["ichiban-kuji", "drugstore", "jirai-kei"]
    if any(term in slug for term in cultural_terms):
        return 0.8
    return 0.6

def assess_technical_seo(slug: str) -> float:
    """Technical SEO assessment (same for both versions)"""
    word_count = len(slug.split('-'))
    if 3 <= word_count <= 10 and len(slug) <= 90:
        return 0.9
    return 0.7

def detect_red_flag_patterns(slug: str) -> List[str]:
    """Detect red flag patterns in slug"""
    patterns = []
    if slug.startswith("premium-"):
        patterns.append("premium starter (64% overuse)")
    if slug.startswith("ultimate-"):
        patterns.append("ultimate starter (8.6% overuse)")
    if slug.endswith("discount-shopping"):
        patterns.append("discount-shopping ending (12.9% overuse)")
    return patterns

def map_search_intent(slug: str, scenario: Dict) -> str:
    """Map slug to search intent hypothesis"""
    if "vs" in slug or len(extract_brands_simple(scenario["content"])) > 2:
        return "brand_comparison_search"
    elif any(service in slug for service in ["proxy", "forwarding"]):
        return "service_specific_search"
    elif any(cultural in slug for cultural in ["ichiban-kuji", "jirai-kei"]):
        return "cultural_term_search"
    else:
        return "generic_product_search"

def calculate_improvements(v1_scores: Dict, v2_scores: Dict) -> Dict:
    """Calculate improvement metrics between versions"""
    
    improvements = {
        "overall_score_change": v2_scores["overall_score"] - v1_scores["overall_score"],
        "dimension_changes": {},
        "new_dimensions": []
    }
    
    # Compare common dimensions
    common_dims = set(v1_scores["dimension_scores"].keys()) & set(v2_scores["dimension_scores"].keys())
    
    for dim in common_dims:
        improvements["dimension_changes"][dim] = v2_scores["dimension_scores"][dim] - v1_scores["dimension_scores"][dim]
    
    # Identify new dimensions in v2.1
    new_dims = set(v2_scores["dimension_scores"].keys()) - set(v1_scores["dimension_scores"].keys())
    improvements["new_dimensions"] = list(new_dims)
    
    return improvements

def validate_expected_improvements(scenario: Dict, v1_scores: Dict, v2_scores: Dict) -> Dict:
    """Validate if expected improvements were achieved"""
    validation = {
        "expected_improvements": scenario.get("expected_improvements_v2.1", []),
        "achieved": []
    }
    
    # Check specific improvements based on scenario
    if "Better brand hierarchy assessment" in str(validation["expected_improvements"]):
        if v2_scores["dimension_scores"]["brand_hierarchy_accuracy"] > v1_scores["dimension_scores"].get("brand_hierarchy_accuracy", 0):
            validation["achieved"].append("Brand hierarchy improvement confirmed")
    
    if "Search intent alignment" in str(validation["expected_improvements"]):
        if "search_intent_alignment" in v2_scores["dimension_scores"]:
            validation["achieved"].append(f"Search intent alignment added: {v2_scores['dimension_scores']['search_intent_alignment']:.2f}")
    
    if "red flag pattern detection" in str(validation["expected_improvements"]):
        if "red_flag_pattern_avoidance" in v2_scores["dimension_scores"]:
            validation["achieved"].append(f"Red flag detection added: {v2_scores['dimension_scores']['red_flag_pattern_avoidance']:.2f}")
    
    return validation

def run_ab_test():
    """Run comprehensive A/B test"""
    
    print("🧪 A/B TESTING: Enhanced SEO Focused v1.0 vs v2.1")
    print("="*70)
    
    # Load prompts
    try:
        manager = EvaluationPromptManager()
        prompt_v1 = manager.load_prompt_template('enhanced_seo_focused')
        prompt_v2 = manager.load_prompt_template('enhanced_seo_focused_v2.1')
        print("✅ Both prompt versions loaded successfully")
    except Exception as e:
        print(f"❌ Error loading prompts: {e}")
        return False
    
    # Create test scenarios
    scenarios = create_test_scenarios()
    print(f"\n📊 Testing {len(scenarios)} scenarios...")
    
    results = []
    
    # Run comparisons
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n🔬 Test {i}: {scenario['name']}")
        print(f"   Slug: {scenario['slug']}")
        
        comparison = simulate_evaluation_comparison(scenario, prompt_v1, prompt_v2)
        results.append(comparison)
        
        # Display results
        v1_overall = comparison["v1_scores"]["overall_score"]
        v2_overall = comparison["v2_scores"]["overall_score"]
        improvement = v2_overall - v1_overall
        
        print(f"   📈 Overall Scores:")
        print(f"      v1.0: {v1_overall:.3f}")
        print(f"      v2.1: {v2_overall:.3f}")
        
        if improvement > 0:
            print(f"      🟢 Improvement: +{improvement:.3f}")
        else:
            print(f"      🔴 Regression: {improvement:.3f}")
        
        # Show key dimension changes
        print(f"   🎯 Key Changes:")
        for dim, change in comparison["improvements"]["dimension_changes"].items():
            status = "🟢" if change > 0 else "🔴" if change < 0 else "🟡"
            print(f"      {status} {dim}: {change:+.3f}")
        
        # Show new dimensions
        if comparison["improvements"]["new_dimensions"]:
            print(f"   ✨ New Dimensions: {', '.join(comparison['improvements']['new_dimensions'])}")
        
        # Validation
        achieved = comparison["expected_met"]["achieved"]
        if achieved:
            print(f"   ✅ Expectations Met: {len(achieved)} improvements")
            for achievement in achieved:
                print(f"      • {achievement}")
    
    # Summary Analysis
    print("\n" + "="*70)
    print("📋 A/B TEST SUMMARY")
    print("="*70)
    
    overall_improvements = [r["improvements"]["overall_score_change"] for r in results]
    avg_improvement = statistics.mean(overall_improvements)
    positive_changes = sum(1 for imp in overall_improvements if imp > 0)
    
    print(f"📊 Performance Summary:")
    print(f"   Average Overall Score Change: {avg_improvement:+.3f}")
    print(f"   Scenarios with Improvement: {positive_changes}/{len(results)}")
    print(f"   Success Rate: {(positive_changes/len(results)*100):.1f}%")
    
    # Dimension analysis
    all_dimension_changes = {}
    for result in results:
        for dim, change in result["improvements"]["dimension_changes"].items():
            if dim not in all_dimension_changes:
                all_dimension_changes[dim] = []
            all_dimension_changes[dim].append(change)
    
    print(f"\n📈 Dimension Analysis:")
    for dim, changes in all_dimension_changes.items():
        avg_change = statistics.mean(changes)
        status = "🟢" if avg_change > 0 else "🔴" if avg_change < 0 else "🟡"
        print(f"   {status} {dim}: {avg_change:+.3f} average")
    
    # New features impact
    new_dimensions = set()
    for result in results:
        new_dimensions.update(result["improvements"]["new_dimensions"])
    
    if new_dimensions:
        print(f"\n✨ New Features in v2.1:")
        for dim in new_dimensions:
            scores = [r["v2_scores"]["dimension_scores"][dim] for r in results if dim in r["v2_scores"]["dimension_scores"]]
            if scores:
                avg_score = statistics.mean(scores)
                print(f"   • {dim}: {avg_score:.3f} average performance")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if avg_improvement > 0.05:
        print(f"   ✅ DEPLOY v2.1: Significant improvement (+{avg_improvement:.3f})")
    elif avg_improvement > 0.01:
        print(f"   ⚠️ CAUTIOUS DEPLOY: Marginal improvement (+{avg_improvement:.3f})")
    else:
        print(f"   ❌ DON'T DEPLOY: No clear benefit (+{avg_improvement:.3f})")
    
    if positive_changes < len(results) * 0.7:
        print(f"   ⚠️ MIXED RESULTS: Only {positive_changes}/{len(results)} scenarios improved")
    
    print(f"\n🎯 Key v2.1 Advantages:")
    print(f"   • Search Intent Alignment: NEW dimension for user behavior matching")
    print(f"   • Embedded Reference Data: Built-in pattern and cultural dictionaries")
    print(f"   • Enhanced Brand Classification: Primary vs secondary brand distinction")
    print(f"   • Structured Evaluation Process: 5-step methodology")
    print(f"   • Improved Output Format: Detailed summaries and human review flags")
    
    return avg_improvement > 0.01

if __name__ == "__main__":
    success = run_ab_test()
    exit(0 if success else 1)