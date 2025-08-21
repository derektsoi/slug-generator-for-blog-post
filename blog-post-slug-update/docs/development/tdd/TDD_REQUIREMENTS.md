# TDD Requirements for Enhanced A/B Testing

## Test-Driven Development Setup Complete ✅

The enhanced A/B testing functionality has been designed using test-driven development. All tests are written and **failing as expected** - ready for implementation.

### Test Files Created:

1. **`tests/integration/test_enhanced_ab_testing.py`** - Comprehensive test suite (267 lines)
2. **`tests/integration/test_enhanced_ab_testing_runner.py`** - Demo script showing expected failures

### Current Test Results (Expected Failures):

```
8 failed, 1 passed, 1 warning in 0.08s
```

**✅ This is exactly what we want in TDD - failing tests that define the requirements!**

## Required Features (Defined by Tests):

### 1. Enhanced Optimizer (`src/optimization/optimizer.py`)

**Missing Features:**
- `include_detailed_results` config flag
- `detailed_url_results` in comparison output 
- `load_sample_urls()` function
- `create_randomized_test_cases()` function  
- `generate_expected_themes()` function
- Enhanced console output with `verbose_output` flag
- URL randomization with `randomize_urls`, `url_count`, `random_seed` config

**Expected Enhancement:**
```python
# Current optimizer output:
{
    'v6_cultural_enhanced': {
        'avg_theme_coverage': 0.90,
        'success_rate': 1.0,
        'avg_duration': 4.2
    }
}

# Enhanced optimizer output (what tests expect):
{
    'v6_cultural_enhanced': {
        'avg_theme_coverage': 0.90,
        'success_rate': 1.0, 
        'avg_duration': 4.2,
        'detailed_url_results': [  # NEW
            {
                'url_index': 0,
                'title': '8大日牌輕珠寶品牌一次睇！Agete、nojess及Star Jewelry等...',
                'generated_slug': 'agete-nojess-star-jewelry-japan-guide',
                'expected_themes': ['agete', 'nojess', 'japanese', 'jewelry'],
                'coverage': 1.0,
                'duration': 4.2,
                'success': True,
                'category': 'jewelry-brands',
                'confidence': 0.9
            },
            # ... 9 more URLs
        ]
    }
}
```

### 2. Enhanced Test Runner (`src/optimization/test_runner.py`)

**Missing Feature:**
- `detailed_individual_results` in `execute_all_tests()` output
- Individual test metadata: `url_index`, `original_title`, `category`, `generated_slug`

**Expected Enhancement:**
```python
# Current test runner output:
{
    'success_rate': 1.0,
    'avg_theme_coverage': 0.8,
    'individual_results': [basic_results...]
}

# Enhanced test runner output (what tests expect):
{
    'success_rate': 1.0,
    'avg_theme_coverage': 0.8,
    'individual_results': [basic_results...],  # Keep existing
    'detailed_individual_results': [  # NEW
        {
            'url_index': 0,
            'original_title': 'Blog post title',
            'category': 'jewelry-brands', 
            'generated_slug': 'extracted-primary-slug',
            'theme_coverage': 0.8,
            'duration': 4.1,
            'success': True
        }
    ]
}
```

### 3. Enhanced JSON Export

**Missing Feature:**
- Per-URL breakdown in exported JSON files
- Metadata about test run configuration

### 4. URL Randomization System

**Missing Functions:**
- `load_sample_urls()` - Load from `tests/fixtures/sample_blog_urls.json`
- `create_randomized_test_cases()` - Generate test cases from URLs
- `generate_expected_themes()` - Auto-generate expected themes

### 5. Enhanced Console Output

**Missing Feature:**
- Per-URL results display in console during testing
- Visual indicators (✅/❌) for success/failure
- Coverage percentages for each URL
- Organized table format

**Expected Console Output:**
```
🔬 TESTING VERSION: V6_CULTURAL_ENHANCED
════════════════════════════════════════

URL 0: "8大日牌輕珠寶品牌一次睇！Agete、nojess及Star Jewelry等..."
  Generated: agete-nojess-star-jewelry-japan-guide
  Expected: [agete, nojess, japanese, jewelry, brands]  
  Coverage: 100% ✅ (4.2s)

URL 1: "英國必買童裝 JoJo Maman Bébé官網 3 折起入手網購教學"  
  Generated: jojo-maman-bebe-baby-clothes-uk-guide
  Expected: [uk, jojo-maman-bebe, baby, clothes, shopping, guide]
  Coverage: 83% ✅ (3.8s)

[... 8 more URLs ...]

SUMMARY: 90% avg coverage, 100% success rate, 4.1s avg duration
```

## Test Architecture:

### Dynamic Prompt Version Discovery ✅
- No hardcoded 'v5', 'v6' versions
- Discovers available prompts from `src/config/prompts/` directory  
- Tests with real prompt versions: `current`, `v6_cultural_enhanced`, `v5_brand_focused`

### Realistic Test Data ✅
- Uses actual cross-border e-commerce blog titles
- Simulates version-specific performance differences
- Tests cultural preservation, brand detection, theme coverage

### Backward Compatibility ✅ 
- All existing functionality must continue working
- Tests verify no breaking changes to current API
- Enhanced features are additive only

## Implementation Priority:

1. **Enhanced Test Runner** - Add `detailed_individual_results` 
2. **Enhanced Optimizer** - Add `detailed_url_results` support
3. **URL Randomization** - Add dataset loading and test case generation  
4. **Enhanced Console Output** - Add verbose per-URL display
5. **Enhanced JSON Export** - Add per-URL breakdown

## Success Criteria:

When implementation is complete, running:
```bash
python -m pytest tests/integration/test_enhanced_ab_testing.py -v
```

Should show:
```
9 passed, 0 failed in X.XXs
```

**The TDD foundation is complete and ready for implementation!**