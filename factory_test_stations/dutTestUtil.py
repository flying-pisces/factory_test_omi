#!/usr/bin/python

import sys
import getopt
import code
import test_station.dut.dut

class simOperator:
    def print_to_console(self, msg):
        print msg

if __name__ == '__main__':
    SN = "1HC30000000000"

    dut = test_station.dut.dut.projectDut('','','')

    # IPython.embed()

    # variables = globals().copy()
    # variables.update(locals())
    # shell = code.InteractiveConsole(variables)
    # shell.interact()


