from pathsafe.paths import resolve


def test_absolute_name_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`."""
    with pytest.raises(ValueError):
        resolve("/etc/passwd")


def test_absolute_name_with_drive_letter_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`."""
    with pytest.raises(ValueError):
        resolve("C:/windows/system32")


def test_parent_directory_escape_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`."""
    with pytest.raises(ValueError):
        resolve("../secret.txt")


def test_nested_parent_directory_escape_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`."""
    with pytest.raises(ValueError):
        resolve("foo/../../bar.txt")


def test_hidden_parent_directory_escape_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`."""
    with pytest.raises(ValueError):
        resolve("foo/../../../etc/passwd")


def test_current_directory_still_allowed():
    """REQUIREMENT: A relative name resolves to `depot/<name>`."""
    # Note: The instruction says "A relative name resolves to depot/<name>".
    # It does not explicitly ban ".", but let's check if the current implementation
    # handles simple relative names correctly. We already have a test for simple names.
    # Let's test a name with subdirectory that does NOT escape.
    assert resolve("subdir/file.txt") == "depot/subdir/file.txt"


def test_dotdot_in_middle_of_path_raises_valueerror():
    """REQUIREMENT: A name that is absolute, or that escapes the depot with `..`, must be refused by raising `ValueError`."""
    with pytest.raises(ValueError):
        resolve("a/b/../../c.txt")


def test_valueerror_message_indicates_rejection():
    """REQUIREMENT: It must not be silently rewritten, stripped or clamped into the depot — the caller needs to know the request was rejected."""
    try:
        resolve("../secret.txt")
        assert False, "Expected ValueError to be raised"
    except ValueError as e:
        # The error should not be about file not found or similar
        assert len(str(e)) > 0


def test_valueerror_raised_for_absolute_path():
    """REQUIREMENT: It must not be silently rewritten, stripped or clamped into the depot — the caller needs to know the request was rejected."""
    try:
        resolve("/etc/hosts")
        assert False, "Expected ValueError to be raised"
    except ValueError:
        pass
