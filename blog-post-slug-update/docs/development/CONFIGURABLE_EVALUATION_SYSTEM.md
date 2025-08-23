# Configurable LLM-as-a-Judge System

**Project Plan for Enabling Developer Control Over Evaluation Prompts**

## Problem Statement

Currently, the slug generation system has excellent configurability for generation prompts (V1→V10 evolution) but evaluation prompts are hardcoded in `SEOEvaluator._create_evaluation_prompt()`. This creates a significant developer experience gap:

- ✅ **Generation prompts**: Fully configurable with versions in `src/config/prompts/`
- ❌ **Evaluation prompts**: Hardcoded, preventing evaluation criteria iteration
- **Result**: Developers can only optimize half the LLM-as-a-Judge workflow

## Vision

Enable developers to iterate both generation AND evaluation prompts for complete prompt optimization workflows, matching the sophistication of the current generation prompt system.

## Architecture Overview

```
Current State:
Generation Prompt (Configurable) → Slug → Evaluation Prompt (Hardcoded) → Score

Target State:
Generation Prompt (Configurable) → Slug → Evaluation Prompt (Configurable) → Score
                                              ↓
                                    A/B Testing Framework
```

---

## Phase 1: Evaluation Prompt Configuration System

**Timeline**: 2-3 days  
**Goal**: Extract hardcoded evaluation prompts into configurable system matching generation prompt architecture

### 1.1 Create Evaluation Prompt Structure

**Directory Structure**:
```
src/config/evaluation_prompts/
├── current.txt                    # Default evaluation prompt (extracted from existing code)
├── v1_baseline.txt                # Simple baseline evaluation
├── v2_cultural_focused.txt        # Emphasizes cultural preservation
├── v3_competitive_focused.txt     # Emphasizes competitive appeal
├── v4_balanced.txt                # Balanced cultural + competitive
├── metadata/
│   ├── current.json               # Prompt metadata and configuration
│   ├── v2_cultural_focused.json
│   └── v3_competitive_focused.json
└── archive/                       # Historical evaluation prompts
    └── legacy_hardcoded.txt
```

**Evaluation Prompt Metadata Format**:
```json
{
  "prompt_version": "v2_cultural_focused",
  "description": "Prioritizes cultural term preservation over competitive appeal",
  "focus_areas": ["cultural_authenticity", "brand_hierarchy"],
  "scoring_dimensions": [
    "user_intent_match",
    "brand_hierarchy", 
    "cultural_authenticity",
    "click_through_potential",
    "competitive_differentiation",
    "technical_seo"
  ],
  "dimension_weights": {
    "cultural_authenticity": 0.25,
    "brand_hierarchy": 0.20,
    "user_intent_match": 0.15,
    "technical_seo": 0.15,
    "click_through_potential": 0.15,
    "competitive_differentiation": 0.10
  },
  "quality_thresholds": {
    "minimum_confidence": 0.7,
    "cultural_preservation_threshold": 0.8
  },
  "created_date": "2025-01-23",
  "author": "system",
  "use_cases": [
    "asian_ecommerce_cultural_preservation",
    "brand_focused_evaluation"
  ]
}
```

### 1.2 Refactor SEOEvaluator Class

**Key Changes**:

1. **Constructor Enhancement**:
```python
class SEOEvaluator:
    def __init__(
        self, 
        api_key: str, 
        model: str = "gpt-4o-mini",
        evaluation_prompt_version: str = "current",  # NEW
        retry_config: Optional[RetryConfig] = None
    ):
```

2. **Dynamic Prompt Loading**:
```python
def _load_evaluation_prompt(self, version: str) -> Dict[str, Any]:
    """Load evaluation prompt and metadata from config files"""
    
def _create_evaluation_prompt(self, slug: str, title: str, content: str) -> str:
    """Create evaluation prompt using configurable template"""
```

3. **Dynamic Scoring Dimensions**:
```python
@property
def scoring_dimensions(self) -> List[str]:
    """Get scoring dimensions from loaded prompt configuration"""
    return self.prompt_metadata.get('scoring_dimensions', self._default_dimensions)
```

### 1.3 Configuration Management System

