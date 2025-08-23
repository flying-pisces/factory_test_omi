# factory_test_omi
The factory test framework with optical module integrator mode

![logo](https://github.com/chuckyin/factory_test_omi/blob/master/logo/logo.PNG)\

Open-source framework focused on hardware automation station fast bring-up at optical module integrator (OMI for short): open, object-orientated and lightweight

## Overview

Factory_test_omi is a python multitier framework  to bring up the test station at component vendor for Oculus hardware product, such as display vendors, lens vendors, camera vendors, sensor vendors, etc. Considering the device under test is not Oculus product, we relieve the restrictions for securities unless we introduce Oculus algorithm. The following principles for this framework applies

(1) Open: open to vendor to maintain the code base reduce the sustain support efforts and save the cost. \
(2) Object-orientated: Any component attributes/properties/methods will be strictly restricted \
(3) Lightweight: To make the framework maintainable, pylint will be strongly recommended to run code quality before implementation.

In the factory_test_omi, the OOP principle is applied to every physical and virtual component. Fixture, DUT, station, even the test_log, GUI is all standalone class which can be instantiated to object. The infrastructure to be used for all stations are hardware_station_common. 

## Features
(1) Encapsulation: Hide values or state inside class, preventing unauthorized parties's direct access. \
(2) Minimize Dependencies: If any component is down, it should have minimum adverse effects on the whole system. \
(3) Network/Station Isolation: The network will be only used for devops of new software and data pushing to server. During the test, there is no interaction between test station to network to comply with principle (2). \
(4) config/limit separation: Limit is to used to judge pass/fail. The config is used to load station specific parameters. They are located under one folder following the nomenclature of `station_config_PROJECT_STATION.py` and `station_limits_PROJECT_STATION.py`. \
(5) Generating a new station under administrator terminal use one line of code under the factory_test_stations directory by
```sh
bash hardware_station_common\new-station PROJECT_NAME STATION_NAME
```
For example, generate a new lens-contrast station for Monterey will be
```sh
bash hardware_station_common\new-station Monterey lens-contrast
```
(6) Deleting a station under administrator terminal use one line of code under the factory_test_stations directory by
```sh
bash hardware_station_common\delete-station PROJECT_NAME STATION_NAME
```
For example, delete the just created len-contrast station for Monterey will be 
```sh
bash hardware_station_common\delete-station Monterey lens-contrast
```


## Nomenclature:
### DUT
Device under Test. 

### Equipment
The third party, usually off-shelf standard instruments to be used in station to interact DUT. Examples: Agilent Power Supply, NI-DAQ, Industry Camera. 

### Fixture
The customized hardware to bind DUT/Equipment, with functions. Examples: Myzy blade fixture, Intelligent Automation IMU fixture, World Fixture, etc. Typically, it needs fast-prototyping, customization and onsite support. Vendors near CM will be preferred.

### Station
Station = DUT + Fixture + Equipment

## Installation:
factory_test_omi can be run by external python; however, setting up a virtual environment to maintain a clean environment is recommended. If the dependencies are not installed yet, please install the dependencies:

**Root Directory:** Use `/factory_test_omi` as the project root (contains README.md, requirements.txt)  
**Working Directory:** Change to `/factory_test_omi/factory_test_stations` to run station scripts

```sh
cd factory_test_omi
.\env\Scripts\activate
pip install -r requirements.txt
```
To exit from the virtualenv, please run:
```sh
deactivate
```

## Usage:

### Python Executable
Use either `python3` or `python` depending on your system:
- **Linux/macOS:** Use `/usr/bin/python3` or `python3`
- **Windows:** Use `python` 
- **Cross-platform:** Use `python3` (recommended)

### UI Modes
All station runners support three UI modes:

**Command Line Arguments:**
- `--console` - Console mode (no GUI) - **DEFAULT**
- `--tk` - Tkinter GUI mode (cross-platform kiosk)  
- `--web` - Web browser GUI mode
- `--help` - Show usage information

### Running Stations

**Change to the working directory first:**
```sh
cd factory_test_omi/factory_test_stations
```

**Basic usage (console mode - default):**
```sh
python3 project_station_run.py
python3 pancake_offaxis_run.py
python3 seacliff_eeprom_run.py
```

**Force specific UI modes:**
```sh
# Console mode (explicit)
python3 project_station_run.py --console

# Tkinter kiosk mode  
python3 project_station_run.py --tk

# Web browser mode
python3 project_station_run.py --web
```

**Get help:**
```sh
python3 project_station_run.py --help
```

**Loop testing (legacy -l argument may be supported by specific stations):**
```sh
python3 pancake_offaxis_run.py -l 100
```

### Available Stations
- `project_station_run.py` - Project station
- `pancake_offaxis_run.py` - Pancake off-axis testing
- `pancake_pixel_run.py` - Pancake pixel testing  
- `pancake_pr788_run.py` - Pancake PR788 testing
- `pancake_uniformity_run.py` - Pancake uniformity testing
- `seacliff_eeprom_run.py` - Seacliff EEPROM programming
- `seacliff_mot_run.py` - Seacliff MOT testing
- `seacliff_paneltesting_run.py` - Seacliff panel testing 

## Framework Product Portofolio
(1) Display panel vendor AUO, AUO Uniformity Station (completed) \
(2) Lens vendor Sunny, (in progress) \
(3) to be continued..... 

## Escalation/Suggestion/
[mailto:chuck.yin@oculus.com](mailto:chuck.yin@oculus.com)

## License
Oculus 
