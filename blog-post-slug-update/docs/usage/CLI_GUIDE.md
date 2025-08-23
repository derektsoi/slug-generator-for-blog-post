# CLI Usage Guide

## Basic Usage

### Generate Single Slug
```bash
python scripts/suggest_slug.py https://blog.example.com/post
```

### Multiple Alternatives
```bash
python scripts/suggest_slug.py --count 3 https://blog.example.com/post
```

### Verbose Output
```bash
python scripts/suggest_slug.py --verbose https://blog.example.com/post
```

## Advanced Options

### Specify Prompt Version
```bash
python scripts/suggest_slug.py --version v10 https://blog.example.com/post
```

### Batch Processing
```bash
python scripts/run_production_batch.py --input urls.json --output ./results/
```

## Real Examples

### Cross-border E-commerce
```bash
# Input: Japanese jewelry brands
python scripts/suggest_slug.py "https://buyandship.today/blog/agete-nojess-star-jewelry"

# Expected Output:
# Primary: agete-nojess-star-jewelry-japan-guide
# Alternatives: japanese-jewelry-brands-guide, luxury-jewelry-shopping-guide
# Confidence: 0.95
```

### Cultural Content
```bash  
# Input: Asian shopping guide
python scripts/suggest_slug.py "https://example.com/大國藥妝香港購物教學"

# Expected Output:
# Primary: daikoku-drugstore-hongkong-proxy-guide
# Alternatives: hong-kong-drugstore-shopping-guide  
# Confidence: 0.92
```

For batch processing, see [Batch Processing Guide](BATCH_PROCESSING.md).