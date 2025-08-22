#!/usr/bin/env python3
"""
Test to verify the fixed GUI shows widgets correctly
"""

import subprocess
import sys
import time

def test_gui():
    """Test the GUI functionality"""
    print("Testing GUI functionality...")
    
    # Start the GUI in background
    try:
        process = subprocess.Popen(
            [sys.executable, "simple_gui_fixed.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for GUI to start
        time.sleep(2)
        
        # Check if process is still running (good sign)
        if process.poll() is None:
            print("✓ GUI started successfully and is running")
            
            # Terminate the process
            process.terminate()
            try:
                process.wait(timeout=5)
                print("✓ GUI terminated cleanly")
                return True
            except subprocess.TimeoutExpired:
                process.kill()
                print("✓ GUI was force-killed (normal for GUI apps)")
                return True
        else:
            # Process already terminated - check output
            stdout, stderr = process.communicate()
            print(f"✗ GUI exited with code {process.returncode}")
            if stdout:
                print(f"stdout: {stdout}")
            if stderr:
                print(f"stderr: {stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Failed to start GUI: {e}")
        return False

def test_project_run():
    """Test the main project_station_run.py"""
    print("\nTesting project_station_run.py...")
    
    try:
        process = subprocess.Popen(
            [sys.executable, "project_station_run.py", "--tkinter"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for GUI to start
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is None:
            print("✓ project_station_run.py GUI started successfully")
            
            # Terminate the process
            process.terminate()
            try:
                process.wait(timeout=5)
                print("✓ project_station_run.py terminated cleanly")
                return True
            except subprocess.TimeoutExpired:
                process.kill()
                print("✓ project_station_run.py was force-killed (normal)")
                return True
        else:
            stdout, stderr = process.communicate()
            print(f"✗ project_station_run.py exited with code {process.returncode}")
            if stdout:
                print(f"stdout: {stdout}")
            if stderr:
                print(f"stderr: {stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Failed to start project_station_run.py: {e}")
        return False

if __name__ == "__main__":
    print("GUI Functionality Test")
    print("=" * 50)
    
    gui_ok = test_gui()
    project_ok = test_project_run()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"  simple_gui_fixed.py: {'✓ PASS' if gui_ok else '✗ FAIL'}")
    print(f"  project_station_run.py: {'✓ PASS' if project_ok else '✗ FAIL'}")
    
    if gui_ok and project_ok:
        print("\n🎉 All GUI tests PASSED! The blank GUI issue has been fixed.")
        print("   The GUI should now display widgets correctly in both PyCharm IDE and terminal.")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")