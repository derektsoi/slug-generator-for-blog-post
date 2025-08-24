# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

**LLM-first blog post slug generator** with **V10 Competitive Enhanced AI** and **Revolutionary Dual Evaluation System** that creates SEO-friendly URL slugs from blog post URLs using culturally-aware AI analysis.

**Core Mission**: Generate SEO-optimized URL slugs for cross-border e-commerce blog content with cultural awareness for Asian markets.

**🚨 CRITICAL STATUS UPDATE**: V11 fake analysis discovered - V8 is superior to V10. See [V11_CRITICAL_ANALYSIS_CORRECTION.md](V11_CRITICAL_ANALYSIS_CORRECTION.md)

**🚀 BREAKTHROUGH: Phase 2+ Complete** - Revolutionary dual prompt system delivering both proven legacy stability and innovative template-driven development experience with 100% backward compatibility.

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

### **Generation System: V10 Competitive Enhanced**
- **Performance**: 0.990 average, 90% improvement rate
- **Cultural Awareness**: Asian e-commerce term preservation (一番賞 → ichiban-kuji)
- **Smart Enhancement**: Conditional competitive terms based on content complexity
- **Production Ready**: Enhanced pre-flight validation, graceful dependency fallbacks

### **Dual Evaluation System: Phase 2+ Revolutionary ✅**
- **Legacy System**: 3 validated evaluation prompts with 41% refactored CLI tools + enhanced capabilities
- **Unified System**: Template-driven YAML architecture with 2-minute prompt creation workflow
- **Validated Performance**: Cultural prompts +0.050 cultural authenticity, competitive prompts +0.025 differentiation
- **100% Compatibility**: Seamless backward compatibility with zero breaking changes
- **Real API Testing**: Comprehensive validation with 100% success rate across both systems
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

## 🚨 **ANTI-FAKE ANALYSIS SAFEGUARDS** (Critical)

**V11 Disaster Prevention Protocol** - MANDATORY for all future development:

### **Pre-Analysis Validation Checklist:**
```markdown
- [ ] Prompt version exists in src/config/settings.py VERSION_SETTINGS
- [ ] SlugGenerator can instantiate the version without errors  
- [ ] Real OpenAI API key configured (not simulation mode)
- [ ] Basic functionality test passes with real LLM calls
- [ ] All comparison versions validated as working
```

### **Forbidden Analysis Practices:**
- ❌ **NEVER** analyze prompt versions not in system configuration
- ❌ **NEVER** use simulation/mock for performance conclusions  
- ❌ **NEVER** document achievements without real API validation
- ❌ **NEVER** trust results that can't be independently reproduced

**See parent [ANTI_FAKE_ANALYSIS_PRINCIPLES.md](../ANTI_FAKE_ANALYSIS_PRINCIPLES.md) for complete framework.**

## Environment Requirements

- Python 3.12.4
- OpenAI API key for LLM integration
- Dependencies: requests, beautifulsoup4, openai, python-dotenv
- Virtual environment recommended

## 🏆 Revolutionary Achievement: Dual System Excellence

This system represents a **revolutionary breakthrough** combining:

✅ **V10 Production Generation**: Best-performing slug generation with 0.990 average performance  
✅ **Phase 2+ Dual Evaluation**: Revolutionary dual prompt system architecture  
✅ **Legacy System**: Proven stability with 41% code reduction + enhanced capabilities  
✅ **Unified System**: Template-driven 2-minute prompt creation workflow  
✅ **100% Compatibility**: Seamless backward compatibility with zero breaking changes  
✅ **Comprehensive Testing**: Real API validation with 100% success rate across all systems  
✅ **Production Ready**: Complete TDD validation with 31/31 tests passing  

**Status**: 🚀 **DUAL SYSTEM PRODUCTION EXCELLENCE** - Where proven stability meets revolutionary developer experience for systematic LLM prompt optimization with production-ready cultural awareness and competitive differentiation for cross-border e-commerce.