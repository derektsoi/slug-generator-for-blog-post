"""
Base CLI Framework for Evaluation Tools

Shared functionality for all evaluation CLI scripts to eliminate code duplication
and provide consistent user experience across tools.
"""

import argparse
import json
import logging
import os
import sys
import traceback
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add src to path for imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


class CLIError(Exception):
    """Custom exception for CLI errors with exit codes"""
    def __init__(self, message: str, exit_code: int = 1):
        self.message = message
        self.exit_code = exit_code
        super().__init__(message)


class BaseCLI(ABC):
    """Base class for evaluation CLI tools"""
    
    def __init__(self, tool_name: str, description: str):
        self.tool_name = tool_name
        self.description = description
        self.verbose = False
        self.api_key = None
        self.logger = None
        
    def validate_api_key(self) -> str:
        """Validate and get API key from environment"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise CLIError(
                "Error: OPENAI_API_KEY environment variable is required.\n"
                "Please set your OpenAI API key:\n"
                "export OPENAI_API_KEY='your-api-key-here'"
            )
        return api_key
    
    def setup_logging(self, level: str = 'INFO') -> None:
        """Setup logging configuration"""
        log_level = getattr(logging, level.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(self.tool_name)
    
    def log_error(self, message: str, exception: Exception = None) -> None:
        """Log error with optional exception details"""
        if self.logger:
            self.logger.error(message)
            if exception and self.verbose:
                self.logger.error(f"Exception details: {str(exception)}")
                self.logger.debug(traceback.format_exc())
        elif self.verbose:
            print(f"ERROR: {message}")
            if exception:
                print(f"Exception: {str(exception)}")
    
    def log_warning(self, message: str) -> None:
        """Log warning message"""
        if self.logger:
            self.logger.warning(message)
        elif self.verbose:
            print(f"WARNING: {message}")
    
    def log_info(self, message: str) -> None:
        """Log info message"""
        if self.logger:
            self.logger.info(message)
        elif self.verbose:
            print(f"INFO: {message}")
    
    def handle_api_error(self, exception: Exception, context: str = "API operation") -> CLIError:
        """Handle API-related errors with context"""
        error_message = f"Failed during {context}: {str(exception)}"
        self.log_error(error_message, exception)
        
        # Provide helpful suggestions based on error type
        if "authentication" in str(exception).lower() or "api key" in str(exception).lower():
            error_message += "\nPlease check your OPENAI_API_KEY environment variable."
        elif "rate limit" in str(exception).lower():
            error_message += "\nRate limit exceeded. Please wait before retrying."
        elif "timeout" in str(exception).lower():
            error_message += "\nRequest timed out. Please check your internet connection and try again."
        
        return CLIError(error_message)
    
    def handle_validation_error(self, exception: Exception, context: str = "validation") -> CLIError:
        """Handle validation errors with context"""
        error_message = f"Validation failed during {context}: {str(exception)}"
        self.log_error(error_message, exception)
        return CLIError(error_message)
    
    def safe_execute(self, operation_name: str, operation_func, *args, **kwargs) -> Any:
        """Safely execute an operation with error handling"""
        try:
            self.log_info(f"Starting {operation_name}")
            result = operation_func(*args, **kwargs)
            self.log_info(f"Completed {operation_name} successfully")
            return result
        except Exception as e:
            self.log_error(f"Failed during {operation_name}", e)
            raise self.handle_api_error(e, operation_name)
    
    def setup_imports(self):
        """Setup imports with error handling"""
        try:
            from config.evaluation_prompt_manager import EvaluationPromptManager
            from config.constants import DEFAULT_SCORING_DIMENSIONS
            from evaluation.core.seo_evaluator import SEOEvaluator
            
            # Store as instance variables for subclass access
            self.EvaluationPromptManager = EvaluationPromptManager
            self.DEFAULT_SCORING_DIMENSIONS = DEFAULT_SCORING_DIMENSIONS  
            self.SEOEvaluator = SEOEvaluator
            
        except ImportError as e:
            raise CLIError(
                f"Error: Failed to import required modules: {e}\n"
                "Please ensure you're running from the project root directory."
            )
    
    @abstractmethod
    def setup_parser(self) -> argparse.ArgumentParser:
        """Setup argument parser - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def run_command(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Execute the main command logic - must be implemented by subclasses"""
        pass
    
    def save_results(self, results: Dict[str, Any], output_file: str) -> bool:
        """Save results to JSON file with consistent format"""
        try:
            output_data = {
                **results,
                'tool': self.tool_name,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            if self.verbose:
                print(f"Results saved to: {output_file}")
            
            return True
        except Exception as e:
            raise CLIError(f"Error: Failed to save results to {output_file}: {e}")
    
    def validate_sample_size(self, sample_size: int, max_recommended: int = 20) -> bool:
        """Validate sample size with user confirmation for large sizes"""
        if sample_size <= 0:
            raise CLIError("Error: Sample size must be greater than 0.")
        
        if sample_size > max_recommended:
            print(f"Warning: Large sample sizes may take significant time and API credits.")
            response = input("Continue? (y/N): ").lower()
            if response != 'y':
                print("Cancelled.")
                return False
        return True
    
    def run(self) -> None:
        """Main entry point for CLI execution"""
        try:
            # Setup argument parser first (for verbose flag detection)
            parser = self.setup_parser()
            args = parser.parse_args()
            
            # Store verbose flag early
            self.verbose = getattr(args, 'verbose', False)
            
            # Setup logging if verbose
            if self.verbose:
                self.setup_logging('DEBUG')
            
            # Setup imports
            self.setup_imports()
            
            # Validate API key
            self.api_key = self.validate_api_key()
            
            # Run the command with safe execution
            results = self.safe_execute("main command execution", self.run_command, args)
            
            # Save results if requested
            if hasattr(args, 'output') and args.output:
                self.safe_execute("results saving", self.save_results, results, args.output)
            
        except CLIError as e:
            print(e.message)
            self.log_error(f"CLI error: {e.message}")
            sys.exit(e.exit_code)
        except KeyboardInterrupt:
            print(f"\n{self.tool_name} cancelled by user.")
            self.log_info("Tool cancelled by user")
            sys.exit(130)
        except Exception as e:
            error_msg = f"Error: {self.tool_name} failed with unexpected error: {e}"
            print(error_msg)
            self.log_error("Unexpected error", e)
            if self.verbose:
                print("\nFull traceback:")
                traceback.print_exc()
            sys.exit(1)


class TestDataMixin:
    """Mixin providing standard test cases for evaluation tools"""
    
    @property
    def standard_test_cases(self) -> List[Dict[str, str]]:
        """Standard test cases for consistent testing across tools"""
        return [
            {
                "slug": "ultimate-ichiban-kuji-guide", 
                "title": "一番賞完全購入指南",
                "content": "Complete guide to ichiban-kuji purchasing and collecting rare anime merchandise"
            },
            {
                "slug": "skinniydip-iface-rhinoshield-comparison",
                "title": "日韓台7大手機殼品牌推介，SKINNIYDIP/iface/犀牛盾iPhone16/Pro手機殼登場！",
                "content": "Comprehensive comparison of top phone case brands including SKINNIYDIP, iface, and RhinoShield"
            },
            {
                "slug": "daikoku-drugstore-shopping-guide", 
                "title": "大國藥妝購物完全攻略",
                "content": "Complete Daikoku drugstore shopping guide for tourists and locals"
            },
            {
                "slug": "rakuten-official-store-benefits",
                "title": "樂天官網購物教學與優惠攻略",
                "content": "Guide to Rakuten official store shopping benefits and discount strategies"
            },
            {
                "slug": "gap-jojo-maman-bebe-kids-fashion", 
                "title": "GAP vs JoJo Maman Bébé童裝比較",
                "content": "Detailed comparison of GAP and JoJo Maman Bébé children's fashion collections"
            },
            {
                "slug": "jk-uniform-authentic-shopping-guide",
                "title": "正版JK制服購買指南與假貨辨別",
                "content": "Authentic JK uniform shopping guide with counterfeit identification tips"
            },
            {
                "slug": "asian-beauty-skincare-routine",
                "title": "亞洲美妝護膚步驟完整教學",
                "content": "Complete Asian beauty skincare routine guide with product recommendations"
            },
            {
                "slug": "cross-border-shipping-consolidation-guide",
                "title": "跨境購物集運教學與費用比較",
                "content": "Cross-border shopping consolidation service guide and cost comparison"
            }
        ]
    
    def get_test_subset(self, sample_size: int) -> List[Dict[str, str]]:
        """Get subset of test cases for specified sample size"""
        test_cases = self.standard_test_cases
        if sample_size <= len(test_cases):
            return test_cases[:sample_size]
        else:
            # If more samples requested than available, cycle through the list
            extended_cases = []
            for i in range(sample_size):
                extended_cases.append(test_cases[i % len(test_cases)])
            return extended_cases


class PromptValidationMixin:
    """Mixin providing prompt validation functionality"""
    
    def validate_prompt_version(self, version: str, manager) -> bool:
        """Validate that evaluation prompt version exists"""
        try:
            available_versions = manager.list_available_versions()
            if version not in available_versions:
                raise CLIError(
                    f"Error: Evaluation prompt version '{version}' not found.\n"
                    f"Available versions: {', '.join(sorted(available_versions))}"
                )
            return True
        except Exception as e:
            raise CLIError(f"Error: Failed to validate prompt version: {e}")
    
    def validate_prompt_versions(self, version_a: str, version_b: str, manager) -> bool:
        """Validate both evaluation prompt versions exist"""
        try:
            available_versions = manager.list_available_versions()
            
            missing_versions = []
            if version_a not in available_versions:
                missing_versions.append(version_a)
            if version_b not in available_versions:
                missing_versions.append(version_b)
            
            if missing_versions:
                raise CLIError(
                    f"Error: Evaluation prompt version(s) not found: {', '.join(missing_versions)}\n"
                    f"Available versions: {', '.join(sorted(available_versions))}"
                )
            
            # Check for identical versions
            if version_a == version_b:
                print("Warning: Comparing identical evaluation prompt versions.")
                print("Results will show no differences between versions.")
                
            return True
        except Exception as e:
            raise CLIError(f"Error: Failed to validate prompt versions: {e}")


class ProgressTrackingMixin:
    """Mixin providing progress tracking utilities"""
    
    def create_progress_tracker(self, total_items: int, description: str = "Processing") -> 'ProgressTracker':
        """Create a simple progress tracker"""
        return ProgressTracker(total_items, description, verbose=getattr(self, 'verbose', False))


class ProgressTracker:
    """Simple progress tracker for CLI operations"""
    
    def __init__(self, total: int, description: str = "Processing", verbose: bool = False):
        self.total = total
        self.current = 0
        self.description = description
        self.verbose = verbose
        
    def update(self, increment: int = 1, message: str = None) -> None:
        """Update progress"""
        self.current += increment
        if self.verbose:
            progress_msg = f"{self.description}: {self.current}/{self.total}"
            if message:
                progress_msg += f" - {message}"
            print(progress_msg)
    
    def complete(self, message: str = None) -> None:
        """Mark progress as complete"""
        self.current = self.total
        if self.verbose:
            complete_msg = f"{self.description} completed"
            if message:
                complete_msg += f" - {message}"
            print(complete_msg)


class OutputFormattingMixin:
    """Mixin providing consistent output formatting across tools"""
    
    def format_score_display(self, score: float, precision: int = 3) -> str:
        """Format score for consistent display"""
        return f"{score:.{precision}f}"
    
    def format_dimension_name(self, dimension: str) -> str:
        """Format dimension name for display"""
        return dimension.replace('_', ' ').title()
    
    def print_section_header(self, title: str, width: int = 60) -> None:
        """Print formatted section header"""
        print(f"{title}")
        print("=" * width)
    
    def print_subsection_header(self, title: str) -> None:
        """Print formatted subsection header"""
        print(f"\n{title}:")
    
    def print_score_line(self, label: str, score: float, symbol: str = "•") -> None:
        """Print formatted score line"""
        formatted_score = self.format_score_display(score)
        print(f"{symbol} {label}: {formatted_score}")
    
    def print_status_line(self, label: str, status: bool, true_symbol: str = "✓", false_symbol: str = "✗") -> None:
        """Print formatted status line"""
        symbol = true_symbol if status else false_symbol
        print(f"  {symbol} {label}")
    
    def print_bullet_list(self, items: List[str], symbol: str = "•") -> None:
        """Print formatted bullet list"""
        for item in items:
            print(f"{symbol} {item}")


# Utility functions for common CLI operations
def setup_common_args(parser: argparse.ArgumentParser) -> None:
    """Add common arguments to parser"""
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Save results to JSON file'
    )


def add_sample_size_arg(parser: argparse.ArgumentParser, default: int = 5) -> None:
    """Add sample size argument with common validation"""
    parser.add_argument(
        '--sample-size',
        type=int,
        default=default,
        help=f'Number of test cases to evaluate (default: {default})'
    )