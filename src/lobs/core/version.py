"""A simple semantic version implementation."""
import dataclasses
import functools
import re
import typing as t


@dataclasses.dataclass(frozen=True)
@functools.total_ordering
class Version:
    major: int
    minor: int
    patch: int
    extra: str | None = None

    SEMVER_REGEX = re.compile(
        r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)'
        r'(?:[-.](?P<extra>.+))?$'
    )

    @classmethod
    def parse(cls, version_str: str) -> t.Self:
        match = cls.SEMVER_REGEX.match(version_str)
        if not match:
            raise ValueError(f"Invalid version string: {version_str}")
        major = int(match.group('major'))
        minor = int(match.group('minor'))
        patch = int(match.group('patch'))
        extra = match.group('extra')

        return cls(major, minor, patch, extra)

    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.extra:
            version += f"-{self.extra}"
        return version

    def __lt__(self, other: t.Any) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return ((self.major, self.minor, self.patch, self.extra or '') <
                (other.major, other.minor, other.patch, other.extra or ''))
