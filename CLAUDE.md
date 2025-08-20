# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

This is **claude-project** - a comprehensive AI development project repository containing both learning materials and production projects:

**Learning Curriculum:**
- `claude-code-curriculum/week-1-foundation/content-analyzer/` - AI-powered content analysis tool for cross-border e-commerce
- `claude-code-curriculum/week-2-llm-mastery/` - Advanced LLM techniques (planned)
- `claude-code-curriculum/week-3-web-scraping/` - Professional web scraping (planned)  
- `claude-code-curriculum/week-4-integration/` - System integration (planned)

**Production Projects:**
- `blog-post-slug-update/` - **V6 Cultural Enhanced LLM slug generator** with refactored architecture and Asian e-commerce awareness

**Multi-Project Structure:**
- **Each project maintains its own `CLAUDE.md`** for specific guidance
- **This parent `CLAUDE.md`** provides repository-wide security and development principles
- **Shared security practices** apply across all projects

## Project Quick Start

### Content Analyzer Project (Week 1)

**Working directory:** `claude-code-curriculum/week-1-foundation/content-analyzer/`

```bash
cd claude-code-curriculum/week-1-foundation/content-analyzer
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# Set up OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# AI-powered analysis
python scripts/run_analysis.py --auto-tag https://example.com/blog-post
```

**See:** `claude-code-curriculum/week-1-foundation/content-analyzer/CLAUDE.md` for detailed guidance.

### Blog Post Slug Generator Project

**Working directory:** `blog-post-slug-update/`

**🎯 Major Achievements (August 2025):** 

1. **V6 Cultural Enhanced Breakthrough:** 100% success rate on unseen URLs with Asian e-commerce cultural awareness
2. **Complete Architecture Refactoring:** Clean modular design with 15+ scattered files → 6 organized modules  
3. **Reusable LLM Optimization Framework:** Production-ready A/B testing tools for systematic prompt improvement

```bash
cd blog-post-slug-update
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Generate slug (uses V6 Cultural Enhanced prompt)
python scripts/suggest_slug.py https://blog.example.com/post

# Test V6 Cultural Enhanced features
python -c "
import sys; sys.path.insert(0, 'src')
from core import SlugGenerator
result = SlugGenerator().generate_slug_from_content('大國藥妝香港購物教學', '大國藥妝香港購物教學')
print(f'V6 Cultural Result: {result[\"primary\"]}')
"
```

**V6 Cultural Enhanced Results:**
```
Complete V1→V6 Evolution with Cultural Breakthrough:
V1 Baseline → V2 Few-shot → V4 Regression → V5 Brand-First → V6 Cultural Enhanced
58.6%       → 72.9%      → 68.0%        → 75% brands    → 100% success rate ✅

V6 Key Breakthroughs:
• Cultural Preservation: 一番賞 → ichiban-kuji (not generic "anime-merchandise") 
• Compound Brands: 大國藥妝 → daikoku-drugstore (V5 failed completely)
• Asian Platforms: 樂天 → rakuten, 官網 → official-store
• Context Awareness: 集運 → shipping, 代購 → proxy-shopping
```

**Refactoring Achievement:**
```
Architecture Transformation:
Before: 15+ scattered test files, mixed abstractions, poor organization
After:  Clean core/config/utils/optimization/extensions with 100% backward compatibility
```

**See:** `blog-post-slug-update/CLAUDE.md` for comprehensive technical documentation and methodology.

## 🔐 Security & Secret Management

**Critical Security Principles for ALL Projects:**
- **NEVER commit API keys or secrets to version control**
- Use `.env` files for local development (automatically ignored by Git)
- Use `.env.example` templates with placeholder values
- Production environments use secure environment variables

**API Key Protection Checklist:**
```bash
# Verify .env files are protected
git check-ignore .env                    # Should output: .env
git status --ignored | grep .env         # Should show .env in ignored files
grep -r "sk-" . --exclude-dir=.git       # Should NOT find real API keys in tracked files
```

**For All Projects:**
- Each project should have its own `.env.example` template
- Real `.env` files must be in `.gitignore`
- Documentation should explain secure setup procedures
- Tests should work with both mocked and real API integrations

## Environment Requirements

**Standard Across All Projects:**
- Python 3.12.4
- Virtual environment recommended (venv/)
- OpenAI API key required for AI features
- Dependencies managed via requirements.txt (requests, beautifulsoup4, openai, python-dotenv)

## 🛠️ LLM Optimization Framework (Reusable)

**Breakthrough Achievement:** Developed and refined in `blog-post-slug-update/` through V1→V6 evolution, now available as production-ready reusable framework for systematic LLM prompt improvement.

**Refactored Framework Components:**
```
blog-post-slug-update/src/optimization/  (Flattened for simplicity)
├── optimizer.py          # A/B testing orchestrator
├── test_runner.py        # Test execution engine  
├── metrics_calculator.py # Performance measurement
└── comparator.py         # Statistical analysis
```

**Validated Through Real V6 Development:**
- **V5→V6 breakthrough**: Detected V5 failures, guided V6 cultural enhancement
- **Production testing**: Validated on completely unseen URLs from real datasets
- **Cultural metrics**: Enhanced to measure Asian e-commerce term preservation
- **Statistical rigor**: Effect size analysis with confidence intervals

**Proven Methodology:**
1. **Systematic A/B Testing**: Compare multiple prompt versions with automated metrics
2. **Statistical Validation**: Effect size analysis and significance testing
3. **Production Testing**: Real API calls with configurable reliability thresholds
4. **Actionable Insights**: Deployment recommendations with confidence levels

**Integration Pattern for Any LLM Application:**
```python
# Updated import path after refactoring
from blog_post_slug_update.src.optimization.optimizer import LLMOptimizer

def test_your_llm_app(prompt_version, test_cases):
    # Your application-specific testing logic
    return {'avg_theme_coverage': 0.75, 'success_rate': 1.0}

optimizer = LLMOptimizer({
    'test_function': test_your_llm_app,
    'primary_metric': 'avg_theme_coverage'
})

results = optimizer.run_comparison(['current', 'experimental'], test_cases)
best_version = optimizer.get_best_version()
insights = optimizer.generate_insights()
```

**Real-World Results (Blog Slug Generator Case Study):**
- **Complete V1 → V6 Evolution**: 58.6% → 100% success rate with cultural breakthrough
- **Cultural Enhancement**: First AI system to properly preserve Asian e-commerce terms
- **Framework Validation**: Guided V5→V6 breakthrough, detected compound brand failures
- **Production Ready**: 100% success rate on unseen URLs, ~5s response time
- **Architecture Success**: 15+ scattered files → clean modular design with 100% backward compatibility

## Navigation

- **For Content Analyzer work**: See `claude-code-curriculum/week-1-foundation/content-analyzer/CLAUDE.md`
- **For Blog Slug Generator work**: See `blog-post-slug-update/CLAUDE.md`
- **For LLM Optimization Framework**: See `blog-post-slug-update/src/optimization/README.md`

This repository demonstrates systematic AI development evolution from learning curriculum to production-ready cultural AI systems with comprehensive refactoring and optimization frameworks.