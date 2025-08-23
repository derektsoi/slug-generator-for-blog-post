# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

**LLM-first blog post slug generator** with **V10 Competitive Enhanced AI** and **Configurable LLM-as-a-Judge Evaluation System** that creates SEO-friendly URL slugs from blog post URLs using culturally-aware AI analysis.

**Core Mission**: Generate SEO-optimized URL slugs for cross-border e-commerce blog content with cultural awareness for Asian markets.

**NEW: Phase 1 Complete** - Configurable evaluation prompt system enables systematic LLM-as-a-Judge optimization, matching generation prompt flexibility.

## Architecture

```
src/
├── core/                           # Core functionality 
│   ├── slug_generator.py           # Main LLM-powered generator
│   ├── content_extractor.py        # Professional web scraping
│   └── validators.py               # SEO-compliant slug validation
├── config/                         # Centralized configuration
│   ├── settings.py                 # All configurable parameters
│   ├── constants.py                # Shared constants (NEW)
│   ├── evaluation_prompt_manager.py# Evaluation prompt management (NEW)
│   ├── prompts/                    # Versioned generation prompts (V1-V10)
│   └── evaluation_prompts/         # Configurable evaluation prompts (NEW)
│       ├── current.txt             # Default evaluation prompt
│       ├── v2_cultural_focused.txt # Cultural preservation focus
│       ├── v3_competitive_focused.txt # Competitive differentiation focus
│       └── metadata/               # Prompt configuration metadata
├── evaluation/                     # LLM-as-a-Judge system (ENHANCED)
│   └── core/
│       └── seo_evaluator.py        # Configurable multi-dimensional evaluation
├── utils/                          # Utilities (retry logic)
├── optimization/                   # LLM A/B testing framework
└── extensions/                     # Production batch processing
```

## Current Production Status

### **Generation System: V10 Competitive Enhanced**
- **Performance**: 0.990 average, 90% improvement rate
- **Cultural Awareness**: Asian e-commerce term preservation (一番賞 → ichiban-kuji)
- **Smart Enhancement**: Conditional competitive terms based on content complexity
- **Production Ready**: Enhanced pre-flight validation, graceful dependency fallbacks

### **Evaluation System: Phase 1 Configurable LLM-as-a-Judge ✅**
- **Configurable Evaluation Prompts**: 3 validated versions (current, cultural-focused, competitive-focused)
- **Validated Performance**: Cultural prompts +0.050 cultural authenticity, competitive prompts +0.025 differentiation
- **Developer Experience**: Full parity with generation prompt configuration system
- **TDD Complete**: 31/31 tests passing, comprehensive integration validation with real LLM evaluation
- **Architecture**: Clean separation, backward compatibility, graceful fallbacks

## Development Setup

```bash
# Environment setup
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt

# API key setup
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Usage Commands

### Basic Usage
```bash
# Generate single slug (uses V10 by default)
python scripts/suggest_slug.py https://blog.example.com/post

# Generate multiple alternatives
python scripts/suggest_slug.py --count 3 https://blog.example.com/post

# Verbose output with validation details
python scripts/suggest_slug.py --verbose https://blog.example.com/post
```

### Version Testing
```bash
# Test different generation prompt versions
python -c "
import sys; sys.path.insert(0, 'src')
from core import SlugGenerator

# V10 Production (default)
generator = SlugGenerator()
result = generator.generate_slug_from_content('大國藥妝香港購物教學', '大國藥妝香港購物教學')
print(f'V10: {result[\"primary\"]}')

# V8 Breakthrough version
generator_v8 = SlugGenerator(prompt_version='v8')
result_v8 = generator_v8.generate_slug_from_content('Same content', 'Same content')
print(f'V8: {result_v8[\"primary\"]}')
"
```

### Configurable Evaluation Testing (NEW)
```bash
# Test different evaluation prompt versions
python -c "
import sys; sys.path.insert(0, 'src')
from evaluation.core.seo_evaluator import SEOEvaluator

# Default evaluation (current)
evaluator = SEOEvaluator(api_key='your-key')
print(f'Default: {evaluator.evaluation_prompt_version}')

# Cultural-focused evaluation
evaluator_cultural = SEOEvaluator(
    api_key='your-key',
    evaluation_prompt_version='v2_cultural_focused'
)
print(f'Cultural: {evaluator_cultural.prompt_metadata[\"description\"]}')

# Competitive-focused evaluation
evaluator_competitive = SEOEvaluator(
    api_key='your-key', 
    evaluation_prompt_version='v3_competitive_focused'
)
print(f'Competitive: {evaluator_competitive.prompt_metadata[\"description\"]}')
"
```

### Testing
```bash
# Run test suite
python -m pytest tests/unit/ -v                    # Unit tests
python -m pytest tests/integration/ -v             # Integration tests
python -m pytest tests/compatibility/ -v           # Backward compatibility tests

