import abc
import typing as t

from lobs.core.module import ProjectModule
from .configuration import ExporterConfiguration

T = t.TypeVar('T', bound=ExporterConfiguration)


class BaseExporter(abc.ABC, t.Generic[T]):
    def __init__(self, module: ProjectModule):
        self.module = module
        """The project top-level module to export."""
        # We explicitly look for the exact type here, to avoid issues with subclasses
        # that is, if an exporter "reuses" the configuration of another exporter,
        # we don't want to pick that up here.
        provided_config = next(
            (c for c in module.pkg.meta.exporter_configuration if type(c) is self.config_cls),
            None,
        )
        self.config = t.cast(T, provided_config) or self.config_cls()
        """The configuration for the exporter."""

    @abc.abstractmethod
    def export(self) -> None:
        """Export the project to the desired format."""

    KNOWN: dict[str, type[t.Self]] = {}

    def __init_subclass__(cls, tag: str, config_cls: type[T]) -> None:
        cls.tag = tag
        cls.config_cls = config_cls
        cls.KNOWN[tag] = cls
        return super().__init_subclass__()


IExporter: t.TypeAlias = BaseExporter[t.Any]
