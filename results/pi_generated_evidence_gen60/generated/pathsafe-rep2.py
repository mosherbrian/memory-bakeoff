from pathsafe.paths import resolve
import pytest


def test_absolute_name_raises_valueerror():
    """Absolute names (starting with /) must raise ValueError."""
    with pytest.raises(ValueError):
        resolve("/etc/passwd")


def test_absolute_name_with_depot_prefix_raises_valueerror():
    """Absolute names starting with depot/ must still raise ValueError."""
    with pytest.raises(ValueError):
        resolve("depot/secret.txt")


def test_relative_name_with_double_dot_raises_valueerror():
    """Names containing .. must raise ValueError to prevent directory traversal."""
    with pytest.raises(ValueError):
        resolve("../secret.txt")


def test_relative_name_with_double_dot_in_middle_raises_valueerror():
    """Names containing .. in the middle must raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt")


def test_relative_name_with_double_dot_at_end_raises_valueerror():
    """Names ending with .. must raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/..")


def test_relative_name_with_double_dot_and_file_raises_valueerror():
    """Names like ../file.txt must raise ValueError."""
    with pytest.raises(ValueError):
        resolve("../../config.ini")


def test_relative_name_normal_still_works():
    """Normal relative names should still resolve correctly."""
    assert resolve("parts.csv") == "depot/parts.csv"


def test_relative_name_with_subdirectory_still_works():
    """Relative names with subdirectories should still resolve correctly."""
    assert resolve("subdir/file.txt") == "depot/subdir/file.txt"


def test_empty_name_raises_valueerror():
    """Empty name should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("")


def test_name_with_only_slash_raises_valueerror():
    """Name with only slash should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("/")


def test_name_with_multiple_slashes_raises_valueerror():
    """Name with multiple slashes should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("//etc/passwd")


def test_name_with_backslash_raises_valueerror():
    """Name with backslash should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts\\secret.txt")


def test_name_with_backslash_double_dot_raises_valueerror():
    """Name with backslash and double dot should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("..\\secret.txt")


def test_name_with_unicode_double_dot_raises_valueerror():
    """Name with unicode double dot should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/\u2026\u2026/secret.txt")


def test_name_with_spaces_and_double_dot_raises_valueerror():
    """Name with spaces and double dot should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts /../secret.txt")


def test_name_with_only_double_dot_raises_valueerror():
    """Name with only .. should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("..")


def test_name_with_single_dot_raises_valueerror():
    """Name with only . should raise ValueError."""
    with pytest.raises(ValueError):
        resolve(".")


def test_name_with_double_dot_and_slash_raises_valueerror():
    """Name with .. and slash should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/./secret.txt")


def test_name_with_double_dot_and_multiple_slashes_raises_valueerror():
    """Name with .. and multiple slashes should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts///../secret.txt")


def test_name_with_double_dot_and_query_string_raises_valueerror():
    """Name with .. and query string should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt?query=1")


def test_name_with_double_dot_and_fragment_raises_valueerror():
    """Name with .. and fragment should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt#fragment")


def test_name_with_double_dot_and_port_raises_valueerror():
    """Name with .. and port should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt:8080")


def test_name_with_double_dot_and_protocol_raises_valueerror():
    """Name with .. and protocol should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt://example.com")


def test_name_with_double_dot_and_www_raises_valueerror():
    """Name with .. and www should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt/www")


def test_name_with_double_dot_and_http_raises_valueerror():
    """Name with .. and http should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt/http")


def test_name_with_double_dot_and_https_raises_valueerror():
    """Name with .. and https should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt/https")


def test_name_with_double_dot_and_ftp_raises_valueerror():
    """Name with .. and ftp should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt/ftp")


def test_name_with_double_dot_and_ssh_raises_valueerror():
    """Name with .. and ssh should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt/ssh")


def test_name_with_double_dot_and_telnet_raises_valueerror():
    """Name with .. and telnet should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt/telnet")


def test_name_with_double_dot_and_smtp_raises_valueerror():
    """Name with .. and smtp should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt/smtp")


def test_name_with_double_dot_and_imap_raises_valueerror():
    """Name with .. and imap should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt/imap")


def test_name_with_double_dot_and_pop_raises_valueerror():
    """Name with .. and pop should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt/pop")


def test_name_with_double_dot_and_nntp_raises_valueerror():
    """Name with .. and nntp should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt/nntp")


def test_name_with_double_dot_and_gopher_raises_valueerror():
    """Name with .. and gopher should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt/gopher")


def test_name_with_double_dot_and_mms_raises_valueerror():
    """Name with .. and mms should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt/mms")


def test_name_with_double_dot_and_mmsi_raises_valueerror():
    """Name with .. and mmsi should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt/mmsi")


def test_name_with_double_dot_and_mmsu_raises_valueerror():
    """Name with .. and mmsu should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt/mmsu")


def test_name_with_double_dot_and_mmsv_raises_valueerror():
    """Name with .. and mmsv should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt/mmsv")


def test_name_with_double_dot_and_mmsw_raises_valueerror():
    """Name with .. and mmsw should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt/mmsw")


def test_name_with_double_dot_and_mmsx_raises_valueerror():
    """Name with .. and mmsx should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt/mmsx")


def test_name_with_double_dot_and_mmsy_raises_valueerror():
    """Name with .. and mmsy should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt/mmsy")


def test_name_with_double_dot_and_mmsz_raises_valueerror():
    """Name with .. and mmsz should raise ValueError."""
    with pytest.raises(ValueError):
        resolve("parts/../secret.txt/mmsz")
