# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

This is a blog post slug generator project that analyzes blog post content and suggests SEO-friendly slugs using AI.

**Planned Structure:**
```
src/
├── slug_generator.py       # Main slug generation logic with OpenAI integration  
├── content_extractor.py    # URL fetching and HTML parsing (reuses content-analyzer code)
├── utils.py               # Shared utilities
└── __init__.py

scripts/
└── suggest_slug.py        # CLI entry point

tests/
├── test_slug_generator.py # Core functionality tests
├── test_cli.py            # CLI interface tests  
├── test_data.py           # Test fixtures and data
└── __init__.py

config/
└── .env                   # OpenAI API key configuration
```

## Project Purpose

AI-powered blog post slug generator that:
- Fetches content from blog post URLs
- Analyzes title and content using OpenAI
- Generates SEO-friendly, readable slugs  
- Transforms date-based URLs like `/2025/08/18/encoded-chinese-text/` into clean slugs like `jojo-maman-bebe-uk-shopping-guide`

## Development Setup

**Environment Setup:**
```bash
# Install dependencies
pip install -r requirements.txt

# Set up OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Testing

**Run Tests:**
```bash
# Run all tests
python3 run_tests.py

# Run specific test module
python3 run_tests.py tests.test_slug_generator

# Run with verbose output
python3 -m unittest discover -v tests/
```

**Test Cases Include:**
- Real BuyandShip blog URLs (Chinese content → English slugs)
- Edge cases (invalid URLs, rate limits, validation)
- CLI interface testing
- OpenAI API integration mocking

## Common Commands

**Main Usage (when implemented):**
```bash
# Generate slug for a URL
python scripts/suggest_slug.py https://blog.example.com/post

# Multiple suggestions  
python scripts/suggest_slug.py --count 3 https://blog.example.com/post

# Verbose output
python scripts/suggest_slug.py --verbose https://blog.example.com/post
```

## Architecture

**Core Components:**
- **SlugGenerator**: Main class using OpenAI API for intelligent slug generation
- **Content extraction**: Reuses proven URL fetching from content-analyzer project
- **AI Integration**: OpenAI GPT for context-aware slug suggestions
- **CLI Interface**: User-friendly command-line tool

**Data Flow:**
1. URL validation and content extraction  
2. Title and content analysis
3. OpenAI API call with context-aware prompts
4. Slug validation and formatting
5. Multiple ranked suggestions output