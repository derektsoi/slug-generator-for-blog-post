# Evaluation Prompt Authoring Guide

**Complete guide to creating and optimizing evaluation prompts for the configurable LLM-as-a-Judge system.**

## Overview

The configurable evaluation system enables developers to create custom evaluation prompts that determine how slugs are assessed across multiple SEO dimensions. This guide covers best practices for authoring effective evaluation prompts.

## Quick Start

### Creating a New Evaluation Prompt

1. **Create prompt file**: `src/config/evaluation_prompts/v4_custom.txt`
2. **Create metadata file**: `src/config/evaluation_prompts/metadata/v4_custom.json`
3. **Test your prompt**: `python scripts/test_evaluation_prompt.py v4_custom`
4. **Validate configuration**: `python scripts/validate_evaluation_prompt.py v4_custom`

## Evaluation Prompt Structure

### Template Format

Evaluation prompts use string templating with three required placeholders:

```
Evaluate this SEO slug across multiple dimensions:

SLUG: "{slug}"
ORIGINAL TITLE: "{title}"  
CONTENT PREVIEW: "{content}"

[Your custom evaluation instructions...]

Return JSON format:
{{
    "dimension_scores": {{
        "user_intent_match": 0.0-1.0,
        "brand_hierarchy": 0.0-1.0,
        // ... other dimensions
    }},
    "overall_score": 0.0-1.0,
    "qualitative_feedback": "detailed analysis...",
    "confidence": 0.0-1.0
}}
```

### Required Placeholders

- `{slug}` - The generated slug to evaluate
- `{title}` - Original blog post title  
- `{content}` - Content preview (first 500 characters)

## Scoring Dimensions

### Default Dimensions

The system supports these standard scoring dimensions:

1. **user_intent_match** (0.0-1.0)
   - How well the slug captures user search intent
   - Focus: keyword relevance, search behavior alignment

2. **brand_hierarchy** (0.0-1.0)  
   - Brand name positioning and recognition
   - Focus: brand prominence, competitive differentiation

3. **cultural_authenticity** (0.0-1.0)
   - Preservation of cultural terms and context
   - Focus: Asian e-commerce terminology, authentic expressions

4. **click_through_potential** (0.0-1.0)
   - Likelihood to generate clicks in search results
   - Focus: compelling language, user engagement

5. **competitive_differentiation** (0.0-1.0)
   - How well slug stands out from alternatives
   - Focus: unique positioning, memorable elements

6. **technical_seo** (0.0-1.0)
   - SEO compliance and structure quality
   - Focus: length, readability, keyword placement

### Custom Dimensions

You can define custom scoring dimensions in your metadata file:

```json
{
  "scoring_dimensions": [
    "user_intent_match",
    "brand_hierarchy", 
    "cultural_authenticity",
    "custom_ecommerce_focus",  // Custom dimension
    "technical_seo"
  ]
}
```

## Prompt Optimization Strategies

### 1. Cultural-Focused Evaluation

**Use Case**: Prioritize cultural authenticity for Asian markets

```
HIGH PRIORITY: Evaluate cultural term preservation
- Rate cultural_authenticity highly if original terms like "一番賞" → "ichiban-kuji" are preserved
- Penalize generic replacements like "anime merchandise" for specific cultural items
- Reward authentic expressions over literal translations
```

**Weight Configuration**:
```json
"dimension_weights": {
  "cultural_authenticity": 0.3,  // Higher weight
  "brand_hierarchy": 0.25,
  "user_intent_match": 0.15,
  "click_through_potential": 0.1,
  "competitive_differentiation": 0.1,
  "technical_seo": 0.1
}
```

### 2. Competitive-Focused Evaluation

**Use Case**: Emphasize competitive differentiation

```
COMPETITIVE ANALYSIS REQUIRED:
- Assess how well slug stands out from generic alternatives
- Reward unique positioning and memorable elements  
- Consider competitive landscape in scoring
- High scores for innovative approaches
```

**Weight Configuration**:
```json
"dimension_weights": {
  "competitive_differentiation": 0.25,  // Higher weight
  "click_through_potential": 0.2,
  "user_intent_match": 0.2,
  "brand_hierarchy": 0.15,
  "cultural_authenticity": 0.1,
  "technical_seo": 0.1
}
```

### 3. Balanced Evaluation

**Use Case**: Equal consideration across all dimensions

```json
"dimension_weights": {
  "user_intent_match": 0.17,
  "brand_hierarchy": 0.17,
  "cultural_authenticity": 0.16,
  "click_through_potential": 0.17,
  "competitive_differentiation": 0.16,
  "technical_seo": 0.17
}
```

## Best Practices

### Writing Effective Prompts

1. **Be Specific**: Provide clear, actionable evaluation criteria
2. **Use Examples**: Include good/bad examples for context
3. **Set Priorities**: Clearly indicate which aspects matter most
4. **Define Quality**: Explain what constitutes high vs low scores
5. **Maintain Consistency**: Use consistent language and structure

