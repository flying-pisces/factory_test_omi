#!/usr/bin/env python3
"""
Minimal tkinter test to debug blank GUI issue
"""

import tkinter as tk
from tkinter import ttk
import sys

def test_basic_tk():
    """Test basic tk widgets"""
    print("Testing basic tk widgets...")
    root = tk.Tk()
    root.title("Basic TK Test")
    root.geometry("400x300")
    
    # Add basic label
    label = tk.Label(root, text="Basic TK Label - Can you see this?", 
                    font=("Arial", 16), bg="yellow", fg="black")
    label.pack(pady=20)
    
    # Add button
    button = tk.Button(root, text="Close", command=root.quit, bg="red", fg="white")
    button.pack(pady=10)
    
    print("Basic TK widgets created, starting mainloop...")
    root.mainloop()
    print("Basic TK test completed")

def test_ttk_widgets():
    """Test ttk widgets"""
    print("Testing ttk widgets...")
    root = tk.Tk()
    root.title("TTK Test")
    root.geometry("400x300")
    
    # Main frame
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # TTK label
    label = ttk.Label(main_frame, text="TTK Label - Can you see this?", 
                     font=("Arial", 16))
    label.pack(pady=20)
    
    # TTK button
    button = ttk.Button(main_frame, text="Close", command=root.quit)
    button.pack(pady=10)
    
    print("TTK widgets created, starting mainloop...")
    root.mainloop()
    print("TTK test completed")

def test_grid_layout():
    """Test grid layout"""
    print("Testing grid layout...")
    root = tk.Tk()
    root.title("Grid Test")
    root.geometry("500x400")
    
    # Configure root
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    # Main frame
    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky="nsew")
    
    # Configure main frame
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(2, weight=1)
    
    # Title
    title = ttk.Label(main_frame, text="Grid Layout Test", font=("Arial", 16))
    title.grid(row=0, column=0, columnspan=2, pady=10)
    
    # Entry
    ttk.Label(main_frame, text="Test:").grid(row=1, column=0, sticky="w")
    entry = ttk.Entry(main_frame, width=20)
    entry.grid(row=1, column=1, sticky="ew", padx=5)
    
    # Text area
    text = tk.Text(main_frame, height=10, width=40)
    text.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)
    text.insert(tk.END, "This is a text area.\nCan you see this text?")
    
    # Button
    button = ttk.Button(main_frame, text="Close", command=root.quit)
    button.grid(row=3, column=0, columnspan=2, pady=5)
    
    print("Grid layout created, starting mainloop...")
    root.mainloop()
    print("Grid test completed")

if __name__ == "__main__":
    print("Starting minimal tkinter tests...")
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        if test_type == "tk":
            test_basic_tk()
        elif test_type == "ttk":
            test_ttk_widgets()
        elif test_type == "grid":
            test_grid_layout()
        else:
            print("Usage: python minimal_test.py [tk|ttk|grid]")
    else:
        print("Running all tests...")
        test_basic_tk()
        test_ttk_widgets()
        test_grid_layout()