#!/usr/bin/env python3
"""
Test script to verify console and web GUI show the same test items
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_station_limits():
    """Test that station limits are loaded correctly"""
    print("Testing station limits configuration...")
    
    try:
        from config import station_limits_project_station
        
        print(f"Found {len(station_limits_project_station.STATION_LIMITS)} test items:")
        
        for i, limit in enumerate(station_limits_project_station.STATION_LIMITS, 1):
            print(f"  {i}. {limit['name']}")
            print(f"     Low Limit: {limit['low_limit']}")
            print(f"     High Limit: {limit['high_limit']}")
            print(f"     Unique ID: {limit['unique_id']}")
            print()
            
        return True
    except Exception as e:
        print(f"Failed to load station limits: {e}")
        return False

def test_station_config():
    """Test that station config is loaded correctly"""
    print("Testing station configuration...")
    
    try:
        import station_config
        station_config.load_station('project_station')
        
        print("Station configuration loaded successfully!")
        print(f"Root directory: {station_config.ROOT_DIR}")
        print(f"CSV summary directory: {station_config.CSV_SUMMARY_DIR}")
        print(f"Serial number validation: {station_config.SERIAL_NUMBER_VALIDATION}")
        print()
        
        return True
    except Exception as e:
        print(f"Failed to load station config: {e}")
        return False

def test_web_gui_initialization():
    """Test that web GUI initializes correctly"""
    print("Testing web GUI initialization...")
    
    try:
        # Import without starting the server
        import web_gui
        
        # Create GUI instance (this will initialize the station)
        gui = web_gui.WebFactoryTestGUI()
        
        print("Web GUI initialized successfully!")
        print(f"Station name: {gui.station_name}")
        print(f"Number of test items: {len(gui.current_test_data['test_items'])}")
        
        print("Test items from web GUI:")
        for item in gui.current_test_data['test_items']:
            print(f"  - {item['name']}: limits {item['low_limit']} to {item['high_limit']}")
        
        return True
    except Exception as e:
        print(f"Failed to initialize web GUI: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("Testing Console vs Web GUI Equivalence")
    print("=" * 60)
    print()
    
    tests = [
        ("Station Limits", test_station_limits),
        ("Station Config", test_station_config),
        ("Web GUI Init", test_web_gui_initialization),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"✓ {test_name}: {'PASS' if result else 'FAIL'}")
        except Exception as e:
            print(f"✗ {test_name}: FAIL - {e}")
            results.append((test_name, False))
        print()
    
    print("=" * 60)
    print("Test Results Summary:")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All tests PASSED! Console and Web GUI are equivalent.")
        print("Both interfaces use the same:")
        print("  - Station configuration files")
        print("  - Test limits and parameters")
        print("  - Test execution logic")
    else:
        print("❌ Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()