# CLI Framework Documentation

## Overview

The Phase 2 refactoring introduced a comprehensive CLI framework that eliminates code duplication and provides consistent functionality across all evaluation tools. The framework achieved a **41% reduction** in total CLI code (1,608 → 948 lines) while adding enhanced capabilities.

## Architecture

```
src/cli/
├── __init__.py              # Framework exports
├── base.py                  # Core CLI framework (433 lines)
└── analysis.py              # Shared statistical analysis (376 lines)

Framework Benefits:
- 660 lines of duplicated code eliminated
- Consistent error handling and logging
- Enhanced progress tracking and performance monitoring
- Standardized argument parsing and output formatting
```

## Core Classes

### BaseCLI (Abstract Base Class)

The foundation class for all CLI tools providing:

#### Key Features
- **Enhanced Error Handling**: Contextual error messages with helpful suggestions
- **Logging Integration**: Structured logging with configurable levels
- **Safe Execution**: Protected operation execution with automatic error recovery
- **API Key Management**: Secure validation and error handling
- **Progress Tracking**: Built-in progress monitoring for long operations

#### Usage Pattern
```python
from cli import BaseCLI, TestDataMixin, PromptValidationMixin, OutputFormattingMixin

class YourCLITool(BaseCLI, TestDataMixin, PromptValidationMixin, OutputFormattingMixin):
    def __init__(self):
        super().__init__(
            tool_name="your_tool.py",
            description="Your tool description"
        )
    
    def setup_parser(self) -> argparse.ArgumentParser:
        # Define your arguments
        pass
    
    def run_command(self, args: argparse.Namespace) -> Dict[str, Any]:
        # Implement your logic
        pass
```

#### Enhanced Error Handling
```python
# Automatic API error handling with context
results = self.safe_execute("evaluation operation", evaluator.evaluate_slug, slug, title, content)

# Contextual error messages
try:
    # Operation
except Exception as e:
    raise self.handle_api_error(e, "slug evaluation")
```

### Mixin Classes

#### TestDataMixin
Provides standardized test cases across all tools:
```python
# Access to 8 diverse test cases
test_cases = self.standard_test_cases
subset = self.get_test_subset(sample_size)
```

#### PromptValidationMixin  
Validates evaluation prompt versions:
```python
# Single version validation
self.validate_prompt_version(version, manager)

# Dual version validation with warnings
self.validate_prompt_versions(version_a, version_b, manager)
```

#### OutputFormattingMixin
Consistent output formatting:
```python
# Formatted headers and scores
self.print_section_header("RESULTS")
self.print_score_line("Overall Score", 0.875)
self.print_bullet_list(insights, "•")
```

#### ProgressTrackingMixin
Progress monitoring utilities:
```python
# Create progress tracker
tracker = self.create_progress_tracker(total_items, "Evaluating")
tracker.update(1, "Processing item 1")
tracker.complete("All evaluations complete")
```

## Statistical Analysis Framework

### Performance Optimizations

#### Caching System
```python
@lru_cache(maxsize=128)
def _calculate_stats_cached(self, values_tuple: tuple) -> Dict[str, float]:
    # Cached statistical calculations for repeated operations
```

#### Batch Processing
```python
batch_processor = BatchProcessor(batch_size=10)
results = batch_processor.process_in_batches(items, processor_func, progress_callback)

# Adaptive batch sizing
optimal_size = batch_processor.adaptive_batch_size(items, processor_func, target_time=5.0)
```

#### Performance Monitoring
```python
monitor = PerformanceMonitor()

@monitor.time_operation("statistical_analysis")
def analyze_data(data):
    # Automatically timed operation
    pass

stats = monitor.get_performance_stats()
# Returns: total_calls, total_time, average_time, min_time, max_time
```

## Refactored CLI Scripts

### Code Reduction Achieved

| Script | Original | Refactored | Reduction |
|--------|----------|------------|-----------|
| test_evaluation_prompt.py | 384 lines | 254 lines | **34%** |
| compare_evaluation_prompts.py | 579 lines | 238 lines | **59%** |
| validate_evaluation_prompt.py | 645 lines | 456 lines | **29%** |
| **Total** | **1,608 lines** | **948 lines** | **41%** |

