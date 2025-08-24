# Prompt A/B Testing Methodology Guide

**🎯 Comprehensive framework for testing both slug generation prompts and evaluation prompts**  
**📅 Established**: August 24, 2025  
**🔄 Status**: Production-ready methodology based on V1-V11 evolution

---

## 🧪 **A/B Testing Framework Overview**

### **Two Testing Types Supported**
1. **🔧 Slug Generation Prompt Testing** - Compare different generation prompt versions
2. **📊 Evaluation Prompt Testing** - Compare different evaluation/judging prompt versions

### **Core Methodology Principles**
- **Real LLM API Calls** - No simulation, actual OpenAI integration
- **Statistical Validation** - Confidence intervals, effect size analysis
- **Comprehensive Test Cases** - Random sampling + targeted problematic cases
- **Multi-dimensional Analysis** - Pattern, cultural, performance metrics

---

## 🔧 **Slug Generation Prompt A/B Testing**

### **Testing Framework Structure**
```python
# Standard 4-Version Comparison Framework
versions_to_test = [
    'baseline_version',     # Current production (e.g., V10)
    'previous_strong',      # Known good version (e.g., V8, V6)
    'new_variant_a',        # New development (e.g., V11a)
    'new_variant_b'         # Alternative approach (e.g., V11b)
]
```

### **Test Case Selection Strategy**
```
Total Test Cases: 40-50 cases
├── Random Sample: 30 cases (representative production data)
├── Problematic Cases: 10-15 cases (targeted challenges)
└── Edge Cases: 5 cases (boundary conditions)

Problematic Case Categories:
1. Multi-brand scenarios (3+ brands)
2. Cultural subculture terms (jirai-kei, yandere, etc.)
3. Pattern repetition victims (ultimate/premium overuse)
4. Simple vs complex content classification
5. Cross-border service contexts
6. Brand hierarchy confusion
7. Geographic complexity
8. Character archetypes
9. Fashion subcultures
10. Seasonal/temporal contexts
```

### **Evaluation Metrics for Generation Prompts**
```python
analysis_dimensions = {
    'pattern_diversification': {
        'banned_word_usage': ['ultimate', 'premium'],
        'alternative_usage': ['comprehensive', 'definitive', 'expert'],
        'repetition_threshold': 0.15  # 15% max repetition
    },
    'cultural_intelligence': {
        'traditional_terms': ['ichiban-kuji', 'daikoku-drugstore'],
        'subculture_terms': ['jirai-kei', 'ryousangata', 'yandere'],
        'preservation_rate': 0.90  # 90% cultural term preservation
    },
    'adaptive_constraints': {
        'simple_content_compliance': '3-5 words',
        'complex_content_compliance': '8-12 words',
        'appropriate_routing': 0.95  # 95% correct classification
    },
    'brand_intelligence': {
        'brand_inclusion_rate': 1.0,  # 100% brand preservation
        'multi_brand_handling': True,
        'hierarchy_recognition': True
    },
    'performance_metrics': {
        'average_confidence': 0.75,  # Minimum confidence threshold
        'success_rate': 0.95,        # 95% successful generation
        'response_consistency': 0.90  # Consistent quality
    }
}
```

### **Implementation Template**
```python
# Generation Prompt Testing Template
from src.core.slug_generator import SlugGenerator

def test_generation_prompts(test_cases, versions):
    results = []
    
    for version in versions:
        generator = SlugGenerator(prompt_version=version)
        version_results = []
        
        for test_case in test_cases:
            try:
                result = generator.generate_slug_from_content(
                    test_case['title'], 
                    test_case['content']
                )
                version_results.append({
                    'test_case_id': test_case['id'],
                    'slug': result['primary'],
                    'confidence': result['confidence'],
                    'success': True
                })
            except Exception as e:
                version_results.append({
                    'test_case_id': test_case['id'],
                    'error': str(e),
                    'success': False
                })
        
        results.append({
            'version': version,
            'results': version_results
        })
    
    return analyze_generation_results(results)
```

---

