#!/usr/bin/env python3
"""
Test runner for Blog Post Slug Generator
Runs all tests and provides coverage information
"""

import unittest
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def run_all_tests():
    """Discover and run all tests"""
    # Discover tests from the tests directory
    loader = unittest.TestLoader()
    start_dir = os.path.join(project_root, 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success/failure
    return result.wasSuccessful()

def run_specific_test(test_name):
    """Run a specific test module or test case"""
    try:
        # Try to load specific test
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(test_name)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
    except Exception as e:
        print(f"Error running test '{test_name}': {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Blog Post Slug Generator - Test Suite")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        print(f"Running specific test: {test_name}")
        success = run_specific_test(test_name)
    else:
        # Run all tests
        print("Running all tests...")
        success = run_all_tests()
    
    print("=" * 60)
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)