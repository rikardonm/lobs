import dataclasses
import typing as t

from lobs.core.version import Version
from lobs.core.configuration import ExporterConfiguration


class Project:
    """Base class for all project types (e.g. application, library).

    This class shall be extended by users to add custom project types.
    These can vary by language, framework, etc.
    """


TP = t.TypeVar("TP", bound=Project)


@dataclasses.dataclass
class ProjectMeta:
    """Base class for all project types (e.g. application, library).

    This class contains the minimal data required for the `lobs` framework to work.
    """
    name: str
    """The name of the project."""
    version: Version
    """The version of the project."""
    short_description: str | None = None
    """A short description of the project."""
    dependencies: list[t.Self] = t.cast(list[t.Self], dataclasses.field(default_factory=list))
    """The list of project dependencies."""
    exporter_configuration: list[ExporterConfiguration] = t.cast(list[ExporterConfiguration], dataclasses.field(default_factory=list))
    """The list of exporter-specific configuration options."""
