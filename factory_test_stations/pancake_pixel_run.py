import platform
import sys
import os
import test_station
import station_config

def main():
    """Main entry point with UI mode selection."""
    
    # Load station configuration
    station_config.load_station('pancake_pixel')
    
    # Detect platform and available GUI frameworks
    has_display = True
    
    # Check for display availability on Linux
    if platform.system() == "Linux" and not os.environ.get("DISPLAY"):
        has_display = False
    
    # Command line argument parsing for UI selection
    force_console = "--console" in sys.argv
    force_tkinter = "--tk" in sys.argv
    force_web = "--web" in sys.argv
    
    print(f"Platform: {platform.system()}")
    print(f"Station: pancake_pixel")
    
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
            runner = console_test_runner.ConsoleTestRunner('pancake_pixel')
            if runner.initialize():
                runner.interactive_mode()
            else:
                print("Failed to initialize console runner")
                sys.exit(1)
        except Exception as e:
            print(f"Console mode failed: {e}")
            sys.exit(1)
        return
    
    # Default to console mode
    print("Starting console mode (default)...")
    try:
        import console_test_runner
        runner = console_test_runner.ConsoleTestRunner('pancake_pixel')
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
Factory Test Station Runner - Pancake Pixel

Usage:
    python pancake_pixel_run.py [options]

Options:
    --console    Force console mode (no GUI) - DEFAULT
    --tk         Force tkinter GUI mode (cross-platform kiosk)
    --web        Force web browser GUI mode
    --help       Show this help message

Examples:
    python pancake_pixel_run.py              # Console mode (default)
    python pancake_pixel_run.py --console    # Force console mode
    python pancake_pixel_run.py --tk         # Force tkinter kiosk mode
    python pancake_pixel_run.py --web        # Force web browser GUI
""")

if __name__ == "__main__":
    if "--help" in sys.argv:
        print_usage()
    else:
        main()
