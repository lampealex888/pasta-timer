import pytest
from pasta_database import PastaDatabase
from models import PastaInfo

class DummyStorage:
    def __init__(self):
        self.saved = None
    def load_custom_pasta(self):
        return {}
    def save_custom_pasta(self, custom_pasta):
        self.saved = custom_pasta
        return True

def make_db():
    db = PastaDatabase()
    db._storage = DummyStorage()
    db._custom_pasta = {}
    return db

def test_add_and_get_custom_pasta():
    db = make_db()
    assert db.get_custom_pasta_count() == 0
    db.add_custom_pasta('TestPasta', 5, 10)
    assert db.get_custom_pasta_count() == 1
    info = db.get_pasta_info('TestPasta')
    assert isinstance(info, PastaInfo)
    assert info.name == 'TestPasta'
    assert info.min_time == 5
    assert info.max_time == 10
    assert info.is_custom

def test_remove_custom_pasta():
    db = make_db()
    db.add_custom_pasta('TestPasta', 5, 10)
    assert db.remove_custom_pasta('TestPasta')
    assert db.get_custom_pasta_count() == 0

def test_increment_pasta_usage():
    db = make_db()
    db.add_custom_pasta('TestPasta', 5, 10)
    info = db.get_pasta_info('TestPasta')
    assert info.usage_count == 0
    db.increment_pasta_usage('TestPasta')
    assert info.usage_count == 1

def test_get_random_fact():
    db = make_db()
    fact = db.get_random_fact()
    assert isinstance(fact, str)
    assert len(fact) > 0 