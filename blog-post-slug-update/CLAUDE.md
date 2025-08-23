# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

**LLM-first blog post slug generator** with **V10 Competitive Enhanced AI** that creates SEO-friendly URL slugs from blog post URLs using culturally-aware AI analysis.

**Core Mission**: Generate SEO-optimized URL slugs for cross-border e-commerce blog content with cultural awareness for Asian markets.

## Architecture

```
src/
├── core/                           # Core functionality 
│   ├── slug_generator.py           # Main LLM-powered generator
│   ├── content_extractor.py        # Professional web scraping
│   └── validators.py               # SEO-compliant slug validation
├── config/                         # Centralized configuration
│   ├── settings.py                 # All configurable parameters
│   └── prompts/                    # Versioned prompts (V1-V10)
├── utils/                          # Utilities (retry logic)
├── optimization/                   # LLM A/B testing framework
└── extensions/                     # Production batch processing
```

## Current Production Status (V10)

**V10 Competitive Enhanced** - Best-performing prompt combining breakthrough insights:
- **Performance**: 0.990 average, 90% improvement rate
- **Cultural Awareness**: Asian e-commerce term preservation (一番賞 → ichiban-kuji)
- **Smart Enhancement**: Conditional competitive terms based on content complexity
- **Production Ready**: Enhanced pre-flight validation, graceful dependency fallbacks

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
# Test different prompt versions
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

### Testing
```bash
# Run test suite
python -m pytest tests/unit/ -v                    # Unit tests
python -m pytest tests/integration/ -v             # Integration tests

# A/B Testing Framework
python tests/performance/test_prompt_versions.py --enhanced --versions v10 v8 --urls 10

# Production validation
python scripts/evaluate_v10.py
```

## Configuration

**SlugGenerator Settings:**
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

**🚨 MANDATORY: All development follows TDD practices**
1. **🔴 RED**: Write failing tests first
2. **🟢 GREEN**: Write minimal code to pass
3. **🔵 REFACTOR**: Improve while keeping tests green

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