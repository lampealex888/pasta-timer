from pasta_database import PastaDatabase
from cli_interface import CLIInterface

class PastaTimerApp:
    """Main application class that orchestrates the pasta timer"""
    
    def __init__(self, debug_mode: bool = False):
        self.pasta_db = PastaDatabase()
        self.debug_mode = debug_mode
        self.cli = CLIInterface(self.pasta_db, debug_mode)
    
    def run(self) -> None:
        """Main application loop"""
        while True:
            try:
                choice = self.cli.display_main_menu()
                
                if choice == "1":  # Start Timer
                    self.cli.display_pasta_options()
                    selected_pasta = self.cli.get_user_pasta_choice()
                    cooking_time = self.cli.get_cooking_time(selected_pasta)
                    self.cli.run_timer_session(selected_pasta, cooking_time)
                    
                    if not self.cli.prompt_restart():
                        break
                
                elif choice == "2":  # Add Custom Pasta
                    self.cli.add_custom_pasta_interactive()
                
                elif choice == "3":  # Manage Custom Pasta
                    self.cli.manage_custom_pasta_interactive()
                
                elif choice == "4":  # View All Pasta Types
                    self.cli.view_all_pasta_types()
                
                elif choice == "5":  # Exit
                    print("👋 Goodbye!")
                    break
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\nSomething went wrong: {e}")

def main():
    """Entry point"""
    # Debug mode: set to True to make all timers last only 6 seconds
    DEBUG_MODE = False  # Change to True for testing
    
    app = PastaTimerApp(debug_mode=DEBUG_MODE)
    app.run()

if __name__ == "__main__":
    main()