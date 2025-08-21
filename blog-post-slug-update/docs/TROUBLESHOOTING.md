# Troubleshooting Guide

## 🎯 **Overview**

This guide provides comprehensive troubleshooting for the LLM Blog Post Slug Generator, covering common issues, debugging strategies, and resolution procedures based on lessons learned during the V1→V9 evolution journey.

## 🚨 **Critical Issues and Resolutions**

### **1. Configuration and Setup Issues**

#### **Problem: OpenAI API Key Not Found**
```
Error: ValueError: OpenAI API key is required. Set OPENAI_API_KEY environment variable.
```

**Solution**:
```bash
# 1. Check if .env file exists
ls -la .env

# 2. Create .env file from template
cp .env.example .env

# 3. Edit .env file and add your API key
# OPENAI_API_KEY=your-actual-api-key-here

# 4. Verify environment variable is loaded
python -c "import os; print('API Key loaded:', bool(os.getenv('OPENAI_API_KEY')))"
```

#### **Problem: Module Import Errors**
```
Error: ImportError: No module named 'openai' or similar
```

**Solution**:
```bash
# 1. Activate virtual environment (CRITICAL STEP)
source venv/bin/activate

# 2. Install requirements
pip install -r requirements.txt

# 3. Verify installation
python -c "import openai; print('OpenAI module loaded successfully')"
```

#### **Problem: Version Configuration Not Found**
```
Error: ValueError: Invalid or unsupported version: v10
```

**Solution**:
```python
# 1. Check available versions
import sys; sys.path.insert(0, 'src')
from config.settings import SlugGeneratorConfig
print("Available versions:", SlugGeneratorConfig.VERSION_SETTINGS.keys())

# 2. Verify prompt file exists
import os
prompt_path = "src/config/prompts/v10_prompt.txt"
print("Prompt file exists:", os.path.exists(prompt_path))

# 3. Create missing prompt file or use existing version
# OR use validate_setup.py for comprehensive checking
```

### **2. Constraint System Issues**

#### **Problem: Constraint Validation Failures**
```
Error: ValueError: Version v10 constraints exceed system bounds (words: 1-20, chars: 1-300)
```

**Solution**:
```python
# 1. Check current constraint settings
from config.settings import SlugGeneratorConfig
config = SlugGeneratorConfig.for_version('v10')
print(f"Current constraints: {config.MAX_WORDS} words, {config.MAX_CHARS} chars")

# 2. Validate constraints manually
valid = SlugGeneratorConfig.validate_constraints(
    config.MAX_WORDS, 
    config.MAX_CHARS, 
    config.MIN_WORDS
)
print(f"Constraints valid: {valid}")

# 3. Fix in settings.py if invalid
# Ensure: 1 ≤ MIN_WORDS ≤ MAX_WORDS ≤ 20 and MAX_CHARS ≤ 300
```

#### **Problem: Slugs Failing Validation**
```
Error: Generated slug fails constraint validation
```

**Debug Process**:
```python
# 1. Test slug validation
from core.validators import validate_slug, validate_slug_system_bounds
from config.settings import SlugGeneratorConfig

test_slug = "your-generated-slug-here"
config = SlugGeneratorConfig.for_version('v8')

# 2. Check system bounds first
system_result = validate_slug_system_bounds(test_slug)
print(f"System bounds: {system_result}")

# 3. Check version-specific constraints
version_result = validate_slug(test_slug, config)
print(f"Version constraints: {version_result}")

# 4. Analyze constraint usage
words = len(test_slug.split('-'))
chars = len(test_slug)
print(f"Slug metrics: {words} words, {chars} chars")
print(f"Constraint limits: {config.MIN_WORDS}-{config.MAX_WORDS} words, {config.MAX_CHARS} chars")
```

### **3. API and LLM Integration Issues**

#### **Problem: OpenAI API Rate Limits**
```
Error: Rate limit exceeded or API quota reached
```

**Solution**:
```python
# 1. Check retry configuration
from config.settings import SlugGeneratorConfig
print(f"Max retries: {SlugGeneratorConfig.MAX_RETRIES}")
print(f"Base delay: {SlugGeneratorConfig.RETRY_BASE_DELAY}s")

# 2. Increase retry delays if needed
# Edit settings.py:
# RETRY_BASE_DELAY = 2.0  # Increase from 1.0
# MAX_RETRIES = 5         # Increase from 3

# 3. Monitor API usage
# Check your OpenAI account usage limits and billing
```

#### **Problem: JSON Parsing Failures**
```
Error: Failed to parse JSON response from OpenAI
```

**Debug Process**:
```python
# 1. Enable verbose logging to see raw response
generator = SlugGenerator(prompt_version='v8', dev_mode=True)

# 2. Test with simple content
result = generator.quick_test("Simple test content")

# 3. Check prompt format requirements
# Ensure prompt explicitly requires JSON format:
# "Return your response in valid JSON format with this structure..."

# 4. Validate JSON in prompt file
import json
prompt_path = "src/config/prompts/v8_prompt.txt"
# Check that prompt includes proper JSON format instructions
```

