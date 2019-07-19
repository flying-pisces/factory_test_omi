__author__ = 'chuckyin'
#!/usr/bin/env python
# pylint: disable 
# Important note: for True/False settings, these do NOT need quotes.
# but they do need capital first letter.  (i.e. True or False)
import os
###################################
# station_type
#
# Valid values are 'UNIF', 'MURA'
STATION_NUMBER = 0
STATION_TYPE = ''


def load_station(station):
    global STATION_NUMBER
    global STATION_TYPE
    STATION_TYPE = station
    STATION_NUMBER = 0
    config_path = os.path.dirname(os.path.realpath(__file__))
    station_config_file = os.path.join(config_path, 'config', ('station_config_' + STATION_TYPE + '.py'))
    station_limits_file = os.path.join(config_path, 'config', ('station_limits_' + STATION_TYPE + '.py'))
    print station_config_file
    print station_limits_file
    try:
        execfile(station_config_file, globals())  # imports station_config into current namespace
        execfile(station_limits_file, globals())
    except:
        raise Exception
