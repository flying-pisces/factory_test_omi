# -*- encoding:utf-8 -*-
__author__ = 'elton.tian'


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
    pass


def login_system(usr, pwd):
    return True, None