#### **Problem: Low Confidence Scores**
```
Warning: Generated slugs consistently below confidence threshold
```

**Analysis and Solution**:
```python
# 1. Check confidence threshold settings
config = SlugGeneratorConfig.for_version('v8')
print(f"Confidence threshold: {config.CONFIDENCE_THRESHOLD}")

# 2. Analyze recent results
# Look for patterns in low-confidence cases
# Common causes:
# - Content too complex for current prompt
# - Cultural terms not in prompt examples
# - Multi-brand scenarios exceeding prompt capability

# 3. Consider threshold adjustment or prompt improvement
# Temporary: Lower threshold for development
# Long-term: Improve prompt to handle specific failure cases
```

### **4. Testing and Validation Issues**

#### **Problem: Test Suite Failures**
```
Error: Tests failing after configuration changes
```

**Systematic Debug Process**:
```bash
# 1. Run individual test categories
python -m pytest tests/unit/test_configuration.py -v
python -m pytest tests/unit/test_validation_pipeline.py -v
python -m pytest tests/integration/test_end_to_end.py -v

# 2. Check specific failing tests
python -m pytest tests/unit/test_configuration.py::test_version_validation -v

# 3. Validate pre-flight system
python scripts/validate_setup.py --all

# 4. Check for environment issues
source venv/bin/activate  # Ensure virtual environment is active
```

#### **Problem: A/B Testing Framework Errors**
```
Error: Enhanced A/B testing failing to compare versions
```

**Solution**:
```python
# 1. Validate both versions exist and are configured
from config.settings import SlugGeneratorConfig

versions = ['v8', 'v10']
for version in versions:
    try:
        config = SlugGeneratorConfig.for_version(version)
        print(f"✅ {version}: Valid configuration")
    except Exception as e:
        print(f"❌ {version}: {e}")

# 2. Test with minimal cases first
python tests/performance/test_prompt_versions.py --enhanced --versions v8 v9 --urls 5

# 3. Check test data availability
import json
with open('tests/fixtures/sample_blog_urls.json', 'r') as f:
    data = json.load(f)
    print(f"Test data available: {len(data)} URLs")
```

### **5. Performance and Production Issues**

#### **Problem: Slow Response Times**
```
Issue: Slug generation taking >10 seconds consistently
```

**Diagnosis and Optimization**:
```python
# 1. Profile generation time components
import time
from core import SlugGenerator

generator = SlugGenerator(prompt_version='v8')

start_time = time.time()
result = generator.generate_slug_from_url("https://example.com/blog/post")
total_time = time.time() - start_time

print(f"Total generation time: {total_time:.2f}s")

# 2. Check content extraction time
# Large pages may take time to scrape and process
# Consider implementing content length limits

# 3. API call optimization
# Monitor OpenAI API response times
# Consider model downgrade if speed is critical (gpt-4o-mini vs gpt-4)
```

#### **Problem: Memory Usage Issues**
```
Issue: High memory consumption during batch processing
```

**Solution**:
```python
# 1. Implement batch processing limits
def process_urls_in_batches(urls, batch_size=10):
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i+batch_size]
        # Process batch
        # Clear memory between batches
        import gc; gc.collect()

# 2. Monitor memory usage
import psutil
process = psutil.Process()
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

### **6. Cultural and Content Issues**

#### **Problem: Cultural Terms Not Preserved**
```
Issue: Asian e-commerce terms being anglicized incorrectly
```

**Analysis Process**:
```python
# 1. Test cultural preservation
cultural_test_cases = [
    "一番賞", "JK制服", "大國藥妝", "樂天", "官網"
]

for term in cultural_test_cases:
    # Test current prompt handling
    result = generator.generate_slug_from_content(f"Title with {term}", f"Content about {term}")
    print(f"{term} handling: {result['primary']}")

# 2. Check prompt examples
# Verify prompt includes cultural term examples
# Add missing cultural context if needed
```

#### **Problem: Multi-Brand Detection Failures**
```
Issue: Complex brand combinations not being captured
```

**V8 Breakthrough Validation**:
```python
# 1. Test the historic V8 breakthrough case
breakthrough_title = "日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！"
expected_result = "skinnydip-iface-rhinoshield-phone-cases-guide"

generator_v8 = SlugGenerator(prompt_version='v8')
result = generator_v8.generate_slug_from_content(breakthrough_title, breakthrough_title)

print(f"Expected: {expected_result}")
print(f"Generated: {result['primary']}")
print(f"Breakthrough preserved: {result['primary'] == expected_result}")

# 2. If failing, check:
# - Constraint settings (V8 should allow 3-8 words, 70 chars)
# - Prompt file integrity
# - Character normalization logic
```

## 🔧 **Debugging Tools and Commands**

### **System Validation Commands**
```bash
# Complete system check
python scripts/validate_setup.py --all

# Quick configuration check
python scripts/validate_setup.py --quick --version v8