### Usage Examples

#### Testing Evaluation Prompts
```bash
# Test with enhanced error handling and logging
python scripts/test_evaluation_prompt_refactored.py v2_cultural_focused --verbose --sample-size 10

# Automatic progress tracking in verbose mode
python scripts/test_evaluation_prompt_refactored.py current --verbose
```

#### Comparing Prompts
```bash
# Statistical comparison with enhanced analysis
python scripts/compare_evaluation_prompts_refactored.py v2_cultural_focused v3_competitive_focused --sample-size 10

# Comprehensive output with performance insights
python scripts/compare_evaluation_prompts_refactored.py current v2_cultural_focused --verbose
```

#### Validation
```bash
# Comprehensive validation with configuration testing
python scripts/validate_evaluation_prompt_refactored.py v2_cultural_focused --comprehensive --test-config

# Enhanced error reporting and auto-fix suggestions
python scripts/validate_evaluation_prompt_refactored.py current --verbose --auto-fix
```

## Error Handling Enhancements

### Contextual Error Messages
```python
# Before (generic)
Error: Evaluation failed with unexpected error: Invalid API key

# After (contextual)
Failed during evaluation operation: Invalid API key
Please check your OPENAI_API_KEY environment variable.
```

### Structured Error Categories
- **API Errors**: Authentication, rate limiting, timeouts
- **Validation Errors**: Prompt versions, configuration issues  
- **CLI Errors**: Argument parsing, file operations
- **Unexpected Errors**: Full stack trace in verbose mode

### Logging Integration
```python
# Structured logging with levels
self.log_info("Starting evaluation process")
self.log_warning("Large sample size detected")
self.log_error("API request failed", exception)
```

## Performance Improvements

### Statistical Analysis Caching
- **LRU Cache**: Prevents recalculation of identical statistical operations
- **Tuple Conversion**: Enables caching of list-based calculations
- **Memory Efficient**: Configurable cache size limits

### Batch Processing
- **Adaptive Sizing**: Automatically determines optimal batch sizes
- **Progress Tracking**: Real-time progress updates for long operations
- **Memory Management**: Processes large datasets in chunks

### Performance Monitoring
- **Operation Timing**: Automatic timing of critical operations  
- **Call Counting**: Track frequency of expensive operations
- **Optimization Suggestions**: Recommend optimal batch sizes based on timing data

## Migration Guide

### From Original to Refactored Scripts

#### 1. Update Imports
```python
# Old
from evaluation.core.seo_evaluator import SEOEvaluator
from config.evaluation_prompt_manager import EvaluationPromptManager

# New
from cli import BaseCLI, TestDataMixin, PromptValidationMixin, OutputFormattingMixin
```

#### 2. Inherit from Framework
```python
# Old
class EvaluationPromptTester:
    def __init__(self, api_key: str, verbose: bool = False):

# New  
class EvaluationPromptTesterRefactored(BaseCLI, TestDataMixin, PromptValidationMixin, OutputFormattingMixin):
    def __init__(self):
        super().__init__(tool_name="test_evaluation_prompt_refactored.py", description="...")
```

#### 3. Use Framework Methods
```python
# Old
try:
    result = evaluator.evaluate_slug(slug, title, content)
except Exception as e:
    print(f"Error: {e}")

# New
result = self.safe_execute("evaluation", evaluator.evaluate_slug, slug, title, content)
```

## Future Enhancements

### Planned Features
- **Configuration Templates**: Pre-built configurations for common use cases
- **Plugin System**: Extensible architecture for custom analysis modules
- **Interactive Mode**: CLI wizard for guided tool usage
- **Result Caching**: Persistent caching of expensive evaluation results
- **Parallel Processing**: Multi-threading for batch operations

### Extension Points
- **Custom Mixins**: Domain-specific functionality mixins
- **Analysis Modules**: Pluggable statistical analysis components
- **Output Formats**: Additional export formats (CSV, Excel, etc.)
- **Validation Rules**: Custom validation logic for specific use cases

This framework provides a solid foundation for consistent, maintainable CLI tools while significantly reducing code complexity and improving user experience.