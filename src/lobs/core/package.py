import dataclasses
import typing as t

from lobs.core import project as p


@dataclasses.dataclass
class Package(t.Generic[p.TP]):
    meta: p.ProjectMeta
    """The metadata of the package."""
    project: p.TP
    """The project instance contained in the package."""


PKG: t.TypeAlias = Package[p.Project]
