#!/usr/bin/env python3
"""
Cross-platform GUI for factory test stations using tkinter.
Fixed version that ensures proper GUI rendering.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import sys
import os
import traceback

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
        # Use after() to ensure thread-safe GUI updates
        self.gui_parent.root.after(0, lambda: self.gui_parent.append_to_console(message, color))
        
    def prompt(self, message, color=None):
        """Display a prompt message."""
        self.gui_parent.root.after(0, lambda: self.gui_parent.set_status(f"PROMPT: {message}"))
        
    def wait(self, duration, message=""):
        """Wait for specified duration with optional message."""
        if message:
            self.print_to_console(f"WAIT: {message}")
        time.sleep(duration)
        
    def update_test_item_array(self, test_items):
        """Update the test items list."""
        self.test_items = test_items
        self.gui_parent.root.after(0, lambda: self.gui_parent.update_test_items(test_items))
        
    def update_root_config(self, config_dict):
        """Update GUI configuration."""
        self.gui_parent.root.after(0, lambda: self.gui_parent.update_config(config_dict))
            
    def clear_console(self):
        """Clear the console."""
        self.gui_parent.root.after(0, self.gui_parent.clear_console)
        
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
        self.root.geometry("900x700")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Set up GUI first
        self.setup_gui()
        
        # Create operator interface
        self.operator_interface = TkinterOperatorInterface(self)
        
        # Add initial message
        self.append_to_console("GUI Started - Initializing station...", "blue")
        
        # Initialize station in background after GUI is ready
        self.root.after(100, self.initialize_station_async)
        
    def setup_gui(self):
        """Set up the GUI layout."""
        # Configure root grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main frame grid
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Factory Test Station", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="ew")
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        control_frame.columnconfigure(1, weight=1)
        
        # Serial number input
        ttk.Label(control_frame, text="Serial Number:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.serial_entry = ttk.Entry(control_frame, width=25, font=("Arial", 12))
        self.serial_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.serial_entry.bind('<Return>', self.on_start_test)
        
        # Start test button
        self.start_button = ttk.Button(control_frame, text="Start Test", command=self.on_start_test)
        self.start_button.grid(row=0, column=2)
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        status_frame.columnconfigure(0, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Starting...")
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, padding="5", background="lightgray")
        status_bar.grid(row=0, column=0, sticky="ew")
        
        # Test result
        self.result_var = tk.StringVar()
        self.result_label = ttk.Label(status_frame, textvariable=self.result_var, 
                                     font=("Arial", 14, "bold"))
        self.result_label.grid(row=0, column=1, padx=(10, 0))
        
        # Console frame
        console_frame = ttk.LabelFrame(main_frame, text="Console Output", padding="5")
        console_frame.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=(0, 10))
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        
        # Console text with scrollbar
        self.console_text = scrolledtext.ScrolledText(
            console_frame, 
            height=20, 
            width=80,
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.console_text.grid(row=0, column=0, sticky="nsew")
        
        # Configure console colors
        self.console_text.tag_config("red", foreground="red")
        self.console_text.tag_config("green", foreground="green") 
        self.console_text.tag_config("blue", foreground="blue")
        self.console_text.tag_config("yellow", foreground="orange")
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, sticky="ew")
        
        # Clear button
        ttk.Button(button_frame, text="Clear Console", 
                  command=self.clear_console).grid(row=0, column=0, padx=(0, 10))
        
        # Exit button  
        ttk.Button(button_frame, text="Exit", 
                  command=self.on_closing).grid(row=0, column=1)
    
    def initialize_station_async(self):
        """Initialize station in background thread."""
        def init_worker():
            try:
                self.append_to_console("Loading station configuration...", "blue")
                
                # Load station configuration
                station_config.load_station('project_station')
                
                self.append_to_console("Creating station instance...", "blue")
                
                # Create station instance
                self.station = self.test_station_class(self.station_config, self.operator_interface)
                
                self.append_to_console("Initializing station hardware...", "blue")
                
                # Initialize the station
                self.station.initialize()
                
                self.append_to_console("Station initialization complete!", "green")
                
                # Update GUI on main thread
                self.root.after(0, lambda: self.set_status("Ready - Enter serial number to start test"))
                self.root.after(0, lambda: self.start_button.config(state="normal"))
                self.root.after(0, lambda: self.serial_entry.focus())
                
            except Exception as e:
                error_msg = f"Failed to initialize station: {str(e)}"
                self.root.after(0, lambda: self.append_to_console(error_msg, "red"))
                self.root.after(0, lambda: self.set_status(f"Error: {str(e)}"))
                print(f"Station initialization error: {e}")
                traceback.print_exc()
        
        # Disable start button during initialization
        self.start_button.config(state="disabled")
        
        # Start initialization in background
        init_thread = threading.Thread(target=init_worker, daemon=True)
        init_thread.start()
    
    def append_to_console(self, message, color=None):
        """Append message to console with optional color."""
        if not message:
            return
            
        timestamp = time.strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}\n"
        
        # Insert text
        self.console_text.insert(tk.END, formatted_msg)
        
        # Apply color if specified
        if color and color in ["red", "green", "blue", "yellow"]:
            # Get the position of the inserted text
            line_start = self.console_text.index(f"{tk.END}-1c linestart")
            line_end = self.console_text.index(f"{tk.END}-1c")
            self.console_text.tag_add(color, line_start, line_end)
        
        # Auto-scroll to bottom
        self.console_text.see(tk.END)
        
        # Force update
        self.root.update_idletasks()
    
    def set_status(self, message):
        """Set status bar message."""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def clear_console(self):
        """Clear the console."""
        self.console_text.delete(1.0, tk.END)
        self.append_to_console("Console cleared")
    
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
            
        if not self.station:
            self.append_to_console("Station not initialized!", "red")
            return
            
        serial_number = self.serial_entry.get().strip()
        if not serial_number:
            messagebox.showerror("Error", "Please enter a serial number")
            self.serial_entry.focus()
            return
        
        # Clear previous results
        self.result_var.set("")
        
        # Disable controls
        self.start_button.config(state="disabled")
        self.serial_entry.config(state="disabled")
        self.is_testing = True
        self.set_status("Testing in progress...")
        
        # Start test in background thread
        self.testing_thread = threading.Thread(target=self.run_test, args=(serial_number,), daemon=True)
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
            traceback.print_exc()
        finally:
            # Re-enable controls on main thread
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
        
        self.append_to_console("Shutting down station...", "blue")
        
        if self.station:
            try:
                self.station.close()
                self.append_to_console("Station closed successfully", "green")
            except Exception as e:
                self.append_to_console(f"Error closing station: {e}", "red")
        
        self.root.quit()
        self.root.destroy()
    
    def main_loop(self):
        """Start the GUI main loop."""
        try:
            # Show window and start main loop
            self.root.deiconify()  # Ensure window is visible
            self.root.lift()       # Bring to front
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
        except Exception as e:
            print(f"GUI Error: {e}")
            traceback.print_exc()


def main():
    """Main entry point for GUI."""
    try:
        print("Starting tkinter GUI...")
        
        # Create and start GUI
        gui = FactoryTestTkinterGUI(station_config, test_station.projectstationStation)
        gui.main_loop()
        
    except Exception as e:
        print(f"Failed to start GUI: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()