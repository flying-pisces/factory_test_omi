#!/usr/bin/env python3
"""
Cleanup utilities for factory test station startup.
Ensures clean initial state by killing previous Python processes.
"""

import os
import sys
import subprocess
import platform
import time
import psutil
from pathlib import Path

class ProcessCleanup:
    """Handles cleanup of previous Python processes on startup."""
    
    def __init__(self):
        self.system = platform.system()
        self.current_pid = os.getpid()
        self.script_dir = Path(__file__).parent
        
    def kill_factory_test_processes(self, verbose=True):
        """Kill all factory test related Python processes except current one."""
        killed_processes = []
        
        if verbose:
            print("🧹 Cleaning up previous Python processes...")
        
        try:
            # Get all running processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    # Skip current process
                    if proc.info['pid'] == self.current_pid:
                        continue
                        
                    # Check if it's a Python process
                    if not proc.info['name'] or 'python' not in proc.info['name'].lower():
                        continue
                        
                    # Check if it's running factory test related scripts
                    cmdline = proc.info['cmdline']
                    if not cmdline:
                        continue
                        
                    cmdline_str = ' '.join(cmdline).lower()
                    
                    # Keywords that identify factory test processes
                    factory_test_keywords = [
                        'project_station_run.py',
                        'factory_test',
                        'console_test_runner.py',
                        'simple_gui',
                        'web_gui.py',
                        'tkinter_gui',
                        'test_station'
                    ]
                    
                    # Check if this process is running factory test code
                    is_factory_test = any(keyword in cmdline_str for keyword in factory_test_keywords)
                    
                    # Also check if process is in our script directory
                    is_in_script_dir = any(str(self.script_dir) in arg for arg in cmdline if isinstance(arg, str))
                    
                    if is_factory_test or is_in_script_dir:
                        if verbose:
                            print(f"  Terminating PID {proc.info['pid']}: {' '.join(cmdline[:2])}")
                        
                        # Try graceful termination first
                        process = psutil.Process(proc.info['pid'])
                        process.terminate()
                        
                        # Wait a bit for graceful shutdown
                        try:
                            process.wait(timeout=2)
                        except psutil.TimeoutExpired:
                            # Force kill if graceful termination failed
                            if verbose:
                                print(f"    Force killing PID {proc.info['pid']}")
                            process.kill()
                        
                        killed_processes.append(proc.info['pid'])
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # Process might have already terminated or we don't have access
                    continue
                    
        except Exception as e:
            if verbose:
                print(f"Warning: Error during process cleanup: {e}")
        
        if verbose:
            if killed_processes:
                print(f"✅ Cleaned up {len(killed_processes)} processes: {killed_processes}")
            else:
                print("✅ No previous processes found to clean up")
                
        return killed_processes
    
    def kill_processes_by_name(self, process_names, verbose=True):
        """Kill processes by name (fallback method)."""
        killed_processes = []
        
        for name in process_names:
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['pid'] == self.current_pid:
                        continue
                        
                    if proc.info['name'] and name.lower() in proc.info['name'].lower():
                        if verbose:
                            print(f"  Killing {name} process PID {proc.info['pid']}")
                        
                        process = psutil.Process(proc.info['pid'])
                        process.terminate()
                        killed_processes.append(proc.info['pid'])
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return killed_processes
    
    def kill_processes_by_port(self, ports, verbose=True):
        """Kill processes using specific ports (useful for web interfaces)."""
        killed_processes = []
        
        for port in ports:
            try:
                for conn in psutil.net_connections():
                    if conn.laddr.port == port and conn.pid and conn.pid != self.current_pid:
                        if verbose:
                            print(f"  Killing process PID {conn.pid} using port {port}")
                        
                        process = psutil.Process(conn.pid)
                        process.terminate()
                        killed_processes.append(conn.pid)
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return killed_processes
    
    def comprehensive_cleanup(self, verbose=True):
        """Perform comprehensive cleanup of all factory test processes."""
        if verbose:
            print("🔄 Starting comprehensive factory test process cleanup...")
        
        total_killed = []
        
        # 1. Kill factory test specific processes
        killed = self.kill_factory_test_processes(verbose)
        total_killed.extend(killed)
        
        # 2. Kill processes using common factory test ports
        web_ports = [5000, 5001, 8000, 8080, 3000]  # Common Flask/web ports
        killed = self.kill_processes_by_port(web_ports, verbose)
        total_killed.extend(killed)
        
        # 3. Platform-specific cleanup
        if self.system == "Windows":
            # Windows specific cleanup
            try:
                subprocess.run(["taskkill", "/f", "/im", "pythonw.exe"], 
                              capture_output=True, check=False)
            except:
                pass
        
        # Wait a moment for processes to fully terminate
        if total_killed:
            time.sleep(1)
            if verbose:
                print("⏳ Waiting for processes to fully terminate...")
        
        if verbose:
            print(f"✅ Cleanup complete! Total processes cleaned: {len(set(total_killed))}")
        
        return list(set(total_killed))

def cleanup_on_startup(verbose=True):
    """Main cleanup function to call on application startup."""
    try:
        # Check if psutil is available
        import psutil
        
        cleaner = ProcessCleanup()
        return cleaner.comprehensive_cleanup(verbose=verbose)
        
    except ImportError:
        if verbose:
            print("⚠️  psutil not available, using basic cleanup...")
        
        # Fallback to basic system commands
        system = platform.system()
        
        if system == "Darwin" or system == "Linux":
            # Unix-like systems
            try:
                subprocess.run(["pkill", "-f", "python.*factory_test"], check=False)
                subprocess.run(["pkill", "-f", "python.*project_station"], check=False)
                if verbose:
                    print("✅ Basic cleanup completed (Unix)")
            except:
                pass
        elif system == "Windows":
            # Windows
            try:
                subprocess.run(["taskkill", "/f", "/im", "python.exe"], check=False)
                subprocess.run(["taskkill", "/f", "/im", "pythonw.exe"], check=False)
                if verbose:
                    print("✅ Basic cleanup completed (Windows)")
            except:
                pass
        
        return []

if __name__ == "__main__":
    """Test the cleanup functionality."""
    print("Testing factory test process cleanup...")
    cleanup_on_startup(verbose=True)