# API Integration Guide

## 🎯 **Overview**

This guide provides comprehensive documentation for integrating with the LLM Blog Post Slug Generator's APIs, including the **honest LLM evaluation system** developed during V9's methodology breakthrough and production deployment strategies.

## 🚀 **Core API Architecture**

### **Main Slug Generation API**

```python
from core import SlugGenerator

# Basic usage
generator = SlugGenerator()
result = generator.generate_slug_from_url("https://blog.example.com/post")

# Advanced configuration
generator = SlugGenerator(
    prompt_version='v8',           # Version-specific constraints and behavior
    max_retries=3,                 # API failure retry attempts
    retry_delay=1.0,               # Base delay for exponential backoff
    dev_mode=True                  # Enable rapid iteration features
)
```

### **Response Format**

```json
{
  "primary": "main-slug-recommendation",
  "alternatives": [
    "alternative-slug-option-1",
    "alternative-slug-option-2"
  ],
  "confidence": 0.85,
  "reasoning": "Brief explanation of slug generation logic",
  "metadata": {
    "word_count": 4,
    "character_count": 28,
    "constraint_compliance": true,
    "cultural_terms_preserved": ["cultural-term"],
    "brands_detected": ["brand1", "brand2"]
  }
}
```

## 🤖 **LLM Evaluation API (V9 Breakthrough)**

### **Honest Evaluation Architecture**

The V9 methodology breakthrough introduced the first systematic LLM-guided evaluation system with **honest architecture** - no fake feedback when LLM is unavailable.

```python
from evaluation.core import EvaluationCoordinator

# Initialize honest evaluation system
evaluator = EvaluationCoordinator(
    api_key=os.getenv('OPENAI_API_KEY'),
    fail_fast_on_llm_unavailable=True  # Critical: No fake feedback
)

# Comprehensive evaluation
result = evaluator.evaluate_slug_quality(
    slug="generated-slug-example",
    original_content="Original blog post content",
    evaluation_criteria={
        'competitive_differentiation': True,
        'cultural_authenticity': True,
        'seo_optimization': True,
        'emotional_appeal': True
    }
)
```

### **Evaluation Response Format**

```json
{
  "evaluation_status": "complete",  // "complete", "partial", "llm_unavailable"
  "honest_evaluation": true,        // True only when LLM actually evaluated
  "quantitative_analysis": {
    "overall_score": 0.87,
    "technical_seo": {
      "score": 0.95,
      "word_count": 6,
      "char_count": 45,
      "structure_score": 1.0
    },
    "constraint_compliance": {
      "score": 1.0,
      "within_word_limit": true,
      "within_char_limit": true,
      "proper_format": true
    }
  },
  "qualitative_analysis": {
    "competitive_differentiation": {
      "score": 0.75,
      "reasoning": "Uses specific brand names and product categories",
      "suggestions": ["Consider emotional triggers for enhanced appeal"]
    },
    "cultural_authenticity": {
      "score": 1.0,
      "reasoning": "Preserves cultural terms appropriately",
      "cultural_terms_found": ["ichiban-kuji"]
    }
  },
  "improvement_recommendations": [
    "Add emotional trigger words for competitive differentiation",
    "Consider product specificity enhancements"
  ]
}
```

### **Error Handling in Honest System**

```python
try:
    evaluation = evaluator.evaluate_slug_quality(slug, content)
    
    if evaluation['honest_evaluation']:
        # Full evaluation available - use qualitative feedback
        qualitative_insights = evaluation['qualitative_analysis']
        improvement_suggestions = evaluation['improvement_recommendations']
    else:
        # LLM unavailable - use only quantitative analysis
        quantitative_only = evaluation['quantitative_analysis']
        # DO NOT use fake qualitative feedback
        
except LLMUnavailableError:
    # Honest failure - handle gracefully
    print("LLM evaluation unavailable - using quantitative metrics only")
    # Fall back to rule-based analysis only
```

