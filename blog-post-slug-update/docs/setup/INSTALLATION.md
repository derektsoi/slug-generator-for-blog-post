# Installation Guide

## 🚀 Quick Setup

### Requirements
- Python 3.12+
- OpenAI API key

### Step 1: Clone and Setup
```bash
git clone https://github.com/derektsoi/slug-generator-for-blog-post.git
cd blog-post-slug-update
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure API Key
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### Step 4: Verify Installation
```bash
python scripts/validate_setup.py
```

## ✅ Quick Test
```bash
python scripts/suggest_slug.py https://example.com/blog-post
```

For detailed configuration options, see [Configuration Guide](CONFIGURATION.md).