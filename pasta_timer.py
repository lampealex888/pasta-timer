import time
import os
import random
import json
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional, Callable, List
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
try:
    from playsound3 import playsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False

class TimerState(Enum):
    """Enum representing the current state of the timer"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"
    CANCELLED = "cancelled"

@dataclass
class PastaInfo:
    """Data class representing pasta information"""
    name: str
    min_time: int
    max_time: int
    is_custom: bool = False
    usage_count: int = 0
    created_date: Optional[str] = None
    
    @property
    def time_range(self) -> Tuple[int, int]:
        return (self.min_time, self.max_time)
    
    def is_valid_time(self, minutes: float) -> bool:
        return self.min_time <= minutes <= self.max_time
    
    def increment_usage(self) -> None:
        """Increment usage count for tracking"""
        self.usage_count += 1

@dataclass
class TimerEvent:
    """Data class representing timer events"""
    event_type: str
    remaining_seconds: int
    pasta_type: str
    additional_data: Optional[Dict] = None
    
    @property
    def minutes(self) -> int:
        return self.remaining_seconds // 60
    
    @property
    def seconds(self) -> int:
        return self.remaining_seconds % 60

class CustomPastaValidator:
    """Validates custom pasta input data"""
    
    @staticmethod
    def validate_pasta_name(name: str, existing_names: List[str]) -> Tuple[bool, str]:
        """Validate pasta name. Returns (is_valid, error_message)"""
        if not name or not name.strip():
            return False, "Pasta name cannot be empty"
        
        name = name.strip()
        if len(name) < 2:
            return False, "Pasta name must be at least 2 characters long"
        
        if len(name) > 50:
            return False, "Pasta name must be 50 characters or less"
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not all(c.isalpha() or c in " -'" for c in name):
            return False, "Pasta name can only contain letters, spaces, hyphens, and apostrophes"
        
        # Check for uniqueness (case-insensitive)
        if name.lower() in [n.lower() for n in existing_names]:
            return False, f"A pasta type named '{name}' already exists"
        
        return True, ""
    
    @staticmethod
    def validate_cooking_time(min_time: int, max_time: int) -> Tuple[bool, str]:
        """Validate cooking times. Returns (is_valid, error_message)"""
        if not isinstance(min_time, int) or not isinstance(max_time, int):
            return False, "Cooking times must be whole numbers"
        
        if min_time < 1 or max_time < 1:
            return False, "Cooking times must be at least 1 minute"
        
        if min_time > 60 or max_time > 60:
            return False, "Cooking times must be 60 minutes or less"
        
        if min_time > max_time:
            return False, "Minimum time cannot be greater than maximum time"
        
        return True, ""

class PastaStorage:
    """Handles persistent storage of custom pasta types"""
    
    def __init__(self, filename: str = "custom_pasta.json"):
        self.filename = filename
        self.backup_filename = f"{filename}.backup"
    
    def load_custom_pasta(self) -> Dict[str, PastaInfo]:
        """Load custom pasta types from file"""
        try:
            if not os.path.exists(self.filename):
                return {}
            
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            custom_pasta = {}
            pasta_data = data.get('custom_pasta', {})
            
            for name, info in pasta_data.items():
                custom_pasta[name] = PastaInfo(
                    name=info['name'],
                    min_time=info['min_time'],
                    max_time=info['max_time'],
                    is_custom=True,
                    usage_count=info.get('usage_count', 0),
                    created_date=info.get('created_date')
                )
            
            return custom_pasta
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Warning: Could not load custom pasta data: {e}")
            return {}
    
    def save_custom_pasta(self, custom_pasta: Dict[str, PastaInfo]) -> bool:
        """Save custom pasta types to file"""
        try:
            # Create backup of existing file
            if os.path.exists(self.filename):
                try:
                    with open(self.filename, 'r') as src, open(self.backup_filename, 'w') as dst:
                        dst.write(src.read())
                except Exception:
                    pass  # Backup failed, but continue with save
            
            # Prepare data for saving
            pasta_data = {}
            for name, info in custom_pasta.items():
                pasta_data[name] = {
                    'name': info.name,
                    'min_time': info.min_time,
                    'max_time': info.max_time,
                    'usage_count': info.usage_count,
                    'created_date': info.created_date
                }
            
            data = {
                'custom_pasta': pasta_data,
                'metadata': {
                    'version': '1.0',
                    'last_updated': datetime.now().isoformat()
                }
            }
            
            # Save to file
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving custom pasta data: {e}")
            return False

class PastaDatabase:
    """Manages pasta types and their cooking information"""
    
    def __init__(self):
        self._built_in_pasta = {
            "spaghetti": PastaInfo("spaghetti", 8, 10),
            "penne": PastaInfo("penne", 11, 13),
            "fusilli": PastaInfo("fusilli", 9, 11),
            "rigatoni": PastaInfo("rigatoni", 12, 14),
            "linguine": PastaInfo("linguine", 8, 10),
            "farfalle": PastaInfo("farfalle", 10, 12),
            "angel hair": PastaInfo("angel hair", 3, 5),
            "fettuccine": PastaInfo("fettuccine", 9, 11)
        }
        
        self._custom_pasta = {}
        self._storage = PastaStorage()
        self._load_custom_pasta()
        
        self._fun_facts = [
            "Did you know? The word 'pasta' comes from the Italian word for 'paste.'",
            "Tip: Always salt your pasta water for better flavor!",
            "Fact: There are over 600 shapes of pasta worldwide.",
            "Tip: Don't rinse your pasta after cooking; the starch helps sauce stick!",
            "Fact: Al dente means 'to the tooth' in Italian, describing pasta's ideal texture.",
            "Tip: Save a cup of pasta water to help thicken your sauce.",
            "Fact: Pasta was first referenced in Sicily in 1154.",
            "Tip: Stir pasta occasionally to prevent sticking.",
            "Fact: The average Italian eats 51 pounds of pasta per year!",
            "Tip: Pair pasta shapes with the right sauce for best results."
        ]
    
    def _load_custom_pasta(self) -> None:
        """Load custom pasta types from storage"""
        self._custom_pasta = self._storage.load_custom_pasta()
    
    def _save_custom_pasta(self) -> bool:
        """Save custom pasta types to storage"""
        return self._storage.save_custom_pasta(self._custom_pasta)
    
    def get_pasta_info(self, pasta_name: str) -> Optional[PastaInfo]:
        """Get pasta information by name"""
        name_lower = pasta_name.lower()
        
        # Check custom pasta first
        if name_lower in self._custom_pasta:
            return self._custom_pasta[name_lower]
        
        # Check built-in pasta
        return self._built_in_pasta.get(name_lower)
    
    def get_all_pasta_types(self) -> List[PastaInfo]:
        """Get all available pasta types (built-in + custom)"""
        all_pasta = list(self._built_in_pasta.values()) + list(self._custom_pasta.values())
        return sorted(all_pasta, key=lambda p: p.name)
    
    def get_built_in_pasta_types(self) -> List[PastaInfo]:
        """Get only built-in pasta types"""
        return list(self._built_in_pasta.values())
    
    def get_custom_pasta_types(self) -> List[PastaInfo]:
        """Get only custom pasta types"""
        return list(self._custom_pasta.values())
    
    def get_pasta_names(self) -> List[str]:
        """Get list of all pasta names"""
        return [p.name for p in self.get_all_pasta_types()]
    
    def add_custom_pasta(self, name: str, min_time: int, max_time: int) -> bool:
        """Add a custom pasta type"""
        # Validate input
        existing_names = self.get_pasta_names()
        is_valid_name, name_error = CustomPastaValidator.validate_pasta_name(name, existing_names)
        if not is_valid_name:
            raise ValueError(name_error)
        
        is_valid_time, time_error = CustomPastaValidator.validate_cooking_time(min_time, max_time)
        if not is_valid_time:
            raise ValueError(time_error)
        
        # Create pasta info
        pasta_info = PastaInfo(
            name=name.strip(),
            min_time=min_time,
            max_time=max_time,
            is_custom=True,
            usage_count=0,
            created_date=datetime.now().isoformat()
        )
        
        # Add to custom pasta and save
        self._custom_pasta[name.lower()] = pasta_info
        return self._save_custom_pasta()
    
    def remove_custom_pasta(self, name: str) -> bool:
        """Remove a custom pasta type"""
        name_lower = name.lower()
        if name_lower in self._custom_pasta:
            del self._custom_pasta[name_lower]
            return self._save_custom_pasta()
        return False
    
    def is_custom_pasta(self, name: str) -> bool:
        """Check if a pasta type is custom"""
        return name.lower() in self._custom_pasta
    
    def get_custom_pasta_count(self) -> int:
        """Get count of custom pasta types"""
        return len(self._custom_pasta)
    
    def increment_pasta_usage(self, pasta_name: str) -> None:
        """Increment usage count for a pasta type"""
        pasta_info = self.get_pasta_info(pasta_name)
        if pasta_info and pasta_info.is_custom:
            pasta_info.increment_usage()
            self._save_custom_pasta()
    
    def get_random_fact(self) -> str:
        """Get a random pasta fact"""
        return random.choice(self._fun_facts)

class TimerObserver(ABC):
    """Abstract base class for timer observers"""
    
    @abstractmethod
    def on_timer_tick(self, event: TimerEvent) -> None:
        """Called every second during timer countdown"""
        pass
    
    @abstractmethod
    def on_timer_finished(self, event: TimerEvent) -> None:
        """Called when timer completes"""
        pass
    
    @abstractmethod
    def on_timer_cancelled(self, event: TimerEvent) -> None:
        """Called when timer is cancelled"""
        pass

class PastaTimer:
    """Core pasta timer class - independent of UI"""
    
    def __init__(self, pasta_type: str, minutes: float, debug_mode: bool = False):
        self.pasta_type = pasta_type
        self.minutes = minutes
        self.debug_mode = debug_mode
        self.state = TimerState.IDLE
        self.observers: List[TimerObserver] = []
        self.total_seconds = int(minutes * 60) if not debug_mode else 6
        self.remaining_seconds = self.total_seconds
    
    def add_observer(self, observer: TimerObserver) -> None:
        """Add an observer to receive timer events"""
        self.observers.append(observer)
    
    def remove_observer(self, observer: TimerObserver) -> None:
        """Remove an observer"""
        if observer in self.observers:
            self.observers.remove(observer)
    
    def _notify_observers(self, event_type: str, additional_data: Optional[Dict] = None) -> None:
        """Notify all observers of a timer event"""
        event = TimerEvent(event_type, self.remaining_seconds, self.pasta_type, additional_data)
        
        for observer in self.observers:
            try:
                if event_type == "tick":
                    observer.on_timer_tick(event)
                elif event_type == "finished":
                    observer.on_timer_finished(event)
                elif event_type == "cancelled":
                    observer.on_timer_cancelled(event)
            except Exception as e:
                # Don't let observer errors crash the timer
                print(f"Observer error: {e}")
    
    def start(self) -> None:
        """Start the timer countdown"""
        if self.state != TimerState.IDLE:
            raise ValueError(f"Timer cannot be started from state: {self.state}")
        
        self.state = TimerState.RUNNING
        
        try:
            while self.remaining_seconds > 0 and self.state == TimerState.RUNNING:
                self._notify_observers("tick")
                time.sleep(1)
                self.remaining_seconds -= 1
            
            if self.state == TimerState.RUNNING:
                self.state = TimerState.FINISHED
                self._notify_observers("finished")
        except KeyboardInterrupt:
            self.cancel()
    
    def cancel(self) -> None:
        """Cancel the timer"""
        if self.state == TimerState.RUNNING:
            self.state = TimerState.CANCELLED
            self._notify_observers("cancelled")
    
    def reset(self) -> None:
        """Reset the timer to initial state"""
        self.state = TimerState.IDLE
        self.remaining_seconds = self.total_seconds

class SoundNotifier:
    """Handles sound notifications"""
    
    def __init__(self, sound_file: str = "alarm.mp3"):
        self.sound_file = sound_file
        self.enabled = SOUND_AVAILABLE
    
    def play_notification(self) -> bool:
        """Play notification sound. Returns True if successful."""
        if not self.enabled:
            return False
        
        try:
            playsound(self.sound_file)
            return True
        except Exception:
            return False

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
    
    def on_timer_tick(self, event: TimerEvent) -> None:
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
    
    def on_timer_finished(self, event: TimerEvent) -> None:
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
    
    def on_timer_cancelled(self, event: TimerEvent) -> None:
        """Handle timer cancellation"""
        print("\n\n⏹️  Timer cancelled. Happy cooking! 👋")
        
        if hasattr(self, '_current_total_seconds'):
            del self._current_total_seconds
    
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
    DEBUG_MODE = True  # Change to True for testing
    
    app = PastaTimerApp(debug_mode=DEBUG_MODE)
    app.run()

if __name__ == "__main__":
    main()