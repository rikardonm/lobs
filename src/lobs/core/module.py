import dataclasses
import inspect
import typing as t
from pathlib import Path
from types import ModuleType

from lobs.core import package


@dataclasses.dataclass
class ProjectModule:
    pkg: package.PKG
    """The project instance contained in the module."""
    filepath: Path
    """The base path of the module file (where the module file is located)."""

    @classmethod
    def from_module(cls, m: ModuleType, filepath: Path) -> t.Self:
        pkg = next((x for _, x in inspect.getmembers(m) if isinstance(x, package.Package)))
        return cls(pkg=pkg, filepath=filepath)
