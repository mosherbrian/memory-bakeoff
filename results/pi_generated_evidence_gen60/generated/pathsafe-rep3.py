import pytest
from pathsafe.paths import resolve


class TestResolveAbsoluteNames:
    """Tests for absolute names that must raise ValueError."""

    def test_absolute_unix_path_raises(self):
        """Absolute paths starting with / must be refused."""
        with pytest.raises(ValueError):
            resolve("/etc/passwd")

    def test_absolute_windows_path_raises(self):
        """Absolute paths starting with C: must be refused."""
        with pytest.raises(ValueError):
            resolve("C:/windows/system32")

    def test_absolute_path_with_slash_raises(self):
        """Paths starting with / must raise ValueError."""
        with pytest.raises(ValueError):
            resolve("/foo/bar/baz")

    def test_absolute_path_with_drive_letter_raises(self):
        """Paths starting with a drive letter must raise ValueError."""
        with pytest.raises(ValueError):
            resolve("D:/data/file.txt")


class TestResolveEscapeAttempts:
    """Tests for paths that try to escape the depot with .."""

    def test_simple_dotdot_raises(self):
        """A name containing .. must raise ValueError."""
        with pytest.raises(ValueError):
            resolve("../secret.txt")

    def test_dotdot_in_middle_raises(self):
        """A name with .. in the middle must raise ValueError."""
        with pytest.raises(ValueError):
            resolve("parts/../secret.txt")

    def test_dotdot_at_end_raises(self):
        """A name ending with .. must raise ValueError."""
        with pytest.raises(ValueError):
            resolve("parts/..")

    def test_multiple_dotdots_raises(self):
        """Multiple .. components must raise ValueError."""
        with pytest.raises(ValueError):
            resolve("../../etc/passwd")

    def test_dotdot_with_trailing_slash_raises(self):
        """A name with .. and trailing slash must raise ValueError."""
        with pytest.raises(ValueError):
            resolve("../")

    def test_nested_dotdot_raises(self):
        """Deeply nested .. must raise ValueError."""
        with pytest.raises(ValueError):
            resolve("a/b/../../secret.txt")

    def test_dotdot_only_raises(self):
        """Just .. must raise ValueError."""
        with pytest.raises(ValueError):
            resolve("..")


class TestResolveValidRelativeNames:
    """Tests for valid relative names that should resolve correctly."""

    def test_simple_filename(self):
        """A simple filename should resolve to depot/<name>."""
        assert resolve("parts.csv") == "depot/parts.csv"

    def test_filename_with_extension(self):
        """A filename with extension should resolve correctly."""
        assert resolve("data.json") == "depot/data.json"

    def test_path_with_single_directory(self):
        """A path with one directory level should resolve correctly."""
        assert resolve("subdir/file.txt") == "depot/subdir/file.txt"

    def test_path_with_multiple_directories(self):
        """A path with multiple directory levels should resolve correctly."""
        assert resolve("a/b/c/file.txt") == "depot/a/b/c/file.txt"

    def test_filename_with_underscore(self):
        """A filename with underscore should resolve correctly."""
        assert resolve("my_file.txt") == "depot/my_file.txt"

    def test_filename_with_dashes(self):
        """A filename with dashes should resolve correctly."""
        assert resolve("my-file.txt") == "depot/my-file.txt"

    def test_filename_with_numbers(self):
        """A filename with numbers should resolve correctly."""
        assert resolve("file123.txt") == "depot/file123.txt"

    def test_empty_subdirectory_name(self):
        """A path with empty subdirectory component should resolve correctly."""
        assert resolve("./file.txt") == "depot/./file.txt"


class TestResolveValueErrorBehavior:
    """Tests to ensure ValueError is raised properly and not silently handled."""

    def test_value_error_is_not_suppressed(self):
        """Ensure that ValueError is actually raised, not caught silently."""
        with pytest.raises(ValueError) as exc_info:
            resolve("../escape.txt")
        # Verify the exception is a ValueError
        assert isinstance(exc_info.value, ValueError)

    def test_absolute_path_raises_value_error(self):
        """Ensure that absolute paths raise ValueError."""
        with pytest.raises(ValueError):
            resolve("/absolute/path")

    def test_no_mutation_of_input(self):
        """Ensure the input string is not modified."""
        original_name = "../escape.txt"
        with pytest.raises(ValueError):
            resolve(original_name)
        assert original_name == "../escape.txt"

    def test_return_type_is_string_for_valid(self):
        """Ensure that valid resolutions return a string."""
        result = resolve("file.txt")
        assert isinstance(result, str)

    def test_return_type_is_string_for_valid_with_path(self):
        """Ensure that valid resolutions with paths return a string."""
        result = resolve("subdir/file.txt")
        assert isinstance(result, str)