**EvaluationPromptManager Class**:
```python
class EvaluationPromptManager:
    """Manages evaluation prompt versions and metadata"""
    
    def __init__(self, config_dir: str = "src/config/evaluation_prompts"):
        self.config_dir = Path(config_dir)
    
    def list_available_versions(self) -> List[str]:
        """List all available evaluation prompt versions"""
    
    def get_prompt_metadata(self, version: str) -> Dict[str, Any]:
        """Get metadata for specific prompt version"""
    
    def validate_prompt_config(self, version: str) -> Dict[str, Any]:
        """Validate prompt configuration and metadata"""
    
    def load_prompt_template(self, version: str) -> str:
        """Load raw prompt template"""
```

### 1.4 Backward Compatibility

- **Default behavior**: Use "current" version (extracted from existing hardcoded prompt)
- **API compatibility**: Existing SEOEvaluator usage continues to work
- **Migration path**: Clear documentation for upgrading to configurable system

---

## Phase 2: Developer Experience Enhancements (COMPLETED ✅)

**Status**: Successfully completed with comprehensive CLI framework refactoring achieving 41% code reduction.

### Refactoring Results (Post-Implementation):
- **CLI Framework**: Created unified framework in `src/cli/` eliminating 660 lines of duplicated code
- **Code Reduction**: 41% reduction (1,608 → 948 lines) across all CLI scripts:
  - `test_evaluation_prompt.py`: 384 → 254 lines (34% reduction)
  - `compare_evaluation_prompts.py`: 579 → 238 lines (59% reduction)  
  - `validate_evaluation_prompt.py`: 645 → 456 lines (29% reduction)
- **Enhanced Capabilities**: Added comprehensive error handling, structured logging, progress tracking, performance monitoring
- **Framework Features**: BaseCLI abstract class, TestDataMixin, PromptValidationMixin, OutputFormattingMixin, ProgressTrackingMixin
- **Maintained Functionality**: All original features preserved with improved reliability and user experience

**Documentation**: See `docs/development/CLI_FRAMEWORK.md` for complete framework documentation.

### Original Phase 2 Plan

**Timeline**: 3-4 days  
**Goal**: Make evaluation prompt iteration as intuitive as generation prompt iteration

### 2.1 Enhanced Configuration API

**Simple Configuration**:
```python
# Basic usage (unchanged)
evaluator = SEOEvaluator(api_key=api_key)

# Cultural-focused evaluation
evaluator = SEOEvaluator(
    api_key=api_key,
    evaluation_prompt_version="v2_cultural_focused"
)

# Custom evaluation configuration
evaluator = SEOEvaluator(
    api_key=api_key,
    evaluation_prompt_version="v3_competitive_focused",
    model="gpt-4o"
)
```

**Evaluation Context Configuration**:
```python
evaluator.configure_context({
    'focus_areas': ['cultural_authenticity', 'brand_hierarchy'],
    'quality_thresholds': {'minimum_confidence': 0.8},
    'evaluation_style': 'detailed'  # vs 'concise'
})
```

### 2.2 Command-Line Tools

**Evaluation Prompt Testing Script**:
```bash
# Test specific evaluation prompt version
python scripts/test_evaluation_prompt.py v2_cultural_focused --sample-size 10

# Compare evaluation prompt versions
python scripts/compare_evaluation_prompts.py current v2_cultural_focused --urls 20

# Validate evaluation prompt configuration
python scripts/validate_evaluation_prompt.py v3_competitive_focused

# Interactive evaluation prompt editor
python scripts/edit_evaluation_prompt.py --create v5_custom
```

**Example Output**:
```
🧪 TESTING EVALUATION PROMPT: v2_cultural_focused
==================================================
Sample Size: 10 slugs
Focus: Cultural authenticity preservation

Evaluation Results:
• Cultural authenticity: 0.89 avg (vs 0.72 baseline)
• Brand hierarchy: 0.85 avg  
• Technical SEO: 0.81 avg
• Overall confidence: 0.87

✅ Strengths:
- Excellent cultural term recognition (ichiban-kuji → 0.95)
- Strong brand preservation (daikoku-drugstore → 0.92)

⚠️ Areas for improvement:
- Lower competitive appeal scoring vs baseline
- May be too strict on technical SEO
```

### 2.3 Documentation & Examples

