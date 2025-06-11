import time
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
import threading
from datetime import datetime, timedelta

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
    
    @abstractmethod
    def on_timer_paused(self, event: TimerEvent) -> None:
        """Called when timer is paused"""
        pass
    
    @abstractmethod
    def on_timer_resumed(self, event: TimerEvent) -> None:
        """Called when timer is resumed"""
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
        self._pause_event = threading.Event()
        self._pause_event.set()  # Start unpaused
    
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
                elif event_type == "paused":
                    observer.on_timer_paused(event)
                elif event_type == "resumed":
                    observer.on_timer_resumed(event)
            except Exception as e:
                # Don't let observer errors crash the timer
                print(f"Observer error: {e}")
    
    def start(self) -> None:
        """Start the timer countdown"""
        if self.state not in [TimerState.IDLE, TimerState.PAUSED]:
            raise ValueError(f"Timer cannot be started from state: {self.state}")
        
        self.state = TimerState.RUNNING
        
        try:
            while self.remaining_seconds > 0 and self.state in [TimerState.RUNNING, TimerState.PAUSED]:
                # Wait if paused
                self._pause_event.wait()
                
                # Check if state changed while waiting
                if self.state != TimerState.RUNNING:
                    continue
                
                self._notify_observers("tick")
                time.sleep(1)
                self.remaining_seconds -= 1
            
            if self.state == TimerState.RUNNING:
                self.state = TimerState.FINISHED
                self._notify_observers("finished")
        except KeyboardInterrupt:
            self.cancel()
    
    def pause(self) -> None:
        """Pause the timer"""
        if self.state == TimerState.RUNNING:
            self.state = TimerState.PAUSED
            self._pause_event.clear()
            self._notify_observers("paused")
    
    def resume(self) -> None:
        """Resume the timer from paused state"""
        if self.state == TimerState.PAUSED:
            self.state = TimerState.RUNNING
            self._pause_event.set()
            self._notify_observers("resumed")
    
    def cancel(self) -> None:
        """Cancel the timer"""
        if self.state in [TimerState.RUNNING, TimerState.PAUSED]:
            self.state = TimerState.CANCELLED
            self._pause_event.set()  # Unblock if paused
            self._notify_observers("cancelled")
    
    def reset(self) -> None:
        """Reset the timer to initial state"""
        self.state = TimerState.IDLE
        self.remaining_seconds = self.total_seconds
        self._pause_event.set()  # Ensure unpaused


class TimerManager:
    """Manages multiple concurrent pasta timers"""
    
    def __init__(self):
        self.active_timers: Dict[str, Dict] = {}  # timer_id -> timer_info
        self.timer_counter = 0
        self.lock = threading.Lock()
    
    def add_timer(self, pasta_type: str, minutes: float, debug_mode: bool = False) -> str:
        """Add a new timer and return its ID"""
        with self.lock:
            self.timer_counter += 1
            timer_id = f"timer_{self.timer_counter}"
            
            timer_info = {
                'id': timer_id,
                'pasta_type': pasta_type,
                'minutes': minutes,
                'timer': PastaTimer(pasta_type, minutes, debug_mode),
                'thread': None,
                'start_time': datetime.now(),
                'status': 'created'
            }
            
            self.active_timers[timer_id] = timer_info
            return timer_id
    
    def start_timer(self, timer_id: str, observer: TimerObserver) -> bool:
        """Start a specific timer"""
        with self.lock:
            if timer_id not in self.active_timers:
                return False
            
            timer_info = self.active_timers[timer_id]
            timer_info['timer'].add_observer(observer)
            timer_info['status'] = 'running'
            
            # Start timer in a separate thread
            def run_timer():
                try:
                    timer_info['timer'].start()
                    with self.lock:
                        if timer_id in self.active_timers:
                            if timer_info['timer'].state.name == 'FINISHED':
                                timer_info['status'] = 'finished'
                            elif timer_info['timer'].state.name == 'CANCELLED':
                                timer_info['status'] = 'cancelled'
                            elif timer_info['timer'].state.name == 'PAUSED':
                                timer_info['status'] = 'paused'
                except Exception as e:
                    with self.lock:
                        if timer_id in self.active_timers:
                            timer_info['status'] = 'error'
                            timer_info['error'] = str(e)
            
            timer_info['thread'] = threading.Thread(target=run_timer, daemon=True)
            timer_info['thread'].start()
            return True
    
    def pause_timer(self, timer_id: str) -> bool:
        """Pause a specific timer"""
        with self.lock:
            if timer_id not in self.active_timers:
                return False
            
            timer_info = self.active_timers[timer_id]
            if timer_info['status'] == 'running':
                timer_info['timer'].pause()
                timer_info['status'] = 'paused'
                return True
            return False
    
    def resume_timer(self, timer_id: str) -> bool:
        """Resume a specific timer"""
        with self.lock:
            if timer_id not in self.active_timers:
                return False
            
            timer_info = self.active_timers[timer_id]
            if timer_info['status'] == 'paused':
                timer_info['timer'].resume()
                timer_info['status'] = 'running'
                return True
            return False
    
    def cancel_timer(self, timer_id: str) -> bool:
        """Cancel a specific timer"""
        with self.lock:
            if timer_id not in self.active_timers:
                return False
            
            timer_info = self.active_timers[timer_id]
            timer_info['timer'].cancel()
            timer_info['status'] = 'cancelled'
            return True
    
    def remove_timer(self, timer_id: str) -> bool:
        """Remove a timer from management"""
        with self.lock:
            if timer_id not in self.active_timers:
                return False
            
            timer_info = self.active_timers[timer_id]
            if timer_info['status'] == 'running':
                timer_info['timer'].cancel()
            
            del self.active_timers[timer_id]
            return True
    
    def get_active_timers(self) -> List[Dict]:
        """Get list of all active timers"""
        with self.lock:
            return [
                {
                    'id': timer_info['id'],
                    'pasta_type': timer_info['pasta_type'],
                    'minutes': timer_info['minutes'],
                    'status': timer_info['status'],
                    'start_time': timer_info['start_time'],
                    'remaining_seconds': timer_info['timer'].remaining_seconds if timer_info['status'] == 'running' else 0,
                    'total_seconds': timer_info['timer'].total_seconds
                }
                for timer_info in self.active_timers.values()
            ]
    
    def cleanup_finished_timers(self) -> None:
        """Remove finished and cancelled timers"""
        with self.lock:
            to_remove = [
                timer_id for timer_id, timer_info in self.active_timers.items()
                if timer_info['status'] in ['finished', 'cancelled', 'error']
            ]
            for timer_id in to_remove:
                del self.active_timers[timer_id]


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
