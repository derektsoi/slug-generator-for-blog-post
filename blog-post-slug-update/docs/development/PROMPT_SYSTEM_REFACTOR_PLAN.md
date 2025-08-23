# Prompt System Refactor Plan: Developer-First Architecture

## 🎯 Vision: 2-Minute Prompt Creation to Production

**Goal**: Make prompt iteration as easy as changing a configuration file, with built-in testing, validation, and deployment pipeline.

## 🔧 Proposed New Structure

### Unified Prompt Architecture
```
src/
├── prompts/                    # Unified prompt system
│   ├── evaluation/
│   │   ├── active/            # Production prompts (YAML format)
│   │   │   ├── current.yaml
│   │   │   ├── cultural_focused.yaml
│   │   │   └── competitive_focused.yaml
│   │   ├── development/       # Work-in-progress prompts
│   │   │   ├── experimental_semantic.yaml
│   │   │   └── draft_technical.yaml
│   │   ├── templates/         # Prompt creation templates
│   │   │   ├── basic.yaml.j2
│   │   │   ├── cultural.yaml.j2
│   │   │   └── competitive.yaml.j2
│   │   ├── archive/          # Version history
│   │   └── benchmarks/       # Performance data
│   │       ├── cultural_focused_results.json
│   │       └── competitive_focused_results.json
│   └── generation/           # Existing V1-V10 prompts
│       └── ...
├── cli/
│   ├── commands/             # Specialized command modules
│   │   ├── prompt.py         # Unified prompt development commands
│   │   ├── evaluation.py     # Evaluation workflow
│   │   └── benchmark.py      # Performance testing
│   ├── base.py              # Framework (existing)
│   ├── analysis.py          # Statistical analysis (existing)
│   └── __init__.py
├── config/
│   ├── prompt_manager.py    # Unified prompt management
│   └── constants.py
└── evaluation/
    └── core/
        └── seo_evaluator.py
```

## 🏗️ Key Design Principles

### 1. Single YAML Format
**Replace**: `prompt.txt` + `metadata.json`  
**With**: `prompt.yaml` (everything in one file)

```yaml
# src/prompts/evaluation/active/cultural_focused.yaml
meta:
  id: cultural_focused
  name: "Cultural Authenticity Focused Evaluation"
  version: "2.1"
  description: "Prioritizes cultural term preservation over competitive appeal"
  author: "dev@company.com"
  created: "2025-01-23"
  status: active  # development, active, archived
  base_template: cultural
  
focus:
  primary: cultural_authenticity
  secondary: brand_hierarchy
  
weights:
  cultural_authenticity: 0.25
  brand_hierarchy: 0.20
  user_intent_match: 0.15
  technical_seo: 0.15
  click_through_potential: 0.15
  competitive_differentiation: 0.10

thresholds:
  minimum_confidence: 0.7
  cultural_preservation_threshold: 0.8
  
prompt: |
  You are evaluating a URL slug for SEO effectiveness with emphasis on cultural authenticity.
  
  EVALUATION PRIORITY ORDER:
  1. Cultural Authenticity (25%): Preserve cultural terms (一番賞 → ichiban-kuji)
  2. Brand Hierarchy (20%): Respect brand positioning and recognition
  3. User Intent Match (15%): Align with search behavior
  4. Technical SEO (15%): Follow SEO best practices
  5. Click Appeal (15%): Generate engagement
  6. Competitive Edge (10%): Differentiate from competitors
  
  CONTENT TO EVALUATE:
  Title: {{title}}
  Content: {{content}}  
  Proposed Slug: {{slug}}
  
  Please evaluate the slug across all dimensions and provide scores 0.0-1.0...

test_cases:
  - name: "Ichiban Kuji Guide"
    slug: "ultimate-ichiban-kuji-guide"
    title: "一番賞完全購入指南"
    content: "Complete guide to ichiban-kuji purchasing"
    expectations:
      cultural_authenticity: ">= 0.8"
      overall: ">= 0.75"
  - name: "Daikoku Drugstore"  
    slug: "daikoku-drugstore-shopping"
    title: "大國藥妝購物攻略"
    content: "Daikoku drugstore shopping guide"
    expectations:
      cultural_authenticity: ">= 0.9"
      overall: ">= 0.80"

benchmarks:
  baseline: "current"
  target_improvement: 0.05
  min_performance:
    avg_overall: 0.70
    avg_cultural: 0.75
```

### 2. Template-Driven Creation
**Templates with Jinja2 for easy customization:**

```yaml
# src/prompts/evaluation/templates/cultural.yaml.j2
meta:
  id: "{{ prompt_id }}"
  name: "{{ display_name }}"
  description: "{{ description }}"
  author: "{{ author }}"
  created: "{{ now() }}"
  status: development
  base_template: cultural

focus:
  primary: {{ primary_focus }}
  secondary: {{ secondary_focus | default('brand_hierarchy') }}

weights:
  cultural_authenticity: {{ cultural_weight | default(0.25) }}
  brand_hierarchy: {{ brand_weight | default(0.20) }}
  user_intent_match: {{ intent_weight | default(0.15) }}
  # ... etc

prompt: |
  You are evaluating a URL slug for SEO effectiveness with emphasis on {{ primary_focus | replace('_', ' ') }}.
  
  {{ custom_instructions | default('') }}
  
  EVALUATION PRIORITY ORDER:
  1. {{ primary_focus | title | replace('_', ' ') }} ({{ cultural_weight * 100 }}%): {{ focus_description }}
  # ... standard framework continues

test_cases: {{ test_cases | default([]) }}
benchmarks:
  baseline: "current"
  target_improvement: {{ target_improvement | default(0.05) }}
```