## 📊 **Evaluation Prompt A/B Testing**

### **Testing Framework Structure**
```python
# Evaluation Prompt Comparison Framework
evaluation_versions = [
    'current',                 # Default balanced evaluation
    'v2_cultural_focused',     # Cultural authenticity focus
    'v3_competitive_focused',  # Competitive differentiation focus
    'new_enhanced_version'     # New development (e.g., v2.1)
]
```

### **Test Case Requirements**
```
Evaluation Test Strategy:
├── Same Slug Set: Test all evaluation prompts on identical slugs
├── Diverse Content: Various content types and complexities
├── Known Quality Range: Good, average, poor slug examples
└── Cultural Variety: Asian, Western, mixed cultural contexts

Evaluation Dimensions to Test:
1. Cultural authenticity scoring consistency
2. Brand hierarchy recognition accuracy
3. Competitive differentiation assessment
4. Technical SEO compliance validation
5. User intent matching evaluation
6. Click-through potential scoring
```

### **Evaluation Metrics for Evaluation Prompts**
```python
evaluation_analysis = {
    'scoring_consistency': {
        'inter_prompt_agreement': 0.85,  # Agreement between prompts
        'intra_prompt_reliability': 0.90, # Same prompt consistency
        'confidence_correlation': 0.80   # Confidence vs quality correlation
    },
    'cultural_accuracy': {
        'cultural_term_recognition': 1.0,  # Must recognize all cultural terms
        'authenticity_scoring': 'validated_against_native_speakers',
        'bias_detection': 'systematic_fairness_analysis'
    },
    'dimension_effectiveness': {
        'brand_scoring_accuracy': 0.90,
        'cultural_scoring_accuracy': 0.95,
        'competitive_scoring_accuracy': 0.85,
        'technical_scoring_accuracy': 0.95
    },
    'practical_utility': {
        'actionable_feedback': True,
        'specific_improvement_suggestions': True,
        'production_deployment_ready': True
    }
}
```

### **Implementation Template**
```python
# Evaluation Prompt Testing Template
from src.evaluation.core.seo_evaluator import SEOEvaluator

def test_evaluation_prompts(test_slugs, evaluation_versions):
    results = []
    
    for version in evaluation_versions:
        evaluator = SEOEvaluator(evaluation_prompt_version=version)
        version_results = []
        
        for slug_data in test_slugs:
            try:
                evaluation = evaluator.evaluate(
                    slug_data['slug'],
                    slug_data['title'],
                    slug_data['content']
                )
                version_results.append({
                    'slug_id': slug_data['id'],
                    'evaluation': evaluation,
                    'success': True
                })
            except Exception as e:
                version_results.append({
                    'slug_id': slug_data['id'],
                    'error': str(e),
                    'success': False
                })
        
        results.append({
            'version': version,
            'results': version_results
        })
    
    return analyze_evaluation_results(results)
```

---

## 📋 **Standard Testing Workflow**

### **Phase 1: Setup & Preparation** (15 minutes)
```bash
1. Create test branch: git checkout -b feature/prompt-testing-[version]
2. Prepare test cases: Select 40-50 representative cases
3. Define success criteria: Set performance thresholds
4. Setup testing environment: Validate API keys and dependencies
```

### **Phase 2: Execution** (30-60 minutes)
```bash
1. Run baseline tests: Test current production version
2. Execute comparison testing: Test all versions in parallel
3. Collect comprehensive data: Save all results for analysis
4. Monitor for issues: Check for failures or anomalies
```

### **Phase 3: Analysis** (30-45 minutes)
```bash
1. Statistical analysis: Calculate significance and effect sizes
2. Pattern analysis: Check for repetition and diversity issues
3. Cultural intelligence assessment: Validate preservation and recognition
4. Performance comparison: Compare confidence and success rates
5. Generate recommendations: Production readiness assessment
```

### **Phase 4: Documentation & Decision** (15-30 minutes)
```bash
1. Document findings: Create comprehensive analysis report
2. Update methodology: Note any improvements to testing process
3. Make deployment decision: Production readiness recommendation
4. Plan next iteration: V[N+1] development direction
```

