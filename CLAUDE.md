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
- `blog-post-slug-update/` - **V10 Competitive Enhanced LLM slug generator** with HISTORIC BREAKTHROUGH in multi-brand handling, Asian e-commerce cultural awareness, and **production-ready batch processing extensions** (21/21 TDD tests passing)

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

**🎯 Historic Achievements (August 2025):** 

1. **V10 PRODUCTION DEPLOYMENT:** Best-performing prompt (0.990 average) combining all breakthrough insights - NOW LIVE IN PRODUCTION
2. **V9 LLM-Guided Optimization BREAKTHROUGH:** FIRST systematic use of LLM qualitative feedback for prompt optimization (+33.3% competitive differentiation)
3. **V8 Enhanced Constraints BREAKTHROUGH:** FIRST prompt to solve persistent multi-brand failures through hypothesis-driven constraint relaxation
4. **Enhanced Infrastructure:** Pre-flight validation, graceful dependency fallbacks, comprehensive evaluation framework
5. **V6 Cultural Enhanced Foundation:** 100% success rate on unseen URLs with Asian e-commerce cultural awareness
6. **Complete Architecture Refactoring:** Clean modular design with 15+ scattered files → 6 organized modules + version-aware configuration
7. **V11 Development Foundation:** Advanced semantic understanding roadmap with production monitoring framework

```bash
cd blog-post-slug-update
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Generate slug (uses V10 Competitive Enhanced prompt by default)
python scripts/suggest_slug.py https://blog.example.com/post

# Test V10 Production vs Previous Versions
python -c "
import sys; sys.path.insert(0, 'src')
from core import SlugGenerator

# V10 Competitive Enhanced (production default - best performer)
generator_v10 = SlugGenerator()  # Uses V10 by default now
result_v10 = generator_v10.generate_slug_from_content('【2025年最新】日本一番賞Online手把手教學！', '【2025年最新】日本一番賞Online手把手教學！')
print(f'🏆 V10 Production: {result_v10[\"primary\"]}')

# V8 Enhanced Constraints (historic breakthrough)
generator_v8 = SlugGenerator(prompt_version='v8')
result_v8 = generator_v8.generate_slug_from_content('日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！', '日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！')
print(f'🚀 V8 Historic Breakthrough: {result_v8[\"primary\"]}')

# V9 LLM-Guided Optimization
generator_v9 = SlugGenerator(prompt_version='v9')
result_v9 = generator_v9.generate_slug_from_content('大國藥妝香港購物教學', '大國藥妝香港購物教學')
print(f'🤖 V9 LLM-Guided: {result_v9[\"primary\"]}')
"

# Enhanced A/B Testing Framework with V10 production validation
python tests/performance/test_prompt_versions.py --enhanced --versions v10 v8 v9 --urls 10

# V10 Production Evaluation and Validation
python scripts/evaluate_v10.py
```

