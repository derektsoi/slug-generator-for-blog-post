"""
LLM Optimization Tool

A reusable framework for systematic prompt optimization through A/B testing,
metrics collection, and automated analysis.

Designed for production LLM applications requiring data-driven prompt improvement.
"""

__version__ = "1.0.0"
__author__ = "Claude Code"

from .core.optimizer import LLMOptimizer
from .core.test_runner import TestRunner
from .core.metrics_calculator import MetricsCalculator
from .core.comparator import Comparator

__all__ = [
    "LLMOptimizer",
    "TestRunner", 
    "MetricsCalculator",
    "Comparator"
]