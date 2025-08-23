#!/usr/bin/env python3
"""
Component Factory - Centralized component creation and dependency injection
Refactored from BatchProcessingContext to eliminate initialization complexity.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Use shared import utilities
try:
    from .import_utils import import_from_core
    # Import Phase 1 components
    AtomicJSONLWriter = import_from_core('atomic_writer', 'AtomicJSONLWriter')
    RobustCheckpointManager = import_from_core('robust_checkpoint', 'RobustCheckpointManager')
    SynchronizedProgressTracker = import_from_core('synchronized_progress', 'SynchronizedProgressTracker')
    # Import Phase 2 components
    ConfigurationPipeline = import_from_core('configuration_pipeline', 'ConfigurationPipeline')
    PreFlightValidator = import_from_core('preflight_validator', 'PreFlightValidator')
    # Import Phase 3 components
    BatchProcessingRecovery = import_from_core('recovery_system', 'BatchProcessingRecovery')
except ImportError:
    # Fallback for direct module loading
    import importlib.util
    
    def load_module(module_name, file_name):
        spec = importlib.util.spec_from_file_location(
            module_name, 
            os.path.join(os.path.dirname(__file__), f"{file_name}.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    # Load all components
    atomic_writer_module = load_module("atomic_writer", "atomic_writer")
    AtomicJSONLWriter = atomic_writer_module.AtomicJSONLWriter
    
    robust_checkpoint_module = load_module("robust_checkpoint", "robust_checkpoint")
    RobustCheckpointManager = robust_checkpoint_module.RobustCheckpointManager
    
    synchronized_progress_module = load_module("synchronized_progress", "synchronized_progress")
    SynchronizedProgressTracker = synchronized_progress_module.SynchronizedProgressTracker
    
    config_pipeline_module = load_module("configuration_pipeline", "configuration_pipeline")
    ConfigurationPipeline = config_pipeline_module.ConfigurationPipeline
    
    preflight_validator_module = load_module("preflight_validator", "preflight_validator")
    PreFlightValidator = preflight_validator_module.PreFlightValidator
    
    recovery_system_module = load_module("recovery_system", "recovery_system")
    BatchProcessingRecovery = recovery_system_module.BatchProcessingRecovery


@dataclass
class ComponentConfiguration:
    """Configuration for component creation"""
    output_dir: str
    prompt_version: str = 'v6'
    batch_size: int = 50
    backup_enabled: bool = True
    checkpoint_interval: int = 100
    enable_recovery: bool = True


class ComponentFactory:
    """Factory for creating and managing batch processing components"""
    
    def __init__(self):
        self._component_cache = {}
        self._config_cache = {}
    
    def create_atomic_writer(self, config: ComponentConfiguration) -> AtomicJSONLWriter:
        """Create atomic JSONL writer"""
        cache_key = f"atomic_writer_{config.output_dir}_{config.backup_enabled}"
        
        if cache_key not in self._component_cache:
            self._component_cache[cache_key] = AtomicJSONLWriter(
                file_path=os.path.join(config.output_dir, 'results.jsonl'),
                backup_enabled=config.backup_enabled
            )
        
        return self._component_cache[cache_key]
    
    def create_checkpoint_manager(self, config: ComponentConfiguration) -> RobustCheckpointManager:
        """Create robust checkpoint manager"""
        cache_key = f"checkpoint_manager_{config.output_dir}_{config.checkpoint_interval}"
        
        if cache_key not in self._component_cache:
            self._component_cache[cache_key] = RobustCheckpointManager(
                output_dir=config.output_dir,
                checkpoint_interval=config.checkpoint_interval
            )
        
        return self._component_cache[cache_key]
    
    def create_progress_tracker(self, config: ComponentConfiguration, total_count: int) -> SynchronizedProgressTracker:
        """Create synchronized progress tracker"""
        # Progress tracker is not cached since it depends on total_count
        return SynchronizedProgressTracker(
            total_count=total_count,
            output_dir=config.output_dir
        )
    
    def create_configuration_pipeline(self, config: ComponentConfiguration) -> Any:
        """Create configuration pipeline with caching"""
        cache_key = f"config_{config.prompt_version}"
        
        if cache_key not in self._config_cache:
            self._config_cache[cache_key] = ConfigurationPipeline.get_config_for_version(config.prompt_version)
        
        return self._config_cache[cache_key]
    
    def create_preflight_validator(self, config: ComponentConfiguration) -> PreFlightValidator:
        """Create preflight validator"""
        cache_key = f"preflight_validator_{config.prompt_version}_{config.output_dir}"
        
        if cache_key not in self._component_cache:
            self._component_cache[cache_key] = PreFlightValidator(
                prompt_version=config.prompt_version,
                output_dir=config.output_dir
            )
        
        return self._component_cache[cache_key]
    
    def create_recovery_system(self, config: ComponentConfiguration) -> Optional[BatchProcessingRecovery]:
        """Create recovery system if enabled"""
        if not config.enable_recovery:
            return None
        
        cache_key = f"recovery_system_{config.output_dir}"
        
        if cache_key not in self._component_cache:
            self._component_cache[cache_key] = BatchProcessingRecovery(config.output_dir)
        
        return self._component_cache[cache_key]
    
    def create_component_bundle(self, config: ComponentConfiguration, total_count: Optional[int] = None) -> Dict[str, Any]:
        """Create a complete bundle of components"""
        bundle = {
            'atomic_writer': self.create_atomic_writer(config),
            'checkpoint_manager': self.create_checkpoint_manager(config),
            'configuration': self.create_configuration_pipeline(config),
            'preflight_validator': self.create_preflight_validator(config),
            'recovery_system': self.create_recovery_system(config)
        }
        
        # Add progress tracker if total count is provided
        if total_count is not None:
            bundle['progress_tracker'] = self.create_progress_tracker(config, total_count)
        
        return bundle
    
    def clear_cache(self):
        """Clear component cache (useful for testing)"""
        self._component_cache.clear()
        self._config_cache.clear()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information for monitoring"""
        return {
            'component_cache_size': len(self._component_cache),
            'config_cache_size': len(self._config_cache),
            'cached_components': list(self._component_cache.keys()),
            'cached_configs': list(self._config_cache.keys())
        }


# Global factory instance for reuse
_global_factory = None

def get_component_factory() -> ComponentFactory:
    """Get global component factory instance"""
    global _global_factory
    if _global_factory is None:
        _global_factory = ComponentFactory()
    return _global_factory


def create_batch_processing_components(output_dir: str, prompt_version: str = 'v6', 
                                     batch_size: int = 50, total_count: Optional[int] = None,
                                     **kwargs) -> Dict[str, Any]:
    """Convenience function for creating batch processing components"""
    factory = get_component_factory()
    config = ComponentConfiguration(
        output_dir=output_dir,
        prompt_version=prompt_version,
        batch_size=batch_size,
        **kwargs
    )
    return factory.create_component_bundle(config, total_count)