import pytest
from validators import CustomPastaValidator

def test_validate_pasta_name_empty():
    is_valid, error = CustomPastaValidator.validate_pasta_name('', [])
    assert not is_valid
    assert 'cannot be empty' in error

def test_validate_pasta_name_too_short():
    is_valid, error = CustomPastaValidator.validate_pasta_name('a', [])
    assert not is_valid
    assert 'at least 2 characters' in error

def test_validate_pasta_name_too_long():
    is_valid, error = CustomPastaValidator.validate_pasta_name('a'*51, [])
    assert not is_valid
    assert '50 characters or less' in error

def test_validate_pasta_name_invalid_chars():
    is_valid, error = CustomPastaValidator.validate_pasta_name('Spa9hetti!', [])
    assert not is_valid
    assert 'only contain letters' in error

def test_validate_pasta_name_duplicate():
    is_valid, error = CustomPastaValidator.validate_pasta_name('Spaghetti', ['spaghetti'])
    assert not is_valid
    assert 'already exists' in error

def test_validate_pasta_name_valid():
    is_valid, error = CustomPastaValidator.validate_pasta_name('Fusilli', ['spaghetti'])
    assert is_valid
    assert error == ''

def test_validate_cooking_time_non_int():
    is_valid, error = CustomPastaValidator.validate_cooking_time(5.5, 10)
    assert not is_valid
    assert 'whole numbers' in error

def test_validate_cooking_time_min_greater():
    is_valid, error = CustomPastaValidator.validate_cooking_time(15, 10)
    assert not is_valid
    assert 'Minimum time cannot be greater' in error

def test_validate_cooking_time_valid():
    is_valid, error = CustomPastaValidator.validate_cooking_time(5, 10)
    assert is_valid
    assert error == '' 