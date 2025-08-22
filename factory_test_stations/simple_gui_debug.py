#!/usr/bin/env python3
"""
Debug version of simple GUI using patterns from working debug_gui.py
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


class SimpleFactoryTestGUIDebug:
    """Simplified version for debugging blank GUI issue."""
    
    def __init__(self):
        self.testing_thread = None
        self.is_testing = False
        self.python_path = sys.executable
        
        # Create output queue for thread communication
        self.output_queue = queue.Queue()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Factory Test Station - Debug GUI")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.setup_gui_simple()
        
        print("GUI initialized successfully")
        
    def setup_gui_simple(self):
        """Simple GUI setup using pack manager like debug_gui.py"""
        
        # Title
        title_label = tk.Label(self.root, text="Factory Test Station - Debug", 
                              font=("Arial", 18, "bold"))
        title_label.pack(pady=20)
        
        # Serial number frame
        serial_frame = tk.Frame(self.root)
        serial_frame.pack(pady=10)
        
        tk.Label(serial_frame, text="Serial Number:").pack(side=tk.LEFT, padx=5)
        self.serial_entry = tk.Entry(serial_frame, width=25, font=("Arial", 12))
        self.serial_entry.pack(side=tk.LEFT, padx=5)
        
        # Start button
        self.start_button = tk.Button(serial_frame, text="Start Test", 
                                     command=self.on_start_test, bg="lightgreen")
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        # Status
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Enter serial number to start test")
        status_label = tk.Label(self.root, textvariable=self.status_var, 
                               relief=tk.SUNKEN, bg="lightgray")
        status_label.pack(fill=tk.X, padx=10, pady=5)
        
        # Result
        self.result_var = tk.StringVar()
        self.result_label = tk.Label(self.root, textvariable=self.result_var, 
                                    font=("Arial", 14, "bold"))
        self.result_label.pack(pady=5)
        
        # Console
        console_label = tk.Label(self.root, text="Console Output:", font=("Arial", 12, "bold"))
        console_label.pack(anchor=tk.W, padx=10)
        
        self.console_text = scrolledtext.ScrolledText(
            self.root, 
            height=15, 
            width=80,
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.console_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Configure console colors
        self.console_text.tag_config("red", foreground="red")
        self.console_text.tag_config("green", foreground="green") 
        self.console_text.tag_config("blue", foreground="blue")
        self.console_text.tag_config("yellow", foreground="orange")
        
        # Button frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Clear Console", 
                 command=self.clear_console).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Test Example", 
                 command=self.test_example).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Exit", 
                 command=self.on_closing).pack(side=tk.LEFT, padx=5)
        
        # Add initial messages
        self.append_to_console("Debug GUI Started", "blue")
        self.append_to_console(f"Platform: {platform.system()}", "blue")
        self.append_to_console(f"Python: {self.python_path}", "blue")
        
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
    
    def clear_console(self):
        """Clear the console."""
        self.console_text.delete(1.0, tk.END)
        self.append_to_console("Console cleared")
    
    def test_example(self):
        """Run test with example serial number."""
        self.serial_entry.delete(0, tk.END)
        self.serial_entry.insert(0, "DEBUG123456789")
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
        
        # Simulate a simple test
        self.append_to_console(f"Starting test for: {serial_number}", "blue")
        self.append_to_console("Simulating test execution...", "blue")
        self.append_to_console("Test step 1: PASSED", "green")
        self.append_to_console("Test step 2: PASSED", "green") 
        self.append_to_console("Test step 3: PASSED", "green")
        self.append_to_console("Overall result: PASS", "green")
        
        # Show result
        self.result_var.set("✓ PASS")
        self.result_label.config(foreground="green")
        self.status_var.set("Test completed successfully")
        
        # Clear serial entry
        self.serial_entry.delete(0, tk.END)
        self.serial_entry.focus()
    
    def on_closing(self):
        """Handle window closing."""
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
    """Main entry point for debug GUI."""
    try:
        print("Starting debug GUI...")
        
        # Create and start GUI
        gui = SimpleFactoryTestGUIDebug()
        gui.main_loop()
        
    except Exception as e:
        print(f"Failed to start debug GUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()