import hardware_station_common.test_station.test_equipment
import os
import json
import clr
import numpy as np
import sys
import pprint
from datetime import datetime
import logging
import ctypes
import traceback
import glob


class seacliffVidEquipmentError(Exception):
    pass


class seacliffVidEquipment(hardware_station_common.test_station.test_equipment.TestEquipment):
    """
        class for seacliff vid Equipment
            this is for doing all the specific things necessary to interface with equipment
    """
    def __init__(self, station_config, operator_interface):
        hardware_station_common.test_station.test_equipment.TestEquipment.__init__(self, station_config, operator_interface)
        self.name = "Raytrix R25"
        self._verbose = station_config.IS_VERBOSE
        self._station_config = station_config
        self._error_message = self.name + "is out of work"
        self._read_error = False
        self._version = None
        self._camera_sn = None
        self._k_errcode = 'ErrorCode'
        self._k_message = 'Message'
        dll_path = os.path.join(self._station_config.ROOT_DIR, self._station_config.CAMERA_DYNAMIC_LIB)
        self._rxLib = ctypes.cdll.LoadLibrary(dll_path)

        # Define the input and output parameter for the functions of the raytrix lib
        self._rxLib.InitLFSystem.restype = ctypes.c_char_p
        self._rxLib.ClearLFSystem.restype = ctypes.c_char_p
        self._rxLib.BindConnectedCamera.restype = ctypes.c_char_p
        self._rxLib.LoadCameraConfig.restype = ctypes.c_char_p
        self._rxLib.LoadCameraConfig.argtypes = ctypes.c_char_p,
        self._rxLib.GetCameraSerialNumber.restype = ctypes.c_char_p
        self._rxLib.TriggerCamera.restype = ctypes.c_char_p
        self._rxLib.ComputeImage.restype = ctypes.c_char_p
        self._rxLib.SaveImage.restype = ctypes.c_char_p
        self._rxLib.SaveImage.argtypes = ctypes.c_char_p,
        self._rxLib.SetComputeParameters.restype = ctypes.c_char_p
        self._rxLib.SetComputeParameters.argtypes = ctypes.c_char_p,
        self._rxLib.BindRayFile.restype = ctypes.c_char_p
        self._rxLib.BindRayFile.argtypes = ctypes.c_char_p,
        self._rxLib.SaveRay.restype = ctypes.c_char_p
        self._rxLib.SaveRay.argtypes = ctypes.c_char_p,

        self._export_list = {
            'Depth3D_ViewVirtualUndistorted_To_Virtual_AfterSettings': 80,
            'Depth3D_ViewVirtualUndistorted_To_Object_AfterSettings': 81,
            'Depth3D_ViewVirtualUndistorted_To_Reference_AfterSettings': 82,
            # 'Depth3D_ViewObjectOrthographic_To_Virtual_AfterSettings': 83,
            # 'Depth3D_ViewObjectOrthographic_To_Object_AfterSettings': 84,
            # 'Depth3D_ViewObjectOrthographic_To_Reference_AfterSettings': 85,
        }

    @property
    def camera_sn(self):
        return self._camera_sn

    def _init_lf_system(self):
        return self._parse_result(self._rxLib.InitLFSystem())

    def _clear_lf_system(self):
        return self._parse_result(self._rxLib.ClearLFSystem())

    def _bind_connected_camera(self):
        return self._parse_result(self._rxLib.BindConnectedCamera())

    def _load_camera_config(self, config_file_name):
        return self._parse_result(self._rxLib.LoadCameraConfig(config_file_name.encode()))

    def _get_camera_sn(self):
        return self._parse_result(self._rxLib.GetCameraSerialNumber())

    def _trigger_camera(self):
        return self._parse_result(self._rxLib.TriggerCamera())

    def _compute_image(self, cmd):
        return self._parse_result(self._rxLib.ComputeImage(cmd))

    def _save_image(self, filename):
        return self._parse_result(self._rxLib.SaveImage(filename.encode()))

    def _set_compute_parameters(self, filename):
        return self._parse_result(self._rxLib.SetComputeParameters(filename.encode()))

    def _bind_ray_file(self, filename):
        return self._parse_result(self._rxLib.BindRayFile(filename.encode()))

    def _save_ray(self, filename):
        return self._parse_result(self._rxLib.SaveRay(filename.encode()))

    def _parse_result(self, res_msg):
        resjson = None
        if self._verbose:
            logging.info(f"rxLib response message:{res_msg}")
        try:
            resjson = json.loads(res_msg.decode())
        except:
            pass
        error = None
        if isinstance(resjson, dict):
            error = int(resjson.get(self._k_errcode))
        if error is None or int(error) != 0:
            raise seacliffVidEquipmentError(f'API <--- {res_msg}')
        return error, resjson

    def is_ready(self):
        pass

    def initialize(self):
        self._operator_interface.print_to_console("Initializing seacliff Vid Equipment.\n")
        self._camera_sn = None
        res, __ = self._parse_result(self._rxLib.InitLFSystem())
        if self._station_config.EQUIPMENT_SIM:
            self._camera_sn = 'SIM'
        else:
            res, __ = self._parse_result(self._rxLib.BindConnectedCamera())
            res, sn_msg = self._parse_result(self._rxLib.GetCameraSerialNumber())
            self._camera_sn = sn_msg.get(self._k_message)
            self._clear_lf_system()
            if not self._camera_sn:
                raise seacliffVidEquipmentError('Fail to initialise Equipment.')

    def open(self):
        # Load configuration from json-file.
        # self._rxLib.SetComputeParameters(self._station_config.CAMERA_RX_SET)
        pass

    def close(self):
        self._operator_interface.print_to_console("Closing seacliff Vid Equipment.\n")

    def do_measure_and_export(self, pattern_name, data_save_dir):
        try:
            self._init_lf_system()
            raw_db_pth = os.path.join(data_save_dir, f'{pattern_name}.ray')
            if self._station_config.EQUIPMENT_SIM:
                files = glob.glob(os.path.join(data_save_dir, f'*.ray'))
                if len(files) >= 1:
                    raw_db_pth = files[-1]
                self._operator_interface.print_to_console(f'bind file: {raw_db_pth} .\n')
                self._bind_ray_file(raw_db_pth)
            else:
                self._bind_connected_camera()
                cfg_filename = os.path.join(self._station_config.ROOT_DIR,
                                            self._station_config.CAMERA_CONFIG, f'{pattern_name}.json')
                self._load_camera_config(cfg_filename)
                self._trigger_camera()

            rxset = os.path.join(self._station_config.ROOT_DIR, self._station_config.CAMERA_RX_SET)
            self._set_compute_parameters(rxset)

            for k, v in self._export_list.items():
                self._compute_image(v)
                target_filename = os.path.join(
                    data_save_dir, 'exp', rf'{pattern_name}_{k}.tiff')
                self._save_image(target_filename)
            if not self._station_config.EQUIPMENT_SIM:
                self._save_ray(raw_db_pth)
        finally:
            self._clear_lf_system()


def print_to_console(self, msg):
    pass


if __name__ == '__main__':
    import sys
    import types

    sys.path.append(r'..\..')
    import station_config

    station_config.load_station('seacliff_vid')
    station_config.print_to_console = types.MethodType(print_to_console, station_config)
    equip = seacliffVidEquipment(station_config, station_config)
    equip._init_lf_system()
    # equip.initialize()
    equip._bind_ray_file(r'C:\Users\Shuttle\Desktop\1209\R25-M-E-U3-B028-RS-A - 2125_1.1.ray')

    cfg_filename = os.path.join(station_config.ROOT_DIR, station_config.CAMERA_CONFIG)

    equip._load_camera_config(cfg_filename)
    equip._trigger_camera()
    equip._clear_lf_system()

    # equip.do_measure_and_export('W255')

    # equip.close()

    pass