**Complete V1→V10 Evolution Results (Historic Journey):**
```
Systematic Prompt Optimization with HISTORIC BREAKTHROUGHS:
V1 → V2 → V4 → V5 → V6 Cultural → V7 Plateau → V8 BREAKTHROUGH → V9 LLM-GUIDED → V10 PRODUCTION
58.6% → 72.9% → 68% → 75% brands → 100% success → 90% specificity → 100% + HISTORIC → +33.3% competitive → 99.0% BEST ✅

V10 Production Deployment (August 2025):
🏆 BEST PERFORMING PROMPT: Combines all breakthrough insights for production excellence
   V8: skinnydip-iface-rhinoshield-phone-cases-guide (breakthrough baseline)
   V10: ultimate-skinnydip-iface-rhinoshield-phone-cases-guide (competitive + cultural excellence)
   Result: 0.990 average performance, 90% improvement rate, +8.2% vs V8

V10 Production Innovations:
• Smart Enhancement Logic: Conditional competitive terms based on content complexity
• Infrastructure Excellence: Enhanced pre-flight validation, graceful dependency fallbacks
• Best of All Worlds: V8 robustness + V9 competitive appeal + V6 cultural foundation
• Production Readiness: 0.990 average, 90% improvement rate, comprehensive documentation

V8 Historic Breakthrough (August 2025):
🚀 FIRST SUCCESS: "日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！"
   → skinnydip-iface-rhinoshield-phone-cases-guide (6 words, 45 chars)
   V6/V7 Status: FAILED ❌ (both versions) → V8: SOLVED ✅ (HISTORIC)

V8 Technical Innovations:
• Relaxed Constraints: 3-8 words (from 3-6), 70 chars (from 60) for complex multi-brand
• Character Normalization: JoJo Maman Bébé → jojo-maman-bebe, SKINNIYDIP/iface → skinniydip-iface  
• Version-Aware Configuration: Dynamic settings system with SlugGeneratorConfig.for_version('v8')
• Hypothesis Validation: User intuition + systematic testing > pure metrics optimization

V6 Cultural Breakthroughs (Foundation):
• Cultural Preservation: 一番賞 → ichiban-kuji (not generic "anime-merchandise") 
• Compound Brands: 大國藥妝 → daikoku-drugstore (V5 failed completely)
• Asian Platforms: 樂天 → rakuten, 官網 → official-store
• Context Awareness: 集運 → shipping, 代購 → proxy-shopping

V7 Enhanced Features (Plateau Phase):
• Product Specificity: thermos-zojirushi-japan-thermal-guide (vs insulated-bottle-guide)
• Commercial Context: tory-burch-sale-discount-guide (vs tory-burch-sale)
• Multi-Component Recognition: sennheiser-headphones-tsum-tsum-recommendations
• Performance Plateau: 90% success rate, same 3 failures as V6 → SOLVED BY V8 ✅
```

**Enhanced A/B Testing Framework + Meta-Analysis Achievement:**
```
V8 Breakthrough Methodology Capabilities:
• Historic breakthrough tracking: First system to solve previously impossible cases
• Hypothesis validation methodology: User intuition + systematic testing framework  
• Version-aware configuration: Dynamic constraint adjustment per prompt version
• Enhanced per-URL visibility: Complete detailed results with failure case analysis
• Meta-analysis insights: Goldilocks Principle, complexity creep patterns, infrastructure co-evolution
• Statistical validation: Automated effect size analysis with deployment recommendations

V8 Meta-Analysis Discoveries:
• The "Goldilocks Principle": V5 too simple, V7 too complex, V6→V8 just right
• What Worked: Hypothesis-driven development, surgical improvements, cultural preservation
• What Didn't: Complexity creep (V7), metrics misalignment, over-engineering patterns
• Domain Expertise > Pure Optimization: V6 cultural breakthrough + V8 user intuition validation

Architecture Evolution (V1→V8):
Before: 15+ scattered test files, mixed abstractions, poor organization, fixed constraints
After:  Clean core/config/utils/optimization/extensions + version-aware configuration + breakthrough tracking
```

**See:** `blog-post-slug-update/CLAUDE.md` for comprehensive technical documentation and methodology.

## 🐛 Bug Patterns & Debugging Methodology

**Reusable debugging patterns discovered through systematic AI development:**

### **Validation Configuration Mismatches**
**Pattern**: AI generates correct output but validation uses wrong constraints  
**Symptoms**: High API success rate but low validation pass rate, "generated content rejected"  
**Root Cause**: Validation functions using default/global config instead of version-specific config  
**Debug Steps**:
1. Check if AI output looks correct but gets rejected
2. Compare validation constraints vs generator constraints  
3. Verify configuration objects passed to validation functions

**Fix Pattern**:
```python
# ❌ Wrong: Uses default config
validation = validate_output(content)

# ✅ Correct: Uses generator's config  
validation = validate_output(content, self.config)
```

