import collections.abc as _t
import inspect
import typing as t
from functools import cached_property
from pathlib import Path
from types import ModuleType

import annotated_types as ant

from lobs.core.version import Version
from lobs.core.exporter import TCFG


T = t.TypeVar("T")


class Parameter(t.Generic[T]):
    def __init__(self, default: T | None) -> None:
        self._owner: "type[Package] | None" = None
        self._value: T | None = default
        self._requirements: list[tuple["type[Package]", ant.BaseMetadata]] = []

    @property
    def owner(self) -> "type[Package] | None":
        return self._owner

    @property
    def value(self) -> T | None:
        return self._value

    @property
    def requirements(self) -> list[tuple["type[Package]", ant.BaseMetadata]]:
        return self._requirements

    def require(self, requester: "Package | type[Package]", query: ant.BaseMetadata) -> None:
        if isinstance(requester, Package):
            requester = type(requester)
        self._requirements.append((requester, query))

    def consume(self, owner: "Package | type[Package]", value: T) -> T | None:
        if self._owner is not None:
            raise RuntimeError(f"Parameter already owned by {self._owner}; cannot be consumed by {owner}.")
        if isinstance(owner, Package):
            owner = type(owner)
        self._owner = owner
        self._value = value
        return value

    def evaluate_requirements(self) -> None:
        for requester, query in self._requirements:
            match query:
                case ant.Gt():
                    if self._value is None or not self._value > query.gt:  # type: ignore
                        raise ValueError(
                            f"Parameter value {self._value} does not satisfy requirement {query} from {requester}."
                        )
                case ant.Lt():
                    if self._value is None or not self._value < query.lt:  # type: ignore
                        raise ValueError(
                            f"Parameter value {self._value} does not satisfy requirement {query} from {requester}."
                        )
                case ant.Predicate():
                    if not query.func(self._value):
                        raise ValueError(
                            f"Parameter value {self._value} does not satisfy requirement {query} from {requester}."
                        )
                case _:
                    raise NotImplementedError(f"Requirement type {type(query)} not supported.")


class Package:
    __known_tags__: dict[str, "type[Package]"] = {}

    def __init_subclass__(
        cls,
        /,
        description: str | None = None,
        version: Version | None = None,
        tag: str | None = None,
    ) -> None:
        """Initialize subclass with metadata.

        :param description: A short description of the package.
        :param version: The version of the package.
        :param tag: An optional tag for the package. If not provided, defaults to the class name.
        """
        super().__init_subclass__()
        cls.version = version
        """The version of the package."""
        cls.description = description
        """A short description of the package."""
        cls.tag = tag or cls.__name__
        """An optional tag for the package. If not provided, defaults to the class name."""
        if cls.tag in cls.__known_tags__:
            owner = cls.__known_tags__[cls.tag]
            raise RuntimeError(f"Tag '{cls.tag}' is already in use by another package ({owner}).")
        cls.__known_tags__[cls.tag] = cls

    def _validate_configuration(self) -> None:
        """Validate the package configuration."""

    def _prepare_files(self, basepath: Path) -> None:
        """Prepare the package for materialization."""

    def _make_project(self, basepath: Path) -> "Project":
        """Materialize the package into one project.

        :param basepath: The base path where the project files should be created.
        :return: The materialized project.
        """
        for attr_name in dir(self):
            if attr_name.startswith('_'):
                continue
            attr = getattr(self, attr_name)
            if isinstance(attr, Project):
                return attr
        raise RuntimeError("No project found in the package.")

    def get_exporter_configuration(
        self,
        config_type: type[TCFG],
        gen_path: Path,
    ) -> TCFG | None:
        """Get the exporter configuration for the given exporter configuration type."""
        if export_config := getattr(self, "export", None):
            if isinstance(export_config, list):
                for cfg in export_config:  # pyright: ignore[reportUnknownVariableType]
                    if isinstance(cfg, config_type):
                        return cfg
            else:
                if isinstance(export_config, config_type):
                    return export_config
        return None

    @classmethod
    def capture_all_from_module(cls, m: ModuleType) -> "type[Package]":
        ret: list[type[Package]] = [
            x for _, x in inspect.getmembers(m)
            if isinstance(x, type) and issubclass(x, Package) and x is not Package
        ]
        if not ret:
            raise RuntimeError("No packages found in the provided project file.")
        if len(ret) > 1:
            raise RuntimeError(f"Multiple packages found in the provided project file: {ret}")
        return ret[0]

    @classmethod
    def require(cls, param: Parameter[T], query: ant.BaseMetadata | T) -> None:
        if isinstance(query, ant.BaseMetadata):
            param.require(cls, query)
        else:
            param.consume(cls, query)


P = t.ParamSpec("P")


class Project:
    class Config:
        validate_assignment = True

    @cached_property
    def dependencies(self) -> _t.Sequence[type[Package]]:
        return self._get_dependencies()

    def _get_dependencies(self) -> _t.Sequence[type[Package]]:
        return []
