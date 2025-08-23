# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

This is **claude-project** - a comprehensive AI development project repository:

**Learning Curriculum:**
- `claude-code-curriculum/week-1-foundation/content-analyzer/` - AI-powered content analysis tool
- `claude-code-curriculum/week-2-llm-mastery/` - Advanced LLM techniques (planned)
- `claude-code-curriculum/week-3-web-scraping/` - Professional web scraping (planned)  
- `claude-code-curriculum/week-4-integration/` - System integration (planned)

**Production Projects:**
- `blog-post-slug-update/` - **V10 Production LLM slug generator** with cultural awareness and batch processing

**Multi-Project Structure:**
- Each project maintains its own `CLAUDE.md` for specific guidance
- This parent `CLAUDE.md` provides repository-wide principles
- **🚨 MANDATORY TDD PROTOCOL** applies to ALL projects

## Quick Start

### Content Analyzer Project
```bash
cd claude-code-curriculum/week-1-foundation/content-analyzer
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add OPENAI_API_KEY
python scripts/run_analysis.py --auto-tag https://example.com/blog-post
```

### Blog Post Slug Generator Project
```bash
cd blog-post-slug-update
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add OPENAI_API_KEY
python scripts/suggest_slug.py https://blog.example.com/post
```

**V10 Production Status:** Best-performing prompt (0.990 average) with cultural awareness and competitive differentiation.

**See project-specific CLAUDE.md files for detailed guidance.


**Detailed Evolution History:** See `blog-post-slug-update/docs/evolution/VERSION_HISTORY.md` for complete V1→V10 journey with breakthrough achievements.

## 🐛 Debugging Patterns

**Reusable Debugging Patterns:** See `blog-post-slug-update/docs/development/DEBUGGING_PATTERNS.md` for comprehensive debugging patterns and production fixes.


## 🧪 Test-Driven Development Protocol (MANDATORY)

**🚨 CRITICAL: ALL code development must follow TDD practices - NO EXCEPTIONS**

### **Universal TDD Rules (Apply to ALL Projects):**
1. **🔴 RED FIRST**: Write failing tests before ANY implementation
2. **🟢 GREEN MINIMAL**: Write only enough code to make tests pass  
3. **🔵 REFACTOR SAFELY**: Improve code while maintaining green tests
4. **✅ VERIFY CYCLE**: Run tests before AND after each implementation step

### **TDD Enforcement Checklist:**
```bash
# BEFORE writing any code:
□ Write comprehensive failing tests
□ Verify tests fail (RED state confirmed)
□ Document expected behavior in tests

# DURING implementation:  
□ Write minimal code to satisfy tests
□ Verify tests pass (GREEN state achieved)
□ Refactor for quality while preserving tests

# AFTER each cycle:
□ Commit working changes
□ Update TDD status in CLAUDE.md
□ Plan next test cases
```

### **TDD Violation Prevention:**
- ❌ **NEVER** write production code without failing tests first
- ❌ **NEVER** skip test verification phases  
- ❌ **NEVER** implement features beyond test requirements
- ❌ **NEVER** refactor without running full test suite

### **Per-Project TDD Status:**
- **Blog Post Slug Generator**: Phase 1 Core Infrastructure (RED ✅, GREEN in progress)
- **Content Analyzer**: TDD protocol to be applied to future features
- **New Projects**: Must start with TDD from day one

**This TDD protocol supersedes all other development practices and must be followed religiously for code quality assurance.**

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
- **Complete V1 → V10 Evolution**: 58.6% → 99.0% with historic breakthrough achievements
- **V10 Production Deployment**: Best performer (0.990 average), 90% improvement rate on challenging cases
- **Cultural + Competitive Excellence**: First AI system combining cultural preservation with smart competitive differentiation
- **Infrastructure Evolution**: Enhanced pre-flight validation, graceful dependency fallbacks, V11 roadmap
- **Production Ready**: V10 default deployment with comprehensive evaluation and monitoring framework
- **Architecture Success**: 15+ scattered files → clean modular design with 100% backward compatibility

## Navigation

- **For Content Analyzer work**: See `claude-code-curriculum/week-1-foundation/content-analyzer/CLAUDE.md`
- **For Blog Slug Generator work**: See `blog-post-slug-update/CLAUDE.md`
- **For LLM Optimization Framework**: See `blog-post-slug-update/src/optimization/README.md`

This repository demonstrates systematic AI development evolution from learning curriculum to production-ready cultural AI systems with HISTORIC BREAKTHROUGH methodology proving that hypothesis-driven development and domain expertise can overcome architectural limits that pure optimization cannot solve.