## 🔧 **Configuration API**

### **Version-Aware Configuration**

```python
from config.settings import SlugGeneratorConfig

# Get configuration for specific version
config = SlugGeneratorConfig.for_version('v8')
print(f"V8 constraints: {config.MAX_WORDS} words, {config.MAX_CHARS} chars")

# Validate constraints before use
if SlugGeneratorConfig.validate_constraints(10, 100, 3):
    print("Custom constraints valid")

# Get detailed constraint information
constraint_info = SlugGeneratorConfig.get_constraint_info('v8')
print(f"Constraint reasoning: {constraint_info['constraint_reasoning']}")
```

### **Dynamic Configuration Response**

```json
{
  "version": "v8",
  "constraints": {
    "words": {"min": 3, "max": 8},
    "chars": {"max": 70}
  },
  "system_bounds": {
    "words": {"min": 1, "max": 20},
    "chars": {"max": 300}
  },
  "constraint_reasoning": {
    "v8_breakthrough": "V8 relaxed from 3-6 to 3-8 words and 60 to 70 chars to solve multi-brand failures",
    "system_bounds": "Up to 20 words and 300 chars allows prompt experimentation for complex content"
  }
}
```

## 📊 **A/B Testing API**

### **Enhanced A/B Testing Framework**

```python
from optimization import LLMOptimizer

# Initialize A/B testing with custom evaluation function
def custom_evaluation_function(slug, content):
    """Custom evaluation logic for your specific use case"""
    return {
        'success_rate': 1.0 if slug else 0.0,
        'theme_coverage': calculate_theme_coverage(slug, content),
        'cultural_preservation': measure_cultural_accuracy(slug, content)
    }

# Create optimizer with custom metrics
optimizer = LLMOptimizer({
    'test_function': custom_evaluation_function,
    'primary_metric': 'theme_coverage',
    'secondary_metrics': ['success_rate', 'cultural_preservation']
})

# Run version comparison
results = optimizer.run_comparison(
    versions=['v8', 'v9'],
    test_cases=test_dataset,
    sample_size=30
)

# Get deployment recommendation
best_version = optimizer.get_best_version()
insights = optimizer.generate_insights()
```

### **A/B Testing Response Format**

```json
{
  "comparison_metadata": {
    "comparison_date": "2025-08-21T10:30:00Z",
    "versions_compared": ["v8", "v9"],
    "sample_size": 30,
    "primary_metric": "theme_coverage"
  },
  "performance_results": {
    "v8": {
      "primary_metric_score": 0.85,
      "secondary_metrics": {
        "success_rate": 1.0,
        "cultural_preservation": 0.95
      },
      "individual_results": [...]
    },
    "v9": {
      "primary_metric_score": 0.78,
      "secondary_metrics": {
        "success_rate": 0.33,
        "cultural_preservation": 0.98
      },
      "individual_results": [...]
    }
  },
  "statistical_analysis": {
    "effect_size": 0.07,
    "confidence_interval": [0.02, 0.12],
    "recommendation": "Deploy v8 for robustness, consider v9 for specific appeal cases"
  },
  "insights": {
    "key_findings": [
      "V8 maintains superior reliability",
      "V9 shows enhanced cultural authenticity",
      "Trade-off exists between robustness and appeal"
    ],
    "deployment_recommendation": "v8_primary_v9_selective"
  }
}
```

## 🔒 **Authentication and Security**

### **API Key Management**

```python
# Environment-based configuration (recommended)
import os
from config.settings import SlugGeneratorConfig

# Secure API key loading
try:
    api_key = SlugGeneratorConfig.get_api_key()
    print("✅ API key loaded securely")
except ValueError as e:
    print(f"❌ API key configuration error: {e}")
    # Handle missing API key gracefully
```

### **Rate Limiting and Retry Logic**

