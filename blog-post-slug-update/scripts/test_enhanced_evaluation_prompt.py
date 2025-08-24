#!/usr/bin/env python3
"""
Test the enhanced SEO-focused evaluation prompt with the existing system
"""

import os
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from evaluation.core.seo_evaluator import SEOEvaluator
from config.evaluation_prompt_manager import EvaluationPromptManager

def test_enhanced_prompt_compatibility():
    """Test if enhanced_seo_focused prompt works with existing system"""
    
    print("🔍 Testing Enhanced SEO-Focused Evaluation Prompt Compatibility...")
    
    # Test prompt loading
    try:
        prompt_manager = EvaluationPromptManager()
        prompt_content = prompt_manager.get_prompt("enhanced_seo_focused")
        metadata = prompt_manager.get_prompt_metadata("enhanced_seo_focused")
        
        print(f"✅ Prompt loaded successfully")
        print(f"📊 Dimensions: {metadata.get('scoring_dimensions', [])}")
        print(f"📝 Description: {metadata.get('description', 'N/A')}")
        
        # Test prompt structure
        required_sections = [
            "EVALUATION DIMENSIONS",
            "BRAND_HIERARCHY_ACCURACY",
            "PATTERN_UNIQUENESS", 
            "CULTURAL_AUTHENTICITY",
            "CROSS_BORDER_SERVICE_CLARITY",
            "TECHNICAL_SEO_COMPLIANCE"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in prompt_content:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"⚠️ Missing sections: {missing_sections}")
        else:
            print("✅ All required sections present")
            
        # Test scoring dimensions compatibility
        current_dimensions = ["user_intent_match", "brand_hierarchy", "cultural_authenticity", "click_through_potential", "competitive_differentiation", "technical_seo"]
        enhanced_dimensions = metadata.get('scoring_dimensions', [])
        
        print(f"\n📈 Dimension Comparison:")
        print(f"Current system: {current_dimensions}")
        print(f"Enhanced prompt: {enhanced_dimensions}")
        
        # Check for overlap
        overlap = set(current_dimensions) & set(enhanced_dimensions)
        print(f"📊 Overlapping dimensions: {list(overlap)}")
        
        if 'cultural_authenticity' in overlap:
            print("✅ Cultural authenticity preserved")
        if 'technical_seo' in enhanced_dimensions:
            print("✅ Technical SEO maintained")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing prompt compatibility: {e}")
        return False

def test_production_data_integration():
    """Test if production insights are properly integrated"""
    
    print(f"\n🏭 Testing Production Data Integration...")
    
    try:
        prompt_manager = EvaluationPromptManager()
        metadata = prompt_manager.get_prompt_metadata("enhanced_seo_focused")
        
        # Check for production data insights
        production_data = metadata.get('production_data_insights', {})
        
        if production_data:
            print(f"✅ Production data insights included")
            print(f"📊 Slugs analyzed: {production_data.get('total_slugs_analyzed', 'N/A')}")
            
            overuse_patterns = production_data.get('critical_overuse_patterns', {})
            if 'premium' in overuse_patterns:
                print(f"✅ Premium overuse pattern detected: {overuse_patterns['premium']}")
            if 'ultimate' in overuse_patterns:
                print(f"✅ Ultimate overuse pattern detected: {overuse_patterns['ultimate']}")
                
            acceptable_patterns = production_data.get('acceptable_patterns', {})
            if acceptable_patterns:
                print(f"✅ Acceptable patterns defined: {list(acceptable_patterns.keys())}")
        else:
            print("⚠️ No production data insights found")
            
        return bool(production_data)
        
    except Exception as e:
        print(f"❌ Error checking production data: {e}")
        return False

def test_framework_compliance():
    """Test LLM-as-a-Judge framework compliance"""
    
    print(f"\n🎯 Testing LLM-as-a-Judge Framework Compliance...")
    
    try:
        prompt_manager = EvaluationPromptManager()
        prompt_content = prompt_manager.get_prompt("enhanced_seo_focused")
        metadata = prompt_manager.get_prompt_metadata("enhanced_seo_focused")
        
        # Check for 6-question framework compliance
        framework_check = metadata.get('framework_compliance', {})
        six_question = framework_check.get('six_question_framework', {})
        
        required_elements = ['role', 'content_type', 'quality_aspects', 'scoring_method', 'rubric_examples', 'output_format']
        
        compliance_score = 0
        for element in required_elements:
            if six_question.get(element):
                compliance_score += 1
                print(f"✅ {element}: {six_question[element][:50]}...")
            else:
                print(f"❌ Missing: {element}")
        
        compliance_percentage = (compliance_score / len(required_elements)) * 100
        print(f"\n📊 Framework Compliance: {compliance_percentage:.0f}%")
        
        # Check for step-by-step reasoning
        if framework_check.get('reasoning_instructions'):
            print("✅ Step-by-step reasoning included")
        
        # Check for uncertainty handling
        if framework_check.get('uncertainty_handling'):
            print("✅ Uncertainty handling included")
            
        return compliance_percentage >= 80
        
    except Exception as e:
        print(f"❌ Error checking framework compliance: {e}")
        return False

def main():
    """Run all compatibility tests"""
    
    print("=" * 70)
    print("🧪 ENHANCED SEO EVALUATION PROMPT - COMPATIBILITY TESTS")
    print("=" * 70)
    
    tests = [
        ("Basic Compatibility", test_enhanced_prompt_compatibility),
        ("Production Data Integration", test_production_data_integration),
        ("LLM-as-a-Judge Framework", test_framework_compliance)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 70)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} | {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 Enhanced evaluation prompt is ready for production!")
        print("\n💡 Next Steps:")
        print("   1. Update evaluation system to use 'enhanced_seo_focused'")
        print("   2. Run A/B comparison with current evaluation")
        print("   3. Monitor pattern uniqueness improvements")
    else:
        print("⚠️ Some tests failed - review before deployment")
    
    return passed == len(tests)

if __name__ == "__main__":
    main()