---

## 🎯 **Success Criteria Templates**

### **Slug Generation Prompt Success Criteria**
```python
generation_success_criteria = {
    'pattern_health': {
        'banned_word_elimination': 1.0,     # 100% elimination of ultimate/premium
        'pattern_diversity': 0.70,          # 70%+ unique starting words
        'repetition_threshold': 0.15        # <15% any single pattern
    },
    'cultural_preservation': {
        'traditional_terms': 1.0,           # 100% preservation of core terms
        'subculture_recognition': 0.80,     # 80% recognition of new subcultures
        'authenticity_maintenance': 0.95    # 95% cultural authenticity
    },
    'performance_standards': {
        'confidence_threshold': 0.75,       # 75%+ average confidence
        'success_rate': 0.95,              # 95%+ successful generation
        'production_readiness': 0.75       # 75%+ overall readiness score
    }
}
```

### **Evaluation Prompt Success Criteria**
```python
evaluation_success_criteria = {
    'scoring_reliability': {
        'consistency_score': 0.85,          # 85%+ inter-prompt agreement
        'bias_minimization': 0.90,          # 90%+ bias mitigation
        'cultural_accuracy': 0.95           # 95%+ cultural scoring accuracy
    },
    'practical_utility': {
        'actionable_feedback': 1.0,         # 100% actionable insights
        'improvement_guidance': 1.0,        # 100% specific recommendations
        'production_deployment': 0.80       # 80%+ production ready
    }
}
```

---

## 📊 **Analysis Output Templates**

### **Standard Analysis Report Structure**
```markdown
# [Version] A/B Testing Analysis Report

## Executive Summary
- Version comparison overview
- Key breakthroughs and limitations
- Production readiness assessment

## Detailed Results
- Statistical significance analysis
- Pattern diversity metrics
- Cultural intelligence comparison
- Performance benchmarking

## Specific Findings
- Pattern repetition analysis
- Cultural preservation validation
- Brand intelligence assessment
- Constraint compliance evaluation

## Recommendations
- Production deployment decision
- Areas for improvement
- Next iteration direction
```

---

## 🛠️ **Tools & Scripts Reference**

### **Generation Prompt Testing Tools**
- **Framework**: `docs/evolution/results/v11/v11_real_ab_testing.py`
- **Pattern Analysis**: `docs/evolution/results/v11/v11_pattern_analysis.py`  
- **Test Case Setup**: `docs/evolution/results/v11/v11_comprehensive_testing.py`

### **Evaluation Prompt Testing Tools**
- **Framework**: `scripts/compare_evaluation_prompts_refactored.py`
- **Individual Testing**: `scripts/test_evaluation_prompt_refactored.py`
- **Validation**: `scripts/validate_evaluation_prompt_refactored.py`

### **Analysis Tools**
- **Statistical Analysis**: Built into testing frameworks
- **Pattern Detection**: Automated repetition analysis
- **Cultural Validation**: Subculture and traditional term recognition

---

## 🎯 **Quick Start Checklist**

### **Before Starting Any A/B Test:**
- [ ] Define testing objective (generation vs evaluation)
- [ ] Select comparison versions (baseline + variants)  
- [ ] Prepare test cases (random + problematic + edge)
- [ ] Set success criteria and performance thresholds
- [ ] Validate testing environment and API access

### **During Testing:**
- [ ] Run tests in parallel for fair comparison
- [ ] Monitor for failures or anomalies
- [ ] Save comprehensive results data
- [ ] Document any issues or observations

### **After Testing:**
- [ ] Perform statistical significance analysis
- [ ] Check pattern diversity and cultural preservation
- [ ] Generate actionable recommendations
- [ ] Update methodology based on learnings
- [ ] Plan next iteration development

---

**This methodology has been validated through V1-V11 evolution and is production-ready for systematic prompt optimization.**

*Methodology Guide created: August 24, 2025*  
*Based on validated V1-V11 testing experience*  
*Ready for V12+ development iterations*