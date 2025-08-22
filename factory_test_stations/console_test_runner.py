#!/usr/bin/env python3
"""
Cross-platform console-based test runner for factory test stations.
This provides a simple alternative to the Windows WPF GUI for testing on all platforms.
"""

import os
import sys
import time
import logging
import argparse
import platform

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import station_config
import test_station.test_station_project_station as test_station


class ConsoleOperatorInterface:
    """Simple console-based operator interface for cross-platform testing."""
    
    def __init__(self):
        self.test_items = []
        self.console_log = []
        
    def print_to_console(self, message, color=None):
        """Print message to console with optional color."""
        timestamp = time.strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message.strip()}"
        
        # Simple color support for terminals
        if color and platform.system() != "Windows":
            color_codes = {
                'red': '\033[91m',
                'green': '\033[92m',
                'yellow': '\033[93m',
                'blue': '\033[94m',
                'grey': '\033[90m',
                'reset': '\033[0m'
            }
            if color in color_codes:
                formatted_msg = f"{color_codes[color]}{formatted_msg}{color_codes['reset']}"
        
        print(formatted_msg)
        self.console_log.append(formatted_msg)
        
    def prompt(self, message, color=None):
        """Display a prompt message."""
        self.print_to_console(f"PROMPT: {message}", color)
        
    def wait(self, duration, message=""):
        """Wait for specified duration with optional message."""
        if message:
            self.print_to_console(f"WAIT: {message}")
        time.sleep(duration)
        
    def update_test_item_array(self, test_items):
        """Update the test items list."""
        self.test_items = test_items
        self.print_to_console(f"Loaded {len(test_items)} test items")
        
    def update_root_config(self, config_dict):
        """Update root configuration (stub for console mode)."""
        for key, value in config_dict.items():
            self.print_to_console(f"CONFIG: {key} = {value}")
            
    def clear_console(self):
        """Clear the console."""
        os.system('cls' if platform.system() == "Windows" else 'clear')
        
    def clear_test_values(self):
        """Clear test values (stub for console mode)."""
        pass
        
    def operator_input(self, title="Input", msg="", msg_type="info"):
        """Get operator input (simplified for console)."""
        self.print_to_console(f"{msg_type.upper()}: {msg}")
        return input(f"{title}: ")


class ConsoleTestRunner:
    """Console-based test runner for factory test stations."""
    
    def __init__(self, station_name):
        self.station_name = station_name
        self.operator_interface = ConsoleOperatorInterface()
        self.station = None
        
    def initialize(self):
        """Initialize the test station."""
        try:
            # Load station configuration
            station_config.load_station(self.station_name)
            
            # Create station instance
            self.station = test_station.projectstationStation(
                station_config, self.operator_interface
            )
            
            self.operator_interface.print_to_console(
                f"Initializing {self.station_name} station...", "blue"
            )
            
            # Initialize the station
            self.station.initialize()
            
            self.operator_interface.print_to_console(
                "Station initialization complete!", "green"
            )
            
            return True
            
        except Exception as e:
            self.operator_interface.print_to_console(
                f"Failed to initialize station: {str(e)}", "red"
            )
            return False
    
    def run_test(self, serial_number):
        """Run a test for the given serial number."""
        try:
            self.operator_interface.print_to_console(
                f"Starting test for unit: {serial_number}", "blue"
            )
            
            # Validate serial number
            self.station.validate_sn(serial_number)
            
            # Check if station is ready
            if not self.station.is_ready():
                self.operator_interface.print_to_console(
                    "Station not ready!", "red"
                )
                return False, "Station not ready"
            
            # Run the test
            overall_result, first_failed_test = self.station.test_unit(serial_number)
            
            # Display results
            if overall_result:
                self.operator_interface.print_to_console(
                    f"✓ Unit {serial_number} PASSED", "green"
                )
            else:
                error_code = first_failed_test.get_unique_id() if first_failed_test else "Unknown"
                self.operator_interface.print_to_console(
                    f"✗ Unit {serial_number} FAILED - Error: {error_code}", "red"
                )
            
            return overall_result, first_failed_test
            
        except Exception as e:
            self.operator_interface.print_to_console(
                f"Test failed with exception: {str(e)}", "red"
            )
            return False, str(e)
    
    def close(self):
        """Close the test station."""
        if self.station:
            try:
                self.station.close()
                self.operator_interface.print_to_console(
                    "Station closed successfully", "blue"
                )
            except Exception as e:
                self.operator_interface.print_to_console(
                    f"Error closing station: {str(e)}", "red"
                )
    
    def interactive_mode(self):
        """Run in interactive mode for manual testing."""
        self.operator_interface.print_to_console(
            "=== Interactive Test Mode ===", "blue"
        )
        self.operator_interface.print_to_console(
            "Enter serial numbers to test, 'quit' to exit", "blue"
        )
        
        while True:
            try:
                serial_number = input("\nSerial Number: ").strip()
                
                if serial_number.lower() in ['quit', 'exit', 'q']:
                    break
                    
                if not serial_number:
                    continue
                    
                self.run_test(serial_number)
                
            except KeyboardInterrupt:
                self.operator_interface.print_to_console(
                    "\nTest interrupted by user", "yellow"
                )
                break
            except Exception as e:
                self.operator_interface.print_to_console(
                    f"Error: {str(e)}", "red"
                )


def main():
    """Main entry point for console test runner."""
    parser = argparse.ArgumentParser(
        description='Cross-platform console test runner for factory test stations'
    )
    parser.add_argument(
        '--station', 
        default='project_station',
        help='Station type to run (default: project_station)'
    )
    parser.add_argument(
        '--serial', 
        help='Serial number to test (if not provided, runs interactive mode)'
    )
    parser.add_argument(
        '--loop', 
        type=int,
        help='Number of test loops to run'
    )
    
    args = parser.parse_args()
    
    # Create and initialize test runner
    runner = ConsoleTestRunner(args.station)
    
    try:
        if not runner.initialize():
            sys.exit(1)
        
        if args.serial:
            # Single test mode
            overall_result, _ = runner.run_test(args.serial)
            sys.exit(0 if overall_result else 1)
        elif args.loop:
            # Loop test mode
            test_sn = input("Enter serial number for loop testing: ").strip()
            passed = 0
            for i in range(args.loop):
                runner.operator_interface.print_to_console(
                    f"Loop {i+1}/{args.loop}", "blue"
                )
                result, _ = runner.run_test(test_sn)
                if result:
                    passed += 1
                time.sleep(1)
            
            runner.operator_interface.print_to_console(
                f"Loop testing complete: {passed}/{args.loop} passed", 
                "green" if passed == args.loop else "yellow"
            )
        else:
            # Interactive mode
            runner.interactive_mode()
            
    except KeyboardInterrupt:
        runner.operator_interface.print_to_console(
            "Test runner interrupted by user", "yellow"
        )
    except Exception as e:
        runner.operator_interface.print_to_console(
            f"Fatal error: {str(e)}", "red"
        )
        sys.exit(1)
    finally:
        runner.close()


if __name__ == "__main__":
    main()