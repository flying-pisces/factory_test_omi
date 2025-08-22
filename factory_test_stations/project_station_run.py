import platform
import sys
import os

import station_config
import test_station.test_station_project_station as test_station

def main():
    """Main entry point with platform detection for GUI selection."""
    
    # Load station configuration
    station_config.load_station('project_station')
    
    # Detect platform and available GUI frameworks
    is_windows = platform.system() == "Windows"
    has_display = True
    
    # Check for display availability on Linux
    if platform.system() == "Linux" and not os.environ.get("DISPLAY"):
        has_display = False
    
    # Command line argument parsing for GUI selection
    force_console = "--console" in sys.argv
    force_tkinter = "--tk" in sys.argv
    force_web = "--web" in sys.argv
    
    print(f"Platform: {platform.system()}")
    print(f"Python version: {sys.version}")
    
    # Force specific UI mode if requested
    if force_web and has_display:
        try:
            print("Starting web browser GUI...")
            import web_gui
            web_gui.main()
            return
        except Exception as e:
            print(f"Web GUI failed: {e}")
            sys.exit(1)
    
    if force_tkinter and has_display:
        try:
            print("Starting tkinter GUI...")
            import simple_gui_fixed as simple_gui
            factory_test_gui = simple_gui.SimpleFactoryTestGUI()
            factory_test_gui.main_loop()
            return
        except Exception as e:
            print(f"Tkinter GUI failed: {e}")
            sys.exit(1)
    
    if force_console:
        print("Starting console mode...")
        try:
            import console_test_runner
            runner = console_test_runner.ConsoleTestRunner('project_station')
            if runner.initialize():
                runner.interactive_mode()
            else:
                print("Failed to initialize console runner")
                sys.exit(1)
        except Exception as e:
            print(f"Console mode failed: {e}")
            sys.exit(1)
        return
    
    # Default to console mode (as requested)
    print("Starting console mode (default)...")
    try:
        import console_test_runner
        runner = console_test_runner.ConsoleTestRunner('project_station')
        if runner.initialize():
            runner.interactive_mode()
        else:
            print("Failed to initialize console runner")
            sys.exit(1)
    except Exception as e:
        print(f"Console mode failed: {e}")
        # Try tkinter GUI as fallback if console fails
        if has_display:
            try:
                print("Console failed, trying tkinter GUI as fallback...")
                import simple_gui_fixed as simple_gui
                factory_test_gui = simple_gui.SimpleFactoryTestGUI()
                factory_test_gui.main_loop()
                return
            except Exception as e:
                print(f"Tkinter GUI also failed: {e}")
        
        print("All UI modes failed")
        sys.exit(1)

def print_usage():
    """Print usage information."""
    print("""
Factory Test Station Runner

Usage:
    python project_station_run.py [options]

Options:
    --console    Force console mode (no GUI) - DEFAULT
    --tk         Force tkinter GUI mode (cross-platform kiosk)
    --web        Force web browser GUI mode
    --help       Show this help message

UI Modes:
    Console:     Command-line interface (default)
    Tkinter:     Cross-platform GUI kiosk mode
    Web:         Browser-based interface

Examples:
    python project_station_run.py              # Console mode (default)
    python project_station_run.py --console    # Force console mode
    python project_station_run.py --tk         # Force tkinter kiosk mode
    python project_station_run.py --web        # Force web browser GUI
""")

if __name__ == "__main__":
    if "--help" in sys.argv:
        print_usage()
    else:
        main()
