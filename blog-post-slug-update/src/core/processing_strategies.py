#!/usr/bin/env python3
"""
Processing Strategies - Strategy pattern for different batch processing modes
Refactored from RefactoredBatchProcessor to support multiple processing strategies.
"""

import time
import threading
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

# Import basic components directly without circular dependencies
try:
    from .error_patterns import ErrorContext
except ImportError:
    # Fallback for direct module loading
    import importlib.util
    import os
    
    spec = importlib.util.spec_from_file_location(
        "error_patterns", 
        os.path.join(os.path.dirname(__file__), "error_patterns.py")
    )
    error_patterns_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(error_patterns_module)
    ErrorContext = error_patterns_module.ErrorContext

# Define ProcessingResult locally to avoid circular import
@dataclass
class ProcessingResult:
    """Local processing result to avoid circular imports"""
    success: bool
    processed_count: int = 0
    success_count: int = 0
    failed_count: int = 0
    total_cost: float = 0.0
    processing_duration: float = 0.0
    resumed_from_checkpoint: bool = False
    recovery_attempted: bool = False
    error_classifications: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics"""
        metrics = {}
        
        if self.processed_count > 0:
            metrics['success_rate'] = self.success_count / self.processed_count
            metrics['avg_time_per_url'] = self.processing_duration / self.processed_count
            metrics['avg_cost_per_url'] = self.total_cost / self.processed_count
        else:
            metrics['success_rate'] = 0.0
            metrics['avg_time_per_url'] = 0.0
            metrics['avg_cost_per_url'] = 0.0
        
        # Cost efficiency: successful URLs per dollar
        if self.total_cost > 0:
            metrics['cost_efficiency'] = self.success_count / self.total_cost
        else:
            metrics['cost_efficiency'] = float('inf') if self.success_count > 0 else 0.0
        
        return metrics
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize result for logging"""
        result_dict = {
            'success': self.success,
            'processed_count': self.processed_count,
            'success_count': self.success_count,
            'failed_count': self.failed_count,
            'total_cost': self.total_cost,
            'processing_duration': self.processing_duration,
            'resumed_from_checkpoint': self.resumed_from_checkpoint,
            'recovery_attempted': self.recovery_attempted,
            'error_classifications': self.error_classifications,
            'timestamp': self.timestamp,
            'performance_metrics': self.get_performance_metrics()
        }
        return result_dict


@dataclass
class ProcessingContext:
    """Context for processing strategies"""
    components: Dict[str, Any]
    configuration: Any
    output_dir: str
    processing_lock: threading.Lock
    checkpoint_interval: int = 10
    progress_update_interval: int = 5
    enable_recovery: bool = True


