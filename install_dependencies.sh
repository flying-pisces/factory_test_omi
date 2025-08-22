#!/bin/bash
# Cross-platform dependency installer for Factory Test OMI framework
# Supports Linux, macOS, and Windows (via Git Bash/WSL)

set -e  # Exit on any error

echo "=== Factory Test OMI Dependency Installer ==="
echo "Detecting platform and installing dependencies for system Python..."

# Detect platform
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="Linux"
    PYTHON_CMD="python3"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macOS"
    PYTHON_CMD="python3"
elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    PLATFORM="Windows"
    PYTHON_CMD="python"
else
    PLATFORM="Unknown"
    PYTHON_CMD="python3"
fi

echo "Platform detected: $PLATFORM"

# Find system Python
if command -v /usr/bin/python3 &> /dev/null; then
    PYTHON_PATH="/usr/bin/python3"
elif command -v $PYTHON_CMD &> /dev/null; then
    PYTHON_PATH=$(which $PYTHON_CMD)
else
    echo "Error: Python 3 not found. Please install Python 3.7+ first."
    exit 1
fi

echo "Using Python: $PYTHON_PATH"

# Show Python version
PYTHON_VERSION=$($PYTHON_PATH --version)
echo "Python version: $PYTHON_VERSION"

# Check pip availability
if ! $PYTHON_PATH -m pip --version &> /dev/null; then
    echo "Error: pip not available. Please install pip first."
    echo "Ubuntu/Debian: sudo apt install python3-pip"
    echo "RHEL/CentOS: sudo yum install python3-pip"
    echo "macOS: Install Xcode command line tools"
    exit 1
fi

# Install system dependencies if needed (Linux only)
if [[ $PLATFORM == "Linux" ]]; then
    echo "Installing system dependencies for Linux..."
    
    # Detect Linux distribution
    if command -v apt-get &> /dev/null; then
        echo "Detected Debian/Ubuntu - installing system packages..."
        sudo apt-get update || true
        sudo apt-get install -y python3-dev python3-pip libxml2-dev libxslt1-dev zlib1g-dev || {
            echo "Warning: Some system packages may not have installed. Continuing..."
        }
    elif command -v yum &> /dev/null; then
        echo "Detected RHEL/CentOS - installing system packages..."
        sudo yum install -y python3-devel python3-pip libxml2-devel libxslt-devel zlib-devel || {
            echo "Warning: Some system packages may not have installed. Continuing..."
        }
    else
        echo "Warning: Unknown Linux distribution. Some dependencies may need manual installation."
    fi
fi

# Install Python dependencies
echo "Installing Python dependencies..."

# Create requirements file if it doesn't exist
if [ ! -f "requirements_complete.txt" ]; then
    cat > requirements_complete.txt << 'EOF'
# Core dependencies for Factory Test OMI framework
numpy>=1.24.0
opencv-python>=4.8.0
scikit-image>=0.20.0
pyserial>=3.5
lxml>=4.9.0
requests>=2.31.0
psutil>=5.9.0
suds-py3>=1.4.5.0
Pillow>=10.0.0
certifi>=2023.7.22
chardet>=5.2.0
six>=1.16.0
tornado>=6.3.0
setuptools>=68.0.0
EOF
    echo "Created requirements_complete.txt"
fi

# Install dependencies with --user flag for non-root installation
echo "Installing dependencies with: $PYTHON_PATH -m pip install --user"
$PYTHON_PATH -m pip install --user -r requirements_complete.txt

echo ""
echo "=== Installation Complete! ==="
echo ""

# Test the installation
echo "Testing installation..."
$PYTHON_PATH -c "
import sys
print('System Python test successful!')
print(f'Python version: {sys.version}')
print('Testing core imports...')

imports_status = []
try:
    import numpy as np
    imports_status.append(f'✓ numpy {np.__version__}')
except ImportError as e:
    imports_status.append(f'✗ numpy: {e}')

try:
    import cv2
    imports_status.append(f'✓ opencv-python {cv2.__version__}')
except ImportError as e:
    imports_status.append(f'✗ opencv-python: {e}')

try:
    import serial
    imports_status.append(f'✓ pyserial')
except ImportError as e:
    imports_status.append(f'✗ pyserial: {e}')

try:
    import lxml
    imports_status.append(f'✓ lxml {lxml.__version__}')
except ImportError as e:
    imports_status.append(f'✗ lxml: {e}')

try:
    import requests
    imports_status.append(f'✓ requests {requests.__version__}')
except ImportError as e:
    imports_status.append(f'✗ requests: {e}')

try:
    import psutil
    imports_status.append(f'✓ psutil {psutil.__version__}')
except ImportError as e:
    imports_status.append(f'✗ psutil: {e}')

for status in imports_status:
    print(status)

failed_imports = [s for s in imports_status if s.startswith('✗')]
if failed_imports:
    print(f'\\nWarning: {len(failed_imports)} dependencies failed to import')
    sys.exit(1)
else:
    print('\\nAll major dependencies successfully imported!')
"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS: All dependencies installed and tested successfully!"
    echo ""
    echo "You can now run the factory test framework:"
    echo "  cd factory_test_stations"
    echo "  $PYTHON_PATH console_test_runner.py --serial \"1NBS1234567890\""
    echo ""
else
    echo ""
    echo "❌ FAILED: Some dependencies could not be imported."
    echo "Please check the error messages above and install missing system packages."
    echo ""
    exit 1
fi