**Developer Guide Structure**:
```
docs/evaluation/
├── EVALUATION_PROMPT_AUTHORING.md     # How to create evaluation prompts
├── SCORING_DIMENSIONS_GUIDE.md        # Understanding evaluation criteria
├── EVALUATION_PATTERNS.md             # Common evaluation strategies
├── TROUBLESHOOTING_EVALUATION.md      # Debugging evaluation issues
└── examples/
    ├── cultural_focused_prompt.txt
    ├── competitive_focused_prompt.txt
    └── balanced_approach_prompt.txt
```

**Key Documentation Topics**:
- Evaluation prompt syntax and structure
- Scoring dimension definitions and trade-offs
- Cultural vs competitive evaluation approaches
- Quality assurance patterns for evaluation prompts
- Integration with generation prompt optimization

### 2.4 IDE Integration

**VSCode Extension Features**:
- Evaluation prompt syntax highlighting
- Metadata schema validation
- Live preview of evaluation criteria
- Integration with A/B testing results

---

## Phase 3: Dual-Prompt A/B Testing Framework

**Timeline**: 4-5 days  
**Goal**: Enable comprehensive A/B testing of generation+evaluation prompt combinations

### 3.1 Enhanced LLMOptimizer Architecture

**Multi-Dimensional Testing Configuration**:
```python
config = {
    'generation_versions': ['v10', 'v8', 'v6'],           # Generation prompts
    'evaluation_versions': ['current', 'v2_cultural'],    # Evaluation prompts  
    'test_matrix': 'full',  # 'full' = all combinations, 'paired' = 1:1 mapping
    'primary_metric': 'avg_theme_coverage',
    'evaluation_metrics': ['consistency', 'discrimination'], # NEW
    'sample_size': 20
}

optimizer = LLMOptimizer(config)
results = optimizer.run_dual_prompt_comparison()
```

**Results Structure**:
```python
{
    'generation_evaluation_matrix': {
        ('v10', 'current'): {'avg_theme_coverage': 0.89, 'consistency': 0.85},
        ('v10', 'v2_cultural'): {'avg_theme_coverage': 0.91, 'consistency': 0.88},
        ('v8', 'current'): {'avg_theme_coverage': 0.85, 'consistency': 0.82},
        ('v8', 'v2_cultural'): {'avg_theme_coverage': 0.87, 'consistency': 0.90}
    },
    'best_combination': ('v10', 'v2_cultural'),
    'evaluation_insights': {
        'v2_cultural_advantages': ['Higher cultural scores', 'More consistent'],
        'current_advantages': ['Faster evaluation', 'Lower API cost']
    }
}
```

### 3.2 Evaluation-Focused A/B Testing

**Evaluation Consistency Analysis**:
```python
class EvaluationConsistencyAnalyzer:
    """Analyze consistency and quality of evaluation prompts"""
    
    def test_evaluation_stability(self, evaluation_version: str, test_cases: List):
        """Test how consistently an evaluation prompt scores identical inputs"""
    
    def compare_evaluation_discrimination(self, versions: List[str]):
        """Compare how well different evaluation prompts distinguish quality levels"""
    
    def analyze_evaluation_bias(self, version: str):
        """Detect potential biases in evaluation criteria"""
```

**Cross-Validation Testing**:
```python
# Test same slugs with multiple evaluation prompts
evaluator_a = SEOEvaluator(evaluation_prompt_version="current")
evaluator_b = SEOEvaluator(evaluation_prompt_version="v2_cultural")

consistency_results = cross_validate_evaluators([evaluator_a, evaluator_b], test_slugs)
```

### 3.3 Co-Evolution Analysis

**Generation-Evaluation Interaction Analysis**:
```python
class CoEvolutionAnalyzer:
    """Analyze how generation and evaluation prompt changes interact"""
    
    def analyze_prompt_alignment(self, gen_version: str, eval_version: str):
        """Analyze alignment between generation and evaluation approaches"""
    
    def recommend_evaluation_updates(self, generation_changes: Dict):
        """Recommend evaluation prompt updates based on generation changes"""
    
    def detect_evaluation_drift(self, historical_results: List):
        """Detect when evaluation criteria become misaligned with generation goals"""
```

**Synchronized Optimization**:
- Automatic evaluation prompt suggestions when generation prompts evolve
- Detection of generation-evaluation misalignment
- Co-evolution tracking across prompt version changes

