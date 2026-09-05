from pathsafe.paths import resolve
from pathsafe.paths import resolve

def test_relative_name_with_multiple_subdirectories_resolves_correctly():
    """REQUIREMENT: A relative name resolves to `depot/<name>`."""
    assert resolve('a/b/c/file.txt') == 'depot/a/b/c/file.txt'

def test_relative_name_with_dot_in_name_resolves_correctly():
    """REQUIREMENT: A relative name resolves to `depot/<name>`."""
    assert resolve('file.name.txt') == 'depot/file.name.txt'

def test_relative_name_just_directory_resolves_correctly():
    """REQUIREMENT: A relative name resolves to `depot/<name>`."""
    assert resolve('dir') == 'depot/dir'
from pathsafe.paths import resolve

def test_double_dot_only_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`."""
    try:
        resolve('..')
        assert False, 'Expected ValueError for double-dot path'
    except ValueError:
        pass

def test_relative_name_with_extension():
    """REQUIREMENT: A relative name resolves to `depot/<name>`."""
    assert resolve('archive.tar.gz') == 'depot/archive.tar.gz'