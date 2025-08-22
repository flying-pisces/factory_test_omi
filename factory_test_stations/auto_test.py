#!/usr/bin/env python3
"""
Auto-closing tkinter test to verify GUI displays correctly
"""

import tkinter as tk
from tkinter import ttk
import sys

def auto_close_test():
    """Test that auto-closes after 3 seconds"""
    print("Creating auto-closing GUI test...")
    
    root = tk.Tk()
    root.title("Auto-Close Test - Should show widgets for 3 seconds")
    root.geometry("600x400")
    
    # Add visible widgets
    title = tk.Label(root, text="AUTO-CLOSE TEST", font=("Arial", 20, "bold"), 
                    bg="yellow", fg="red")
    title.pack(pady=20)
    
    status = tk.Label(root, text="If you can see this, GUI widgets are working!", 
                     font=("Arial", 14), bg="lightgreen")
    status.pack(pady=10)
    
    # Entry and button
    frame = tk.Frame(root, bg="lightblue")
    frame.pack(pady=20)
    
    tk.Label(frame, text="Test Entry:", bg="lightblue").pack(side=tk.LEFT)
    entry = tk.Entry(frame, width=20)
    entry.pack(side=tk.LEFT, padx=5)
    entry.insert(0, "Test text visible?")
    
    button = tk.Button(frame, text="Test Button", bg="orange")
    button.pack(side=tk.LEFT, padx=5)
    
    # Console area
    text_area = tk.Text(root, height=8, width=60, bg="white")
    text_area.pack(pady=10)
    text_area.insert(tk.END, "Console area text:\nLine 1\nLine 2\nLine 3\n")
    text_area.insert(tk.END, "If you can read this, the GUI is working properly!\n")
    
    countdown_label = tk.Label(root, text="Closing in 3 seconds...", 
                              font=("Arial", 12), bg="red", fg="white")
    countdown_label.pack(pady=10)
    
    def close_window():
        print("Auto-closing window...")
        root.quit()
        root.destroy()
    
    # Auto-close after 3 seconds
    root.after(3000, close_window)
    
    print("Starting GUI (will auto-close in 3 seconds)...")
    try:
        root.mainloop()
        print("GUI closed successfully")
        return True
    except Exception as e:
        print(f"GUI error: {e}")
        return False

if __name__ == "__main__":
    success = auto_close_test()
    if success:
        print("✓ GUI test completed successfully")
    else:
        print("✗ GUI test failed")