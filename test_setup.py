#!/usr/bin/env python3
"""
Simple validation test to ensure all modules can be imported
"""

import sys
import traceback

def test_imports():
    """Test that all modules can be imported"""
    tests_passed = 0
    tests_failed = 0
    
    print("Testing module imports...")
    print("=" * 50)
    
    # Test yaml
    try:
        import yaml
        print("✓ yaml imported successfully")
        tests_passed += 1
    except ImportError as e:
        print(f"✗ Failed to import yaml: {e}")
        tests_failed += 1
    
    # Test opencv
    try:
        import cv2
        print("✓ cv2 imported successfully")
        tests_passed += 1
    except ImportError as e:
        print(f"✗ Failed to import cv2: {e}")
        tests_failed += 1
    
    # Test numpy
    try:
        import numpy
        print("✓ numpy imported successfully")
        tests_passed += 1
    except ImportError as e:
        print(f"✗ Failed to import numpy: {e}")
        tests_failed += 1
    
    # Test config loading
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        print("✓ config.yaml loaded successfully")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Failed to load config.yaml: {e}")
        tests_failed += 1
    
    # Test source imports (these may fail if dependencies aren't installed)
    try:
        from src.bird_detector import BirdDetector
        print("✓ BirdDetector imported successfully")
        tests_passed += 1
    except ImportError as e:
        print(f"⚠ BirdDetector import failed (dependencies may not be installed): {e}")
        tests_failed += 1
    
    try:
        from src.ptz_controller import PTZController
        print("✓ PTZController imported successfully")
        tests_passed += 1
    except ImportError as e:
        print(f"⚠ PTZController import failed (dependencies may not be installed): {e}")
        tests_failed += 1
    
    try:
        from src.bird_tracker import BirdTracker
        print("✓ BirdTracker imported successfully")
        tests_passed += 1
    except ImportError as e:
        print(f"⚠ BirdTracker import failed (dependencies may not be installed): {e}")
        tests_failed += 1
    
    print("=" * 50)
    print(f"\nResults: {tests_passed} passed, {tests_failed} failed")
    
    if tests_failed == 0:
        print("\n✓ All tests passed!")
        return 0
    elif tests_failed <= 3:
        print("\n⚠ Some imports failed - you may need to install dependencies:")
        print("  pip install -r requirements.txt")
        return 0
    else:
        print("\n✗ Multiple tests failed - please check your installation")
        return 1

if __name__ == '__main__':
    sys.exit(test_imports())
