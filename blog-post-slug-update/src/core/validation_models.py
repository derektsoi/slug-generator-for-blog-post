#!/usr/bin/env python3
"""
Standardized validation models and result structures.
Extracted from Phase 2 components for consistency and maintainability.
"""

import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ValidationStatus(Enum):
    """Standard validation status codes"""
    PASSED = "passed"
    FAILED = "failed" 
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class ValidationResult:
    """Standardized validation result structure"""
    passed: bool
    message: str
    status: ValidationStatus = field(init=False)
    timestamp: float = field(default_factory=time.time)
    fix_suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set status based on passed field"""
        self.status = ValidationStatus.PASSED if self.passed else ValidationStatus.FAILED
    
    def add_fix_suggestion(self, suggestion: str) -> 'ValidationResult':
        """Add fix suggestion and return self for chaining"""
        self.fix_suggestions.append(suggestion)
        return self
    
    def add_metadata(self, key: str, value: Any) -> 'ValidationResult':
        """Add metadata and return self for chaining"""
        self.metadata[key] = value
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for backward compatibility"""
        result = {
            'passed': self.passed,
            'message': self.message,
            'timestamp': self.timestamp
        }
        
        if self.fix_suggestions:
            result['fix'] = self.fix_suggestions[0]  # Legacy single fix field
            result['fix_suggestions'] = self.fix_suggestions
        
        if self.metadata:
            result.update(self.metadata)
            
        return result


@dataclass 
class ConfigurationSpec:
    """Configuration specification for version-aware settings"""
    version: str
    max_slug_words: int
    max_slug_chars: int
    description: str = ""
    
    @classmethod
    def get_specifications(cls) -> Dict[str, 'ConfigurationSpec']:
        """Get all configuration specifications"""
        return {
            'v6': cls(
                version='v6',
                max_slug_words=6,
                max_slug_chars=60,
                description="Standard constraints for V6 Cultural Enhanced"
            ),
            'v8': cls(
                version='v8', 
                max_slug_words=8,
                max_slug_chars=70,
                description="Enhanced constraints for V8 breakthrough (multi-brand)"
            ),
            'v10': cls(
                version='v10',
                max_slug_words=10, 
                max_slug_chars=90,
                description="Competitive constraints for V10 production deployment"
            )
        }
    
    @classmethod
    def for_version(cls, version: str) -> 'ConfigurationSpec':
        """Get configuration specification for version"""
        specs = cls.get_specifications()
        if version not in specs:
            available = ', '.join(specs.keys())
            raise ValueError(f"Invalid version '{version}'. Available: {available}")
        return specs[version]


@dataclass
class ValidationSuite:
    """Collection of validation results with aggregation"""
    name: str
    results: Dict[str, ValidationResult] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def add_result(self, check_name: str, result: ValidationResult) -> 'ValidationSuite':
        """Add validation result and return self for chaining"""
        self.results[check_name] = result
        return self
    
    @property
    def overall_passed(self) -> bool:
        """Check if all validations passed"""
        return all(result.passed for result in self.results.values())
    
    @property
    def failed_checks(self) -> List[str]:
        """Get list of failed check names"""
        return [name for name, result in self.results.items() if not result.passed]
    
    @property
    def passed_checks(self) -> List[str]:
        """Get list of passed check names"""  
        return [name for name, result in self.results.items() if result.passed]
    
    def get_recommendation(self) -> str:
        """Get overall recommendation"""
        return "PROCEED" if self.overall_passed else "FIX_ISSUES"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for backward compatibility"""
        return {
            'overall_passed': self.overall_passed,
            'recommendation': self.get_recommendation(),
            'results': {name: result.to_dict() for name, result in self.results.items()},
            'summary': {
                'total_checks': len(self.results),
                'passed': len(self.passed_checks),
                'failed': len(self.failed_checks),
                'failed_checks': self.failed_checks
            }
        }