```python
# Built-in retry logic with exponential backoff
from utils.retry_logic import exponential_backoff_retry

@exponential_backoff_retry(
    max_retries=3,
    base_delay=1.0,
    max_delay=30.0
)
def api_call_with_retry():
    """API call with automatic retry on failure"""
    return generator.generate_slug_from_content(title, content)

# Custom rate limiting
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_calls=60, time_window=60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = deque()
    
    def is_allowed(self):
        now = time.time()
        # Remove old calls outside time window
        while self.calls and self.calls[0] <= now - self.time_window:
            self.calls.popleft()
        
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False
```

## 🎛️ **Batch Processing API**

### **Efficient Batch Operations**

```python
from extensions.batch_processor import BatchSlugProcessor

# Initialize batch processor
batch_processor = BatchSlugProcessor(
    prompt_version='v8',
    batch_size=10,           # Process in batches to manage memory
    rate_limit_delay=1.0,    # Delay between API calls
    progress_callback=lambda progress: print(f"Progress: {progress}%")
)

# Process multiple URLs
urls = [
    "https://blog.example.com/post1",
    "https://blog.example.com/post2",
    # ... more URLs
]

results = batch_processor.process_urls(urls)

# Process with custom content
content_list = [
    {"title": "Title 1", "content": "Content 1"},
    {"title": "Title 2", "content": "Content 2"},
    # ... more content
]

results = batch_processor.process_content_list(content_list)
```

### **Batch Response Format**

```json
{
  "batch_metadata": {
    "total_items": 50,
    "successful_items": 48,
    "failed_items": 2,
    "processing_time": 245.7,
    "average_time_per_item": 4.91
  },
  "results": [
    {
      "index": 0,
      "url": "https://blog.example.com/post1",
      "status": "success",
      "slug": "generated-slug-for-post1",
      "processing_time": 4.2,
      "confidence": 0.87
    },
    {
      "index": 1,
      "url": "https://blog.example.com/post2",
      "status": "failed",
      "error": "Content extraction failed",
      "processing_time": 2.1
    }
  ],
  "summary_statistics": {
    "average_confidence": 0.84,
    "success_rate": 0.96,
    "average_word_count": 5.2,
    "average_char_count": 42.3
  }
}
```

## 🔍 **Validation API**

### **Pre-Flight Validation**

```python
from scripts.validate_setup import validate_system_configuration

# Comprehensive system validation
validation_result = validate_system_configuration(
    version='v8',
    check_api_connectivity=True,
    check_constraint_compliance=True,
    check_cultural_preservation=True
)

if validation_result['all_checks_passed']:
    print("✅ System ready for production")
else:
    print(f"❌ Validation failures: {validation_result['failed_checks']}")
```

### **Slug Validation API**

```python
from core.validators import validate_slug, validate_slug_system_bounds

# Version-specific validation
config = SlugGeneratorConfig.for_version('v8')
validation_result = validate_slug("test-slug-example", config)

# System bounds validation
system_validation = validate_slug_system_bounds("test-slug-example")

# Combined validation response
combined_result = {
    'version_compliance': validation_result,
    'system_compliance': system_validation,
    'overall_valid': validation_result['is_valid'] and system_validation['is_valid']
}
```

## 📈 **Monitoring and Analytics API**

### **Performance Monitoring**

```python
from monitoring import PerformanceMonitor

# Initialize monitoring
monitor = PerformanceMonitor(
    track_response_times=True,
    track_success_rates=True,
    track_cultural_preservation=True,
    alert_threshold_ms=10000
)

# Generate slug with monitoring
with monitor.track_operation("slug_generation"):
    result = generator.generate_slug_from_content(title, content)

# Get performance metrics
metrics = monitor.get_metrics(time_range="last_24_hours")
```

### **Analytics Response Format**

