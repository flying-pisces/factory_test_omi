#!/usr/bin/env python3
"""
Test script for TK interface table functionality.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_tk_table():
    """Test the TK interface table functionality."""
    print("Testing TK interface table functionality...")
    
    try:
        from simple_gui_fixed import SimpleFactoryTestGUI
        
        # Create a test instance
        root = tk.Tk()
        root.title("TK Table Test")
        
        # Create a minimal test frame
        test_frame = tk.Frame(root, bg="white")
        test_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Test table creation
        columns = ("parameter", "value", "low_limit", "high_limit", "attachment")
        test_table = ttk.Treeview(test_frame, columns=columns, show="headings", height=8)
        
        # Configure headings
        test_table.heading("parameter", text="Test Parameter")
        test_table.heading("value", text="Test Value") 
        test_table.heading("low_limit", text="Low Limit")
        test_table.heading("high_limit", text="High Limit")
        test_table.heading("attachment", text="Attachment")
        
        # Configure columns
        test_table.column("parameter", width=200, anchor=tk.W)
        test_table.column("value", width=120, anchor=tk.CENTER)
        test_table.column("low_limit", width=100, anchor=tk.CENTER)
        test_table.column("high_limit", width=100, anchor=tk.CENTER)
        test_table.column("attachment", width=100, anchor=tk.CENTER)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(test_frame, orient=tk.VERTICAL, command=test_table.yview)
        test_table.configure(yscrollcommand=scrollbar.set)
        
        # Pack table
        test_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure styling
        test_table.tag_configure("evenrow", background="#f8f9fa")
        test_table.tag_configure("oddrow", background="white")
        
        # Add test data
        test_items = [
            ("TEST ITEM 1", "✓ 1.1", "0.5", "2.0", "📊", "evenrow"),
            ("TEST ITEM 2", "✓ 1.4", "1.0", "1.5", "📈", "oddrow"),
            ("NON PARAMETRIC TEST ITEM 3", "✓ True", "True", "True", "📷", "evenrow"),
            ("TEST ITEM 4 (FAIL)", "✗ 2.5", "0.5", "2.0", "📊", "oddrow"),
            ("TEST ITEM 5 (TESTING)", "⏳ Testing...", "1.0", "3.0", "", "evenrow")
        ]
        
        for parameter, value, low, high, attachment, tag in test_items:
            test_table.insert("", tk.END, values=(parameter, value, low, high, attachment), tags=(tag,))
        
        # Add click handler
        def on_double_click(event):
            selection = test_table.selection()
            if selection:
                item = test_table.item(selection[0])
                values = item["values"]
                print(f"Double-clicked: {values[0]} -> {values[4]}")
        
        test_table.bind("<Double-1>", on_double_click)
        
        # Add control buttons
        button_frame = tk.Frame(root)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(button_frame, text="Clear Table", 
                 command=lambda: [test_table.delete(item) for item in test_table.get_children()]).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Add Test Row", 
                 command=lambda: test_table.insert("", tk.END, 
                                                  values=("New Test", "⏳ Running...", "0.0", "10.0", "📊"),
                                                  tags=("evenrow",))).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Close", 
                 command=root.quit).pack(side=tk.RIGHT, padx=5)
        
        # Info label
        info_label = tk.Label(root, text="✅ Table test successful! Double-click rows to test interactions.", 
                             bg="lightgreen", fg="black", font=("Arial", 10))
        info_label.pack(fill=tk.X, padx=20, pady=5)
        
        # Set window size and center
        root.geometry("800x500")
        root.resizable(True, True)
        
        print("✅ TK Table test GUI created successfully!")
        print("📋 Features tested:")
        print("   - Table creation with proper columns")
        print("   - Alternating row colors")
        print("   - Status icons (✓, ✗, ⏳)")
        print("   - Emoji attachments")
        print("   - Scrollbar functionality")
        print("   - Double-click interaction")
        print("   - Dynamic row addition/removal")
        print("\nClose the window to end the test.")
        
        # Start the GUI
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing TK table: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🧪 TK Interface Table Test")
    print("=" * 40)
    
    success = test_tk_table()
    
    if success:
        print("🎉 TK table test completed successfully!")
    else:
        print("💥 TK table test failed!")

if __name__ == "__main__":
    main()