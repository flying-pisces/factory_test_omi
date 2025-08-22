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
        
        # Set minimum size
        self.root.minsize(600, 400)
        
        self.setup_gui()
        
        # Add initial message
        self.append_to_console("Simple GUI Started", "blue")
        self.append_to_console(f"Platform: {platform.system()}", "blue")
        self.append_to_console(f"Python: {self.python_path}", "blue")
        self.set_status("Ready - Enter serial number to start test")
        
    def setup_gui(self):
        """Set up the GUI layout using pack manager for simplicity."""
        
        # Title at top
        title_frame = tk.Frame(self.root, bg="lightblue")
        title_frame.pack(fill=tk.X, pady=5)
        
        title_label = tk.Label(title_frame, text="Factory Test Station - Simple GUI", 
                              font=("Arial", 18, "bold"), bg="lightblue")
        title_label.pack(pady=10)
        
        # Control panel
        control_frame = tk.Frame(self.root, bg="lightgray")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Serial number input
        serial_frame = tk.Frame(control_frame, bg="lightgray")
        serial_frame.pack(pady=10)
        
        tk.Label(serial_frame, text="Serial Number:", font=("Arial", 12), 
                bg="lightgray").pack(side=tk.LEFT, padx=5)
        
        self.serial_entry = tk.Entry(serial_frame, width=25, font=("Arial", 12))
        self.serial_entry.pack(side=tk.LEFT, padx=5)
        self.serial_entry.bind('<Return>', self.on_start_test)
        
        # Start test button
        self.start_button = tk.Button(serial_frame, text="Start Test", 
                                     command=self.on_start_test, bg="lightgreen", 
                                     font=("Arial", 10, "bold"))
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        # Button row
        button_frame = tk.Frame(control_frame, bg="lightgray")
        button_frame.pack(pady=5)
        
        tk.Button(button_frame, text="Clear Console", 
                 command=self.clear_console, bg="yellow").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Test Example", 
                 command=self.test_example, bg="orange").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Exit", 
                 command=self.on_closing, bg="red", fg="white").pack(side=tk.LEFT, padx=5)
        
        # Status area
        status_frame = tk.Frame(self.root, bg="white")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(status_frame, textvariable=self.status_var, 
                             relief=tk.SUNKEN, bg="lightgray", anchor=tk.W, padx=5)
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Test result
        self.result_var = tk.StringVar()
        self.result_label = tk.Label(status_frame, textvariable=self.result_var, 
                                    font=("Arial", 14, "bold"), bg="white")
        self.result_label.pack(side=tk.RIGHT, padx=10)
        
        # Console area
        console_frame = tk.Frame(self.root)
        console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Console label
        console_label = tk.Label(console_frame, text="Console Output:", 
                                font=("Arial", 12, "bold"), anchor=tk.W)
        console_label.pack(fill=tk.X)
        
        # Console text with scrollbar
        self.console_text = scrolledtext.ScrolledText(
            console_frame, 
            height=20, 
            width=80,
            font=("Consolas", 10),
            wrap=tk.WORD,
            bg="black",
            fg="white"
        )
        self.console_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure console colors
        self.console_text.tag_config("red", foreground="red")
        self.console_text.tag_config("green", foreground="lightgreen") 
        self.console_text.tag_config("blue", foreground="lightblue")
        self.console_text.tag_config("yellow", foreground="yellow")
        
        # Focus on serial entry
        self.serial_entry.focus()
        
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