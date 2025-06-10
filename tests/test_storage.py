import os
import json
import tempfile
from storage import PastaStorage
from models import PastaInfo

def test_load_custom_pasta_empty(tmp_path, monkeypatch):
    filename = tmp_path / "empty.json"
    filename.write_text('{}')
    storage = PastaStorage(str(filename))
    monkeypatch.setattr(os.path, 'exists', lambda f: True)
    result = storage.load_custom_pasta()
    assert isinstance(result, dict)
    assert result == {}

def test_save_and_load_custom_pasta(tmp_path, monkeypatch):
    filename = tmp_path / "custom.json"
    storage = PastaStorage(str(filename))
    pasta = PastaInfo('Test', 5, 10, is_custom=True, usage_count=2, created_date="2024-01-01T00:00:00")
    custom_pasta = {'test': pasta}
    # Save
    assert storage.save_custom_pasta(custom_pasta)
    # Load
    loaded = storage.load_custom_pasta()
    assert 'test' in loaded
    loaded_pasta = loaded['test']
    assert loaded_pasta.name == 'Test'
    assert loaded_pasta.min_time == 5
    assert loaded_pasta.max_time == 10
    assert loaded_pasta.usage_count == 2
    assert loaded_pasta.created_date == "2024-01-01T00:00:00" 