# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

**LLM-first blog post slug generator** with **V10 Competitive Enhanced AI** and **Revolutionary Dual Evaluation System** that creates SEO-friendly URL slugs from blog post URLs using culturally-aware AI analysis.

**Core Mission**: Generate SEO-optimized URL slugs for cross-border e-commerce blog content with cultural awareness for Asian markets.

**🚨 BREAKTHROUGH STATUS**: **V11a Quality Winner Discovered** - Complete A/B testing with authentic evaluation reveals V11a achieves highest overall quality (0.808) and cultural authenticity (0.850), despite 20% failure rate.

**📊 QUALITY EVALUATION COMPLETE**: Revolutionary analysis using v2_cultural_focused evaluation prompt exposes critical gap in previous A/B testing. V10's "ultimate" pattern does NOT hurt competitive scores but causes technical SEO penalties.

**🎯 BUSINESS RECOMMENDATION**: Deploy V11a with V8 fallback for best-of-both-worlds - superior quality when working, reliable fallback when failing.

**🔧 ITERATION FRAMEWORK**: Complete refactoring plan created for independent generation vs evaluation prompt iteration. See [ITERATION_REFACTORING_PLAN.md](ITERATION_REFACTORING_PLAN.md).

## Dual System Architecture

### **🔧 Legacy System (Phase 2 - Proven & Stable)**
```
src/config/evaluation_prompts/
├── current.txt + metadata/current.json           # Default balanced evaluation
├── v2_cultural_focused.txt + .json               # Cultural authenticity focus (25% weight)  
├── v3_competitive_focused.txt + .json            # Competitive differentiation focus
└── evaluation_prompt_manager.py                  # Original manager (41% refactored)
```

### **🚀 Unified System (Template-Driven - Revolutionary)**
```
src/prompts/evaluation/
├── active/cultural_focused.yaml                  # Production-ready unified prompts
├── development/                                  # Work-in-progress area
├── templates/                                    # Template-driven creation
│   ├── basic.yaml.j2                           # Balanced evaluation template
│   ├── cultural.yaml.j2                        # Cultural authenticity focused
│   └── competitive.yaml.j2                     # Competitive positioning focused  
├── archive/                                     # Version history
└── benchmarks/                                  # Performance tracking
```

### **📁 Complete Production Architecture**
```
src/
├── core/                           # Core slug generation functionality 
│   ├── slug_generator.py           # Main LLM-powered generator (V10 Production)
│   ├── content_extractor.py        # Professional web scraping
│   └── validators.py               # SEO-compliant slug validation
├── config/                         # Centralized configuration + legacy system
│   ├── settings.py                 # All configurable parameters
│   ├── constants.py                # Shared constants
│   ├── evaluation_prompt_manager.py# Legacy evaluation prompt management
│   ├── unified_prompt_manager.py   # Revolutionary unified system (NEW)
│   ├── prompts/                    # Versioned generation prompts (V1-V10)
│   └── evaluation_prompts/         # Legacy evaluation prompts
├── prompts/                        # Unified evaluation system (NEW)
│   └── evaluation/                 # Template-driven prompt development
├── cli/                           # Enhanced CLI framework (41% code reduction)
│   ├── base.py                    # Shared CLI infrastructure
│   ├── analysis.py                # Statistical analysis tools
│   └── commands/prompt.py         # Complete development lifecycle
├── evaluation/                     # LLM-as-a-Judge system (ENHANCED)
│   └── core/seo_evaluator.py      # Configurable multi-dimensional evaluation
├── utils/                          # Utilities (retry logic)
├── optimization/                   # LLM A/B testing framework
└── extensions/                     # Production batch processing
```

## Current Production Status

### **Generation System: V11a Quality Winner vs V10 Reliable**
- **V11a Performance**: 0.808 overall quality, 0.850 cultural authenticity, 80% success rate WITH retries
- **V10 Performance**: 0.790 overall quality, 0.880 brand hierarchy, 100% reliability 
- **Quality Discovery**: Complete evaluation using v2_cultural_focused reveals V11a superiority despite reliability challenges
- **Business Decision**: V11a + V8 fallback recommended for optimal quality-reliability balance

