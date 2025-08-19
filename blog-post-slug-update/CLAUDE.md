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

data/
└── blog_urls_dataset.json # Production dataset with 8k+ blog URLs
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
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Mac/Linux
# On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

**Note:** Always use a virtual environment to avoid dependency conflicts. The venv should be activated before running any Python commands or installing packages.

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

## Dataset

**Production Dataset:** `data/blog_urls_dataset.json`
- **8,194 real blog post entries** from BuyandShip.today
- **Chinese titles** with corresponding **encoded URLs**
- **Perfect for testing:** URLs like `%e6%97%a5%e6%9c%ac%e8%bc%95%e7%8f%a0%e5%af%b6` that need clean English slugs
- **JSON format** for reliable parsing without CSV issues
- **Date range:** 2014-2025 historical blog content
- **Content types:** Cross-border e-commerce, fashion, electronics, beauty products

**Usage Examples:**
```python
import json

# Load dataset
with open('data/blog_urls_dataset.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

# Example entry
entry = dataset[0]
print(entry['title'])  # "8大日牌輕珠寶品牌一次睇！Agete、nojess及Star Jewelry等日劇女主御用明星珠寶"
print(entry['url'])    # "https://www.buyandship.today/blog/2025/08/18/%e6%97%a5%e6%9c%ac%e8%bc%95%e7%8f%a0%e5%af%b6%e5%93%81%e7%89%8c%e5%90%88%e9%9b%86/"
```

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