class ProcessingStrategy(ABC):
    """Abstract base class for processing strategies"""
    
    def __init__(self, context: ProcessingContext):
        self.context = context
        self.components = context.components
        self.config = context.configuration
    
    @abstractmethod
    def process_urls(self, urls: List[Dict[str, str]], resume: bool = False) -> ProcessingResult:
        """Process URLs using this strategy"""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get strategy name for logging"""
        pass
    
    def _create_base_result(self) -> ProcessingResult:
        """Create base processing result"""
        return ProcessingResult(success=False)
    
    def _classify_error(self, error: Exception, context: ErrorContext) -> str:
        """Classify processing error"""
        error_str = str(error).lower()
        
        if 'rate limit' in error_str:
            return 'API_RATE_LIMIT'
        elif 'timeout' in error_str:
            return 'API_TIMEOUT'
        elif 'connection' in error_str:
            return 'CONNECTION_ERROR'
        elif 'processing failure' in error_str:
            return 'PROCESSING_FAILURE'
        else:
            return 'UNKNOWN_ERROR'
    
    def _attempt_recovery(self, error: Exception) -> Dict[str, Any]:
        """Attempt recovery using recovery system"""
        if not self.context.enable_recovery or 'recovery_system' not in self.components:
            return {'attempted': False, 'success': False}
        
        try:
            recovery_system = self.components['recovery_system']
            recovery_context = ErrorContext(operation='batch_processing')
            
            # Create appropriate error type
            from .error_classification import BatchProcessingError
            batch_error = BatchProcessingError(
                str(error),
                'PROCESSING_FAILURE',
                context=recovery_context.to_dict()
            )
            
            recovery_result = recovery_system.attempt_resume_recovery(batch_error)
            
            return {
                'attempted': True,
                'success': recovery_result.get('success', False),
                'strategy': recovery_result.get('strategy', 'unknown')
            }
            
        except Exception:
            return {'attempted': True, 'success': False}


class StandardProcessingStrategy(ProcessingStrategy):
    """Standard sequential processing strategy"""
    
    def get_strategy_name(self) -> str:
        return "standard_sequential"
    
    def process_urls(self, urls: List[Dict[str, str]], resume: bool = False) -> ProcessingResult:
        """Process URLs sequentially"""
        start_time = time.time()
        result = self._create_base_result()
        
        try:
            with self.context.processing_lock:
                # Initialize progress tracker
                progress_tracker = self.components.get('progress_tracker')
                if progress_tracker is None and len(urls) > 0:
                    from .component_factory import get_component_factory, ComponentConfiguration
                    factory = get_component_factory()
                    config = ComponentConfiguration(output_dir=self.context.output_dir)
                    progress_tracker = factory.create_progress_tracker(config, len(urls))
                    self.components['progress_tracker'] = progress_tracker
                
                # Handle resume
                start_index = self._handle_resume(resume, result)
                
                # Process URLs
                for i, url_data in enumerate(urls[start_index:], start=start_index):
                    success = self._process_single_url(url_data, i, result)
                    
                    # Update progress
                    if progress_tracker:
                        progress_tracker.update_progress(success, i)
                    
                    # Checkpoint
                    if i % self.context.checkpoint_interval == 0:
                        self._save_checkpoint(i + 1, result.success_count, result.failed_count)
                    
                    result.processed_count += 1
                
                # Finalize
                self._finalize_processing(result)
                result.success = True
                result.processing_duration = time.time() - start_time
                
        except Exception as e:
            recovery_result = self._attempt_recovery(e)
            result.recovery_attempted = recovery_result.get('attempted', True)
            
            if not recovery_result.get('success', False):
                result.success = False
                result.error_classifications.append('CRITICAL_FAILURE')
        
        return result
    
    def _handle_resume(self, resume: bool, result: ProcessingResult) -> int:
        """Handle resume logic"""
        if not resume:
            return 0
        
        try:
            checkpoint_manager = self.components.get('checkpoint_manager')
            if checkpoint_manager:
                checkpoint_data = checkpoint_manager.load_checkpoint()
                if checkpoint_data and 'resume_index' in checkpoint_data:
                    result.resumed_from_checkpoint = True
                    return checkpoint_data['resume_index']
        except Exception:
            pass
        
        return 0
    
    def _process_single_url(self, url_data: Dict[str, str], index: int, result: ProcessingResult) -> bool:
        """Process a single URL"""
        try:
            # Mock slug generation - would be replaced with actual implementation
            slug_result = self._generate_slug(url_data)
            
            # Create result entry
            result_entry = {
                'title': url_data['title'],
                'url': url_data['url'],
                'slug': slug_result['primary'],
                'alternatives': slug_result.get('alternatives', []),
                'confidence': slug_result.get('confidence', 0.0),
                'timestamp': time.time()
            }
            
            # Write result atomically
            atomic_writer = self.components.get('atomic_writer')
            if atomic_writer:
                atomic_writer.write_entry(result_entry)
            
            result.success_count += 1
            return True
            
        except Exception as e:
            # Handle error
            error_context = ErrorContext(
                operation='url_processing',
                current_index=index,
                additional_data={'url': url_data.get('url', 'unknown')}
            )
            
            error_classification = self._classify_error(e, error_context)
            result.error_classifications.append(error_classification)
            
            # Attempt recovery for critical errors
            if 'processing failure' in str(e).lower():
                recovery_result = self._attempt_recovery(e)
                result.recovery_attempted = recovery_result.get('attempted', True)
            
            result.failed_count += 1
            return False
    
    def _save_checkpoint(self, processed_count: int, success_count: int, failed_count: int):
        """Save processing checkpoint"""
        checkpoint_manager = self.components.get('checkpoint_manager')
        if checkpoint_manager:
            checkpoint_data = {
                'version': 'refactored_v1',
                'resume_index': processed_count,
                'processed_count': processed_count,
                'success_count': success_count,
                'failed_count': failed_count,
                'timestamp': time.time(),
                'metadata': {
                    'strategy': self.get_strategy_name()
                }
            }
            checkpoint_manager.save_checkpoint(checkpoint_data)
    
    def _finalize_processing(self, result: ProcessingResult):
        """Finalize processing"""
        # Finalize atomic writer
        atomic_writer = self.components.get('atomic_writer')
        if atomic_writer:
            atomic_writer.finalize()
        
        # Final checkpoint
        self._save_checkpoint(
            result.processed_count,
            result.success_count,
            result.failed_count
        )
    
    def _generate_slug(self, url_data: Dict[str, str]) -> Dict[str, Any]:
        """Generate slug (mock implementation)"""
        return {
            'primary': 'optimized-generated-slug',
            'alternatives': ['alt-optimized-slug'],
            'confidence': 0.85
        }


class HighThroughputProcessingStrategy(StandardProcessingStrategy):
    """High throughput processing strategy with optimizations"""
    
    def get_strategy_name(self) -> str:
        return "high_throughput"
    
    def process_urls(self, urls: List[Dict[str, str]], resume: bool = False) -> ProcessingResult:
        """Process URLs with throughput optimizations"""
        # Reduce checkpoint frequency for higher throughput
        original_checkpoint_interval = self.context.checkpoint_interval
        self.context.checkpoint_interval = max(50, self.context.checkpoint_interval * 2)
        
        try:
            result = super().process_urls(urls, resume)
            result.metadata = {'optimized_for': 'throughput'}
            return result
        finally:
            self.context.checkpoint_interval = original_checkpoint_interval


class ReliabilityFocusedProcessingStrategy(StandardProcessingStrategy):
    """Reliability-focused processing strategy"""
    
    def get_strategy_name(self) -> str:
        return "reliability_focused"
    
    def process_urls(self, urls: List[Dict[str, str]], resume: bool = False) -> ProcessingResult:
        """Process URLs with reliability optimizations"""
        # Increase checkpoint frequency for better reliability
        original_checkpoint_interval = self.context.checkpoint_interval
        self.context.checkpoint_interval = min(5, self.context.checkpoint_interval)
        
        try:
            result = super().process_urls(urls, resume)
            result.metadata = {'optimized_for': 'reliability'}
            return result
        finally:
            self.context.checkpoint_interval = original_checkpoint_interval
    
    def _process_single_url(self, url_data: Dict[str, str], index: int, result: ProcessingResult) -> bool:
        """Process single URL with additional reliability measures"""
        # Add extra error handling for reliability
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                return super()._process_single_url(url_data, index, result)
            except Exception as e:
                if attempt == max_retries:
                    raise e
                time.sleep(0.1 * (attempt + 1))  # Brief retry delay
        return False


def get_processing_strategy(strategy_name: str, context: ProcessingContext) -> ProcessingStrategy:
    """Factory function for creating processing strategies"""
    strategies = {
        'standard': StandardProcessingStrategy,
        'high_throughput': HighThroughputProcessingStrategy,
        'reliability': ReliabilityFocusedProcessingStrategy
    }
    
    strategy_class = strategies.get(strategy_name, StandardProcessingStrategy)
    return strategy_class(context)