### Common Patterns

#### Emphasis Markers
```
HIGH PRIORITY: [Critical evaluation aspect]
IMPORTANT: [Secondary consideration]
CONSIDER: [Additional factor]
```

#### Quality Thresholds
```
Score 0.8-1.0: Excellent alignment with criteria
Score 0.6-0.7: Good performance with minor issues  
Score 0.4-0.5: Moderate performance, room for improvement
Score 0.0-0.3: Poor performance, significant issues
```

#### Context-Specific Instructions
```
For Asian e-commerce content:
- Preserve cultural terminology (一番賞 → ichiban-kuji)
- Maintain brand authenticity (大國藥妝 → daikoku-drugstore)
- Consider cross-cultural appeal
```

## Metadata Configuration

### Complete Metadata Example

```json
{
  "prompt_version": "v4_custom",
  "description": "Custom evaluation focusing on e-commerce conversion optimization",
  "focus_areas": ["conversion_optimization", "brand_appeal"],
  "scoring_dimensions": [
    "user_intent_match",
    "brand_hierarchy", 
    "cultural_authenticity",
    "click_through_potential",
    "competitive_differentiation",
    "technical_seo"
  ],
  "dimension_weights": {
    "click_through_potential": 0.25,
    "user_intent_match": 0.2,
    "brand_hierarchy": 0.2,
    "competitive_differentiation": 0.15,
    "cultural_authenticity": 0.1,
    "technical_seo": 0.1
  },
  "quality_thresholds": {
    "minimum_confidence": 0.7,
    "conversion_focus_threshold": 0.8
  },
  "created_date": "2025-01-23",
  "author": "developer",
  "use_cases": [
    "ecommerce_conversion_optimization",
    "click_through_rate_improvement"
  ]
}
```

### Required Fields

- `prompt_version`: Unique identifier
- `scoring_dimensions`: List of dimensions to evaluate
- `dimension_weights`: Weights that sum to 1.0

### Optional Fields

- `description`: Human-readable description
- `focus_areas`: Key areas of emphasis
- `quality_thresholds`: Custom thresholds
- `use_cases`: Recommended applications

## Testing Your Prompts

### 1. Individual Testing
```bash
python scripts/test_evaluation_prompt.py v4_custom --sample-size 10 --verbose
```

### 2. Comparative Testing
```bash
python scripts/compare_evaluation_prompts.py current v4_custom --urls 20 --statistical
```

### 3. Validation
```bash
python scripts/validate_evaluation_prompt.py v4_custom --verbose
```

## Advanced Techniques

### Dynamic Context Integration

Use the enhanced configuration API for runtime customization:

```python
from evaluation.core.seo_evaluator import SEOEvaluator

evaluator = SEOEvaluator(
    api_key=api_key,
    evaluation_prompt_version="v4_custom"
)

# Customize evaluation context
evaluator.configure_context({
    'focus_areas': ['click_through_potential', 'brand_hierarchy'],
    'evaluation_style': 'detailed',
    'quality_thresholds': {'minimum_confidence': 0.8}
})

# Evaluation will use both prompt configuration and runtime context
result = evaluator.evaluate_slug(slug, title, content)
```

### Multi-Prompt Strategies

Use different evaluation prompts for different content types:

```python
def get_evaluator_for_content(content_type, api_key):
    prompt_mapping = {
        'cultural_products': 'v2_cultural_focused',
        'competitive_analysis': 'v3_competitive_focused', 
        'general_ecommerce': 'current'
    }
    
    return SEOEvaluator(
        api_key=api_key,
        evaluation_prompt_version=prompt_mapping.get(content_type, 'current')
    )
```

## Troubleshooting

### Common Issues

1. **Weights Don't Sum to 1.0**
   ```bash
   python scripts/validate_evaluation_prompt.py v4_custom
   ```

2. **Missing Placeholders**
   - Ensure `{slug}`, `{title}`, `{content}` are present

3. **Inconsistent Scoring**
   - Test with multiple samples to identify inconsistencies
   - Use statistical analysis to validate improvements

4. **Poor Performance**
   - Compare against baseline prompts
   - Check dimension weight balance
   - Validate prompt clarity and specificity

### Getting Help

- **Validation Issues**: Use `validate_evaluation_prompt.py --verbose`
- **Performance Problems**: Use comparative analysis tools
- **Configuration Errors**: Check metadata JSON syntax
- **Integration Issues**: Review API documentation

## Examples

See `docs/evaluation/examples/` for complete working examples:

- `cultural_focused_prompt.txt` - Cultural authenticity emphasis
- `competitive_focused_prompt.txt` - Competitive differentiation focus  
- `balanced_approach_prompt.txt` - Equal dimension weighting