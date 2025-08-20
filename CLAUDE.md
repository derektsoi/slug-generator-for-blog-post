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
- `blog-post-slug-update/` - **Advanced LLM-first blog post slug generator** with systematic optimization framework

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

**🚀 Major Achievement:** Built production-ready LLM optimization framework that systematically improves prompt performance through A/B testing, achieving 25% improvement in brand detection for cross-border e-commerce SEO.

```bash
cd blog-post-slug-update
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Generate slug (uses V5 brand-focused prompt)
python scripts/suggest_slug.py https://blog.example.com/post

# Test optimization framework
python test_v5_brand_samples.py      # Test brand detection
python demo_llm_optimizer.py         # Demonstrate optimization tool
```

**Optimization Results:**
```
Prompt Evolution with Brand-Weighted Scoring:
V1 Baseline   → V2 Few-shot  → V4 Regression → V5 Brand-First
58.6% themes  → 49.2% brands → 52.5% brands  → 64.2% brands (+25% brand detection)

Key Discovery: Traditional metrics hid brand regression in V4.
Brand-weighted scoring (3x weight) revealed V5's true superiority.
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

**Breakthrough Achievement:** Developed in `blog-post-slug-update/` and now available as reusable framework for any LLM application requiring systematic prompt improvement.

**Framework Components:**
```
src/llm_optimizer/
├── core/optimizer.py          # A/B testing orchestrator
├── core/test_runner.py        # Test execution engine
├── core/metrics_calculator.py # Performance measurement
└── core/comparator.py         # Statistical analysis
```

**Proven Methodology:**
1. **Systematic A/B Testing**: Compare multiple prompt versions with automated metrics
2. **Statistical Validation**: Effect size analysis and significance testing
3. **Production Testing**: Real API calls with configurable reliability thresholds
4. **Actionable Insights**: Deployment recommendations with confidence levels

**Integration Pattern for Any LLM Application:**
```python
from llm_optimizer.core.optimizer import LLMOptimizer

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
- **V1 → V5 Evolution**: 58.6% → 64.2% brand-weighted performance (+25% brand detection)
- **Framework Validation**: Successfully detected V4 regression through proper metrics
- **Production Ready**: 88% success rate, 3.2s response time, 75% brand detection

## Navigation

- **For Content Analyzer work**: See `claude-code-curriculum/week-1-foundation/content-analyzer/CLAUDE.md`
- **For Blog Slug Generator work**: See `blog-post-slug-update/CLAUDE.md`
- **For LLM Optimization Framework**: See `blog-post-slug-update/src/llm_optimizer/README.md`

This repository demonstrates systematic AI development across multiple projects with shared security practices and reusable optimization frameworks.