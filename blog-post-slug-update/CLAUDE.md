# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Structure

This is a comprehensive SEO package generator that creates complete SEO optimization (slug, title, meta description) for blog posts across multiple regions using AI.

**Current Structure:**
```
src/
├── content_analyzer.py     # URL decoding & content intelligence extraction  
├── seo_generator.py       # LLM-powered SEO package generation (slug/title/meta)
├── batch_processor.py     # Multi-region batch processing with failure recovery
├── character_limit_handler.py # Smart character limit handling with retry
├── output_manager.py      # JSON output file management per region
├── region_manager.py      # Dynamic region support and slug suffix handling
├── performance_estimator.py # Cost and time estimation for large batches
└── utils.py               # Shared utilities

scripts/
└── batch_seo_generator.py # CLI entry point for batch processing

tests/
├── test_content_analyzer.py # Content intelligence & URL decoding tests
├── test_seo_generator.py   # SEO package generation tests
├── test_batch_processor.py # Batch processing & multi-region tests  
├── test_performance.py    # Performance & cost estimation tests
└── fixtures/              # Test data and expected outputs

data/
└── blog_urls_dataset.json # Production dataset with 8,194 blog URLs

results/                   # Generated SEO packages (one JSON per region)
├── seo_mapping_hong_kong_YYYYMMDD.json
├── seo_mapping_singapore_YYYYMMDD.json
└── seo_mapping_australia_YYYYMMDD.json
```

## Project Purpose

**Complete SEO Migration Tool** for transforming Chinese blog URLs into region-specific SEO packages:

**Input:** Chinese blog titles + encoded URLs  
**Output:** Complete SEO package (slug, title, meta description) for multiple regions

**Key Features:**
- **Multi-region support:** Generate SEO packages for Hong Kong, Singapore, Australia, Malaysia, Taiwan, etc.
- **Batch processing:** Handle 8k+ entries efficiently with cost optimization
- **Intelligent content analysis:** URL decoding, brand extraction, category detection
- **Region-specific optimization:** Each region gets localized SEO content
- **Production-ready:** Failure recovery, progress tracking, cost estimation

**Example Transformation:**
```
Input: "8大日牌輕珠寶品牌一次睇！Agete、nojess及Star Jewelry等"
       "https://.../%e6%97%a5%e6%9c%ac%e8%bc%95%e7%8f%a0%e5%af%b6%e5%93%81%e7%89%8c%e5%90%88%e9%9b%86/"

Output (Hong Kong):
- Slug: "japanese-jewelry-brands-guide-hong-kong"  
- Title: "Japanese Jewelry Brands Guide | Hong Kong"
- Meta: "Discover Agete, Nojess & Star Jewelry. Shop authentic Japanese jewelry with BuyandShip Hong Kong."
```

## Development Setup

**Environment Setup:**
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
# On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install psutil  # For performance testing

# Set up OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

**⚠️ Important:** Always activate the virtual environment before running any Python commands:
```bash
source venv/bin/activate  # Must run this first!
```

## Test-Driven Development

This project uses **Test-Driven Development (TDD)** approach:

**Run Tests:**
```bash
# IMPORTANT: Always activate venv first
source venv/bin/activate

# Run all tests (most will initially fail until implemented)
python -m unittest discover tests/ -v

# Run specific test modules
python -m unittest tests.test_content_analyzer -v
python -m unittest tests.test_seo_generator -v  
python -m unittest tests.test_batch_processor -v
python -m unittest tests.test_performance -v

# Performance estimation test (can run anytime)
python -m unittest tests.test_performance.TestPerformanceEstimation.test_performance_baseline_without_implementation -v
```

**Test Coverage:**
- ✅ **Content Analysis:** URL decoding, brand extraction, categorization
- ✅ **SEO Generation:** Slug/title/meta with character limits & region support
- ✅ **Batch Processing:** Multi-region processing, failure handling, async performance
- ✅ **Performance:** Cost estimation, memory usage, rate limiting for 8k+ entries

**Expected Test Results:**
- **Initially:** Most tests skip/fail (components not implemented)
- **TDD Progress:** Tests pass as components are implemented
- **Target:** >95% success rate, <10 hours processing, <$50 cost

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

## Batch Processing Commands

**Production Usage:**
```bash
# IMPORTANT: Always activate venv first
source venv/bin/activate

# Process all regions (default: Hong Kong, Singapore, Australia, Malaysia, Taiwan)
python scripts/batch_seo_generator.py --input data/blog_urls_dataset.json

# Specific regions only
python scripts/batch_seo_generator.py \
    --input data/blog_urls_dataset.json \
    --regions "Hong Kong" "Singapore" "Australia"

# Performance test mode (estimate cost & time)
python scripts/batch_seo_generator.py --performance-test --sample-size 100

# Resume failed processing
python scripts/batch_seo_generator.py --resume results/failed_entries_hong_kong_20250819.json
```

**Expected Performance:**
- **Processing time:** 2-8 hours for 8,194 entries × 5 regions  
- **Cost:** $10-50 depending on model choice (GPT-4o-mini recommended)
- **Output:** One JSON file per region in `results/` directory

## Architecture

**Two-Step Processing Pipeline:**

**Step 1: Content Intelligence**
- **URL Decoding:** Convert `%e6%97%a5%e6%9c%ac` → `日本輕珠寶品牌合集`
- **Brand Extraction:** Identify "Agete", "nojess", "Star Jewelry" from mixed language text  
- **Content Categorization:** Auto-detect jewelry/fashion/electronics/etc.
- **Keyword Analysis:** Extract evergreen keywords vs promotional terms

**Step 2: LLM-Powered SEO Generation**
- **Multi-component generation:** Slug + Title + Meta Description
- **Region-specific optimization:** Each region gets localized content
- **Character limit handling:** Smart retry for over-limit content
- **Quality validation:** Format, length, and content requirements

**Key Components:**
- **ContentAnalyzer:** Intelligent content extraction and analysis
- **SEOGenerator:** LLM-powered multi-region SEO package creation
- **BatchProcessor:** Production-scale processing with failure recovery
- **OutputManager:** Clean JSON output organization per region