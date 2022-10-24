# -*- encoding:utf-8 -*-
__author__ = 'elton.tian'
import win32process
import psutil


def ok_to_test(serial):
    return True, f''


def save_results(test_log):
    """

    :type test_log: hardware_station_common.test_station.test_log.TestRecord
    """
    return save_results_from_logs(test_log.get_file_path())


def save_results_from_logs(log_file_path):
    return True, f''


def initialize(station_config):
    try:
        if 'mes_helper_eeprom.exe' not in [c.info['name'] for c in psutil.process_iter(['name'])]:
            sb = win32process.CreateProcess(
                'c:/SourceCodeMyzy/meshelper/src/dist/mes_helper_eeprom.exe', '',
                None, None, 0, win32process.CREATE_NO_WINDOW, None, None, win32process.STARTUPINFO())
            print('======='*10)
        print('abcd'*10)

    except Exception as e:
        print(str(e))
        print(sb)


def login_system(usr, pwd):
    return True, None