# Configurable Evaluation Tests (NEW)
python -m pytest tests/unit/config/ -v             # EvaluationPromptManager tests
python -m pytest tests/integration/test_llm_as_judge_evaluation.py -v  # Real LLM A/B testing

# A/B Testing Framework
python tests/performance/test_prompt_versions.py --enhanced --versions v10 v8 --urls 10

# Production validation
python scripts/evaluate_v10.py
```

## Configuration

### **Generation Configuration**
```python
generator = SlugGenerator(
    api_key="your-key",
    prompt_version="v10",       # Version selection
    max_retries=3,              # Retry attempts
    retry_delay=1.0,            # Base delay for backoff
)
```

**V10 Enhanced Constraints:**
- Max words: 10 (vs 6 in earlier versions)
- Max characters: 90 (vs 60 in earlier versions) 
- Confidence threshold: ≥0.7
- Cultural term preservation enabled

### **Evaluation Configuration (NEW)**
```python
# Basic usage (backward compatible)
evaluator = SEOEvaluator(api_key="your-key")

# Cultural-focused evaluation
evaluator = SEOEvaluator(
    api_key="your-key",
    evaluation_prompt_version="v2_cultural_focused"
)

# Competitive-focused evaluation  
evaluator = SEOEvaluator(
    api_key="your-key",
    evaluation_prompt_version="v3_competitive_focused",
    model="gpt-4o"
)
```

**Available Evaluation Versions:**
- `current`: Default balanced evaluation (backward compatible)
- `v2_cultural_focused`: Prioritizes cultural authenticity (+0.050 avg boost)
- `v3_competitive_focused`: Emphasizes competitive differentiation (+0.025 avg boost)

## Batch Processing

**Production-scale batch processing** with comprehensive features:
```python
from extensions.production_batch_processor import ProductionBatchProcessor

processor = ProductionBatchProcessor(
    batch_size=50,
    max_budget=100.0,
    checkpoint_interval=100
)

urls = [{"title": "Blog Post Title", "url": "https://example.com/post"}]
result = processor.process_urls_production(urls, resume=True)
```

**Features:**
- ✅ Cost control with pre-flight estimation
- ✅ Quality assurance with validation
- ✅ Resume support with checkpoints
- ✅ Real-time progress monitoring
- ✅ 21/21 TDD unit tests passing

## Production Examples

**V10 Cultural + Competitive Excellence:**
```
Input: "【2025年最新】日本一番賞Online手把手教學！"
V10: ultimate-ichiban-kuji-online-purchasing-masterclass

Input: "日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！"
V10: ultimate-skinnydip-iface-rhinoshield-phone-cases-guide
```

## TDD Protocol

**🚨 MANDATORY: All development follows enhanced TDD practices**

### **Enhanced AI/LLM TDD Process:**
1. **🔴 RED**: Write failing tests first (specification-driven)
2. **🟢 GREEN**: Write minimal code to pass tests
3. **🧪 INTEGRATION VALIDATION**: Prove system works end-to-end with real LLM behavior
4. **🔵 REFACTOR**: Improve code quality while preserving functionality

### **Critical Learning: Integration Validation Phase**
**Phase 1 Breakthrough**: Traditional TDD missed validating actual LLM evaluation differences. Integration validation with real API calls proved:
- Cultural prompts produce measurably different results (+0.050 cultural authenticity)
- Competitive prompts enhance differentiation (+0.025 competitive scores) 
- Configuration ≠ Functionality - real LLM behavior validation required

**AI System Testing Principle**: Mock tests validate configuration, real API calls validate AI behavior changes.

## Documentation

**Comprehensive Documentation Available:**
- **Evolution History**: `docs/evolution/VERSION_HISTORY.md` - Complete V1→V10 journey
- **Debugging Patterns**: `docs/development/DEBUGGING_PATTERNS.md` - Production fixes  
- **TDD Protocol**: `docs/development/TDD_PROTOCOL.md` - Testing methodology
- **API Guide**: `docs/API_INTEGRATION_GUIDE.md` - Integration details
- **Troubleshooting**: `docs/TROUBLESHOOTING.md` - Common issues

**Performance Data**: 
- `docs/evolution/results/v10/` - V10 validation results
- `docs/evolution/results/v6-v8/` - Historic breakthrough data
- `docs/archive/development-results/` - Complete test archives

## Known Issues & Fixes

**Critical Production Fixes Applied:**
- ✅ V10 prompt configuration (filename requirements)
- ✅ Validation constraint mismatches (version-aware config)
- ✅ Progress tracking (real-time file persistence)
- ✅ Batch resume logic (checkpoint format alignment)

**See `docs/development/DEBUGGING_PATTERNS.md` for complete debugging guide.**

## Environment Requirements

- Python 3.12.4
- OpenAI API key for LLM integration
- Dependencies: requests, beautifulsoup4, openai, python-dotenv
- Virtual environment recommended

This system represents the culmination of systematic LLM prompt optimization achieving production-ready cultural awareness and competitive differentiation for cross-border e-commerce.