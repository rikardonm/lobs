import inspect
import typing as t
from pathlib import Path
from types import ModuleType

from lobs.core import project as p


class Package(t.Generic[p.TP]):
    def __init__(self, meta: p.ProjectMeta, project: p.TP, dependencies: 'list[IPackage] | None' = None) -> None:
        self.meta = meta
        """The metadata of the package."""
        self.project = project
        """The project instance contained in the package."""
        self.dependencies = dependencies or []
        """The list of project dependencies."""
        self.package_path = self._get_caller_path()
        """The path to the package file."""

    def collect_dependencies_paths(self) -> set[Path]:
        """Collect the paths of all dependencies recursively; excluding the package's own path."""
        # We use a set to avoid duplicates, and a list to process the dependencies in a DFS manner.
        # I looked into reusing pip, pipdeptree or even pipgrip but this is simpler for now.
        paths: set[Path] = set()
        to_process: list[IPackage] = [self]
        while to_process:
            current = to_process.pop()
            c_path = current.package_path.parent
            if c_path not in paths:
                paths.add(c_path)
                to_process.extend(current.dependencies)
        paths.discard(self.package_path.parent)
        return set(paths)

    @classmethod
    def _get_caller_path(cls) -> Path:
        # See: https://stackoverflow.com/a/60297932/3474172
        stack = inspect.stack()
        if len(stack) < 3:
            raise RuntimeError("Could not determine caller path.")
        frame_info = stack[2]
        if frame_info.filename == "<stdin>":
            raise RuntimeError("Could not determine caller path from stdin.")
        return Path(frame_info.filename).resolve()

    @classmethod
    def from_module(cls, m: ModuleType) -> 'IPackage':
        pkg = next((x for _, x in inspect.getmembers(m) if isinstance(x, Package)), None)  # pyright: ignore
        if pkg is None:
            raise ValueError(f"No 'lobs' package found in module {m.__name__}.")
        return pkg  # pyright: ignore


IPackage: t.TypeAlias = Package[p.Project]
