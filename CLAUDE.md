# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Factory_test_omi is a Python multitier framework for bringing up test stations at optical module integrator (OMI) facilities for Oculus hardware components (displays, lenses, cameras, sensors). The framework follows OOP principles with strict separation of concerns: each physical/virtual component (Fixture, DUT, Station, TestLog, GUI) is a standalone class.

## Project Structure

The codebase follows a hierarchical architecture:

```
factory_test_stations/
├── *_run.py                    # Entry points for each station type
├── config/                     # Station configurations and limits
│   ├── station_config_*.py     # Station-specific parameters 
│   └── station_limits_*.py     # Pass/fail criteria
├── test_station/              # Core testing components
│   ├── dut/                   # Device Under Test implementations
│   ├── test_equipment/        # Third-party instruments
│   ├── test_fixture/          # Custom hardware bindings
│   └── test_station_*.py      # Station orchestration classes
└── hardware_station_common/   # Shared infrastructure (missing from current codebase)
```

## Station Types

Current implementations include:
- **pancake_offaxis**: Off-axis optical measurements
- **pancake_pixel**: Pixel-level testing  
- **pancake_pr788**: PR788 specific tests
- **pancake_uniformity**: Display uniformity testing
- **seacliff_eeprom**: EEPROM programming/validation
- **seacliff_mot**: Motor testing
- **seacliff_paneltesting**: Panel testing

## Core Architecture Components

### 1. Station Class Hierarchy
- Base class: `test_station.TestStation`  
- Station-specific classes inherit and implement `_do_test()` method
- Each station manages its own DUT, Fixture, and Equipment instances

### 2. Configuration System
- **Config files**: Station-specific parameters (paths, timeouts, hardware settings)
- **Limits files**: Pass/fail criteria for measurements
- Loaded dynamically via `station_config.load_station(station_name)`

### 3. DUT (Device Under Test)
- Base class: `hardware_station_common.test_station.dut.DUT`
- Station-specific implementations (e.g., `pancakeDut`, `pancakeDutOffAxis`)
- Handles device communication, power control, display patterns
- Supports both serial and ethernet communication

### 4. Test Equipment Integration
- Interfaces with third-party instruments (cameras, power supplies, DAQs)
- Sequence-based testing using `.seqx` algorithm files
- Measurement export capabilities (CSV, PNG formats)

### 5. Test Fixtures
- Custom hardware for DUT/Equipment binding
- Motion control (XY positioning)
- Environmental controls (particle counters)
- Operator interface buttons

## Running Stations

Each station has its own entry point:

```bash
# Run a specific station
python pancake_offaxis_run.py

# Loop testing (100 iterations)  
python pancake_offaxis_run.py -l 100

# Other station examples
python seacliff_eeprom_run.py
python pancake_uniformity_run.py
```

## Development Commands

### Installation
```bash
cd factory_test_omi
.\env\Scripts\activate
pip install -r requirements.txt
```

### Cleanup
```bash
# Windows
clean.bat

# Unix/Linux/Mac
./clean.sh
```

Both scripts remove:
- Python cache files (*.pyc, __pycache__)
- Test artifacts (*.log, *_debug.log, *_1.json)
- Temporary files (*.bin, *.*~, Thumbs.db)
- Capture directories (CaptureFolder1, CaptureFolder2)

## Key Development Patterns

### Serial Number Validation
- Regex patterns defined in config files (`SERIAL_NUMBER_MODEL_NUMBER`)
- Station-specific validation in `validate_sn()` methods

### Test Execution Flow
1. `is_ready()` - Validate station state and DUT connection
2. `_do_test()` - Execute test sequence  
3. Station-specific test methods (e.g., `offaxis_test_do()`)
4. `close_test()` - Cleanup and result processing

### Hardware Communication
- Serial communication for DUTs via COM ports
- Ethernet proxy for network-connected devices  
- Equipment APIs for instrument control

### Data Management
- Test results stored in `test_log.TestRecord` objects
- Measurement data exported to CSV/PNG formats
- TTXM database files for detailed analysis
- Configurable data retention (`IS_SAVEDB` flag)

### Error Handling
- Custom exception classes (`DUTError`, `pancakeoffaxisError`)
- Retry mechanisms for hardware operations
- Graceful degradation with simulation modes

## Configuration Management

### Station Config Structure
```python
# Paths and directories
ROOT_DIR = r'C:\oculus\factory_test_omi\factory_test_stations'
CSV_SUMMARY_DIR = r'...\factory-test_logs\offaxis_summary'

# Hardware settings
FIXTURE_COMPORT = "COM2"  
DUT_COMPORT = "COM1"
CAMERA_SN = "camera_serial_number"

# Test parameters
PATTERNS = ['White', 'Red', 'Green', 'Blue']
COLORS = [(255,255,255), (255,0,0), (0,255,0), (0,0,255)]
POSITIONS = [(0, [100, 200], ['White', 'Red'])]  # posIdx, [x,y], patterns
```

### Simulation Modes
- `FIXTURE_SIM`: Simulate fixture operations
- `DUT_SIM`: Simulate DUT responses  
- `EQUIPMENT_SIM`: Use demo data instead of real measurements

## File Organization

### Binary Tools Location
- ADB tools consolidated in: `test_station/dut/bin/`
- Test patterns in: `test_station/dut/test_patterns/`
- Algorithms in: `test_station/test_equipment/algorithm/`

### Naming Conventions
- Station configs: `station_config_PROJECT_STATION.py`
- Station limits: `station_limits_PROJECT_STATION.py`
- Run files: `PROJECT_STATION_run.py`
- Test stations: `test_station_PROJECT_STATION.py`

## Testing and Quality

The framework emphasizes hardware automation reliability:
- Configurable retry mechanisms for hardware operations
- Environmental monitoring (particle counters, free disk space)
- Comprehensive logging and error reporting
- Data validation and export capabilities

## Security and Network Isolation

- Network only used for DevOps and data upload
- No network interaction during testing (principle of minimal adverse effects)
- Station/network isolation maintained for reliability