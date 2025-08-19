# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

This is a comprehensive AI development project repository containing both learning materials and production projects:

**Learning Curriculum:**
- `claude-code-curriculum/week-1-foundation/content-analyzer/` - AI-powered content analysis tool for cross-border e-commerce
- `claude-code-curriculum/week-2-llm-mastery/` - Advanced LLM techniques (planned)
- `claude-code-curriculum/week-3-web-scraping/` - Professional web scraping (planned)  
- `claude-code-curriculum/week-4-integration/` - System integration (planned)

**Production Projects:**
- `blog-post-slug-update/` - AI-powered blog post slug generator using OpenAI API

**Multi-Project Structure:**
- Each project maintains its own `CLAUDE.md` for specific guidance
- Parent `CLAUDE.md` (this file) provides repository-wide security and development principles
- Shared security practices apply across all projects

## Common Development Commands

### Content Analyzer Project (Week 1)

Working directory: `claude-code-curriculum/week-1-foundation/content-analyzer/`

**Environment Setup:**
```bash
cd claude-code-curriculum/week-1-foundation/content-analyzer
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

**Main Usage:**
```bash
# AI-powered analysis (requires OpenAI API key in .env)
python scripts/run_analysis.py --auto-tag https://example.com/blog-post

# Basic text analysis only
python scripts/run_analysis.py https://example.com/blog-post
python scripts/run_analysis.py path/to/textfile.txt

# Demo mode
python scripts/run_analysis.py
```

**Development:**
```bash
# Always activate virtual environment first
source venv/bin/activate

# Install new dependencies
pip install package-name
pip freeze > requirements.txt

# Deactivate when done
deactivate
```

### Blog Post Slug Generator Project

Working directory: `blog-post-slug-update/`

**Environment Setup:**
```bash
cd blog-post-slug-update
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

**Main Usage:**
```bash
# Generate slug for a blog post URL
python scripts/suggest_slug.py https://blog.example.com/post

# Multiple suggestions with verbose output
python scripts/suggest_slug.py --count 3 --verbose https://blog.example.com/post

# Run comprehensive tests
python tests/test_slug_generator.py
```

## Project Architecture

### Content Analyzer System Design

**Core Components:**
- `src/content_analyzer.py` - Text analysis engine (word count, readability, keywords)
- `src/auto_tagger.py` - AI tagging system using OpenAI API
- `src/utils.py` - Shared utilities (URL fetching, result formatting)
- `scripts/run_analysis.py` - CLI entry point with argument handling

**Data Flow:**
1. Input processing (URL fetch or file read)
2. Basic text analysis (ContentAnalyzer class)
3. AI-powered tagging (AutoTagger class) - optional with --auto-tag flag
4. Result formatting and JSON output to `data/outputs/YYYY-MM-DD/`

**AI Tagging Categories:**
- Brands (Amazon, Lululemon, etc.)
- Product Categories (Electronics, Athleisure, etc.)  
- Product Source Regions (US, UK, Japan, etc.)
- Target User Regions (Singapore, Malaysia, etc.)
- Shopping Intent (Price-comparison, How-to-buy, etc.)

**Configuration:**
- Environment variables via `.env` file (OpenAI API key required for AI features)
- AI prompts stored in `config/prompts/`
- Test data and ground truth in `tests/ground_truth_regions.json`

## 🔐 Security & Secret Management

**Critical Security Principles:**
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

- Python 3.12.4
- Virtual environment recommended (venv/)
- OpenAI API key required for AI tagging features
- Dependencies managed via requirements.txt (requests, beautifulsoup4, openai, python-dotenv)