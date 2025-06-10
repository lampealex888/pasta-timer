import time
from abc import ABC, abstractmethod
from typing import List, Optional, Dict

from models import TimerState, TimerEvent

try:
    from playsound3 import playsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False


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
