import time
import os
import random
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum
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
    
    @property
    def time_range(self) -> Tuple[int, int]:
        return (self.min_time, self.max_time)
    
    def is_valid_time(self, minutes: float) -> bool:
        return self.min_time <= minutes <= self.max_time

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


class PastaDatabase:
    """Manages pasta types and their cooking information"""
    
    def __init__(self):
        self._pasta_data = {
            "spaghetti": PastaInfo("spaghetti", 8, 10),
            "penne": PastaInfo("penne", 11, 13),
            "fusilli": PastaInfo("fusilli", 9, 11),
            "rigatoni": PastaInfo("rigatoni", 12, 14),
            "linguine": PastaInfo("linguine", 8, 10),
            "farfalle": PastaInfo("farfalle", 10, 12),
            "angel hair": PastaInfo("angel hair", 3, 5),
            "fettuccine": PastaInfo("fettuccine", 9, 11)
        }
        
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
    
    def get_pasta_info(self, pasta_name: str) -> Optional[PastaInfo]:
        """Get pasta information by name"""
        return self._pasta_data.get(pasta_name.lower())
    
    def get_all_pasta_types(self) -> List[PastaInfo]:
        """Get all available pasta types"""
        return list(self._pasta_data.values())
    
    def get_pasta_names(self) -> List[str]:
        """Get list of all pasta names"""
        return list(self._pasta_data.keys())
    
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
    
    def display_pasta_options(self) -> None:
        """Display all available pasta types"""
        print("\n🍝 Available Pasta Types:")
        print("-" * 30)
        pasta_types = self.pasta_db.get_all_pasta_types()
        for i, pasta in enumerate(pasta_types, 1):
            print(f"{i}. {pasta.name.title()} - {pasta.min_time}-{pasta.max_time} minutes")
        print("-" * 30)
    
    def get_user_pasta_choice(self) -> str:
        """Get user's pasta selection"""
        pasta_names = self.pasta_db.get_pasta_names()
        while True:
            try:
                choice = int(input("Enter the number of your pasta choice: "))
                if 1 <= choice <= len(pasta_names):
                    return pasta_names[choice - 1]
                else:
                    print(f"Please enter a number between 1 and {len(pasta_names)}")
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
    
    def on_timer_tick(self, event: TimerEvent) -> None:
        """Handle timer tick events"""
        timer_display = f"{event.minutes:02d}:{event.seconds:02d}"
        self._clear_screen()
        print(f"🍝 Cooking {event.pasta_type.title()}")
        print(f"⏰ Time remaining: {timer_display}")
        print(f"💡 {self.current_fact}")
        print("Press Ctrl+C to cancel")
    
    def on_timer_finished(self, event: TimerEvent) -> None:
        """Handle timer completion"""
        self._clear_screen()
        print("🎉 TIME'S UP! 🎉")
        print(f"Your {event.pasta_type} is ready!")
        print("Remember to taste test before serving! 👨‍🍳")
        
        if self.sound_notifier.play_notification():
            print("🔔 Sound notification played!")
        else:
            print("(Install 'playsound3' for sound notifications)")
    
    def on_timer_cancelled(self, event: TimerEvent) -> None:
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
                print("Goodbye! 👋")
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

class PastaTimerApp:
    """Main application class that orchestrates the pasta timer"""
    
    def __init__(self, debug_mode: bool = False):
        self.pasta_db = PastaDatabase()
        self.debug_mode = debug_mode
        self.cli = CLIInterface(self.pasta_db, debug_mode)
    
    def run(self) -> None:
        """Main application loop"""
        print("🍝 Welcome to the Pasta Timer! 🍝")
        
        while True:
            try:
                self.cli.display_pasta_options()
                selected_pasta = self.cli.get_user_pasta_choice()
                cooking_time = self.cli.get_cooking_time(selected_pasta)
                self.cli.run_timer_session(selected_pasta, cooking_time)
                
                if not self.cli.prompt_restart():
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