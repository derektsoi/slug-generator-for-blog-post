"""
Unified Prompt Manager - Next Generation Prompt Management System

Template-driven, YAML-based prompt management with integrated development workflow.
Replaces the scattered txt+json system with a unified, developer-friendly approach.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging
from dataclasses import dataclass
from jinja2 import Environment, FileSystemLoader, Template

logger = logging.getLogger(__name__)


@dataclass
class PromptMetrics:
    """Performance metrics for a prompt"""
    avg_overall_score: float
    avg_cultural_score: float
    avg_brand_score: float
    sample_size: int
    last_updated: str
    

@dataclass
class PromptInfo:
    """Complete prompt information"""
    id: str
    name: str
    description: str
    version: str
    author: str
    created: str
    status: str  # development, active, archived
    focus_areas: List[str]
    weights: Dict[str, float]
    thresholds: Dict[str, float]
    prompt_template: str
    test_cases: List[Dict[str, Any]]
    benchmarks: Dict[str, Any]
    file_path: Path
    

class UnifiedPromptManager:
    """
    Unified prompt management system supporting YAML-based prompts
    with templates, validation, and integrated development workflow.
    """
    
    def __init__(self, prompts_dir: str = "src/prompts"):
        """Initialize with prompts directory"""
        self.prompts_dir = Path(prompts_dir)
        self.evaluation_dir = self.prompts_dir / "evaluation"
        self.templates_dir = self.evaluation_dir / "templates"
        
        # Initialize directory structure
        self._ensure_directory_structure()
        
        # Initialize Jinja2 template engine
        self.template_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.template_env.globals['now'] = datetime.now
        
    def _ensure_directory_structure(self) -> None:
        """Ensure proper directory structure exists"""
        directories = [
            self.evaluation_dir / "active",
            self.evaluation_dir / "development", 
            self.evaluation_dir / "templates",
            self.evaluation_dir / "archive",
            self.evaluation_dir / "benchmarks"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
    def list_prompts(self, status: Optional[str] = None) -> List[str]:
        """List available prompts, optionally filtered by status"""
        prompts = []
        
        # Get prompts from different directories based on status
        search_dirs = []
        if status is None:
            search_dirs = ["active", "development", "archive"]
        elif status == "active":
            search_dirs = ["active"]
        elif status == "development":
            search_dirs = ["development"]
        elif status == "archived":
            search_dirs = ["archive"]
        else:
            raise ValueError(f"Invalid status: {status}. Use 'active', 'development', or 'archived'")
        
        for subdir in search_dirs:
            directory = self.evaluation_dir / subdir
            if directory.exists():
                for file_path in directory.glob("*.yaml"):
                    prompts.append(file_path.stem)
        
        return sorted(set(prompts))  # Remove duplicates and sort
    
    def get_prompt_info(self, prompt_id: str) -> PromptInfo:
        """Get complete prompt information"""
        file_path = self._find_prompt_file(prompt_id)
        if not file_path:
            raise FileNotFoundError(f"Prompt '{prompt_id}' not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        meta = data.get('meta', {})
        
        return PromptInfo(
            id=meta.get('id', prompt_id),
            name=meta.get('name', prompt_id),
            description=meta.get('description', ''),
            version=meta.get('version', '1.0'),
            author=meta.get('author', 'unknown'),
            created=meta.get('created', ''),
            status=meta.get('status', 'unknown'),
            focus_areas=data.get('focus', {}).get('primary', ['general']),
            weights=data.get('weights', {}),
            thresholds=data.get('thresholds', {}),
            prompt_template=data.get('prompt', ''),
            test_cases=data.get('test_cases', []),
            benchmarks=data.get('benchmarks', {}),
            file_path=file_path
        )
    
    def get_prompt_template(self, prompt_id: str) -> str:
        """Get the prompt template string"""
        info = self.get_prompt_info(prompt_id)
        return info.prompt_template
    
    def get_prompt_metadata(self, prompt_id: str) -> Dict[str, Any]:
        """Get prompt metadata in legacy format for backward compatibility"""
        info = self.get_prompt_info(prompt_id)
        
        return {
            'prompt_version': info.id,
            'description': info.description,
            'focus_areas': info.focus_areas if isinstance(info.focus_areas, list) else [info.focus_areas],
            'scoring_dimensions': list(info.weights.keys()),
            'dimension_weights': info.weights,
            'quality_thresholds': info.thresholds,
            'created_date': info.created,
            'author': info.author,
            'version': info.version,
            'status': info.status
        }
    
    def _find_prompt_file(self, prompt_id: str) -> Optional[Path]:
        """Find prompt file in active, development, or archive directories"""
        search_order = ["active", "development", "archive"]
        
        for subdir in search_order:
            file_path = self.evaluation_dir / subdir / f"{prompt_id}.yaml"
            if file_path.exists():
                return file_path
        
        return None
    
    def create_from_template(
        self, 
        prompt_id: str, 
        template_name: str, 
        variables: Dict[str, Any]
    ) -> Path:
        """Create new prompt from template"""
        template_file = f"{template_name}.yaml.j2"
        
        try:
            template = self.template_env.get_template(template_file)
        except Exception as e:
            raise FileNotFoundError(f"Template '{template_name}' not found: {e}")
        
        # Add standard variables
        variables.update({
            'prompt_id': prompt_id,
            'created': datetime.now().isoformat(),
        })
        
        # Render template
        content = template.render(**variables)
        
        # Save to development directory
        output_path = self.evaluation_dir / "development" / f"{prompt_id}.yaml"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Created prompt '{prompt_id}' from template '{template_name}' at {output_path}")
        return output_path
    
    def validate_prompt(self, prompt_id: str) -> Dict[str, Any]:
        """Validate prompt structure and content"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            info = self.get_prompt_info(prompt_id)
        except Exception as e:
            validation_results['valid'] = False
            validation_results['errors'].append(f"Failed to load prompt: {e}")
            return validation_results
        
        # Validate required fields
        required_meta_fields = ['id', 'name', 'description', 'version', 'status']
        for field in required_meta_fields:
            if not getattr(info, field, None):
                validation_results['warnings'].append(f"Missing or empty meta field: {field}")
        
        # Validate weights
        if not info.weights:
            validation_results['errors'].append("No dimension weights specified")
            validation_results['valid'] = False
        else:
            weight_sum = sum(info.weights.values())
            if abs(weight_sum - 1.0) > 0.01:  # Allow small floating point differences
                validation_results['warnings'].append(f"Dimension weights sum to {weight_sum:.3f}, not 1.0")
        
        # Validate prompt template
        if not info.prompt_template:
            validation_results['errors'].append("No prompt template specified")
            validation_results['valid'] = False
        else:
            # Check for required template variables
            required_vars = ['title', 'content', 'slug']
            template_content = info.prompt_template.lower()
            for var in required_vars:
                if f"{{{{{var}" not in template_content:
                    validation_results['warnings'].append(f"Template may be missing variable: {{{{{var}}}}}")
        
        # Validate test cases
        if not info.test_cases:
            validation_results['warnings'].append("No test cases specified - consider adding some for validation")
        else:
            for i, test_case in enumerate(info.test_cases):
                required_fields = ['slug', 'title']
                for field in required_fields:
                    if field not in test_case:
                        validation_results['errors'].append(f"Test case {i+1} missing required field: {field}")
                        validation_results['valid'] = False
        
        return validation_results
    
    def promote_prompt(self, prompt_id: str) -> Path:
        """Promote prompt from development to active"""
        dev_path = self.evaluation_dir / "development" / f"{prompt_id}.yaml"
        active_path = self.evaluation_dir / "active" / f"{prompt_id}.yaml"
        
        if not dev_path.exists():
            raise FileNotFoundError(f"Development prompt '{prompt_id}' not found")
        
        # Validate before promotion
        validation = self.validate_prompt(prompt_id)
        if not validation['valid']:
            raise ValueError(f"Cannot promote invalid prompt. Errors: {validation['errors']}")
        
        # Update status to active
        with open(dev_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        data['meta']['status'] = 'active'
        data['meta']['promoted'] = datetime.now().isoformat()
        
        # Write to active directory
        with open(active_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        # Remove from development
        dev_path.unlink()
        
        logger.info(f"Promoted prompt '{prompt_id}' from development to active")
        return active_path
    
    def archive_prompt(self, prompt_id: str) -> Path:
        """Archive a prompt (move to archive directory)"""
        current_path = self._find_prompt_file(prompt_id)
        if not current_path:
            raise FileNotFoundError(f"Prompt '{prompt_id}' not found")
        
        archive_path = self.evaluation_dir / "archive" / f"{prompt_id}.yaml"
        
        # Update status to archived
        with open(current_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        data['meta']['status'] = 'archived'
        data['meta']['archived'] = datetime.now().isoformat()
        
        # Write to archive directory
        with open(archive_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        # Remove from original location
        current_path.unlink()
        
        logger.info(f"Archived prompt '{prompt_id}' to {archive_path}")
        return archive_path
    
    def list_templates(self) -> List[str]:
        """List available prompt templates"""
        templates = []
        if self.templates_dir.exists():
            for file_path in self.templates_dir.glob("*.yaml.j2"):
                templates.append(file_path.stem)
        return sorted(templates)
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Get information about a template"""
        template_file = self.templates_dir / f"{template_name}.yaml.j2"
        if not template_file.exists():
            raise FileNotFoundError(f"Template '{template_name}' not found")
        
        # Parse template to extract metadata comments
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract template documentation from comments
        lines = content.split('\n')
        doc_lines = []
        for line in lines:
            if line.strip().startswith('#'):
                doc_lines.append(line.strip('# ').strip())
            elif line.strip():  # Stop at first non-comment, non-empty line
                break
        
        return {
            'name': template_name,
            'description': ' '.join(doc_lines) if doc_lines else f"Template for {template_name} prompts",
            'file_path': str(template_file)
        }


# Backward compatibility wrapper
class EvaluationPromptManager:
    """Backward compatibility wrapper for existing code"""
    
    def __init__(self, config_dir: str = "src/config/evaluation_prompts"):
        # Try to use unified system first, fall back to legacy
        try:
            self.unified_manager = UnifiedPromptManager()
            self.use_unified = True
        except Exception:
            # Fall back to legacy system if needed
            self.use_unified = False
            from .evaluation_prompt_manager import EvaluationPromptManager as LegacyManager
            self.legacy_manager = LegacyManager(config_dir)
    
    def list_available_versions(self) -> List[str]:
        """List available evaluation prompt versions"""
        if self.use_unified:
            return self.unified_manager.list_prompts(status="active")
        else:
            return self.legacy_manager.list_available_versions()
    
    def load_prompt_template(self, version: str) -> str:
        """Load prompt template for specified version"""
        if self.use_unified:
            return self.unified_manager.get_prompt_template(version)
        else:
            return self.legacy_manager.load_prompt_template(version)
    
    def get_prompt_metadata(self, version: str) -> Dict[str, Any]:
        """Get metadata for specified version"""
        if self.use_unified:
            return self.unified_manager.get_prompt_metadata(version)
        else:
            return self.legacy_manager.get_prompt_metadata(version)