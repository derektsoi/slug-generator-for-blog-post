"""
EvaluationPromptManager - Configuration management for evaluation prompts

Manages evaluation prompt versions, metadata, and validation for the
configurable LLM-as-a-Judge system.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from .constants import DEFAULT_SCORING_DIMENSIONS

# Set up logging
logger = logging.getLogger(__name__)


class EvaluationPromptManager:
    """Manages evaluation prompt versions and metadata"""
    
    def __init__(self, config_dir: str = "src/config/evaluation_prompts"):
        """Initialize with configuration directory path"""
        self.config_dir = Path(config_dir)
        
        # Use centralized scoring dimensions
        self.default_scoring_dimensions = DEFAULT_SCORING_DIMENSIONS
    
    def list_available_versions(self) -> List[str]:
        """List all available evaluation prompt versions"""
        if not self.config_dir.exists():
            return []
        
        versions = []
        for file_path in self.config_dir.glob("*.txt"):
            # Extract version name from filename (without .txt extension)
            version_name = file_path.stem
            versions.append(version_name)
        
        return sorted(versions)
    
    def load_prompt_template(self, version: str) -> str:
        """Load raw prompt template for specified version"""
        prompt_file = self.config_dir / f"{version}.txt"
        
        if not prompt_file.exists():
            logger.warning(f"Evaluation prompt file not found: {prompt_file}")
            raise FileNotFoundError(f"Evaluation prompt file not found: {prompt_file}")
        
        try:
            return prompt_file.read_text(encoding='utf-8')
        except (IOError, UnicodeDecodeError) as e:
            logger.error(f"Failed to read prompt file {prompt_file}: {e}")
            raise
    
    def get_prompt_metadata(self, version: str) -> Dict[str, Any]:
        """Get metadata for specific prompt version"""
        metadata_file = self.config_dir / "metadata" / f"{version}.json"
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                return metadata
            except json.JSONDecodeError:
                # Fall back to default metadata if JSON is invalid
                pass
        
        # Return default metadata if file doesn't exist or is invalid
        return self.get_default_metadata(version)
    
    def get_default_metadata(self, version: str) -> Dict[str, Any]:
        """Get default metadata structure for a version"""
        return {
            "prompt_version": version,
            "description": f"Default metadata for {version}",
            "focus_areas": ["balanced_evaluation"],
            "scoring_dimensions": self.default_scoring_dimensions,
            "dimension_weights": self._create_balanced_weights(self.default_scoring_dimensions),
            "quality_thresholds": {
                "minimum_confidence": 0.7
            },
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "author": "system",
            "use_cases": ["general_evaluation"]
        }
    
    def validate_prompt_config(self, version: str) -> Dict[str, Any]:
        """Validate prompt configuration and metadata"""
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check if prompt file exists
        prompt_file = self.config_dir / f"{version}.txt"
        if not prompt_file.exists():
            result["is_valid"] = False
            result["errors"].append(f"Prompt file not found: {prompt_file}")
        
        # Check metadata file
        metadata_file = self.config_dir / "metadata" / f"{version}.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Validate metadata structure
                validation_result = self._validate_metadata_structure(metadata)
                result["errors"].extend(validation_result["errors"])
                result["warnings"].extend(validation_result["warnings"])
                
                if validation_result["errors"]:
                    result["is_valid"] = False
                    
            except json.JSONDecodeError as e:
                result["is_valid"] = False
                result["errors"].append(f"Invalid JSON in metadata file: {e}")
        else:
            result["warnings"].append("No metadata file found, will use defaults")
        
        return result
    
    def _validate_metadata_structure(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the structure and content of metadata"""
        result = {
            "errors": [],
            "warnings": []
        }
        
        # Check required fields
        required_fields = ["prompt_version", "scoring_dimensions"]
        for field in required_fields:
            if field not in metadata:
                result["errors"].append(f"Missing required field: {field}")
        
        # Validate scoring dimensions and weights consistency
        if "scoring_dimensions" in metadata and "dimension_weights" in metadata:
            dimensions = set(metadata["scoring_dimensions"])
            weight_keys = set(metadata["dimension_weights"].keys())
            
            if dimensions != weight_keys:
                missing_weights = dimensions - weight_keys
                extra_weights = weight_keys - dimensions
                
                if missing_weights:
                    result["errors"].append(f"Missing weights for dimensions: {missing_weights}")
                if extra_weights:
                    result["errors"].append(f"Extra weights for unknown dimensions: {extra_weights}")
            
            # Check if weights sum to approximately 1.0
            if "dimension_weights" in metadata:
                weight_sum = sum(metadata["dimension_weights"].values())
                if abs(weight_sum - 1.0) > 0.01:  # Allow small floating point errors
                    result["warnings"].append(
                        f"Dimension weights sum to {weight_sum:.3f}, not 1.0. "
                        f"This may affect evaluation balance."
                    )
        
        return result
    
    def _create_balanced_weights(self, dimensions: List[str]) -> Dict[str, float]:
        """Create balanced weights that sum exactly to 1.0"""
        if not dimensions:
            return {}
        
        base_weight = 1.0 / len(dimensions)
        weights = {}
        
        # Assign base weight to all but the last dimension
        total_assigned = 0.0
        for dim in dimensions[:-1]:
            weight = round(base_weight, 6)  # Higher precision for intermediate calculation
            weights[dim] = weight
            total_assigned += weight
        
        # Assign remaining weight to last dimension to ensure sum = 1.0
        weights[dimensions[-1]] = round(1.0 - total_assigned, 6)
        
        return weights