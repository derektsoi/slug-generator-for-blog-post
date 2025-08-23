"""
CLI Framework for Evaluation Tools

Provides base classes and utilities for building consistent CLI tools
for evaluation prompt testing, comparison, and validation.
"""

from .base import (
    BaseCLI,
    CLIError,
    TestDataMixin,
    PromptValidationMixin,
    OutputFormattingMixin,
    ProgressTrackingMixin,
    ProgressTracker,
    setup_common_args,
    add_sample_size_arg
)

__all__ = [
    'BaseCLI',
    'CLIError', 
    'TestDataMixin',
    'PromptValidationMixin',
    'OutputFormattingMixin',
    'ProgressTrackingMixin',
    'ProgressTracker',
    'setup_common_args',
    'add_sample_size_arg'
]