import os
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from models import PastaInfo, TimerEvent
from pasta_database import PastaDatabase
from timer import TimerObserver, PastaTimer, TimerManager, SoundNotifier
from validators import CustomPastaValidator

class CLIInterface(TimerObserver):
    """Command-line interface for the pasta timer with multiple timer support"""
    
    def __init__(self, pasta_db: PastaDatabase, debug_mode: bool = False):
        self.pasta_db = pasta_db
        self.debug_mode = debug_mode
        self.sound_notifier = SoundNotifier()
        self.timer_manager = TimerManager()
        self.current_facts: Dict[str, str] = {}  # timer_id -> fact
        self.display_mode = 'menu'  # 'menu' or 'monitoring'
        self.monitoring_active = False
        self.last_screen_update = time.time()
    
    def display_main_menu(self) -> str:
        """Display main menu and get user choice"""
        active_timers = self.timer_manager.get_active_timers()
        active_count = len([t for t in active_timers if t['status'] == 'running'])
        
        print("\n🍝 Welcome to the Pasta Timer! 🍝")
        print("=" * 45)
        print(f"1. Start New Timer")
        print(f"2. View Active Timers ({active_count} running)")
        print(f"3. Monitor All Timers")
        print(f"4. Add Custom Pasta Type")
        print(f"5. Manage Custom Pasta Types")
        print(f"6. View All Pasta Types")
        print(f"7. Exit")
        print("=" * 45)
        
        while True:
            choice = input("Select an option (1-7): ").strip()
            if choice in ["1", "2", "3", "4", "5", "6", "7"]:
                return choice
            print("Please enter a number between 1 and 7.")
    
    def display_pasta_options(self) -> List[PastaInfo]:
        """Display all available pasta types and return the list in display order"""
        built_in = self.pasta_db.get_built_in_pasta_types()
        custom = self.pasta_db.get_custom_pasta_types()
        pasta_list = built_in + custom

        print("\n🍝 Available Pasta Types:")
        print("=" * 50)

        if built_in:
            print("Built-in Types:")
            for i, pasta in enumerate(built_in, 1):
                print(f"{i:2d}. {pasta.name.title()} - {pasta.min_time}-{pasta.max_time} minutes")

        if custom:
            print("\nCustom Types:")
            start_num = len(built_in) + 1
            for i, pasta in enumerate(custom, start_num):
                usage_text = f" (Used {pasta.usage_count} times)" if pasta.usage_count > 0 else ""
                print(f"{i:2d}. ⭐ {pasta.name.title()} - {pasta.min_time}-{pasta.max_time} minutes{usage_text}")

        print("=" * 50)
        return pasta_list
    
    def get_user_pasta_choice(self) -> str:
        """Get user's pasta selection"""
        pasta_list = self.display_pasta_options()
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
    
    def start_new_timer(self) -> None:
        """Start a new concurrent timer"""
        selected_pasta = self.get_user_pasta_choice()
        cooking_time = self.get_cooking_time(selected_pasta)
        
        # Create and start the timer
        timer_id = self.timer_manager.add_timer(selected_pasta, cooking_time, self.debug_mode)
        self.current_facts[timer_id] = self.pasta_db.get_random_fact()
        
        print(f"\n🔥 Starting timer for {selected_pasta.title()}")
        print(f"⏰ Cooking time: {cooking_time} minutes")
        print(f"🆔 Timer ID: {timer_id}")
        
        if self.timer_manager.start_timer(timer_id, self):
            print("✅ Timer started successfully!")
            time.sleep(2)
        else:
            print("❌ Failed to start timer")
    
    def view_active_timers(self) -> None:
        """Display all active timers"""
        active_timers = self.timer_manager.get_active_timers()
        
        if not active_timers:
            print("\n📭 No active timers")
            input("Press Enter to continue...")
            return
        
        print("\n🕐 Active Timers")
        print("=" * 60)
        
        for timer in active_timers:
            status_emoji = {
                'running': '🔥',
                'finished': '✅',
                'cancelled': '❌',
                'error': '⚠️'
            }.get(timer['status'], '❓')
            
            elapsed = datetime.now() - timer['start_time']
            
            if timer['status'] == 'running':
                remaining_time = timedelta(seconds=timer['remaining_seconds'])
                print(f"{status_emoji} {timer['id']}: {timer['pasta_type'].title()}")
                print(f"   Time remaining: {remaining_time}")
                print(f"   Elapsed: {elapsed}")
            else:
                print(f"{status_emoji} {timer['id']}: {timer['pasta_type'].title()} - {timer['status'].upper()}")
                print(f"   Total time: {elapsed}")
            print()
        
        print("=" * 60)
        
        # Offer management options
        while True:
            action = input("Actions: (c)ancel timer, (r)emove finished, (b)ack to menu: ").strip().lower()
            
            if action == 'b':
                break
            elif action == 'c':
                timer_id = input("Enter timer ID to cancel: ").strip()
                if self.timer_manager.cancel_timer(timer_id):
                    print(f"✅ Timer {timer_id} cancelled")
                else:
                    print(f"❌ Timer {timer_id} not found")
            elif action == 'r':
                self.timer_manager.cleanup_finished_timers()
                print("✅ Finished timers removed")
                break
            else:
                print("Please enter 'c', 'r', or 'b'")
    
    def monitor_all_timers(self) -> None:
        """Real-time monitoring of all active timers"""
        print("\n🔍 Monitoring Mode - Press Ctrl+C to return to menu")
        time.sleep(2)
        
        self.monitoring_active = True
        try:
            while self.monitoring_active:
                self._display_monitoring_screen()
                time.sleep(1)
        except KeyboardInterrupt:
            self.monitoring_active = False
            print("\n\n↩️ Returning to main menu...")
            time.sleep(1)
    
    def _display_monitoring_screen(self) -> None:
        """Display the monitoring screen"""
        self._clear_screen()
        active_timers = self.timer_manager.get_active_timers()
        running_timers = [t for t in active_timers if t['status'] == 'running']
        
        print("🔍 PASTA TIMER MONITORING")
        print("=" * 60)
        
        if not running_timers:
            print("📭 No active timers running")
            print("\nPress Ctrl+C to return to menu")
            return
        
        for timer in running_timers:
            minutes = timer['remaining_seconds'] // 60
            seconds = timer['remaining_seconds'] % 60
            timer_display = f"{minutes:02d}:{seconds:02d}"
            
            progress_bar = self._render_progress_bar(
                timer['total_seconds'], 
                timer['remaining_seconds']
            )
            
            fact = self.current_facts.get(timer['id'], "Cooking pasta is an art! 🎨")
            
            print(f"🍝 {timer['pasta_type'].title()} ({timer['id']})")
            print(f"⏰ Time remaining: {timer_display}")
            print(progress_bar)
            print(f"💡 {fact}")
            print("-" * 40)
        
        print("\nPress Ctrl+C to return to menu")
    
    def add_custom_pasta_interactive(self) -> None:
        """Interactive process to add custom pasta"""
        print("\n🌟 Add Custom Pasta Type")
        print("-" * 30)
        
        while True:
            name = input("Enter pasta name: ").strip()
            existing_names = self.pasta_db.get_pasta_names()
            is_valid, error = CustomPastaValidator.validate_pasta_name(name, existing_names)
            if is_valid:
                break
            print(f"❌ {error}")
        
        while True:
            try:
                min_time = int(input("Enter minimum cooking time (minutes): "))
                if 1 <= min_time <= 60:
                    break
                print("Please enter a time between 1 and 60 minutes.")
            except ValueError:
                print("Please enter a whole number!")
        
        while True:
            try:
                max_time = int(input("Enter maximum cooking time (minutes): "))
                is_valid, error = CustomPastaValidator.validate_cooking_time(min_time, max_time)
                if is_valid:
                    break
                print(f"❌ {error}")
            except ValueError:
                print("Please enter a whole number!")
        
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
    
    # Timer Observer methods
    def on_timer_tick(self, event: TimerEvent) -> None:
        """Handle timer tick events - only update if in monitoring mode"""
        if self.monitoring_active:
            # The monitoring loop will handle display updates
            pass
    
    def on_timer_finished(self, event: TimerEvent) -> None:
        """Handle timer completion"""
        print(f"\n🎉 TIMER FINISHED! 🎉")
        print(f"Your {event.pasta_type.title()} is ready!")
        print("Remember to taste test before serving! 👨‍🍳")
        
        # Increment usage count for custom pasta
        self.pasta_db.increment_pasta_usage(event.pasta_type)
        
        if self.sound_notifier.play_notification():
            print("🔔 Sound notification played!")
        else:
            print("(Install 'playsound3' for sound notifications)")
    
    def on_timer_cancelled(self, event: TimerEvent) -> None:
        """Handle timer cancellation"""
        print(f"\n⏹️ Timer for {event.pasta_type.title()} was cancelled")
    
    def _clear_screen(self) -> None:
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _render_progress_bar(self, total_seconds: int, remaining_seconds: int, bar_length: int = 30) -> str:
        """Render a progress bar"""
        elapsed = total_seconds - remaining_seconds
        percent = elapsed / total_seconds if total_seconds else 0
        filled_length = int(bar_length * percent)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        return f"[{bar}] {int(percent * 100):3d}%"