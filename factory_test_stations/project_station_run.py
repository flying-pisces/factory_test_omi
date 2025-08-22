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
    force_gui = "--gui" in sys.argv
    force_tkinter = "--tkinter" in sys.argv
    force_web = "--web" in sys.argv
    
    print(f"Platform: {platform.system()}")
    print(f"Python version: {sys.version}")
    
    # Try Web GUI first (all platforms)
    if has_display and not force_console and not force_tkinter and not force_gui:
        try:
            print("Starting Chrome browser-based GUI...")
            import web_gui
            web_gui.main()
            return
        except Exception as e:
            print(f"Web GUI failed: {e}")
            print("Falling back to other GUI options...")
    
    # Try Windows WPF GUI (Windows only)
    if is_windows and not force_console and not force_tkinter and not force_web:
        try:
            print("Attempting to start Windows WPF GUI...")
            import hardware_station_common.factory_test_gui as gui
            factory_test_gui = gui.FactoryTestGui(station_config, test_station.projectstationStation)
            factory_test_gui.main_loop()
            return
        except ImportError as e:
            print(f"Windows GUI not available: {e}")
            print("Falling back to cross-platform GUI...")
    
    # Try tkinter GUI (cross-platform) - only if forced or web GUI failed
    if has_display and not force_console and not force_web:
        try:
            print("Starting cross-platform tkinter GUI...")
            import simple_gui_fixed as simple_gui
            factory_test_gui = simple_gui.SimpleFactoryTestGUI()
            factory_test_gui.main_loop()
            return
        except Exception as e:
            print(f"Tkinter GUI failed: {e}")
            print("Falling back to console mode...")
    
    # Fallback to console mode
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

def print_usage():
    """Print usage information."""
    print("""
Factory Test Station Runner

Usage:
    python project_station_run.py [options]

Options:
    --console    Force console mode (no GUI)
    --gui        Force GUI mode (Windows WPF if available)
    --tkinter    Force tkinter GUI mode (cross-platform)
    --web        Force web browser GUI mode (Chrome-based)
    --help       Show this help message

Platform Support:
    All platforms: Web GUI (preferred) → platform GUI → console
    Windows:       Web GUI → WPF GUI → tkinter GUI → console
    macOS/Linux:   Web GUI → tkinter GUI → console
    Headless:      console only

Examples:
    python project_station_run.py              # Auto-detect best interface (Web GUI)
    python project_station_run.py --console    # Force console mode
    python project_station_run.py --web        # Force web browser GUI
    python project_station_run.py --tkinter    # Force tkinter GUI
""")

if __name__ == "__main__":
    if "--help" in sys.argv:
        print_usage()
    else:
        main()