```json
{
  "time_range": "2025-08-21T00:00:00Z to 2025-08-21T23:59:59Z",
  "total_operations": 1247,
  "performance_metrics": {
    "average_response_time": 4.83,
    "95th_percentile_response_time": 8.20,
    "success_rate": 0.987,
    "cultural_preservation_rate": 0.953
  },
  "version_breakdown": {
    "v8": {
      "operations": 950,
      "success_rate": 1.0,
      "avg_response_time": 4.71
    },
    "v9": {
      "operations": 297,
      "success_rate": 0.34,
      "avg_response_time": 5.12
    }
  },
  "error_analysis": {
    "api_errors": 8,
    "constraint_violations": 5,
    "content_extraction_failures": 3
  }
}
```

## 🚀 **Production Deployment Patterns**

### **Microservice Integration**

```python
# FastAPI service example
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core import SlugGenerator

app = FastAPI(title="Slug Generator API", version="v8.0")

class SlugRequest(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    version: str = "v8"
    include_alternatives: bool = True

class SlugResponse(BaseModel):
    primary: str
    alternatives: List[str]
    confidence: float
    processing_time: float
    metadata: dict

@app.post("/generate-slug", response_model=SlugResponse)
async def generate_slug(request: SlugRequest):
    try:
        generator = SlugGenerator(prompt_version=request.version)
        
        start_time = time.time()
        if request.url:
            result = generator.generate_slug_from_url(request.url)
        else:
            result = generator.generate_slug_from_content(
                request.title, request.content
            )
        processing_time = time.time() - start_time
        
        return SlugResponse(
            primary=result['primary'],
            alternatives=result.get('alternatives', []),
            confidence=result.get('confidence', 0.0),
            processing_time=processing_time,
            metadata=result.get('metadata', {})
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """System health validation endpoint"""
    try:
        # Quick validation
        generator = SlugGenerator(prompt_version='v8')
        test_result = generator.quick_test("Health check")
        return {"status": "healthy", "version": "v8", "test_passed": bool(test_result)}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

### **Container Deployment**

```dockerfile
# Dockerfile for production deployment
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Set environment variables
ENV PYTHONPATH=/app/src
ENV OPENAI_API_KEY=""

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python scripts/validate_setup.py --quick --version v8 || exit 1

# Run application
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Environment Configuration**

```yaml
# docker-compose.yml for production
version: '3.8'
services:
  slug-generator:
    build: .
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## 📚 **SDK and Client Libraries**

### **Python SDK**

```python
# Official Python SDK
from slug_generator_sdk import SlugGeneratorClient

# Initialize client
client = SlugGeneratorClient(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url="https://api.yourdomain.com",  # Your API endpoint
    version='v8'  # Default version
)

# Simple usage
slug = client.generate_slug(url="https://blog.example.com/post")

# Advanced usage with options
slug = client.generate_slug(
    title="Blog post title",
    content="Blog post content",
    version='v8',
    include_alternatives=True,
    cultural_context='asian_ecommerce'
)

# Batch processing
results = client.generate_slugs_batch(urls_list)

# A/B testing
comparison = client.compare_versions(
    content="Test content",
    versions=['v8', 'v9']
)
```

### **JavaScript/Node.js SDK**

```javascript
// Official Node.js SDK
const { SlugGeneratorClient } = require('@your-org/slug-generator-sdk');

const client = new SlugGeneratorClient({
    apiKey: process.env.OPENAI_API_KEY,
    baseUrl: 'https://api.yourdomain.com',
    version: 'v8'
});

// Async/await usage
async function generateSlug(url) {
    try {
        const result = await client.generateSlug({ url });
        return result.primary;
    } catch (error) {
        console.error('Slug generation failed:', error);
        throw error;
    }
}

// Promise-based usage
client.generateSlug({ 
    title: 'Blog post title',
    content: 'Blog post content'
})
.then(result => console.log('Generated slug:', result.primary))
.catch(error => console.error('Error:', error));
```

This API Integration Guide provides comprehensive documentation for integrating with all aspects of the LLM Blog Post Slug Generator, including the breakthrough V9 honest evaluation system and production deployment patterns.