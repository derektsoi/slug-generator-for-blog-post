# LLM Optimization Tool

A reusable framework for systematic LLM prompt optimization through data-driven A/B testing, automated metrics collection, and statistical analysis.

## 🎯 Purpose

Transform manual prompt optimization into a systematic, reproducible process:

**Before (Manual):**
- Trial-and-error prompt adjustments
- Subjective performance evaluation  
- No systematic comparison methodology
- Difficult to measure improvement

**After (Automated):**
- Systematic A/B testing across prompt versions
- Quantitative metrics (theme coverage, success rate, duration)
- Statistical significance testing
- Automated insights and deployment recommendations

## ⚡ Quick Start

```python
from llm_optimizer.core.optimizer import LLMOptimizer

# Define your test function
def test_my_llm_app(prompt_version, test_cases):
    # Your LLM application testing logic here
    return {'avg_theme_coverage': 0.75, 'success_rate': 1.0}

# Configure optimizer
config = {
    'test_function': test_my_llm_app,
    'metrics': ['avg_theme_coverage', 'success_rate', 'duration'],
    'primary_metric': 'avg_theme_coverage'
}

optimizer = LLMOptimizer(config)

# Run optimization
test_cases = [{'input': 'test', 'expected': ['theme1', 'theme2']}]
results = optimizer.run_comparison(['v1', 'v2', 'v3'], test_cases)

# Get best version and insights
best_version = optimizer.get_best_version()
insights = optimizer.generate_insights()
```

## 🏗️ Architecture

### Core Components

```
llm_optimizer/
├── core/
│   ├── optimizer.py          # Main optimization orchestrator
│   ├── test_runner.py        # Test execution engine
│   ├── metrics_calculator.py # Performance measurement
│   └── comparator.py         # A/B testing and statistical analysis
├── utils/                    # Utility modules (planned)
├── cli/                      # Command-line interface (planned)
└── config/                   # Configuration management (planned)
```

### Component Responsibilities

**LLMOptimizer** (Main Orchestrator):
- Coordinates A/B testing workflow
- Manages prompt version comparison
- Generates optimization insights
- Exports comprehensive results

**TestRunner** (Execution Engine):
- Executes test cases across prompt versions
- Collects performance metrics
- Handles error cases and timeouts
- Aggregates results with statistics

**MetricsCalculator** (Performance Measurement):
- Theme coverage calculation with fuzzy matching
- Duration measurement with context managers
- SEO compliance checking
- Failure pattern analysis

**Comparator** (Statistical Analysis):
- Version ranking by performance
- Statistical significance testing
- Insight generation and recommendations
- Trend analysis over time

## 📊 Use Cases

### 1. Blog Slug Generation Optimization

```python
def test_slug_generator(prompt_version, test_cases):
    """Test slug generator with specific prompt version"""
    generator = SlugGenerator(prompt_version=prompt_version)
    
    results = []
    for case in test_cases:
        result = generator.generate_slug(case['title'])
        
        # Calculate theme coverage
        expected = set(case['expected_themes'])
        slug_text = result['primary'].lower()
        matched = set(theme for theme in expected if theme in slug_text)
        coverage = len(matched) / len(expected)
        
        results.append({'coverage': coverage, 'success': True})
    
    return {
        'avg_theme_coverage': sum(r['coverage'] for r in results) / len(results),
        'success_rate': sum(1 for r in results if r['success']) / len(results)
    }

# Test scenarios
test_scenarios = [
    {
        "title": "英國必買童裝 JoJo Maman Bébé官網購買教學",
        "expected_themes": ["uk", "baby", "clothes", "shopping", "guide"]
    }
]

# Run optimization
optimizer = LLMOptimizer({'test_function': test_slug_generator})
results = optimizer.run_comparison(['v1', 'v2', 'v3'], test_scenarios)
```

### 2. Content Classification Optimization

```python
def test_content_classifier(prompt_version, test_cases):
    """Test content classifier with different prompts"""
    classifier = ContentClassifier(prompt_version=prompt_version)
    
    correct_predictions = 0
    total_cases = len(test_cases)
    
    for case in test_cases:
        prediction = classifier.classify(case['content'])
        if prediction == case['expected_category']:
            correct_predictions += 1
    
    return {
        'accuracy': correct_predictions / total_cases,
        'success_rate': 1.0  # All tests completed
    }
```

### 3. Translation Quality Optimization

```python
def test_translation_quality(prompt_version, test_cases):
    """Test translation quality across prompt versions"""
    translator = Translator(prompt_version=prompt_version)
    
    bleu_scores = []
    for case in test_cases:
        translation = translator.translate(case['source'])
        bleu_score = calculate_bleu(translation, case['reference'])
        bleu_scores.append(bleu_score)
    
    return {
        'avg_bleu_score': sum(bleu_scores) / len(bleu_scores),
        'success_rate': 1.0
    }
```

## 🔧 Configuration Options

### Optimizer Configuration

```python
config = {
    # Required: Function to test different prompt versions
    'test_function': your_test_function,
    
    # Optional: Metrics to collect and analyze
    'metrics': ['avg_theme_coverage', 'success_rate', 'avg_duration'],
    
    # Optional: Primary metric for ranking versions
    'primary_metric': 'avg_theme_coverage',
    
    # Optional: Minimum confidence threshold for results
    'confidence_threshold': 0.8
}
```

### Test Case Format

```python
test_cases = [
    {
        'input': 'Input to your LLM application',
        'expected': ['expected', 'themes', 'or', 'outputs'],
        'category': 'optional_category_for_analysis'
    }
]
```

### Test Function Interface

Your test function must follow this interface:

