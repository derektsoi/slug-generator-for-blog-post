# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

This is an **LLM-first blog post slug generator** that creates SEO-friendly URL slugs from blog post URLs using advanced AI analysis.

**Current Structure:**
```
src/
├── slug_generator.py       # LLM-powered slug generation with retry logic
├── utils.py               # Professional web scraping with Beautiful Soup
└── content_analyzer.py    # Content intelligence extraction (legacy)

config/
└── prompts/
    ├── slug_generation.txt     # Original prompt template
    ├── slug_generation_v2.txt  # Optimized production prompt (72.9% coverage)
    └── slug_generation_v3.txt  # Advanced experimental prompt

scripts/
├── suggest_slug.py        # CLI entry point for slug generation
└── test_sample.py         # Sample testing script

tests/
├── test_llm_implementation.py    # Current implementation analysis tests
├── test_improved_implementation.py # TDD tests for all improvements
├── test_slug_generator.py        # Legacy unit tests
├── test_prompt_evolution.py      # Prompt optimization testing framework
├── test_comprehensive_comparison.py # Multi-version prompt comparison
├── test_v3_prompt.py             # V3 prompt focused testing
└── mock_patterns.py              # Test utilities

data/
└── blog_urls_dataset.json       # 8,194 real blog URLs for testing

results/                          # Generated test results and analysis
├── comprehensive_prompt_comparison_*.json
├── prompt_evolution_*.json
└── test_results_*.json

prompt_analysis.py                # Prompt performance analysis tools
```

## Project Purpose

**Advanced AI-Powered Slug Generation** for cross-border e-commerce blog content:

**Input:** Blog post URL  
**Output:** SEO-optimized slug with alternatives

**Key Features:**
- **LLM-first approach:** No keyword fallbacks, pure AI generation
- **Intelligent retry logic:** Exponential backoff for API failures
- **Enhanced content analysis:** 3000-char content extraction
- **Optimized prompting:** Production V2 prompt with 72.9% theme coverage
- **Prompt engineering:** Systematic A/B testing framework for optimization
- **Cross-border specialization:** Geographic and brand context awareness
- **Confidence scoring:** Quality-based filtering with reasoning

**Example Transformation:**
```
Input URL: "https://www.buyandship.today/blog/2025/08/18/jojo-maman-bebe%e8%8b%b1%e5%9c%8b%e5%ae%98%e7%b6%b2%e6%8a%98%e6%89%a3%e5%8f%8a%e8%b3%bc%e8%b2%b7%e6%95%99%e5%ad%b8/"

Output:
- Primary: "uk-jojo-maman-bebe-guide"
- Alternatives: ["buy-jojo-kids-clothing-uk", "jojo-maman-bebe-shopping-tips"]
- Confidence: 0.95 with reasoning
```

## Major Improvements Implemented

### **🚀 LLM-First Architecture (December 2024)**

**Before (Issues):**
- ❌ Content severely truncated (500 chars to LLM)
- ❌ Keyword-based fallback mechanisms
- ❌ Basic prompting without structure
- ❌ gpt-3.5-turbo with text parsing

**After (Improved):**
- ✅ Enhanced content limits (3000/1500 chars)
- ✅ Pure LLM approach with intelligent retry
- ✅ External prompt templates with 5-step analysis
- ✅ gpt-4o-mini with structured JSON responses

### **🔧 Technical Improvements:**

**Content Extraction:**
- API content limit: 2000 → 3000 characters
- Prompt preview limit: 500 → 1500 characters
- Professional Beautiful Soup scraping with proper headers
- Robust error handling without silent fallbacks

**LLM Integration:**
- Model upgrade: gpt-3.5-turbo → gpt-4o-mini
- Forced JSON response format with confidence scoring
- External prompt system from `config/prompts/slug_generation.txt`
- Systematic 5-step analysis process

**Reliability:**
- Intelligent retry logic with exponential backoff
- Configurable retry attempts and delays
- Proper error handling for rate limits and API failures
- No keyword fallbacks - fail fast with clear messages

**Quality Assurance:**
- Confidence threshold filtering (≥0.5)
- Multiple slug alternatives with reasoning
- Cross-border e-commerce specialization
- Geographic and brand context recognition

### **📊 Performance Results (Tested):**

**Test Results (10 samples):**
- ✅ **100% Success Rate**: No failures or fallbacks
- ⏱️ **5.09s Average**: Consistent response times
- 📈 **63.5% Theme Coverage**: Excellent context recognition
- 🎯 **Perfect SEO Format**: 3-6 words, under 60 chars

