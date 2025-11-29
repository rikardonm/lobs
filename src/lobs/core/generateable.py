"""This represents a file that can be generated as part of a build process."""
import typing as t

from pathlib import Path


@t.runtime_checkable
class Generateable(t.Protocol):
    """A file that can be generated as part of a build process."""

    def generate(self, output_directory: Path) -> Path:
        """Generate the file at the specified output path."""
        ...
