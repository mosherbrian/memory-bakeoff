from pathsafe.paths import resolve


def test_absolute_name_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`. It must not be silently rewritten, stripped or clamped into the depot — the caller needs to know the request was rejected."""
    with pytest.raises(ValueError):
        resolve("/etc/passwd")


def test_absolute_name_with_depot_prefix_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`. It must not be silently rewritten, stripped or clamped into the depot — the caller needs to know the request was rejected."""
    with pytest.raises(ValueError):
        resolve("/depot/secrets.txt")


def test_parent_directory_escape_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`. It must not be silently rewritten, stripped or clamped into the depot — the caller needs to know the request was rejected."""
    with pytest.raises(ValueError):
        resolve("../config.ini")


def test_deep_parent_directory_escape_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`. It must not be silently rewritten, stripped or clamped into the depot — the caller needs to know the request was rejected."""
    with pytest.raises(ValueError):
        resolve("../../../etc/passwd")


def test_parent_directory_escape_in_subdirectory_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`. It must not be silently rewritten, stripped or clamped into the depot — the caller needs to know the request was rejected."""
    with pytest.raises(ValueError):
        resolve("subdir/../../etc/passwd")


def test_hidden_parent_directory_escape_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`. It must not be silently rewritten, stripped or clamped into the depot — the caller needs to know the request was rejected."""
    with pytest.raises(ValueError):
        resolve("subdir/../config.ini")


def test_relative_name_with_subdirectory_resolves_correctly():
    """REQUIREMENT: A relative name resolves to `depot/<name>`."""
    assert resolve("subdir/file.txt") == "depot/subdir/file.txt"


def test_relative_name_with_multiple_subdirectories_resolves_correctly():
    """REQUIREMENT: A relative name resolves to `depot/<name>`."""
    assert resolve("a/b/c/file.txt") == "depot/a/b/c/file.txt"


def test_relative_name_with_extension_resolves_correctly():
    """REQUIREMENT: A relative name resolves to `depot/<name>`."""
    assert resolve("image.png") == "depot/image.png"


def test_relative_name_with_dot_in_name_resolves_correctly():
    """REQUIREMENT: A relative name resolves to `depot/<name>`."""
    assert resolve("file.name.txt") == "depot/file.name.txt"


def test_relative_name_just_directory_resolves_correctly():
    """REQUIREMENT: A relative name resolves to `depot/<name>`."""
    assert resolve("dir") == "depot/dir"
