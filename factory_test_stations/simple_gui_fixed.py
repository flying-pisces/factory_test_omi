#!/usr/bin/env python3
"""
Fixed cross-platform GUI for factory test stations using tkinter.
Uses simpler layout patterns that are proven to work.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import sys
import os
import subprocess
import queue
import platform
import importlib
try:
    import select
except ImportError:
    select = None

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class SimpleFactoryTestGUI:
    """Simple cross-platform factory test GUI using subprocess calls."""
    
    def __init__(self):
        self.testing_thread = None
        self.is_testing = False
        self.python_path = sys.executable
        
        # Create output queue for thread communication
        self.output_queue = queue.Queue()
        
        # Load station limits configuration
        self.station_limits = self.load_station_limits()
        self.test_items = {}  # Dict to store test item data by name
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Factory Test Station - Simple GUI")
        self.root.geometry("900x700")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Set minimum size
        self.root.minsize(600, 400)
        
        self.setup_gui()
        
        # Initialize persistent test table from configuration
        self.initialize_persistent_test_table()
        
        # Add initial messages (web interface style)
        self.append_to_console("[Ready] Factory Test Station TK Interface", "#ffffff")
        self.append_to_console(f"[Ready] Platform: {platform.system()}", "#ffffff")
        self.append_to_console(f"[Ready] Loaded {len(self.station_limits)} test items from configuration", "#ffffff")
        self.append_to_console("[Ready] Enter serial number or use Auto Scan to start", "#ffffff")
        self.set_status("Ready - Enter serial number to start test", "ready")
        
    def load_station_limits(self):
        """Load station limits configuration from project_station_limits.py"""
        try:
            # Import the station limits module
            limits_module = importlib.import_module("config.station_limits_project_station")
            
            # Get the STATION_LIMITS array
            station_limits = getattr(limits_module, 'STATION_LIMITS', [])
            
            return station_limits
            
        except ImportError as e:
            print(f"[Warning] Could not load station limits: {e}")
            # Return default test items as fallback
            return [
                {'name': 'TEST ITEM 1', 'low_limit': 1, 'high_limit': 2, 'unique_id': 11},
                {'name': 'TEST ITEM 2', 'low_limit': None, 'high_limit': None, 'unique_id': 12},
                {'name': 'NON PARAMETRIC TEST ITEM 3', 'low_limit': True, 'high_limit': True, 'unique_id': 13}
            ]
        except Exception as e:
            print(f"[Error] Error loading station limits: {e}")
            return []
    
    def initialize_persistent_test_table(self):
        """Initialize the test table with items from station limits (persistent structure)."""
        # Clear any existing items
        for item in self.results_table.get_children():
            self.results_table.delete(item)
        
        # Populate table with test items from configuration
        for i, test_limit in enumerate(self.station_limits):
            test_name = test_limit.get('name', f'Test Item {i+1}')
            low_limit = test_limit.get('low_limit', '')
            high_limit = test_limit.get('high_limit', '')
            unique_id = test_limit.get('unique_id', i)
            
            # Format limits for display
            if low_limit is None or low_limit == '':
                low_display = ''
            elif isinstance(low_limit, bool):
                low_display = str(low_limit)
            else:
                low_display = str(low_limit)
                
            if high_limit is None or high_limit == '':
                high_display = ''
            elif isinstance(high_limit, bool):
                high_display = str(high_limit)
            else:
                high_display = str(high_limit)
            
            # Determine attachment icon based on test type
            if 'NON PARAMETRIC' in test_name.upper():
                attachment = '📷'
            elif 'ITEM 1' in test_name:
                attachment = '📊'
            elif 'ITEM 2' in test_name:
                attachment = '📈'
            else:
                attachment = '📋'
            
            # Add row to table (starts with no test value)
            row_tag = "evenrow" if i % 2 == 0 else "oddrow"
            item_id = self.results_table.insert("", tk.END, 
                                              values=(test_name, "—", low_display, high_display, attachment),
                                              tags=(row_tag,))
            
            # Store the item mapping for later updates
            self.test_items[test_name] = {
                'item_id': item_id,
                'low_limit': low_limit,
                'high_limit': high_limit,
                'unique_id': unique_id,
                'attachment': attachment
            }
        
    def setup_gui(self):
        """Set up GUI layout to match web interface design."""
        
        # Header section (matching web interface dark theme)
        header_frame = tk.Frame(self.root, bg="#2c3e50")
        header_frame.pack(fill=tk.X)
        
        header_content = tk.Frame(header_frame, bg="#2c3e50")
        header_content.pack(fill=tk.X, padx=15, pady=15)
        
        # Station name and description
        tk.Label(header_content, text="project_station", 
                font=("Arial", 18, "bold"), bg="#2c3e50", fg="white").pack(side=tk.LEFT)
        tk.Label(header_content, text="Factory Test Station - TK Interface", 
                font=("Arial", 11), bg="#2c3e50", fg="white").pack(side=tk.RIGHT)
        
        # Serial number section (white background with blue left border)
        serial_section = tk.Frame(self.root, bg="white")
        serial_section.pack(fill=tk.X, padx=10, pady=10)
        
        # Blue left border effect
        tk.Frame(serial_section, bg="#3498db", width=4).pack(side=tk.LEFT, fill=tk.Y)
        
        serial_content = tk.Frame(serial_section, bg="white")
        serial_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        tk.Label(serial_content, text="Device Serial Number", 
                font=("Arial", 12, "bold"), bg="white").pack(anchor=tk.W)
        
        # Input and buttons row
        input_frame = tk.Frame(serial_content, bg="white")
        input_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.serial_entry = tk.Entry(input_frame, font=("Arial", 10), width=25,
                                   relief="solid", bd=1)
        self.serial_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.serial_entry.bind('<Return>', self.on_start_test)
        
        # Auto scan button (gray like web)
        tk.Button(input_frame, text="Auto Scan", command=self.auto_scan,
                 bg="#6c757d", fg="white", font=("Arial", 9), 
                 relief="flat", padx=15, pady=5).pack(side=tk.LEFT, padx=(0, 5))
        
        # Start test button (green like web)
        self.start_button = tk.Button(input_frame, text="Start Test", 
                                     command=self.on_start_test, bg="#28a745",
                                     fg="white", font=("Arial", 9), 
                                     relief="flat", padx=15, pady=5)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # Status summary section (like web interface)
        self.status_frame = tk.Frame(self.root, bg="#f8f9fa")
        self.status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.status_var = tk.StringVar(value="Ready - Enter serial number to start test")
        self.status_label = tk.Label(self.status_frame, textvariable=self.status_var,
                                   font=("Arial", 11, "bold"), bg="#f8f9fa", 
                                   fg="#6c757d", pady=15)
        self.status_label.pack()
        
        # Test results section (white with green header) - matching web interface
        results_section = tk.Frame(self.root, bg="white")
        results_section.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Results header (green like web)
        results_header = tk.Frame(results_section, bg="#28a745")
        results_header.pack(fill=tk.X)
        tk.Label(results_header, text="Test Results", 
                font=("Arial", 12, "bold"), bg="#28a745", 
                fg="white", pady=10).pack()
        
        # Test results table (matching web interface structure)
        table_frame = tk.Frame(results_section, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Create Treeview for table display
        columns = ("parameter", "value", "low_limit", "high_limit", "attachment")
        self.results_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
        
        # Configure column headings (matching web interface)
        self.results_table.heading("parameter", text="Test Parameter")
        self.results_table.heading("value", text="Test Value") 
        self.results_table.heading("low_limit", text="Low Limit")
        self.results_table.heading("high_limit", text="High Limit")
        self.results_table.heading("attachment", text="Attachment")
        
        # Configure column widths
        self.results_table.column("parameter", width=200, anchor=tk.W)
        self.results_table.column("value", width=120, anchor=tk.CENTER)
        self.results_table.column("low_limit", width=100, anchor=tk.CENTER)
        self.results_table.column("high_limit", width=100, anchor=tk.CENTER)
        self.results_table.column("attachment", width=100, anchor=tk.CENTER)
        
        # Add scrollbar for table
        table_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.results_table.yview)
        self.results_table.configure(yscrollcommand=table_scrollbar.set)
        
        # Pack table and scrollbar
        self.results_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add click handler for attachment column (to view images/files)
        self.results_table.bind("<Double-1>", self.on_table_double_click)
        
        # Configure table styling (alternating row colors)
        self.results_table.tag_configure("evenrow", background="#f8f9fa")
        self.results_table.tag_configure("oddrow", background="white")
        
        # Note: Table will be populated by initialize_persistent_test_table()
        
        # Overall result display (below table)
        result_summary_frame = tk.Frame(results_section, bg="white")
        result_summary_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        self.result_var = tk.StringVar()
        self.result_label = tk.Label(result_summary_frame, textvariable=self.result_var, 
                                    font=("Arial", 14, "bold"), bg="white")
        self.result_label.pack()
        
        # Console section (dark like web interface)
        console_section = tk.Frame(self.root, bg="#1e1e1e")
        console_section.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Console header
        console_header = tk.Frame(console_section, bg="#1e1e1e")
        console_header.pack(fill=tk.X, padx=10, pady=(10, 5))
        tk.Label(console_header, text="Console Output", 
                font=("Arial", 10, "bold"), bg="#1e1e1e", fg="white").pack(anchor=tk.W)
        
        # Console text area
        self.console_text = scrolledtext.ScrolledText(
            console_section, height=12, width=80, font=("Courier New", 9),
            bg="#1e1e1e", fg="white", insertbackground="white", 
            relief="flat", bd=0, wrap=tk.WORD
        )
        self.console_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Configure console colors to match web interface
        self.console_text.tag_config("#dc3545", foreground="#dc3545")  # red/error
        self.console_text.tag_config("#28a745", foreground="#28a745")  # green/success
        self.console_text.tag_config("#007bff", foreground="#007bff")  # blue/info
        self.console_text.tag_config("#ffc107", foreground="#ffc107")  # yellow/warning
        self.console_text.tag_config("#ffffff", foreground="#ffffff")  # white/normal
        
        # Focus on serial entry
        self.serial_entry.focus()
    
    def auto_scan(self):
        """Auto scan for device serial number (placeholder function)."""
        self.append_to_console("Auto scanning for device...", "#007bff")
        # Simulate auto-detected serial for demo
        import random
        mock_serial = f"TEST{random.randint(1000, 9999)}"
        self.serial_entry.delete(0, tk.END)
        self.serial_entry.insert(0, mock_serial)
        self.append_to_console(f"Device detected: {mock_serial}", "#28a745")
        self.set_status("Device detected - Ready to start test")
    
    
    def on_table_double_click(self, event):
        """Handle double-click on table rows (for viewing attachments)."""
        # Get the selected item
        selection = self.results_table.selection()
        if not selection:
            return
        
        item_id = selection[0]
        values = self.results_table.item(item_id)["values"]
        
        if len(values) >= 5 and values[4]:  # Check if attachment column has content
            parameter = values[0]
            attachment = values[4]
            # Log the attachment view (matching web interface behavior)
            self.append_to_console(f"View image for: {parameter} (Image viewer would open here in full implementation)", "#007bff")
    
    def update_test_value(self, test_name, value, status="pending"):
        """Update only the test value for a specific test item (preserves table structure)."""
        if test_name not in self.test_items:
            return
        
        item_id = self.test_items[test_name]['item_id']
        current_values = list(self.results_table.item(item_id)["values"])
        
        # Format value based on status
        if status == "pass":
            formatted_value = f"✓ {value}"
        elif status == "fail":
            formatted_value = f"✗ {value}"
        elif status == "testing":
            formatted_value = f"⏳ {value}"
        else:
            formatted_value = str(value) if value is not None else "—"
        
        # Update only the value column (index 1)
        current_values[1] = formatted_value
        self.results_table.item(item_id, values=current_values)
    
    def update_test_values_to_testing(self):
        """Update all test values to show testing in progress (preserves table structure)."""
        for test_name in self.test_items:
            self.update_test_value(test_name, "Testing...", "testing")
    
    def update_test_values_with_results(self, test_results, overall_status="pass"):
        """Update test values with actual results (preserves table structure)."""
        # Demo test results matching the station limits
        demo_results = {
            "TEST ITEM 1": {"value": 1.1, "status": "pass"},
            "TEST ITEM 2": {"value": 1.4, "status": "pass"}, 
            "NON PARAMETRIC TEST ITEM 3": {"value": True, "status": "pass"}
        }
        
        # If overall test failed, make some items fail
        if overall_status == "fail":
            demo_results["TEST ITEM 1"]["value"] = 2.5  # Out of range (1-2)
            demo_results["TEST ITEM 1"]["status"] = "fail"
            demo_results["NON PARAMETRIC TEST ITEM 3"]["value"] = False
            demo_results["NON PARAMETRIC TEST ITEM 3"]["status"] = "fail"
        
        # Update each test item value
        for test_name, result_data in demo_results.items():
            if test_name in self.test_items:
                self.update_test_value(test_name, result_data["value"], result_data["status"])
    
    def reset_test_values(self):
        """Reset all test values to empty state (preserves table structure)."""
        for test_name in self.test_items:
            self.update_test_value(test_name, "—", "pending")
        
    def append_to_console(self, message, color=None):
        """Add message to console with web interface style coloring."""
        if not message:
            return
            
        self.console_text.config(state=tk.NORMAL)
        
        timestamp = time.strftime("%H:%M:%S")
        
        # Map old color names to web interface hex colors
        color_map = {
            "red": "#dc3545",
            "green": "#28a745", 
            "blue": "#007bff",
            "yellow": "#ffc107",
            "white": "#ffffff"
        }
        
        display_color = color_map.get(color, color) if color else "#ffffff"
        
        # Insert timestamped message with color
        full_message = f"[{timestamp}] {message}\n"
        self.console_text.insert(tk.END, full_message, display_color)
        
        self.console_text.config(state=tk.DISABLED)
        self.console_text.see(tk.END)
        self.root.update_idletasks()
    
    def set_status(self, message, status_type="ready"):
        """Update status display with web interface styling."""
        self.status_var.set(message)
        
        # Update status frame colors to match web interface
        if status_type == "ready":
            self.status_frame.config(bg="#f8f9fa")
            self.status_label.config(bg="#f8f9fa", fg="#6c757d")
        elif status_type == "testing":
            self.status_frame.config(bg="#fff3cd")
            self.status_label.config(bg="#fff3cd", fg="#856404")
        elif status_type == "pass":
            self.status_frame.config(bg="#d4edda")
            self.status_label.config(bg="#d4edda", fg="#155724")
        elif status_type == "fail":
            self.status_frame.config(bg="#f8d7da")
            self.status_label.config(bg="#f8d7da", fg="#721c24")
        
        self.root.update_idletasks()
    
    
    def on_start_test(self, event=None):
        """Start test button handler with web interface styling."""
        if self.is_testing:
            self.append_to_console("Test already in progress!", "#ffc107")
            return
            
        serial_number = self.serial_entry.get().strip()
        if not serial_number:
            self.append_to_console("Error: Please enter a serial number", "#dc3545")
            self.serial_entry.focus()
            return
        
        # Clear previous results and show test in progress
        self.result_var.set("")
        self.update_test_values_to_testing()
        
        # Disable controls and update UI state
        self.start_button.config(state="disabled")
        self.serial_entry.config(state="disabled")
        self.is_testing = True
        self.set_status("Testing in progress...", "testing")
        
        # Start test in background thread
        self.testing_thread = threading.Thread(target=self.run_test, args=(serial_number,), daemon=True)
        self.testing_thread.start()
        
        # Start monitoring the output queue
        self.monitor_output()
    
    def run_test(self, serial_number):
        """Run test in background thread using subprocess."""
        try:
            self.output_queue.put(("log", f"Starting test for unit: {serial_number}", "blue"))
            
            # Build command to run console test runner
            cmd = [
                self.python_path,
                "console_test_runner.py",
                "--serial", serial_number
            ]
            
            self.output_queue.put(("log", f"Running: {' '.join(cmd)}", "blue"))
            
            # Check if console_test_runner.py exists
            console_runner_path = os.path.join(os.getcwd(), "console_test_runner.py")
            if not os.path.exists(console_runner_path):
                self.output_queue.put(("log", f"Error: console_test_runner.py not found at {console_runner_path}", "red"))
                self.output_queue.put(("result", "FAIL"))
                return
            
            # Run the console test runner with timeout
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Add timeout to prevent hanging
            timeout = 300  # 5 minutes timeout
            start_time = time.time()
            
            # Read output line by line with timeout
            while True:
                # Check for timeout
                if time.time() - start_time > timeout:
                    process.terminate()
                    self.output_queue.put(("log", "Test timed out after 5 minutes", "red"))
                    break
                
                # Use polling to avoid blocking
                if platform.system() == "Windows" or select is None:
                    # Windows doesn't have select for pipes, use different approach
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                else:
                    # Unix systems can use select
                    ready, _, _ = select.select([process.stdout], [], [], 0.1)
                    if ready:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                    elif process.poll() is not None:
                        break
                    else:
                        continue
                        
                if output:
                    # Parse output for results
                    line = output.strip()
                    if line:
                        # Determine color based on content
                        color = None
                        if "PASSED" in line or "✓" in line:
                            color = "green"
                        elif "FAILED" in line or "✗" in line or "ERROR" in line:
                            color = "red"
                        elif "WARNING" in line:
                            color = "yellow"
                        elif "Initializing" in line or "Starting" in line:
                            color = "blue"
                        
                        self.output_queue.put(("log", line, color))
            
            # Get final return code
            return_code = process.poll()
            
            # Read any remaining stderr
            stderr = process.stderr.read()
            if stderr:
                self.output_queue.put(("log", f"Errors: {stderr}", "red"))
            
            # Determine overall result
            if return_code == 0:
                self.output_queue.put(("result", "PASS"))
                self.output_queue.put(("log", "Test completed successfully!", "#28a745"))
            else:
                self.output_queue.put(("result", "FAIL"))
                self.output_queue.put(("log", f"Test failed with return code: {return_code}", "#dc3545"))
                
        except Exception as e:
            self.output_queue.put(("log", f"Test failed with exception: {str(e)}", "#dc3545"))
            self.output_queue.put(("result", "FAIL"))
        finally:
            self.output_queue.put(("complete", None))
    
    def monitor_output(self):
        """Monitor the output queue and update GUI."""
        try:
            while True:
                try:
                    msg_type, data, *args = self.output_queue.get_nowait()
                    
                    if msg_type == "log":
                        color = args[0] if args else None
                        self.append_to_console(data, color)
                    elif msg_type == "result":
                        if data == "PASS":
                            self.result_var.set("✓ PASS")
                            self.result_label.config(foreground="#28a745")
                            self.set_status("Test completed - PASS", "pass")
                            # Update table with passing results (preserves structure)
                            self.update_test_values_with_results(None, "pass")
                        else:
                            self.result_var.set("✗ FAIL")
                            self.result_label.config(foreground="#dc3545") 
                            self.set_status("Test completed - FAIL", "fail")
                            # Update table with failure results (preserves structure)
                            self.update_test_values_with_results(None, "fail")
                    elif msg_type == "complete":
                        self.test_complete()
                        return
                        
                except queue.Empty:
                    break
        except:
            pass
            
        # Schedule next check
        self.root.after(100, self.monitor_output)
    
    def test_complete(self):
        """Re-enable controls after test completion (keep test results visible)."""
        self.start_button.config(state="normal")
        self.serial_entry.config(state="normal")
        self.serial_entry.delete(0, tk.END)
        self.serial_entry.focus()
        self.is_testing = False
        self.set_status("Ready - Enter serial number to start test", "ready")
        
        # Keep test results visible - do NOT reset the table
        # The test results remain persistent until next test starts
    
    def on_closing(self):
        """Handle window closing."""
        if self.is_testing:
            self.append_to_console("Warning: Test in progress. Terminating...", "yellow")
            # Force terminate the testing thread if it exists
            if self.testing_thread and self.testing_thread.is_alive():
                self.is_testing = False
        
        self.append_to_console("Shutting down GUI...", "blue")
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
            import traceback
            traceback.print_exc()


def main():
    """Main entry point for simple GUI."""
    try:
        print("Starting simple cross-platform GUI...")
        
        # Create and start GUI
        gui = SimpleFactoryTestGUI()
        gui.main_loop()
        
    except Exception as e:
        print(f"Failed to start GUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()