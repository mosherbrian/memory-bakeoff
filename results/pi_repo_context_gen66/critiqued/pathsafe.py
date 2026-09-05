from pathsafe.paths import resolve

def test_absolute_name_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`."""
    try:
        resolve('/etc/passwd')
        assert False, 'Expected ValueError for absolute path'
    except ValueError:
        pass

def test_absolute_name_with_drive_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`."""
    try:
        resolve('C:/Windows/System32')
        assert False, 'Expected ValueError for absolute path with drive'
    except ValueError:
        pass

def test_parent_directory_escape_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`."""
    try:
        resolve('../secret.txt')
        assert False, 'Expected ValueError for path with ..'
    except ValueError:
        pass

def test_nested_parent_directory_escape_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`."""
    try:
        resolve('foo/../../bar.txt')
        assert False, 'Expected ValueError for path with ..'
    except ValueError:
        pass

def test_hidden_parent_directory_escape_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`."""
    try:
        resolve('foo/../../../bar.txt')
        assert False, 'Expected ValueError for path with ..'
    except ValueError:
        pass

def test_dot_only_escape_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`."""
    try:
        resolve('..')
        assert False, 'Expected ValueError for ..'
    except ValueError:
        pass

def test_absolute_path_inside_depot_still_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`. It must not be silently rewritten, stripped or clamped into the depot — the caller needs to know the request was rejected."""
    try:
        resolve('/depot/something.txt')
        assert False, 'Expected ValueError for absolute path inside depot'
    except ValueError:
        pass

def test_relative_name_still_works():
    """REQUIREMENT: A relative name resolves to `depot/<name>`."""
    assert resolve('file.txt') == 'depot/file.txt'

def test_relative_name_with_subdirectory_works():
    """REQUIREMENT: A relative name resolves to `depot/<name>`."""
    assert resolve('subdir/file.txt') == 'depot/subdir/file.txt'

def test_relative_name_with_multiple_subdirectories_works():
    """REQUIREMENT: A relative name resolves to `depot/<name>`."""
    assert resolve('a/b/c.txt') == 'depot/a/b/c.txt'
from pathsafe.paths import resolve

def test_absolute_name_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`. It must not be silently rewritten, stripped or clamped into the depot — the caller needs to know the request was rejected."""
    with pytest.raises(ValueError):
        resolve('/etc/passwd')

def test_absolute_name_with_depot_prefix_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`. It must not be silently rewritten, stripped or clamped into the depot — the caller needs to know the request was rejected."""
    with pytest.raises(ValueError):
        resolve('/depot/secrets.txt')

def test_parent_directory_escape_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`. It must not be silently rewritten, stripped or clamped into the depot — the caller needs to know the request was rejected."""
    with pytest.raises(ValueError):
        resolve('../config.ini')

def test_deep_parent_directory_escape_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`. It must not be silently rewritten, stripped or clamped into the depot — the caller needs to know the request was rejected."""
    with pytest.raises(ValueError):
        resolve('../../../etc/passwd')

def test_parent_directory_escape_in_subdirectory_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`. It must not be silently rewritten, stripped or clamped into the depot — the caller needs to know the request was rejected."""
    with pytest.raises(ValueError):
        resolve('subdir/../../etc/passwd')

def test_hidden_parent_directory_escape_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`. It must not be silently rewritten, stripped or clamped into the depot — the caller needs to know the request was rejected."""
    with pytest.raises(ValueError):
        resolve('subdir/../config.ini')

def test_relative_name_with_subdirectory_resolves_correctly():
    """REQUIREMENT: A relative name resolves to `depot/<name>`."""
    assert resolve('subdir/file.txt') == 'depot/subdir/file.txt'

def test_relative_name_with_multiple_subdirectories_resolves_correctly():
    """REQUIREMENT: A relative name resolves to `depot/<name>`."""
    assert resolve('a/b/c/file.txt') == 'depot/a/b/c/file.txt'

def test_relative_name_with_extension_resolves_correctly():
    """REQUIREMENT: A relative name resolves to `depot/<name>`."""
    assert resolve('image.png') == 'depot/image.png'

def test_relative_name_with_dot_in_name_resolves_correctly():
    """REQUIREMENT: A relative name resolves to `depot/<name>`."""
    assert resolve('file.name.txt') == 'depot/file.name.txt'

def test_relative_name_just_directory_resolves_correctly():
    """REQUIREMENT: A relative name resolves to `depot/<name>`."""
    assert resolve('dir') == 'depot/dir'
from pathsafe.paths import resolve

def test_absolute_name_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`."""
    try:
        resolve('/etc/passwd')
        assert False, 'Expected ValueError for absolute path'
    except ValueError:
        pass

def test_absolute_name_with_drive_letter_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`."""
    try:
        resolve('C:/Windows/System32')
        assert False, 'Expected ValueError for absolute path with drive letter'
    except ValueError:
        pass

def test_parent_directory_escape_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`."""
    try:
        resolve('../secret.txt')
        assert False, 'Expected ValueError for path escaping depot with ..'
    except ValueError:
        pass

def test_nested_parent_directory_escape_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`."""
    try:
        resolve('subdir/../../etc/passwd')
        assert False, 'Expected ValueError for path escaping depot with nested ..'
    except ValueError:
        pass

def test_parent_directory_escape_in_middle_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`."""
    try:
        resolve('a/b/../../../etc/passwd')
        assert False, 'Expected ValueError for path escaping depot with .. in the middle'
    except ValueError:
        pass

def test_dot_only_escape_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`."""
    try:
        resolve('.')
        assert False, 'Expected ValueError for dot-only path'
    except ValueError:
        pass

def test_double_dot_only_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`."""
    try:
        resolve('..')
        assert False, 'Expected ValueError for double-dot path'
    except ValueError:
        pass

def test_absolute_path_raises_valueerror_not_silently_rewritten():
    """REQUIREMENT: It must not be silently rewritten, stripped or clamped into the depot — the caller needs to know the request was rejected."""
    try:
        resolve('/absolute/path')
        assert False, 'Expected ValueError, not a rewritten path'
    except ValueError:
        pass

def test_escape_path_raises_valueerror_not_silently_clamped():
    """REQUIREMENT: It must not be silently rewritten, stripped or clamped into the depot — the caller needs to know the request was rejected."""
    try:
        resolve('../outside')
        assert False, 'Expected ValueError, not a clamped path'
    except ValueError:
        pass

def test_relative_name_still_works():
    """REQUIREMENT: A relative name resolves to `depot/<name>`."""
    assert resolve('file.txt') == 'depot/file.txt'

def test_relative_name_with_subdirectory():
    """REQUIREMENT: A relative name resolves to `depot/<name>`."""
    assert resolve('subdir/file.txt') == 'depot/subdir/file.txt'

def test_relative_name_with_multiple_subdirectories():
    """REQUIREMENT: A relative name resolves to `depot/<name>`."""
    assert resolve('a/b/c/file.txt') == 'depot/a/b/c/file.txt'

def test_relative_name_with_extension():
    """REQUIREMENT: A relative name resolves to `depot/<name>`."""
    assert resolve('archive.tar.gz') == 'depot/archive.tar.gz'