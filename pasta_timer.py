import argparse
from pasta_database import PastaDatabase
from cli_interface import CLIInterface

__version__ = "1.0.0"

class PastaTimerApp:
    """Main application class that orchestrates the pasta timer"""
    
    def __init__(self, debug_mode: bool = False):
        self.pasta_db = PastaDatabase()
        self.debug_mode = debug_mode
        self.cli = CLIInterface(self.pasta_db, debug_mode)
    
    def run(self) -> None:
        """Main application loop with concurrent timer support"""
        
        while True:
            try:
                # Clean up any finished timers before showing menu
                self.cli.timer_manager.cleanup_finished_timers()
                
                choice = self.cli.display_main_menu()
                
                if choice == "1":  # Start New Timer
                    self.cli.start_new_timer()
                
                elif choice == "2":  # View Active Timers
                    self.cli.view_active_timers()
                
                elif choice == "3":  # Monitor All Timers
                    self.cli.monitor_all_timers()
                    
                elif choice == "4":  # Add Custom Pasta
                    self.cli.add_custom_pasta_interactive()
                
                elif choice == "5":  # Manage Custom Pasta
                    self.cli.manage_custom_pasta_interactive()
                
                elif choice == "6":  # View All Pasta Types
                    self.cli.view_all_pasta_types()
                
                elif choice == "7":  # Exit
                    if self._cleanup_and_exit():
                        break
                    
            except KeyboardInterrupt:
                if self._cleanup_and_exit():
                    break
            except Exception as e:
                print(f"\n❌ Something went wrong: {e}")
                print("The application will continue running...")
    
    def _cleanup_and_exit(self) -> bool:
        """Clean up active timers and exit gracefully"""
        active_timers = self.cli.timer_manager.get_active_timers()
        running_timers = [t for t in active_timers if t['status'] == 'running']
        
        if running_timers:
            print(f"\n⚠️  You have {len(running_timers)} timer(s) still running:")
            for timer in running_timers:
                remaining_mins = timer['remaining_seconds'] // 60
                remaining_secs = timer['remaining_seconds'] % 60
                print(f"   • {timer['pasta_type'].title()} - {remaining_mins}:{remaining_secs:02d} remaining")
            
            confirm = input("\nDo you really want to exit and cancel all running timers? (y/n): ").strip().lower()
            if confirm not in ("y", "yes"):
                print("Returning to main menu...")
                return False
            
            # Cancel all running timers
            for timer in running_timers:
                self.cli.timer_manager.cancel_timer(timer['id'])
            
            print("🛑 All running timers cancelled.")

        # Stop any sound notifications
        self.cli.notification_manager.stop_sound()
        
        print("👋 Thanks for using Pasta Timer! Goodbye!")
        return True

def main():
    """Entry point for the pasta timer application"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="🍝 Pasta Timer - Never overcook your pasta again!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pasta_timer.py              # Normal mode
  python pasta_timer.py --debug      # Debug mode (6 second timers)
  python pasta_timer.py -d           # Debug mode (short form)
        """
    )
    
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Enable debug mode (all timers will run for 6 seconds only)"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"Pasta Timer {__version__}"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        print("🔧 DEBUG MODE: All timers will run for 6 seconds only")
    
    app = PastaTimerApp(debug_mode=args.debug)
    app.run()


if __name__ == "__main__":
    main()