### **Evaluation System: Quality-Driven Analysis Complete ✅**
- **v2_cultural_focused**: Proven evaluation prompt prioritizing cultural authenticity and brand hierarchy
- **Quality Metrics**: 6-dimensional SEO scoring (overall, cultural_authenticity, brand_hierarchy, competitive_differentiation, click_through_potential, technical_seo)
- **A/B Testing Integration**: Complete pipeline combining generation testing with quality evaluation
- **Authenticity Validation**: 100% GPT-validated responses with API call tracing
- **Business Impact**: Exposed critical evaluation gap, enabled data-driven V11a vs V10 decision

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

### Dual Evaluation System Testing (BREAKTHROUGH)
```bash
# Test legacy evaluation system (proven & stable)
python scripts/test_evaluation_prompt_refactored.py v2_cultural_focused --sample-size 5
python scripts/compare_evaluation_prompts_refactored.py v2_cultural_focused v3_competitive_focused

# Test unified evaluation system (template-driven)
python -m cli.prompt list --verbose
python -m cli.prompt test cultural_focused --samples 5
python -m cli.prompt compare cultural_focused v2_cultural_focused

# Test both systems with real API calls
python -c "
import sys; sys.path.insert(0, 'src')
from evaluation.core.seo_evaluator import SEOEvaluator

# Legacy system (backward compatible)
evaluator_legacy = SEOEvaluator(api_key='your-key', evaluation_prompt_version='v2_cultural_focused')
print(f'Legacy: {evaluator_legacy.prompt_metadata[\"description\"]}')

# Unified system via wrapper (seamless integration)
evaluator_unified = SEOEvaluator(api_key='your-key', evaluation_prompt_version='cultural_focused')
print(f'Unified: Working seamlessly')
"

# Comprehensive dual system validation
python scripts/comprehensive_system_test.py
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

## TDD Protocol & Revolutionary Dual System Development

**🚨 MANDATORY: All development follows enhanced TDD practices with dual system architecture**

### **Enhanced AI/LLM TDD Process:**
1. **🔴 RED**: Write failing tests first (specification-driven)
2. **🟢 GREEN**: Write minimal code to pass tests
3. **🧪 INTEGRATION VALIDATION**: Prove system works end-to-end with real LLM behavior
4. **🔵 REFACTOR**: Improve code quality while preserving functionality
5. **🔄 DUAL VALIDATION**: Test both legacy and unified systems for compatibility

### **Revolutionary Phase 2+ Breakthrough: Dual System TDD**
**Legacy System Validation**: Traditional TDD missed validating actual LLM evaluation differences. Integration validation with real API calls proved:
- Cultural prompts produce measurably different results (+0.050 cultural authenticity)
- Competitive prompts enhance differentiation (+0.025 competitive scores) 
- Configuration ≠ Functionality - real LLM behavior validation required

**Unified System Innovation**: Template-driven development with comprehensive testing:
- 2-minute prompt creation from templates to production
- Built-in validation and automated testing
- Real API integration testing for both systems
- 100% backward compatibility with zero breaking changes

**AI System Testing Principle**: Mock tests validate configuration, real API calls validate AI behavior changes, dual testing ensures seamless compatibility.

## Documentation

### **🎯 Dual System Documentation**
- **🏆 [DUAL_PROMPT_SYSTEM_GUIDE.md](DUAL_PROMPT_SYSTEM_GUIDE.md)** - Complete dual system architecture guide
- **📊 [Phase 2+ Validation Results](docs/results/phase2-validation/)** - Comprehensive testing and validation
- **🔧 Legacy System**: `src/config/evaluation_prompts/` - Phase 2 proven evaluation prompts (41% refactored)
- **🚀 Unified System**: `src/prompts/evaluation/` - Revolutionary template-driven architecture

### **Comprehensive Documentation Available:**
- **Evolution History**: `docs/evolution/VERSION_HISTORY.md` - Complete V1→V10 journey
- **Debugging Patterns**: `docs/development/DEBUGGING_PATTERNS.md` - Production fixes  
- **TDD Protocol**: `docs/development/TDD_PROTOCOL.md` - Testing methodology
- **API Guide**: `docs/API_INTEGRATION_GUIDE.md` - Integration details
- **Troubleshooting**: `docs/TROUBLESHOOTING.md` - Common issues

### **Performance Data & Validation Results**: 
- **Dual System**: `docs/results/phase2-validation/` - Comprehensive dual system test results (100% success rate)
- **Generation**: `docs/evolution/results/v10/` - V10 validation results
- **Historic**: `docs/evolution/results/v6-v8/` - Breakthrough data
- **Archive**: `docs/archive/development-results/` - Complete test archives

## Known Issues & Fixes

**Critical Production Fixes Applied:**
- ✅ V10 prompt configuration (filename requirements)
- ✅ Validation constraint mismatches (version-aware config)
- ✅ Progress tracking (real-time file persistence)
- ✅ Batch resume logic (checkpoint format alignment)

**See `docs/development/DEBUGGING_PATTERNS.md` for complete debugging guide.**

## 🛡️ **AUTHENTICITY VALIDATION COMPLETE** ✅

**V11 Success Protocol** - Comprehensive validation achieved:

### **Completed Validation Checklist:**
- ✅ **Real API Integration**: All 40 generations authenticated with API call tracing
- ✅ **Version Configuration**: V11a/V11b properly added to VERSION_SETTINGS
- ✅ **TDD Implementation**: Complete RED→GREEN cycle with failing/passing tests
- ✅ **Quality Evaluation**: Multi-dimensional scoring using v2_cultural_focused
- ✅ **Business Analysis**: Complete PM decision report with quality vs reliability data

### **Authenticity Validation System:**
- **TrackedSlugGenerator**: Complete API call tracing with response fingerprinting
- **Trace Files**: 4 files with 10 authenticated API calls each (40 total)
- **Anti-Fake Safeguards**: Request/response hashing prevents simulation contamination
- **100% Success Rate**: All evaluations confirmed authentic GPT responses

### **Future Iteration Framework:**
- **Independent Testing**: Generation vs evaluation prompt iteration support
- **Results Reuse**: Avoid expensive re-generation for evaluation experiments  
- **Quality-First**: Evaluation integrated by default, not afterthought
- **See**: [ITERATION_REFACTORING_PLAN.md](ITERATION_REFACTORING_PLAN.md) for complete framework

## Environment Requirements

- Python 3.12.4
- OpenAI API key for LLM integration
- Dependencies: requests, beautifulsoup4, openai, python-dotenv
- Virtual environment recommended

## 🏆 Revolutionary Achievement: Quality-Driven AI System

This system represents a **breakthrough in LLM evaluation methodology** combining:

✅ **Quality-First Discovery**: V11a achieves highest overall quality (0.808) and cultural authenticity (0.850)  
✅ **Authenticity Validation**: 100% GPT-validated responses with comprehensive API tracing  
✅ **Evaluation Integration**: Multi-dimensional SEO scoring reveals true performance differences  
✅ **Business Intelligence**: Data-driven recommendations balancing quality vs reliability  
✅ **Future Framework**: Independent generation/evaluation iteration architecture planned  
✅ **TDD Excellence**: Complete RED→GREEN implementation with real API validation  
✅ **Anti-Fake Safeguards**: Comprehensive prevention of simulation contamination

**Status**: 🎯 **QUALITY EVALUATION BREAKTHROUGH** - First AI system with integrated authenticity validation and multi-dimensional quality assessment, enabling evidence-based prompt optimization for cross-border e-commerce excellence.

**Next Phase**: Implementation of [ITERATION_REFACTORING_PLAN.md](ITERATION_REFACTORING_PLAN.md) for systematic iteration framework supporting independent generation and evaluation prompt development.