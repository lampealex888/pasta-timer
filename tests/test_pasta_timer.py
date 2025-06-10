import pytest
from pasta_timer import PastaTimerApp

class DummyCLI:
    def __init__(self):
        self.displayed_menu = False
        self.prompted_restart = False
        self.timer_started = False
    def display_main_menu(self):
        self.displayed_menu = True
        return "5"  # Simulate exit
    def display_pasta_options(self):
        pass
    def get_user_pasta_choice(self):
        return "spaghetti"
    def get_cooking_time(self, pasta_type):
        return 1
    def run_timer_session(self, pasta_type, minutes):
        self.timer_started = True
    def prompt_restart(self):
        self.prompted_restart = True
        return False
    def add_custom_pasta_interactive(self):
        pass
    def manage_custom_pasta_interactive(self):
        pass
    def view_all_pasta_types(self):
        pass

def test_app_exit(monkeypatch):
    app = PastaTimerApp()
    app.cli = DummyCLI()
    app.run()
    assert app.cli.displayed_menu
    assert not app.cli.timer_started 