# JSON output for automation
python scripts/validate_setup.py --json --version v8
```

### **Interactive Debugging**
```python
# 1. Development mode testing
from core import SlugGenerator
generator = SlugGenerator(prompt_version='v8', dev_mode=True)

# 2. Single case testing
result = generator.quick_test("Test content here")
print(result)

# 3. Version comparison
comparison = generator.compare_versions(
    "Test content", 
    versions=['v6', 'v8'], 
    metrics=['success_rate', 'cultural_preservation']
)
print(comparison)
```

### **Configuration Inspection**
```python
# 1. View all configuration details
from config.settings import SlugGeneratorConfig
import json
print(json.dumps(SlugGeneratorConfig.to_dict(), indent=2))

# 2. Version-specific information
print(json.dumps(SlugGeneratorConfig.get_constraint_info('v8'), indent=2))

# 3. Constraint validation testing
print("Valid constraints:", SlugGeneratorConfig.validate_constraints(8, 70, 3))
print("Invalid constraints:", SlugGeneratorConfig.validate_constraints(25, 400, 0))
```

## 📊 **Performance Monitoring**

### **Health Check Script**
```python
def system_health_check():
    """Comprehensive system health validation"""
    health_status = {
        'api_connectivity': False,
        'configuration_valid': False,
        'constraints_working': False,
        'core_functionality': False,
        'cultural_preservation': False
    }
    
    try:
        # 1. API connectivity test
        from core import SlugGenerator
        generator = SlugGenerator(prompt_version='v8')
        test_result = generator.quick_test("Health check test")
        health_status['api_connectivity'] = bool(test_result)
        
        # 2. Configuration validation
        from config.settings import SlugGeneratorConfig
        config = SlugGeneratorConfig.for_version('v8')
        health_status['configuration_valid'] = True
        
        # 3. Constraint system test
        constraints_valid = SlugGeneratorConfig.validate_constraints(8, 70, 3)
        health_status['constraints_working'] = constraints_valid
        
        # 4. Core functionality test
        if test_result and 'primary' in test_result:
            health_status['core_functionality'] = True
        
        # 5. Cultural preservation test
        cultural_test = generator.generate_slug_from_content(
            "一番賞 test", "Content about 一番賞"
        )
        if 'ichiban' in cultural_test.get('primary', ''):
            health_status['cultural_preservation'] = True
            
    except Exception as e:
        print(f"Health check error: {e}")
    
    return health_status

# Run health check
health = system_health_check()
print("System Health Status:")
for component, status in health.items():
    print(f"  {component}: {'✅' if status else '❌'}")
```

### **Performance Baseline Measurement**
```python
def measure_performance_baseline():
    """Establish performance baseline for monitoring"""
    import time
    from core import SlugGenerator
    
    generator = SlugGenerator(prompt_version='v8')
    test_cases = [
        "Simple blog post title",
        "Complex multi-brand scenario with cultural elements",
        "Asian e-commerce content with specific terminology"
    ]
    
    performance_data = []
    
    for i, test_case in enumerate(test_cases):
        start_time = time.time()
        try:
            result = generator.generate_slug_from_content(test_case, test_case)
            duration = time.time() - start_time
            success = bool(result and 'primary' in result)
            
            performance_data.append({
                'test_case': i + 1,
                'duration': round(duration, 2),
                'success': success,
                'content_length': len(test_case)
            })
        except Exception as e:
            performance_data.append({
                'test_case': i + 1,
                'duration': time.time() - start_time,
                'success': False,
                'error': str(e)
            })
    
    return performance_data

# Establish baseline
baseline = measure_performance_baseline()
print("Performance Baseline:")
for data in baseline:
    print(f"  Test {data['test_case']}: {data['duration']}s - {'✅' if data['success'] else '❌'}")
```

## 📝 **Issue Reporting Template**

When reporting issues, please include:

```
## Issue Description
Brief description of the problem

## Environment
- Python version: 
- Virtual environment active: Yes/No
- OpenAI API key configured: Yes/No
- Version attempting to use: 

## Error Message
```
Full error message and stack trace
```

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected vs Actual Behavior
Expected: 
Actual:

## System Health Check Results
```
Run system_health_check() and paste results
```

## Additional Context
Any additional information, recent changes, or relevant details
```

## 🚀 **Emergency Recovery Procedures**

### **Complete System Reset**
```bash
# 1. Deactivate and recreate virtual environment
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# 2. Reinstall dependencies
pip install -r requirements.txt

# 3. Verify configuration
cp .env.example .env
# Edit .env with your API key

# 4. Run comprehensive validation
python scripts/validate_setup.py --all
```

### **Rollback to Known Good Version**
```python
# If new version is causing issues, rollback to V8 (known stable)
from core import SlugGenerator

# Use stable V8 configuration
generator = SlugGenerator(prompt_version='v8')  # Known working version
result = generator.generate_slug_from_content("test", "test content")
print(f"V8 fallback working: {bool(result)}")
```

This troubleshooting guide covers the most common issues encountered during the V1→V9 evolution journey and provides systematic resolution procedures for maintaining robust operation.