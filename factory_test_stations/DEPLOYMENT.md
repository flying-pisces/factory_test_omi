# Factory Test Station Deployment Guide

## Portable Python Environment

This deployment approach creates a self-contained Python environment that can be bundled with the repository, ensuring clean DevOps environments without system-wide Python dependencies.

## Quick Setup

### 1. Create Portable Environment
```bash
# Run the setup script
python setup_portable_env.py

# This creates:
# - portable_env/          # Self-contained Python environment
# - launchers/             # Cross-platform launch scripts  
# - requirements.txt       # Dependency reference
```

### 2. Use the Station
```bash
# Windows
launchers/run_station.bat --web

# Unix/Linux/Mac  
./launchers/run_station.sh --tk

# Cross-platform Python
python launchers/run_station.py --console
```

## Directory Structure After Setup

```
factory_test_stations/
├── portable_env/           # Self-contained Python environment
│   ├── bin/               # Python executables (Unix/Linux)
│   ├── Scripts/           # Python executables (Windows)  
│   ├── lib/               # Python packages
│   └── pyvenv.cfg         # Environment configuration
├── launchers/             # Launch scripts
│   ├── run_station.bat    # Windows launcher
│   ├── run_station.sh     # Unix/Linux launcher
│   └── run_station.py     # Cross-platform launcher
├── requirements.txt       # Dependencies list
└── setup_portable_env.py  # Setup script
```

## Benefits

1. **Clean DevOps**: No system-wide Python installations required
2. **Reproducible**: Consistent Python version and dependencies
3. **Portable**: Can be copied to any machine
4. **Isolated**: Doesn't interfere with other Python projects
5. **Versioned**: Environment definition is code-controlled
6. **Auto-Cleanup**: Automatically kills previous Python processes on startup for clean state

## CI/CD Integration

### Docker Alternative
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY factory_test_stations/ .
RUN python setup_portable_env.py
CMD ["python", "launchers/run_station.py", "--web"]
```

### GitHub Actions
```yaml
- name: Setup Factory Test Environment
  run: |
    python factory_test_stations/setup_portable_env.py
    
- name: Run Tests  
  run: |
    python factory_test_stations/launchers/run_station.py --console
```

## Manual Deployment

### 1. Copy Repository
```bash
# Copy the entire factory_test_stations directory
cp -r factory_test_stations/ /target/location/
```

### 2. Setup Environment
```bash
cd /target/location/factory_test_stations/
python setup_portable_env.py
```

### 3. Run Station
```bash
./launchers/run_station.sh --web
```

## Environment Management

### Updating Dependencies
```bash
# Recreate environment with new packages
python setup_portable_env.py

# Or manually update
portable_env/bin/pip install package_name
```

### Backing Up Environment
```bash
# The entire portable_env directory can be archived
tar -czf factory_station_env.tar.gz portable_env/
```

### Sharing Environment
```bash
# Zip the entire setup for distribution
zip -r factory_test_station.zip factory_test_stations/
```

## Troubleshooting

### Python Not Found
- Ensure Python 3.7+ is available for initial setup
- After setup, use the launcher scripts exclusively

### Permission Issues (Unix/Linux)
```bash
chmod +x launchers/run_station.sh
chmod +x launchers/run_station.py
```

### Package Installation Failures
- Check internet connectivity during setup
- Some packages may need system dependencies
- Consider using `--no-deps` for problematic packages

### Environment Corruption
```bash
# Simply recreate the environment
rm -rf portable_env/
python setup_portable_env.py
```

## Process Management Features

### Automatic Cleanup on Startup
The factory test station automatically performs comprehensive cleanup on every startup:

- **Process Detection**: Identifies previous Python processes running factory test code
- **Port Cleanup**: Kills processes using common web interface ports (5000, 5001, 8000, etc.)
- **Graceful Termination**: Attempts graceful shutdown before force termination
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Safe Operation**: Never kills the current startup process

### Manual Testing
```bash
# Test cleanup functionality
python test_cleanup.py

# View cleanup during startup
python project_station_run.py --help
```

### Cleanup Dependencies
The cleanup feature requires `psutil>=5.8.0`:
```bash
pip install psutil>=5.8.0
```

If psutil is not available, falls back to basic system commands.

## Advanced Usage

### Custom Python Version
```bash
# Use specific Python version for setup
/path/to/python3.9 setup_portable_env.py
```

### Adding Packages
Edit `setup_portable_env.py` and modify the `requirements` list, then run:
```bash
python setup_portable_env.py
```

### Platform-Specific Packages
The setup script can be modified to install different packages based on the platform:
```python
if platform.system() == "Windows":
    requirements.append("windows-specific-package")
elif platform.system() == "Linux":
    requirements.append("linux-specific-package")
```

## Integration with Existing Workflows

The portable environment approach is designed to replace:
- System Python installations
- Global package management
- Complex dependency resolution
- Platform-specific setup scripts

All while maintaining compatibility with existing factory test station code.