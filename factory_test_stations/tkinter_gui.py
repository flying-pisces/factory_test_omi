#!/usr/bin/env python3
"""
Cross-platform GUI for factory test stations using tkinter.
This provides a simple GUI alternative to the Windows WPF interface.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import sys
import os
import platform

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import station_config
import test_station.test_station_project_station as test_station


class TkinterOperatorInterface:
    """Tkinter-based operator interface for cross-platform GUI."""
    
    def __init__(self, gui_parent):
        self.gui_parent = gui_parent
        self.test_items = []
        
    def print_to_console(self, message, color=None):
        """Print message to GUI console."""
        self.gui_parent.append_to_console(message, color)
        
    def prompt(self, message, color=None):
        """Display a prompt message."""
        self.gui_parent.set_status(f"PROMPT: {message}", color)
        
    def wait(self, duration, message=""):
        """Wait for specified duration with optional message."""
        if message:
            self.print_to_console(f"WAIT: {message}")
        time.sleep(duration)
        
    def update_test_item_array(self, test_items):
        """Update the test items list."""
        self.test_items = test_items
        self.gui_parent.update_test_items(test_items)
        
    def update_root_config(self, config_dict):
        """Update GUI configuration."""
        self.gui_parent.update_config(config_dict)
            
    def clear_console(self):
        """Clear the console."""
        self.gui_parent.clear_console()
        
    def clear_test_values(self):
        """Clear test values."""
        pass
        
    def operator_input(self, title="Input", msg="", msg_type="info"):
        """Get operator input."""
        if msg_type == "error":
            messagebox.showerror(title, msg)
        elif msg_type == "warning":
            messagebox.showwarning(title, msg)
        else:
            messagebox.showinfo(title, msg)
        return ""
    
    def close(self):
        """Close the interface."""
        pass


class FactoryTestTkinterGUI:
    """Cross-platform factory test GUI using tkinter."""
    
    def __init__(self, station_config_module, test_station_class):
        self.station_config = station_config_module
        self.test_station_class = test_station_class
        self.station = None
        self.operator_interface = None
        self.testing_thread = None
        self.is_testing = False
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Factory Test Station - Cross Platform")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_gui()
        self.operator_interface = TkinterOperatorInterface(self)
        
    def setup_gui(self):
        """Set up the GUI layout."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Factory Test Station", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Serial number input
        ttk.Label(main_frame, text="Serial Number:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.serial_entry = ttk.Entry(main_frame, width=20, font=("Arial", 12))
        self.serial_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.serial_entry.bind('<Return>', self.on_start_test)
        
        # Start test button
        self.start_button = ttk.Button(main_frame, text="Start Test", command=self.on_start_test)
        self.start_button.grid(row=1, column=2, padx=(5, 0))
        
        # Console output
        console_frame = ttk.LabelFrame(main_frame, text="Console Output", padding="5")
        console_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        
        self.console_text = scrolledtext.ScrolledText(console_frame, height=15, width=80)
        self.console_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, padding="5")
        status_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Test results frame
        results_frame = ttk.LabelFrame(main_frame, text="Test Results", padding="5")
        results_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.result_var = tk.StringVar()
        self.result_label = ttk.Label(results_frame, textvariable=self.result_var, 
                                     font=("Arial", 14, "bold"))
        self.result_label.grid(row=0, column=0)
        
        # Initialize station
        self.initialize_station()
        
    def initialize_station(self):
        """Initialize the test station."""
        try:
            self.append_to_console("Initializing test station...", "blue")
            
            # Load station configuration
            station_config.load_station('project_station')
            
            # Create station instance
            self.station = self.test_station_class(self.station_config, self.operator_interface)
            
            # Initialize the station
            self.station.initialize()
            
            self.append_to_console("Station initialization complete!", "green")
            self.set_status("Ready - Enter serial number to start test")
            
        except Exception as e:
            self.append_to_console(f"Failed to initialize station: {str(e)}", "red")
            self.set_status(f"Error: {str(e)}")
    
    def append_to_console(self, message, color=None):
        """Append message to console with optional color."""
        timestamp = time.strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}\n"
        
        # Insert text
        self.console_text.insert(tk.END, formatted_msg)
        
        # Apply color if specified
        if color:
            start_idx = self.console_text.index(f"{tk.END}-1c linestart")
            end_idx = self.console_text.index(f"{tk.END}-1c")
            
            # Configure color tags
            if color == "red":
                self.console_text.tag_add("red", start_idx, end_idx)
                self.console_text.tag_config("red", foreground="red")
            elif color == "green":
                self.console_text.tag_add("green", start_idx, end_idx)
                self.console_text.tag_config("green", foreground="green")
            elif color == "blue":
                self.console_text.tag_add("blue", start_idx, end_idx)
                self.console_text.tag_config("blue", foreground="blue")
        
        # Auto-scroll to bottom
        self.console_text.see(tk.END)
        self.root.update_idletasks()
    
    def set_status(self, message, color=None):
        """Set status bar message."""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def clear_console(self):
        """Clear the console."""
        self.console_text.delete(1.0, tk.END)
    
    def update_test_items(self, test_items):
        """Update test items display."""
        self.append_to_console(f"Loaded {len(test_items)} test items")
    
    def update_config(self, config_dict):
        """Update configuration."""
        for key, value in config_dict.items():
            if key == "FinalResult":
                if value == "OK":
                    self.result_var.set("✓ PASS")
                    self.result_label.config(foreground="green")
                elif value == "NG":
                    self.result_var.set("✗ FAIL")
                    self.result_label.config(foreground="red")
                else:
                    self.result_var.set("")
    
    def on_start_test(self, event=None):
        """Start test button handler."""
        if self.is_testing:
            self.append_to_console("Test already in progress!", "yellow")
            return
            
        serial_number = self.serial_entry.get().strip()
        if not serial_number:
            messagebox.showerror("Error", "Please enter a serial number")
            return
        
        # Clear previous results
        self.result_var.set("")
        self.clear_console()
        
        # Disable controls
        self.start_button.config(state="disabled")
        self.serial_entry.config(state="disabled")
        self.is_testing = True
        
        # Start test in background thread
        self.testing_thread = threading.Thread(target=self.run_test, args=(serial_number,))
        self.testing_thread.daemon = True
        self.testing_thread.start()
    
    def run_test(self, serial_number):
        """Run test in background thread."""
        try:
            self.append_to_console(f"Starting test for unit: {serial_number}", "blue")
            
            # Validate serial number
            self.station.validate_sn(serial_number)
            
            # Check if station is ready
            if not self.station.is_ready():
                self.append_to_console("Station not ready!", "red")
                return
            
            # Run the test
            overall_result, first_failed_test = self.station.test_unit(serial_number)
            
            # Display results
            if overall_result:
                self.append_to_console(f"✓ Unit {serial_number} PASSED", "green")
                self.root.after(0, lambda: self.update_config({"FinalResult": "OK"}))
            else:
                error_code = first_failed_test.get_unique_id() if first_failed_test else "Unknown"
                self.append_to_console(f"✗ Unit {serial_number} FAILED - Error: {error_code}", "red")
                self.root.after(0, lambda: self.update_config({"FinalResult": "NG"}))
            
        except Exception as e:
            self.append_to_console(f"Test failed with exception: {str(e)}", "red")
        finally:
            # Re-enable controls
            self.root.after(0, self.test_complete)
    
    def test_complete(self):
        """Re-enable controls after test completion."""
        self.start_button.config(state="normal")
        self.serial_entry.config(state="normal")
        self.serial_entry.delete(0, tk.END)
        self.serial_entry.focus()
        self.is_testing = False
        self.set_status("Ready - Enter serial number to start test")
    
    def on_closing(self):
        """Handle window closing."""
        if self.is_testing:
            if not messagebox.askokcancel("Quit", "Test in progress. Really quit?"):
                return
        
        if self.station:
            try:
                self.station.close()
            except:
                pass
        
        self.root.destroy()
    
    def main_loop(self):
        """Start the GUI main loop."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()


def main():
    """Main entry point for GUI."""
    try:
        # Check if we can use the GUI
        if platform.system() == "Linux" and not os.environ.get("DISPLAY"):
            print("Error: No display available. Use console_test_runner.py instead.")
            sys.exit(1)
        
        # Create and start GUI
        gui = FactoryTestTkinterGUI(station_config, test_station.projectstationStation)
        gui.main_loop()
        
    except Exception as e:
        print(f"Failed to start GUI: {e}")
        print("Falling back to console mode...")
        # Could import and run console_test_runner here as fallback
        sys.exit(1)


if __name__ == "__main__":
    main()