### 3.4 Advanced Testing Workflows

**Comprehensive Testing Pipeline**:
```bash
# Full dual-prompt optimization workflow  
python scripts/dual_prompt_optimization.py \
    --generation-versions v10,v8 \
    --evaluation-versions current,v2_cultural,v3_competitive \
    --test-matrix full \
    --sample-size 50 \
    --export-results results/dual_prompt_analysis.json

# Evaluation prompt development workflow
python scripts/develop_evaluation_prompt.py \
    --base-version current \
    --focus cultural_preservation \
    --validate-against v10_generation \
    --test-sample 20
```

---

## Phase 4: Advanced Evaluation Features (Future)

**Timeline**: 5-7 days (Future enhancement)  
**Goal**: Professional-grade evaluation prompt development ecosystem

### 4.1 Evaluation Prompt Validation

- **Schema validation**: Enforce evaluation prompt structure
- **Conflict detection**: Identify contradictory evaluation criteria  
- **Quality metrics**: Measure evaluation prompt effectiveness
- **Regression testing**: Ensure evaluation changes don't break existing workflows

### 4.2 Evaluation Analytics

- **Inter-evaluator agreement**: Statistical analysis of evaluation consistency
- **Dimension correlation**: Understand relationships between scoring dimensions
- **Performance dashboards**: Visual evaluation prompt performance tracking
- **Historical trending**: Track evaluation prompt evolution over time

### 4.3 Meta-Evaluation System

- **Evaluating the evaluators**: Assessment of evaluation prompt quality
- **Automatic prompt tuning**: Data-driven evaluation prompt optimization  
- **Criteria recommendation**: Suggest new evaluation dimensions based on data
- **Evaluation prompt evolution**: Systematic improvement of evaluation methodology

---

## Implementation Guidelines

### Code Quality Standards

- **TDD Protocol**: All development follows RED-GREEN-REFACTOR cycle
- **Backward Compatibility**: Existing APIs continue to work unchanged
- **Error Handling**: Graceful degradation when evaluation configs invalid
- **Documentation**: Comprehensive docs for each new feature

### Testing Strategy

- **Unit Tests**: All new evaluation prompt functionality
- **Integration Tests**: End-to-end dual-prompt testing workflows
- **Performance Tests**: Evaluation prompt performance impact
- **User Acceptance Tests**: Developer experience validation

### Migration Strategy

- **Phase 1**: Extract existing prompts, maintain compatibility
- **Phase 2**: Add new features alongside existing functionality  
- **Phase 3**: Gradual migration of existing workflows
- **Phase 4**: Advanced features built on stable foundation

---

## Success Metrics

### Developer Experience
- **Time to iterate**: Reduce evaluation prompt iteration time by 80%
- **Learning curve**: New developers productive with evaluation prompts in <2 hours
- **Feature adoption**: >90% of prompt iterations use configurable evaluation

### System Performance  
- **Evaluation quality**: Improve evaluation consistency by 25%
- **Optimization effectiveness**: 50% improvement in dual-prompt optimization outcomes
- **Development velocity**: 3x faster evaluation prompt experimentation

### Business Impact
- **Prompt quality**: Higher quality generation-evaluation combinations
- **Innovation speed**: Faster development of new evaluation approaches
- **Competitive advantage**: More sophisticated LLM-as-a-Judge capabilities than alternatives

---

## Risk Mitigation

### Technical Risks
- **Complexity**: Phase-by-phase rollout reduces integration complexity
- **Performance**: Caching and optimization for evaluation prompt loading
- **Compatibility**: Extensive testing ensures backward compatibility

### User Experience Risks  
- **Learning curve**: Comprehensive documentation and examples
- **Migration effort**: Automated migration tools and clear upgrade paths
- **Feature discoverability**: CLI tools and IDE integration

### Business Risks
- **Development time**: Phased approach allows value delivery throughout development
- **Resource allocation**: Clear priority ordering focuses effort on highest-value features
- **Adoption risk**: Backward compatibility ensures gradual, low-risk adoption

---

This configurable evaluation system will transform the LLM-as-a-Judge development experience, enabling the same sophisticated prompt optimization that drove the V1→V10 generation prompt evolution, but applied to evaluation methodology as well.