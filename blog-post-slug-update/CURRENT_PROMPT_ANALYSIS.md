# Current Evaluation Prompt Analysis

**Date**: August 23, 2025  
**Branch**: `feature/llm-as-judge-enhancements`

## 🔍 Analysis of Existing Prompts

### **Cultural Focused Prompt (v2_cultural_focused.txt)**

#### Strengths:
- ✅ Clear priority weighting (HIGH PRIORITY markers)
- ✅ Specific examples (ichiban-kuji vs anime-merchandise)
- ✅ Structured JSON output format
- ✅ Cultural term preservation focus
- ✅ Confidence scoring included

#### Areas for Improvement:
- ❌ **No chain-of-thought reasoning**: Jumps directly to scoring
- ❌ **Limited bias mitigation**: No explicit bias awareness instructions
- ❌ **Vague scoring guidance**: "Score 0.9+ for preserved terms" lacks detailed rubric
- ❌ **No step-by-step evaluation process**: Doesn't guide thinking through dimensions
- ❌ **Limited examples**: Only 2 examples for cultural authenticity

### **Competitive Focused Prompt (v3_competitive_focused.txt)**

#### Strengths:
- ✅ Clear competitive focus with specific terms ("ultimate", "premium", "exclusive")
- ✅ Priority ranking explicit
- ✅ Structured JSON output
- ✅ Commercial intent emphasis

#### Areas for Improvement:
- ❌ **No reasoning process**: Direct scoring without explanation
- ❌ **Potential bias toward superlatives**: May over-reward "clickbait" terms
- ❌ **No bias mitigation**: Could favor sensational over authentic content
- ❌ **Limited rubric detail**: Scoring criteria not specific enough
- ❌ **No cross-cultural considerations**: May conflict with cultural authenticity

## 📊 Identified Issues

### **1. Lack of Chain-of-Thought Reasoning**
Both prompts ask for direct scoring without requiring the LLM to explain its reasoning process first.

**Current**: 
```
1. CULTURAL_AUTHENTICITY: Does this preserve cultural terms...?
```

**Should be**:
```
1. First, analyze the cultural terms present...
2. Then, consider preservation vs generic alternatives...
3. Finally, score based on your analysis...
```

### **2. Insufficient Bias Mitigation**
No explicit instructions to consider multiple perspectives or avoid systematic biases.

**Missing**:
- Instructions to consider different cultural contexts
- Warnings about over-weighting certain term types
- Guidance on balanced evaluation

### **3. Vague Scoring Rubrics**
Scoring guidance is too general and subjective.

**Current**: "Score 0.9+ for preserved terms"
**Better**: Detailed rubric with specific examples for each score range

### **4. No Evaluation Process Structure**
Prompts don't guide the LLM through a systematic evaluation methodology.

## 🎯 Enhancement Opportunities

### **Priority 1: Add Chain-of-Thought Reasoning**
```
EVALUATION PROCESS:
1. ANALYZE: First, examine the slug for [specific aspects]
2. COMPARE: Consider alternatives and context
3. REASON: Explain your thinking for each dimension
4. SCORE: Rate based on your analysis
5. JUSTIFY: Provide specific evidence for scores
```

### **Priority 2: Explicit Bias Mitigation**
```
BIAS AWARENESS:
- Consider multiple cultural perspectives
- Avoid over-weighting trendy terms vs timeless quality
- Balance cultural authenticity with accessibility
- Check for systematic preferences
```

### **Priority 3: Detailed Scoring Rubrics**
```
SCORING GUIDE:
0.9-1.0: Exceptional - [specific criteria with examples]
0.7-0.8: Good - [specific criteria with examples] 
0.5-0.6: Average - [specific criteria with examples]
0.3-0.4: Poor - [specific criteria with examples]
0.0-0.2: Unacceptable - [specific criteria with examples]
```

### **Priority 4: Structured Evaluation Process**
Break evaluation into clear steps rather than simultaneous dimension scoring.

## 🧪 Prototype Enhanced Prompt Structure

Based on LLM-as-a-Judge best practices:

```
# ENHANCED EVALUATION PROMPT STRUCTURE

## CONTEXT & TASK
[Clear task definition]

## EVALUATION METHODOLOGY
Step 1: ANALYZE - Systematic examination
Step 2: REASON - Explicit thinking process  
Step 3: SCORE - Evidence-based rating
Step 4: VALIDATE - Bias and consistency check

## DETAILED RUBRICS
[Specific criteria for each score level]

## BIAS MITIGATION
[Explicit bias awareness instructions]

## OUTPUT FORMAT
[Structured JSON with reasoning]
```

## 📋 Next Actions

1. **Create Enhanced Cultural Prompt**: Rewrite v2_cultural_focused with chain-of-thought
2. **A/B Test**: Compare original vs enhanced on 20 test cases
3. **Measure Improvements**: Consistency, explanation quality, score reliability
4. **Iterate Based on Results**: Refine based on what works

---

This analysis reveals our current prompts are functional but lack the sophistication of modern LLM-as-a-Judge best practices. The main improvements needed are structured reasoning, explicit bias mitigation, and detailed rubrics.