import inspect
from types import ModuleType
import typing as t
from pathlib import Path

import pydantic

from lobs.core.version import Version
from lobs._machinery.logger import module_logger


T = t.TypeVar("T")


class Registry(t.Generic[T]):
    def __init__(self, friendly_name: str) -> None:
        self.logger = module_logger.getChild(friendly_name + "Registry")
        self._items: set[T] = set()

    def register(self, item: T) -> None:
        self.logger.debug(f"Registering item: {item!r}")
        self._items.add(item)


class Project(pydantic.BaseModel):
    def get_dependencies(self) -> 'list[type[Package]]':
        return []


class ProjectConfig(pydantic.BaseModel):
    pass


class Package:
    version: Version
    """The version of the package."""
    description: str
    """A short description of the package."""
    tag: str
    """An optional tag for the package. If not provided, defaults to the class name."""

    def __init_subclass__(
        cls,
        /,
        version: Version,
        description: str,
        tag: str | None = None,
    ) -> None:
        super().__init_subclass__()
        cls.version = version
        cls.description = description
        cls.tag = tag or cls.__name__

    def configure(self, config: ProjectConfig | None) -> None:
        """Configure the package with the given configuration."""
        if config is not None:
            raise RuntimeError(
                "The package does not accept any configuration "
                f"(class: {type(config).__name__}, instance: {config!r})."
            )

    def prepare_files(self, basepath: Path) -> None:
        """Prepare the package for materialization."""
        pass

    def materialize(self, basepath: Path) -> Project:
        """Materialize the package into one or more projects."""
        for attr_name in dir(self):
            if attr_name.startswith('__'):
                continue
            attr = getattr(self, attr_name)
            if isinstance(attr, Project):
                return attr
        raise RuntimeError("No project found in the package.")

    @classmethod
    def capture_all_from_module(cls, m: ModuleType) -> "type[Package]":
        ret = [
            x for _, x in inspect.getmembers(m)
            if isinstance(x, type) and issubclass(x, Package) and x is not Package
        ]
        if not ret:
            raise RuntimeError("No packages found in the provided project file.")
        if len(ret) > 1:
            raise RuntimeError(f"Multiple packages found in the provided project file: {ret}")
        return ret[0]
