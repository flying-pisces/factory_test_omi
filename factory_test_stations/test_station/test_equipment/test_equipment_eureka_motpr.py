import hardware_station_common.test_station.test_equipment


class EurekaMotPREquipment(hardware_station_common.test_station.test_equipment.TestEquipment):
    """
        class for Eureka motpr Equipment
            this is for doing all the specific things necessary to interface with equipment
    """
    def __init__(self, station_config, operator_interface):
        hardware_station_common.test_station.test_equipment.TestEquipment.__init__(self, station_config, operator_interface)

    def is_ready(self):
        pass

    def initialize(self):
        self._operator_interface.print_to_console("Initializing Eureka MotPR Equipment\n")

    def close(self):
        self._operator_interface.print_to_console("Closing Eureka MotPR Equipment\n")