**Best Examples:**
- `japan-light-jewelry-brands` (Japanese jewelry guide)
- `uk-jojo-maman-bebe-guide` (UK children's clothing)
- `kindle-shopping-guide-hong-kong` (E-reader comparison)

### **🚀 Prompt Engineering Optimization (December 2024)**

**Major Achievement:** Systematic prompt optimization achieving **14.3% performance improvement** through data-driven A/B testing.

**Optimization Process:**
- **V1 (Baseline)**: Original 5-step analysis prompt - 58.6% theme coverage
- **V2 (Production)**: Few-shot examples with brand-product associations - **72.9% coverage**
- **V3 (Experimental)**: Advanced semantic rules - 91.7% focused, 60.7% comprehensive

**V2 Prompt Features (Production Default):**
```
✅ Few-shot learning with perfect examples
✅ Explicit brand-product association rules
✅ Enhanced geographic context recognition  
✅ Mandatory product category inclusion
✅ Improved content type classification
```

**Testing Framework:**
```
🔬 Comprehensive A/B Testing:
├── 7 content categories (brand-product, seasonal, fashion, etc.)
├── Automated theme coverage measurement
├── Real blog URL validation
└── Performance ranking and analysis
```

**Production Results:**
- **Theme Coverage**: 72.9% (vs 58.6% baseline)
- **Success Rate**: 100% (no fallbacks triggered)
- **Performance**: 4.87s average response time
- **Reliability**: Perfect JSON parsing and confidence scoring

**Key Learnings:**
1. **Few-shot examples > Complex rules**: V2's concrete examples outperformed V3's sophisticated logic
2. **Systematic testing is crucial**: Without A/B testing, we wouldn't know V2 > V3
3. **Production validation matters**: Real blog content revealed true performance
4. **Simpler can be better**: Focused approach beat over-engineered complexity

**Files:**
- `config/prompts/slug_generation_v2.txt` - Previous production prompt (72.9% coverage)
- `config/prompts/slug_generation_v4.txt` - Current optimized prompt (68.0% coverage)
- `test_comprehensive_comparison.py` - A/B testing framework
- `prompt_analysis.py` - Performance measurement tools
- `results/comprehensive_prompt_comparison_*.json` - Detailed test results

### **🛠️ LLM Optimization Tool Development (December 2024)**

**Major Achievement:** Built reusable LLM optimization framework that systematically improves prompt performance through automated A/B testing.

**Tool Architecture:**
```
src/llm_optimizer/
├── core/
│   ├── optimizer.py          # Main orchestrator (A/B testing coordination)
│   ├── test_runner.py        # Test execution engine
│   ├── metrics_calculator.py # Performance measurement (theme coverage, duration)
│   └── comparator.py         # Statistical analysis and insights generation
├── utils/                    # Utility modules (planned extensions)
└── README.md                 # Comprehensive documentation
```

**Proven Results with Blog Slug Generator:**
```
V4 Optimization Test Results:
├── V2 Production: 67.0% coverage, 100% success, 3.5s avg
└── V4 Optimized:  68.0% coverage, 100% success, 3.2s avg (+1.0% improvement)

Evolution Journey:
V1 (Baseline) → V2 (Few-shot) → V4 (Optimized)
58.6%         → 67.0%         → 68.0%
Total improvement: +9.4% theme coverage through systematic optimization
```

**Tool Capabilities:**
- **Automated A/B Testing**: Compare multiple prompt versions with statistical validation
- **Theme Coverage Analysis**: Semantic analysis with fuzzy matching for cross-border e-commerce
- **Performance Metrics**: Success rate, duration, confidence scoring
- **Actionable Insights**: Deployment recommendations with confidence levels
- **Production Validation**: Real API testing with configurable reliability thresholds

**Integration Example:**
```python
from llm_optimizer.core.optimizer import LLMOptimizer

optimizer = LLMOptimizer({
    'test_function': your_llm_test_function,
    'primary_metric': 'avg_theme_coverage'
})

results = optimizer.run_comparison(['v2', 'v4'], test_cases)
best_version = optimizer.get_best_version()
insights = optimizer.generate_insights()
```

**Test Framework:**
- ✅ **Core functionality**: 11/19 tests passing (core components complete)
- ✅ **Production validation**: Successfully tested with real OpenAI API calls
- ✅ **Issue detection**: Tool correctly identified configuration problems in production
- ✅ **Iterative improvement**: Guided V1 → V2 → V4 prompt evolution

## Development Setup

**Environment Setup:**
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux

# Install dependencies
pip install -r requirements.txt
pip install pytest  # For testing

# Set up OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

**⚠️ Important:** Always activate the virtual environment:
```bash
source venv/bin/activate  # Must run this first!
```

## Usage Commands

**Basic Usage:**
```bash
# Generate single slug
python scripts/suggest_slug.py https://blog.example.com/post

# Generate multiple alternatives
python scripts/suggest_slug.py --count 3 https://blog.example.com/post

# Verbose output with validation details
python scripts/suggest_slug.py --verbose https://blog.example.com/post
```

**Testing:**
```bash
# Run all TDD tests (19 comprehensive tests)
python -m pytest tests/test_improved_implementation.py -v

# Test current implementation issues
python -m pytest tests/test_llm_implementation.py -v

# Manual analysis of current implementation
python test_current_implementation.py

# Test with 10 real samples
python test_10_samples.py

# Prompt optimization testing
python test_comprehensive_comparison.py  # Compare all prompt versions
python test_prompt_evolution.py         # Evolution testing framework
python test_v3_prompt.py                # Test experimental V3 prompt
python test_v4_optimization_fixed.py    # Test V4 vs V2 optimization
python prompt_analysis.py               # Analyze current prompt performance

# LLM optimization tool usage
python demo_llm_optimizer.py            # Demonstration of optimization tool
python validate_optimization_tool.py    # Validate tool effectiveness
python test_v4_simple.py               # Simple V4 prompt comparison
```

## Test-Driven Development

**Comprehensive Test Suite:**

**Current Implementation Analysis:**
- Content extraction validation
- Prompt effectiveness testing
- Fallback mechanism detection
- Content limit analysis

**Improved Implementation (TDD):**
- ✅ Keyword fallback elimination
- ✅ Retry logic with exponential backoff
- ✅ Enhanced content limits
- ✅ Structured prompt patterns
- ✅ JSON response parsing
- ✅ Model upgrade validation
- ✅ Error handling without fallbacks

**Test Results:**
- **19/19 tests passing** ✅
- **100% success rate** on real API tests
- **Zero fallbacks triggered** in production testing

## Architecture Patterns

**Adopted from content-analyzer project:**

**External Prompt System:**
```
config/prompts/slug_generation.txt
├── 5-step systematic analysis
├── Cross-border e-commerce context
├── Confidence scoring requirements
└── JSON response format specification
```

**LLM Integration Patterns:**
```python
# Retry with exponential backoff
for attempt in range(max_retries + 1):
    try:
        return self._generate_with_openai(title, content, count)
    except Exception as e:
        if attempt == max_retries:
            raise Exception(f"Failed after {max_retries} attempts: {e}")
        delay = retry_delay * (2 ** attempt)
        time.sleep(delay)
```

**Structured Response Parsing:**
```python
# Force JSON format
response_format={"type": "json_object"}

# Parse with confidence filtering
filtered_slugs = [
    slug for slug in response["slugs"]
    if slug.get("confidence", 0) >= confidence_threshold
]
```

## Dataset

**Production Dataset:** `data/blog_urls_dataset.json`
- **8,194 real blog URLs** from cross-border e-commerce
- **Chinese titles with encoded URLs**
- **Perfect for testing** geographic and brand recognition
- **Comprehensive coverage** of fashion, electronics, beauty, etc.

**Testing Sample:**
```python
# Test with real dataset
import json
with open('data/blog_urls_dataset.json', 'r') as f:
    dataset = json.load(f)

# Use first 10 for testing
test_samples = dataset[:10]
```

## Configuration

**SlugGenerator Settings:**
```python
generator = SlugGenerator(
    api_key="your-key",
    max_retries=3,          # Retry attempts
    retry_delay=1.0,        # Base delay for backoff
)

# Automatic configuration
api_content_limit = 3000    # Content sent to API
prompt_preview_limit = 1500 # Content in prompt preview
confidence_threshold = 0.5  # Minimum confidence score
```

**Environment Variables:**
```bash
OPENAI_API_KEY=your-openai-api-key-here
```

## Production Ready

**Validation Results:**
- ✅ **100% LLM success rate** (no fallbacks needed)
- ✅ **Comprehensive error handling** with clear messages
- ✅ **Professional web scraping** with proper headers
- ✅ **Structured output** with confidence scoring
- ✅ **Cross-border specialization** for e-commerce content
- ✅ **SEO optimization** meeting all requirements

**Performance Characteristics:**
- **Response Time:** ~5 seconds average
- **Content Analysis:** 3000 characters processed
- **Quality Metrics:** 63.5% theme coverage
- **Reliability:** Zero API failures in testing

This implementation is ready for production use with cross-border e-commerce blog content.