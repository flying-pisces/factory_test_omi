import hardware_station_common.test_station.test_equipment


class TokkiOffAxisNEquipment(hardware_station_common.test_station.test_equipment.TestEquipment):
    """
        class for Tokki offaxisn Equipment
            this is for doing all the specific things necessary to interface with equipment
    """
    def __init__(self, station_config, operator_interface):
        hardware_station_common.test_station.test_equipment.TestEquipment.__init__(self, station_config, operator_interface)

    def is_ready(self):
        pass

    def initialize(self):
        self._operator_interface.print_to_console("Initializing Tokki OffAxisN Equipment\n")

    def close(self):
        self._operator_interface.print_to_console("Closing Tokki OffAxisN Equipment\n")
