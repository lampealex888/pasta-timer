import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from cli_interface import CLIInterface
from pasta_database import PastaDatabase
from models import PastaInfo

class DummyDB(PastaDatabase):
    def __init__(self):
        self._built_in_pasta = {"spaghetti": PastaInfo("spaghetti", 8, 10)}
        self._custom_pasta = {}
    def get_built_in_pasta_types(self):
        return list(self._built_in_pasta.values())
    def get_custom_pasta_types(self):
        return list(self._custom_pasta.values())
    def get_pasta_info(self, name):
        return self._built_in_pasta.get(name, None)
    def get_pasta_names(self):
        return list(self._built_in_pasta.keys())

@pytest.fixture
def cli():
    return CLIInterface(pasta_db=DummyDB())

def test_render_progress_bar_full(cli):
    bar = cli._render_progress_bar(total_seconds=100, remaining_seconds=0, bar_length=10)
    assert bar.startswith("[██████████]")
    assert bar.endswith("100%")

def test_render_progress_bar_half(cli):
    bar = cli._render_progress_bar(total_seconds=100, remaining_seconds=50, bar_length=10)
    assert bar.startswith("[█████-----]")
    assert bar.endswith(" 50%")

def test_render_progress_bar_zero(cli):
    bar = cli._render_progress_bar(total_seconds=100, remaining_seconds=100, bar_length=10)
    assert bar.startswith("[----------]")
    assert bar.endswith("  0%")

def test_get_user_pasta_choice(monkeypatch, cli):
    # Simulate user entering '1' for the first pasta
    monkeypatch.setattr('builtins.input', lambda _: '1')
    result = cli.get_user_pasta_choice()
    assert result == 'spaghetti'

def test_get_cooking_time(monkeypatch, cli):
    # Simulate user entering '9' for cooking time
    monkeypatch.setattr('builtins.input', lambda _: '9')
    result = cli.get_cooking_time('spaghetti')
    assert result == 9

def test_prompt_restart_yes(monkeypatch, cli):
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    assert cli.prompt_restart() is True

def test_prompt_restart_no(monkeypatch, cli):
    monkeypatch.setattr('builtins.input', lambda _: 'n')
    assert cli.prompt_restart() is False 