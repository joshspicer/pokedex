#!/usr/bin/env python3
"""
Simple test runner for the Pokédex application.

This script provides a convenient way to run all tests for the application.
"""

import unittest
import sys
import os

def run_tests():
    """Run all unit tests for the Pokédx application."""
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    
    # Load tests from the current directory
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success/failure status
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)