### 3. Unified CLI Commands
**Single `prompt` command for entire development lifecycle:**

```bash
# Create new prompt from template
python -m cli prompt create cultural_semantic --template cultural --focus semantic_search

# Test prompt during development  
python -m cli prompt test cultural_semantic --samples 5 --verbose

# Compare with existing prompts
python -m cli prompt compare cultural_semantic cultural_focused --metric cultural_authenticity

# Validate before promotion
python -m cli prompt validate cultural_semantic --comprehensive --fix-issues

# Benchmark performance
python -m cli prompt benchmark cultural_semantic --baseline current --samples 20

# Promote to production
python -m cli prompt promote cultural_semantic

# List and manage prompts
python -m cli prompt list --status development
python -m cli prompt archive old_competitive_focused
```

### 4. Integrated Development Workflow
**Complete prompt development pipeline:**

#### Phase 1: Creation (30 seconds)
```bash
$ python -m cli prompt create my_new_prompt --template cultural

🎨 Creating new evaluation prompt: my_new_prompt
📋 Template: cultural (cultural authenticity focused)
✅ Created: src/prompts/evaluation/development/my_new_prompt.yaml
📝 Open the file to customize weights and instructions
🧪 Test with: python -m cli prompt test my_new_prompt
```

#### Phase 2: Development & Testing (5 minutes)
```bash
$ python -m cli prompt test my_new_prompt --samples 3

🧪 Testing: my_new_prompt (development)
📊 Running 3 test cases with cultural focus...

[1/3] Ichiban Kuji Guide
  Overall: 0.850 | Cultural: 0.900 | Brand: 0.800
  ✅ Meets expectations (cultural >= 0.8)

[2/3] Daikoku Drugstore  
  Overall: 0.720 | Cultural: 0.750 | Brand: 0.700
  ⚠️ Below expectation (cultural >= 0.9) 

[3/3] Korean Skincare
  Overall: 0.780 | Cultural: 0.820 | Brand: 0.750
  ✅ Meets expectations

📈 SUMMARY: 2/3 tests passed | Avg Overall: 0.783 | Avg Cultural: 0.823
💡 Consider increasing cultural weight for Daikoku-style content
```

#### Phase 3: Comparison & Validation (2 minutes)
```bash
$ python -m cli prompt compare my_new_prompt cultural_focused

📊 COMPARISON: my_new_prompt vs cultural_focused
Sample Size: 10 cases | Test Duration: 45s

Performance Metrics:
                    my_new_prompt  cultural_focused  Difference
Overall Score            0.783           0.775        +0.008
Cultural Score           0.823           0.810        +0.013  ✅
Brand Score             0.750           0.765        -0.015
User Intent             0.771           0.780        -0.009

🎯 Cultural Focus Analysis:
✅ my_new_prompt shows 1.3% improvement in cultural scoring
⚠️ Slight decrease in brand hierarchy scoring
💡 Recommendation: Consider adjusting brand weight from 0.20 to 0.22

🏆 Winner: my_new_prompt (0.8% overall improvement)
```

#### Phase 4: Production Promotion (30 seconds)
```bash
$ python -m cli prompt promote my_new_prompt

🔄 Promoting my_new_prompt to production...
✅ Validation passed (comprehensive checks)
✅ Benchmarks exceed baseline by 0.8%
✅ All test cases pass
📁 Moved to: src/prompts/evaluation/active/my_new_prompt.yaml
🚀 Available for production use
```

## 🛠️ Implementation Plan

### Phase 1: Core Infrastructure (2 hours)
1. **Unified PromptManager**: Replace EvaluationPromptManager with YAML-based system
2. **Template Engine**: Jinja2 integration for prompt creation
3. **Validation System**: YAML schema validation and test case verification

### Phase 2: CLI Integration (3 hours)  
1. **Unified Commands**: Single `prompt` CLI with subcommands
2. **Workflow Integration**: Create → Test → Compare → Promote pipeline
3. **Enhanced Output**: Better formatting and actionable insights

### Phase 3: Developer Experience (2 hours)
1. **Templates**: Create cultural, competitive, and balanced templates
2. **Documentation**: Interactive help and examples
3. **Migration Tools**: Convert existing prompts to new format

## 🎯 Benefits for Future Developers

### Dramatically Reduced Barrier to Entry
- **30 seconds**: Create new prompt from template
- **5 minutes**: Test and iterate with real data  
- **2 minutes**: Compare performance against baselines
- **30 seconds**: Deploy to production

### Built-in Best Practices
- **Schema validation**: Prevent configuration errors
- **Test cases**: Ensure quality before deployment
- **Benchmarking**: Performance-driven development
- **Version control**: Clear development → production workflow

### Unified Development Experience
- **Single CLI**: One command for all prompt operations
- **Consistent format**: YAML everywhere, no split files
- **Template system**: Best practices encoded in templates
- **Integrated testing**: Real data validation at every step

## 🚀 Migration Strategy

### Step 1: Parallel System
- Build new YAML-based system alongside existing
- Convert existing prompts to new format
- Test compatibility with existing CLI tools

### Step 2: Gradual Migration  
- Update CLI tools to use new PromptManager
- Maintain backward compatibility during transition
- Add migration commands for easy conversion

### Step 3: Full Transition
- Remove old system after validation
- Update documentation and examples
- Train developers on new workflow

This refactored system will transform prompt development from a complex, error-prone process into a streamlined, developer-friendly workflow that encourages experimentation and rapid iteration.