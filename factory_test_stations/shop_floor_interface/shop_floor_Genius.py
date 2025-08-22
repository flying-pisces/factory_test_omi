#!/usr/bin/env python3
"""
Cross-platform shop floor interface stub for Genius system.
This provides a simple stub for testing without actual shop floor integration.
"""

class GeniusShopFloorInterface:
    """Stub implementation of Genius shop floor interface."""
    
    def __init__(self, station_config=None):
        self.station_config = station_config
        
    def ok_to_test(self, serial_number):
        """
        Check if unit is OK to test.
        For barebone testing, always return True.
        """
        print(f"Shop Floor: Checking if {serial_number} is OK to test...")
        return True
    
    def save_results(self, test_log):
        """
        Save test results to shop floor system.
        For barebone testing, just print the results.
        """
        print(f"Shop Floor: Saving results for {test_log.serial_number}")
        print(f"Shop Floor: Overall result: {test_log.get_overall_result()}")
        return True
    
    def get_work_order(self, serial_number):
        """Get work order for serial number."""
        return f"WO-{serial_number[:6]}"
    
    def validate_routing(self, serial_number):
        """Validate routing for serial number."""
        return True

# For compatibility with existing code
def create_shop_floor_interface(station_config):
    """Factory function to create shop floor interface."""
    return GeniusShopFloorInterface(station_config)

# Global interface instance
shop_floor = None

def initialize_shop_floor(station_config):
    """Initialize the shop floor interface."""
    global shop_floor
    shop_floor = create_shop_floor_interface(station_config)
    return shop_floor

def get_shop_floor_interface():
    """Get the current shop floor interface."""
    return shop_floor