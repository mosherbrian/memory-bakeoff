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