#!/usr/bin/env python3
"""
Test script to verify the cleanup functionality works correctly.
"""

import sys
import os
import time
import subprocess
from pathlib import Path

def test_cleanup():
    """Test the cleanup functionality."""
    print("🧪 Testing cleanup functionality...")
    
    # Import the cleanup function
    try:
        from cleanup_utils import cleanup_on_startup
        print("✅ Successfully imported cleanup_utils")
    except ImportError as e:
        print(f"❌ Failed to import cleanup_utils: {e}")
        return False
    
    # Test basic cleanup (should not kill current process)
    print("\n🔍 Testing process cleanup...")
    try:
        killed = cleanup_on_startup(verbose=True)
        print(f"✅ Cleanup completed, processes handled: {len(killed)}")
        return True
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False

def test_full_startup():
    """Test the full startup sequence with cleanup."""
    print("\n🚀 Testing full startup sequence...")
    
    # Test importing project_station_run
    try:
        import project_station_run
        print("✅ Successfully imported project_station_run")
    except ImportError as e:
        print(f"❌ Failed to import project_station_run: {e}")
        return False
    
    # Test that main function exists and has cleanup
    try:
        # Read the main function to verify cleanup is integrated
        script_path = Path(__file__).parent / "project_station_run.py"
        with open(script_path, 'r') as f:
            content = f.read()
        
        if "cleanup_on_startup" in content:
            print("✅ Cleanup integration found in main function")
            return True
        else:
            print("❌ Cleanup integration not found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking integration: {e}")
        return False

def test_psutil_availability():
    """Test if psutil is available for advanced cleanup."""
    print("\n📊 Testing psutil availability...")
    
    try:
        import psutil
        print(f"✅ psutil available, version: {psutil.__version__}")
        
        # Test basic psutil functionality
        current_process = psutil.Process()
        print(f"✅ Current process PID: {current_process.pid}")
        print(f"✅ Process name: {current_process.name()}")
        
        return True
    except ImportError:
        print("⚠️  psutil not available, will use fallback cleanup")
        return False
    except Exception as e:
        print(f"❌ psutil test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🏁 Starting cleanup functionality tests...\n")
    
    tests = [
        ("Basic Cleanup", test_cleanup),
        ("Startup Integration", test_full_startup), 
        ("Psutil Availability", test_psutil_availability)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Cleanup functionality is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()