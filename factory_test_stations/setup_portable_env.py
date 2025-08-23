#!/usr/bin/env python3
"""
Portable Python environment setup for factory test stations.
Creates a self-contained Python environment with all dependencies.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

class PortablePythonSetup:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.env_dir = self.root_dir / "portable_env"
        self.system = platform.system()
        
    def create_environment(self):
        """Create a portable Python environment."""
        print(f"Creating portable Python environment in {self.env_dir}")
        
        # Remove existing environment
        if self.env_dir.exists():
            print("Removing existing environment...")
            shutil.rmtree(self.env_dir)
        
        # Create virtual environment
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(self.env_dir)], check=True)
        
        # Get pip path for the new environment
        if self.system == "Windows":
            pip_path = self.env_dir / "Scripts" / "pip.exe"
            python_path = self.env_dir / "Scripts" / "python.exe"
        else:
            pip_path = self.env_dir / "bin" / "pip"
            python_path = self.env_dir / "bin" / "python"
        
        # Upgrade pip
        print("Upgrading pip...")
        subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        self.install_requirements(pip_path)
        
        # Create launcher scripts
        self.create_launchers(python_path)
        
        print("Portable environment created successfully!")
        print(f"Environment location: {self.env_dir}")
        
    def install_requirements(self, pip_path):
        """Install required packages."""
        requirements = [
            "flask>=2.0.0",
            "flask-socketio>=5.0.0", 
            "python-socketio>=5.0.0",
            "eventlet>=0.33.0",
            "pyserial>=3.5",
            "requests>=2.25.0",
            "numpy>=1.20.0",
            "Pillow>=8.0.0",
            "opencv-python>=4.5.0",
            "matplotlib>=3.3.0",
            "psutil>=5.8.0"
        ]
        
        print("Installing requirements...")
        for req in requirements:
            try:
                print(f"Installing {req}...")
                subprocess.run([str(pip_path), "install", req], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Warning: Failed to install {req}: {e}")
                
    def create_launchers(self, python_path):
        """Create launcher scripts for different platforms."""
        launchers_dir = self.root_dir / "launchers"
        launchers_dir.mkdir(exist_ok=True)
        
        # Windows launcher
        bat_content = f"""@echo off
cd /d "%~dp0.."
"{python_path}" project_station_run.py %*
"""
        with open(launchers_dir / "run_station.bat", "w") as f:
            f.write(bat_content)
            
        # Unix/Linux launcher
        sh_content = f"""#!/bin/bash
cd "$(dirname "$0")/.."
"{python_path}" project_station_run.py "$@"
"""
        with open(launchers_dir / "run_station.sh", "w") as f:
            f.write(sh_content)
        os.chmod(launchers_dir / "run_station.sh", 0o755)
        
        # Cross-platform Python launcher
        py_content = f'''#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path

# Change to the parent directory of this script
script_dir = Path(__file__).parent
parent_dir = script_dir.parent
os.chdir(parent_dir)

# Run the station with the portable Python
python_path = r"{python_path}"
cmd = [python_path, "project_station_run.py"] + sys.argv[1:]
subprocess.run(cmd)
'''
        with open(launchers_dir / "run_station.py", "w") as f:
            f.write(py_content)
        os.chmod(launchers_dir / "run_station.py", 0o755)
        
        print(f"Created launchers in {launchers_dir}:")
        print("  - run_station.bat (Windows)")
        print("  - run_station.sh (Unix/Linux)")  
        print("  - run_station.py (Cross-platform)")
        
    def create_requirements_file(self):
        """Create a requirements.txt file for reference."""
        requirements_content = """# Factory Test Station Requirements
flask>=2.0.0
flask-socketio>=5.0.0
python-socketio>=5.0.0
eventlet>=0.33.0
pyserial>=3.5
requests>=2.25.0
numpy>=1.20.0
Pillow>=8.0.0
opencv-python>=4.5.0
matplotlib>=3.3.0
psutil>=5.8.0

# Optional dependencies for enhanced functionality
# Add platform-specific packages as needed
"""
        with open(self.root_dir / "requirements.txt", "w") as f:
            f.write(requirements_content)
        print("Created requirements.txt")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
Portable Python Environment Setup

Usage:
    python setup_portable_env.py [options]

Options:
    --help          Show this help message
    --requirements  Create requirements.txt only

This script creates a self-contained Python environment that can be
bundled with the repository for DevOps environment cleanliness.
""")
        return
        
    setup = PortablePythonSetup()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--requirements":
        setup.create_requirements_file()
    else:
        setup.create_environment()
        setup.create_requirements_file()

if __name__ == "__main__":
    main()