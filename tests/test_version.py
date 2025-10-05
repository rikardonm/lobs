"""Test suite for the version module."""
import dataclasses
import pytest
from lobs.core.version import Version


class TestVersionCreation:
    """Test Version object creation."""

    def test_create_version_basic(self):
        """Test creating a basic version without extra."""
        version = Version(1, 2, 3)
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.extra is None

    def test_create_version_with_extra(self):
        """Test creating a version with extra information."""
        version = Version(1, 2, 3, "alpha")
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.extra == "alpha"

    def test_version_is_frozen(self):
        """Test that Version objects are immutable."""
        version = Version(1, 2, 3)
        with pytest.raises(dataclasses.FrozenInstanceError):
            version.major = 2  # pyright: ignore[reportAttributeAccessIssue]


class TestVersionParsing:
    """Test Version.parse() functionality."""

    def test_parse_basic_version(self):
        """Test parsing a basic semantic version."""
        version = Version.parse("1.2.3")
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.extra is None

    def test_parse_version_with_extra(self):
        """Test parsing a version with extra information."""
        version = Version.parse("1.2.3-alpha")
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.extra == "alpha"

    def test_parse_version_with_complex_extra(self):
        """Test parsing a version with complex extra information."""
        version = Version.parse("1.2.3-alpha.1+build.123")
        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3
        assert version.extra == "alpha.1+build.123"

    def test_parse_zero_version(self):
        """Test parsing version 0.0.0."""
        version = Version.parse("0.0.0")
        assert version.major == 0
        assert version.minor == 0
        assert version.patch == 0
        assert version.extra is None

    def test_parse_large_numbers(self):
        """Test parsing versions with large numbers."""
        version = Version.parse("999.888.777")
        assert version.major == 999
        assert version.minor == 888
        assert version.patch == 777

    @pytest.mark.parametrize("invalid_version", [
        "",                          # Empty string
        "1",                         # Missing components
        "1.2",                       # Missing patch
        "1.2.3.4",                   # Too many components
        "v1.2.3",                    # Prefix not allowed
        "1.2.3-",                    # Trailing dash
        "01.2.3",                    # Leading zeros not allowed
        "1.02.3",                    # Leading zeros not allowed
        "1.2.03",                    # Leading zeros not allowed
        "a.b.c",                     # Non-numeric
        "1.a.3",                     # Non-numeric minor
        "1.2.c",                     # Non-numeric patch
        "-1.2.3",                    # Negative numbers
        "1.-2.3",                    # Negative numbers
        "1.2.-3",                    # Negative numbers
        "1.2.3 ",                    # Trailing space
        " 1.2.3",                    # Leading space
        "1 .2.3",                    # Space in version
    ])
    def test_parse_invalid_versions(self, invalid_version: str):
        """Test that parsing invalid versions raises ValueError."""
        with pytest.raises(ValueError, match="Invalid version string"):
            _ = Version.parse(invalid_version)


class TestVersionStringRepresentation:
    """Test Version.__str__() functionality."""

    def test_str_basic_version(self):
        """Test string representation of a basic version."""
        version = Version(1, 2, 3)
        assert str(version) == "1.2.3"

    def test_str_version_with_extra(self):
        """Test string representation of a version with extra."""
        version = Version(1, 2, 3, "alpha")
        assert str(version) == "1.2.3-alpha"

    def test_str_zero_version(self):
        """Test string representation of version 0.0.0."""
        version = Version(0, 0, 0)
        assert str(version) == "0.0.0"

    def test_str_large_numbers(self):
        """Test string representation with large numbers."""
        version = Version(999, 888, 777, "beta.1")
        assert str(version) == "999.888.777-beta.1"

    def test_parse_str_roundtrip(self):
        """Test that parsing and stringifying is consistent."""
        original = "1.2.3-alpha.1+build.123"
        version = Version.parse(original)
        assert str(version) == original


class TestVersionOrdering:
    """Test Version ordering functionality."""

    def test_version_equality(self):
        """Test version equality comparison."""
        v1 = Version(1, 2, 3)
        v2 = Version(1, 2, 3)
        assert v1 == v2

    def test_version_inequality(self):
        """Test version inequality comparison."""
        v1 = Version(1, 2, 3)
        v2 = Version(1, 2, 4)
        assert v1 != v2

    def test_version_less_than(self):
        """Test version less than comparison."""
        v1 = Version(1, 2, 3)
        v2 = Version(1, 2, 4)
        assert v1 < v2

    def test_version_greater_than(self):
        """Test version greater than comparison."""
        v1 = Version(1, 2, 4)
        v2 = Version(1, 2, 3)
        assert v1 > v2

    def test_version_ordering_major(self):
        """Test ordering by major version."""
        v1 = Version(1, 9, 9)
        v2 = Version(2, 0, 0)
        assert v1 < v2

    def test_version_ordering_minor(self):
        """Test ordering by minor version when major is equal."""
        v1 = Version(1, 2, 9)
        v2 = Version(1, 3, 0)
        assert v1 < v2

    def test_version_ordering_patch(self):
        """Test ordering by patch version when major and minor are equal."""
        v1 = Version(1, 2, 3)
        v2 = Version(1, 2, 4)
        assert v1 < v2

    def test_version_ordering_with_extra(self):
        """Test ordering with extra information."""
        # Extra is compared lexicographically as the last field
        v1 = Version(1, 2, 3, "alpha")
        v2 = Version(1, 2, 3, "beta")
        assert v1 < v2

    def test_version_ordering_none_extra_vs_string_extra(self):
        """Test ordering when one has extra and one doesn't."""
        # None should come before any string in dataclass ordering
        v1 = Version(1, 2, 3, None)
        v2 = Version(1, 2, 3, "alpha")
        assert v1 < v2

    def test_version_sorting(self):
        """Test sorting a list of versions."""
        versions = [
            Version(2, 0, 0),
            Version(1, 2, 3, "beta"),
            Version(1, 2, 3, "alpha"),
            Version(1, 2, 3),
            Version(1, 3, 0),
        ]

        expected_order = [
            Version(1, 2, 3),           # None extra comes first
            Version(1, 2, 3, "alpha"),
            Version(1, 2, 3, "beta"),
            Version(1, 3, 0),
            Version(2, 0, 0),
        ]

        assert sorted(versions) == expected_order


class TestVersionRegex:
    """Test the VERSION_REGEX pattern."""

    def test_regex_basic_match(self):
        """Test regex matches basic version format."""
        match = Version.VERSION_REGEX.match("1.2.3")
        assert match is not None
        assert match.group('major') == '1'
        assert match.group('minor') == '2'
        assert match.group('patch') == '3'
        assert match.group('extra') is None

    def test_regex_with_extra_match(self):
        """Test regex matches version with extra."""
        match = Version.VERSION_REGEX.match("1.2.3-alpha")
        assert match is not None
        assert match.group('major') == '1'
        assert match.group('minor') == '2'
        assert match.group('patch') == '3'
        assert match.group('extra') == 'alpha'

    def test_regex_no_match_invalid_format(self):
        """Test regex doesn't match invalid formats."""
        assert Version.VERSION_REGEX.match("1.2") is None
        assert Version.VERSION_REGEX.match("v1.2.3") is None
        assert Version.VERSION_REGEX.match("01.2.3") is None