```python
def your_test_function(prompt_version: str, test_cases: List[Dict]) -> Dict[str, float]:
    """
    Test your LLM application with a specific prompt version.
    
    Args:
        prompt_version: Version identifier (e.g., 'v1', 'v2', 'baseline')
        test_cases: List of test case dictionaries
        
    Returns:
        Dictionary with metrics:
        {
            'avg_theme_coverage': 0.75,  # 0.0 to 1.0
            'success_rate': 1.0,         # 0.0 to 1.0
            'avg_duration': 4.5,         # seconds
            'any_custom_metric': 0.8     # your application-specific metrics
        }
    """
    # Your implementation here
    return metrics_dict
```

## 📈 Performance Results

### Blog Slug Generator Case Study

Using the LLM optimization tool on our blog slug generator:

```
🏆 Optimization Results:
├── V1 (Baseline): 58.6% theme coverage, 100% success rate
├── V2 (Optimized): 72.9% theme coverage, 100% success rate ⭐
└── V3 (Advanced): 60.7% theme coverage, 86% success rate

📈 Improvement: +14.3% theme coverage (V2 vs V1)
🎯 Recommendation: Deploy V2 to production
```

**Key Insights Generated:**
- V2 achieved significant improvement through few-shot examples
- V3's complexity reduced reliability despite sophistication
- Theme coverage variance indicates optimization opportunities
- Statistical significance confirmed with effect size analysis

## 🧪 Testing Framework

The tool includes comprehensive TDD test coverage:

```bash
# Run all tests
python -m pytest tests/test_llm_optimizer.py -v

# Test specific components
python -m pytest tests/test_llm_optimizer.py::TestLLMOptimizer -v
python -m pytest tests/test_llm_optimizer.py::TestMetricsCalculator -v
python -m pytest tests/test_llm_optimizer.py::TestComparator -v
```

**Test Coverage:**
- ✅ Core optimizer functionality (4/4 tests passing)
- ✅ Metrics calculation and theme coverage (3/3 tests passing)  
- ✅ Statistical comparison and insights (3/3 tests passing)
- ⏳ Test runner integration (2 tests need mock fixes)
- ⏳ CLI and utility modules (planned implementation)

## 🔬 Advanced Features

### Statistical Analysis

```python
# Check if improvement is statistically significant
comparator = Comparator()
is_significant = comparator.is_statistically_significant(
    baseline_scores=[0.58, 0.61, 0.55],
    improved_scores=[0.73, 0.75, 0.71],
    confidence_level=0.95
)
```

### Automated Insights

```python
insights = optimizer.generate_insights()

# Access structured insights
print(insights['summary']['best_version'])
print(insights['recommendations'])
print(insights['deployment_recommendation'])
print(insights['statistical_analysis'])
```

### Export and Reporting

```python
# Export comprehensive results
optimizer.export_results('results/optimization_analysis.json')

# Results include:
# - Full configuration and test parameters
# - Detailed metrics for each version
# - Statistical analysis and significance tests
# - Actionable recommendations and next steps
```

## 🚀 Integration Patterns

### 1. Existing LLM Application Integration

```python
# Minimal integration - just wrap your existing function
def test_wrapper(prompt_version, test_cases):
    # Load specific prompt version
    prompt = load_prompt(prompt_version)
    
    # Test with your existing application
    results = your_existing_app.test(prompt, test_cases)
    
    # Return standardized metrics
    return calculate_metrics(results)

optimizer = LLMOptimizer({'test_function': test_wrapper})
```

### 2. Continuous Optimization Pipeline

```python
# Schedule regular optimization
def weekly_optimization():
    test_cases = load_production_samples()
    prompt_versions = ['current', 'experimental_v1', 'experimental_v2']
    
    results = optimizer.run_comparison(prompt_versions, test_cases)
    
    if should_deploy(results):
        deploy_best_prompt(optimizer.get_best_version())
        notify_team(optimizer.generate_insights())
```

### 3. Multi-Application Optimization

```python
# Optimize multiple applications with same framework
applications = ['slug_generator', 'content_classifier', 'translator']

for app in applications:
    app_optimizer = LLMOptimizer({
        'test_function': get_test_function(app),
        'primary_metric': get_primary_metric(app)
    })
    
    results = app_optimizer.run_comparison(
        prompt_versions=['current', 'optimized'],
        test_cases=load_test_cases(app)
    )
    
    save_optimization_results(app, results)
```

## 🔮 Future Enhancements

### Planned Features

1. **CLI Interface**: Command-line tool for easy optimization workflows
2. **Prompt Management**: Automatic prompt loading and version management  
3. **Continuous Monitoring**: Performance tracking and drift detection
4. **Advanced Statistics**: More sophisticated statistical tests and analysis
5. **Visualization**: Charts and graphs for optimization results
6. **Multi-Objective Optimization**: Balance multiple competing metrics

### Extension Points

```python
# Custom metrics calculator
class CustomMetricsCalculator(MetricsCalculator):
    def calculate_custom_metric(self, data):
        # Your custom metric implementation
        pass

# Custom comparator for domain-specific analysis  
class DomainSpecificComparator(Comparator):
    def generate_domain_insights(self, results):
        # Your domain-specific insight generation
        pass
```

## 📚 References

Based on successful optimization of blog slug generation achieving:
- **14.3% improvement** in theme coverage through systematic A/B testing
- **100% reliability** maintained while improving performance
- **Statistical validation** of improvements with effect size analysis
- **Production deployment** with automated recommendation system

This tool generalizes those successful patterns into a reusable framework for any LLM application requiring systematic prompt optimization.

---

**Built with Claude Code** - Systematic LLM optimization through data-driven prompt engineering.