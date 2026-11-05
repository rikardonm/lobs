import collections.abc as _t
import inspect
import typing as t
from functools import cached_property
from pathlib import Path
from types import ModuleType

import annotated_types as ant

from lobs.core.version import Version
from lobs.core.exporter import TCFG
from lobs.machinery.freezer import FrozenMutationError

T = t.TypeVar("T")


class ParameterRequirementNotFullfiledError(ValueError):
    def __init__(self, parameter: "Parameter[t.Any]", requestor: "t.Any", statement: t.Any):
        super().__init__()
        self.parameter = parameter
        self.requestor = requestor
        self.statement = f"value {self.parameter.value} fails test '{statement}'"

    def __str__(self) -> str:
        return f"Parameter {self.parameter.fqn} {self.statement} required by {self.requestor}"


class Parameter(t.Generic[T]):
    @property
    def fqn(self) -> str:
        """The fully-qualified parameter name"""
        # see: https://stackoverflow.com/a/2020083
        o = self._d_owner
        n = self._d_name
        m = o.__module__
        if m == "builtins":
            # not gonna happen...
            assert False
        return f"{m}.{o.__name__}.{n}"

    def __set_name__(self, owner: type, name: str):
        if name.startswith("_"):
            raise ValueError(
                f"Parameter name '{name}' is invalid, it should not start with '_'. Use class variables instead."
            )
        self._d_owner = owner
        self._d_name = name

    def __get__(self, obj: t.Any, objtype: t.Any = None) -> t.Self:
        match (obj, objtype):
            case (None, None):
                raise ValueError("I'm sorry Claudia, I can't do anything.")
            case (None, _):
                return self
            case (_, None):
                raise NotImplementedError
            case (_, _):
                return getattr(objtype, self._d_name)

    @t.overload
    def __init__(self, *, require_non_null: bool) -> None: ...

    @t.overload
    def __init__(self, default: T | None) -> None: ...

    def __init__(self, default: T | None = None, require_non_null: bool = False) -> None:
        """Create a user-configurable, type-safe, checkable program parameter.

        :param default: The default value that this parameter should have.
        :param require_value: Require that any given value is not `None`.
        """
        self._owner: "type[Package] | None" = None
        self._value: T | None = default
        self._requirements: list[tuple["type[Package]", ant.BaseMetadata]] = []
        self._require_non_null_value = require_non_null

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
        """Go through all stated requirements and validate their values."""
        if self._require_non_null_value and self.value is None:
            raise ParameterRequirementNotFullfiledError(self, self._d_owner, "is not None")
        for requestor, query in self._requirements:
            match query:
                case ant.Gt():
                    if self._value is None or not self._value > query.gt:  # type: ignore
                        raise ParameterRequirementNotFullfiledError(self, requestor, query)
                case ant.Lt():
                    if self._value is None or not self._value < query.lt:  # type: ignore
                        raise ParameterRequirementNotFullfiledError(self, requestor, query)
                case ant.Predicate():
                    if not query.func(self._value):
                        raise ParameterRequirementNotFullfiledError(self, requestor, query)
                case _:
                    raise NotImplementedError(f"Requirement type {type(query)} not supported yet.")


class ParameterGroup:
    """A helper to tag classes that have parameter groups and should be evaluated."""

    def _evaluate_requirements(self):
        """Recursively scan the objects in the class instance, and evalute parameter requirements."""
        for a_name in dir(self):
            if a_name.startswith("_"):
                continue
            a_obj = getattr(self, a_name)
            if isinstance(a_obj, Parameter):
                a_obj.evaluate_requirements()
            elif isinstance(a_obj, ParameterGroup):
                a_obj._evaluate_requirements()


class _FrozenPackage(type):
    __is_frozen__ = True

    def __setattr__(self, name: str, value: t.Any) -> None:
        if not self.__is_frozen__:
            return super().__setattr__(name, value)
        raise FrozenMutationError(self, name, value)


class Package(ParameterGroup, metaclass=_FrozenPackage):
    __is_frozen__ = False
    __known_tags__: dict[str, "type[Package]"] = {}

    def __setattr__(self, name: str, value: t.Any) -> None:
        if not self.__is_frozen__:
            return super().__setattr__(name, value)
        raise FrozenMutationError(self, name, value)

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
        cls.__is_frozen__ = True

    def _validate_configuration(self) -> None:
        """Validate the package configuration.

        Usual actions are checking if the provided class state is valid (i.e. parameters).
        This "protected" method is invoked by other machinery objects in `lobs`.
        """

    def _prepare_files(self, basepath: Path) -> None:
        """Prepare the package for materialization.

        Usual actions are download, copy or generation of files.
        This "protected" method is invoked by other machinery objects in `lobs`.

        :param basepath: The generated, temporary `lobs-project` component path.
        """

    def _make_project(self, basepath: Path) -> "Project":
        """Materialize the package into one project.

        This "protected" method is invoked by other machinery objects in `lobs`.

        :param basepath: The base path where the project files should be created.
        :return: The materialized project.
        """
        for attr_name in dir(self):
            if attr_name.startswith("_"):
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
            obj
            for name, obj in inspect.getmembers(m)
            if (isinstance(obj, type) and issubclass(obj, Package) and obj is not Package and not name.startswith("_"))
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


class Project:
    class Config:
        validate_assignment = True

    @cached_property
    def dependencies(self) -> _t.Sequence[type[Package]]:
        return self._get_dependencies()

    def _get_dependencies(self) -> _t.Sequence[type[Package]]:
        return []
