import os
import time
from typing import List
from datetime import datetime

from models import PastaInfo
from pasta_database import PastaDatabase
from timer import TimerObserver, PastaTimer, SoundNotifier
from validators import CustomPastaValidator


class CLIInterface(TimerObserver):
    """Command-line interface for the pasta timer"""
    
    def __init__(self, pasta_db: PastaDatabase, debug_mode: bool = False):
        self.pasta_db = pasta_db
        self.debug_mode = debug_mode
        self.sound_notifier = SoundNotifier()
        self.current_fact = ""
    
    def display_main_menu(self) -> str:
        """Display main menu and get user choice"""
        print("\n🍝 Welcome to the Pasta Timer! 🍝")
        print("=" * 40)
        print("1. Start Timer")
        print("2. Add Custom Pasta Type")
        print("3. Manage Custom Pasta Types")
        print("4. View All Pasta Types")
        print("5. Exit")
        print("=" * 40)
        
        while True:
            choice = input("Select an option (1-5): ").strip()
            if choice in ["1", "2", "3", "4", "5"]:
                return choice
            print("Please enter a number between 1 and 5.")
    
    def display_pasta_options(self) -> List[PastaInfo]:
        """Display all available pasta types and return the list in display order"""
        built_in = self.pasta_db.get_built_in_pasta_types()
        custom = self.pasta_db.get_custom_pasta_types()
        pasta_list = built_in + custom  # Order: built-in first, then custom

        print("\n🍝 Available Pasta Types:")
        print("=" * 50)

        # Display built-in pasta types
        if built_in:
            print("Built-in Types:")
            for i, pasta in enumerate(built_in, 1):
                print(f"{i:2d}. {pasta.name.title()} - {pasta.min_time}-{pasta.max_time} minutes")

        # Display custom pasta types
        if custom:
            print("\nCustom Types:")
            start_num = len(built_in) + 1
            for i, pasta in enumerate(custom, start_num):
                usage_text = f" (Used {pasta.usage_count} times)" if pasta.usage_count > 0 else ""
                print(f"{i:2d}. ⭐ {pasta.name.title()} - {pasta.min_time}-{pasta.max_time} minutes{usage_text}")

        print("=" * 50)
        return pasta_list
    
    def get_user_pasta_choice(self) -> str:
        """Get user's pasta selection using the same order as display_pasta_options"""
        pasta_list = self.display_pasta_options()  # Always display and get the same list/order
        while True:
            try:
                choice = int(input("Enter the number of your pasta choice: "))
                if 1 <= choice <= len(pasta_list):
                    return pasta_list[choice - 1].name
                else:
                    print(f"Please enter a number between 1 and {len(pasta_list)}")
            except ValueError:
                print("Please enter a valid number!")
    
    def get_cooking_time(self, pasta_type: str) -> float:
        """Get cooking time from user"""
        pasta_info = self.pasta_db.get_pasta_info(pasta_type)
        if not pasta_info:
            raise ValueError(f"Unknown pasta type: {pasta_type}")
        
        if self.debug_mode:
            return 0.1  # 6 seconds in minutes
        
        if pasta_info.min_time == pasta_info.max_time:
            return float(pasta_info.min_time)
        
        print(f"\nThe recommended cooking time for {pasta_type.title()} is between "
              f"{pasta_info.min_time} and {pasta_info.max_time} minutes.")
        
        while True:
            try:
                user_time = float(input(f"Enter your desired cooking time in minutes "
                                      f"({pasta_info.min_time}-{pasta_info.max_time}): "))
                if pasta_info.is_valid_time(user_time):
                    return user_time
                else:
                    print(f"Please enter a time between {pasta_info.min_time} and {pasta_info.max_time} minutes.")
            except ValueError:
                print("Please enter a valid number!")
    
    def add_custom_pasta_interactive(self) -> None:
        """Interactive process to add custom pasta"""
        print("\n🌟 Add Custom Pasta Type")
        print("-" * 30)
        
        # Get pasta name
        while True:
            name = input("Enter pasta name: ").strip()
            existing_names = self.pasta_db.get_pasta_names()
            is_valid, error = CustomPastaValidator.validate_pasta_name(name, existing_names)
            if is_valid:
                break
            print(f"❌ {error}")
        
        # Get minimum cooking time
        while True:
            try:
                min_time = int(input("Enter minimum cooking time (minutes): "))
                if 1 <= min_time <= 60:
                    break
                print("Please enter a time between 1 and 60 minutes.")
            except ValueError:
                print("Please enter a whole number!")
        
        # Get maximum cooking time
        while True:
            try:
                max_time = int(input("Enter maximum cooking time (minutes): "))
                is_valid, error = CustomPastaValidator.validate_cooking_time(min_time, max_time)
                if is_valid:
                    break
                print(f"❌ {error}")
            except ValueError:
                print("Please enter a whole number!")
        
        # Confirm details
        print(f"\n📋 Pasta Details:")
        print(f"   Name: {name.title()}")
        print(f"   Cooking Time: {min_time}-{max_time} minutes")
        
        confirm = input("\nSave this pasta type? (y/n): ").strip().lower()
        if confirm in ("y", "yes"):
            try:
                if self.pasta_db.add_custom_pasta(name, min_time, max_time):
                    print(f"✅ Successfully added '{name.title()}'!")
                else:
                    print("❌ Failed to save pasta type.")
            except ValueError as e:
                print(f"❌ Error: {e}")
        else:
            print("❌ Pasta type not saved.")
    
    def manage_custom_pasta_interactive(self) -> None:
        """Interactive process to manage custom pasta"""
        custom_pasta = self.pasta_db.get_custom_pasta_types()
        
        if not custom_pasta:
            print("\n📭 No custom pasta types found.")
            print("Use 'Add Custom Pasta Type' to create your first one!")
            return
        
        while True:
            print("\n⚙️  Manage Custom Pasta Types")
            print("-" * 35)
            
            for i, pasta in enumerate(custom_pasta, 1):
                usage_text = f" (Used {pasta.usage_count} times)" if pasta.usage_count > 0 else ""
                print(f"{i}. {pasta.name.title()} - {pasta.min_time}-{pasta.max_time} minutes{usage_text}")
            
            print(f"\n{len(custom_pasta) + 1}. ← Back to Main Menu")
            print("-" * 35)
            
            try:
                choice = int(input("Select pasta to delete (or back to menu): "))
                if choice == len(custom_pasta) + 1:
                    break
                elif 1 <= choice <= len(custom_pasta):
                    pasta_to_delete = custom_pasta[choice - 1]
                    confirm = input(f"Delete '{pasta_to_delete.name.title()}'? (y/n): ").strip().lower()
                    if confirm in ("y", "yes"):
                        if self.pasta_db.remove_custom_pasta(pasta_to_delete.name):
                            print(f"✅ Deleted '{pasta_to_delete.name.title()}'")
                            custom_pasta = self.pasta_db.get_custom_pasta_types()
                            if not custom_pasta:
                                print("📭 No more custom pasta types.")
                                break
                        else:
                            print("❌ Failed to delete pasta type.")
                    else:
                        print("❌ Deletion cancelled.")
                else:
                    print(f"Please enter a number between 1 and {len(custom_pasta) + 1}")
            except ValueError:
                print("Please enter a valid number!")
    
    def view_all_pasta_types(self) -> None:
        """Display detailed view of all pasta types"""
        built_in = self.pasta_db.get_built_in_pasta_types()
        custom = self.pasta_db.get_custom_pasta_types()
        
        print("\n📖 All Pasta Types")
        print("=" * 60)
        
        if built_in:
            print("🍝 Built-in Pasta Types:")
            for pasta in built_in:
                print(f"   • {pasta.name.title()} - {pasta.min_time}-{pasta.max_time} minutes")
        
        if custom:
            print("\n⭐ Custom Pasta Types:")
            for pasta in custom:
                usage_text = f" | Used {pasta.usage_count} times" if pasta.usage_count > 0 else ""
                created_date = ""
                if pasta.created_date:
                    try:
                        date_obj = datetime.fromisoformat(pasta.created_date.replace('Z', '+00:00'))
                        created_date = f" | Created {date_obj.strftime('%Y-%m-%d')}"
                    except:
                        pass
                print(f"   • {pasta.name.title()} - {pasta.min_time}-{pasta.max_time} minutes{usage_text}{created_date}")
        
        print("=" * 60)
        print(f"Total: {len(built_in)} built-in, {len(custom)} custom")
        input("\nPress Enter to continue...")
    
    def on_timer_tick(self, event) -> None:
        """Handle timer tick events"""
        timer_display = f"{event.minutes:02d}:{event.seconds:02d}"
        self._clear_screen()
        # Find total_seconds for this timer
        pasta_info = self.pasta_db.get_pasta_info(event.pasta_type)
        if pasta_info:
            # Try to get the original total_seconds (for custom times, fallback to event.remaining_seconds + elapsed)
            total_seconds = getattr(self, '_current_total_seconds', event.remaining_seconds + 1)
        else:
            total_seconds = event.remaining_seconds + 1

        # Store total_seconds for next tick if not already set
        if not hasattr(self, '_current_total_seconds'):
            self._current_total_seconds = total_seconds

        progress_bar = self._render_progress_bar(self._current_total_seconds, event.remaining_seconds)
        print(f"🍝 Cooking {event.pasta_type.title()}")
        print(f"⏰ Time remaining: {timer_display}")
        print(progress_bar)
        print(f"💡 {self.current_fact}")
        print("Press Ctrl+C to cancel")
    
    def on_timer_finished(self, event) -> None:
        """Handle timer completion"""
        self._clear_screen()
        print("🎉 TIME'S UP! 🎉")
        print(f"Your {event.pasta_type} is ready!")
        print("Remember to taste test before serving! 👨‍🍳")
        
        # Increment usage count for custom pasta
        self.pasta_db.increment_pasta_usage(event.pasta_type)
        
        if self.sound_notifier.play_notification():
            print("🔔 Sound notification played!")
        else:
            print("(Install 'playsound3' for sound notifications)")
        
        if hasattr(self, '_current_total_seconds'):
            del self._current_total_seconds
    
    def on_timer_cancelled(self, event) -> None:
        """Handle timer cancellation"""
        print("\n\n⏹️  Timer cancelled. Happy cooking! 👋")
        
    def _clear_screen(self) -> None:
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def prompt_restart(self) -> bool:
        """Ask user if they want to restart"""
        while True:
            answer = input("\nWould you like to start another timer? (y/n): ").strip().lower()
            if answer in ("y", "yes"):
                return True
            elif answer in ("n", "no"):
                return False
            else:
                print("Please enter 'y' or 'n'.")
    
    def run_timer_session(self, pasta_type: str, minutes: float) -> None:
        """Run a complete timer session"""
        self.current_fact = self.pasta_db.get_random_fact()
        
        print(f"\n🔥 Starting timer for {pasta_type.title()}")
        print(f"⏰ Cooking time: {minutes} minutes")
        print("Timer starting in 3 seconds...")
        time.sleep(3)
        
        timer = PastaTimer(pasta_type, minutes, self.debug_mode)
        timer.add_observer(self)
        timer.start()

    def _render_progress_bar(self, total_seconds: int, remaining_seconds: int, bar_length: int = 30) -> str:
        elapsed = total_seconds - remaining_seconds
        percent = elapsed / total_seconds if total_seconds else 0
        filled_length = int(bar_length * percent)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        return f"[{bar}] {int(percent * 100):3d}%"