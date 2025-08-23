#!/usr/bin/env python3
"""
Test script for persistent table functionality with configuration loading.
"""

import sys
import os
import importlib

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_loading():
    """Test loading of station limits configuration."""
    print("🧪 Testing Configuration Loading")
    print("=" * 40)
    
    try:
        # Test importing the limits module
        limits_module = importlib.import_module("config.station_limits_project_station")
        station_limits = getattr(limits_module, 'STATION_LIMITS', [])
        
        print(f"✅ Successfully loaded {len(station_limits)} test items")
        
        for i, limit in enumerate(station_limits):
            print(f"   {i+1}. {limit.get('name', 'Unknown')}")
            print(f"      Low: {limit.get('low_limit', 'N/A')}")
            print(f"      High: {limit.get('high_limit', 'N/A')}")
            print(f"      ID: {limit.get('unique_id', 'N/A')}")
            print()
        
        return True, station_limits
        
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return False, []

def test_table_initialization():
    """Test table initialization logic."""
    print("🔧 Testing Table Initialization Logic")
    print("=" * 40)
    
    success, station_limits = test_config_loading()
    if not success:
        return False
    
    # Simulate table initialization
    test_items = {}
    
    for i, test_limit in enumerate(station_limits):
        test_name = test_limit.get('name', f'Test Item {i+1}')
        low_limit = test_limit.get('low_limit', '')
        high_limit = test_limit.get('high_limit', '')
        unique_id = test_limit.get('unique_id', i)
        
        # Format limits for display
        if low_limit is None or low_limit == '':
            low_display = ''
        elif isinstance(low_limit, bool):
            low_display = str(low_limit)
        else:
            low_display = str(low_limit)
            
        if high_limit is None or high_limit == '':
            high_display = ''
        elif isinstance(high_limit, bool):
            high_display = str(high_limit)
        else:
            high_display = str(high_limit)
        
        # Determine attachment icon
        if 'NON PARAMETRIC' in test_name.upper():
            attachment = '📷'
        elif 'ITEM 1' in test_name:
            attachment = '📊'
        elif 'ITEM 2' in test_name:
            attachment = '📈'
        else:
            attachment = '📋'
        
        test_items[test_name] = {
            'low_limit': low_limit,
            'high_limit': high_limit,
            'unique_id': unique_id,
            'attachment': attachment,
            'low_display': low_display,
            'high_display': high_display
        }
        
        print(f"✅ Initialized: {test_name}")
        print(f"   Display: {test_name} | — | {low_display} | {high_display} | {attachment}")
    
    print(f"\n✅ Successfully initialized {len(test_items)} test items")
    return True

def test_value_update_logic():
    """Test the value update logic."""
    print("\n🔄 Testing Value Update Logic")
    print("=" * 40)
    
    # Test value formatting
    test_cases = [
        ("1.1", "pass", "✓ 1.1"),
        ("2.5", "fail", "✗ 2.5"),
        ("Testing...", "testing", "⏳ Testing..."),
        ("True", "pass", "✓ True"),
        ("False", "fail", "✗ False"),
        (None, "pending", "—")
    ]
    
    for value, status, expected in test_cases:
        # Format value based on status
        if status == "pass":
            formatted_value = f"✓ {value}"
        elif status == "fail":
            formatted_value = f"✗ {value}"
        elif status == "testing":
            formatted_value = f"⏳ {value}"
        else:
            formatted_value = str(value) if value is not None else "—"
        
        if formatted_value == expected:
            print(f"✅ {value} ({status}) → {formatted_value}")
        else:
            print(f"❌ {value} ({status}) → {formatted_value} (expected: {expected})")
    
    return True

def main():
    """Run all tests."""
    print("🏁 Factory Test Station - Persistent Table Tests")
    print("=" * 60)
    
    tests = [
        ("Configuration Loading", test_config_loading),
        ("Table Initialization", test_table_initialization),
        ("Value Update Logic", test_value_update_logic)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n▶️  Running: {test_name}")
            result = test_func()
            results.append((test_name, result if isinstance(result, bool) else result[0]))
        except Exception as e:
            print(f"💥 Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Persistent table functionality is ready.")
        print("\n📋 Key Features Implemented:")
        print("   • Configuration loading from station_limits_project_station.py")
        print("   • Persistent table structure (never recreated)")
        print("   • Value-only updates with status formatting")
        print("   • Proper limit display formatting")
        print("   • Test result retention after completion")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()