### **Progress Tracking in Multi-Step Systems**
**Pattern**: Progress updated in memory but not persisted for monitoring threads  
**Symptoms**: Progress bars stuck at 0%, count mismatches between components, stale UI  
**Root Cause**: Background threads can only read files, not memory state  
**Debug Steps**:
1. Check if processing logic updates progress correctly
2. Verify if progress data is written to files
3. Confirm monitoring threads read from correct data source

**Fix Pattern**:
```python
# ❌ Wrong: Progress only in memory
progress_info = self.monitor.update_progress()

# ✅ Correct: Progress persisted to disk
progress_info = self.monitor.update_progress()
self._write_progress_to_file(progress_info)
```

### **File vs Memory State Synchronization**
**Pattern**: Processing logic works but monitoring shows incorrect state  
**Symptoms**: Accurate final results but wrong real-time progress, UI lag  
**Root Cause**: State stored in memory while monitors read from files  
**Fix**: Ensure all state changes are immediately written to files that monitors can access

### **Import Dependencies in Modular Systems**
**Pattern**: Silent failures when adding new functionality to existing modules  
**Symptoms**: Methods not working, missing functionality, silent exceptions  
**Root Cause**: Missing imports when adding new methods that use additional libraries  
**Debug**: Check error logs for import-related failures, verify all dependencies imported  
**Fix**: Add missing imports at module level when extending functionality

### **Configuration vs Prompt Version Mismatches**
**Pattern**: Prompts designed for enhanced capabilities but constrained by old validation  
**Symptoms**: Advanced AI output rejected by legacy validation rules  
**Root Cause**: Version-specific prompts not paired with version-specific validation  
**Fix**: Implement version-aware configuration systems that update both prompts and constraints

### **Batch Processing Resume Failures**
**Pattern**: Resume logic restarts from beginning instead of checkpoint, creating duplicates  
**Symptoms**: Progress shows high completion but processing starts from 0, duplicate entries in results  
**Root Cause**: Resume checkpoint format mismatches, file overwriting instead of appending  
**Debug Steps**:
1. Check if multiple result files exist with different entry counts
2. Verify checkpoint files have compatible formats with resume logic
3. Examine if results files use overwrite vs append mode during resume

**Fix Pattern**:
```python
# ❌ Wrong: Overwrites existing results
results_file = open(output_file, 'w')

# ✅ Correct: Appends to existing results during resume  
results_file = open(output_file, 'a' if resume else 'w')
```

### **Multi-File State Synchronization Issues**
**Pattern**: Processing logic updates one set of files while monitoring reads from different files  
**Symptoms**: Progress tracking shows incorrect state, UI displays stale data, file count mismatches  
**Root Cause**: State distributed across multiple files without proper synchronization  
**Debug Steps**:
1. Map all state files and their update/read patterns
2. Verify which files are authoritative vs derived
3. Check if resume logic reads from correct checkpoint files

**Fix Pattern**:
```python
# ❌ Wrong: Multiple files with unclear precedence
progress_file_1, progress_file_2, checkpoint_file = get_files()

# ✅ Correct: Single source of truth with clear derivation
authoritative_file = get_primary_checkpoint()
derived_status = calculate_from_authoritative(authoritative_file)
```

### **Content Processing Assumption Validation**
**Pattern**: Assuming different systems use different content processing approaches without verification  
**Symptoms**: Unexplained performance differences, incorrect root cause analysis, wrong optimization targets  
**Root Cause**: Technical assumptions not validated against actual implementation code  
**Debug Steps**:
1. Verify actual method calls in both systems (title-only vs full content)
2. Check dataset structure and what data is actually available
3. Test both approaches on the same failure cases to isolate true causes

**Fix Pattern**:
```python
# ❌ Wrong: Assuming without verification
# "System A uses full content, System B uses titles only"

# ✅ Correct: Code analysis reveals truth
# Both systems: generate_slug_from_content(title, title)
# Dataset: {title, url} pairs only - no content field
# True cause: Edge cases with very short titles (≤5 chars)
```

**Lesson**: Always validate technical assumptions with actual code review before optimizing the wrong component.

These patterns help debug similar issues across different AI projects and prevent common architectural mistakes.

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