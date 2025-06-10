import pytest
from timer import PastaTimer, TimerObserver
from models import TimerEvent, TimerState

class DummyObserver(TimerObserver):
    def __init__(self):
        self.ticks = 0
        self.finished = False
        self.cancelled = False
    def on_timer_tick(self, event):
        self.ticks += 1
    def on_timer_finished(self, event):
        self.finished = True
    def on_timer_cancelled(self, event):
        self.cancelled = True

def test_add_remove_observer():
    timer = PastaTimer('spaghetti', 0.1, debug_mode=True)
    obs = DummyObserver()
    timer.add_observer(obs)
    assert obs in timer.observers
    timer.remove_observer(obs)
    assert obs not in timer.observers

def test_timer_reset():
    timer = PastaTimer('spaghetti', 0.1, debug_mode=True)
    timer.remaining_seconds = 0
    timer.reset()
    assert timer.state == TimerState.IDLE
    assert timer.remaining_seconds == timer.total_seconds

def test_notify_observers():
    timer = PastaTimer('spaghetti', 0.1, debug_mode=True)
    obs = DummyObserver()
    timer.add_observer(obs)
    timer._notify_observers('tick')
    assert obs.ticks == 1
    timer._notify_observers('finished')
    assert obs.finished
    timer._notify_observers('cancelled')
    assert obs.cancelled 