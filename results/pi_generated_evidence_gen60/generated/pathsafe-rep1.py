import pytest
from pathsafe.paths import resolve


def test_absolute_name_raises_valueerror():
    """An absolute name (starting with /) must raise ValueError."""
    with pytest.raises(ValueError):
        resolve("/etc/passwd")


def test_absolute_name_with_drive_letter_raises_valueerror():
    """An absolute name with a drive letter (e.g., C:/) must raise ValueError."""
    with pytest.raises(ValueError):
        resolve("C:/Windows/System32")


def test_parent_directory_escape_raises_valueerror():
    """A name containing '..' to escape the depot must raise ValueError."""
    with pytest.raises(ValueError):
        resolve("../secret.txt")


def test_double_parent_directory_escape_raises_valueerror():
    """A name containing '../..' to escape the depot must raise ValueError."""
    with pytest.raises(ValueError):
        resolve("../../etc/passwd")


def test_parent_directory_in_middle_raises_valueerror():
    """A name containing '..' in the middle of the path must raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt")


def test_parent_directory_at_end_raises_valueerror():
    """A name ending with '..' must raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/..")


def test_parent_directory_with_trailing_slash_raises_valueerror():
    """A name ending with '..' and a trailing slash must raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../")


def test_simple_relative_name_resolves_correctly():
    """A simple relative name should resolve to depot/<name>."""
    assert resolve("parts.csv") == "depot/parts.csv"


def test_relative_name_with_subdirectory_resolves_correctly():
    """A relative name with a subdirectory should resolve to depot/<subdir>/<name>."""
    assert resolve("subdir/file.txt") == "depot/subdir/file.txt"


def test_relative_name_with_multiple_subdirectories_resolves_correctly():
    """A relative name with multiple subdirectories should resolve correctly."""
    assert resolve("a/b/c/file.txt") == "depot/a/b/c/file.txt"


def test_relative_name_with_extension_resolves_correctly():
    """A relative name with an extension should resolve correctly."""
    assert resolve("data.json") == "depot/data.json"


def test_empty_name_raises_valueerror():
    """An empty name should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("")


def test_name_with_only_dots_raises_valueerror():
    """A name that is just dots should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("..")


def test_name_with_single_dot_raises_valueerror():
    """A name that is just a single dot should raise ValueError."""
    with pytest.raises(ValueError):
        resolve(".")


def test_name_with_leading_slash_and_relative_path_raises_valueerror():
    """A name with a leading slash should raise ValueError even if rest is relative."""
    with pytest.raises(ValueError):
        resolve("/relative/path")


def test_name_with_backslashes_raises_valueerror():
    """A name with backslashes (Windows-style paths) should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("..\\secret.txt")


def test_name_with_mixed_slashes_raises_valueerror():
    """A name with mixed slashes containing '..' should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/..\\secret.txt")
