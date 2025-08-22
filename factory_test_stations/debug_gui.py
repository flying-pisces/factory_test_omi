#!/usr/bin/env python3
"""
Debug GUI to test tkinter step by step
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import traceback

def test_basic_window():
    """Test 1: Basic window"""
    print("Test 1: Creating basic window...")
    root = tk.Tk()
    root.title("Debug Test 1 - Basic Window")
    root.geometry("400x300")
    
    label = tk.Label(root, text="Basic Window Test", font=("Arial", 16))
    label.pack(pady=20)
    
    def close_test():
        print("Basic window test completed")
        root.quit()
        root.destroy()
    
    button = tk.Button(root, text="Close Test 1", command=close_test)
    button.pack(pady=10)
    
    root.after(5000, close_test)  # Auto close after 5 seconds
    root.mainloop()

def test_grid_layout():
    """Test 2: Grid layout"""
    print("Test 2: Creating grid layout...")
    root = tk.Tk()
    root.title("Debug Test 2 - Grid Layout")
    root.geometry("500x400")
    
    # Configure grid
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    # Main frame
    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky="nsew")
    main_frame.columnconfigure(1, weight=1)
    
    # Title
    title = ttk.Label(main_frame, text="Grid Layout Test", font=("Arial", 16))
    title.grid(row=0, column=0, columnspan=2, pady=10)
    
    # Entry
    ttk.Label(main_frame, text="Test Input:").grid(row=1, column=0, sticky="w", padx=5)
    entry = ttk.Entry(main_frame, width=20)
    entry.grid(row=1, column=1, sticky="ew", padx=5)
    entry.insert(0, "Test value")
    
    # Button
    def on_button():
        value = entry.get()
        messagebox.showinfo("Test", f"Entry value: {value}")
    
    button = ttk.Button(main_frame, text="Test Button", command=on_button)
    button.grid(row=2, column=0, columnspan=2, pady=10)
    
    def close_test():
        print("Grid layout test completed")
        root.quit()
        root.destroy()
    
    close_btn = ttk.Button(main_frame, text="Close Test 2", command=close_test)
    close_btn.grid(row=3, column=0, columnspan=2, pady=5)
    
    root.after(8000, close_test)  # Auto close after 8 seconds
    root.mainloop()

def test_scrolled_text():
    """Test 3: ScrolledText widget"""
    print("Test 3: Creating scrolled text...")
    try:
        from tkinter import scrolledtext
        
        root = tk.Tk()
        root.title("Debug Test 3 - ScrolledText")
        root.geometry("600x400")
        
        # Configure grid
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)
        
        # Title
        title = ttk.Label(root, text="ScrolledText Test", font=("Arial", 16))
        title.grid(row=0, column=0, pady=10)
        
        # ScrolledText
        text_widget = scrolledtext.ScrolledText(root, height=15, width=60)
        text_widget.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Add some text
        for i in range(20):
            text_widget.insert(tk.END, f"Line {i+1}: This is a test line\n")
        
        def close_test():
            print("ScrolledText test completed")
            root.quit()
            root.destroy()
        
        close_btn = ttk.Button(root, text="Close Test 3", command=close_test)
        close_btn.grid(row=2, column=0, pady=10)
        
        root.after(8000, close_test)  # Auto close after 8 seconds
        root.mainloop()
        
    except Exception as e:
        print(f"ScrolledText test failed: {e}")
        traceback.print_exc()

def run_all_tests():
    """Run all tests sequentially"""
    try:
        print("Starting GUI debug tests...")
        test_basic_window()
        test_grid_layout()  
        test_scrolled_text()
        print("All tests completed successfully!")
    except Exception as e:
        print(f"Test failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_num = sys.argv[1]
        if test_num == "1":
            test_basic_window()
        elif test_num == "2":
            test_grid_layout()
        elif test_num == "3":
            test_scrolled_text()
        else:
            print("Usage: python debug_gui.py [1|2|3]")
    else:
        run_all_tests()