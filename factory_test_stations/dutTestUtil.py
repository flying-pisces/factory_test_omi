#!/usr/bin/python

import sys
import getopt
import code
import test_station.dut.dut
import hardware_station_common.test_station.dut
import os
import time
# from test_station.dut.displayserver import DisplayServer

class simOperator:
    def print_to_console(self, msg):
        print msg

if __name__ == '__main__':
    sys.path.append("../..")
    import station_config

    SN = "1HC30000000000"
    # dut = test_station.dut.dut.projectDut('','','')
    station_config.load_station('pancake_uniformity')
    operator = simOperator()
    dut = test_station.dut.dut.pancakeDut(SN, station_config, operator)
    dut.initialize()
    # IPython.embed()

    variables = globals().copy()
    variables.update(locals())
    shell = code.InteractiveConsole(variables)
    shell.interact()


