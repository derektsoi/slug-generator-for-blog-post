"""
Unit Tests for EvaluationPromptManager

These tests define the behavior of the new EvaluationPromptManager class
for handling configurable evaluation prompts.

TDD Phase: RED (these will initially fail - class doesn't exist yet)
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import sys

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

# This import will initially fail - that's expected in RED phase
try:
    from config.evaluation_prompt_manager import EvaluationPromptManager
except ImportError:
    # Expected to fail initially - we haven't created the class yet
    EvaluationPromptManager = None


class TestEvaluationPromptManager:
    """Test the EvaluationPromptManager class functionality"""
    
    def setup_method(self):
        """Set up test environment before each test"""
        if EvaluationPromptManager is None:
            pytest.skip("EvaluationPromptManager not implemented yet - RED phase expected")
        
        # Create temporary directory for test prompt files
        self.temp_dir = tempfile.mkdtemp()
        self.prompts_dir = Path(self.temp_dir) / "evaluation_prompts"
        self.prompts_dir.mkdir(parents=True)
        
        # Create metadata directory
        self.metadata_dir = self.prompts_dir / "metadata"
        self.metadata_dir.mkdir()
    
    def teardown_method(self):
        """Clean up test environment after each test"""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir)
    
    def test_evaluation_prompt_manager_initialization(self):
        """EvaluationPromptManager should initialize with config directory"""
        manager = EvaluationPromptManager(config_dir=str(self.prompts_dir))
        
        assert manager.config_dir == Path(self.prompts_dir)
    
    def test_evaluation_prompt_manager_default_config_dir(self):
        """EvaluationPromptManager should use default config directory"""
        manager = EvaluationPromptManager()
        
        expected_dir = Path("src/config/evaluation_prompts")
        assert manager.config_dir == expected_dir
    
    def test_list_available_versions_returns_all_prompt_files(self):
        """list_available_versions should return all .txt files in config directory"""
        # Create test prompt files
        (self.prompts_dir / "current.txt").write_text("Test prompt 1")
        (self.prompts_dir / "v1_baseline.txt").write_text("Test prompt 2")
        (self.prompts_dir / "v2_cultural.txt").write_text("Test prompt 3")
        (self.prompts_dir / "README.md").write_text("Not a prompt")  # Should be ignored
        
        manager = EvaluationPromptManager(config_dir=str(self.prompts_dir))
        versions = manager.list_available_versions()
        
        expected_versions = ["current", "v1_baseline", "v2_cultural"]
        assert sorted(versions) == sorted(expected_versions)
        assert "README" not in versions  # Non-.txt files should be ignored
    
    def test_list_available_versions_empty_directory(self):
        """list_available_versions should return empty list for empty directory"""
        manager = EvaluationPromptManager(config_dir=str(self.prompts_dir))
        versions = manager.list_available_versions()
        
        assert versions == []
    
    def test_load_prompt_template_returns_correct_content(self):
        """load_prompt_template should return content of specified prompt file"""
        test_content = """
        Evaluate this SEO slug:
        SLUG: "{slug}"
        TITLE: "{title}"
        Rate from 0.0-1.0...
        """
        
        (self.prompts_dir / "test_version.txt").write_text(test_content)
        
        manager = EvaluationPromptManager(config_dir=str(self.prompts_dir))
        content = manager.load_prompt_template("test_version")
        
        assert content.strip() == test_content.strip()
    
    def test_load_prompt_template_nonexistent_file_raises_error(self):
        """load_prompt_template should raise appropriate error for missing file"""
        manager = EvaluationPromptManager(config_dir=str(self.prompts_dir))
        
        with pytest.raises(FileNotFoundError) as exc_info:
            manager.load_prompt_template("nonexistent")
        
        assert "nonexistent" in str(exc_info.value)
    
    def test_get_prompt_metadata_loads_json_correctly(self):
        """get_prompt_metadata should load and return JSON metadata"""
        test_metadata = {
            "prompt_version": "test_version",
            "description": "Test evaluation prompt",
            "scoring_dimensions": [
                "user_intent_match",
                "brand_hierarchy", 
                "cultural_authenticity"
            ],
            "dimension_weights": {
                "user_intent_match": 0.4,
                "brand_hierarchy": 0.3,
                "cultural_authenticity": 0.3
            }
        }
        
        metadata_file = self.metadata_dir / "test_version.json"
        with open(metadata_file, 'w') as f:
            json.dump(test_metadata, f)
        
        manager = EvaluationPromptManager(config_dir=str(self.prompts_dir))
        metadata = manager.get_prompt_metadata("test_version")
        
        assert metadata == test_metadata
        assert metadata["prompt_version"] == "test_version"
        assert len(metadata["scoring_dimensions"]) == 3
    
    def test_get_prompt_metadata_missing_file_returns_defaults(self):
        """get_prompt_metadata should return default metadata for missing file"""
        manager = EvaluationPromptManager(config_dir=str(self.prompts_dir))
        metadata = manager.get_prompt_metadata("missing_version")
        
        # Should return default metadata structure
        assert "prompt_version" in metadata
        assert "scoring_dimensions" in metadata
        assert "dimension_weights" in metadata
        assert metadata["prompt_version"] == "missing_version"
        
        # Should have standard scoring dimensions
        expected_dimensions = [
            'user_intent_match',
            'brand_hierarchy', 
            'cultural_authenticity',
            'click_through_potential',
            'competitive_differentiation',
            'technical_seo'
        ]
        assert metadata["scoring_dimensions"] == expected_dimensions
    
    def test_validate_prompt_config_validates_complete_config(self):
        """validate_prompt_config should validate complete prompt configuration"""
        # Create valid prompt file
        (self.prompts_dir / "valid_config.txt").write_text("Test prompt content")
        
        # Create valid metadata file  
        valid_metadata = {
            "prompt_version": "valid_config",
            "description": "Valid test prompt",
            "scoring_dimensions": ["user_intent_match", "brand_hierarchy"],
            "dimension_weights": {"user_intent_match": 0.6, "brand_hierarchy": 0.4},
            "quality_thresholds": {"minimum_confidence": 0.7}
        }
        
        metadata_file = self.metadata_dir / "valid_config.json"
        with open(metadata_file, 'w') as f:
            json.dump(valid_metadata, f)
        
        manager = EvaluationPromptManager(config_dir=str(self.prompts_dir))
        result = manager.validate_prompt_config("valid_config")
        
        assert result["is_valid"] == True
        assert result["errors"] == []
        assert result["warnings"] == []
    
    def test_validate_prompt_config_catches_missing_prompt_file(self):
        """validate_prompt_config should catch missing prompt file"""
        manager = EvaluationPromptManager(config_dir=str(self.prompts_dir))
        result = manager.validate_prompt_config("missing_prompt")
        
        assert result["is_valid"] == False
        assert any("prompt file not found" in error.lower() for error in result["errors"])
    
    def test_validate_prompt_config_catches_invalid_metadata_json(self):
        """validate_prompt_config should catch invalid JSON metadata"""
        # Create valid prompt file
        (self.prompts_dir / "invalid_metadata.txt").write_text("Test prompt")
        
        # Create invalid JSON metadata file
        metadata_file = self.metadata_dir / "invalid_metadata.json"
        metadata_file.write_text("{ invalid json content }")
        
        manager = EvaluationPromptManager(config_dir=str(self.prompts_dir))
        result = manager.validate_prompt_config("invalid_metadata")
        
        assert result["is_valid"] == False
        assert any("json" in error.lower() for error in result["errors"])
    
    def test_validate_prompt_config_catches_dimension_weight_mismatch(self):
        """validate_prompt_config should catch dimension/weight mismatches"""
        # Create valid prompt file
        (self.prompts_dir / "weight_mismatch.txt").write_text("Test prompt")
        
        # Create metadata with mismatched dimensions and weights
        invalid_metadata = {
            "prompt_version": "weight_mismatch",
            "scoring_dimensions": ["user_intent_match", "brand_hierarchy"], 
            "dimension_weights": {"user_intent_match": 0.6}  # Missing brand_hierarchy weight
        }
        
        metadata_file = self.metadata_dir / "weight_mismatch.json"
        with open(metadata_file, 'w') as f:
            json.dump(invalid_metadata, f)
        
        manager = EvaluationPromptManager(config_dir=str(self.prompts_dir))
        result = manager.validate_prompt_config("weight_mismatch")
        
        assert result["is_valid"] == False
        assert any("weight" in error.lower() for error in result["errors"])
    
    def test_validate_prompt_config_warns_about_weight_sum_not_one(self):
        """validate_prompt_config should warn when dimension weights don't sum to 1.0"""
        # Create valid prompt file
        (self.prompts_dir / "weight_sum.txt").write_text("Test prompt")
        
        # Create metadata with weights that don't sum to 1.0
        metadata = {
            "prompt_version": "weight_sum",
            "scoring_dimensions": ["user_intent_match", "brand_hierarchy"],
            "dimension_weights": {"user_intent_match": 0.3, "brand_hierarchy": 0.3}  # Sums to 0.6
        }
        
        metadata_file = self.metadata_dir / "weight_sum.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)
        
        manager = EvaluationPromptManager(config_dir=str(self.prompts_dir))
        result = manager.validate_prompt_config("weight_sum")
        
        # Should be valid but with warnings
        assert result["is_valid"] == True
        assert any("sum" in warning.lower() for warning in result["warnings"])
    
    def test_get_default_metadata_structure(self):
        """get_default_metadata should return properly structured default metadata"""
        manager = EvaluationPromptManager(config_dir=str(self.prompts_dir))
        default_metadata = manager.get_default_metadata("test_version")
        
        required_fields = [
            "prompt_version",
            "description", 
            "scoring_dimensions",
            "dimension_weights",
            "quality_thresholds",
            "created_date",
            "author"
        ]
        
        for field in required_fields:
            assert field in default_metadata
        
        assert default_metadata["prompt_version"] == "test_version"
        assert len(default_metadata["scoring_dimensions"]) == 6
        assert len(default_metadata["dimension_weights"]) == 6
        
        # Weights should sum to 1.0
        weight_sum = sum(default_metadata["dimension_weights"].values())
        assert abs(weight_sum - 1.0) < 0.001