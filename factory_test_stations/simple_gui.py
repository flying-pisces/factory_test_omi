#!/usr/bin/env python3
"""
Simple cross-platform GUI for factory test stations using tkinter.
This version avoids all CLR/Windows dependencies by directly using the console test runner.
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
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Factory Test Station - Simple GUI")
        self.root.geometry("900x700")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_gui()
        
        # Add initial message
        self.append_to_console("Simple GUI Started", "blue")
        self.append_to_console(f"Platform: {platform.system()}", "blue")
        self.append_to_console(f"Python: {self.python_path}", "blue")
        self.set_status("Ready - Enter serial number to start test")
        
    def setup_gui(self):
        """Set up the GUI layout."""
        # Configure root grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure main frame grid - fix column configuration
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Factory Test Station - Simple GUI", 
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
        self.serial_entry.focus()
        
        # Start test button
        self.start_button = ttk.Button(control_frame, text="Start Test", command=self.on_start_test)
        self.start_button.grid(row=0, column=2)
        
        # Status frame
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        status_frame.columnconfigure(0, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(status_frame, textvariable=self.status_var, 
                             relief=tk.SUNKEN, bg="lightgray", padx=5, pady=2)
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
        
        # Test with example button
        ttk.Button(button_frame, text="Test Example", 
                  command=self.test_example).grid(row=0, column=1, padx=(0, 10))
        
        # Exit button  
        ttk.Button(button_frame, text="Exit", 
                  command=self.on_closing).grid(row=0, column=2)
    
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
    
    def test_example(self):
        """Run test with example serial number."""
        self.serial_entry.delete(0, tk.END)
        self.serial_entry.insert(0, "GUI123456789")
        self.on_start_test()
    
    def on_start_test(self, event=None):
        """Start test button handler."""
        if self.is_testing:
            self.append_to_console("Test already in progress!", "yellow")
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
            
            # Run the console test runner
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read output line by line
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
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
                self.output_queue.put(("log", "Test completed successfully!", "green"))
            else:
                self.output_queue.put(("result", "FAIL"))
                self.output_queue.put(("log", f"Test failed with return code: {return_code}", "red"))
                
        except Exception as e:
            self.output_queue.put(("log", f"Test failed with exception: {str(e)}", "red"))
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
                            self.result_label.config(foreground="green")
                        else:
                            self.result_var.set("✗ FAIL")
                            self.result_label.config(foreground="red")
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