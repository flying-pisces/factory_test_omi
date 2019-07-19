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
```sh
cd factory_test_omi
.\env\Scripts\activate
pip install -r requirements.txt
```
To exit from the virtualenv, please run:\
```sh
deactivate
```

## Usage:
To run a station under a project, double click `PROJECT_STATION_run.py` or `python PROJECT_STATION_run.py`. For example, to run the AUO uniformity station,\

``` sh
python auo_unif_run.py 
```

Loop test for 100 times, the arg is `-l`
```sh
python auo_unif_run.py -l 100
```
More features such as pyinstall will be developped later. 

## Framework Product Portofolio
(1) Display panel vendor AUO, AUO Uniformity Station (completed) \
(2) Lens vendor Sunny, (in progress) \
(3) to be continued..... 

## Escalation/Suggestion/
[mailto:chuck.yin@oculus.com](mailto:chuck.yin@oculus.com)

## License
Oculus 
